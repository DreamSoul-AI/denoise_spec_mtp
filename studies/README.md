# Studies

一次研究是一个目录：`study.yaml` 声明因素，`docs/PLAN.md` 写问题和判定，`docs/STUDY_REPORT.md` 写结果。`runs/` 不进 git。Study 由已安装的 RPipe 执行（目录与阶段合同见 RPipe `studies/README.md` 与 `docs/code/flow.md` §14）。

SpecMTP Study 的固定写法：

- `recipe: recipe.py`，内容是 `from spec_mtp.recipe import register`：构造前校验配置并注册 `spec_mtp` source；
- `flow: {study_phases: true, prepare_shared: false}`；
- `flow/write/run.py` 调 `spec_mtp.flow.checks.run_gate`：`exact_match_rate` 不是 1 的 Run 在 result 定稿前记为 `failed`；
- `flow/process/run.py` 只在 `ctx.scope == 'study'` 时调 `study_gate`：index 缺 Run、只是子集、有失败或源码 digest 不一致都不算完整通过，结果写 `spec_mtp_study_check.json`；
- 其他阶段用库默认实现，不加空 hook。

已记录的接受数在 [history_extrapolation](history_extrapolation/docs/STUDY_REPORT.md)。那一轮没有 `study.yaml`，不重跑。

| **Study** | **状态** | **问题** |
| --- | --- | --- |
| [history_extrapolation](history_extrapolation/docs/PLAN.md) | 已记录 | 长记忆 gamma 接受的 draft 是否多于冻结 prompt mean |
| [hw_probe](hw_probe/docs/PLAN.md) | 已记录 | 2026-10-07 本机 GPU 显存探针 |
| [smoke_tiny_llama](smoke_tiny_llama/docs/PLAN.md) | CPU 门 | 随机 tiny LLaMA 上三种 mask 是否与普通生成逐 token 一致；含 2026-10-12 重构前后对照 |
| [_template](_template/docs/PLAN.md) | 空模板 | 复制成 `studies/<name>/` 后再写问题和因素 |

新 Study 从 `_template` 复制。先写 `docs/PLAN.md`，再由 Study 自己的脚本开跑：

```text
set PYTHONUTF8=1
python -m spec_mtp make studies/<name>
studies/<name>/scripts/launch.ps1
```

`python -m spec_mtp make` 等于 `python -m rpipe make` 再加 SpecMTP 源码清单 `spec_mtp_sources.json`。`make` 写出 `studies/<name>/scripts/`（`launch.ps1` / `launch.sh` 调 `rpipe launch`）。脚本、`provenance.json`、`spec_mtp_sources.json` 不进 git。SpecBench 在 `studies/history_extrapolation/data/`，下载脚本是 `studies/history_extrapolation/scripts/download_data.sh`。`runs/` 和 `results/` 也不进 git。
