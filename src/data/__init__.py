"""Prompt-set registry. `get_prompts(cfg)` -> (prompts, eos_token_ids).

Each prompt is {'question_id', 'category', 'input_ids' [1, L]}. EOS ids come
from the tokenizer (plus generation-config extras) unless the dataset has no
tokenizer (synthetic smoke prompts)."""

from data import dolly, local_prompts, specbench

_REGISTRY = {
    'specbench': specbench.get_prompts,
    'local_prompts': local_prompts.get_prompts,
    'dolly': dolly.get_prompts,
}


def _load_tokenizer(cfg):
    from transformers import AutoTokenizer

    name = cfg.data.get('tokenizer_name', None) or cfg.model.get('name_or_path', None)
    if name is None:
        return None
    return AutoTokenizer.from_pretrained(
        name, local_files_only=bool(cfg.model.get('local_files_only', False)))


def _eos_ids(tokenizer):
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
    name = str(cfg.data.get('name', 'specbench')).lower()
    if name not in _REGISTRY:
        raise ValueError(f'Unknown dataset: {name}. Available: {list(_REGISTRY)}')
    needs_tokenizer = not (
        name == 'local_prompts'
        and str(cfg.data.get('mode', 'synthetic')).lower() == 'synthetic')
    tokenizer = _load_tokenizer(cfg) if needs_tokenizer else None
    prompts = _REGISTRY[name](cfg, tokenizer)
    return prompts, _eos_ids(tokenizer)
