"""Single CPU check entry for local runs and CI.

    python scripts/run_ci_checks.py                 # plan cpu_pr_checks
    python scripts/run_ci_checks.py --plan cpu_smoke_only

Every run writes .test-results/<run_id>/ with manifest.json, results.jsonl
(one line per check, appended as each check finishes) and report.md. The
report is written even when a check fails, so partial evidence survives.
Smoke runs write under the run directory, never under results/, so they
cannot mix rows into a collaborator's CSVs (the Logger appends).
"""

import argparse
import datetime
import json
import os
import platform
import subprocess
import sys
import time
import uuid

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

SMOKE_STUDY = 'studies/smoke_tiny_llama'
SMOKE_RUNS = 3
SMOKE_BASELINE_ACCEPTED = {
    'esp_static': 27,
    'esp_dynamic': 31,
    'ema_velocity': 8,
}

PLANS = {
    'cpu_pr_checks': ['correctness', 'ema_history', 'smoke'],
    'cpu_smoke_only': ['smoke'],
}


def _git(*args):
    try:
        return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return 'unknown'


def _environment():
    env = {'python': sys.version.split()[0], 'platform': platform.platform()}
    try:
        import torch
        import transformers
        env['torch'] = torch.__version__
        env['transformers'] = transformers.__version__
        env['cuda_available'] = bool(torch.cuda.is_available())
    except ImportError as exc:
        env['import_error'] = str(exc)
    return env


def _read_summary(path):
    import csv
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def _run_env():
    return {
        **os.environ,
        'PYTHONUTF8': '1',
        'PYTHONPATH': os.path.join(ROOT, 'src'),
        'MPLBACKEND': 'Agg',
    }


def _run(cmd, log_path):
    start = time.perf_counter()
    with open(log_path, 'w', encoding='utf-8') as log:
        proc = subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                              text=True, env=_run_env())
    return proc.returncode, time.perf_counter() - start


def _checks_for(plan, run_dir):
    checks = []
    for group in PLANS[plan]:
        if group == 'correctness':
            checks.append(('correctness',
                           [sys.executable, 'tests/spec_mtp/spec/test_correctness.py'], None))
        elif group == 'ema_history':
            checks.append(('ema_history',
                           [sys.executable, 'tests/spec_mtp/spec/test_ema_history.py'], None))
        elif group == 'smoke':
            checks.append(('rpipe_smoke',
                           [sys.executable, '-m', 'rpipe', 'run', SMOKE_STUDY],
                           'rpipe_study'))
    return checks


def _nested_get(mapping, dotted, default=None):
    cur = mapping
    for key in dotted.split('.'):
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def _rpipe_smoke_detail():
    import yaml

    runs_root = os.path.join(ROOT, SMOKE_STUDY, 'runs')
    if not os.path.isdir(runs_root):
        return 'failed', f'missing {runs_root}'
    detail = {}
    for entry in sorted(os.listdir(runs_root)):
        run_dir = os.path.join(runs_root, entry)
        cfg_path = os.path.join(run_dir, 'config.yaml')
        summary_path = os.path.join(run_dir, 'assets', 'summary.csv')
        if not os.path.isfile(summary_path):
            continue
        with open(cfg_path, encoding='utf-8') as handle:
            cfg = yaml.safe_load(handle) or {}
        variant = _nested_get(cfg, 'algorithm.config.variant')
        rows = _read_summary(summary_path)
        overall = [r for r in rows if r.get('category') == 'overall']
        if len(overall) != 1:
            return 'failed', f'overall row missing in {summary_path}'
        row = overall[0]
        if float(row.get('exact_match_rate', 0.0)) != 1.0:
            return 'failed', f'exact_match_rate={row.get("exact_match_rate")} in {summary_path}'
        accepted = int(float(row.get('accept_d1', 0)))
        if variant in SMOKE_BASELINE_ACCEPTED and accepted != SMOKE_BASELINE_ACCEPTED[variant]:
            return 'failed', (
                f'{variant} accept_d1={accepted}, expected {SMOKE_BASELINE_ACCEPTED[variant]}')
        label = str(variant or entry)
        detail[label] = {
            'accept_d1': accepted,
            'exact_match_rate': row.get('exact_match_rate'),
            'tau': row.get('tau'),
        }
    if len(detail) != SMOKE_RUNS:
        return 'failed', f'expected {SMOKE_RUNS} runs, got {len(detail)}'
    return 'passed', detail


def _verdict(returncode, summary_path):
    """Process exit is necessary; smoke also needs exact_match_rate == 1."""
    if returncode != 0:
        return 'failed', None
    if summary_path == 'rpipe_study':
        return _rpipe_smoke_detail()
    if summary_path is None:
        return 'passed', None
    if not os.path.exists(summary_path):
        return 'failed', 'summary.csv missing'
    rows = _read_summary(summary_path)
    overall = [r for r in rows if r.get('category') == 'overall']
    if len(overall) != 1:
        return 'failed', f'expected one overall row, got {len(overall)}'
    row = overall[0]
    if float(row.get('exact_match_rate', 0.0)) != 1.0:
        return 'failed', f'exact_match_rate={row.get("exact_match_rate")}'
    return 'passed', {k: row[k] for k in ('tau', 'exact_match_rate', 'tokens_per_s', 'speedup') if k in row}


def _write_report(run_dir, manifest, results):
    lines = [
        f'# CPU check report `{manifest["run_id"]}`', '',
        f'- plan_id: `{manifest["plan_id"]}`',
        f'- commit: `{manifest["commit"]}` (dirty: {manifest["dirty"]})',
        f'- branch: `{manifest["branch"]}`',
        f'- environment: `{json.dumps(manifest["environment"])}`',
        f'- status: **{manifest["status"]}**', '',
        '| **check** | **verdict** | **seconds** | **detail** |',
        '| --- | --- | --- | --- |',
    ]
    for r in results:
        detail = json.dumps(r['detail']) if r['detail'] is not None else ''
        lines.append(f'| {r["check"]} | {r["verdict"]} | {r["seconds"]:.1f} | {detail} |')
    not_run = [c for c in manifest['selected'] if c not in {r['check'] for r in results}]
    lines += ['', f'Checks: {len(results)} run / {len(manifest["selected"])} selected; '
              f'passed {sum(r["verdict"] == "passed" for r in results)}.']
    if not_run:
        lines.append(f'Not run: {", ".join(not_run)}.')
    lines += ['', 'Smoke tau comes from a random tiny LLaMA and is a pipeline check, '
              'not a method comparison. GPU model runs are outside this plan.', '']
    with open(os.path.join(run_dir, 'report.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(description='CPU CI checks')
    parser.add_argument('--plan', default='cpu_pr_checks', choices=sorted(PLANS))
    parser.add_argument('--out', default='.test-results')
    args = parser.parse_args()

    stamp = datetime.datetime.now().astimezone().strftime('%Y%m%dT%H%M%S%z')
    run_id = f'{stamp}_{uuid.uuid4().hex[:6]}'
    run_dir = os.path.join(ROOT, args.out, run_id)
    os.makedirs(run_dir, exist_ok=True)

    checks = _checks_for(args.plan, run_dir)
    manifest = {
        'run_id': run_id,
        'plan_id': args.plan,
        'commit': _git('rev-parse', 'HEAD'),
        'branch': _git('rev-parse', '--abbrev-ref', 'HEAD'),
        'dirty': _git('status', '--porcelain') not in ('', 'unknown'),
        'environment': _environment(),
        'selected': [name for name, _, _ in checks],
        'commands': {name: cmd for name, cmd, _ in checks},
        'status': 'running',
    }
    manifest_path = os.path.join(run_dir, 'manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    results = []
    try:
        for name, cmd, summary in checks:
            code, seconds = _run(cmd, os.path.join(run_dir, f'{name}.log'))
            verdict, detail = _verdict(code, summary)
            result = {'check': name, 'returncode': code, 'verdict': verdict,
                      'seconds': seconds, 'detail': detail,
                      'log': f'{name}.log'}
            results.append(result)
            with open(os.path.join(run_dir, 'results.jsonl'), 'a', encoding='utf-8') as f:
                f.write(json.dumps(result) + '\n')
            print(f'[{verdict}] {name} ({seconds:.1f}s)')
    finally:
        complete = len(results) == len(checks)
        all_passed = complete and all(r['verdict'] == 'passed' for r in results)
        manifest['status'] = 'passed' if all_passed else ('failed' if complete else 'incomplete')
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        _write_report(run_dir, manifest, results)
        print(f'report: {os.path.relpath(os.path.join(run_dir, "report.md"), ROOT)}')

    sys.exit(0 if manifest['status'] == 'passed' else 1)


if __name__ == '__main__':
    main()
