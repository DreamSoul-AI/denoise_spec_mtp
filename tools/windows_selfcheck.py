"""Windows self-check for native import order (CPU only, no weights, no network).

    set PYTHONUTF8=1
    python tools\\windows_selfcheck.py            # all modes and entry orders
    python tools\\windows_selfcheck.py --smoke    # also run the CPU smoke Study once per passing mode

Each case runs in a fresh interpreter so a DLL fault (access violation, hard
exit) only fails that case. Cases:

- ``spec_mtp-first`` x SPEC_MTP_WIN_IMPORT_ORDER in {torch, numpy, off}:
  ``import spec_mtp`` then rpipe, torch, numpy, a NumPy and a Torch matmul and
  a tiny LLaMA forward (what ``python -m spec_mtp`` does);
- ``rpipe-first``: ``import rpipe`` first (what ``python -m rpipe`` does).

Prints a table and writes ``windows_selfcheck.json`` (cwd). Exit 0 when every
case passes. On non-Windows the switch is a no-op; the script still runs and
says so.
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
import sys, json
first = sys.argv[1]
order = []
if first == 'rpipe':
    import rpipe; order.append('rpipe')
import spec_mtp; order.append('spec_mtp')
from spec_mtp import _win_import
preloaded = [m for m in ('torch', 'numpy') if m in sys.modules]
import rpipe, numpy, torch
a = numpy.ones((64, 64)); numpy.linalg.svd(a @ a)
t = torch.ones(64, 64); torch.mm(t, t).sum().item()
from transformers import LlamaConfig, LlamaForCausalLM
torch.manual_seed(0)
m = LlamaForCausalLM(LlamaConfig(vocab_size=64, hidden_size=32, intermediate_size=64,
                                 num_hidden_layers=1, num_attention_heads=2, num_key_value_heads=1))
m(torch.tensor([[1, 2, 3]])).logits.sum().item()
print(json.dumps({'mode': _win_import.mode(), 'loaded_before_spec_mtp_body': preloaded,
                  'torch': torch.__version__, 'numpy': numpy.__version__,
                  'mkl': bool(getattr(torch.backends, 'mkl', None) and torch.backends.mkl.is_available()),
                  'threads': torch.get_num_threads()}))
'''


def run_case(name, mode, first, timeout):
    env = dict(os.environ, PYTHONUTF8='1')
    if mode is None:
        env.pop('SPEC_MTP_WIN_IMPORT_ORDER', None)
    else:
        env['SPEC_MTP_WIN_IMPORT_ORDER'] = mode
    start = time.time()
    try:
        proc = subprocess.run([sys.executable, '-c', PROBE, first], env=env, capture_output=True,
                              text=True, timeout=timeout, cwd=ROOT)
    except subprocess.TimeoutExpired:
        return {'case': name, 'ok': False, 'returncode': None, 'error': f'timeout {timeout}s'}
    out = {'case': name, 'ok': proc.returncode == 0, 'returncode': proc.returncode,
           'seconds': round(time.time() - start, 1)}
    if proc.returncode == 0:
        out.update(json.loads(proc.stdout.strip().splitlines()[-1]))
    else:
        out['error'] = (proc.stderr or proc.stdout)[-1500:]
    return out


def run_smoke(mode, timeout):
    env = dict(os.environ, PYTHONUTF8='1', SPEC_MTP_WIN_IMPORT_ORDER=mode)
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / 'smoke_tiny_llama'
        shutil.copytree(ROOT / 'studies' / 'smoke_tiny_llama', dest,
                        ignore=shutil.ignore_patterns('runs', 'shared', 'scripts', 'regression', '__pycache__'))
        try:
            proc = subprocess.run([sys.executable, '-m', 'spec_mtp', 'run', str(dest)], env=env,
                                  capture_output=True, text=True, timeout=timeout, cwd=ROOT)
        except subprocess.TimeoutExpired:
            return {'case': f'smoke:{mode}', 'ok': False, 'error': f'timeout {timeout}s'}
        return {'case': f'smoke:{mode}', 'ok': proc.returncode == 0, 'returncode': proc.returncode,
                **({} if proc.returncode == 0 else {'error': (proc.stderr or proc.stdout)[-1500:]})}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--smoke', action='store_true', help='also run studies/smoke_tiny_llama per passing mode')
    parser.add_argument('--timeout', type=int, default=300)
    parser.add_argument('--out', default='windows_selfcheck.json')
    args = parser.parse_args()
    print(f'python {sys.version.split()[0]} on {platform.platform()} ({sys.platform})')
    if sys.platform != 'win32':
        print('note: not Windows; SPEC_MTP_WIN_IMPORT_ORDER is a no-op here, results say nothing about DLLs')
    cases = [(f'spec_mtp-first:{m or "default"}', m, 'spec_mtp') for m in (None, 'torch', 'numpy', 'off')]
    cases.append(('rpipe-first', None, 'rpipe'))
    results = [run_case(n, m, f, args.timeout) for n, m, f in cases]
    if args.smoke:
        for mode in ('torch', 'numpy', 'off'):
            if any(r['ok'] and r.get('mode') == mode for r in results):
                results.append(run_smoke(mode, args.timeout * 4))
    for r in results:
        status = 'ok  ' if r['ok'] else 'FAIL'
        extra = (f"preloaded={r.get('loaded_before_spec_mtp_body')} torch={r.get('torch')} numpy={r.get('numpy')}"
                 if r['ok'] and 'torch' in r else (r.get('error', '').strip().splitlines() or [''])[-1])
        print(f'{status} {r["case"]:<28} {extra}')
    Path(args.out).write_text(json.dumps({'platform': platform.platform(), 'python': sys.version,
                                          'results': results}, indent=2), encoding='utf-8')
    print(f'wrote {args.out}')
    return 0 if all(r['ok'] for r in results) else 1


if __name__ == '__main__':
    sys.exit(main())
