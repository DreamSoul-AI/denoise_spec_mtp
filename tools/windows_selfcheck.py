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
import tempfile
import time
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


def run_smoke(timeout):
    env = dict(os.environ, PYTHONUTF8='1')
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / 'smoke'
        shutil.copytree(ROOT / 'studies' / 'smoke', dest,
                        ignore=shutil.ignore_patterns('runs', 'shared', 'scripts', '__pycache__'))
        try:
            proc = subprocess.run([sys.executable, '-m', 'spec_mtp', 'run', str(dest)], env=env,
                                  capture_output=True, text=True, timeout=timeout, cwd=ROOT)
        except subprocess.TimeoutExpired:
            return {'case': 'smoke', 'ok': False, 'error': f'timeout {timeout}s'}
        return {'case': 'smoke', 'ok': proc.returncode == 0, 'returncode': proc.returncode,
                **({} if proc.returncode == 0 else {'error': (proc.stderr or proc.stdout)[-1500:]})}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--smoke', action='store_true', help='also run studies/smoke')
    parser.add_argument('--timeout', type=int, default=300)
    parser.add_argument('--out', default='windows_selfcheck.json')
    args = parser.parse_args()
    print(f'python {sys.version.split()[0]} on {platform.platform()} ({sys.platform})')
    results = [run_case('spec_mtp-first', 'spec_mtp', args.timeout),
               run_case('rpipe-first', 'rpipe', args.timeout)]
    if args.smoke:
        results.append(run_smoke(args.timeout * 4))
    for r in results:
        status = 'ok  ' if r['ok'] else 'FAIL'
        extra = (f"torch={r.get('torch')} numpy={r.get('numpy')}"
                 if r['ok'] and 'torch' in r else (r.get('error', '').strip().splitlines() or [''])[-1])
        print(f'{status} {r["case"]:<20} {extra}')
    Path(args.out).write_text(json.dumps({'platform': platform.platform(), 'python': sys.version,
                                          'results': results}, indent=2), encoding='utf-8')
    print(f'wrote {args.out}')
    return 0 if all(r['ok'] for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
