# Studies

一次研究是一个目录：`study.yaml` 声明因素，`docs/PLAN.md` 写问题和判定，`docs/STUDY_REPORT.md` 写结果。`runs/` 不进 git。

已记录的接受数在 [history_extrapolation](history_extrapolation/docs/STUDY_REPORT.md)。那一轮没有 `study.yaml`，不重跑。

| **Study** | **状态** | **问题** |
| --- | --- | --- |
| [history_extrapolation](history_extrapolation/docs/PLAN.md) | 已记录 | 长记忆 gamma 接受的 draft 是否多于冻结 prompt mean |
| [hw_probe](hw_probe/docs/PLAN.md) | 已记录 | 2026-10-07 本机 GPU 显存探针 |
| [smoke_tiny_llama](smoke_tiny_llama/docs/PLAN.md) | CPU 门 | 随机 tiny LLaMA 上三种 mask 是否与普通生成逐 token 一致 |
| [_template](_template/docs/PLAN.md) | 空模板 | 复制成 `studies/<name>/` 后再写问题和因素 |

新 Study 从 `_template` 复制。先写 `docs/PLAN.md`，再由 Study 自己的脚本开跑：

```text
set PYTHONUTF8=1
python -m spec_mtp make studies/<name>
studies/<name>/scripts/launch.ps1
```

`make` 写出 `studies/<name>/scripts/`（`launch.ps1` 调 `python -m spec_mtp launch`）。脚本不进 git。SpecBench 在 `studies/history_extrapolation/data/`，下载脚本是 `studies/history_extrapolation/scripts/download_data.sh`。`runs/` 和 `results/` 也不进 git。
