"""Windows native-import probe (CPU only, no weights, no network).

    python tools/windows_selfcheck.py
    python tools/windows_selfcheck.py --smoke
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time

import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PROBE = r'''
import json, sys
first = sys.argv[1]
if first == 'rpipe':
    import rpipe
import spec_mtp
import rpipe, numpy, torch
a = numpy.ones((64, 64)); numpy.linalg.svd(a @ a)
t = torch.ones(64, 64); torch.mm(t, t).sum().item()
from transformers import LlamaConfig, LlamaForCausalLM
torch.manual_seed(0)
m = LlamaForCausalLM(LlamaConfig(vocab_size=64, hidden_size=32, intermediate_size=64,
                                 num_hidden_layers=1, num_attention_heads=2, num_key_value_heads=1))
m(torch.tensor([[1, 2, 3]])).logits.sum().item()
print(json.dumps({'torch': torch.__version__, 'numpy': numpy.__version__,
                  'threads': torch.get_num_threads()}))
'''


def run_case(name, first, timeout):
    env = dict(os.environ, PYTHONUTF8='1')
    start = time.time()
    try:
        proc = subprocess.run([sys.executable, '-c', PROBE, first], env=env, capture_output=True,
                              text=True, timeout=timeout, cwd=ROOT)
    except subprocess.TimeoutExpired:
        return {'case': name, 'ok': False, 'error': f'timeout {timeout}s'}
    out = {'case': name, 'ok': proc.returncode == 0, 'returncode': proc.returncode,
           'seconds': round(time.time() - start, 1)}
    if proc.returncode == 0:
        out.update(json.loads(proc.stdout.strip().splitlines()[-1]))
    else:
        out['error'] = (proc.stderr or proc.stdout)[-1500:]
    return out


def run_smoke(timeout, output_dir):
    env = dict(os.environ, PYTHONUTF8='1', MPLBACKEND='Agg', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
    identity = f'windows-v031-{time.time_ns()}-{os.getpid()}'
    dest = output_dir / identity
    shutil.copytree(ROOT / 'studies' / 'smoke', dest,
                    ignore=shutil.ignore_patterns('runs', 'shared', 'scripts', 'docs', 'index.json',
                        'process.json', 'provenance.json', 'spec_mtp_*.json', 'activity.json', '__pycache__'))
    declared = yaml.safe_load((dest / 'study.yaml').read_text(encoding='utf-8'))
    declared['study'] = identity
    declared['fixed']['algorithm']['config']['version'] = identity
    declared['freeze'] = True
    (dest / 'study.yaml').write_text(yaml.safe_dump(declared, sort_keys=False), encoding='utf-8')
    start = time.monotonic()
    commands = []
    for verb, options in [('make', ['--num-gpus', '0', '--round', '1']),
                          ('launch', ['--num-gpus', '0', '--console', 'shared']),
                          ('process', []), ('report', [])]:
        argv = [sys.executable, '-m', 'spec_mtp', verb, str(dest), *options]
        try:
            proc = subprocess.run(argv, env=env, capture_output=True, text=True, timeout=timeout, cwd=ROOT)
        except subprocess.TimeoutExpired:
            return {'case': 'smoke', 'ok': False, 'error': f'{verb} timeout {timeout}s', 'study': str(dest)}
        (dest / f'{verb}.stdout.log').write_text(proc.stdout, encoding='utf-8')
        (dest / f'{verb}.stderr.log').write_text(proc.stderr, encoding='utf-8')
        commands.append({'argv': argv, 'returncode': proc.returncode})
        if proc.returncode:
            return {'case': 'smoke', 'ok': False, 'returncode': proc.returncode, 'commands': commands,
                    'study': str(dest), 'error': (proc.stderr or proc.stdout)[-1500:]}
    body = json.loads((dest / 'process.json').read_text(encoding='utf-8'))
    complete = body.get('complete') is True and body.get('spec_mtp', {}).get('passed') is True
    return {'case': 'smoke', 'ok': complete, 'seconds': time.monotonic() - start,
            'study': str(dest), 'complete': complete, 'commands': commands}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--smoke', action='store_true', help='also run studies/smoke')
    parser.add_argument('--timeout', type=int, default=300)
    parser.add_argument('--out', default='.tmp/windows_selfcheck.json')
    args = parser.parse_args()
    print(f'python {sys.version.split()[0]} on {platform.platform()} ({sys.platform})')
    output_path = Path(args.out).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results = [run_case('spec_mtp-first', 'spec_mtp', args.timeout),
               run_case('rpipe-first', 'rpipe', args.timeout)]
    if args.smoke:
        results.append(run_smoke(args.timeout * 4, output_path.parent))
    for r in results:
        status = 'ok  ' if r['ok'] else 'FAIL'
        extra = (f"torch={r.get('torch')} numpy={r.get('numpy')}"
                 if r['ok'] and 'torch' in r else (r.get('error', '').strip().splitlines() or [''])[-1])
        print(f'{status} {r["case"]:<20} {extra}')
    output_path.write_text(json.dumps({'platform': platform.platform(), 'python': sys.version,
                                          'results': results}, indent=2), encoding='utf-8')
    print(f'wrote {args.out}')
    return 0 if all(r['ok'] for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
