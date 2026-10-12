"""configs/hf -> studies/paper_hf: generated files current, every legacy cell
reproduced exactly by one expanded Run config, recipe checks pass. No weights."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from rpipe.structure.make import expand_study

from spec_mtp import recipe
from spec_mtp.structure.algorithm.config_bridge import apply_variant

ROOT = Path(__file__).resolve().parents[2]
STUDIES = sorted(p.name for p in (ROOT / 'studies' / 'paper_hf').iterdir() if (p / 'study.yaml').is_file())
LEGACY = sorted((ROOT / 'configs' / 'hf').glob('*/*/*.yaml'))


def test_generated_files_are_current():
    proc = subprocess.run([sys.executable, str(ROOT / 'studies/paper_hf/migrate_configs.py'), '--check'],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr


def _expand_all(tmp_path):
    runs = []
    for name in STUDIES:
        dest = tmp_path / name
        shutil.copytree(ROOT / 'studies' / 'paper_hf' / name, dest,
                        ignore=shutil.ignore_patterns('runs', 'shared', 'scripts', 'docs', '__pycache__'))
        for path in expand_study(dest)['configs']:
            runs.append((name, yaml.safe_load(Path(path).read_text(encoding='utf-8'))))
    return runs


def _plain(value):
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


def _key(data, model, task, eval_cfg, spec, seed):
    return yaml.safe_dump([data, model, task, eval_cfg, spec, seed], sort_keys=True)


def test_every_legacy_cell_maps_to_exactly_one_run(tmp_path):
    runs = _expand_all(tmp_path)
    assert len(runs) == len(LEGACY) == 59
    expanded = []
    for _, cfg in runs:
        recipe.validate(cfg)
        settings = cfg['algorithm']['config']
        task = str(settings['task'])
        spec = dict(settings.get('spec') or {})
        if task != 'ar_baseline':
            spec = _plain(apply_variant(spec, settings['variant']))
        data = {'name': cfg['data']['name'], **cfg['data']['config']}
        model = {'type': cfg['model']['name'], **cfg['model']['config']}
        assert cfg['system']['config']['device'] == 'cuda'
        expanded.append(_key(data, model, task, settings['eval'], spec if task != 'ar_baseline' else None,
                             cfg['seed']))
    legacy = []
    for path in LEGACY:
        c = yaml.safe_load(path.read_text(encoding='utf-8'))
        eval_cfg = {k: v for k, v in c['eval'].items() if k != 'device'}
        task = c['run']['algorithm']
        legacy.append(_key(c['data'], c['model'], task, eval_cfg,
                           c['spec'] if task != 'ar_baseline' else None, c['run']['seed']))
    assert sorted(expanded) == sorted(legacy)


@pytest.mark.parametrize('study', STUDIES)
def test_study_declares_recipe_and_flow(study):
    declared = yaml.safe_load((ROOT / 'studies/paper_hf' / study / 'study.yaml').read_text(encoding='utf-8'))
    assert declared['recipe'] == 'recipe.py'
    assert declared['flow'] == {'study_phases': True, 'prepare_shared': False}

