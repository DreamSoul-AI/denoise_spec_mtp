"""Output-space state math, final-norm observation and real tiny lossless loop."""

import pytest
import torch

from spec_mtp.structure.algorithm.output_masks import OutputHiddenMaskProvider
from spec_mtp.structure.algorithm.decoding import SpecDecoder, ar_generate
from spec_mtp.structure.control.named import _convert
from spec_mtp.structure.model.hf_causal import HFCausalLM


@pytest.fixture(scope='module')
def model():
    torch.manual_seed(7)
    m = HFCausalLM(tiny_config={'vocab_size': 64, 'hidden_size': 32, 'num_layers': 2,
                              'num_heads': 2, 'num_kv_heads': 1, 'max_position_embeddings': 128})
    m.hf.lm_head.weight = m.hf.model.embed_tokens.weight
    m.hf.config.tie_word_embeddings = True
    return m


def spec(order=1, impl='efficient'):
    return _convert({'method': 'output_hidden', 'num_masks': 2, 'impl': impl,
                     'tree': {'mode': 'static', 'branches': [1, 1], 'pruning': False},
                     'output': {'order': order, 'beta': .9, 'beta_prime': .99}})


def test_only_final_norm_matches_all_layer_reference_and_preserves_logits(model):
    embeds = model.embed(torch.tensor([[1, 2, 3, 4]]))
    pos = torch.arange(4).unsqueeze(0)
    full = model(embeds, pos, output_hidden_states=True)
    last = model(embeds, pos, last_hidden_only=True)
    assert torch.equal(last.last_hidden_state, full.hidden_states[-1])
    assert torch.equal(last.logits, full.logits)
    assert last.hidden_states is None
    assert not model.hf.model.norm._forward_hooks
    with pytest.raises(ValueError, match='no all-layer'):
        model(embeds, pos, last_hidden_only=True, output_hidden_states=True)


def test_hook_removed_when_forward_fails(model, monkeypatch):
    def fail(*args, **kwargs):
        raise RuntimeError('injected norm failure')
    monkeypatch.setattr(model.hf.model.norm, 'forward', fail)
    with pytest.raises(RuntimeError, match='injected'):
        model(model.embed(torch.tensor([[1]])), torch.tensor([[0]]), last_hidden_only=True)
    assert not model.hf.model.norm._forward_hooks


def test_state_observation_delay_proxy_updates_and_norm_mapping():
    provider = OutputHiddenMaskProvider(2, torch.tensor([[3., 4.], [3., 4.]]), beta=.5, beta_prime=.75)
    provider.init_hidden(torch.tensor([[1., 0.], [3., 2.]]))
    assert torch.equal(provider.anchor, torch.tensor([3., 2.]))
    assert torch.equal(provider.velocity, torch.tensor([1., 1.]))
    anchor, velocity = provider.anchor.clone(), provider.velocity.clone()
    proxies = torch.tensor([[5., 2.], [7., 4.]])
    masks = provider.masks_per_owner(proxies)
    first_v = .75 * velocity + .25 * (proxies[0] - anchor)
    second_v = .75 * first_v + .25 * (proxies[1] - proxies[0])
    slots = torch.stack([torch.stack([proxies[0], proxies[0] + first_v]),
                         torch.stack([proxies[1], proxies[1] + second_v]),
                         torch.stack([proxies[1] + second_v, proxies[1] + 2 * second_v])])
    assert torch.allclose(masks, 5 * slots / slots.norm(dim=-1, keepdim=True))
    assert torch.equal(provider.anchor, anchor) and torch.equal(provider.velocity, velocity)
    assert torch.allclose(masks.norm(dim=-1), torch.full((3, 2), 5.))
    assert not torch.equal(masks[0], masks[1])
    # The current generated root has no observation yet. Only after its next
    # block forward does the exact root hidden advance committed state.
    provider.observe_committed(torch.tensor([6., 2.]))
    assert torch.equal(provider.velocity, torch.tensor([2., .5]))


@pytest.mark.parametrize('order', [0, 1])
@pytest.mark.parametrize('temperature', [0., .7])
@pytest.mark.parametrize('impl', ['naive', 'efficient'])
def test_output_chain_lossless_sampling_budget_and_exact_state_positions(model, order, temperature, impl):
    cfg = _convert({'max_new_tokens': 12, 'temperature': temperature, 'stop_on_eos': False})
    prompt = torch.tensor([[1, 2, 3, 4, 5]])
    calls = []
    handle = model.hf.model.norm.register_forward_hook(lambda _m, _a, out: calls.append(out.shape[1]))
    try:
        out, stats = SpecDecoder(model, spec(order, impl), cfg,
                                 generator=torch.Generator().manual_seed(123)).generate(prompt)
    finally:
        handle.remove()
    ar, _ = ar_generate(model, prompt, cfg, generator=torch.Generator().manual_seed(123))
    assert torch.equal(out, ar)
    assert len(calls) == 1 + stats['decode_calls']
    assert out.shape[1] == prompt.shape[1] + 12
    for trace in stats['trace']:
        observation = trace['output_hidden']
        assert observation['owner_count'] == 3 and observation['slot_count'] == 2
        assert observation['observed_block_rows'] == ([] if trace['stopped'] else [0] + trace['accepted_nodes'])
        if not trace['stopped']:
            assert trace['cache_after'] == trace['root_position'] + 1 + len(trace['accepted_nodes'])
    assert not model.hf.model.norm._forward_hooks


def test_output_rejects_untied_nonchain_and_invalid_states(model):
    bad = spec(); bad.tree.branches = [2, 1]
    with pytest.raises(ValueError, match='unpruned static chain'):
        SpecDecoder(model, bad, _convert({}))
    untied = HFCausalLM(tiny_config={'vocab_size': 64, 'hidden_size': 32, 'num_layers': 1})
    with pytest.raises(ValueError, match='actually tied'):
        SpecDecoder(untied, spec(), _convert({}))
    with pytest.raises(ValueError, match='order0/1'):
        OutputHiddenMaskProvider(2, model.embedding_table, order=2)
    provider = OutputHiddenMaskProvider(2, model.embedding_table, order=0)
    provider.init_hidden(torch.ones(1, 32))
    with pytest.raises(ValueError, match='nonzero norms'):
        provider.masks_per_owner(torch.zeros(2, 32))
    with pytest.raises(ValueError, match='nonfinite'):
        provider.observe_committed(torch.full((32,), float('nan')))


def test_observed_exact_hiddens_equal_full_causal_prefix(model, monkeypatch):
    observed = []
    original = OutputHiddenMaskProvider.observe_committed
    def capture(self, hidden):
        observed.append(hidden.clone())
        return original(self, hidden)
    monkeypatch.setattr(OutputHiddenMaskProvider, 'observe_committed', capture)
    prompt = torch.tensor([[2, 4, 6, 8]])
    cfg = _convert({'max_new_tokens': 10, 'temperature': 0., 'stop_on_eos': False})
    out, _ = SpecDecoder(model, spec(), cfg).generate(prompt)
    prefix = out[:, :len(observed)]
    reference = model(model.embed(prefix), torch.arange(prefix.shape[1]).unsqueeze(0),
                      last_hidden_only=True).last_hidden_state[0]
    assert len(observed) > prompt.shape[1]
    assert torch.allclose(torch.stack(observed), reference, rtol=1e-5, atol=1e-6)


def test_output_sampling_eos_truncation_matches_ar(model):
    prompt = torch.tensor([[2, 4, 6, 8]])
    cfg = _convert({'max_new_tokens': 12, 'temperature': 1., 'stop_on_eos': False})
    ar, _ = ar_generate(model, prompt, cfg, generator=torch.Generator().manual_seed(12))
    eos = int(ar[0, prompt.shape[1] + 3])
    cfg.stop_on_eos = True
    out, _ = SpecDecoder(model, spec(), cfg, eos_ids=[eos],
                         generator=torch.Generator().manual_seed(12)).generate(prompt)
    reference, _ = ar_generate(model, prompt, cfg, eos_ids=[eos], generator=torch.Generator().manual_seed(12))
    assert torch.equal(out, reference) and int(out[0, -1]) == eos
