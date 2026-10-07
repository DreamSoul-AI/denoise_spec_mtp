# Speculative MTP — ESP Reproduction + EMA-Velocity Masks

Training-free multi-token prediction. Two things live here:

1. A reproduction of **ESP** (Embedding-Space Probing),
   [arXiv:2603.17942](https://arxiv.org/abs/2603.17942), including the masking
   settings in its ablations. The PDF is local-only: see
   [docs/papers/README.md](docs/papers/README.md).
2. **EMA-velocity**: the same pipeline, with the ESP mask replaced by an EMA
   of input-embedding differences.

How the loop, the two masks, and the result files fit together:
[docs/architecture.md](docs/architecture.md). History-extrapolation counts:
[docs/research.md](docs/research.md). CI: [docs/ci.md](docs/ci.md). Next
restructuring, not started: [docs/BRAINSTORM.md](docs/BRAINSTORM.md).

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
docs/        architecture, research, CI, brainstorm; papers/ is local PDFs
```

## Quick Start (CPU, no downloads)

```bash
pip install -r requirements.txt
bash scripts/run_correctness_checks.sh
bash scripts/run_smoke.sh
python scripts/run_ci_checks.py
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
`summary.csv` (per category + overall). Column meanings are in
[docs/architecture.md](docs/architecture.md).

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
| extra: frozen mask (no update) | `ablations/update_off_bc30.yaml` |
| ours: EMA velocity + sweeps | `run_0/ema_bc*.yaml`, `scripts/run_ema_ablations.sh` |

Baselines PLD / STAND / LADE are other repos' methods. They are not
reimplemented here. The AR baseline is the speedup denominator.

## Reading choices

Where this code does not follow a literal line of the paper — Last-K index,
per-dimension sampling sigma, the Table 3 block size, 100 vs 256 new tokens,
and the static tree behind the BC=60 headline — the list is in
[docs/architecture.md](docs/architecture.md). Use `attn_implementation: eager`
or sdpa. Flash-attention 2 cannot take the 4D tree masks.
