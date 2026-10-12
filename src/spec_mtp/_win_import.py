"""Windows native-extension import order, switchable by environment variable.

``SPEC_MTP_WIN_IMPORT_ORDER`` (read once, when ``spec_mtp`` is imported):

- ``torch`` (default) — import Torch first, as the pre-refactor package did
  (2026-10-06 local Windows setup: NumPy first faulted in ``blas_fpe_check``);
- ``numpy`` — import NumPy first, the order RPipe dev uses on win32 (shares
  Conda's libiomp5md);
- ``off`` — import nothing here; the first importer decides.

Only applies when ``sys.platform == 'win32'`` and only when spec_mtp is
imported before rpipe / torch / numpy (the ``python -m spec_mtp`` entry).
``python -m rpipe`` runs RPipe's own order first. Check a machine with
``python tools/windows_selfcheck.py``.
"""

from __future__ import annotations

import importlib
import os
import sys

ENV = 'SPEC_MTP_WIN_IMPORT_ORDER'
MODES = {'torch': ('torch', 'numpy'), 'numpy': ('numpy', 'torch'), 'off': ()}
DEFAULT = 'torch'


def mode(environ=None) -> str:
    value = str((environ if environ is not None else os.environ).get(ENV, DEFAULT) or DEFAULT).strip().lower()
    if value not in MODES:
        raise ValueError(f'{ENV}={value!r}; expected one of {sorted(MODES)}')
    return value


def preload(platform=None, environ=None, importer=None) -> list[str]:
    """Import the modules for the selected mode; return the names imported.

    Like the old package, the first module that imports successfully is enough
    (a missing Torch falls back to NumPy).
    """
    if (platform or sys.platform) != 'win32':
        return []
    importer = importer or importlib.import_module
    for name in MODES[mode(environ)]:
        try:
            importer(name)
        except ImportError:
            continue
        return [name]
    return []
