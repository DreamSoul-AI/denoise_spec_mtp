"""SpecMTP — ESP + EMA-velocity speculative MTP on RPipe (installed dependency).

- ``spec_mtp.structure`` — SpecMTP-only Data / Model / Algorithm and helpers
- ``spec_mtp.recipe`` — ``register(ctx)`` used by Study recipes
- ``spec_mtp.flow.checks`` — Run / Study gates used by Study flow phases
- ``python -m spec_mtp`` — thin entry over ``python -m rpipe``

Importing this package registers nothing; registration happens in a Study
recipe before Data / Model are built.
"""

from spec_mtp._win_import import preload as _preload

# Windows only: import order of native extensions (OpenMP / BLAS DLLs).
# Default ``torch`` keeps the pre-refactor behaviour; RPipe dev uses NumPy
# first. Switch with SPEC_MTP_WIN_IMPORT_ORDER=torch|numpy|off, see
# spec_mtp/_win_import.py and docs/WINDOWS.md. Not verifiable on Linux.
_preload()

__version__ = '0.2.0'
