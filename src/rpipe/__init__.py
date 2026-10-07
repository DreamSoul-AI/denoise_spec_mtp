"""RPipe — research execution substrate.

- ``rpipe.structure`` — control, four layers, artifact, make
- ``rpipe.flow`` — study execution; ``python -m rpipe`` is the cli
"""

import sys

# On Windows, import Torch before other native extensions so OpenMP/BLAS DLLs
# agree. Importing NumPy alone first can fault in blas_fpe_check on some setups.
if sys.platform == 'win32':
    try:
        import torch  # noqa: F401
    except ImportError:
        import numpy  # noqa: F401

__version__ = '0.2.0'
