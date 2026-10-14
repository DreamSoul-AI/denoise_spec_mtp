"""Compatibility entry; all commands use the same flow.cli implementation."""
from spec_mtp.flow.cli import _command, _study_arg, _study_freeze, main, write_lock_for

__all__ = ['_command', '_study_arg', '_study_freeze', 'main', 'write_lock_for']

if __name__ == '__main__':
    raise SystemExit(main())
