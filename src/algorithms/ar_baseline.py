"""Plain autoregressive decoding baseline (timing / sanity reference)."""

import torch

from core import logger as log_module
from core.tools import get_device, sync_device
from data import get_prompts
from models.hf_causal import build_model
from spec.decoding import ar_generate


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
    seed = int(cfg.run.seed)

    logger = log_module.Logger(cfg.run.get('save_dir', None), filename='spec_metrics.csv')
    total_tokens, total_time = 0, 0.0
    for idx, item in enumerate(prompts):
        generator = torch.Generator(device=device)
        generator.manual_seed(seed + idx)
        sync_device(device)
        _, stats = ar_generate(model, item['input_ids'], cfg.eval,
                               eos_ids=eos_ids, generator=generator)
        sync_device(device)
        logger.log({'prompt': idx, 'category': item['category'], **stats})
        total_tokens += stats['ar_new_tokens']
        total_time += stats['ar_time']

    summary = {
        'prompts': len(prompts),
        'tokens_per_s': total_tokens / total_time if total_time > 0 else 0.0,
    }
    log_module.Logger(cfg.run.get('save_dir', None), filename='summary.csv').log(summary)
    return summary
