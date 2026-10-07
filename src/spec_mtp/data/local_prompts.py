"""Deterministic prompts that need no download.

Two modes:
  - synthetic: random token-id sequences for the `tiny_llama` smoke model
    (which has no tokenizer). Seeded, so runs are reproducible.
  - text: a small builtin prompt list tokenized with the real tokenizer,
    for quick pretrained-model sanity checks without SpecBench.
"""

import torch

from spec_mtp.data.encode import render

_TEXT_PROMPTS = [
    'Explain speculative decoding in two sentences.',
    'Write a haiku about parallel token prediction.',
    'What is the capital of France, and why is it famous?',
    'List three uses of dynamic programming.',
]


def is_synthetic(data_cfg):
    return str(data_cfg.get('mode', 'synthetic')).lower() == 'synthetic'


def load_records(data_cfg):
    mode = str(data_cfg.get('mode', 'synthetic')).lower()
    num_prompts = int(data_cfg.get('num_prompts', 8))

    if mode == 'synthetic':
        vocab_size = int(data_cfg.get('vocab_size', 256))
        prompt_len = int(data_cfg.get('prompt_len', 32))
        generator = torch.Generator().manual_seed(int(data_cfg.get('seed', 0)))
        return [{
            'question_id': i,
            'category': 'synthetic',
            'input_ids': torch.randint(
                0, vocab_size, (1, prompt_len), generator=generator),
        } for i in range(num_prompts)]

    if mode == 'text':
        return [{
            'question_id': i,
            'category': 'local',
            'text': _TEXT_PROMPTS[i % len(_TEXT_PROMPTS)],
        } for i in range(num_prompts)]

    raise ValueError(f'Unsupported local_prompts mode: {mode}')


def encode(records, tokenizer, data_cfg):
    if is_synthetic(data_cfg):
        return [dict(item) for item in records]
    apply_template = bool(data_cfg.get('apply_chat_template', True))
    return [{
        'question_id': item['question_id'],
        'category': item['category'],
        'input_ids': render(tokenizer, item['text'], apply_template),
    } for item in records]
