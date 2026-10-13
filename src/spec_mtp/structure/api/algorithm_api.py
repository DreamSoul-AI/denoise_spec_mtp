"""Algorithm configuration API used by cross-layer evidence checks."""
from spec_mtp.structure.algorithm.config_bridge import legacy_cfg
from spec_mtp.structure.algorithm.eval import effective_spec, task_name

__all__ = ['effective_spec', 'task_name', 'legacy_cfg']
