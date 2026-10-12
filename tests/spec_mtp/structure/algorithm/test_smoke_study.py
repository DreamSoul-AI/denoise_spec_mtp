"""CPU smoke Study through RPipe: three mask variants, exact match against plain generation.

The pooled accept_d1 numbers are the pre-refactor baseline (b1f6191, copied
framework). They guard the migration; they are not a research result.
"""

import csv
import json


from conftest import SMOKE, cli

EXPECTED_ACCEPT_D1 = {
    'esp_static': 27,
    'esp_dynamic': 31,
    'ema_velocity': 8,
}


def _overall(study, run_id):
    with (study / 'runs' / run_id / 'assets' / 'summary.csv').open(newline='', encoding='utf-8') as handle:
        rows = [row for row in csv.DictReader(handle) if row['category'] == 'overall']
    assert len(rows) == 1
    return rows[0]


def _check_smoke(study):
    index = json.loads((study / 'index.json').read_text(encoding='utf-8'))
    seen = {}
    for experiment in index['experiments']:
        variant = experiment['factors']['algorithm.config.variant']
        run_id = experiment['runs'][0]['id']
        overall = _overall(study, run_id)
        assert float(overall['exact_match_rate']) == 1.0
        seen[variant] = int(float(overall['accept_d1']))
        result = json.loads((study / 'runs' / run_id / 'result.json').read_text(encoding='utf-8'))
        assert result['status'] == 'succeeded'
        assert result['spec_mtp']['passed'] is True
        assert result['spec_mtp']['sources']['digest'] == result['spec_mtp']['sources_digest']
        assert result['provenance']  # RPipe provenance digest of the Study
    assert seen == EXPECTED_ACCEPT_D1
    check = json.loads((study / 'spec_mtp_study_check.json').read_text(encoding='utf-8'))
    assert check['complete'] and check['passed'] and len(check['sources_digests']) == 1


def test_smoke_study_matches_plain_generation():
    """The repository Study itself, via the thin spec_mtp entry (CI path)."""
    cli('run', 'studies/smoke_tiny_llama', check=True)
    _check_smoke(SMOKE)


def test_rpipe_entry_runs_the_same_chain(study_copy):
    study = study_copy()
    cli('run', study, entry='rpipe', check=True)
    _check_smoke(study)


def test_make_then_launch_scripts_path(study_copy):
    study = study_copy()
    cli('make', study, check=True)
    assert (study / 'spec_mtp_sources.json').is_file()
    assert (study / 'scripts' / 'launch.sh').is_file()
    proc = cli('launch', study, '--console', 'shared')
    assert proc.returncode == 0, proc.stdout[-3000:] + proc.stderr[-3000:]
    _check_smoke(study)


def test_exact_match_failure_fails_the_run(study_copy):
    """Context limit 56 < prompt 32 + 32 new tokens: spec stops early, exact_match < 1."""
    def patch(study):
        study['fixed']['model']['config']['tiny']['max_position_embeddings'] = 56
        study['axes'] = {'algorithm.config.variant': ['esp_static']}
    study = study_copy(patch, name='ctx_limit')
    proc = cli('run', study)
    assert proc.returncode != 0
    index = json.loads((study / 'index.json').read_text(encoding='utf-8'))
    run_id = index['experiments'][0]['runs'][0]['id']
    result = json.loads((study / 'runs' / run_id / 'result.json').read_text(encoding='utf-8'))
    assert result['status'] == 'failed'
    assert 'exact_match_rate' in result['error']
    assert float(_overall(study, run_id)['exact_match_rate']) < 1.0


def test_bad_config_fails_before_construction(study_copy):
    def patch(study):
        study['fixed']['model']['config']['attn_implementation'] = 'flash_attention_2'
        study['axes'] = {'algorithm.config.variant': ['esp_static']}
    study = study_copy(patch, name='bad_attn')
    proc = cli('run', study)
    assert proc.returncode != 0
    index = json.loads((study / 'index.json').read_text(encoding='utf-8'))
    run_id = index['experiments'][0]['runs'][0]['id']
    result = json.loads((study / 'runs' / run_id / 'result.json').read_text(encoding='utf-8'))
    assert result['status'] == 'failed' and 'eager or sdpa' in result['error']
    assert not (study / 'runs' / run_id / 'assets' / 'summary.csv').exists()


def test_freeze_rejects_spec_mtp_change_after_make(study_copy):
    study = study_copy(lambda s: s.update(freeze=True), name='frozen')
    cli('make', study, check=True)
    lock = study / 'spec_mtp_sources.json'
    body = json.loads(lock.read_text(encoding='utf-8'))
    body['files']['spec_mtp/structure/algorithm/tree.py'] = '0' * 64  # simulate a source edit after make
    lock.write_text(json.dumps(body), encoding='utf-8')
    run_id = json.loads((study / 'index.json').read_text())['experiments'][0]['runs'][0]['id']
    proc = cli('run-one', study, run_id)
    assert proc.returncode != 0
    result = json.loads((study / 'runs' / run_id / 'result.json').read_text(encoding='utf-8'))
    assert result['status'] == 'failed' and 'tree.py' in result['error']


def test_freeze_rejects_study_change_after_make(study_copy):
    """RPipe's own freeze still covers the Study files (recipe, flow, declarations)."""
    study = study_copy(lambda s: s.update(freeze=True), name='frozen_study')
    cli('make', study, check=True)
    hook = study / 'flow' / 'write' / 'run.py'
    hook.write_text(hook.read_text(encoding='utf-8') + '\n# edited after make\n', encoding='utf-8')
    run_id = json.loads((study / 'index.json').read_text())['experiments'][0]['runs'][0]['id']
    proc = cli('run-one', study, run_id)
    assert proc.returncode != 0
    assert 'provenance changed' in (proc.stdout + proc.stderr)
