# Implementation Notes — ESP Reproduction

Paper: *Efficient Training-Free Multi-Token Prediction via Embedding-Space
Probing* (Goel et al., Qualcomm, ICML 2026), arXiv 2603.17942v2. No official
code exists (the v1 was rejected from ICLR; see the July 31 call), so this is
a from-scratch reimplementation from the paper text.

## Paper → code map

| Paper element | Code |
|---|---|
| Eq (1)–(3) generation/verification setup | `spec/decoding.py` |
| Eq (4) mean-prompt mask init | `spec/mask_providers.py::ESPMaskProvider` (`init: mean_prompt`) |
| Eq (5) mask EMA update, lambda=0.1 | `ESPMaskProvider.on_token_committed` |
| Table 5 inits (Last-K / Sample / Mean) | `init: last_k / sample_embedding / mean_prompt` |
| G.8 out-of-distribution init mu+c*sigma | `init: offset_embedding`, `offset_scale` |
| G.9 lambda ablation | `mask.lam` |
| Sec 3.2 / Fig 2 / Appendix A alignment | `algorithms/alignment_probe.py` |
| Sec 3.3 block complexity Eq (7) | `spec/tree.py::DraftTree.block_complexity`, `node_budget_for` |
| Sec 3.4 / Alg 1 dynamic tree | `spec/tree.py::build_dynamic_tree` |
| Appendix D Top-1 expansion | both tree builders (only the depth-Top-1 node has children) |
| Sec 3.5 pruning | `spec/tree.py::_topk_with_pruning` |
| Fig 3/7 block layout, tree attention, PIDs | `spec/tree_attention.py` |
| Appendix E efficient mask/PID reuse | `spec/tree_attention.py::TreeAttentionCache` (`spec.impl`) |
| Sec 4 metrics (tau, S/R), Table 6 call reduction | `algorithms/esp_mtp.py::_aggregate` |
| SpecBench evaluation | `data/specbench.py`, `scripts/download_data.sh` |

## Algorithmic reading (the parts the paper leaves implicit)

- **Slot semantics.** Mask *i* is placed at position `pid(owner)+i`, i.e. it
  occupies the *slot* of the i-th future token after its owner, and its
  output distribution proposes the token for the following position. At
  prefill the k masks trail the prompt (plain causal attention suffices);
  during decode every block token (root + each draft node) carries its own k
  masks, giving exactly Eq (7): `(k+1)(1 + sum K_i)`.
- **Simultaneous generate + verify.** One decode forward: (a) the model's
  own prediction chain is walked through the tree (exact match ⇒ accept),
  (b) the first mismatch's prediction is the committed bonus/correction
  token, (c) the next tree is seeded from the mask logits of the deepest
  accepted node — its mask 1 sits in the slot of the just-committed bonus
  token, so the proposals correctly target the token after the next root.
- **Losslessness.** "Sample matching" = accept only exact matches against
  the model's own (greedy or sampled) chain. One RNG draw per committed
  token in chain order ⇒ with a shared generator the output is
  token-identical to plain AR decoding. This is asserted in
  `tests/check_correctness.py` across the whole config grid and surfaced as
  `exact_match_rate` in every run with `run_ar_baseline: true`.
- **KV cache.** A block forward appends KV for all block positions; after
  verification, `spec/kv_cache.py::keep_block_positions` retains prefix +
  root + accepted path only. The bonus token is never cached — it is the
  next block's root. Invariant asserted each step: `cache_len == root_pos`.
- **Dynamic tree = Algorithm 1 under Top-1 expansion.** At decode time only
  the k mask distributions exist (not per-node logits), so the candidate
  pool at depth i chains below the depth-(i-1) Top-1 token with
  multiplicative cumulative probabilities; the `BC/(k+1) - 1` best
  trajectories are kept (ancestor closure enforced). This matches the
  paper's Fig 6 example (BC=30, two masks → 7+2 nodes selected from 9+8
  pools).

## Ambiguities and the choices made

1. **Eq (5) update granularity.** `m_i[s+1] = m_i[s] + λ(e_{t+s} − m_i[s])`
   indexes generation steps `s` by *token*. When one pass commits several
   tokens we apply the update once per committed token, in order.
2. **Last-K index.** The paper writes `m_i = e_{t−k−i}`, which for i=1..k
   selects tokens *before* the last k — contradicting its own description
   "uses the embeddings of the last k prompt tokens". We implement the
   description: `m_i = e_{t−k+i}` (so `m_k = e_t`).
3. **Sample init sigma.** `N(µ, σ²I)` with "µ and σ the mean and standard
   deviation across all V vocabulary embeddings": σ is computed per
   dimension (a diagonal fit), which also matches G.8's elementwise `µ+5σ`.
4. **Table 3 `[7,5,3]`.** Eq (7) gives (3+1)(1+15)=64 ≠ 60. We reproduce
   the printed branches literally and log the realized BC (64).
5. **Output length.** Section 4 says 100 tokens (A100); Table 1's caption
   says 256 (H100). Configs default to `max_new_tokens: 100`; use
   `--set eval.max_new_tokens=256` to mirror Table 1.
6. **G.4 BC=120 branches.** Only "decreasing order" is stated; we use
   `[15,10,4]`, which satisfies Eq (7) exactly: 4·(1+29)=120.
7. **Prefill masks see only the prompt.** The first tree is proposed before
   x_{t+1} exists; mask 1's slot is x_{t+2}'s. This matches Fig 1 (middle).
8. **Qwen3 chat template.** The paper is silent on thinking mode; 100-token
   direct answers imply it is off → `chat_template_kwargs.enable_thinking:
   false` in the Qwen configs.
9. **Efficient impl scope.** Appendix E's cached mask/PID reuse assumes a
   fixed tree structure; `spec.impl: efficient` therefore requires
   `tree.mode: static` (the paper's dynamic-tree runs pay the naive cost —
   their "Future Directions" concede exactly this).
10. **Table 1 tree mode.** The main-results BC=60 configs use the STATIC
    [15,4] tree with the efficient impl, not dynamic expansion: Table 1's
    BC=60 S/R (1.22x / 1.38x) is numerically identical to Table 4's
    "Efficient" m1,m2(60) rows, and Appendix C states no efficient
    dynamic-tree implementation exists — so the paper's headline speedups
    were produced static+efficient. tau is unaffected either way (Table 2:
    dynamic 1.630/1.712 vs static 1.631/1.708). Dynamic expansion is
    reproduced via `*_bc60_dynamic.yaml` (Table 2 / Section 4.2).
    (Caught by the adversarial faithfulness review.)
11. **tau accounting.** tau = committed (accepted + bonus) per *decode*
    call; the prefill forward is counted separately, mirroring standard
    SpecBench practice. `call_reduction = 1 − 1/τ` reproduces Table 6's
    arithmetic (e.g. τ=1.56 → 35.9%).
12. **Baselines.** PLD/STAND/LADE (Appendix F) are external methods and are
    not reimplemented; the AR baseline supplies wall-time and losslessness
    references. Appendix F's configurations are recorded here for when we
    wire their official repos: PLD depth-10 chain; LADE BC=(L−1)(W+G) with
    (L,W,G) = (3,4,1)/(4,5,5)/(5,8,7) for BC 10/30/60.

## Verification status

- `tests/check_correctness.py`: 172 checks — provider algebra (Eq 4/5, all
  inits, EMA-velocity recursion), Eq 7 accounting, Top-1 expansion, pruning,
  Algorithm 1 budget/closure/confidence-adaptivity, Appendix-E mask/PID
  equality with the naive path, and end-to-end losslessness vs AR on a tiny
  random LLaMA over {esp, ema_velocity} × {k=1,2,3} × {static, dynamic} ×
  {pruning on/off} × {naive, efficient} × {T=0, T=1}. All pass on CPU
  (torch 2.13, transformers 5.14).
- `scripts/run_smoke.sh` runs the same stack through `src/main.py` configs;
  every summary reports `exact_match_rate=1.0000`.
- GPU-scale numbers (tau vs paper Tables 1–15) require the real models —
  everything is wired so `scripts/run_main_results.sh` reproduces them once
  a GPU server is attached.
