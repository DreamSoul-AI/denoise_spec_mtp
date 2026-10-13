"""SpecMTP Run / Study gates on synthetic assets (no decoding)."""

import csv
import json
from types import SimpleNamespace

import pytest

from spec_mtp.flow import checks
from spec_mtp.structure.artifact import sources
from spec_mtp.structure.artifact.evidence import digest


def _assets(tmp_path, rate='1.0', with_sources=True, overall=True, name='a'):
    assets = tmp_path / name
    assets.mkdir(parents=True)
    rows = [{'category': 'synthetic', 'exact_match_rate': rate, 'accept_d1': '5'}]
    if overall:
        rows.append({'category': 'overall', 'exact_match_rate': rate, 'accept_d1': '5'})
    with (assets / 'summary.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    cfg = _config()
    saved = sources.manifest()
    saved['config_digest'] = digest(cfg)
    study_dir = assets.parents[2]
    if (study_dir / 'study.yaml').exists():
        from rpipe.structure.artifact.provenance import source_files
        from rpipe.structure.make.expand import load_study_yaml
        saved['study_files'] = source_files(study_dir, load_study_yaml(study_dir))
    if with_sources:
        (assets / 'spec_mtp_sources.json').write_text(json.dumps(saved), encoding='utf-8')
    inputs = {'settings': {'run': {'seed': 0}, 'eval': {'run_ar_baseline': True, 'device': 'cpu'}, 'spec': {}},
              'files': {}, 'device': 'cpu', 'prompts': [{'input_ids': [1, 2], 'category': 'synthetic'}]}
    stats = {'new_tokens': 6, 'committed': 5, 'accepted': 5, 'decode_calls': 1,
             'trace': [{'root_position': 2, 'cache_before': 2, 'accepted_nodes': [1, 2, 3, 4, 5],
                        'stopped': True, 'cache_after': None, 'committed_tokens': [4, 5, 6, 7, 8]}]}
    row = {'category': 'synthetic', **{k: stats[k] for k in ('new_tokens', 'committed', 'accepted', 'decode_calls')},
           'spec_time': 1, 'ar_time': 1, 'exact_match': float(rate) if rate else 1,
           'accept_d1': 5, 'attempt_d1': 5}
    item = {'input_ids': [1, 2], 'output_ids': [1, 2, 3, 4, 5, 6, 7, 8],
            'ar_ids': [1, 2, 3, 4, 5, 6, 7, 8], 'stats': stats}
    raw = {'task': 'esp_mtp', 'inputs_digest': digest(inputs), 'out': {'rows': [row], 'evidence': [item]}}
    (assets / 'decode_inputs.json').write_text(json.dumps(inputs))
    (assets / 'decode_observations.json').write_text(json.dumps(raw))
    if overall and rate == '1.0':
        from spec_mtp.structure.algorithm.esp_mtp import _aggregate
        flat = [{'category': k, **v} for k, v in _aggregate([row]).items()]
        with (assets / 'summary.csv').open('w', newline='', encoding='utf-8') as handle:
            writer = csv.DictWriter(handle, fieldnames=list(flat[0]))
            writer.writeheader()
            writer.writerows(flat)
    return assets


def _config(task='esp_mtp', run_ar=True):
    return {'algorithm': {'config': {'task': task, 'eval': {'run_ar_baseline': run_ar}}}}


def test_exact_match_one_passes(tmp_path):
    report = checks.evaluate_run(_config(), _assets(tmp_path))
    assert report['passed'] and report['exact_match_rate'] == 1.0 and report['sources_digest'] == sources.manifest()['digest']


@pytest.mark.parametrize('kwargs, reason', [
    ({'rate': '0.75'}, 'exact_match_rate=0.75'),
    ({'rate': '0.9999'}, '!= 1'),
    ({'overall': False}, 'no single overall row'),
    ({'with_sources': False}, 'spec_mtp_sources'),
])
def test_gate_failures(tmp_path, kwargs, reason):
    report = checks.evaluate_run(_config(), _assets(tmp_path, **kwargs))
    assert not report['passed']
    assert any(reason in item for item in report['reasons'])


def test_unaudited_esp_run_fails(tmp_path):
    report = checks.evaluate_run(_config(run_ar=False), _assets(tmp_path))
    assert not report['passed'] and 'run_ar_baseline' in report['reasons'][0]


def test_run_gate_raises_and_records(tmp_path):
    assets = _assets(tmp_path, rate='0.5')
    ctx = SimpleNamespace(config=_config(), layout=SimpleNamespace(assets_dir=assets),
                          state={'result_draft': {'metrics': {}}})
    with pytest.raises(checks.SpecMtpGateError):
        checks.run_gate(ctx)
    assert ctx.state['result_draft']['spec_mtp']['passed'] is False


def _study(tmp_path, runs, axes=None, seeds=(123,)):
    import yaml

    study = tmp_path / 'study'
    (study / 'runs').mkdir(parents=True)
    (study / 'study.yaml').write_text(yaml.safe_dump(
        {'study': 'x', 'axes': axes or {'algorithm.config.variant': ['a', 'b']}, 'seeds': list(seeds)}))
    experiments = []
    for variant, status, passed, source_digest in runs:
        run_id = f'run_{variant}'
        experiments.append({'factors': {'algorithm.config.variant': variant},
                            'runs': [{'id': run_id, 'run_dir': run_id, 'seed': 123}]})
        if status is None:
            continue
        (study / 'runs' / run_id).mkdir()
        _assets(study / 'runs' / run_id, name='assets')
        (study / 'runs' / run_id / 'config.yaml').write_text(__import__('yaml').safe_dump(_config()))
        digest_value = sources.manifest()['digest'] if source_digest == 'd' else source_digest
        (study / 'runs' / run_id / 'result.json').write_text(json.dumps(
            {'status': status, 'spec_mtp': {'passed': passed, 'sources_digest': digest_value}}))
    (study / 'index.json').write_text(json.dumps({'study': 'x', 'experiments': experiments}))
    return SimpleNamespace(scope='study', study_dir=study, state={})


def test_study_gate_complete_pass(tmp_path):
    ctx = _study(tmp_path, [('a', 'succeeded', True, 'd'), ('b', 'succeeded', True, 'd')])
    assert checks.study_gate(ctx)['passed']
    assert json.loads((ctx.study_dir / checks.STUDY_CHECK_NAME).read_text())['complete']


def test_study_gate_subset_is_incomplete(tmp_path):
    ctx = _study(tmp_path, [('a', 'succeeded', True, 'd')])
    with pytest.raises(checks.SpecMtpGateError, match='incomplete'):
        checks.study_gate(ctx)
    assert ctx.state['spec_mtp']['expected_factors_match'] is False


def test_study_gate_missing_result_is_incomplete(tmp_path):
    ctx = _study(tmp_path, [('a', 'succeeded', True, 'd'), ('b', None, None, None)])
    with pytest.raises(checks.SpecMtpGateError, match='incomplete'):
        checks.study_gate(ctx)
    assert ctx.state['spec_mtp']['missing_runs'] == ['run_b']


def test_study_gate_failed_run_fails(tmp_path):
    ctx = _study(tmp_path, [('a', 'succeeded', True, 'd'), ('b', 'failed', False, 'd')])
    with pytest.raises(checks.SpecMtpGateError, match='failed'):
        checks.study_gate(ctx)


def test_study_gate_mixed_source_digest_fails(tmp_path):
    ctx = _study(tmp_path, [('a', 'succeeded', True, 'd1'), ('b', 'succeeded', True, 'd2')])
    with pytest.raises(checks.SpecMtpGateError):
        checks.study_gate(ctx)


def test_study_gate_seed_mismatch_is_incomplete(tmp_path):
    ctx = _study(tmp_path, [('a', 'succeeded', True, 'd'), ('b', 'succeeded', True, 'd')], seeds=(123, 124))
    with pytest.raises(checks.SpecMtpGateError, match='incomplete'):
        checks.study_gate(ctx)


def test_study_gate_skips_run_scope():
    assert checks.study_gate(SimpleNamespace(scope='run')) == {}


# ------------------------------------------------------------ edge branches

def test_ar_baseline_needs_summary(tmp_path):
    empty = tmp_path / 'empty'
    empty.mkdir()
    (empty / 'spec_mtp_sources.json').write_text('{"digest": "d"}')
    assert checks.evaluate_run(_config('ar_baseline'), empty)['reasons'] == ['missing summary.csv']
    assert checks.evaluate_run(_config('ar_baseline'), _assets(tmp_path))['passed']


def test_alignment_probe_needs_its_csv(tmp_path):
    assets = _assets(tmp_path)
    assert checks.evaluate_run(_config('alignment_probe'), assets)['reasons'] == ['missing alignment_metrics.csv']
    (assets / 'alignment_metrics.csv').write_text('layer\n1\n')
    assert checks.evaluate_run(_config('alignment_probe'), assets)['passed']


def test_empty_rate_is_missing(tmp_path):
    report = checks.evaluate_run(_config(), _assets(tmp_path, rate=''))
    assert report['reasons'] == ['exact_match_rate missing'] and report['exact_match_rate'] is None


def test_two_overall_rows_are_rejected(tmp_path):
    assets = _assets(tmp_path)
    with (assets / 'summary.csv').open('a', newline='', encoding='utf-8') as handle:
        handle.write('overall,1.0,5\n')
    assert 'summary.csv has no single overall row' in checks.evaluate_run(_config(), assets)['reasons']


def test_task_name_is_case_insensitive(tmp_path):
    assert checks.evaluate_run(_config('ESP_MTP'), _assets(tmp_path))['task'] == 'esp_mtp'


def test_run_gate_without_draft_still_gates(tmp_path):
    ctx = SimpleNamespace(config=_config(), layout=SimpleNamespace(assets_dir=_assets(tmp_path)), state={})
    assert checks.run_gate(ctx)['passed']
    bad = SimpleNamespace(config=_config(), layout=SimpleNamespace(assets_dir=_assets(tmp_path, '0.5', name='b')),
                          state={})
    with pytest.raises(checks.SpecMtpGateError, match='exact_match_rate=0.5 != 1'):
        checks.run_gate(bad)


def test_study_gate_empty_index_is_incomplete(tmp_path):
    ctx = _study(tmp_path, [])
    with pytest.raises(checks.SpecMtpGateError, match='incomplete'):
        checks.study_gate(ctx)
    assert ctx.state['spec_mtp']['complete'] is False


def test_study_gate_explicit_expected_factors(tmp_path):
    ctx = _study(tmp_path, [('a', 'succeeded', True, 'd'), ('b', 'succeeded', True, 'd')])
    expected = [{'algorithm.config.variant': 'b'}, {'algorithm.config.variant': 'a'}]
    assert checks.study_gate(ctx, expected_factors=expected)['passed']


def test_declared_factors_without_axes():
    assert checks.declared_factors({}) == [{}]


@pytest.mark.parametrize('name', ['decode_inputs.json', 'decode_observations.json', 'spec_mtp_sources.json'])
def test_final_gate_requires_raw_evidence(tmp_path, name):
    assets = _assets(tmp_path)
    (assets / name).unlink()
    ctx = SimpleNamespace(config=_config(), layout=SimpleNamespace(assets_dir=assets), state={})
    with pytest.raises(checks.SpecMtpGateError):
        checks.run_gate(ctx)


def test_final_gate_rejects_token_mismatch_even_when_summary_passes(tmp_path):
    assets = _assets(tmp_path)
    path = assets / 'decode_observations.json'
    body = json.loads(path.read_text())
    body['out']['evidence'][0]['ar_ids'][-1] = 99
    path.write_text(json.dumps(body))
    ctx = SimpleNamespace(config=_config(), layout=SimpleNamespace(assets_dir=assets), state={})
    with pytest.raises(checks.SpecMtpGateError, match='raw exact_match'):
        checks.run_gate(ctx)


def test_final_gate_rejects_source_drift(tmp_path):
    assets = _assets(tmp_path)
    path = assets / 'spec_mtp_sources.json'
    body = json.loads(path.read_text())
    body['files']['spec_mtp/added.py'] = 'bad'
    path.write_text(json.dumps(body))
    ctx = SimpleNamespace(config=_config(), layout=SimpleNamespace(assets_dir=assets), state={})
    with pytest.raises(checks.SpecMtpGateError, match='sources changed'):
        checks.run_gate(ctx)


def test_final_gate_rejects_config_drift(tmp_path):
    assets = _assets(tmp_path)
    config = _config()
    config['model'] = {'name': 'changed'}
    ctx = SimpleNamespace(config=config, layout=SimpleNamespace(assets_dir=assets), state={})
    with pytest.raises(checks.SpecMtpGateError, match='configuration changed'):
        checks.run_gate(ctx)


def test_study_gate_rechecks_missing_evidence(tmp_path):
    ctx = _study(tmp_path, [('a', 'succeeded', True, 'd'), ('b', 'succeeded', True, 'd')])
    (ctx.study_dir / 'runs/run_b/assets/decode_observations.json').unlink()
    with pytest.raises(checks.SpecMtpGateError):
        checks.study_gate(ctx)
    assert ctx.state['spec_mtp']['failed_runs'] == ['run_b']


def test_legacy_axis_seed_is_not_an_experiment_factor():
    assert checks.declared_factors({'axes': {'seed': [1, 2], 'x': ['a']}}) == [{'x': 'a'}]


def test_final_gate_rejects_live_input_file_drift(tmp_path):
    from spec_mtp.structure.artifact.evidence import file_hash
    assets = _assets(tmp_path)
    source = tmp_path / 'prompt.txt'
    source.write_text('before')
    path = assets / 'decode_inputs.json'
    inputs = json.loads(path.read_text())
    inputs['files'] = {str(source): file_hash(source)}
    path.write_text(json.dumps(inputs))
    raw_path = assets / 'decode_observations.json'
    raw = json.loads(raw_path.read_text())
    raw['inputs_digest'] = digest(inputs)
    raw_path.write_text(json.dumps(raw))
    source.write_text('after')
    with pytest.raises(checks.SpecMtpGateError, match='input changed'):
        checks.run_gate(SimpleNamespace(config=_config(), layout=SimpleNamespace(assets_dir=assets), state={}))


def test_cuda_device_alias_does_not_look_like_config_drift(tmp_path):
    assets = _assets(tmp_path)
    path = assets / 'decode_inputs.json'
    inputs = json.loads(path.read_text())
    inputs['device'] = 'cuda:0'
    inputs['settings']['eval']['device'] = 'cuda'
    path.write_text(json.dumps(inputs))
    raw_path = assets / 'decode_observations.json'
    raw = json.loads(raw_path.read_text())
    raw['inputs_digest'] = digest(inputs)
    raw_path.write_text(json.dumps(raw))
    checks.verify_evidence(_config(), assets)
