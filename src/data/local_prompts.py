"""Deterministic prompts that need no download.

Two modes:
  - synthetic: random token-id sequences for the `tiny_llama` smoke model
    (which has no tokenizer). Seeded, so runs are reproducible.
  - text: a small builtin prompt list tokenized with the real tokenizer,
    for quick pretrained-model sanity checks without SpecBench.
"""

import torch

_TEXT_PROMPTS = [
    'Explain speculative decoding in two sentences.',
    'Write a haiku about parallel token prediction.',
    'What is the capital of France, and why is it famous?',
    'List three uses of dynamic programming.',
]


def get_prompts(cfg, tokenizer):
    data_cfg = cfg.data
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
        prompts = []
        for i in range(num_prompts):
            text = _TEXT_PROMPTS[i % len(_TEXT_PROMPTS)]
            if bool(data_cfg.get('apply_chat_template', True)):
                input_ids = tokenizer.apply_chat_template(
                    [{'role': 'user', 'content': text}],
                    add_generation_prompt=True, return_tensors='pt')
            else:
                input_ids = tokenizer(text, return_tensors='pt').input_ids
            prompts.append({
                'question_id': i, 'category': 'local', 'input_ids': input_ids})
        return prompts

    raise ValueError(f'Unsupported local_prompts mode: {mode}')
