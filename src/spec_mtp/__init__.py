"""SpecMTP — ESP + EMA-velocity speculative MTP on RPipe (installed dependency).

- ``spec_mtp.structure`` — SpecMTP-only Data / Model / Algorithm and helpers
- ``spec_mtp.recipe`` — ``register(ctx)`` used by Study recipes
- ``spec_mtp.flow.checks`` — Run / Study gates used by Study flow phases
- ``python -m spec_mtp`` — thin entry over ``python -m rpipe``

Importing this package registers nothing; registration happens in a Study
recipe before Data / Model are built.
"""

import sys

# On Windows, import Torch before other native extensions so OpenMP/BLAS DLLs
# agree. Importing NumPy alone first can fault in blas_fpe_check on some setups.
# Kept from the pre-refactor package (2026-10-06 local Windows setup); it only
# takes effect when spec_mtp is imported before rpipe (the spec_mtp entry).
# Not verifiable on Linux; do not drop it as part of de-duplication.
if sys.platform == 'win32':
    try:
        import torch  # noqa: F401
    except ImportError:
        import numpy  # noqa: F401

__version__ = '0.2.0'
