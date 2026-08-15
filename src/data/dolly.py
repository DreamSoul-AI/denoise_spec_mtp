"""Dolly-Databricks creative-writing prompts (Conover et al., 2023).

Used by the Figure 2 alignment probe: 100 creative-writing samples.
Requires the `datasets` package (see scripts/download_data.sh)."""


def get_prompts(cfg, tokenizer):
    from datasets import load_dataset

    data_cfg = cfg.data
    category = data_cfg.get('dolly_category', 'creative_writing')
    num_prompts = int(data_cfg.get('num_prompts', 100))

    ds = load_dataset('databricks/databricks-dolly-15k', split='train')
    prompts = []
    for item in ds:
        if item['category'] != category:
            continue
        text = item['instruction']
        if item.get('context'):
            text = f"{item['context']}\n\n{text}"
        input_ids = tokenizer.apply_chat_template(
            [{'role': 'user', 'content': text}],
            add_generation_prompt=True, return_tensors='pt')
        if input_ids.size(1) > int(data_cfg.get('max_prompt_len', 2048)):
            continue
        prompts.append({
            'question_id': len(prompts),
            'category': category,
            'input_ids': input_ids,
        })
        if len(prompts) >= num_prompts:
            break
    return prompts
