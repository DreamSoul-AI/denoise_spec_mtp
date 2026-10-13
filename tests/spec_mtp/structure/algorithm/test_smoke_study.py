"""CPU smoke Study through RPipe: three mask variants, exact match against plain generation.

The pooled accept_d1 numbers are the pre-refactor baseline (b1f6191, copied
framework). They guard the migration; they are not a research result.
"""

import csv
import json


from conftest import cli

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


def test_smoke_study_matches_plain_generation(study_copy):
    """The repository Study itself, via the thin spec_mtp entry (CI path)."""
    study = study_copy(name='fresh_smoke')
    cli('run', study, check=True)
    _check_smoke(study)


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


def test_context_limit_run_passes_on_reached_budget(study_copy):
    """Option A: context limit 56 < 32 + 32; AR is audited on the budget the speculative pass reached."""
    def patch(study):
        study['fixed']['model']['config']['tiny']['max_position_embeddings'] = 56
        study['axes'] = {'algorithm.config.variant': ['esp_static']}
    study = study_copy(patch, name='ctx_limit')
    cli('run', study, check=True)
    run_id = json.loads((study / 'index.json').read_text())['experiments'][0]['runs'][0]['id']
    assert float(_overall(study, run_id)['exact_match_rate']) == 1.0


def test_unaudited_run_fails_the_gate(study_copy):
    def patch(study):
        study['fixed']['algorithm']['config']['eval']['run_ar_baseline'] = False
        study['axes'] = {'algorithm.config.variant': ['esp_static']}
    study = study_copy(patch, name='unaudited')
    proc = cli('run', study)
    assert proc.returncode != 0
    run_id = json.loads((study / 'index.json').read_text())['experiments'][0]['runs'][0]['id']
    result = json.loads((study / 'runs' / run_id / 'result.json').read_text(encoding='utf-8'))
    assert result['status'] == 'failed' and 'run_ar_baseline' in result['error']


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
    assert not (study / 'runs' / run_id / 'result.json').exists()
    assert 'tree.py' in proc.stderr


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


def test_alignment_probe_writes_metrics_and_passes_the_gate(study_copy):
    """The probe's artifact is alignment_metrics.csv; the gate needs it (was dropped before 2026-10-12)."""
    def patch(study):
        study['fixed']['algorithm']['config']['task'] = 'alignment_probe'
        study['fixed']['algorithm']['config']['eval']['probe_steps_per_prompt'] = 4
        study['axes'] = {'algorithm.config.variant': ['esp_static']}
    study = study_copy(patch, name='probe')
    cli('run', study, check=True)
    run_id = json.loads((study / 'index.json').read_text())['experiments'][0]['runs'][0]['id']
    with (study / 'runs' / run_id / 'assets' / 'alignment_metrics.csv').open(encoding='utf-8') as handle:
        rows = list(csv.DictReader(handle))
    assert [int(r['layer']) for r in rows] == [1, 2]
    assert all(int(r['n_accepted']) + int(r['n_rejected']) > 0 for r in rows)
    result = json.loads((study / 'runs' / run_id / 'result.json').read_text(encoding='utf-8'))
    assert result['status'] == 'succeeded' and result['spec_mtp']['passed']


def test_ar_baseline_runs_the_same_stage_chain(study_copy):
    def patch(study):
        study['fixed']['algorithm']['config']['task'] = 'ar_baseline'
        study['axes'] = {'algorithm.config.variant': ['esp_static']}
    study = study_copy(patch, name='ar_stage_chain')
    cli('run', study, check=True)
    run_id = json.loads((study / 'index.json').read_text())['experiments'][0]['runs'][0]['id']
    root = study / 'runs' / run_id
    result = json.loads((root / 'result.json').read_text())
    raw = json.loads((root / 'assets/decode_observations.json').read_text())
    assert result['status'] == 'succeeded' and result['spec_mtp']['passed']
    assert len(raw['out']['evidence']) == 4
    assert all(len(item['output_ids']) == 64 for item in raw['out']['evidence'])


def test_raw_mismatch_fails_before_success_is_written(study_copy):
    study = study_copy(name='raw_mismatch')
    hook = study / 'flow/collect/run.py'
    hook.write_text("""from spec_mtp.flow.collect import run as collect

def run(ctx):
    collect(ctx)
    import json
    from pathlib import Path
    path = Path(ctx.layout.assets_dir) / 'decode_observations.json'
    raw = json.loads(path.read_text())
    raw['out']['evidence'][0]['ar_ids'][-1] = -1
    path.write_text(json.dumps(raw))
""")
    proc = cli('run', study)
    assert proc.returncode != 0
    index = json.loads((study / 'index.json').read_text())
    for experiment in index['experiments']:
        root = study / 'runs' / experiment['runs'][0]['id']
        if (root / 'result.json').is_file():
            result = json.loads((root / 'result.json').read_text())
            assert result['status'] == 'failed' and 'raw exact_match' in result['error']


def test_source_preflight_preserves_existing_result(study_copy):
    study = study_copy(name='preserve_previous_result')
    cli('make', study, check=True)
    run_id = json.loads((study / 'index.json').read_text())['experiments'][0]['runs'][0]['id']
    result = study / 'runs' / run_id / 'result.json'
    original = b'{"status":"succeeded","previous_evidence":"do not replace"}'
    result.write_bytes(original)
    lock = study / 'spec_mtp_sources.json'
    saved = json.loads(lock.read_text())
    saved['files']['spec_mtp/new.py'] = 'old'
    lock.write_text(json.dumps(saved))
    for command in ('run', 'launch', 'run-one', 'process'):
        proc = cli(command, study, *([run_id] if command == 'run-one' else []))
        assert proc.returncode != 0 and 'sources changed' in proc.stderr
        assert result.read_bytes() == original
