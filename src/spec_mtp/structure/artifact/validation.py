"""Pure SpecMTP result and evidence validation; no Flow orchestration."""
from __future__ import annotations
import csv
import json
from pathlib import Path
from typing import Any
GATE_KEY = 'spec_mtp'
STUDY_CHECK_NAME = 'spec_mtp_study_check.json'

class SpecMtpGateError(RuntimeError):
    pass

def _overall(assets: Path) -> dict[str, str] | None:
    path = assets / 'summary.csv'
    if not path.is_file():
        return None
    with path.open(newline='', encoding='utf-8') as handle:
        rows = [row for row in csv.DictReader(handle) if row.get('category') == 'overall']
    return rows[0] if len(rows) == 1 else None

def evaluate_run(config: dict[str, Any], assets: Path) -> dict[str, Any]:
    """Pure check of one Run's assets; no decoding."""
    algorithm = config.get('algorithm') or {}
    settings = algorithm.get('config') or {}
    task = str(settings.get('task', 'esp_mtp')).lower()
    eval_cfg = settings.get('eval') or {}
    out: dict[str, Any] = {'task': task, 'passed': False, 'reasons': []}
    sources = assets / 'spec_mtp_sources.json'
    if sources.is_file():
        out['sources_digest'] = json.loads(sources.read_text(encoding='utf-8')).get('digest')
    else:
        out['reasons'].append('missing assets/spec_mtp_sources.json')
    if task == 'esp_mtp':
        if not bool(eval_cfg.get('run_ar_baseline', True)):
            out['reasons'].append('eval.run_ar_baseline is false; exact_match audit did not run')
        overall = _overall(assets)
        if overall is None:
            out['reasons'].append('summary.csv has no single overall row')
        else:
            raw = overall.get('exact_match_rate')
            rate = float(raw) if raw is not None and raw != '' else None
            out['exact_match_rate'] = rate
            for key in ('prompts', 'accept_d1', 'accept_d2', 'accept_d3', 'tau', 'call_reduction'):
                if overall.get(key) not in (None, ''):
                    out[key] = float(overall[key])
            if rate is None:
                out['reasons'].append('exact_match_rate missing')
            elif rate != 1.0:
                out['reasons'].append(f'exact_match_rate={rate} != 1')
    elif task == 'ar_baseline':
        if _overall_any(assets) is None:
            out['reasons'].append('missing summary.csv')
    elif task == 'alignment_probe':
        if not (assets / 'alignment_metrics.csv').is_file():
            out['reasons'].append('missing alignment_metrics.csv')
    if task not in ('esp_mtp', 'ar_baseline', 'alignment_probe'):
        out['reasons'].append(f'unsupported task: {task}')
    out['passed'] = not out['reasons']
    return out

def _overall_any(assets: Path) -> Path | None:
    path = assets / 'summary.csv'
    return path if path.is_file() else None

def declared_factors(study: dict[str, Any]) -> list[dict[str, Any]]:
    """Cartesian product of ``study.yaml`` axes: the Experiments a complete index must list."""
    from rpipe.structure.make.expand import cartesian

    axes = dict(study.get('axes') or {})
    axes.pop('seed', None)
    return cartesian(axes)

def verify_evidence(config: dict[str, Any], assets: Path) -> None:
    """Recompute correctness from raw tokens, and reject execution/finalisation drift."""
    from spec_mtp.structure.artifact.evidence import check_inputs, digest
    from spec_mtp.structure.artifact.sources import changed_files, manifest

    saved = json.loads((assets / 'spec_mtp_sources.json').read_text(encoding='utf-8'))
    current = manifest()
    if saved.get('digest') != current['digest'] or changed_files(saved, current) or saved.get('rpipe') != current['rpipe']:
        raise SpecMtpGateError('SpecMTP sources changed since prepare')
    if saved.get('config_digest') != digest(config):
        raise SpecMtpGateError('Run configuration changed since prepare')
    inputs = json.loads((assets / 'decode_inputs.json').read_text(encoding='utf-8'))
    raw = json.loads((assets / 'decode_observations.json').read_text(encoding='utf-8'))
    if raw['inputs_digest'] != digest(inputs):
        raise SpecMtpGateError('decode input evidence digest mismatch')
    check_inputs(inputs)
    study_dir = assets.parents[2]
    if (study_dir / 'study.yaml').is_file():
        from rpipe.structure.artifact.provenance import source_files
        from rpipe.structure.make.expand import load_study_yaml
        if saved.get('study_files') != source_files(study_dir, load_study_yaml(study_dir)):
            raise SpecMtpGateError('Study sources changed since prepare')
    settings = inputs['settings']
    if str(settings['run']['seed']) != str(config.get('seed', settings['run']['seed'])):
        raise SpecMtpGateError('decode seed changed')
    algorithm = config.get('algorithm') or {}
    from rpipe.structure.control.layers import AlgorithmConfig
    from spec_mtp.structure.api.algorithm_api import effective_spec, task_name
    from spec_mtp.structure.api.algorithm_api import legacy_cfg
    from types import SimpleNamespace

    algo = AlgorithmConfig.from_mapping(algorithm)
    expected = legacy_cfg(SimpleNamespace(meta={}), SimpleNamespace(meta={}),
                          SimpleNamespace(device=settings['eval']['device']), algo, settings['run']['seed'])
    expected.spec = effective_spec(expected.spec, algo)
    if digest(expected.spec) != digest(settings['spec']) or digest(expected.eval) != digest(settings['eval']):
        raise SpecMtpGateError('decode configuration changed')
    task = task_name(algo)
    if raw['task'] != task:
        raise SpecMtpGateError('decode task mismatch')
    # Runtime gates apply inside a Run; later readout compares the saved inputs and raw evidence.
    if task == 'esp_mtp':
        evidence, rows = raw['out']['evidence'], raw['out']['rows']
        if not evidence or len(evidence) != len(inputs['prompts']) or len(rows) != len(evidence):
            raise SpecMtpGateError('missing prompt decode evidence')
        for item, row, prompt in zip(evidence, rows, inputs['prompts']):
            if item['input_ids'] != prompt['input_ids'] or item['output_ids'][:len(item['input_ids'])] != item['input_ids']:
                raise SpecMtpGateError('prompt token evidence mismatch')
            if item['ar_ids'] != item['output_ids'] or row.get('exact_match') != 1:
                raise SpecMtpGateError('raw exact_match != 1')
            stats = item['stats']
            if stats['new_tokens'] != len(item['output_ids']) - len(item['input_ids']):
                raise SpecMtpGateError('generated token count mismatch')
            if len(stats['trace']) != stats['decode_calls'] or sum(len(t['accepted_nodes']) for t in stats['trace']) != stats['accepted']:
                raise SpecMtpGateError('acceptance trace mismatch')
            continuation = item['output_ids'][len(item['input_ids']):]
            if sum(len(t['committed_tokens']) for t in stats['trace']) != stats['committed']:
                raise SpecMtpGateError('committed trace count mismatch')
            if continuation[1:] != [token for t in stats['trace'] for token in t['committed_tokens']]:
                raise SpecMtpGateError('committed token trace mismatch')
            for trace in stats['trace']:
                if trace['cache_before'] != trace['root_position']:
                    raise SpecMtpGateError('cache prefix mismatch')
                if not trace['stopped'] and trace['cache_after'] != trace['root_position'] + 1 + len(trace['accepted_nodes']):
                    raise SpecMtpGateError('cache eviction mismatch')
            for key in ('accepted', 'committed', 'decode_calls', 'new_tokens'):
                if row[key] != stats[key]:
                    raise SpecMtpGateError(f'{key} evidence mismatch')
        from spec_mtp.structure.algorithm.esp_mtp import _aggregate
        expected_summary = _aggregate(rows)['overall']
        actual = _overall(assets)
        if actual is None or any(float(actual[k]) != float(v) for k, v in expected_summary.items()):
            raise SpecMtpGateError('summary does not match raw decode evidence')
    elif task == 'ar_baseline':
        evidence, rows = raw['out']['evidence'], raw['out']['rows']
        if not evidence or len(evidence) != len(inputs['prompts']) or len(rows) != len(evidence):
            raise SpecMtpGateError('missing AR token evidence')
        for item, row, prompt in zip(evidence, rows, inputs['prompts']):
            if item['input_ids'] != prompt['input_ids'] or item['output_ids'][:len(item['input_ids'])] != item['input_ids']:
                raise SpecMtpGateError('AR prompt evidence mismatch')
            if row['ar_new_tokens'] != len(item['output_ids']) - len(item['input_ids']):
                raise SpecMtpGateError('AR generated token count mismatch')
        with (assets / 'summary.csv').open(newline='', encoding='utf-8') as handle:
            summary_rows = list(csv.DictReader(handle))
        total_time = sum(r['ar_time'] for r in rows)
        expected_speed = sum(r['ar_new_tokens'] for r in rows) / total_time if total_time > 0 else 0
        if len(summary_rows) != 1 or float(summary_rows[0]['prompts']) != len(evidence) or float(summary_rows[0]['tokens_per_s']) != expected_speed:
            raise SpecMtpGateError('AR summary does not match raw evidence')
    elif task == 'alignment_probe':
        out = raw['out']
        if out['n_accepted'] + out['n_rejected'] <= 0:
            raise SpecMtpGateError('alignment probe has no observations')
        with (assets / 'alignment_metrics.csv').open(newline='', encoding='utf-8') as handle:
            rows = list(csv.DictReader(handle))
        import torch

        if len(rows) != len(out['sums']['accept']):
            raise SpecMtpGateError('alignment layer evidence missing')
        for i, row in enumerate(rows):
            for key, column in (('accept', 'cos_accepted'), ('reject', 'cos_rejected')):
                expected_value = (torch.tensor(out['sums'][key][i]) / max(out['counts'][key], 1)).item()
                if float(row[column]) != expected_value:
                    raise SpecMtpGateError('alignment CSV does not match raw evidence')
