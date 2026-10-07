"""Evaluate ESP / EMA-velocity multi-token prediction (training-free).

Reports the paper's metrics per SpecBench category and overall:
  - accepted: draft tokens accepted by verification (the headline count).
  - tau: average acceptance length = committed tokens (accepted + bonus) per
    decode model call (Section 4 "Performance Metric"); tau ~ 1/model-calls.
  - call_reduction: 1 - 1/tau (Appendix G.1, Table 6).
  - speedup: AR wall time / spec wall time on the same prompts, when the AR
    reference pass is enabled (eval.run_ar_baseline).
  - exact_match: token-for-token equality with AR decoding under a shared
    seed, the losslessness audit.
"""

import torch

from spec_mtp import csv_logger
from spec_mtp.algorithms.common import legacy_inputs, make_generator
from spec_mtp.spec.decoding import SpecDecoder, ar_generate
from spec_mtp.tools import sync_device


def _aggregate(rows):
    """Aggregate per-prompt rows into per-category + overall summaries."""
    groups = {}
    for row in rows:
        for key in (row['category'], 'overall'):
            groups.setdefault(key, []).append(row)
    out = {}
    for key, group in sorted(groups.items()):
        committed = sum(r['committed'] for r in group)
        decode_calls = max(sum(r['decode_calls'] for r in group), 1)
        new_tokens = sum(r['new_tokens'] for r in group)
        spec_time = sum(r['spec_time'] for r in group)
        tau = committed / decode_calls
        summary = {
            'prompts': len(group),
            'tau': tau,
            'call_reduction': 1.0 - 1.0 / tau if tau > 0 else 0.0,
            'new_tokens_per_prompt': new_tokens / len(group),
            'tokens_per_s': new_tokens / spec_time if spec_time > 0 else 0.0,
        }
        if any('ar_time' in r for r in group):
            ar_time = sum(r.get('ar_time', 0.0) for r in group)
            summary['speedup'] = ar_time / spec_time if spec_time > 0 else 0.0
            summary['exact_match_rate'] = (
                sum(r.get('exact_match', 0) for r in group) / len(group))
        for depth in (1, 2, 3):
            attempts = sum(int(r.get(f'attempt_d{depth}', 0)) for r in group)
            accepts = sum(int(r.get(f'accept_d{depth}', 0)) for r in group)
            summary[f'attempt_d{depth}'] = attempts
            summary[f'accept_d{depth}'] = accepts
            summary[f'accept_rate_d{depth}'] = accepts / attempts if attempts else 0.0
        out[key] = summary
    return out


def totals(rows):
    """Pooled counts over all prompts; `accepted` is what the reports compare."""
    keys = ('accepted', 'committed', 'decode_calls', 'new_tokens')
    return {key: int(sum(int(r[key]) for r in rows)) for key in keys}


def _warmup(decoder, model, prompt_ids, eval_cfg, eos_ids, run_ar, device, seed):
    """Short untimed generation before the measured loop.

    The first CUDA call pays kernel selection and allocator growth,
    which may inflate the measurement.
    Disable with `eval.warmup: false`.
    """
    budget = int(eval_cfg.get('warmup_tokens', 8))
    original = decoder.max_new_tokens
    decoder.max_new_tokens = budget
    try:
        decoder.generate(prompt_ids)
    finally:
        decoder.max_new_tokens = original
    if run_ar:
        warm_cfg = dict(eval_cfg)
        warm_cfg['max_new_tokens'] = budget
        ar_generate(model, prompt_ids, warm_cfg, eos_ids=eos_ids,
                    generator=make_generator(device, seed))
    sync_device(device)


def evaluate(model, prompts, eos_ids, spec_cfg, eval_cfg, seed, device, save_dir=None):
    """Decode every prompt; write spec_metrics.csv / summary.csv under save_dir.

    Returns {'rows': per-prompt rows, 'summaries': per-category summaries}.
    """
    run_ar = bool(eval_cfg.get('run_ar_baseline', True))
    seed = int(seed)

    decoder = SpecDecoder(
        model, spec_cfg, eval_cfg, eos_ids=eos_ids,
        generator=make_generator(device, seed),
    )
    print(f'[esp_mtp] method={spec_cfg.get("method", "esp")} '
          f'num_masks={decoder.num_masks} '
          f'block_complexity={decoder.nominal_block_complexity} '
          f'impl={decoder.impl} prompts={len(prompts)}')

    per_prompt_logger = None
    if bool(eval_cfg.get('log_per_prompt', True)):
        per_prompt_logger = csv_logger.Logger(save_dir, filename='spec_metrics.csv')

    if bool(eval_cfg.get('warmup', True)) and prompts:
        _warmup(decoder, model, prompts[0]['input_ids'], eval_cfg, eos_ids,
                run_ar, device, seed)

    rows = []
    for idx, item in enumerate(prompts):
        prompt_ids = item['input_ids']
        # Fresh, identically seeded generators per prompt so spec and AR see
        # the same sample stream (exact-match audit at temperature > 0).
        decoder.generator = make_generator(device, seed + idx)

        sync_device(device)
        output, stats = decoder.generate(prompt_ids)
        sync_device(device)

        row = {
            'prompt': idx,
            'category': item['category'],
            'new_tokens': stats['new_tokens'],
            'committed': stats['committed'],
            'decode_calls': stats['decode_calls'],
            'accepted': stats['accepted'],
            'tau': stats['committed'] / max(stats['decode_calls'], 1),
            'spec_time': stats['prefill_time'] + stats['decode_time'],
            'hit_context_limit': stats['hit_context_limit'],
        }
        for depth in (1, 2, 3):
            row[f'attempt_d{depth}'] = int(stats['attempt_by_depth'][depth])
            row[f'accept_d{depth}'] = int(stats['accept_by_depth'][depth])
        if run_ar:
            sync_device(device)
            ar_out, ar_stats = ar_generate(
                model, prompt_ids, eval_cfg, eos_ids=eos_ids,
                generator=make_generator(device, seed + idx),
            )
            sync_device(device)
            row['ar_time'] = ar_stats['ar_time']
            row['ar_calls'] = ar_stats['ar_calls']
            row['exact_match'] = int(torch.equal(output, ar_out))
        rows.append(row)
        if per_prompt_logger is not None:
            per_prompt_logger.log(row)

    summaries = _aggregate(rows)
    summary_logger = csv_logger.Logger(save_dir, filename='summary.csv')
    for category, summary in summaries.items():
        summary_logger.log({'category': category, **summary})
    return {'rows': rows, 'summaries': summaries}


def test(cfg, model=None):
    model, prompts, eos_ids, device = legacy_inputs(cfg, model)
    return evaluate(model, prompts, eos_ids, cfg.spec, cfg.eval, cfg.run.seed,
                    device, cfg.run.get('save_dir', None))['summaries']
