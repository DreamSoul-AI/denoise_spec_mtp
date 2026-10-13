"""SpecMTP eval Algorithm ``(eval, spec_mtp)``: esp_mtp / ar_baseline / alignment_probe.

Registered on RPipe's AlgorithmRegistry by ``spec_mtp.recipe.register``.
Decoding is a dedicated Algorithm, not RPipe's classification eval.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from rpipe.structure.algorithm.base import Algorithm
from rpipe.structure.algorithm.factory import AlgorithmRegistry
from rpipe.structure.algorithm.tracker import AlgorithmTracker

from spec_mtp.structure.algorithm import alignment_probe, ar_baseline, esp_mtp
from spec_mtp.structure.algorithm.common import place_model, select_prompts
from spec_mtp.structure.algorithm.config_bridge import apply_variant, legacy_cfg
from spec_mtp.structure.algorithm.mask_settings import spec_for
from spec_mtp.structure.data.prompts import resolve_eos, resolve_prompts

_TASKS = {
    'esp_mtp': esp_mtp,
    'ar_baseline': ar_baseline,
    'alignment_probe': alignment_probe,
}


def task_name(algorithm_config):
    return str(algorithm_config.setting('task', 'esp_mtp')).lower()


def effective_spec(spec, algorithm_config):
    """``spec`` block, then ``variant``, then a named ``mask`` setting (last wins)."""
    variant = algorithm_config.setting('variant', None)
    if variant:
        spec = apply_variant(dict(spec), variant)
    mask = algorithm_config.setting('mask', None)
    if mask:
        spec = spec_for(
            mask,
            beta=algorithm_config.setting('beta', None),
            lam=algorithm_config.setting('lam', None),
            gamma=algorithm_config.setting('gamma', None),
            branches=algorithm_config.setting('branches', None),
            num_masks=algorithm_config.setting('num_masks', None),
        )
    return spec


class SpecMtpEvalAlgorithm(Algorithm):
    def run(self, data, model, system, tracker: AlgorithmTracker) -> dict:
        task = task_name(self.config)
        impl = _TASKS.get(task)
        if impl is None:
            raise ValueError(f'unknown spec_mtp task: {task!r}')

        seed = int(system.meta.get('seed', 0))
        cfg = legacy_cfg(data, model, system, self.config, seed)
        cfg.spec = effective_spec(cfg.spec, self.config)

        module = place_model(model.module, system.device)
        prompts, eos_ids = select_prompts(
            resolve_prompts(data, model),
            resolve_eos(data, model, cfg.eval),
            cfg.eval,
        )
        from spec_mtp.structure.artifact.evidence import capture, check_inputs, digest, model_digest, runtime

        assets = Path(system.assets_dir)
        assets.mkdir(parents=True, exist_ok=True)
        inputs = capture(data, model, prompts, eos_ids, cfg)
        (assets / 'decode_inputs.json').write_text(json.dumps(inputs, indent=2) + '\n', encoding='utf-8')
        if task == 'ar_baseline':
            out = impl.evaluate(
                module, prompts, eos_ids, cfg.eval, seed, system.device, save_dir=None, aggregate=False)
        elif task == 'alignment_probe':
            # collect writes the layer metrics from these raw sums and counts.
            assets.mkdir(parents=True, exist_ok=True)
            out = impl.evaluate(
                module, prompts, eos_ids, cfg.spec, cfg.eval, save_dir=None, aggregate=False)
        else:
            out = impl.evaluate(
                module, prompts, eos_ids, cfg.spec, cfg.eval, seed, system.device,
                save_dir=None, aggregate=False)

        check_inputs(inputs)
        if inputs['model_digest'] != model_digest(module) or inputs['runtime'] != runtime():
            raise RuntimeError('model weights or runtime changed during decoding')
        raw = {'task': task, 'out': out, 'inputs_digest': digest(inputs)}
        (assets / 'decode_observations.json').write_text(json.dumps(raw, indent=2) + '\n', encoding='utf-8')
        return {'mode': 'eval', 'task': task}


def collect(ctx):
    """Study collect hook: derive CSV and Tracker metrics from execute evidence."""
    assets = Path(ctx.layout.assets_dir)
    raw = json.loads((assets / 'decode_observations.json').read_text(encoding='utf-8'))
    task, out = raw['task'], raw['out']
    if task == 'esp_mtp':
        out['summaries'] = esp_mtp._aggregate(out['rows'])
    elif task == 'ar_baseline':
        rows = out['rows']
        total_time = sum(row['ar_time'] for row in rows)
        out['summary'] = {'prompts': len(rows), 'tokens_per_s': sum(row['ar_new_tokens'] for row in rows) / total_time if total_time > 0 else 0.0}
    elif task == 'alignment_probe':
        import torch

        out['rows'] = [
            {'layer': i + 1, 'cos_accepted': (torch.tensor(a) / max(out['counts']['accept'], 1)).item(),
             'cos_rejected': (torch.tensor(b) / max(out['counts']['reject'], 1)).item(),
             'n_accepted': out['n_accepted'], 'n_rejected': out['n_rejected']}
            for i, (a, b) in enumerate(zip(out['sums']['accept'], out['sums']['reject']))]
    metrics = _tracker_metrics(task, out)
    tracker = ctx.state['tracker']
    tracker.append('test', values=metrics)
    tracker.save('test')
    tracker.flush_state()
    _write_assets(assets, task, out)
    ctx.state['collected']['metrics'].update({f'test_{k.lower()}': v for k, v in metrics.items()})



def _tracker_metrics(task, out):
    if task == 'alignment_probe':
        return {
            'Accepted': float(out.get('n_accepted', 0)),
            'Rejected': float(out.get('n_rejected', 0)),
        }
    if task == 'ar_baseline':
        summary = out.get('summary') or {}
        return {'TokensPerS': float(summary.get('tokens_per_s', 0.0))}
    rows = out.get('rows') or []
    totals = esp_mtp.totals(rows)
    summaries = out.get('summaries') or {}
    overall = summaries.get('overall', {})
    return {
        'Accepted': float(totals['accepted']),
        'Committed': float(totals['committed']),
        'DecodeCalls': float(totals['decode_calls']),
        'Tau': float(overall.get('tau', 0.0)),
        'ExactMatchRate': float(overall.get('exact_match_rate', 0.0)),
    }


def _write_assets(assets_dir: Path, task: str, out: dict) -> None:
    assets_dir.mkdir(parents=True, exist_ok=True)
    rows = out.get('rows')
    if rows:
        path = assets_dir / ('alignment_metrics.csv' if task == 'alignment_probe' else 'spec_metrics.csv')
        with path.open('w', newline='', encoding='utf-8') as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    summaries = out.get('summaries')
    if summaries:
        flat = [{'category': k, **v} for k, v in summaries.items()]
        path = assets_dir / 'summary.csv'
        with path.open('w', newline='', encoding='utf-8') as handle:
            writer = csv.DictWriter(handle, fieldnames=list(flat[0].keys()))
            writer.writeheader()
            writer.writerows(flat)
    summary = out.get('summary')
    if summary:
        path = assets_dir / 'summary.csv'
        with path.open('w', newline='', encoding='utf-8') as handle:
            writer = csv.DictWriter(handle, fieldnames=list(summary.keys()))
            writer.writeheader()
            writer.writerow(summary)


TASKS = tuple(_TASKS)


def register_algorithms():
    AlgorithmRegistry.register('eval', 'spec_mtp', SpecMtpEvalAlgorithm)
