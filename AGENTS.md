# Denoising Speculative Decoding Agent 工作约定

适用于本仓库。长期约定在这里。目录、解码口径、怎么跑 Study、测试入口在下表。数字在对应报告里。

## 1. 怎么工作

1. 先读 [README.md](README.md) 和相关入口。不必每次通读整个 `docs/`。
2. 文档和实现不一致时，先核对原因。已记下的接受数在 [history-extrapolation.md](docs/history-extrapolation.md)。
3. 改目录或分层看 [layout.md](docs/layout.md)。`src/rpipe/` 是上游拷贝（`src/rpipe/ORIGIN`，RPipe `main` v0.3.1）。`src/spec_mtp/` 只放 SpecMTP。不改拷过来的框架文件，Windows 先 import torch 除外。不要把 SpecMTP 注册进 `rpipe`。
4. 按改动范围验证，并改被这次改动碰到的文档。

## 2. 文档入口

| **需要** | **入口** |
| --- | --- |
| 目录、vendored RPipe、`origin` 规则、shared | [layout.md](docs/layout.md) |
| 解码、mask、和论文不一致的地方 | [architecture.md](docs/architecture.md) |
| 怎么跑 Study | [studies/README.md](studies/README.md) |
| RPipe 职责映射与迁移边界 | [rpipe-migration.md](docs/rpipe-migration.md) |
| 测试与 CI | [testing.md](docs/testing.md) |
| Windows | [windows.md](docs/windows.md) |
| 还没拍板的下一步 | [brainstorm.md](docs/brainstorm.md) |
| 研究计划草案（非 Study 合同） | [research/readme.md](docs/research/readme.md) |
| 论文 PDF | [papers/index.md](docs/papers/index.md)。PDF 不进 git |
| 问题与兼容性 | [bugs.md](docs/bugs.md) |
| 开发记录 | [record.md](docs/record.md) |
| 异机接手与待验范围 | [handover.md](docs/handover.md) |
| 已经记下的接受数 | [history-extrapolation.md](docs/history-extrapolation.md) |

一般技术文档文件名用小写；Study 目录入口用 `README.md`，计划、报告和数字用 `docs/PLAN.md`、`docs/STUDY_REPORT.md`、`docs/NUMBERS.md`，与固定 RPipe 合同一致。不要维护第二套大小写文档。

## 3. 协作

- 保留工作区里已有改动。临时输出放 `.tmp/`。Study 产物（`runs/`、`shared/`、`scripts/`、`index.json`、`process.json`）不进 git。
- 默认分支为 `main`。工作分支通过 PR 先进入 `dev`，再由同仓库 `dev` 的 PR 进入 `main`；不直接推 `dev`/`main`，不强推或删除长期分支。
- PR 必须通过 `cpu-checks` 和 `Branch flow`；保留现有审批要求。提交、推送、合并和实验仍按当次授权。

## 4. 代码放在哪

- `src/rpipe/`：调度、Flow、Tracker、artifact、make。提交见 `ORIGIN`。
- `src/spec_mtp/`：Data / Model / Algorithm（`(eval, spec_mtp)`）、`structure/api/recipe.py`、`flow/<phase>/run.py`、专项 artifact/evidence/validation；根 recipe/cli 与 flow.checks 仅兼容导出。注册发生在 Study `recipe.py`（import 时 `register_sources()`，Run 时 `register(ctx)`）。
- 入口：`python -m spec_mtp` 是薄封装，其余转给这份 `rpipe`。不恢复 `src/main.py`。不要加 `sitecustomize.py`。

## 5. 实验

- 开跑前写 `studies/<name>/docs/PLAN.md`（问题、对照、指标、停止规则、[studies/README.md](studies/README.md) §5 排班）。
- `python -m spec_mtp make studies/<name>`，再 `python -m spec_mtp launch studies/<name>`。
- `flow.prepare_shared: false`（RPipe make 下载只认 torchvision）。Run prepare 仍把 SpecBench 和权重写进 `shared/`。**不要写 `origin: foreign`**（[layout.md](docs/layout.md)）。权重用 ModelScope。
- `exact_match_rate` 必须是 1。表里的数是接受的 draft 数。速度和 `tau` 不决定结论。不把 γ 叫成 slope。
- 已有数字的格子不重跑。不复用一个 Run 目录。源码或输入变化用新的 algorithm.config.version；make/remake 不签收旧成功 Run。
- Study collect 从 execute 的原始观测计算指标，summarize 跑成功门，write 再核验，process 只终验当前 index。
- Windows：`PYTHONUTF8=1`，`D:\anaconda3\python.exe`，不另建 venv。
