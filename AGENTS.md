# SpecMTP Agent 工作约定

适用于本仓库及其子目录。本文件提供工作方式和文档入口。设计、数字和测试约定在 `docs/`。

## 1. 文档驱动的工作方式

1. 先从 [README.md](README.md) 和相关文档确认背景。按需阅读，不必每次通读整个项目。
2. 对照代码、测试和 [history_extrapolation](studies/history_extrapolation/docs/STUDY_REPORT.md) 里已经记下的数字。文档和实现不一致时，先核对原因，不把现状直接写成设计结论。
3. 涉及目录或分层的改动，先看 [LAYOUT.md](docs/LAYOUT.md)。`src/spec_mtp/` 是 RPipe 按文件拷过来的。新代码放进对应层的 `spec_mtp/` 子模块，不改拷过来的框架文件。解码在 `structure/algorithm/eval/spec_mtp/`，和 RPipe 的 `train/`、`eval/` 并列。
4. 按改动范围做必要验证，并同步相关文档。交付时说明完成内容、验证结果和未完成事项。

## 2. 去哪里找文档

| **需要了解的内容** | **入口** |
| --- | --- |
| 目录 | [LAYOUT.md](docs/LAYOUT.md) |
| 解码、mask、和论文不一致的地方 | [ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| 已经记下的接受数 | [history_extrapolation](studies/history_extrapolation/docs/STUDY_REPORT.md) |
| 怎么跑一个 Study | [studies/README.md](studies/README.md)，以及该 Study 的 `docs/PLAN.md` |
| 测试与 CI | [TESTING.md](docs/TESTING.md)、[CI.md](docs/CI.md) |
| 还没拍板的下一步 | [BRAINSTORM.md](docs/BRAINSTORM.md) |
| 论文 PDF | [papers/INDEX.md](docs/papers/INDEX.md)。PDF 不进 git |

[BRAINSTORM.md](docs/BRAINSTORM.md) 只记探索，不当实现合同。

## 3. 基本协作约定

- 修改前查看工作区状态，保留用户和其他任务的已有改动。
- 临时脚本和验证输出放 `.tmp/`。正式结果放 Study 的 `runs/<id>/` 或 `results/`。这两处和 `shared/`、`scripts/`、`index.json`、`process.json` 不进 git。
- 提交、推送、开实验，按当次授权。不直接推 `dev` 或 `main`。
- 只把长期约定放在这里。数字和阶段状态留在对应文档。

## 4. 代码放在哪

- `src/rpipe/` 是上游 RPipe，保持那一份。本机 Windows 需要在包入口先 import torch，这一处保留。不要把 SpecMTP 注册进 `rpipe`。
- `src/spec_mtp/` 跟随 RPipe：`flow/` 是 prepare → execute → collect → summarize → write → process；`structure/` 的各层与 RPipe 相同。
- SpecMTP 自己的文件只出现在某层下面的 `spec_mtp/` 子目录。mask、树、解码、esp / ar / alignment 在 `structure/algorithm/eval/spec_mtp/`。数据在 `structure/data/spec_mtp/`，模型在 `structure/model/spec_mtp/`。
- 入口是 `python -m spec_mtp`。不恢复 `src/main.py`。

## 5. 实验

- 开跑之前先写该 Study 的 `docs/PLAN.md`：问题、假设、对照、指标、停止规则。不在用来检验预注册结论的那一组上再调 β、λ、γ。
- 人从 Study 跑：`python -m spec_mtp make studies/<name>`，然后 `studies/<name>/scripts/launch.ps1`（bash 用同目录的 `launch.sh`）。`scripts/` 由 `make` 写出，不进 git。
- `exact_match_rate` 必须是 1，否则该格作废。表里的数是接受的 draft 数。速度和 `tau` 不决定结论。不把 γ 叫成 slope。
- [history_extrapolation](studies/history_extrapolation/docs/STUDY_REPORT.md) 里已经有数字的格子不重跑。不复用一个 Run 目录，logger 会追加。
- Windows 上设 `PYTHONUTF8=1`。权重用 ModelScope。用本机的 `D:\anaconda3\python.exe`，不另建 venv。
