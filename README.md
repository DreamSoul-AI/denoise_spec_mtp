# Denoising Speculative Decoding

ESP reproduction + EMA-velocity masks.

Training-free multi-token prediction:

1. **ESP** (Embedding-Space Probing), [arXiv:2603.17942](https://arxiv.org/abs/2603.17942). PDF is local-only: [docs/papers/index.md](docs/papers/index.md).
2. **EMA-velocity**: the same pipeline, mask from EMA of input-embedding differences.

Agent notes: [AGENTS.md](AGENTS.md). Layout and the SpecMTP `origin` / shared rule: [docs/layout.md](docs/layout.md). Decode / paper mismatches: [docs/architecture.md](docs/architecture.md). Structure mapping: [docs/rpipe-migration.md](docs/rpipe-migration.md). How to run a Study: [studies/README.md](studies/README.md). Recorded accepts: [docs/history-extrapolation.md](docs/history-extrapolation.md).

`src/rpipe/` is a file copy of `diaoenmao/RPipe` `main` at `7a15c46b75c5eb951cccd60ed7b9fc3463db90f5` (v0.3.1). SpecMTP registers onto that copy through a Study recipe.

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

Current checkpoint, validation and remaining real-model prerequisite: [handover](docs/handover.md). The execution copy is fixed at v0.3.1; current-device acceptance is tracked in the handover and Study reports.

Current-device v0.3.1 checks: [smoke acceptance](studies/smoke/docs/STUDY_REPORT.md) and [validation](studies/smoke/docs/v031_validation.json). The four real-model input-mask prerequisite Runs completed with ModelScope Qwen3-0.6B, FP32/eager and strict source/evidence gates; see the [report](studies/input_mask_baseline/docs/STUDY_REPORT.md).

Next stage: [output-space chain prerequisite](studies/output_space_prerequisite/README.md), tied final-hidden order0/order1 with a matched frozen-input chain. Implementation and four-case real-model correctness gates passed. On the fixed development prompt the output masks accepted10 drafts each versus17 for the matched input chain; no superiority or Kalman claim.

Follow-up: [three-prompt small matrix](studies/output_space_small_matrix/README.md) and matched-prefix analysis. All outputs remain AR-identical; q172–q174 acceptance counts for input/order0/order1 are1/1/1,5/1/3,0/1/1. These mixed development observations do not establish stable superiority.

历史Qwen3-4B **FP32**：[同prompt first26复验](studies/output_space_4b_recheck_v2/docs/STUDY_REPORT.md)两阶总接受均高于输入，[固定4条新输入](studies/output_space_4b_holdout/docs/STUDY_REPORT.md)未保持收益，[历史输入EMA同链控制](studies/output_space_4b_input_control/docs/STUDY_REPORT.md)已执行。三批全AR一致，计时关闭；这些结果及此前0.6B机理/罕见事件记录保留归档，不代替当前BF16证据。


2026-10-15 当前进度：历史4B FP32归档经PR #7合dev；[ESP Table1全480 BF16复现](studies/esp_table1_bf16_full_argmax/docs/STUDY_REPORT.md)四格和原生process完成，BC30 pooled τ=1.563378、BC60单mask=1.647301，未达到1.63/1.74，负结果保留，PR #10经CI合dev。现执行[4B BF16五方法加AR配对](studies/qwen3_4b_bf16_five_methods/docs/STUDY_REPORT.md)，同480条、BC30/60、双mask动态剪枝树；独立AR、BC30五方法与BC60 frozen mean/输入零阶共8/11格原生成功，全部Spec提交token的argmax审计通过，完整两预算结论待剩余三格。独立AR逐token一致率仅报告、不作失败门。其他研究暂停；8B仅限该Table1复现，不新增FP32实验、不测速，不强推、合main或删除分支和数据。
