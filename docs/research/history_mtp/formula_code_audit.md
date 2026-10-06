# Formula–code audit: ESP, EMA-Velocity, Momentum Guidance

Date: 2026-10-06. Code: commit `b636f90` (`main`, author Jason) plus the
uncommitted `feature/research-ema-history-audit` branch.

Sources actually read:

- ESP [arXiv 2603.17942v2](https://arxiv.org/abs/2603.17942v2): §2, §3.1–3.5,
  §4 setup (HTML). Repo copy: `papers/2603.17942v2.pdf`. Proof appendix not read.
- Momentum Guidance [arXiv 2602.20360v2](https://arxiv.org/abs/2602.20360v2):
  Algorithm 1, §3 Eq (11)–(12), §4 setup, Appendix B.1–B.2 (HTML). No local PDF.
  Official code not inspected.
- Repo: `README.md`, `notes/ema_velocity_method.md`, `notes/metrics.md`,
  `notes/implementation_notes.md`, `src/spec/{mask_providers,decoding,kv_cache,tree,tree_attention}.py`,
  `src/algorithms/esp_mtp.py`, `tests/check_correctness.py`.
- Local DreamSoul notes: *Momentum Guidance 研究记录* and *推测解码 文献调研*.
- Not available: `lark_transcripts/summary_july31.md` (gitignored, absent from the clone).

Labels used below: **[paper]** stated in the paper, **[repo]** stated in repo
docs, **[code]** verified by reading code, **[test]** verified by a check that
ran in this session, **[derived]** our own algebra.

## 1. Three mechanisms, three state objects

| **Method** | **History state** | **What is extrapolated** | **Downstream check** |
| --- | --- | --- | --- |
| ESP Eq (4)–(5) | one shared mask vector pulled toward each new token embedding | mask embedding that probes future positions | target model verifies drafts by exact match |
| EMA-Velocity | EMA `vhat` of consecutive input-embedding differences | `m_i = e_last + i * step(vhat)` | same tree, KV and verification as ESP |
| Momentum Guidance | EMA `m` of ODE velocities | `v + α(v − m)` as the integration velocity | none; it changes the sampled trajectory |

All three keep an EMA of something historical, but none inherits the others'
guarantees. ESP/EMA move the *input* of a frozen LM and are filtered by token
verification. MG moves the *state* of a continuous ODE and changes the sample
distribution of a finite-step sampler. **[derived]**

## 2. ESP

- Eq (4) `m_i = mean_j e_j` → `ESPMaskProvider.init_from_prompt('mean_prompt')`. **[paper][code]**
- Eq (5) `m_i[s+1] = m_i[s] + λ(e_{t+s} − m_i[s])`, λ=0.1. The paper indexes
  `s` by generation step; the repo applies it once per committed token in
  commit order. Repo flags this as its own choice. **[paper][repo][code]**
- Mask `j` of owner `b` gets position `pid(b)+j` and predicts the token after
  that slot (`tree_attention.block_layout`). **[code][test]**
- Verification walks the model's own (greedy or sampled) chain through the
  tree and accepts exact matches only; the first mismatch is the bonus token.
  This is the paper's "sample matching", not Leviathan/Chen residual sampling.
  Token equality with AR under a shared seed is an implementation audit, not a
  distribution proof for T>0. **[paper][code]**

## 3. EMA-Velocity

```
init:    vhat = EMA_beta(e_{j+1} − e_j over the prompt),  first diff seeds vhat
commit:  vhat ← beta·vhat + (1−beta)(e_new − e_prev)       once per committed token
mask:    m_i = e_last + gamma·i·vhat                        normalize=false
         m_i = e_last + gamma·i·r·vhat/‖vhat‖               normalize=true, r = EMA of ‖diff‖
```

**[repo][code]** Checked facts:

| **Question** | **Answer** | **Evidence** |
| --- | --- | --- |
| Mask offset vs step index | mask `i` at position offset `i`, extrapolates `i` steps | **[test]** `check_ema_history.py` alignment |
| Updates per committed token | exactly one, including the prefill-committed root | **[test]** live hook, 48/48 updates |
| Rejected tree nodes in history | never; final state equals a fresh EMA over committed output only | **[test]** two mixed accept/reject cases (18/406 and 3/396 accepted) |
| KV after rejection | prefix + root + accepted path only | **[code]** `kv_cache.keep_block_positions`, `cache_len == root_pos` assert |
| `extrapolate_ema=true` side effects | uses local copies, committed state untouched | **[code]** + existing purity check |
| `update=false` | `vhat` frozen, anchor still moves | **[test]** live hook |
| Init bias correction | none; first diff seeds `vhat` (MG-style `m_0 = v_0`, not `1−β^s`) | **[code]** |
| Constant-diff trajectory | recovered exactly, masks equal true future | **[test]** synthetic |
| Oscillating diffs | raw step shrinks to ~5% of a hop; normalized step restores hop length | **[test]** synthetic, β=0.9 |

No bug was found in history alignment or rejection isolation.

**Confound in the repo's comparison [derived][test-supported]:** `esp_*` vs
`ema_*` changes two things at once: the anchor (prompt mean → last committed
embedding) and the direction (none → `vhat`). The repo's ablation script has
no `step_scale=0` arm, which is EMA with zero extrapolation, i.e. "mask = last
token embedding". Without it, a tau difference cannot be attributed to the
history direction. See the experiment log for why this matters.

## 4. Momentum Guidance

v2 Eq (11)–(12): `m_{i+1} = (1−β)v_i + β m_i`, `Z_{i+1} = Z_i + Δt[v_i + α(v_i − m_i)]`,
`m_0 = v_0`. Appendix B.2 adds optional zero-init debiasing `1−β^s` and
rescaling `m` to `‖v‖`; the ImageNet headline uses both plus an FID grid over
(α, β) and a guidance interval. **[paper]**

Differences that matter for transferring ideas to EMA-Velocity **[derived]**:

- MG amplifies the *deviation of the current velocity from history*
  (`v − m`). EMA-Velocity *continues along* the history (`+ i·vhat`). The two
  can point in opposite directions.
- MG normalization matches the reference to the current velocity norm.
  EMA-Velocity normalization drops `‖vhat‖` and uses the EMA of hop lengths.
  Same word, different operation.
- MG's AB2 special case (β=0, α=½) is a statement about ODE integration
  accuracy. Nothing analogous is established for token embeddings, which are
  discrete points with no underlying continuous trajectory. The README's
  "flow-matching view of AR" is an analogy **[repo]**, not a result.

An MG-style analogue for masks would be `m_i = e_last + γ·i·(d_last − vhat)`,
with `d_last` the latest diff. It is untested and listed only as a candidate.

## 5. What a real model did, on a small slice

Qwen3-8B bf16, 26 SpecBench prompts, BC=30 `[14]`. Numbers and the bf16
exact-match diagnosis are in `experiment_log_20261006.md`. Short version:
default EMA matches its own `step_scale=0` control and both sit below ESP.
That is evidence about this slice only. It is not a reproduction of the
paper's tables, and it is not a lossless speedup, because bf16 greedy flips
tokens when the top-2 gap is one unit in the last place.

## 6. Repo claims not verified here

- GPU tau/speedup matching ESP Tables 1–15 on the full 480-prompt set.
- EMA beating matched ESP on SpecBench. The dev slice goes the other way, and
  the zero-step control says the direction is not the cause.
- README's "172 checks": the current `tests/check_correctness.py` runs **196**.
