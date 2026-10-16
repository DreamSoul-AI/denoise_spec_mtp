"""Native magnitude controls keep the shared mean, fixed direction and argmax gate."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest
import torch
import yaml

from spec_mtp.structure.algorithm.mask_providers import EMAVelocityMaskProvider, ESPMaskProvider

ROOT = Path(__file__).resolve().parents[2]


def module(monkeypatch):
    monkeypatch.setattr(sys, 'path', sys.path.copy())
    path = ROOT / 'studies/qwen3_4b_bf16_bias_norm_scan/norm_control.py'
    spec = importlib.util.spec_from_file_location('sd_norm_control', path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.mark.parametrize('mode', ['template', 'random0', 'random1', 'random2'])
def test_native_scale_retains_mean_and_seed_direction(monkeypatch, mode):
    m = module(monkeypatch)
    embeds = torch.randn(10, 16, generator=torch.Generator().manual_seed(7)).bfloat16()
    directions = []
    for scale in (0., .5, 1., 2.):
        provider = EMAVelocityMaskProvider(2, embeds, beta=.9999, level='order0', lam=.1, step_scale=scale)
        info = {}
        m.observe_initial_bias(provider, mode, info).init_from_prompt(embeds[:8])
        assert info['rounded_slot_displacement_norms'] == (provider.masks().float() - provider._level.float()).norm(dim=-1).tolist()
        zero = ESPMaskProvider(2, embeds, lam=.1)
        zero.init_from_prompt(embeds[:8])
        directions.append(provider._velocity.clone())
        for previous, new in zip(embeds[7:9], embeds[8:10]):
            assert torch.equal(provider._level, zero.masks()[0])
            if scale == 0:
                assert torch.equal(provider.masks(), zero.masks())
            provider.on_token_committed(new, previous)
            zero.on_token_committed(new, previous)
            assert torch.equal(provider._velocity, directions[-1])
        assert info['step_scale'] == scale and info['full_prompt_mean_preserved']
    assert all(torch.equal(v, directions[0]) for v in directions)


def test_eight_preregistered_cells_and_immutable_inputs(monkeypatch):
    m = module(monkeypatch)
    m.check_refs()
    decl = yaml.safe_load((m.STUDY / 'study.yaml').read_text(encoding='utf-8'))
    rows = decl['axes']['algorithm.config']
    assert [(r['direction'], r['spec']['ema']['step_scale']) for r in rows] == [
        (mode, scale) for mode in ('template', 'random0', 'random1', 'random2') for scale in (.5, 2.)]
    assert all(r['spec']['num_masks'] == 2 and r['spec']['block_complexity'] == 30 for r in rows)


@pytest.mark.parametrize('scale', [.5, 2.])
def test_native_tiny_bf16_argmax_audit_for_scaled_bias(monkeypatch, scale):
    from spec_mtp.structure.algorithm import decoding
    from spec_mtp.structure.control.named import _convert
    from spec_mtp.structure.model.hf_causal import HFCausalLM
    m = module(monkeypatch)
    torch.manual_seed(17)
    model = HFCausalLM(tiny_config={'vocab_size': 32, 'hidden_size': 16, 'intermediate_size': 32,
        'num_hidden_layers': 1, 'num_attention_heads': 2, 'num_key_value_heads': 2,
        'max_position_embeddings': 128}, torch_dtype='bfloat16', attn_implementation='eager')
    spec = _convert({'method': 'ema_velocity', 'num_masks': 2, 'block_complexity': 30, 'impl': 'naive',
        'tree': {'mode': 'dynamic', 'pruning': True},
        'ema': {'level': 'order0', 'beta': .9999, 'lam': .1, 'step_scale': scale}})
    original = decoding.build_mask_provider
    monkeypatch.setattr(decoding, 'time', SimpleNamespace(perf_counter=lambda: 0.))
    monkeypatch.setattr(decoding, 'build_mask_provider', lambda *a, **kw: m.observe_initial_bias(original(*a, **kw), 'random1', {}))
    output, stats = decoding.SpecDecoder(model, spec, _convert({'temperature': 0., 'max_new_tokens': 12})).generate(torch.tensor([[1, 2, 3, 4, 5]]))
    assert output.shape[1] == 17
    assert stats['verification_argmax_audit']['passed'] and stats['verification_argmax_audit']['checked_committed_tokens'] == 12


def test_unmade_readout_cannot_claim_completed_scan(monkeypatch):
    from spec_mtp.structure.artifact.sources import SpecMtpSourceChangedError
    m = module(monkeypatch)
    monkeypatch.syspath_prepend(str(m.STUDY))
    spec = importlib.util.spec_from_file_location('sd_norm_readout', m.STUDY / 'analyze_results.py')
    readout = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(readout)
    with pytest.raises(SpecMtpSourceChangedError):
        readout.main()
    assert not (m.STUDY / 'docs/norm_evidence_v1.json').exists()


def test_first_block_pairing_excludes_changed_prefill_and_missing_blocks(monkeypatch):
    m = module(monkeypatch)
    spec = importlib.util.spec_from_file_location('sd_norm_depth_readout', m.STUDY / 'analyze_results.py')
    readout = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(readout)
    prompts = [{'question_id': i, 'input_ids': [1, 2]} for i in range(4)]
    def evidence(token, accepted):
        trace = [] if accepted is None else [{'accepted_nodes': list(range(accepted))}]
        return {'input_ids': [1, 2], 'output_ids': [1, 2, token],
            'stats': {'prefill_calls': 1, 'decode_calls': len(trace), 'trace': trace,
                      'attempt_by_depth': [0, 1, 0], 'accept_by_depth': [0, 0, 0]}}
    first = readout.depth_rows([evidence(3, n) for n in (0, 1, 1, None)], prompts)
    second = readout.depth_rows([evidence(3, 1), evidence(3, 0), evidence(4, 2), evidence(3, 2)], prompts)
    assert readout.first_block_compare(first, second) == {'total': 4, 'same_prefix_with_block': 2,
        'different_prefix': 1, 'missing_block': 1, 'accepted': {'win': 1, 'tie': 0, 'loss': 1}}
    second[0]['question_id'] = 99
    with pytest.raises(AssertionError):
        readout.first_block_compare(first, second)
