"""Evaluate ESP / EMA-velocity multi-token prediction (training-free).

Reports the paper's metrics per SpecBench category and overall:
  - tau: average acceptance length = committed tokens (accepted + bonus) per
    decode model call (Section 4 "Performance Metric"); tau ~ 1/model-calls.
  - call_reduction: 1 - 1/tau (Appendix G.1, Table 6).
  - speedup: AR wall time / spec wall time on the same prompts, when the AR
    reference pass is enabled (eval.run_ar_baseline).
  - exact_match: token-for-token equality with AR decoding under a shared
    seed — the losslessness audit.
"""

import torch

from core import logger as log_module
from core.tools import get_device, sync_device
from data import get_prompts
from models.hf_causal import build_model
from spec.decoding import SpecDecoder, ar_generate


def _make_generator(device, seed):
    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed))
    return gen


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
        out[key] = summary
    return out


def test(cfg, model=None):
    device = get_device(cfg.eval.get('device', 'auto'))
    if model is None:
        model = build_model(cfg)
    model = model.to(device)
    model.eval()

    prompts, data_eos = get_prompts(cfg)
    num_eval = int(cfg.eval.get('num_eval_prompts', len(prompts)))
    prompts = prompts[:num_eval]

    eos_ids = cfg.eval.get('eos_token_ids', None) or data_eos
    run_ar = bool(cfg.eval.get('run_ar_baseline', True))
    seed = int(cfg.run.seed)

    decoder = SpecDecoder(
        model, cfg.spec, cfg.eval, eos_ids=eos_ids,
        generator=_make_generator(device, seed),
    )
    print(f'[esp_mtp] method={cfg.spec.get("method", "esp")} '
          f'num_masks={decoder.num_masks} '
          f'block_complexity={decoder.nominal_block_complexity} '
          f'impl={decoder.impl} prompts={len(prompts)}')

    per_prompt_logger = None
    if bool(cfg.eval.get('log_per_prompt', True)):
        per_prompt_logger = log_module.Logger(
            cfg.run.get('save_dir', None), filename='spec_metrics.csv')

    rows = []
    for idx, item in enumerate(prompts):
        prompt_ids = item['input_ids']
        # Fresh, identically seeded generators per prompt so spec and AR see
        # the same sample stream (exact-match audit at temperature > 0).
        decoder.generator = _make_generator(device, seed + idx)

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
        if run_ar:
            sync_device(device)
            ar_out, ar_stats = ar_generate(
                model, prompt_ids, cfg.eval, eos_ids=eos_ids,
                generator=_make_generator(device, seed + idx),
            )
            sync_device(device)
            row['ar_time'] = ar_stats['ar_time']
            row['ar_calls'] = ar_stats['ar_calls']
            row['exact_match'] = int(torch.equal(output, ar_out))
        rows.append(row)
        if per_prompt_logger is not None:
            per_prompt_logger.log(row)

    summaries = _aggregate(rows)
    summary_logger = log_module.Logger(
        cfg.run.get('save_dir', None), filename='summary.csv')
    for category, summary in summaries.items():
        summary_logger.log({'category': category, **summary})
    return summaries
