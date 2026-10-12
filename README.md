# Speculative MTP — ESP Reproduction + EMA-Velocity Masks

Training-free multi-token prediction:

1. **ESP** (Embedding-Space Probing), [arXiv:2603.17942](https://arxiv.org/abs/2603.17942). PDF is local-only: [docs/papers/index.md](docs/papers/index.md).
2. **EMA-velocity**: the same pipeline, mask from EMA of input-embedding differences.

Agent notes: [AGENTS.md](AGENTS.md). Layout and the SpecMTP `origin` / shared rule: [docs/layout.md](docs/layout.md). Decode / paper mismatches: [docs/architecture.md](docs/architecture.md). How to run a Study: [studies/readme.md](studies/readme.md). Recorded accepts: [docs/history-extrapolation.md](docs/history-extrapolation.md).

`src/rpipe/` is a file copy of `diaoenmao/RPipe` `main` at `804b3823ab6d2af46cbda1a65688ca8b76c60b22` (v0.3.0). SpecMTP registers onto that copy through a Study recipe.

## Quick start (CPU)

```text
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -e ".[dev]"
set PYTHONUTF8=1
python -m pytest tests/spec_mtp
```

Smoke: `python -m spec_mtp make studies/smoke` then `python -m spec_mtp launch studies/smoke`. Every Run must have `exact_match_rate=1`.

GPU cells are new Studies under `studies/`. Copy `_template/`. SpecBench lives in `datasets/spec_bench/` and is copied into that Study's `shared/data` on make. ModelScope / HF weights land in `shared/model`. Do not start from `src/main.py`.
