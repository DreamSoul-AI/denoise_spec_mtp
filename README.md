# Speculative MTP — ESP Reproduction + EMA-Velocity Masks

Training-free multi-token prediction. Two things live here:

1. A faithful reproduction of **ESP** (Embedding-Space Probing) from
   *"Efficient Training-Free Multi-Token Prediction via Embedding-Space
   Probing"* (Goel, Gagrani, Lee, Lott — Qualcomm AI Research, ICML 2026),
   [papers/2603.17942v2.pdf](papers/2603.17942v2.pdf) — including **every
   masking setting in its ablations**.
2. **EMA-velocity** (ours): the same pipeline with ESP's Equations (4)/(5)
   swapped for EMA-of-differences velocity extrapolation — see
   [notes/ema_velocity_method.md](notes/ema_velocity_method.md) and
   [lark_transcripts/summary_july31.md](lark_transcripts/summary_july31.md).

The layout intentionally mirrors the sibling `layerwise_speculative_mtp/`
project:

```text
configs/     smoke/ (CPU, no downloads)  +  hf/<family>/run_0 + ablations
scripts/     download_data.sh, run_*.sh sweeps (one per paper table)
src/
  algorithms/  esp_mtp, ar_baseline, alignment_probe
  core/        config / logger / tools
  data/        specbench, dolly, local_prompts
  models/      hf_causal (LLaMA3 / Qwen3 / tiny_llama adapter)
  spec/        mask_providers, tree, tree_attention, kv_cache, decoding
tests/       CPU correctness checks (no GPU, no downloads)
```

## Quick Start (CPU, no downloads)

```bash
pip install -r requirements.txt
bash scripts/run_correctness_checks.sh   # 172 checks incl. losslessness vs AR
bash scripts/run_smoke.sh                # tiny random LLaMA through main.py
```

Every smoke summary must show `exact_match_rate=1.0000`: speculative output
is verified token-for-token against plain autoregressive decoding.

## GPU Server

```bash
bash scripts/download_data.sh --models --dolly   # SpecBench + weights + Dolly
bash scripts/run_main_results.sh llama3_2_3b     # Table 1 row (ESP + ours + AR)
bash scripts/run_main_results.sh llama3_1_8b
bash scripts/run_main_results.sh qwen3_8b
bash scripts/run_main_results.sh qwen3_32b
```

Results land in `results/<...>/spec_metrics.csv` (per prompt) and
`summary.csv` (per category + overall).

## Method (ESP, Sections 2–3)

- **Mask injection**: k mask tokens synthesized in embedding space are
  appended to the input; mask *i* occupies the slot of future token x_{t+i}
  and its logits predict x_{t+i+1}. Init Eq (4): mean of prompt embeddings;
  update Eq (5): `m += lam * (e_last_generated - m)` per generated token.
- **Draft tree**: Top-K candidates per mask under Top-1 expansion
  (Appendix D). Static branches `[K_1..K_k]` or dynamic Algorithm 1
  (cumulative-probability budget `BC/(k+1) - 1`). Pruning (Sec 3.5) replaces
  parent-repeat candidates with the next-best token.
- **Blocks**: one decode forward processes `[root | tree nodes | k masks per
  node]` = Eq (7) block complexity `(k+1)(1 + sum K_i)`, with a tree
  attention mask and tree position IDs; the same pass verifies drafts
  (exact/sample matching → lossless), yields the bonus token, and produces
  the next tree's mask logits (at the deepest accepted node's masks).
- **KV cache** keeps only root + accepted path after each pass.
- **Efficient impl** (Appendix E): cached attention-mask structure +
  uniform PID shift; `spec.impl: naive` rebuilds per step (Table 4).

## Config → Paper Map

| Paper | Config / script |
|---|---|
| Table 1, Figs 4–5 (main, BC=10/30/60) | `configs/hf/<family>/run_0/esp_bc*.yaml`, `scripts/run_main_results.sh` |
| Table 2 (dynamic vs static trees) | `scripts/run_ablation_tree.sh`, `run_0/esp_bc60_dynamic.yaml` |
| Table 3 (# masks at BC=60) | `scripts/run_ablation_masks.sh`, `ablations/masks{1,3}_bc60.yaml` |
| Table 4 (naive vs efficient impl) | `scripts/run_ablation_impl.sh`, `ablations/impl_naive_bc30.yaml` |
| Table 5 (mask init: Last-K / Sample / Mean) | `scripts/run_ablation_init.sh`, `ablations/init_*_bc30.yaml` |
| Fig 2 (layer-wise cosine alignment) | `configs/hf/llama3_2_3b/run_0/alignment_probe.yaml` |
| G.3 (temperature 1.0) | `scripts/run_ablation_temperature.sh`, `ablations/temp1_bc*.yaml` |
| G.4 (BC=120, 3 masks) | `ablations/bc120_masks3.yaml` |
| G.8 (init at mu+5s / mu+10s) | `ablations/init_offset{5,10}_bc60.yaml` |
| G.9 (lambda 0.01/0.1/0.5) | `scripts/run_ablation_lambda.sh`, `ablations/lam*_bc30.yaml` |
| G.7 (tree pruner on/off) | `scripts/run_ablation_pruner.sh`, `ablations/pruner_off_bc30.yaml` |
| extra: frozen mask (no Eq 5 update) | `ablations/update_off_bc30.yaml` |
| ours: EMA velocity + sweeps | `run_0/ema_bc*.yaml`, `scripts/run_ema_ablations.sh` |

Baselines PLD / STAND / LADE are other repos' methods (paper Appendix F);
they are not reimplemented here — the AR baseline provides the speedup
denominator, and paper numbers provide the comparison points.

## Metrics

- `tau`: committed tokens (accepted + bonus) per decode model call — the
  paper's average acceptance length; `call_reduction = 1 - 1/tau` (Table 6).
- `speedup`: AR wall time / speculative wall time on identical prompts.
- `exact_match_rate`: losslessness audit vs AR under a shared seed
  (temperature 0 and 1 both supported); must be 1.0.

Full column-by-column schemas for `spec_metrics.csv` / `summary.csv`, the
audit invariants relating them, and the per-algorithm schema differences
are in [notes/metrics.md](notes/metrics.md).

## Caveats / paper ambiguities

Deliberate interpretation choices are documented in
[notes/implementation_notes.md](notes/implementation_notes.md) — notably the
Last-K index typo, the per-dimension sampling sigma, the Table 3 `[7,5,3]`
block-complexity inconsistency (64 vs 60), the 100- vs 256-token output
lengths, and Eq (5)'s per-token update granularity. Use
`attn_implementation: eager` (or sdpa); flash-attention 2 cannot take the 4D
tree masks.
