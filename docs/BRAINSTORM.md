# BRAINSTORM

未拍板。这里只记下一步要做的事，不当实现合同。当前代码以 [ARCHITECTURE.md](ARCHITECTURE.md)、[CI.md](CI.md) 为准。已有数字在 [history_extrapolation](../studies/history_extrapolation/docs/STUDY_REPORT.md)。

## 1. 用 RPipe 重构这个仓库

**状态（2026-10-12）**：设计从“复制 RPipe、保留两套框架”改为“依赖 RPipe（`dev` 固定提交），保留 SpecMTP 专用实现”。`src/rpipe/` 与 `src/spec_mtp/` 里复制的框架已删除；SpecMTP 代码在 `src/spec_mtp/structure/<layer>/`，由 Study recipe 注册为 `spec_mtp` source。见 [LAYOUT.md](LAYOUT.md)、[ARCHITECTURE.md](ARCHITECTURE.md)。2026-10-09 的复制方案见提交 `b1f6191`。

仍待做：

- `sample_embedding` 初始化与采样共用 RNG，temperature > 0 时无法逐 token 审计（[ARCHITECTURE.md](ARCHITECTURE.md) 第 13 条）。`sample_embedding` 已在 `refactor/rpipe-dependency` 合入独立 Generator（[MASK_INIT_RNG.md](MASK_INIT_RNG.md)）；论文消融用 T=0，T>0 对齐只让 exact_match 更严。

- `configs/hf/` 已收成 [studies/paper_hf](../studies/paper_hf/README.md)（2026-10-12），只验证了展开和配置一致，GPU 未跑。已记录的接受数在 [history_extrapolation](../studies/history_extrapolation/docs/STUDY_REPORT.md)。

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
