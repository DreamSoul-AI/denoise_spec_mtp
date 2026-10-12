"""Study recipe for SpecMTP: construction checks, then source registration.

A Study opts in with ``recipe: recipe.py`` whose body is
``from spec_mtp.recipe import register``. RPipe calls ``register(ctx)`` in
prepare, after its own freeze check and before Data / Model / Algorithm are
built. Nothing here loads weights, reads prompts or decodes.

Registration targets RPipe's runtime registries under the ``spec_mtp`` source
only; RPipe's default sources are untouched.
"""

from __future__ import annotations

import json
from typing import Any

SOURCE = 'spec_mtp'
FLASH_ATTENTION = ('flash_attention_2', 'flash_attention_3')


class SpecMtpConfigError(ValueError):
    pass


def _layer(config: dict[str, Any], name: str) -> dict[str, Any]:
    block = config.get(name) or {}
    if not isinstance(block, dict):
        raise SpecMtpConfigError(f'{name} must be a mapping')
    return block


def validate(config: dict[str, Any]) -> dict[str, Any]:
    """Reject configs outside the supported SpecMTP boundary before construction.

    Returns a small description of the checked Run. Only conditions the
    decoder already requires are checked here; nothing is relaxed or added.
    """
    from rpipe.structure.control.layers import AlgorithmConfig

    from spec_mtp.structure.algorithm.eval import TASKS, effective_spec, task_name
    from spec_mtp.structure.control.named import _convert
    from spec_mtp.structure.data import _REGISTRY as DATASETS

    data, model, algorithm = (_layer(config, name) for name in ('data', 'model', 'algorithm'))
    if algorithm.get('source') != SOURCE:
        raise SpecMtpConfigError(f'algorithm.source must be {SOURCE!r} in a SpecMTP Study')
    if algorithm.get('mode') != 'eval':
        raise SpecMtpConfigError('SpecMTP decoding is an eval Algorithm; set algorithm.mode: eval')
    if data.get('source') == SOURCE and str(data.get('name', '')).lower() not in DATASETS:
        raise SpecMtpConfigError(f'unknown SpecMTP data name: {data.get("name")!r}; known: {sorted(DATASETS)}')
    if model.get('source') == SOURCE:
        if model.get('name') not in ('tiny_llama', 'hf_causal'):
            raise SpecMtpConfigError(f'unknown SpecMTP model name: {model.get("name")!r}')
        attn = str((model.get('config') or {}).get('attn_implementation', 'eager')).lower()
        if attn in FLASH_ATTENTION:
            raise SpecMtpConfigError(
                f'attn_implementation={attn} cannot take the 4D tree attention mask; use eager or sdpa')
    algorithm_config = AlgorithmConfig.from_mapping(algorithm)
    task = task_name(algorithm_config)
    if task not in TASKS:
        raise SpecMtpConfigError(f'unknown spec_mtp task: {task!r}; known: {list(TASKS)}')
    # Same resolution as the Algorithm (spec → variant → mask); pure config work.
    spec = effective_spec(_convert(dict(algorithm_config.setting('spec', {}) or {})), algorithm_config)
    info = {'task': task}
    if task == 'esp_mtp':  # only the tree decoder has the impl / tree boundary
        impl = str(spec.get('impl', 'efficient')).lower()
        mode = str((spec.get('tree') or {}).get('mode', 'dynamic')).lower()
        if impl not in ('naive', 'efficient'):
            raise SpecMtpConfigError(f'Unsupported spec.impl: {impl}')
        if impl == 'efficient' and mode != 'static':
            raise SpecMtpConfigError('spec.impl=efficient requires spec.tree.mode=static; '
                                     'use spec.impl=naive with dynamic trees')
        info.update(impl=impl, tree=mode, method=str(spec.get('method', 'esp')))
    return info


def register_sources() -> None:
    """Idempotent: (name, spec_mtp) Data / Model builders and the eval Algorithm."""
    from spec_mtp.structure.algorithm.eval import register_algorithms
    from spec_mtp.structure.data.registry import register_data
    from spec_mtp.structure.model.registry import register_models

    register_data()
    register_models()
    register_algorithms()


def register(ctx) -> None:
    from rpipe.structure.make.expand import load_study_yaml

    from spec_mtp.structure.artifact.sources import RUN_ASSET_NAME, check_frozen, manifest

    study = load_study_yaml(ctx.study_dir) if (ctx.study_dir / 'study.yaml').is_file() else {}
    flow = study.get('flow') or {}
    if flow.get('prepare_shared', True) is not False:
        raise SpecMtpConfigError('SpecMTP Studies build prompts per Run; set flow.prepare_shared: false')
    current = manifest()
    check_frozen(ctx.study_dir, study, current)
    validate(ctx.config)
    ctx.assets_dir.mkdir(parents=True, exist_ok=True)
    (ctx.assets_dir / RUN_ASSET_NAME).write_text(
        json.dumps(current, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    register_sources()
