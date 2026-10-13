# Speculative MTP — ESP Reproduction + EMA-Velocity Masks

Training-free multi-token prediction:

1. **ESP** (Embedding-Space Probing), [arXiv:2603.17942](https://arxiv.org/abs/2603.17942). PDF is local-only: [docs/papers/index.md](docs/papers/index.md).
2. **EMA-velocity**: the same pipeline, mask from EMA of input-embedding differences.

Agent notes: [AGENTS.md](AGENTS.md). Layout and the SpecMTP `origin` / shared rule: [docs/layout.md](docs/layout.md). Decode / paper mismatches: [docs/architecture.md](docs/architecture.md). How to run a Study: [studies/readme.md](studies/readme.md). Recorded accepts: [docs/history-extrapolation.md](docs/history-extrapolation.md).

`src/rpipe/` is a file copy of `diaoenmao/RPipe` `main` at `804b3823ab6d2af46cbda1a65688ca8b76c60b22` (v0.3.0). SpecMTP registers onto that copy through a Study recipe.

## Quick start

Existing GPU environments: preserve CUDA torch; install the project with `pip install -e ".[dev]" --no-deps` and supply missing non-torch dependencies separately. The following CPU setup is for a new CPU environment.

### New CPU environment

```text
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -e ".[dev]"
set PYTHONUTF8=1
python -m pytest tests/spec_mtp
```

Smoke: `python -m spec_mtp make studies/smoke` then `python -m spec_mtp launch studies/smoke`. Every Run must have `exact_match_rate=1` and complete raw evidence. Change `algorithm.config.version` before accepting new sources/inputs with make/remake. See [acceptance report](studies/smoke/docs/study_report.md).

GPU cells are new Studies under `studies/`. Copy `_template/`. SpecBench lives in `datasets/spec_bench/` and is copied into that Study's `shared/data` on the first Run. ModelScope / HF weights land in `shared/model`. Do not start from `src/main.py`.
