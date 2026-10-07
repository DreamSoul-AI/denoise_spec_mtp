# STUDY_REPORT — history_extrapolation

记录日期：2026-10-06 至 2026-10-08。数字来自当时的 Run，不是这次重构新跑的。完整格子表在 [RESEARCH.md](../../../docs/RESEARCH.md)。

## 一、摘要

主指标是接受的 draft 数。float32 贪心各格都与普通生成逐 token 一致。

长记忆 gamma（均值加 gamma，γ = 1）在 4B 上高于冻结 prompt 均值：first 26 是 777 对 680，last 52 是 1723 对 1476。0.6B 和 1.7B 上，在 first 26 选出的那一对只回到冻结均值附近，没有同样的超出。4B 的 next 52 还没有这对参数的格子。冻结均值在每个已有对照上都不低于最后 token。

## 二、选出的一对对照冻结均值

β 和 λ 只在 first 26 上选。0.6B 用 β = 0.9999、λ = 0.1。1.7B 用 β = 0.999、λ = 0.1（780，高于 β = 0.9999 的 775）。4B 带到 last 52 的是 β = 0.9999、λ = 0.1。

| **模型** | **组** | **冻结均值** | **更新均值** | **均值加 gamma** |
| --- | --- | ---: | ---: | ---: |
| 0.6B | first 26 | 726 | 701 | 723 |
| 0.6B | next 52 | 1550 | 1473 | 1553 |
| 0.6B | last 52 | 1598 | 1468 | 1575 |
| 1.7B | first 26 | 778 | 757 | 780 |
| 1.7B | next 52 | 1747 | 1639 | 1709 |
| 1.7B | last 52 | 1723 | 1626 | 1719 |
| 4B | first 26 | 680 | 704 | 777 |
| 4B | next 52 | 1462 | 1479 | 1686 |
| 4B | last 52 | 1476 | 1525 | 1723 |

4B 的 next 52 均值加 gamma 是 2026-10-08 的确认格，run `9d48dc5a82624d1a`，见 [history_4b_next52_confirm](../../history_4b_next52_confirm/docs/STUDY_REPORT.md)。冻结均值、最后 token、更新均值仍是原先记下的 1462、1323、1479，没有重跑。

## 三、从扫描里读到的

1. 冻结 prompt 均值在每个模型、每个已有组上都不少于最后 token。
2. gamma 加在最后 token 上（β = 0.9，γ = 1）停在最后 token 的接受数附近。只保留方向的那一格没有更高。
3. gamma 加在更新均值上取决于 β。β = 0.5 少于更新均值。β = 0.999 或 0.9999 更多。λ 的扫描没有把这个方向反过来。
4. 更新均值相对冻结均值的符号，在 4B 上略高，在 0.6B 和 1.7B 上更低。

β 扫描和 λ 扫描的逐格表在 [RESEARCH.md](../../../docs/RESEARCH.md)。

## 四、本机结果目录

这些目录被 gitignore，clone 里没有。

- 4B last-52 冻结均值和最后 token：`results/qwen3_4b_last52_20261008/`
- 0.6B 和 1.7B：`results/sweep_20261007/`，另有 `results/try_qwen3_0_6b_20261007/`、`results/try_qwen3_1_7b_20261007/`
- 切片：`results/slices_20261007/`，由 `scripts/make_dev_slice.py` 按 skip/take `0/2`、`2/4`、`6/4` 写出

当时的入口是 `src/main.py` 加 `configs/hf/qwen3_8b/run_0/ema_bc30.yaml` 或 `esp_bc30.yaml`，`model.torch_dtype=float32`。现在同一因素用 `algorithm.config.mask`，见 [PLAN.md](PLAN.md)。
