"""Recipe contract: no registration at import, idempotent registration on RPipe,
construction checks before Data / Model are built, SpecMTP source freeze."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from rpipe.structure.algorithm.factory import AlgorithmRegistry
from rpipe.structure.data.factory import DataRegistry
from rpipe.structure.make.recipe import RecipeContext
from rpipe.structure.model.factory import ModelRegistry

from spec_mtp import recipe
from spec_mtp.structure.artifact import sources


def _config(**algorithm_config):
    base = yaml.safe_load((Path(__file__).resolve().parents[2]
                           / 'studies/smoke_tiny_llama/experiment_config.yaml').read_text(encoding='utf-8'))
    base['algorithm']['config'].update(algorithm_config)
    return base


def test_import_registers_nothing():
    code = ('import spec_mtp, spec_mtp.structure.algorithm.eval;'
            'from rpipe.structure.data.factory import DataRegistry;'
            'from rpipe.structure.model.factory import ModelRegistry;'
            'from rpipe.structure.algorithm.factory import AlgorithmRegistry;'
            'assert not [k for k in DataRegistry.list() if k[1]=="spec_mtp"];'
            'assert not [k for k in ModelRegistry.list() if k[1]=="spec_mtp"];'
            'assert ("eval","spec_mtp") not in AlgorithmRegistry.list()')
    subprocess.run([sys.executable, '-c', code], check=True)


def test_register_sources_is_idempotent_and_keeps_rpipe_defaults():
    recipe.register_sources()
    recipe.register_sources()
    assert ('eval', 'spec_mtp') in AlgorithmRegistry.list()
    assert ('eval', 'custom_torch') in AlgorithmRegistry.list()
    assert ('train', 'custom_torch') in AlgorithmRegistry.list()
    data = {name for name, source in DataRegistry.list() if source == 'spec_mtp'}
    assert {'specbench', 'local_prompts', 'dolly'} <= data
    models = {name for name, source in ModelRegistry.list() if source == 'spec_mtp'}
    assert models == {'hf_causal', 'tiny_llama'}


@pytest.mark.parametrize('variant', ['esp_static', 'esp_dynamic', 'ema_velocity'])
def test_validate_accepts_smoke_variants(variant):
    info = recipe.validate(_config(variant=variant))
    assert info['task'] == 'esp_mtp'


@pytest.mark.parametrize('mutate, message', [
    (lambda c: c['algorithm'].update(mode='train'), 'eval Algorithm'),
    (lambda c: c['algorithm'].update(source='custom_torch'), 'algorithm.source'),
    (lambda c: c['algorithm']['config'].update(task='nope'), 'unknown spec_mtp task'),
    (lambda c: c['algorithm']['config'].update(variant='nope'), 'unknown spec variant'),
    (lambda c: c['algorithm']['config'].update(mask='nope'), 'unknown mask setting'),
    (lambda c: c['model']['config'].update(attn_implementation='flash_attention_2'), 'eager or sdpa'),
    (lambda c: c['data'].update(name='nope'), 'unknown SpecMTP data name'),
    (lambda c: c['model'].update(name='nope'), 'unknown SpecMTP model name'),
    (lambda c: c['algorithm']['config'].update(
        variant=None, spec={'impl': 'efficient', 'tree': {'mode': 'dynamic'}}), 'requires spec.tree.mode=static'),
    (lambda c: c['algorithm']['config'].update(variant=None, spec={'impl': 'fast'}), 'Unsupported spec.impl'),
])
def test_validate_rejects_unsupported_configs(mutate, message):
    config = _config(variant='esp_static')
    mutate(config)
    with pytest.raises(ValueError, match=message):
        recipe.validate(config)


def test_alignment_probe_and_ar_baseline_skip_tree_checks():
    assert recipe.validate(_config(task='alignment_probe'))['task'] == 'alignment_probe'
    assert recipe.validate(_config(task='ar_baseline'))['task'] == 'ar_baseline'


def _ctx(study_dir, config):
    return RecipeContext(study_dir=study_dir, run_id='r', seed=123, config=config,
                         shared_data_dir=study_dir / 'shared/data', shared_model_dir=study_dir / 'shared/model',
                         assets_dir=study_dir / 'runs/r/assets')


def test_register_requires_prepare_shared_false(study_copy):
    study_dir = study_copy(lambda s: s['flow'].update(prepare_shared=True))
    with pytest.raises(ValueError, match='prepare_shared'):
        recipe.register(_ctx(study_dir, _config(variant='esp_static')))


def test_register_writes_source_manifest(study_copy):
    study_dir = study_copy()
    recipe.register(_ctx(study_dir, _config(variant='esp_static')))
    body = json.loads((study_dir / 'runs/r/assets' / sources.RUN_ASSET_NAME).read_text(encoding='utf-8'))
    assert body['digest'] == sources.manifest()['digest']
    assert 'spec_mtp/recipe.py' in body['files']


def test_freeze_without_lock_fails(study_copy):
    study_dir = study_copy(lambda s: s.update(freeze=True))
    with pytest.raises(sources.SpecMtpSourceChangedError, match='missing'):
        recipe.register(_ctx(study_dir, _config(variant='esp_static')))


def test_freeze_detects_changed_spec_mtp_source(study_copy):
    study_dir = study_copy(lambda s: s.update(freeze=True))
    lock = sources.write_lock(study_dir)
    recipe.register(_ctx(study_dir, _config(variant='esp_static')))  # unchanged: passes
    body = json.loads(lock.read_text(encoding='utf-8'))
    body['files']['spec_mtp/structure/algorithm/decoding.py'] = '0' * 64
    lock.write_text(json.dumps(body), encoding='utf-8')
    with pytest.raises(sources.SpecMtpSourceChangedError, match='decoding.py'):
        recipe.register(_ctx(study_dir, _config(variant='esp_static')))


def test_freeze_detects_changed_rpipe_commit(study_copy):
    study_dir = study_copy(lambda s: s.update(freeze=True))
    lock = sources.write_lock(study_dir)
    body = json.loads(lock.read_text(encoding='utf-8'))
    body['rpipe'] = {**body.get('rpipe', {}), 'commit': 'f' * 40}
    lock.write_text(json.dumps(body), encoding='utf-8')
    with pytest.raises(sources.SpecMtpSourceChangedError, match='rpipe commit'):
        recipe.register(_ctx(study_dir, _config(variant='esp_static')))


@pytest.mark.parametrize('study', ['_template', 'smoke_tiny_llama'])
def test_repository_studies_expand_and_validate(tmp_path, study):
    """make-level expansion through RPipe, then the recipe checks on every Run config (no weights)."""
    import shutil

    from rpipe.structure.make import expand_study
    from rpipe.structure.make.expand import load_study_yaml

    src = Path(__file__).resolve().parents[2] / 'studies' / study
    dest = tmp_path / study
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns(
        'runs', 'shared', 'scripts', '*.json', 'docs', 'regression', '__pycache__'))
    declared = load_study_yaml(dest)
    assert declared['recipe'] == 'recipe.py'
    assert declared['flow'] == {'study_phases': True, 'prepare_shared': False}
    out = expand_study(dest)
    assert out['configs']
    for path in out['configs']:
        recipe.validate(yaml.safe_load(Path(path).read_text(encoding='utf-8')))
