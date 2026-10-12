"""RPipe — research execution substrate.

- ``rpipe.structure`` — control, four layers, artifact, make
- ``rpipe.flow`` — study execution; ``python -m rpipe`` is the cli
"""

import sys

# Local Windows exception (this checkout): import Torch before other native
# extensions so OpenMP/BLAS DLLs agree. Upstream RPipe loads NumPy first;
# that can fault in blas_fpe_check here. Do not copy this patch back upstream
# unless asked.
if sys.platform == 'win32':
    try:
        import torch  # noqa: F401
    except ImportError:
        import numpy  # noqa: F401

__version__ = '0.3.0'
