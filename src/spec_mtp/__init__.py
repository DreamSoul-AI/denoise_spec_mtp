"""SpecMTP — ESP + EMA-velocity speculative MTP on the vendored RPipe package.

- ``spec_mtp.structure`` — SpecMTP-only Data / Model / Algorithm and helpers
- ``spec_mtp.recipe`` — ``register(ctx)`` used by Study recipes
- ``spec_mtp.flow.<phase>`` — collect, success and Study gates; checks is a compatibility facade
- ``python -m spec_mtp`` — thin entry over ``python -m rpipe``

Importing this package registers nothing; registration happens in a Study
recipe before Data / Model are built.
"""

__version__ = '0.2.0'
