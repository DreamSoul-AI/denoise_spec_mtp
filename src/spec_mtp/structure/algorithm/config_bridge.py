"""Map an RPipe Run layer into the legacy NamedDict the decoders expect."""

from __future__ import annotations

from typing import Any

from spec_mtp.structure.control.named import _convert


def legacy_cfg(data: Any, model: Any, system: Any, algorithm_config: Any, seed: int) -> Any:
    eval_cfg = dict(algorithm_config.setting('eval', {}) or {})
    eval_cfg['device'] = str(system.device)
    return _convert({
        'run': {'seed': int(seed)},
        'data': dict(data.meta.get('data_cfg') or {}),
        'model': dict(model.meta.get('model_cfg') or {}),
        'eval': eval_cfg,
        'spec': dict(algorithm_config.setting('spec', {}) or {}),
    })


def apply_variant(spec_cfg: dict[str, Any] | None, variant: str | None) -> Any:
    """Merge a smoke variant or a ``<group>/<cell>`` paper preset into ``spec``."""
    from spec_mtp.structure.algorithm.paper_variants import PAPER_VARIANTS
    from spec_mtp.structure.algorithm.smoke_variants import VARIANTS

    key = str(variant or '').lower()
    if not key:
        return spec_cfg
    presets = {**VARIANTS, **PAPER_VARIANTS}
    if key not in presets:
        import difflib

        close = difflib.get_close_matches(key, sorted(presets), n=3, cutoff=0.6)
        hint = f'; did you mean {", ".join(map(repr, close))}?' if close else (
            f'; smoke variants: {sorted(VARIANTS)}; paper presets are <llama3|qwen3>/<cell>, '
            'see spec_mtp/structure/algorithm/paper_variants.py')
        raise ValueError(f'unknown spec variant: {key!r}{hint}')
    merged = dict(spec_cfg or {})
    merged.update(presets[key])
    return _convert(merged)
