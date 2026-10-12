"""Run .github/workflows/cpu-checks.yml locally, step by step, without Docker.

Equivalent of ``act`` for this workflow: a clean ``git worktree`` of HEAD
stands in for actions/checkout, a fresh Python venv of the workflow's
``python-version`` (via ``uv``) stands in for actions/setup-python, and every
``run:`` block is executed verbatim with ``bash -e`` and the step ``env``.
GitHub-hosted runner image, caches and the PR merge commit are not reproduced.

    python tools/ci_local.py [--workflow .github/workflows/cpu-checks.yml] [--keep]

Work dirs live under ``.tmp/ci_local/`` (gitignored).
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def sh(cmd, **kw):
    print('+', cmd if isinstance(cmd, str) else ' '.join(map(str, cmd)), flush=True)
    return subprocess.run(cmd, check=True, **kw)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--workflow', default='.github/workflows/cpu-checks.yml')
    parser.add_argument('--keep', action='store_true', help='keep the worktree and venv')
    args = parser.parse_args()
    workflow = yaml.safe_load((ROOT / args.workflow).read_text(encoding='utf-8'))
    base = ROOT / '.tmp' / 'ci_local'
    base.mkdir(parents=True, exist_ok=True)
    results = []
    for job_name, job in workflow['jobs'].items():
        work = base / job_name / 'repo'
        venv = base / job_name / 'venv'
        if work.exists():
            sh(['git', 'worktree', 'remove', '--force', str(work)], cwd=ROOT)
        shutil.rmtree(work, ignore_errors=True)
        shutil.rmtree(venv, ignore_errors=True)
        sh(['git', 'worktree', 'add', '--detach', str(work), 'HEAD'], cwd=ROOT)
        try:
            for step in job['steps']:
                uses = step.get('uses', '')
                if uses.startswith('actions/checkout'):
                    results.append((job_name, 'checkout (git worktree HEAD)', 'ok', 0.0))
                    continue
                if uses.startswith('actions/setup-python'):
                    version = str(step['with']['python-version'])
                    sh(['uv', 'venv', '-q', '--seed', '-p', version, str(venv)])
                    results.append((job_name, f'setup-python {version} (uv venv)', 'ok', 0.0))
                    continue
                if 'run' not in step:
                    raise SystemExit(f'unsupported step: {step}')
                env = {**os.environ, **{k: str(v) for k, v in (step.get('env') or {}).items()},
                       'VIRTUAL_ENV': str(venv), 'PATH': f'{venv / "bin"}{os.pathsep}{os.environ["PATH"]}'}
                env.pop('PYTHONPATH', None)
                start = time.time()
                print(f'\n=== {job_name}: {step.get("name", "run")} ===', flush=True)
                proc = subprocess.run(['bash', '-e', '-c', step['run']], cwd=work, env=env)
                status = 'ok' if proc.returncode == 0 else f'FAILED ({proc.returncode})'
                results.append((job_name, step.get('name', 'run'), status, time.time() - start))
                if proc.returncode != 0:
                    break
        finally:
            if not args.keep:
                subprocess.run(['git', 'worktree', 'remove', '--force', str(work)], cwd=ROOT)
    print('\nsummary:')
    for job_name, name, status, seconds in results:
        print(f'  {job_name:12s} {status:12s} {seconds:7.1f}s  {name}')
    return 0 if all(r[2] == 'ok' for r in results) else 1


if __name__ == '__main__':
    sys.exit(main())
