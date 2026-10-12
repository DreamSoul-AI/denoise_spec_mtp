"""Register the SpecMTP sources for this Study.

``register_sources()`` runs at import so ``rpipe make`` can land Data into
``shared/data`` before any Run. ``register(ctx)`` still does the per-Run checks.
"""

from spec_mtp.recipe import register, register_sources

register_sources()

__all__ = ['register']
