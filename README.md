# Speculative MTP — ESP Reproduction + EMA-Velocity Masks

Training-free multi-token prediction. Two things live here:

1. A reproduction of **ESP** (Embedding-Space Probing),
   [arXiv:2603.17942](https://arxiv.org/abs/2603.17942), including the masking
   settings in its ablations. The PDF is local-only: see
   [docs/papers/INDEX.md](docs/papers/INDEX.md).
2. **EMA-velocity**: the same pipeline, with the ESP mask replaced by an EMA
   of input-embedding differences.

Docs (UPPERCASE filenames): [ARCHITECTURE](docs/ARCHITECTURE.md),
[CI](docs/CI.md), [LAYOUT](docs/LAYOUT.md),
[TESTING](docs/TESTING.md), [BRAINSTORM](docs/BRAINSTORM.md).
Recorded accepts: [history_extrapolation](studies/history_extrapolation/docs/STUDY_REPORT.md).
Agent notes: [AGENTS.md](AGENTS.md).

```text
src/
  rpipe/       full RPipe package: structure/ + flow/, unchanged
  spec_mtp/    RPipe copied file for file; SpecMTP sits in each layer's spec_mtp/ submodule
               (the decoder is structure/algorithm/eval/spec_mtp/)
studies/           each Study holds its code and data; scripts/, runs/, and results/ stay local
configs/       old per-run YAML; not an entry
tests/         tests/spec_mtp mirrors src/spec_mtp
docs/          ARCHITECTURE, CI, LAYOUT, TESTING, BRAINSTORM; papers/ is local PDFs
```

## Quick Start (CPU, no downloads)

```bash
pip install -e .
set PYTHONUTF8=1
python -m pytest tests/spec_mtp
```

The smoke Study is `studies/smoke_tiny_llama`. A person runs the script that Study generates: `studies/smoke_tiny_llama/scripts/launch.ps1`. Every smoke summary must show `exact_match_rate=1.0000`.

## Run a Study

A run starts from `studies/<name>`, not from `src/main.py`. `make` writes
`studies/<name>/scripts/` (gitignored). That script is what you run.

```text
set PYTHONUTF8=1
python -m spec_mtp make studies/<name>
studies/<name>/scripts/launch.ps1
```

On bash the same directory has `launch.sh`. CI calls `python -m spec_mtp run`
on `studies/smoke_tiny_llama` directly; that is the same runner the script uses.

## GPU Server

```bash
bash studies/history_extrapolation/scripts/download_data.sh --models --dolly
```

A GPU cell is a Study under `studies/`, then `studies/<name>/scripts/launch.ps1`.
Per-prompt rows and the category summary land in `studies/<name>/runs/<id>/assets/`.

## Config → Paper Map

These YAML files record the paper factors. A run is a Study, not one of these files.

| Paper | Config |
|---|---|
| Table 1, Figs 4–5 (main, BC=10/30/60) | `configs/hf/<family>/run_0/esp_bc*.yaml` |
| Table 2 (dynamic vs static trees) | `run_0/esp_bc60_dynamic.yaml` |
| Table 3 (# masks at BC=60) | `ablations/masks{1,3}_bc60.yaml` |
| Table 4 (naive vs efficient impl) | `ablations/impl_naive_bc30.yaml` |
| Table 5 (mask init: Last-K / Sample / Mean) | `ablations/init_*_bc30.yaml` |
| Fig 2 (layer-wise cosine alignment) | `configs/hf/llama3_2_3b/run_0/alignment_probe.yaml` |
| G.3 (temperature 1.0) | `ablations/temp1_bc*.yaml` |
| G.4 (BC=120, 3 masks) | `ablations/bc120_masks3.yaml` |
| G.8 (init at mu+5s / mu+10s) | `ablations/init_offset{5,10}_bc60.yaml` |
| G.9 (lambda 0.01/0.1/0.5) | `ablations/lam*_bc30.yaml` |
| G.7 (tree pruner on/off) | `ablations/pruner_off_bc30.yaml` |
| extra: frozen mask (no update) | `ablations/update_off_bc30.yaml` |
| ours: EMA velocity + sweeps | `run_0/ema_bc*.yaml` |

Baselines PLD / STAND / LADE are other repos' methods. They are not
reimplemented here. The AR baseline is the speedup denominator.

## Reading choices

Where this code does not follow a literal line of the paper — Last-K index,
per-dimension sampling sigma, the Table 3 block size, 100 vs 256 new tokens,
and the static tree behind the BC=60 headline — the list is in
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Use `attn_implementation: eager`
or sdpa. Flash-attention 2 cannot take the 4D tree masks.
