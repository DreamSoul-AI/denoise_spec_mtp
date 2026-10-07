"""Prompt sets. Loading and tokenizing are separate steps.

`load_records(data_cfg)` reads raw prompts without a tokenizer (the RPipe
Data layer). `encode_prompts(records, tokenizer, data_cfg)` turns them into
{'question_id', 'category', 'input_ids' [1, L]} once the model's tokenizer is
known. `get_prompts(cfg)` composes both for the single-config CLI.

EOS ids come from the tokenizer (plus generation-config extras) unless the
dataset has no tokenizer (synthetic smoke prompts)."""

from spec_mtp.data import dolly, local_prompts, specbench

_REGISTRY = {
    'specbench': specbench,
    'local_prompts': local_prompts,
    'dolly': dolly,
}


def _module(data_cfg):
    name = str(data_cfg.get('name', 'specbench')).lower()
    if name not in _REGISTRY:
        raise ValueError(f'Unknown dataset: {name}. Available: {list(_REGISTRY)}')
    return _REGISTRY[name]


def needs_tokenizer(data_cfg):
    name = str(data_cfg.get('name', 'specbench')).lower()
    return not (name == 'local_prompts' and local_prompts.is_synthetic(data_cfg))


def load_records(data_cfg):
    return _module(data_cfg).load_records(data_cfg)


def encode_prompts(records, tokenizer, data_cfg):
    return _module(data_cfg).encode(records, tokenizer, data_cfg)


def load_tokenizer(name, local_files_only=False):
    from transformers import AutoTokenizer

    if name is None:
        return None
    return AutoTokenizer.from_pretrained(name, local_files_only=bool(local_files_only))


def eos_ids(tokenizer):
    if tokenizer is None:
        return []
    ids = set()
    if tokenizer.eos_token_id is not None:
        ids.add(int(tokenizer.eos_token_id))
    # Instruct models often stop on extra ids (e.g. <|eot_id|> for LLaMA3).
    for name in ('eot_token_id',):
        extra = getattr(tokenizer, name, None)
        if extra is not None:
            ids.add(int(extra))
    return sorted(ids)


def get_prompts(cfg):
    _module(cfg.data)
    tokenizer = None
    if needs_tokenizer(cfg.data):
        name = cfg.data.get('tokenizer_name', None) or cfg.model.get('name_or_path', None)
        tokenizer = load_tokenizer(name, cfg.model.get('local_files_only', False))
    prompts = encode_prompts(load_records(cfg.data), tokenizer, cfg.data)
    return prompts, eos_ids(tokenizer)
