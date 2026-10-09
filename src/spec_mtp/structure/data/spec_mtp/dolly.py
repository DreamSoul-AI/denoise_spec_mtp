"""Dolly-Databricks creative-writing prompts (Conover et al., 2023).

Used by the Figure 2 alignment probe: 100 creative-writing samples.
Requires the `datasets` package (see studies/history_extrapolation/scripts/download_data.sh)."""

from spec_mtp.structure.data.spec_mtp.encode import render


def load_records(data_cfg):
    from datasets import load_dataset

    category = data_cfg.get('dolly_category', 'creative_writing')
    ds = load_dataset('databricks/databricks-dolly-15k', split='train')
    records = []
    for item in ds:
        if item['category'] != category:
            continue
        text = item['instruction']
        if item.get('context'):
            text = f"{item['context']}\n\n{text}"
        records.append({'category': category, 'text': text})
    return records


def encode(records, tokenizer, data_cfg):
    num_prompts = int(data_cfg.get('num_prompts', 100))
    max_prompt_len = int(data_cfg.get('max_prompt_len', 2048))
    prompts = []
    for item in records:
        input_ids = render(tokenizer, item['text'])
        if input_ids.size(1) > max_prompt_len:
            continue
        prompts.append({
            'question_id': len(prompts),
            'category': item['category'],
            'input_ids': input_ids,
        })
        if len(prompts) >= num_prompts:
            break
    return prompts
