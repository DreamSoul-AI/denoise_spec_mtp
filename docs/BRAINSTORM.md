# BRAINSTORM

未拍板。这里只记下一步要做的事，不当实现合同。当前代码以 [ARCHITECTURE.md](ARCHITECTURE.md)、[CI.md](CI.md) 为准。已有数字在 [history_extrapolation](../studies/history_extrapolation/docs/STUDY_REPORT.md)。

## 1. 用 RPipe 重构这个仓库

**状态（2026-10-09）**：`src/spec_mtp/` 是 RPipe 按文件拷过来的，包名换成 `spec_mtp`。SpecMTP 的代码在各层的 `spec_mtp/` 子模块里。解码在 `structure/algorithm/eval/spec_mtp/`，和 RPipe 的 `train/`、`eval/` 并列，注册为 `(eval, spec_mtp)`。`src/rpipe/` 保持上游那份，不往里面注册。CPU 门是 `studies/smoke_tiny_llama`，人跑 `studies/<name>/scripts/launch.ps1`，CI 用 `python -m spec_mtp run`。见 [LAYOUT.md](LAYOUT.md)、[CI.md](CI.md)、[TESTING.md](TESTING.md)。

仍待做：

- `configs/hf/` 里 ESP 论文复现扫描还没收成 Study。已记录的接受数在 [history_extrapolation](../studies/history_extrapolation/docs/STUDY_REPORT.md)。下一轮从 `_template` 复制。

## 2. 在输出层做外推

现在的 `vhat` 是输入 embedding 的差分。mask 直接拼进 `inputs_embeds`，不投影回词表。模型只在 logits 上取 token。输入空间的差值对不上词表里的一步。

下一次可以单开的方向：用模型输出 embedding 作为 `v`，在输出层外推，再用 argmax，或用加权平均，在词表里取一个 token。这次不实现，也不改现有 mask。

## 3. 还没有跑的格子

不在结构改动里顺手开这些实验。已经有数字的格子在 [history_extrapolation](../studies/history_extrapolation/docs/STUDY_REPORT.md)，不重跑。

还没跑：

- 输出层外推（见上一节）
- `vhat` 的 `1 − β^s` 校正
- Momentum Guidance。它放大的是当前速度相对历史的偏差，和这里沿 `vhat` 往前走不是同一个对象
- 1.7B 上的 `γ` 扫描、`β = 0`、两层树。0.6B 和 4B 上这几格已经有记录
- 0.6B 全量 480。4B 全量已经有记录

已经跑过、数字留在 [history_extrapolation](../studies/history_extrapolation/docs/STUDY_REPORT.md) 里的，包括 4B / 0.6B 的 `γ` 扫描、`β = 0`、两层树 `[7, 2]`，以及 4B 全量 480 和 next-52 长记忆 gamma。

## 4. 这次已经收好的文档

2026-10-08：`notes/` 和 `docs/research/history_mtp/` 收成 ARCHITECTURE / CI，实验记录进 Study。论文 PDF 在 `docs/papers/`，不进 git，索引是 [papers/INDEX.md](papers/INDEX.md)。
