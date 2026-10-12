"""Thin entry over ``rpipe.flow.cli``.

The only addition: ``make`` / ``run`` (and ``launch --remake`` or a launch that
has no jobs yet) write the SpecMTP source lock into the Study before RPipe
expands it. Every other command and argument goes to RPipe unchanged, so
scripts, this cli and ``python -m rpipe`` share one execution chain.
"""

from __future__ import annotations

import sys
from pathlib import Path

_LOCK_COMMANDS = ('make', 'run', 'launch')


def _study_arg(argv: list[str]) -> Path | None:
    args = argv[1:]
    if argv[0] == 'study' and args[:1] == ['run']:
        args = args[1:]
    for item in args:
        if not item.startswith('-'):
            path = Path(item)
            return path if (path / 'study.yaml').is_file() else None
    return None


def _command(argv: list[str]) -> str | None:
    if not argv:
        return None
    if argv[0] == 'study' and argv[1:2] == ['run']:
        return 'run'
    return argv[0]


def write_lock_for(argv: list[str]) -> Path | None:
    command = _command(argv)
    if command not in _LOCK_COMMANDS:
        return None
    study = _study_arg(argv)
    if study is None:
        return None
    from spec_mtp.structure.artifact.sources import load_lock, write_lock

    if command == 'launch' and '--remake' not in argv and (study / 'scripts' / 'jobs.json').is_file():
        # launch reuses the make plan; keep the make-time lock so freeze can detect drift.
        if load_lock(study) is not None:
            return None
    return write_lock(study)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    lock = write_lock_for(argv)
    if lock is not None:
        print(f'spec_mtp sources: {lock}', flush=True)
    from rpipe.flow.cli import main as rpipe_main

    return int(rpipe_main(argv) or 0)


if __name__ == '__main__':
    raise SystemExit(main())
