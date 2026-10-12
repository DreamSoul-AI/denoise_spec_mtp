"""Editable install adds ``src/`` to sys.path; site.py then imports this.

``python -m rpipe`` never imports ``spec_mtp``, so ``spec_mtp/__init__.py``
cannot put Torch ahead of NumPy on Windows. This file runs for any interpreter
that has this checkout installed editable. Non-Windows is a no-op.
"""

from spec_mtp._win_import import preload

preload()
