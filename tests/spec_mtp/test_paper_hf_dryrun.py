"""tools/paper_hf_dryrun.py: substrate swap keeps every algorithm factor; one tiny chain per task."""

import importlib.util
import json
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('paper_hf_dryrun', ROOT / 'tools' / 'paper_hf_dryrun.py')
dryrun = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dryrun)


def _study(name):
    return yaml.safe_load((ROOT / 'studies/paper_hf' / name / 'study.yaml').read_text(encoding='utf-8'))


@pytest.mark.parametrize('name', ['qwen3_8b_main', 'llama3_2_3b_ablations_temp1p0', 'llama3_2_3b_alignment_probe'])
def test_substitute_only_touches_the_substrate(name):
    before = _study(name)
    after = dryrun.substitute(before, None)
    assert after['fixed']['model']['name'] == 'tiny_llama'
    assert 'name_or_path' not in json.dumps(after['fixed']['model'])
    assert after['fixed']['data']['config']['mode'] == 'synthetic'
    assert after['fixed']['system']['config']['device'] == 'cpu'
    assert after['axes'] == before['axes'] and after['seeds'] == before['seeds']
    assert after['recipe'] == before['recipe'] and after['flow'] == before['flow']
    kept_algo = {k: v for k, v in after['fixed']['algorithm']['config'].items() if k != 'eval'}
    assert kept_algo == {k: v for k, v in before['fixed']['algorithm']['config'].items() if k != 'eval'}
    eval_after, eval_before = after['fixed']['algorithm']['config']['eval'], before['fixed']['algorithm']['config']['eval']
    for key, value in eval_before.items():
        if key not in dryrun.EVAL_OVERRIDES:
            assert eval_after[key] == value, key
    assert before['fixed']['model']['name'] == 'hf_causal'  # input not mutated


def test_cells_limits_axes():
    assert dryrun.substitute(_study('qwen3_8b_main'), 2)['axes']['algorithm.config.variant'] == \
        _study('qwen3_8b_main')['axes']['algorithm.config.variant'][:2]


def test_one_cell_per_task_runs_through_the_gates(tmp_path):
    out = tmp_path / 'report.json'
    code = dryrun.main(['--study', 'qwen3_8b_main', '--study', 'llama3_2_3b_ablations_temp1p0',
                        '--study', 'llama3_2_3b_ar_baseline', '--study', 'llama3_2_3b_alignment_probe',
                        '--cells', '1', '--out', str(out)])
    report = json.loads(out.read_text(encoding='utf-8'))
    assert code == 0, json.dumps(report, indent=1)[-3000:]
    assert [len(r['runs']) for r in report['results']] == [1, 1, 1, 1]
    rates = {r['study']: r['runs'][0]['exact_match_rate'] for r in report['results']}
    assert rates['qwen3_8b_main'] == 1.0 and rates['llama3_2_3b_ablations_temp1p0'] == 1.0


def test_list_prints_studies(capsys):
    assert dryrun.main(['--list']) == 0
    out = capsys.readouterr().out
    assert 'qwen3_8b_main\t10\tesp_mtp' in out
    assert 'llama3_2_3b_alignment_probe\t1\talignment_probe' in out
