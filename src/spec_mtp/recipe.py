"""Compatibility recipe exports; construction/registration is in structure.api."""
from spec_mtp.structure.api.recipe import (
    FLASH_ATTENTION, SOURCE, SpecMtpConfigError, register, register_sources, suggest, validate,
)

__all__ = ['FLASH_ATTENTION', 'SOURCE', 'SpecMtpConfigError', 'register', 'register_sources', 'suggest', 'validate']
