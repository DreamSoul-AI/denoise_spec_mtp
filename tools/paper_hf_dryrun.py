"""Weight-free dry run of studies/paper_hf: the full Study chain on a tiny stand-in.

    python tools/paper_hf_dryrun.py                     # every Study, every cell
    python tools/paper_hf_dryrun.py --study qwen3_8b_main --cells 2
    python tools/paper_hf_dryrun.py --out .tmp/paper_hf_dryrun.json

Each paper_hf Study is copied to a temp dir and only its *substrate* is swapped:

- model  -> ``tiny_llama`` (random weights, 2 layers, vocab 256; the HF ``name_or_path``
  is dropped, nothing is downloaded);
- data   -> ``local_prompts`` synthetic (2 prompts, 32 tokens);
- eval   -> ``max_new_tokens`` 16, ``num_eval_prompts`` 2, ``probe_steps_per_prompt`` 4;
- system -> ``device: cpu``.

Everything else is kept verbatim: task, temperature, ``stop_on_eos``,
``run_ar_baseline``, every ``algorithm.config.variant`` preset (masks, trees,
impl, EMA settings), seeds, recipe, flow hooks and the exact_match gate. Then
``python -m spec_mtp run <copy>`` runs prepare → execute → write gate →
Study-scope process. The point is that every paper preset is accepted by the
recipe, builds a decoder, decodes losslessly on a real (tiny) transformer and
passes the gates. It says nothing about acceptance on the real models, GPU,
bf16 or memory.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / 'studies' / 'paper_hf'
TINY = {'vocab_size': 256, 'hidden_size': 64, 'intermediate_size': 128, 'num_layers': 2,
        'num_heads': 4, 'num_kv_heads': 2, 'max_position_embeddings': 1024}
EVAL_OVERRIDES = {'max_new_tokens': 16, 'num_eval_prompts': 2, 'probe_steps_per_prompt': 4}


def substitute(study: dict, cells: int | None) -> dict:
    """Swap model / data / eval budget / device; keep every algorithm factor."""
    study = json.loads(json.dumps(study))
    fixed = study['fixed']
    attn = (fixed['model'].get('config') or {}).get('attn_implementation', 'eager')
    fixed['model'] = {'name': 'tiny_llama', 'source': 'spec_mtp',
                      'config': {'attn_implementation': attn, 'tiny': dict(TINY)}}
    fixed['data'] = {'name': 'local_prompts', 'source': 'spec_mtp',
                     'config': {'mode': 'synthetic', 'vocab_size': 256, 'prompt_len': 32,
                                'num_prompts': 2, 'seed': 0}}
    eval_cfg = fixed['algorithm']['config'].setdefault('eval', {})
    eval_cfg.update(EVAL_OVERRIDES)
    fixed['system'] = {'config': {**fixed.get('system', {}).get('config', {}), 'device': 'cpu'}}
    if cells is not None:
        for key, values in (study.get('axes') or {}).items():
            study['axes'][key] = values[:cells]
    study['description'] = 'paper_hf dry run on tiny_llama (not a result)'
    return study


def base_config(study: dict) -> dict:
    fixed = study['fixed']
    return {'experiment': study['experiment']['name'], 'description': 'dry-run base',
            'seed': study['seeds'][0], 'data': fixed['data'], 'model': fixed['model'],
            'algorithm': fixed['algorithm'], 'system': fixed['system']}


def prepare(name: str, dest: Path, cells: int | None) -> Path:
    src = PAPER / name
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns('runs', 'shared', 'scripts', 'docs', '__pycache__'))
    study = substitute(yaml.safe_load((src / 'study.yaml').read_text(encoding='utf-8')), cells)
    (dest / 'study.yaml').write_text(yaml.safe_dump(study, sort_keys=False), encoding='utf-8')
    (dest / 'experiment_config.yaml').write_text(yaml.safe_dump(base_config(study), sort_keys=False),
                                                 encoding='utf-8')
    return dest


def collect(dest: Path) -> list[dict]:
    rows = []
    for result in sorted((dest / 'runs').glob('*/result.json')):
        body = json.loads(result.read_text(encoding='utf-8'))
        config = yaml.safe_load((result.parent / 'config.yaml').read_text(encoding='utf-8'))
        gate = body.get('spec_mtp') or {}
        rows.append({'variant': (config['algorithm'].get('config') or {}).get('variant'),
                     'status': body.get('status'), 'gate_passed': gate.get('passed'),
                     'exact_match_rate': gate.get('exact_match_rate'), 'reasons': gate.get('reasons')})
    return rows


def run_study(name: str, cells: int | None, timeout: int, keep: Path | None) -> dict:
    tmp = Path(tempfile.mkdtemp(prefix='paper_hf_dry_'))
    try:
        dest = prepare(name, (keep or tmp) / name, cells)
        env = dict(os.environ, PYTHONUTF8='1')
        start = time.time()
        proc = subprocess.run([sys.executable, '-m', 'spec_mtp', 'run', str(dest)], cwd=ROOT, env=env,
                              capture_output=True, text=True, timeout=timeout)
        runs = collect(dest)
        check = dest / 'spec_mtp_study_check.json'
        study_check = json.loads(check.read_text(encoding='utf-8')) if check.is_file() else None
        expected = len(yaml.safe_load((dest / 'study.yaml').read_text(encoding='utf-8'))
                       .get('axes', {}).get('algorithm.config.variant', [None]))
        ok = (proc.returncode == 0 and len(runs) == expected
              and all(r['status'] == 'succeeded' and r['gate_passed'] for r in runs)
              and bool(study_check and study_check.get('passed')))
        out = {'study': name, 'ok': ok, 'returncode': proc.returncode, 'runs': runs, 'expected_runs': expected,
               'study_gate_passed': bool(study_check and study_check.get('passed')),
               'seconds': round(time.time() - start, 1)}
        if not ok:
            out['log_tail'] = (proc.stderr or proc.stdout)[-3000:]
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--study', action='append', help='paper_hf Study name (repeatable); default all')
    parser.add_argument('--cells', type=int, default=None, help='first N variants per Study')
    parser.add_argument('--timeout', type=int, default=900)
    parser.add_argument('--out', default=None, help='write the JSON report here')
    parser.add_argument('--keep', default=None, help='keep the Study copies under this directory')
    args = parser.parse_args(argv)
    names = args.study or sorted(p.name for p in PAPER.iterdir() if (p / 'study.yaml').is_file())
    keep = Path(args.keep).resolve() if args.keep else None
    if keep:
        keep.mkdir(parents=True, exist_ok=True)
    results = []
    for name in names:
        result = run_study(name, args.cells, args.timeout, keep)
        results.append(result)
        rates = sorted({str(r['exact_match_rate']) for r in result['runs']})
        print(f"{'ok  ' if result['ok'] else 'FAIL'} {name:<32} runs={len(result['runs'])}/{result['expected_runs']}"
              f" exact_match={','.join(rates)} {result['seconds']}s")
        if not result['ok']:
            print(result.get('log_tail', ''))
    report = {'stand_in': {'model': TINY, 'eval': EVAL_OVERRIDES, 'device': 'cpu'}, 'results': results,
              'ok': all(r['ok'] for r in results)}
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(report, indent=1) + '\n', encoding='utf-8')
    total = sum(len(r['runs']) for r in results)
    print(f"{'ok' if report['ok'] else 'FAIL'}: {len(results)} Studies, {total} Runs")
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
