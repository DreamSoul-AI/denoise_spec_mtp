"""Inputs shared by every evaluation: model on device, prompt slice, EOS ids."""

import torch

from spec_mtp.structure.data.spec_mtp import get_prompts
from spec_mtp.structure.model.spec_mtp.hf_causal import build_model
from spec_mtp.structure.system.spec_mtp.device import get_device


def make_generator(device, seed):
    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed))
    return gen


def select_prompts(prompts, data_eos, eval_cfg):
    num_eval = int(eval_cfg.get('num_eval_prompts', len(prompts)))
    eos_ids = eval_cfg.get('eos_token_ids', None) or data_eos
    return prompts[:num_eval], eos_ids


def place_model(model, device):
    model = model.to(device)
    model.eval()
    return model


def legacy_inputs(cfg, model=None):
    """Single-config CLI path: build the model, then tokenize its prompts."""
    device = get_device(cfg.eval.get('device', 'auto'))
    if model is None:
        model = build_model(cfg)
    model = place_model(model, device)
    prompts, data_eos = get_prompts(cfg)
    prompts, eos_ids = select_prompts(prompts, data_eos, cfg.eval)
    return model, prompts, eos_ids, device
