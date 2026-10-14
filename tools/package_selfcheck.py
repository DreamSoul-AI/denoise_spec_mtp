"""Build and check wheel/sdist outside src, reusing the current GPU-safe dependencies.

    python tools/package_selfcheck.py --workspace .tmp/package-<new-id>

No venv or dependency resolution: each distribution installs into its own target.
Imports must come from that target; CUDA torch and other installed dependencies
are shared deliberately. This checks package isolation, not a fresh dependency OS.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', required=True, type=Path)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    if workspace.exists():
        parser.error('workspace must be new; previous evidence is retained')
    workspace.mkdir(parents=True)
    records = []
    report = {'python': sys.version, 'workspace': str(workspace), 'commands': records, 'passed': False}

    def command(argv, cwd, env, label):
        start = time.monotonic()
        proc = subprocess.run(list(map(str, argv)), cwd=cwd, env=env, capture_output=True,
                              text=True, encoding='utf-8', errors='replace', timeout=900)
        (workspace / f'{label}.stdout.log').write_text(proc.stdout, encoding='utf-8')
        (workspace / f'{label}.stderr.log').write_text(proc.stderr, encoding='utf-8')
        records.append({'label': label, 'argv': list(map(str, argv)), 'returncode': proc.returncode,
                        'seconds': time.monotonic() - start})
        print(label, proc.returncode, flush=True)
        if proc.returncode:
            raise RuntimeError(f'{label}: {proc.stderr[-2000:]} {proc.stdout[-1000:]}')
        return proc.stdout

    env = dict(os.environ, PYTHONUTF8='1', MPLBACKEND='Agg', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
    env.pop('PYTHONPATH', None)
    try:
        dist = workspace / 'dist'
        dist.mkdir()
        build = ('from setuptools.build_meta import build_wheel, build_sdist; '
                 f'build_wheel({str(dist)!r}); build_sdist({str(dist)!r})')
        command([sys.executable, '-c', build], ROOT, env, 'build')
        for kind, pattern in [('wheel', '*.whl'), ('sdist', '*.tar.gz')]:
            package = next(dist.glob(pattern))
            target = workspace / kind / 'installed'
            outside = workspace / kind / 'outside'
            outside.mkdir(parents=True)
            command([sys.executable, '-m', 'pip', 'install', '--no-deps', '--no-build-isolation',
                     '--no-cache-dir', '--disable-pip-version-check', '--target', target, package],
                    outside, env, kind + '-install')
            installed_env = dict(env, PYTHONPATH=str(target))
            probe = ("import json,rpipe,spec_mtp; from pathlib import Path; "
                     f"root=Path({str(target)!r}).resolve(); "
                     "assert Path(rpipe.__file__).resolve().is_relative_to(root); "
                     "assert Path(spec_mtp.__file__).resolve().is_relative_to(root); "
                     "assert rpipe.__version__=='0.3.1'; "
                     "assert (root/'rpipe/ORIGIN').read_text().splitlines()[0] == "
                     "'7a15c46b75c5eb951cccd60ed7b9fc3463db90f5'; "
                     "assert 'MIT' in (root/'rpipe/LICENSE.md').read_text(); "
                     "print(json.dumps({'rpipe':rpipe.__file__,'spec_mtp':spec_mtp.__file__}))")
            command([sys.executable, '-c', probe], outside, installed_env, kind + '-imports')
            commands = {}
            for module, console in [('rpipe', 'rpipe'), ('spec_mtp', 'spec-mtp')]:
                executable = next(target.rglob(console + ('.exe' if sys.platform == 'win32' else '')))
                commands[module] = [executable]
                command([sys.executable, '-m', module, '--help'], outside, installed_env,
                        kind + '-' + module + '-module-help')
                command([executable, '--help'], outside, installed_env, kind + '-' + module + '-console-help')
            for module in ('rpipe', 'spec_mtp'):
                study = outside / module
                identity = f'v031-{kind}-{module}-{workspace.name}'
                if module == 'rpipe':
                    study.mkdir()
                    declared = {'study': identity, 'seeds': [0, 1], 'axes': {'algorithm.mode': ['train', 'eval']},
                                'freeze': True}
                    base = {'version': identity, 'data': {'name': 'Toy', 'source': 'stub'},
                            'model': {'name': 'linear'}, 'algorithm': {'source': 'custom_torch', 'mode': 'train',
                            'num_steps': 2, 'progress_unit': 'step'}, 'system': {'device': 'cpu',
                            'deterministic': True, 'cudnn_benchmark': False}}
                else:
                    shutil.copytree(ROOT / 'studies/smoke', study, ignore=shutil.ignore_patterns(
                        'runs', 'shared', 'scripts', 'docs', 'index.json', 'process.json', 'provenance.json',
                        'spec_mtp_*.json', 'activity.json', '__pycache__'))
                    declared = yaml.safe_load((study / 'study.yaml').read_text(encoding='utf-8'))
                    base = yaml.safe_load((study / 'experiment_config.yaml').read_text(encoding='utf-8'))
                    declared['study'] = identity
                    declared['fixed']['algorithm']['config']['version'] = identity
                    declared['freeze'] = True
                (study / 'study.yaml').write_text(yaml.safe_dump(declared, sort_keys=False), encoding='utf-8')
                (study / 'experiment_config.yaml').write_text(yaml.safe_dump(base, sort_keys=False), encoding='utf-8')
                prefix = kind + '-' + module
                command([*commands[module], 'make', study, '--num-gpus', '0', '--round', '1'], outside,
                        installed_env, prefix + '-make')
                command([sys.executable, '-m', module, 'launch', study, '--num-gpus', '0', '--console', 'shared'],
                        outside, installed_env, prefix + '-launch')
                for verb in ('process', 'status', 'logs', 'report'):
                    command([*commands[module], verb, study], outside, installed_env, prefix + '-' + verb)
                process = json.loads((study / 'process.json').read_text(encoding='utf-8'))
                assert process['complete'] is True
                index = json.loads((study / 'index.json').read_text(encoding='utf-8'))
                before = {}
                for experiment in index['experiments']:
                    for run in experiment['runs']:
                        result_path = study / 'runs' / run['id'] / 'result.json'
                        result = json.loads(result_path.read_text(encoding='utf-8'))
                        assert result['status'] == 'succeeded'
                        if module == 'spec_mtp':
                            assert result['spec_mtp']['passed'] is True
                            assert result['spec_mtp']['exact_match_rate'] == 1.0
                        before[str(result_path)] = result_path.read_bytes()
                assert len(before) == (4 if module == 'rpipe' else 3)
                command([*commands[module], 'launch', study, '--num-gpus', '0', '--console', 'shared'],
                        outside, installed_env, prefix + '-skip-done')
                assert all(Path(path).read_bytes() == content for path, content in before.items())
                assert (study / 'docs/NUMBERS.md').is_file()
        report['passed'] = True
    except Exception as error:
        report['error'] = str(error)
        raise
    finally:
        (workspace / 'validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
