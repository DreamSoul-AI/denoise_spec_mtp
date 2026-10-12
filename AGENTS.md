# SpecMTP Agent 工作约定

适用于本仓库及其子目录。本文件提供工作方式和文档入口。设计、数字和测试约定在 `docs/`。

## 1. 文档驱动的工作方式

1. 先从 [README.md](README.md) 和相关文档确认背景。按需阅读，不必每次通读整个项目。
2. 对照代码、测试和 [history_extrapolation](studies/history_extrapolation/docs/STUDY_REPORT.md) 里已经记下的数字。文档和实现不一致时，先核对原因，不把现状直接写成设计结论。
3. 涉及目录或分层的改动，先看 [LAYOUT.md](docs/LAYOUT.md)。本项目**依赖** RPipe（固定提交见 [LAYOUT.md](docs/LAYOUT.md)），不再复制 RPipe。`src/spec_mtp/` 只放 SpecMTP 专用实现，经 Study recipe 注册到 RPipe 运行时 Registry。不改上游 RPipe 源码；确需改 RPipe 公共接口时先说明缺口和跨仓库影响，再请求授权。
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
| 结构改动的开发记录 | [RECORD.md](docs/RECORD.md) |
| RPipe 的 Study / Flow 合同 | RPipe 仓库 `studies/README.md`、`docs/code/flow.md` §14（按 `pyproject.toml` 固定的提交读） |
| 论文 PDF | [papers/INDEX.md](docs/papers/INDEX.md)。PDF 不进 git |

[BRAINSTORM.md](docs/BRAINSTORM.md) 只记探索，不当实现合同。

## 3. 基本协作约定

- 修改前查看工作区状态，保留用户和其他任务的已有改动。
- 临时脚本和验证输出放 `.tmp/`。正式结果放 Study 的 `runs/<id>/` 或 `results/`。这两处和 `shared/`、`scripts/`、`index.json`、`process.json` 不进 git。
- 提交、推送、开实验，按当次授权。不直接推 `dev` 或 `main`。
- 只把长期约定放在这里。数字和阶段状态留在对应文档。

## 4. 代码放在哪

- RPipe 是外部依赖（`pyproject.toml` 固定 `diaoenmao/RPipe` 的 `dev` 提交）。调度、Flow 阶段链、FlowContext、Tracker、Logger、result、provenance / freeze、聚合与 readout 都用库里的，不在本仓库复制，也不通过换包名复制 runner、Factory、Registry、artifact、make。
- `src/spec_mtp/` 是 SpecMTP 专用代码，按 RPipe 的 `structure` 分层命名：`structure/algorithm/`（mask、树、解码、esp / ar / alignment，注册为 `(eval, spec_mtp)`）、`structure/data/`、`structure/model/`、`structure/system/`、`structure/control/`、`structure/artifact/`。`spec_mtp/recipe.py` 做注册和构造条件校验；`spec_mtp/flow/` 只放 Study 阶段会调用的 SpecMTP 专用检查。
- 注册只发生在 Study 的 `recipe.register(ctx)` 里，导入 `spec_mtp` 不注册、不计算。不改 RPipe 默认 source。
- 入口：`python -m rpipe …` 是主入口。`python -m spec_mtp` / `spec-mtp` 是薄入口：在 make / run 时额外写 SpecMTP 源码清单，其余原样转给 `rpipe`。本项目安装不提供 `rpipe` 命令，不覆盖真正的 RPipe。
- Windows：`spec_mtp/__init__.py` 保留“先 import torch”的适配（原因见该文件注释）；只在经 `spec_mtp` 入口时先于 RPipe 生效。Linux 上无法验证，不要据此删除。不恢复 `src/main.py`。

## 5. 实验

- 开跑之前先写该 Study 的 `docs/PLAN.md`：问题、假设、对照、指标、停止规则。不在用来检验预注册结论的那一组上再调 β、λ、γ。
- 人从 Study 跑：`python -m spec_mtp make studies/<name>`（等价于 `rpipe make` 加 SpecMTP 源码清单），然后 `studies/<name>/scripts/launch.ps1`（bash 用同目录的 `launch.sh`）。`scripts/` 由 `make` 写出，不进 git。
- 每个 Study 用 `recipe: recipe.py` 注册 SpecMTP source，`flow.prepare_shared: false`。`exact_match_rate` 门在 write 定稿前执行，不为 1 的 Run 记为 failed。
- `exact_match_rate` 必须是 1，否则该格作废。表里的数是接受的 draft 数。速度和 `tau` 不决定结论。不把 γ 叫成 slope。
- [history_extrapolation](studies/history_extrapolation/docs/STUDY_REPORT.md) 里已经有数字的格子不重跑。不复用一个 Run 目录，logger 会追加。
- Windows 上设 `PYTHONUTF8=1`。权重用 ModelScope。用本机的 `D:\anaconda3\python.exe`，不另建 venv。
