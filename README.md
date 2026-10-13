# Denoising Speculative Decoding

ESP reproduction + EMA-velocity masks.

Training-free multi-token prediction:

1. **ESP** (Embedding-Space Probing), [arXiv:2603.17942](https://arxiv.org/abs/2603.17942). PDF is local-only: [docs/papers/index.md](docs/papers/index.md).
2. **EMA-velocity**: the same pipeline, mask from EMA of input-embedding differences.

Agent notes: [AGENTS.md](AGENTS.md). Layout and the SpecMTP `origin` / shared rule: [docs/layout.md](docs/layout.md). Decode / paper mismatches: [docs/architecture.md](docs/architecture.md). Structure mapping: [docs/rpipe-migration.md](docs/rpipe-migration.md). How to run a Study: [studies/README.md](studies/README.md). Recorded accepts: [docs/history-extrapolation.md](docs/history-extrapolation.md).

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

For a fresh [smoke](studies/smoke/README.md), copy `studies/smoke` to an isolated directory and set a new Study name and `algorithm.config.version` before `python -m spec_mtp make <copy>` and `launch <copy>`. Every Run must have `exact_match_rate=1` and complete raw evidence. Source/input changes require explicit make/remake; do not rerun historical Run IDs. See the [acceptance report](studies/smoke/docs/STUDY_REPORT.md).

GPU cells are new Studies under `studies/`. Copy `_template/`. SpecBench lives in `datasets/spec_bench/` and is copied into that Study's `shared/data` on the first Run. ModelScope / HF weights land in `shared/model`. Do not start from `src/main.py`.

## Development

Repository: [DreamSoul-AI/denoising-speculative-decoding](https://github.com/DreamSoul-AI/denoising-speculative-decoding). Default branch: `main`. Changes enter `dev` through a work-branch PR, then reach `main` through a PR from this repository's `dev`. Both paths require `cpu-checks` and `Branch flow`; existing approvals remain required.

Research-to-Study extraction: [protocol](docs/research/rpipe-study-extraction.md), with the real-model [input-mask baseline](studies/input_mask_baseline/README.md). This prerequisite does not implement or validate the output-space / Kalman hypotheses.

Current checkpoint and the v0.3.1 migration queue: [handover](docs/handover.md). The execution copy remains v0.3.0 until the documented upgrade and regression pass.
