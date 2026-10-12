# brainstorm

未拍板。不当实现合同。当前代码以 [architecture.md](architecture.md) 为准。已有数字在 [history-extrapolation.md](history-extrapolation.md)，不重跑。研究计划草案在 [research/readme.md](research/readme.md)。

## 输出层外推

现在的 `vhat` 是输入 embedding 的差分。下一次可以单开：用输出 embedding 当 `v`。这次不实现。

## 还没有跑的格子

- 输出层外推
- `vhat` 的 `1 − β^s` 校正
- Momentum Guidance
- 1.7B 上的 `γ` 扫描、`β = 0`、两层树
- 0.6B 全量 480
