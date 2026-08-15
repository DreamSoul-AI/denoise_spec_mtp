"""SpecBench prompts (Xia et al., 2024) — the paper's evaluation suite.

Expects the `question.jsonl` from the official Spec-Bench repo (see
scripts/download_data.sh), one JSON object per line:

    {"question_id": ..., "category": "...", "turns": ["...", ...]}

Categories cover writing, roleplay, reasoning, math, coding, extraction,
stem, humanities (MT-Bench), plus translation (WMT14 DE-EN), summarization
(CNN/DM), qa (Natural Questions), math_reasoning (GSM8K) and rag. Prompts
are the first turn, rendered through the model's chat template (all paper
models are Instruct variants).
"""

import json
import os


def load_questions(path, categories=None):
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f'SpecBench question file not found: {path}\n'
            f'Run scripts/download_data.sh first.')
    questions = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            if categories and item['category'] not in categories:
                continue
            questions.append(item)
    return questions


def get_prompts(cfg, tokenizer):
    data_cfg = cfg.data
    path = data_cfg.get('path', 'data/spec_bench/question.jsonl')
    categories = data_cfg.get('categories', None)
    max_prompt_len = int(data_cfg.get('max_prompt_len', 2048))
    apply_template = bool(data_cfg.get('apply_chat_template', True))
    # e.g. {enable_thinking: false} for Qwen3.
    template_kwargs = dict(data_cfg.get('chat_template_kwargs', {}) or {})

    prompts = []
    for item in load_questions(path, categories):
        text = item['turns'][0]
        if apply_template:
            input_ids = tokenizer.apply_chat_template(
                [{'role': 'user', 'content': text}],
                add_generation_prompt=True, return_tensors='pt',
                **template_kwargs)
        else:
            input_ids = tokenizer(text, return_tensors='pt').input_ids
        if input_ids.size(1) > max_prompt_len:
            continue
        prompts.append({
            'question_id': item.get('question_id', None),
            'category': item['category'],
            'input_ids': input_ids,
        })
    return prompts
