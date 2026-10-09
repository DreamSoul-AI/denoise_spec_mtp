"""Map an RPipe Run layer into the legacy NamedDict the decoders expect."""

from spec_mtp.structure.control.spec_mtp.named import NamedDict, _convert


def legacy_cfg(data, model, system, algorithm_config, seed):
    eval_cfg = dict(algorithm_config.setting('eval', {}) or {})
    eval_cfg['device'] = str(system.device)
    return _convert({
        'run': {'seed': int(seed)},
        'data': dict(data.meta.get('data_cfg') or {}),
        'model': dict(model.meta.get('model_cfg') or {}),
        'eval': eval_cfg,
        'spec': dict(algorithm_config.setting('spec', {}) or {}),
    })


def apply_variant(spec_cfg, variant):
    """Merge a smoke / sweep variant label into ``spec``."""
    from spec_mtp.structure.algorithm.eval.spec_mtp.smoke_variants import VARIANTS

    key = str(variant or '').lower()
    if not key:
        return spec_cfg
    if key not in VARIANTS:
        raise ValueError(f'unknown spec variant: {key!r}')
    merged = dict(spec_cfg or {})
    merged.update(VARIANTS[key])
    return _convert(merged)
