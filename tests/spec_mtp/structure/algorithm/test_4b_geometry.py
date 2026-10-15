import importlib.util
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parents[4]


def tool(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_trace_root_is_generated_index_and_bad_totals_are_rejected():
    module = tool('analyze_4b_geometry')
    stats = {'trace': [{'root_position': 5, 'cache_before': 5, 'accepted_nodes': [1], 'committed_tokens': [2, 3]},
                       {'root_position': 7, 'cache_before': 7, 'accepted_nodes': [], 'committed_tokens': [4]}],
             'decode_calls': 2, 'accepted': 1, 'committed': 3, 'accept_by_depth': [0, 1, 0, 0]}
    assert module.trace_metrics({'stats': stats}, 5) == [(0, 1, 2), (2, 0, 1)]
    with pytest.raises(AssertionError):
        module.trace_metrics({'stats': dict(stats, accepted=2)}, 5)
    with pytest.raises(AssertionError):
        module.trace_metrics({'stats': stats}, 4)
    assert module.distribution([]) == {'n': 0}
    assert module.distribution([2])['median'] == 2


def test_output_velocity_does_not_directly_change_first_slot_at_depth_zero_or_one():
    module = tool('capture_4b_geometry')
    proxies = torch.tensor([[2., 1.], [3., 2.]])
    anchor, velocity = torch.tensor([1., 0.]), torch.tensor([.5, -.5])
    raw, _ = module.raw_output_slots(anchor, velocity, proxies, 1, .99)
    assert torch.equal(raw[:2, 0], proxies)
    assert not torch.equal(raw[:2, 1], proxies)
    assert torch.equal(anchor, torch.tensor([1., 0.])) and torch.equal(velocity, torch.tensor([.5, -.5]))
    zero, _ = module.raw_output_slots(anchor, torch.zeros_like(velocity), proxies, 0, .99)
    assert torch.equal(zero[:, 0], zero[:, 1])


def test_target_embedding_alignment_and_tail_are_not_shifted():
    module = tool('capture_4b_geometry')
    embedding = torch.eye(4)
    masks = torch.stack([embedding[2], embedding[3]])[None]
    frame = {'root_index': 0, 'depths': [0], 'masks': masks, 'raw_predictions': masks,
             'real_hidden': embedding[2][None], 'velocity_ratios': [0.]}
    rows, skipped = module.point_rows([frame], torch.tensor([1, 2, 3]), embedding, 'input_first', 121, 2)
    assert skipped == 0 and [r['target_index'] for r in rows] == [1, 2]
    assert all(r['mask_target_cos'] == 1 for r in rows)
    assert [r['shared_prefix'] for r in rows] == [True, False]
    assert rows[0]['real_hidden_target_cos'] == 1
    _, skipped = module.point_rows([frame], torch.tensor([1, 2]), embedding, 'input_first', 121, 2)
    assert skipped == 1


@pytest.mark.parametrize('free,command,passed', [(19000, 'python release-ci.py', True),
                                                (18000, 'python release-ci.py', False),
                                                (19000, 'python model_training.py', False)])
def test_admission_defers_on_capacity_or_unknown_work(monkeypatch, free, command, passed):
    import json
    module = tool('capture_4b_geometry')
    def output(args, **kwargs):
        return f'GPU-test, {free}, 2000' if args[0] == 'nvidia-smi' else json.dumps(
            [{'ProcessId': -1, 'CommandLine': command}])
    monkeypatch.setattr(module.subprocess, 'check_output', output)
    assert module.admission()['passed'] is passed


@pytest.mark.parametrize('method', ['input_first', 'output_zero', 'output_first'])
def test_read_only_observer_preserves_tiny_bf16_output_and_forward_budget(method):
    from spec_mtp.structure.model.hf_causal import HFCausalLM
    from spec_mtp.structure.algorithm.decoding import SpecDecoder
    from spec_mtp.structure.control.named import _convert
    module = tool('capture_4b_geometry')
    torch.manual_seed(5)
    model = HFCausalLM(tiny_config={'vocab_size': 32, 'hidden_size': 16, 'num_layers': 1,
                                   'num_heads': 2, 'num_kv_heads': 1, 'max_position_embeddings': 64})
    model.hf.lm_head.weight = model.hf.model.embed_tokens.weight
    model.hf.bfloat16()
    spec = {'method': 'ema_velocity' if method == 'input_first' else 'output_hidden', 'num_masks': 2,
            'block_complexity': 12, 'impl': 'naive', 'tree': {'mode': 'dynamic', 'pruning': True}}
    if method == 'input_first':
        spec['ema'] = {'level': 'order0', 'beta': .9999, 'lam': .1}
    else:
        spec['output'] = {'order': int(method == 'output_first'), 'beta': .9, 'beta_prime': .99}
    cfg = {'temperature': 0., 'max_new_tokens': 7, 'stop_on_eos': False}
    prompt = torch.tensor([[1, 2, 3]])
    expected, expected_stats = SpecDecoder(model, _convert(spec), _convert(cfg)).generate(prompt)
    actual, stats, frames, calls = module.observe(model, prompt, spec, cfg, [], 123)
    assert torch.equal(expected[0], actual)
    assert expected_stats['accepted'] == stats['accepted'] and calls == 1 + len(frames)
    assert stats['verification_argmax_audit']['checked_committed_tokens'] == 7
    rows, _ = module.point_rows(frames, actual[3:], model.embedding_table, method, 121, 7)
    assert rows and all(row['target_index'] >= row['root_index'] + row['depth'] + 1 for row in rows)
    assert not model._forward_hooks and not model._forward_pre_hooks and not model.hf.model.norm._forward_hooks


def test_cpu_downloader_requires_verified_content(monkeypatch):
    import json
    from types import SimpleNamespace
    module = tool('capture_4b_geometry')
    command = 'D:\\GitHub\\DreamSoul\\quantization\\.tmp\\paroquant-paper-env\\python.exe -u .tmp/paroquant-reference/download_layers.py'
    monkeypatch.setattr(module.subprocess, 'check_output', lambda args, **kw:
                        'GPU-test, 19000, 2000' if args[0] == 'nvidia-smi' else
                        json.dumps([{'ProcessId': -1, 'CommandLine': command}]))
    monkeypatch.setattr(module.Path, 'is_file', lambda _: True)
    monkeypatch.setattr(module.Path, 'read_bytes', lambda _: b'inspected downloader')
    monkeypatch.setattr(module.hashlib, 'sha256', lambda _: SimpleNamespace(hexdigest=lambda:
                        '10689bac808d0e5fa1958d306508f459d3c4637dc92a51bf5b6c1bb915545026'))
    assert module.admission()['passed'] and module.admission()['verified_cpu_preparation_count'] == 1
    monkeypatch.setattr(module.hashlib, 'sha256', lambda _: SimpleNamespace(hexdigest=lambda: 'changed'))
    assert not module.admission()['passed']
