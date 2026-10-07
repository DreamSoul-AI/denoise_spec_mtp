"""RPipe Data builders for spec_mtp prompt sets."""

from __future__ import annotations

from rpipe.structure.data.factory import Data, DataRegistry

from spec_mtp.data import encode_prompts, load_records, needs_tokenizer


def _data_cfg(data_config):
    cfg = dict(data_config.config or {})
    cfg['name'] = str(data_config.name or 'local_prompts').lower()
    return cfg


def _build(data_config, assets_dir, seed=None):
    del assets_dir, seed
    data_cfg = _data_cfg(data_config)
    records = load_records(data_cfg)
    meta = {'data_cfg': data_cfg}
    if needs_tokenizer(data_cfg):
        loaders = {'test': records}
        meta['record_count'] = len(records)
    else:
        prompts = encode_prompts(records, None, data_cfg)
        loaders = {'test': prompts}
        meta['prompt_count'] = len(prompts)
    label = str(data_config.name or data_cfg['name'])
    return Data(name=label, source='spec_mtp', loaders=loaders, meta=meta)


def register_data():
    for name in ('specbench', 'local_prompts', 'dolly', 'SpecBench', 'LocalPrompts', 'Dolly'):
        DataRegistry.register(name, 'spec_mtp', _build)
