# BRAINSTORM

未拍板。这里只记下一步要做的事，不当实现合同。当前代码和已有数字以 [architecture.md](architecture.md)、[research.md](research.md)、[ci.md](ci.md) 为准。

## 1. 用 RPipe 重构这个仓库

整仓重构对齐 [RPipe](https://github.com/diaoenmao/RPipe)，在 `feature/rpipe-refactor` 上进行。该分支从 `dev` 拉出，`main` 仍停在复现基线。量化仓库 `DreamSoul-AI/quantization` 已经按这套模板拆过：`src/rpipe` 是执行层，研究代码单独放，一轮实验是 `studies/<name>/` 里的 Study、Experiment、Run。

重构时要保住的行为：

- ESP 与 EMA-velocity 的 mask、树、验证不变。float32 贪心必须仍和普通生成逐 token 一致。
- CPU 门留着：`tests/check_correctness.py`、`tests/check_ema_history.py`、tiny-LLaMA smoke。入口现在是 `scripts/run_ci_checks.py`，见 [ci.md](ci.md)。
- [research.md](research.md) 里的接受数不重跑，也不改口径。

重构前要先定、现在不定的事：

- `configs/hf/` 和 `scripts/run_*.sh` 怎么收成 Study 的因素声明。
- 现在的 `spec_metrics.csv` / `summary.csv` 怎么落到 RPipe 的 Run result。
- `rpipe` 是安装依赖，还是像量化仓库那样把源码放进本仓库。
- CI 是换成 RPipe 的测试入口，还是先保留现在这条 CPU 工作流。

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

2026-10-08：`notes/` 和 `docs/research/history_mtp/` 收成上面三份文档。论文 PDF 在 `docs/papers/`，不进 git，索引是 [papers/README.md](papers/README.md)。
