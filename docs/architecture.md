# Architecture

Training-free multi-token prediction. One decode loop, two mask providers: ESP from the paper, and EMA-velocity. The mask is a vector in the model's input-embedding space. It is concatenated into `inputs_embeds`. It is not mapped back to a token id. The model emits logits; greedy or sampled argmax yields a real token; verification compares token ids.

Paper: *Efficient Training-Free Multi-Token Prediction via Embedding-Space Probing* (Goel, Gagrani, Lee, Lott — Qualcomm AI Research, ICML 2026), [arXiv:2603.17942](https://arxiv.org/abs/2603.17942). Local PDF, not in git: `docs/papers/2603.17942v2.pdf`.

## Modules

```text
src/main.py                 config in, one algorithm out
src/algorithms/esp_mtp.py   the speculative loop and CSV aggregation
src/algorithms/ar_baseline.py
src/algorithms/alignment_probe.py
src/spec/decoding.py        embed, append masks, forward, select, verify
src/spec/mask_providers.py  ESP and EMA-velocity
src/spec/tree.py            static and dynamic draft trees, pruning
src/spec/tree_attention.py  block layout, tree mask, position ids
src/spec/kv_cache.py        keep prefix + root + accepted path
src/models/hf_causal.py     input embedding table; forward takes inputs_embeds
src/data/                   SpecBench, Dolly, local prompts
src/core/                   config, logger, tools
```

`configs/hf/<family>/` is one YAML per paper setting. `configs/smoke/` is a tiny random LLaMA, no download. `scripts/run_*.sh` is one sweep per paper table.

## One decode step

1. Embed the committed tokens with the input embedding table, `e = E[x]`.
2. The mask provider returns `k` vectors. They are appended after the root and after each draft node.
3. One forward covers `[root | tree nodes | k masks per node]`. Block size is `(k+1)(1 + sum K_i)`.
4. Walk the model's own next-token chain through the tree. An exact token-id match is accepted. The first mismatch is the bonus token.
5. Re-embed only committed tokens and hand those embeddings to the provider. Rejected drafts never enter the history.
6. Drop KV for rejected positions. After the step, `cache_len == root_pos`. The bonus token is the next block's root, not a cached position.

Float32 greedy with a shared seed must match ordinary generation token for token. `exact_match` is that check. It is not the quality metric. The quality metric used in [research.md](research.md) is how many draft tokens were kept.

## ESP

`ESPMaskProvider`. Default init is the mean of the prompt embeddings. Each committed token then moves that vector:

```text
m ← (1 − λ) m + λ e_new
```

`λ = 0.1` in the paper. `spec.mask.update: false` leaves the prompt mean frozen. Every mask slot shares this one vector. The slot index only changes the position id.

Other inits, used by the paper ablations: last-k prompt embeddings, a sample from the embedding table, and an offset `μ + cσ`. See the class docstring in `mask_providers.py` for the Last-K index choice.

## EMA-velocity

`EMAVelocityMaskProvider`, `spec.method: ema_velocity`. Differences are input embeddings only:

```text
vhat ← β vhat + (1 − β) (e_new − e_prev)
```

The first prompt difference seeds `vhat`. There is no `1 − β^s` correction. At `β = 0.9999`, `vhat` stays near that first difference. `β = 0` would use only the latest step. That setting has not been run.

The mask is

```text
m_i = origin + γ · i · step(vhat)
```

`γ` is `spec.ema.step_scale`. `i` is the slot. A tree with one slot uses `i = 1`.

`origin` depends on `spec.ema.level`:

| **level** | **origin** |
| --- | --- |
| `last` (code default) | the latest committed embedding |
| `order0` | the ESP mean: prompt mean, then the `λ` update above |

`γ = 0` removes the velocity term. On `level=last` the mask is the last token. On `level=order0` the mask is the updating mean. `off` in the research tables means the term is absent, not the number 0.

`normalize: true` replaces `vhat` with a unit direction scaled by the EMA of difference norms. `extrapolate_ema: true` rolls the EMA across the `k` slots inside one block. It does not change the committed state. Both default to false. The history tables use `normalize` only for the direction-only row, and do not turn on `extrapolate_ema`.

`update: false` freezes `vhat`. The last-token anchor still moves.

## Tree and verification

Static branches are a fixed list such as `[14]` (one mask, block complexity 30). Dynamic branches follow the paper's Algorithm 1 under top-1 expansion. Pruning replaces a parent-repeat candidate with the next token.

Verification is exact match against the model's own chain, not residual sampling. One random draw per committed token, in order, keeps temperature 1 aligned with ordinary generation when the generator is shared.

`spec.impl: efficient` reuses the attention mask and shifts position ids. It requires a static tree. `naive` rebuilds the mask every step.

## Choices that differ from a literal reading of the paper

1. The `λ` update runs once per committed token, in order, when one pass commits several tokens.
2. Last-K uses the last `k` prompt embeddings. The printed index `e_{t−k−i}` points before those tokens.
3. The sample-init standard deviation is per dimension.
4. Printed branches `[7,5,3]` have block complexity 64, not 60. The code keeps the printed branches and logs 64.
5. Configs default to 100 new tokens. Table 1's caption says 256. Override with `eval.max_new_tokens`.
6. The BC=120 ablation uses `[15,10,4]`.
7. The first tree is proposed before the first new token exists.
8. Qwen3 thinking is off.
9. Efficient mask reuse is static trees only.
10. The BC=60 main configs are static plus efficient. Dynamic trees are the separate `*_bc60_dynamic.yaml` files.
11. `tau` is committed tokens per decode call. The prefill forward is not in the denominator. `call_reduction = 1 − 1/tau`.
12. PLD, STAND, and LADE are not in this repo. The autoregressive baseline is.

## Result files

Each run writes `results/<save_root>/<save_name>/`. The logger appends. A new run needs a new directory.

`spec_metrics.csv`, one row per prompt: `prompt`, `category`, `new_tokens`, `committed`, `decode_calls`, `accepted`, `tau`, `spec_time`, `hit_context_limit`. With `eval.run_ar_baseline: true` also `ar_time`, `ar_calls`, `exact_match`.

`accepted` counts kept draft tokens. `committed = accepted + decode_calls`, aside from a short final pass that stops on the token budget or EOS. `new_tokens = committed + 1` for the prefill token, with the same caveat. `tau = committed / decode_calls`.

`summary.csv` pools `tau` as `sum(committed) / sum(decode_calls)`, plus `call_reduction`, `tokens_per_s`, and, when the baseline ran, `speedup` and `exact_match_rate`. `exact_match_rate` must be 1.

`tau` does not change between `naive` and `efficient`. Wall time does.

An `ar_baseline` run writes `ar_calls`, `ar_time`, `ar_new_tokens` only. An alignment probe writes `alignment_metrics.csv` (`layer`, cosine of accepted and rejected positions) instead of the speculative CSV.
