# BRAINSTORM

未拍板。这里只记下一步要做的事，不当实现合同。当前代码和已有数字以 [ARCHITECTURE.md](ARCHITECTURE.md)、[RESEARCH.md](RESEARCH.md)、[CI.md](CI.md) 为准。

## 1. 用 RPipe 重构这个仓库

**状态（2026-10-08，`refactor/spec-rpipe`）**：已 vendor `src/rpipe`，研究代码迁到 `src/spec_mtp/`，`eval` + `source: spec_mtp` 注册完成。CPU 门改为 `studies/smoke_tiny_llama`（`python -m rpipe run`），仍经 `scripts/run_ci_checks.py`，见 [CI.md](CI.md)、[TESTING.md](TESTING.md)。`spec_metrics.csv` / `summary.csv` 写在 Run `assets/`；汇总指标进 tracker。`configs/smoke/` + `src/main.py` 保留作对照。

仍待做（不在本段实现合同里）：

- `configs/hf/` 与 `scripts/run_*.sh` 收成 Study 声明（history-extrapolation 等）。
- 可选：收紧 `tests/rpipe/` 进 CI，或只保留 spec_mtp 脚本门。
- PR 合入 `dev` 后删 `refactor/spec-rpipe`。

## 2. 在输出层做外推

现在的 `vhat` 是输入 embedding 的差分。mask 直接拼进 `inputs_embeds`，不投影回词表。模型只在 logits 上取 token。输入空间的差值对不上词表里的一步。

下一次可以单开的方向：用模型输出 embedding 作为 `v`，在输出层外推，再用 argmax，或用加权平均，在词表里取一个 token。这次不实现，也不改现有 mask。

## 3. 还没有跑的格子

不在 RPipe 重构里顺手开这些实验：

- SpecBench 全量 480 条
- 更深的树，以及 `i` 不是 1
- `vhat` 的 `1 − β^s` 校正
- Momentum Guidance。它放大的是当前速度相对历史的偏差，和这里沿 `vhat` 往前走不是同一个对象
- `β = 0`，以及 0 和 1 以外的 `γ`
- 4B 中间那组 52 条上的长记忆 gamma。这组已有冻结均值 1462、最后 token 1323、更新均值 1479，没有 `β = 0.9999` 的 mean-plus-gamma

## 4. 这次已经收好的文档

2026-10-08：`notes/` 和 `docs/research/history_mtp/` 收成 ARCHITECTURE / RESEARCH / CI。论文 PDF 在 `docs/papers/`，不进 git，索引是 [papers/INDEX.md](papers/INDEX.md)。
