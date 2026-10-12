"""SpecMTP eval Algorithm ``(eval, spec_mtp)``: esp_mtp / ar_baseline / alignment_probe.

Registered on RPipe's AlgorithmRegistry by ``spec_mtp.recipe.register``.
Decoding is a dedicated Algorithm, not RPipe's classification eval.
"""

from __future__ import annotations

import csv
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
        assets = Path(system.assets_dir)
        if task == 'ar_baseline':
            out = impl.evaluate(
                module, prompts, eos_ids, cfg.eval, seed, system.device, save_dir=None)
        elif task == 'alignment_probe':
            out = impl.evaluate(
                module, prompts, eos_ids, cfg.spec, cfg.eval, save_dir=None)
        else:
            out = impl.evaluate(
                module, prompts, eos_ids, cfg.spec, cfg.eval, seed, system.device,
                save_dir=None)

        metrics = _tracker_metrics(task, out)
        tracker.append('test', values=metrics)
        tracker.save('test')
        _write_assets(assets, task, out)
        overall = (out.get('summaries') or {}).get('overall', out.get('summary', {}))
        return {
            'mode': 'eval',
            'task': task,
            'elapsed_seconds': 0.0,
            **{k: overall.get(k) for k in (
                'exact_match_rate', 'tau', 'accepted', 'committed', 'decode_calls',
            ) if k in overall},
            **metrics,
        }


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
    if task == 'alignment_probe':
        return
    rows = out.get('rows')
    if rows:
        path = assets_dir / 'spec_metrics.csv'
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
