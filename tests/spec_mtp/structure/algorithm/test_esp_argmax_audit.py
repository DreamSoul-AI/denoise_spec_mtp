import importlib.util
import json
from pathlib import Path
import pytest
import torch
from spec_mtp.structure.algorithm import decoding
from spec_mtp.structure.control.named import _convert
from spec_mtp.structure.model.hf_causal import HFCausalLM

ROOT = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location('esp_argmax_audit', ROOT/'studies/esp_table1_bf16_full_argmax/argmax_audit.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def decoder():
    torch.manual_seed(7)
    model = HFCausalLM(tiny_config={'vocab_size':32, 'hidden_size':16, 'intermediate_size':32,
        'num_layers':1, 'num_heads':2, 'num_kv_heads':1, 'max_position_embeddings':64}).to(torch.bfloat16)
    config = _convert({'method':'esp', 'num_masks':1, 'block_complexity':10, 'impl':'naive',
        'tree':{'mode':'dynamic','pruning':True}, 'mask':{'init':'mean_prompt','lam':.1,'update':True}})
    return decoding.SpecDecoder(model, config, {'temperature':0, 'max_new_tokens':7, 'stop_on_eos':False})


@pytest.mark.parametrize('prefill_only', [False, True])
def test_observer_preserves_bf16_outputs_calls_and_restores(tmp_path, prefill_only):
    dec = decoder()
    if prefill_only:
        dec.max_new_tokens = 1
    prompt = torch.tensor([[1,2,3]])
    expected, base = dec.generate(prompt)
    generate, select = decoding.SpecDecoder.generate, decoding.select_token
    with audit.observe_argmax(tmp_path):
        actual, stats = dec.generate(prompt)
        # Independent AR remains outside the observer.
        decoding.ar_generate(dec.model, prompt, {'temperature':0,'max_new_tokens':1})
    assert torch.equal(actual, expected)
    assert stats['decode_calls'] == base['decode_calls']
    assert stats['trace'] == base['trace']
    assert decoding.SpecDecoder.generate is generate and decoding.select_token is select
    assert not dec.model._forward_hooks
    recorded = json.loads((tmp_path/'argmax_audit.jsonl').read_text())
    assert recorded == stats['verification_argmax_audit']
    assert recorded['passed'] and recorded['checked_committed_tokens'] == stats['new_tokens']
    with pytest.raises(AssertionError, match='old audit'):
        with audit.observe_argmax(tmp_path):
            pass


def test_wrong_selection_is_rejected_and_restored(tmp_path, monkeypatch):
    dec = decoder()
    wrong = lambda row, temperature, generator: (int(row.argmax().item()) + 1) % row.numel()
    monkeypatch.setattr(decoding, 'select_token', wrong)
    generate = decoding.SpecDecoder.generate
    with pytest.raises(AssertionError, match='forward argmax'):
        with audit.observe_argmax(tmp_path):
            dec.generate(torch.tensor([[1,2,3]]))
    assert decoding.select_token is wrong and decoding.SpecDecoder.generate is generate
    assert not dec.model._forward_hooks and not (tmp_path/'argmax_audit.jsonl').read_text()


def test_eos_or_budget_trim_is_not_counted_as_committed_and_wrong_owner_fails():
    selections = [{'forward':0,'row':1,'chosen':7,'argmax':7},
                  {'forward':1,'row':0,'chosen':8,'argmax':8},
                  {'forward':1,'row':2,'chosen':9,'argmax':9},
                  {'forward':1,'row':3,'chosen':10,'argmax':10}]
    stats = {'trace':[{'accepted_nodes':[2,3],'committed_tokens':[8]}], 'new_tokens':2,'committed':1}
    result = audit.bind_committed([1,2],[1,2,7,8],stats,selections)
    assert result['checked_committed_tokens']==2 and result['selected_tokens_including_trimmed_tail']==4
    selections[2]['row']=4
    with pytest.raises(AssertionError):
        audit.bind_committed([1,2],[1,2,7,8],stats,selections)


def test_tau_aggregation_does_not_gate_on_ar_and_keeps_all_weights(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'studies/esp_table1_bf16_full_argmax'))
    spec = importlib.util.spec_from_file_location('argmax_report',ROOT/'studies/esp_table1_bf16_full_argmax/analyze_results.py')
    report = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(report)
    rows = [{'category':'a','committed':4,'decode_calls':4,'accepted':0,'exact':False,'argmax_passed':True,'argmax_checked_tokens':5},
            {'category':'a','committed':4,'decode_calls':2,'accepted':2,'exact':True,'argmax_passed':True,'argmax_checked_tokens':5},
            {'category':'b','committed':9,'decode_calls':3,'accepted':6,'exact':False,'argmax_passed':True,'argmax_checked_tokens':10}]
    summary = report.summarize(rows)
    assert summary['AR_exact_rate']==pytest.approx(1/3)
    assert summary['argmax_all_passed'] and summary['argmax_checked_tokens']==20
    assert summary['pooled_tau']==pytest.approx(17/9) and summary['prompt_mean_tau']==2
    assert summary['category_mean_pooled_tau']==pytest.approx((8/6+3)/2)
    rows[0]['argmax_passed']=False
    assert not report.summarize(rows)['argmax_all_passed']
    cells = report.ordered_cells({(60,1):summary,(60,2):{'pooled_tau':3}})
    assert cells[2]['role']=='primary' and cells[3]['role']=='control'


def test_new_full_contract_keeps_original_settings_and_480_inputs():
    import yaml
    previous = ROOT/'studies/esp_table1_bf16_full'
    current = ROOT/'studies/esp_table1_bf16_full_argmax'
    old = yaml.safe_load((previous/'experiment_config.yaml').read_text())
    new = yaml.safe_load((current/'experiment_config.yaml').read_text())
    for key in ('seed','data','model','system'):
        assert old[key]==new[key]
    for key in ('task','eval'):
        assert old['algorithm']['config'][key]==new['algorithm']['config'][key]
    before = yaml.safe_load((previous/'study.yaml').read_text())
    after = yaml.safe_load((current/'study.yaml').read_text())
    assert before['axes']==after['axes'] and before['seeds']==after['seeds']
    assert 'argmax_audit.py' in after['provenance']['include']
    assert (previous/'docs/prompts_manifest.json').read_bytes()==(current/'docs/prompts_manifest.json').read_bytes()
    assert len(json.loads((current/'docs/prompts_manifest.json').read_text())['rendered_prompts'])==480
