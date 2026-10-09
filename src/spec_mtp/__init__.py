"""SpecMTP on RPipe — ESP + EMA-velocity speculative MTP.

- ``spec_mtp.structure`` — RPipe layers; SpecMTP code sits in each layer's ``spec_mtp`` submodule
- ``spec_mtp.flow`` — study execution; ``python -m spec_mtp`` is the cli
"""

import sys

# On Windows, import Torch before other native extensions so OpenMP/BLAS DLLs
# agree. Importing NumPy alone first can fault in blas_fpe_check on some setups.
if sys.platform == 'win32':
    try:
        import torch  # noqa: F401
    except ImportError:
        import numpy  # noqa: F401

from spec_mtp.structure.api.spec_mtp.register import register_all

register_all()
