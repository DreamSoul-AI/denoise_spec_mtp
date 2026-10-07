# PLAN — history_4b_next52_confirm

未跑。这一轮只加一个格子，用来确认已经选出的参数，不在这组 prompt 上重新选 β 或 λ。

## 一、问题

Qwen3-4B 上，β = 0.9999、λ = 0.1、γ = 1 的均值加 gamma，在 first 26 接受 777，冻结均值是 680。同一对在 last 52 接受 1723，冻结均值是 1476。next 52 没有用来选参，冻结均值已经记下是 1462。

这一个未跑的格子上，接受数是否仍高于 1462。

## 二、假设

在 next 52 上，均值加 gamma 的接受数大于已记录的冻结均值 1462。

若接受数小于或等于 1462，last 52 上的超出没有在这组上重复。到此停止，不改 β、不改 λ、不把三组合在一起再排一次。

## 三、对照

对照不新跑。next 52 上已经记下的是：

| **设定** | **接受数** | **来源** |
| --- | ---: | --- |
| 冻结 prompt 均值 | 1462 | [history_extrapolation](../../history_extrapolation/docs/STUDY_REPORT.md) |
| 最后 token | 1323 | 同上 |
| 更新中的均值 | 1479 | 同上 |

主对照是冻结均值 1462。更新均值 1479 只作旁注，不单独做判定。

## 四、这一格

| **项** | **取值** |
| --- | --- |
| 模型 | Qwen/Qwen3-4B，float32 |
| 数据 | SpecBench，每类 skip 2、take 4（52 条） |
| mask | `mean_plus_gamma` |
| β / λ / γ | 0.9999 / 0.1 / 1 |
| 树 | `[14]`，一个槽 |
| 解码 | 贪心，temperature 0，最多 100 个新 token，seed 123，thinking 关 |
| 种子 | 123，只这一次 |

声明在同目录 `study.yaml`。跑的时候：

```text
set PYTHONUTF8=1
python -m rpipe run studies/history_4b_next52_confirm
```

需要本机已有 SpecBench 的 `question.jsonl` 和 Qwen3-4B 权重。结果写到该 Study 的 `runs/<id>/`，目录不进 git。

## 五、指标和判定

1. `exact_match_rate` 必须是 1。否则这格无效，不和 1462 比。
2. 主指标是 overall 的接受数，等于 `accept_d1`（树深只有一层）。
3. 大于 1462：4B 上的超出在未参与选参的 next 52 上仍在。
4. 小于或等于 1462：超出没有在这组上重复。不换参数重试。

速度不参与判定。

## 六、刻意不做

不重跑 1462、1323、1479。不扫 β、λ、γ。不跑 480 条，不加深树，不做输出层外推，不改 `vhat` 的偏差校正。
