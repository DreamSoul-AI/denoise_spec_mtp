"""Register spec_mtp builders on the vendored RPipe registries."""

from __future__ import annotations

_PATCHED = False


def _patch_shared_data_skip() -> None:
    from rpipe.structure.data import prepare as prepare_mod

    if getattr(prepare_mod, '_spec_mtp_skip_patched', False):
        return

    original = prepare_mod._shared_data_mapping

    def _shared_data_mapping(cfg):
        data = cfg.get('data')
        if isinstance(data, dict) and data.get('source') == 'spec_mtp':
            return None
        return original(cfg)

    prepare_mod._shared_data_mapping = _shared_data_mapping
    prepare_mod._spec_mtp_skip_patched = True


def register_all() -> None:
    global _PATCHED
    if _PATCHED:
        return
    from spec_mtp.rpipe.algorithm import register_algorithms
    from spec_mtp.rpipe.data import register_data
    from spec_mtp.rpipe.model import register_models

    register_data()
    register_models()
    register_algorithms()
    _patch_shared_data_skip()
    _PATCHED = True
