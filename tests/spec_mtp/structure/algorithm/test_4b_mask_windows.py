import importlib.util
from pathlib import Path
import sys

import pytest
import torch

ROOT = Path(__file__).resolve().parents[4]


def tool(name, monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'tools'))
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    return module


def test_radial_and_tangent_velocity_are_distinguished(monkeypatch):
    m = tool('analyze_4b_velocity', monkeypatch)
    a = torch.tensor([1., 0.])
    radial = m.velocity_geometry(a, torch.tensor([1., 0.]))
    assert radial['tangent_over_velocity'] == 0 and radial['normalized_movement_retention'] == 0
    tangent = m.velocity_geometry(a, torch.tensor([0., .01]))
    assert tangent['tangent_over_velocity'] == 1 and tangent['normalized_movement_retention'] > .99
    with pytest.raises(AssertionError):
        m.velocity_geometry(a, torch.zeros(2))


def test_transitions_use_previous_owner_depth_and_never_cross_prompts(monkeypatch):
    m = tool('analyze_4b_velocity', monkeypatch)
    trace = [{'root_position': 5, 'cache_before': 5, 'accepted_nodes': [1, 2], 'committed_tokens': [2, 3, 4], 'stopped': False},
             {'root_position': 8, 'cache_before': 8, 'accepted_nodes': [], 'committed_tokens': [5], 'stopped': False}]
    e = {'input_ids': [0] * 5, 'stats': {'trace': trace, 'decode_calls': 2, 'accepted': 2,
                                       'committed': 4, 'accept_by_depth': [0, 1, 1, 0]}}
    r = m.transition_counts([e, e])
    assert r['2']['transitions'] == 2 and r['2']['next_accept_d1_rate'] == 0
    assert r['0']['transitions'] == r['1']['transitions'] == 0


def test_local_factorial_keeps_native_first_and_shifts_only_declared_formula(monkeypatch):
    from spec_mtp.structure.algorithm.output_masks import OutputHiddenMaskProvider
    m = tool('diagnose_4b_mask_windows', monkeypatch)
    e = torch.tensor([[1., 0.], [0., 1.]])
    shadow = OutputHiddenMaskProvider(2, e, order=1)
    shadow.init_hidden(torch.tensor([[1., 0.], [1., 1.]]))
    proxies = torch.tensor([[2., 1.], [3., 1.]])
    before = shadow.anchor.clone(), shadow.velocity.clone()
    zero = torch.ones(3, 2, 2, dtype=torch.bfloat16)
    masks = m.intervention_masks(shadow, proxies, zero)
    assert torch.equal(masks['zero'], zero)
    assert torch.equal(masks['first'], shadow.masks_per_owner(proxies).bfloat16())
    assert torch.equal(masks['shifted'][:, 0], masks['first'][:, 1])
    assert not torch.equal(masks['radial'][:, 1], masks['first'][:, 1])
    assert torch.equal(shadow.anchor, before[0]) and torch.equal(shadow.velocity, before[1])


def test_fixed_window_uses_native_control_and_predicts_after_bonus(monkeypatch):
    from spec_mtp.structure.model.hf_causal import HFCausalLM
    from spec_mtp.structure.algorithm.decoding import SpecDecoder
    from spec_mtp.structure.control.named import _convert
    m = tool('diagnose_4b_mask_windows', monkeypatch)
    torch.manual_seed(42)
    model = HFCausalLM(tiny_config={'vocab_size': 32, 'hidden_size': 16, 'num_layers': 1,
                                  'num_heads': 2, 'num_kv_heads': 1, 'max_position_embeddings': 128})
    model.hf.lm_head.weight = model.hf.model.embed_tokens.weight
    model.hf.bfloat16()
    spec = {'method': 'output_hidden', 'num_masks': 2, 'block_complexity': 30, 'impl': 'naive',
            'tree': {'mode': 'dynamic', 'pruning': True}, 'output': {'order': 0, 'beta': .9, 'beta_prime': .99}}
    cfg = {'temperature': 0., 'max_new_tokens': 32, 'stop_on_eos': False}
    ids = torch.tensor([[1, 2, 3]])
    reference, _ = SpecDecoder(model, _convert(spec), _convert(cfg)).generate(ids)
    packet = m.capture_window(model, ids, spec, cfg, [], 123, minimum=2)
    input_spec = {'method': 'ema_velocity', 'num_masks': 2, 'ema': {'level': 'order0', 'beta': .9999, 'lam': .1}}
    packet['masks']['input_first'] = m.input_control(model, ids, reference[0, 3:3 + packet['root_index'] + 1].tolist(), input_spec)
    assert not model._forward_hooks and not model._forward_pre_hooks
    rows, private = m.probe_window(model, packet, spec, reference[0, 3:].tolist())
    assert [r['variant'] for r in rows] == list(m.VARIANTS) and len(private) == 6
    assert all(r['current_owner_argmax_unchanged'] and r['argmax_passed'] for r in rows)
    assert all(r['next_root_index'] == packet['root_index'] + len(packet['chosen']) for r in rows)
    assert rows[0]['next_verified_chain_equals_reference']


def test_window_admission_rejects_unrelated_work_and_tracks_cpu_children(monkeypatch):
    import json
    m = tool('diagnose_4b_mask_windows', monkeypatch)
    processes = [{'ProcessId': -1, 'ParentProcessId': 0, 'CommandLine': 'python release-ci.py'},
                 {'ProcessId': -2, 'ParentProcessId': -1, 'CommandLine': None}]
    monkeypatch.setattr(m.subprocess, 'check_output', lambda args, **kw:
                        '19000, 2000' if args[0] == 'nvidia-smi' else json.dumps(processes))
    assert m.admission()['passed'] and m.admission()['verified_cpu_count'] == 2
    processes.append({'ProcessId': -3, 'ParentProcessId': 0, 'CommandLine': 'python unknown_model.py'})
    assert not m.admission()['passed']
