# layout

`src/rpipe/` 是上游 RPipe `main` 的文件拷贝，提交 `7a15c46b75c5eb951cccd60ed7b9fc3463db90f5`（`src/rpipe/ORIGIN`，v0.3.1）。`src/spec_mtp/` 只放 SpecMTP，经 Study recipe 注册。不要把 SpecMTP 写进 `rpipe` 的默认 source。

```text
src/
  rpipe/                   vendored RPipe；Windows 上 __init__.py 先 import torch
  spec_mtp/
    recipe.py              compatibility exports for structure/api/recipe.py
    flow/cli.py            薄入口；根 cli.py 保留 console script 兼容导出
    flow/{collect,summarize,write,process}/   专项阶段；checks.py 兼容导出
    structure/artifact/evidence.py   实际权重/输入/runtime 证据
    structure/             algorithm / data / model / system / control / artifact
datasets/spec_bench/       SpecBench 源文件；Run prepare 拷进 shared/data
studies/                   见 studies/README.md
configs/hf/                论文格子的旧 YAML；不是入口
tools/                     ci_local.py, windows_selfcheck.py, profile_cpu.py,
                           decode_fingerprint.py, package_selfcheck.py
tests/spec_mtp/            跟着 src/spec_mtp
docs/                      architecture, layout, testing, windows, brainstorm,
                           history-extrapolation；research/；papers/
```

产物：`studies/<name>/runs/<id>/`。`runs/`、`shared/`、`scripts/`、`index.json`、`process.json`、`provenance.json`、`spec_mtp_sources.json` 不进 git。

## shared/

RPipe 的 make 共享下载只认识 torchvision 数据集。SpecMTP Study 写 `flow.prepare_shared: false`，但 **Run prepare 仍然把东西写进 `shared/`**：

- SpecBench jsonl → `studies/<name>/shared/data/specbench/`
- ModelScope / HF 权重 → `studies/<name>/shared/model/`

同一 Study 里不要让每个 Run 再下一遍。源文件在 `datasets/spec_bench/`。

Study `recipe.py` 在 import 时调用 `register_sources()`。

## 不要写 `origin: foreign`

这是本仓库相对 RPipe 的规则。缺省就是 foreign，并且不改环境变量。一旦写出 `origin`，prepare 会设置 `HF_ENDPOINT`。权重走 `model.config.hub: modelscope`。只有需要 RPipe 去改 HF 镜像时才写 `origin: domestic`。

## Study 合同（2026-10-13）

目录入口统一 README.md，docs/PLAN.md 与 docs/STUDY_REPORT.md 分别保存计划和人类结论；NUMBERS 保留 report 数字。两份 YAML 仍按基底 → fixed → axes/seed 合并，不搬动已有研究配置。smoke 的原交付 version 和正式 JSON 保留，新实测采用隔离目录与新 version。阶段仅保留 collect/summarize/write/process 的专项扩展，默认 prepare/execute 通过 recipe、builder 与 Algorithm 执行。training-free 报告用真实解码结果图适配上游学习曲线要求，不增加训练或恢复承诺。完整合同见 [Study 指南](../studies/README.md)。

当前结构迁移详见 [rpipe-migration.md](rpipe-migration.md)：data 的业务从 __init__ 移至 datasets，跨层输入与注册由 structure/api 组装，纯证据核验在 structure/artifact/validation。make、prepare 与 execute 无专项编排时直接复用库；不补空壳。

`tools/diagnose_output_windows.py` follows the existing direct-decoder profiling utilities. It observes fixed q173 windows, binds tool/PLAN/native raw/source hashes and refuses mismatching replay. Full selected tensors stay in a new .tmp directory; scalar diagnosis belongs to the Study. Scientific src, original Run and source locks are retained.

`tools/diagnose_mask_scale.py` uses the saved window tensors to cross the two observed directions/norms at one predeclared position, with four isolated causal forwards. It reuses the existing model wrapper and scalar helpers; it does not alter decoder/provider/config or choose a new default.

`tools/diagnose_proxy_transfer.py` scopes one predeclared provider-return vector replacement to a diagnostic replay. It infers seed ownership from actual root progress and verifies the returned trace, keeping post-intervention paths rather than forcing baseline acceptance. Its PLAN/results and offline `analyze_transfers.py` live in output_space_small_matrix; no scientific source/default/Run changes.

`tools/diagnose_cross_prompt.py` runs the predeclared q171/q172/q174 selection with the unchanged observation/transfer helpers. It binds both original Studies and compares same-position committed anchor/velocity rather than assuming they are equal. Selection and failure/termination controls live in output_space_small_matrix/docs/CROSS_PROMPT_PLAN.md; full local tensors remain ignored.
