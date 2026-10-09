"""CPU smoke Study: three mask variants, exact match against plain generation."""

import os
import subprocess
import sys

import yaml

STUDY = 'studies/smoke_tiny_llama'
EXPECTED_ACCEPT_D1 = {
    'esp_static': 27,
    'esp_dynamic': 31,
    'ema_velocity': 8,
}


def test_smoke_study_matches_plain_generation():
    env = {
        **os.environ,
        'PYTHONUTF8': '1',
        'MPLBACKEND': 'Agg',
        'PYTHONPATH': os.path.join(os.getcwd(), 'src'),
    }
    subprocess.run(
        [sys.executable, '-m', 'spec_mtp', 'run', STUDY],
        check=True, env=env,
    )
    with open(os.path.join(STUDY, 'index.json'), encoding='utf-8') as handle:
        index = yaml.safe_load(handle)
    seen = {}
    for experiment in index['experiments']:
        variant = experiment['factors']['algorithm.config.variant']
        run_id = experiment['runs'][0]['id']
        summary = os.path.join(STUDY, 'runs', run_id, 'assets', 'summary.csv')
        import csv
        with open(summary, newline='', encoding='utf-8') as handle:
            rows = list(csv.DictReader(handle))
        overall = [row for row in rows if row['category'] == 'overall']
        assert len(overall) == 1
        assert float(overall[0]['exact_match_rate']) == 1.0
        seen[variant] = int(float(overall[0]['accept_d1']))
    assert seen == EXPECTED_ACCEPT_D1
