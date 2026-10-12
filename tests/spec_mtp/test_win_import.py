"""SPEC_MTP_WIN_IMPORT_ORDER switch (logic only; real DLL behaviour needs Windows)."""

import pytest

from spec_mtp import _win_import as w


def _importer(missing=()):
    calls = []

    def imp(name):
        calls.append(name)
        if name in missing:
            raise ImportError(name)
    return imp, calls


def test_non_windows_imports_nothing():
    imp, calls = _importer()
    assert w.preload('linux', {}, imp) == [] and calls == []


@pytest.mark.parametrize('env, expected', [({}, ['torch']), ({w.ENV: 'torch'}, ['torch']),
                                           ({w.ENV: 'NumPy'}, ['numpy']), ({w.ENV: 'off'}, [])])
def test_modes(env, expected):
    imp, calls = _importer()
    assert w.preload('win32', env, imp) == expected
    assert calls == expected


def test_torch_missing_falls_back_to_numpy():
    imp, calls = _importer(missing=('torch',))
    assert w.preload('win32', {}, imp) == ['numpy']
    assert calls == ['torch', 'numpy']


def test_bad_value_fails():
    with pytest.raises(ValueError, match=w.ENV):
        w.preload('win32', {w.ENV: 'scipy'}, _importer()[0])


def test_sitecustomize_lives_next_to_the_package():
    from pathlib import Path

    import spec_mtp
    import sitecustomize

    assert Path(sitecustomize.__file__).resolve().parent == Path(spec_mtp.__file__).resolve().parents[1]
