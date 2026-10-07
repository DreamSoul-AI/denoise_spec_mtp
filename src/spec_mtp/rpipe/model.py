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
        cfg['name_or_path'] = cfg.get('name_or_path') or model_config.name
        cfg = _materialize_hub(cfg)
    return cfg


def _materialize_hub(model_cfg):
    """Download via ModelScope when ``hub: modelscope`` is set, then load locally."""
    hub = str(model_cfg.get('hub', '') or '').lower()
    if hub != 'modelscope':
        return model_cfg
    import torch  # load before ModelScope on Windows so BLAS DLLs agree
    from modelscope import snapshot_download

    local = snapshot_download(str(model_cfg['name_or_path']))
    resolved = dict(model_cfg)
    resolved['name_or_path'] = local
    resolved['local_files_only'] = True
    return resolved


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
