"""SpecMTP quality gates for RPipe Study phases.

``run_gate(ctx)`` is called by a Study's ``flow/write/run.py``. RPipe runs the
Study write hook before its own write, so a failed gate leaves the Run
``failed`` instead of finalising a ``succeeded`` result.

``study_gate(ctx)`` is called by ``flow/process/run.py`` at Study scope. It
only passes when every Run in the current index succeeded the gate with one
SpecMTP source digest; a subset or a missing Run is reported as incomplete,
never as a complete pass.
"""

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
            rate = float(raw) if raw not in (None, '') else None
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
    out['passed'] = not out['reasons']
    return out


def _overall_any(assets: Path) -> Path | None:
    path = assets / 'summary.csv'
    return path if path.is_file() else None


def declared_factors(study: dict[str, Any]) -> list[dict[str, Any]]:
    """Cartesian product of ``study.yaml`` axes: the Experiments a complete index must list."""
    import itertools

    axes = study.get('axes') or {}
    keys = list(axes)
    return [dict(zip(keys, values)) for values in itertools.product(*(axes[key] for key in keys))]


def run_gate(ctx) -> dict[str, Any]:
    """Study write hook: gate this Run before RPipe writes result.json."""
    report = evaluate_run(ctx.config, Path(ctx.layout.assets_dir))
    draft = ctx.state.get('result_draft')
    if draft is not None:
        draft[GATE_KEY] = report
        sources = Path(ctx.layout.assets_dir) / 'spec_mtp_sources.json'
        if sources.is_file():
            body = json.loads(sources.read_text(encoding='utf-8'))
            draft[GATE_KEY]['sources'] = {k: body.get(k) for k in ('digest', 'git', 'rpipe')}
    if not report['passed']:
        raise SpecMtpGateError('SpecMTP gate failed: ' + '; '.join(report['reasons']))
    return report


def study_gate(ctx, expected_factors: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Study process hook (``ctx.scope == 'study'``); writes ``spec_mtp_study_check.json``."""
    from rpipe.structure.artifact._atomic import atomic_write_text
    from rpipe.structure.artifact.index import load_index

    if ctx.scope != 'study':
        return {}
    study_dir = Path(ctx.study_dir)
    index = load_index(study_dir)
    rows, missing, failed, digests, seen = [], [], [], set(), []
    for experiment in index.get('experiments') or []:
        seen.append(experiment.get('factors') or {})
        for run in experiment.get('runs') or []:
            root = study_dir / 'runs' / str(run.get('run_dir') or run['id'])
            result_path = root / 'result.json'
            if not result_path.is_file():
                missing.append(run['id'])
                continue
            result = json.loads(result_path.read_text(encoding='utf-8'))
            gate = result.get(GATE_KEY) or {}
            row = {'run': run['id'], 'seed': run.get('seed'), 'factors': experiment.get('factors') or {},
                   'status': result.get('status'), 'gate_passed': gate.get('passed') is True,
                   'exact_match_rate': gate.get('exact_match_rate'), 'accept_d1': gate.get('accept_d1'),
                   'sources_digest': gate.get('sources_digest')}
            rows.append(row)
            if row['status'] != 'succeeded' or not row['gate_passed']:
                failed.append(run['id'])
            if row['sources_digest']:
                digests.add(row['sources_digest'])
    expected_ok = True
    if expected_factors is None and (study_dir / 'study.yaml').is_file():
        from rpipe.structure.make.expand import load_study_yaml

        expected_factors = declared_factors(load_study_yaml(study_dir))
    seeds_ok = True
    if (study_dir / 'study.yaml').is_file():
        from rpipe.structure.make.expand import load_study_yaml

        declared_seeds = sorted(load_study_yaml(study_dir).get('seeds') or [])
        for experiment in index.get('experiments') or []:
            if declared_seeds and sorted(r.get('seed') for r in experiment.get('runs') or []) != declared_seeds:
                seeds_ok = False
    if expected_factors is not None:
        norm = lambda items: sorted(json.dumps(item, sort_keys=True) for item in items)
        expected_ok = norm(seen) == norm(expected_factors)
    complete = not missing and bool(rows) and expected_ok and seeds_ok
    body = {
        'scope': 'study',
        'complete': complete,
        'passed': complete and not failed and len(digests) == 1,
        'runs': rows,
        'missing_runs': missing,
        'failed_runs': failed,
        'expected_factors_match': expected_ok,
        'declared_seeds_match': seeds_ok,
        'sources_digests': sorted(digests),
    }
    atomic_write_text(study_dir / STUDY_CHECK_NAME, json.dumps(body, indent=2, ensure_ascii=False) + '\n')
    ctx.state[GATE_KEY] = body
    if not body['passed']:
        state = 'incomplete' if not complete else 'failed'
        raise SpecMtpGateError(f'SpecMTP Study gate {state}; see {study_dir / STUDY_CHECK_NAME}')
    return body
