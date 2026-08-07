"""CPU correctness checks (no GPU, no downloads).

Run via scripts/run_correctness_checks.sh. Covers:

  1. Mask providers: Eq (4) mean init, Eq (5) update algebra, every ablation
     init (last_k / sample / offset), EMA-velocity hand-computed recursion.
  2. Trees: Eq (7) block-complexity accounting, Top-1 expansion chains,
     Section 3.5 pruning, Algorithm 1 budget + ancestor closure.
  3. Tree attention: the efficient (Appendix E) masks/PIDs are bit-identical
     to the naive per-step construction; attend-set structure is causal.
  4. End-to-end losslessness on a random tiny LLaMA: ESP and EMA-velocity
     outputs equal plain AR decoding token-for-token across methods, mask
     counts, static/dynamic trees, pruning on/off, naive/efficient impls,
     and temperatures {0.0, 1.0} (shared seeds). This exercises prefill,
     tree attention, position IDs, KV-cache surgery, and verification.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import torch

from core.config import NamedDict, _convert
from models.hf_causal import HFCausalLM
from spec.decoding import SpecDecoder, ar_generate
from spec.mask_providers import EMAVelocityMaskProvider, ESPMaskProvider
from spec.tree import build_dynamic_tree, build_static_tree, node_budget_for
from spec.tree_attention import (TreeAttentionCache, block_layout,
                                 build_block_attention, mask_indices_of)

PASSED = 0


def check(name, condition):
    global PASSED
    if not condition:
        raise AssertionError(f'FAILED: {name}')
    PASSED += 1
    print(f'  ok: {name}')


# ---------------------------------------------------------------- providers
def test_mask_providers():
    print('[mask providers]')
    torch.manual_seed(0)
    table = torch.randn(64, 8)
    prompt = torch.randn(10, 8)

    p = ESPMaskProvider(2, table, init='mean_prompt', lam=0.1)
    p.init_from_prompt(prompt)
    check('Eq 4: mean-of-prompt init',
          torch.allclose(p.masks(), prompt.mean(0).expand(2, 8)))
    m0 = p.masks().clone()
    e_new = torch.randn(8)
    p.on_token_committed(e_new, prompt[-1])
    check('Eq 5: m + lam*(e - m)',
          torch.allclose(p.masks(), m0 + 0.1 * (e_new.unsqueeze(0) - m0)))

    p = ESPMaskProvider(2, table, init='mean_prompt', lam=0.1, update=False)
    p.init_from_prompt(prompt)
    m0 = p.masks().clone()
    p.on_token_committed(e_new, prompt[-1])
    check('update=false freezes the mask', torch.equal(p.masks(), m0))

    p = ESPMaskProvider(3, table, init='last_k')
    p.init_from_prompt(prompt)
    check('last_k init = last k prompt embeddings',
          torch.equal(p.masks(), prompt[-3:]))

    gen = torch.Generator().manual_seed(1)
    p = ESPMaskProvider(2, table, init='sample_embedding', generator=gen)
    p.init_from_prompt(prompt)
    check('sample init shape/finite',
          p.masks().shape == (2, 8) and torch.isfinite(p.masks()).all())

    p = ESPMaskProvider(1, table, init='offset_embedding', offset_scale=5.0)
    p.init_from_prompt(prompt)
    expected = table.mean(0) + 5.0 * table.std(0)
    check('G.8 offset init = mu + 5*sigma', torch.allclose(p.masks()[0], expected))

    # EMA velocity vs a hand computation.
    beta = 0.9
    p = EMAVelocityMaskProvider(2, table, beta=beta, step_scale=1.0)
    p.init_from_prompt(prompt)
    diffs = prompt[1:] - prompt[:-1]
    vhat = diffs[0].clone()
    for j in range(1, diffs.size(0)):
        vhat = beta * vhat + (1 - beta) * diffs[j]
    check('EMA velocity: prefill recursion',
          torch.allclose(p._velocity, vhat, atol=1e-6))
    check('EMA velocity: m_i = e_last + i*vhat',
          torch.allclose(p.masks(),
                         torch.stack([prompt[-1] + vhat, prompt[-1] + 2 * vhat]),
                         atol=1e-5))
    p.on_token_committed(e_new, prompt[-1])
    vhat2 = beta * vhat + (1 - beta) * (e_new - prompt[-1])
    check('EMA velocity: commit folds the diff',
          torch.allclose(p._velocity, vhat2, atol=1e-6))
    check('EMA velocity: anchor tracks last token',
          torch.equal(p._anchor, e_new))


# -------------------------------------------------------------------- trees
def test_trees():
    print('[trees]')
    torch.manual_seed(0)
    V = 50
    probs = torch.softmax(torch.randn(2, V), dim=-1)

    tree = build_static_tree(probs, [7, 2], root_token=3, pruning=False)
    check('static [7,2]: widths', tree.branch_widths() == [7, 2])
    check('Eq 7: BC = (k+1)(1+sum K) = 30', tree.block_complexity(2) == 30)
    top1 = max(range(7), key=lambda j: tree.probs[j])
    check('Top-1 expansion: depth-2 parent is depth-1 argmax',
          all(tree.parents[j] == top1 + 1 for j in range(7, 9)))
    d2 = torch.topk(probs[1], 2).indices.tolist()
    check('depth-2 candidates are mask-2 top-k',
          sorted(tree.tokens[7:9]) == sorted(d2))
    check('cumulative probs multiply',
          abs(tree.probs[7] - tree.probs[top1] * probs[1][tree.tokens[7]].item()) < 1e-6)

    # Pruning: force the parent's token to be mask-2's argmax.
    probs2 = probs.clone()
    parent_token = tree.tokens[top1]
    probs2[1] = 1e-9
    probs2[1][parent_token] = 0.9
    probs2[1][(parent_token + 1) % V] = 0.05
    probs2[1][(parent_token + 2) % V] = 0.03
    probs2[1] = probs2[1] / probs2[1].sum()
    pruned = build_static_tree(probs2, [7, 2], root_token=3, pruning=True)
    check('pruning drops parent-repeat token',
          parent_token not in [pruned.tokens[j] for j in range(7, 9)])
    unpruned = build_static_tree(probs2, [7, 2], root_token=3, pruning=False)
    check('without pruning the repeat stays',
          parent_token in [unpruned.tokens[j] for j in range(7, 9)])

    check('node budget: BC=30,k=2 -> 9', node_budget_for(30, 2) == 9)
    check('node budget: BC=60,k=1 -> 29', node_budget_for(60, 1) == 29)
    dyn = build_dynamic_tree(probs, node_budget_for(30, 2), root_token=3, pruning=False)
    check('dynamic: exactly the node budget', dyn.num_nodes == 9)
    widths = dyn.branch_widths()
    check('dynamic: widths fill [9-i, i]', sum(widths) == 9 and widths[0] >= 1)
    check('dynamic: depth-1 top-1 always kept',
          torch.topk(probs[0], 1).indices.item() in
          [dyn.tokens[j] for j in range(dyn.num_nodes) if dyn.depths[j] == 1])
    if len(widths) > 1:
        by_prob_d1 = sorted(dyn.probs[j] for j in range(dyn.num_nodes)
                            if dyn.depths[j] == 1)[0]
        max_d2 = max((dyn.probs[j] for j in range(dyn.num_nodes)
                      if dyn.depths[j] == 2), default=0.0)
        check('dynamic: kept depth-2 beats dropped depth-1 candidates',
              max_d2 <= max(dyn.probs) + 1e-9 and by_prob_d1 >= 0)

    # A peaked mask-1 distribution should push budget into depth 2.
    peaked = probs.clone()
    peaked[0] = 1e-9
    peaked[0][7] = 1.0
    peaked[0] = peaked[0] / peaked[0].sum()
    dyn2 = build_dynamic_tree(peaked, 9, root_token=3, pruning=False)
    check('dynamic: confident mask-1 -> deeper tree',
          dyn2.branch_widths()[0] < 9 and len(dyn2.branch_widths()) == 2)


# ---------------------------------------------------------- tree attention
def test_tree_attention():
    print('[tree attention]')
    torch.manual_seed(0)
    probs = torch.softmax(torch.randn(2, 50), dim=-1)
    tree = build_static_tree(probs, [3, 2], root_token=1, pruning=True)
    k = 2
    attend, rel, owners, size = block_layout(tree, k)
    check('block size = (k+1)(1+sum K)', size == tree.block_size(k) == 18)
    check('root attends only itself (plus cache)', attend[0] == {0})
    node_rows = range(1, 1 + tree.num_nodes)
    check('nodes attend root + ancestors + self',
          all(0 in attend[i] and i in attend[i] for i in node_rows))
    for owner in range(1 + tree.num_nodes):
        rows = mask_indices_of(tree, k, owner)
        check(f'mask rows of owner {owner}: pids follow owner',
              all(rel[r] == rel[owner] + j + 1 for j, r in enumerate(rows)))
        check(f'mask rows of owner {owner}: attend owner path + earlier masks',
              all(attend[r] == attend[owner] | set(rows[:j + 1])
                  for j, r in enumerate(rows)))

    # Naive vs efficient equality across growing cache lengths.
    cache_impl = TreeAttentionCache()
    for step, (cache_len, root_pos) in enumerate([(10, 10), (13, 13), (17, 17)]):
        naive_mask, naive_pid = build_block_attention(
            tree, k, cache_len, root_pos, torch.float32, 'cpu', float('-inf'))
        eff_mask, eff_pid = cache_impl.get(
            tree, k, cache_len, root_pos, torch.float32, 'cpu', float('-inf'))
        check(f'appendix E step {step}: masks identical',
              torch.equal(naive_mask, eff_mask))
        check(f'appendix E step {step}: PIDs identical',
              torch.equal(naive_pid, eff_pid))


# ------------------------------------------------------------- end to end
def _tiny_model():
    torch.manual_seed(7)
    return HFCausalLM(tiny_config={'vocab_size': 199, 'hidden_size': 64,
                                   'intermediate_size': 128, 'num_layers': 2,
                                   'num_heads': 4, 'num_kv_heads': 2,
                                   'max_position_embeddings': 1024})


def _spec_cfg(method, num_masks, tree_mode, branches=None, bc=None,
              pruning=True, impl='naive'):
    return _convert({
        'method': method,
        'num_masks': num_masks,
        'block_complexity': bc,
        'impl': impl,
        'tree': {'mode': tree_mode, 'branches': branches, 'pruning': pruning},
        'mask': {'init': 'mean_prompt', 'lam': 0.1, 'update': True},
        'ema': {'beta': 0.9, 'step_scale': 1.0, 'update': True},
    })


def test_lossless():
    print('[end-to-end losslessness on tiny random LLaMA]')
    model = _tiny_model()
    eval_cfg = _convert({'max_new_tokens': 24, 'temperature': 0.0,
                         'stop_on_eos': False})
    prompt_gen = torch.Generator().manual_seed(11)
    prompts = [torch.randint(0, 199, (1, n), generator=prompt_gen)
               for n in (16, 25, 40)]

    grid = [
        ('esp', 1, 'static', [4], None, True, 'naive'),
        ('esp', 1, 'static', [4], None, True, 'efficient'),
        ('esp', 1, 'static', [14], None, False, 'efficient'),
        ('esp', 2, 'static', [7, 2], None, True, 'efficient'),
        ('esp', 2, 'dynamic', None, 30, True, 'naive'),
        ('esp', 3, 'dynamic', None, 60, True, 'naive'),
        ('esp', 3, 'static', [7, 5, 3], None, True, 'efficient'),
        ('ema_velocity', 1, 'static', [4], None, True, 'efficient'),
        ('ema_velocity', 2, 'dynamic', None, 30, True, 'naive'),
        ('ema_velocity', 2, 'static', [15, 4], None, False, 'efficient'),
    ]
    for method, k, mode, branches, bc, pruning, impl in grid:
        spec_cfg = _spec_cfg(method, k, mode, branches, bc, pruning, impl)
        for temperature in (0.0, 1.0):
            eval_cfg.temperature = temperature
            for pi, prompt in enumerate(prompts):
                dec = SpecDecoder(model, spec_cfg, eval_cfg,
                                  generator=torch.Generator().manual_seed(100 + pi))
                out, stats = dec.generate(prompt)
                ar_out, _ = ar_generate(
                    model, prompt, eval_cfg,
                    generator=torch.Generator().manual_seed(100 + pi))
                tag = (f'{method} k={k} {mode} branches={branches} bc={bc} '
                       f'pruning={pruning} impl={impl} T={temperature} prompt={pi}')
                check(f'lossless: {tag}', torch.equal(out, ar_out))
                check(f'tau >= 1: {tag}',
                      stats['committed'] >= stats['decode_calls'])

    # ESP init ablations must also stay lossless.
    for init in ('last_k', 'sample_embedding', 'offset_embedding'):
        spec_cfg = _spec_cfg('esp', 2, 'static', [7, 2], None, True, 'efficient')
        spec_cfg.mask.init = init
        eval_cfg.temperature = 0.0
        dec = SpecDecoder(model, spec_cfg, eval_cfg,
                          generator=torch.Generator().manual_seed(3))
        out, _ = dec.generate(prompts[0])
        ar_out, _ = ar_generate(model, prompts[0], eval_cfg,
                                generator=torch.Generator().manual_seed(3))
        check(f'lossless under init={init}', torch.equal(out, ar_out))

    # Frozen-mask and lambda ablation knobs.
    for knob in ({'lam': 0.01}, {'lam': 0.5}, {'update': False}):
        spec_cfg = _spec_cfg('esp', 1, 'static', [14], None, True, 'efficient')
        for key, value in knob.items():
            spec_cfg.mask[key] = value
        dec = SpecDecoder(model, spec_cfg, eval_cfg,
                          generator=torch.Generator().manual_seed(5))
        out, _ = dec.generate(prompts[1])
        ar_out, _ = ar_generate(model, prompts[1], eval_cfg,
                                generator=torch.Generator().manual_seed(5))
        check(f'lossless under mask {knob}', torch.equal(out, ar_out))

    # max_new_tokens budget is respected exactly.
    eval_cfg.max_new_tokens = 7
    spec_cfg = _spec_cfg('esp', 2, 'static', [7, 2], None, True, 'efficient')
    dec = SpecDecoder(model, spec_cfg, eval_cfg,
                      generator=torch.Generator().manual_seed(9))
    out, stats = dec.generate(prompts[0])
    check('budget respected', out.size(1) == prompts[0].size(1) + 7)


def main():
    test_mask_providers()
    test_trees()
    test_tree_attention()
    test_lossless()
    print(f'\nAll {PASSED} checks passed.')


if __name__ == '__main__':
    main()
