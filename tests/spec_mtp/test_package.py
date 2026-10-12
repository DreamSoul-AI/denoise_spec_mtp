"""Packaging and entry: RPipe is a dependency, spec_mtp is a thin entry, no rpipe override."""

import importlib.metadata as metadata
import json
import re
from pathlib import Path

import pytest
import rpipe

from spec_mtp import cli
from spec_mtp.structure.artifact import sources

tomllib = pytest.importorskip('tomllib')  # Python >= 3.11

ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))


def _pinned_commit():
    for dep in PYPROJECT['project']['dependencies']:
        match = re.match(r'rpipe @ git\+https://github.com/diaoenmao/RPipe(?:\.git)?@([0-9a-f]{40})$', dep)
        if match:
            return match.group(1)
    raise AssertionError('rpipe dependency must be pinned to a full commit')


def test_rpipe_is_a_pinned_dependency_not_vendored():
    assert _pinned_commit()
    assert not (ROOT / 'src' / 'rpipe').exists()
    assert PYPROJECT['tool']['setuptools']['packages']['find']['include'] == ['spec_mtp*']
    assert Path(rpipe.__file__).resolve().parents[1] != (ROOT / 'src').resolve()


def test_console_scripts_do_not_override_rpipe():
    assert PYPROJECT['project']['scripts'] == {'spec-mtp': 'spec_mtp.cli:main'}
    eps = [ep for ep in metadata.entry_points(group='console_scripts') if ep.name == 'rpipe']
    assert all(ep.value == 'rpipe.flow.cli:main' for ep in eps)
    dist = metadata.distribution('denoise-spec-mtp')
    assert {ep.name for ep in dist.entry_points if ep.group == 'console_scripts'} == {'spec-mtp'}


def test_installed_rpipe_matches_pin_when_vcs_installed():
    origin = sources.rpipe_origin()
    if 'commit' in origin:
        assert origin['commit'] == _pinned_commit()


def test_manifest_covers_package_sources():
    body = sources.manifest()
    assert {'spec_mtp/recipe.py', 'spec_mtp/flow/checks.py',
            'spec_mtp/structure/algorithm/decoding.py'} <= set(body['files'])
    assert not any(name.startswith('rpipe/') for name in body['files'])
    assert body['digest'] == sources.files_digest(body['files'])


def test_cli_lock_only_for_make_run_launch(tmp_path):
    study = tmp_path / 's'
    study.mkdir()
    (study / 'study.yaml').write_text('study: s\n')
    assert cli.write_lock_for(['status', str(study)]) is None
    assert cli.write_lock_for(['make', str(study)]) == study / sources.LOCK_NAME
    first = json.loads((study / sources.LOCK_NAME).read_text())['created_at']
    (study / 'scripts').mkdir()
    (study / 'scripts' / 'jobs.json').write_text('{}')
    assert cli.write_lock_for(['launch', str(study)]) is None  # keep the make-time lock
    assert json.loads((study / sources.LOCK_NAME).read_text())['created_at'] == first
    assert cli.write_lock_for(['launch', str(study), '--remake']) is not None
    assert cli.write_lock_for(['study', 'run', str(study)]) is not None


def test_load_lock_absent_is_none(tmp_path):
    assert sources.load_lock(tmp_path) is None


def test_load_lock_rejects_corrupt_and_non_object(tmp_path):
    path = tmp_path / sources.LOCK_NAME
    path.write_text('{not json', encoding='utf-8')
    with pytest.raises(sources.SpecMtpSourceChangedError, match='not valid JSON'):
        sources.load_lock(tmp_path)
    path.write_text('[1, 2]', encoding='utf-8')
    with pytest.raises(sources.SpecMtpSourceChangedError, match='JSON object'):
        sources.load_lock(tmp_path)
    path.write_text('{"digest": "abc"}\n', encoding='utf-8')
    assert sources.load_lock(tmp_path) == {'digest': 'abc'}
