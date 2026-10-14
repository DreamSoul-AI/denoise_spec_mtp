"""Register sources without constructing inputs, loading weights or decoding."""

from spec_mtp.recipe import register, register_sources

register_sources()

__all__ = ['register']
