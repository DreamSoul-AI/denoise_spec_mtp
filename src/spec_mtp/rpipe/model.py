"""RPipe Model builders for HF causal and tiny LLaMA smoke models."""

from __future__ import annotations

from pathlib import Path

from rpipe.structure.model.factory import Model, ModelRegistry

from spec_mtp.config import NamedDict, _convert
from spec_mtp.models.hf_causal import build_model


def _model_cfg(model_config, model_type):
    cfg = dict(model_config.config or {})
    cfg['type'] = model_type
    if model_type == 'hf_causal':
        cfg['name_or_path'] = model_config.name
    return cfg


def _build_tiny(model_config, assets_dir, data_meta=None):
    del assets_dir, data_meta
    model_cfg = _model_cfg(model_config, 'tiny_llama')
    module = build_model(_convert({'model': model_cfg}))
    return Model(
        name=str(model_config.name or 'tiny_llama'),
        source='spec_mtp',
        module=module,
        meta={'model_cfg': model_cfg},
    )


def _build_hf(model_config, assets_dir, data_meta=None):
    del assets_dir, data_meta
    model_cfg = _model_cfg(model_config, 'hf_causal')
    module = build_model(_convert({'model': model_cfg}))
    return Model(
        name=str(model_config.name or 'hf_causal'),
        source='spec_mtp',
        module=module,
        meta={'model_cfg': model_cfg},
    )


def register_models():
    ModelRegistry.register('tiny_llama', 'spec_mtp', _build_tiny)
    ModelRegistry.register('hf_causal', 'spec_mtp', _build_hf)
