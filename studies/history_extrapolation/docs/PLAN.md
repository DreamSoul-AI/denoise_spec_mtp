# PLAN — history_extrapolation

记录在前，这一问已经有结论。没有 `study.yaml`。不重跑。

## 一、问题

在固定的 SpecBench 切片上，长记忆的 mean-plus-gamma 接受的 draft，是否多于冻结的 prompt mean。γ 是步长系数，不是斜率。

## 二、判定

1. `exact_match_rate` 必须是 1，否则该格作废。
2. 主指标是接受的 draft 数。一层树用 `accept_d1`。树 `[7, 2]` 用 `accept_d1 + accept_d2`。速度和 `tau` 不参与判定。
3. β、λ 只在 first 26 上选取。52 条和全量 480 只用来确认，不回头改 β、λ、γ。

## 三、固定

Qwen3，float32，greedy，temperature 0，最多 100 个新 token，seed 123，thinking 关。一层树是 `[14]`，一个 mask 槽。切片按类别内文件顺序：first 26、next 52、last 52。

## 四、刻意不做

去偏 `vhat`、Momentum Guidance、以及除已记录两层树以外的 `i`。已有数字的格子不重跑。
