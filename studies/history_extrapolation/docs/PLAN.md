# PLAN — history_extrapolation

这份计划是事后整理，对应 2026-10-06 至 2026-10-08 已经跑完的格子。它不展开成新的 `rpipe run`。逐格数字见 [STUDY_REPORT.md](STUDY_REPORT.md) 和 [RESEARCH.md](../../../docs/RESEARCH.md)。

## 1. 问题

在 Qwen3 的输入 embedding 上，mask 写成

```text
m = origin + γ · vhat
```

时，长记忆的 `vhat`（大 β）加在更新中的 prompt 均值上，接受的 draft 是否多于冻结的 prompt 均值。树只有一个槽，所以 `i = 1`。

## 2. 固定条件

float32，贪心，temperature 0，最多 100 个新 token，seed 123，Qwen3 thinking 关闭。树 `[14]`，一个 mask 槽，block complexity 30。SpecBench 按类别排序，类别内保持文件顺序。

| **组** | **skip / take（每类）** | **条数** |
| --- | --- | ---: |
| first | 0 / 2 | 26 |
| next | 2 / 4 | 52 |
| last | 6 / 4 | 52 |

β 和 λ 只在 first 26 上选。52 条的两组不参与选参。

## 3. 因素

代码里的名字在 `spec_mtp.rpipe.mask_settings`。

| **设定** | **mask** | **β** | **λ** | **γ** |
| --- | --- | ---: | ---: | ---: |
| 冻结 prompt 均值 | `frozen_mean` | off | 0 | 0 |
| 最后 token | `last_token` | off | off | 0 |
| 更新中的均值 | `updating_mean` | off | 0.1 | 0 |
| gamma 加在最后 token | `gamma_last` | 0.9 | off | 1 |
| 只保留方向，加在最后 token | `gamma_last_unit` | 0.9 | off | 1 |
| 均值加 gamma | `mean_plus_gamma` | 扫描 | 扫描 | 1 |

`off` 表示该项不在 mask 里。β = 0，以及 0 和 1 以外的 γ，没有跑。

## 4. 指标

主指标是接受的 draft 数。同一模型、同一组 prompt 上，各行提交的 token 相同。float32 贪心必须与普通生成逐 token 一致；这是完整性检查，不是质量指标。

## 5. 刻意不做

不把这批格子重新跑一遍。输出层外推、更深的树、全量 480 条，都不在这个 Study 里。
