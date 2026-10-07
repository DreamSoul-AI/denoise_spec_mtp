# STUDY_REPORT — history_4b_next52_confirm

2026-10-08 跑完。本机 NVIDIA GeForce RTX 5090 D（24GB），float32，权重来自 ModelScope `Qwen/Qwen3-4B`。`exact_match_rate` 为 1，这格有效。

## 判定

假设是接受数大于已记录的冻结均值 1462。实测 overall `accept_d1` 为 **1686**。假设成立：4B 上、在没有参与选 β 和 λ 的 next 52 上，均值加 gamma 仍然更高。

不改 β，不改 λ，不把这组拿去重选参数。

| **设定** | **接受数** | **exact_match_rate** | **run_id** |
| --- | ---: | ---: | --- |
| 冻结均值（已记录，未重跑） | 1462 | 1 | 见 history_extrapolation |
| 均值加 gamma，β=0.9999，λ=0.1，γ=1 | 1686 | 1 | `9d48dc5a82624d1a` |

差值是 1686 − 1462 = 224。同一对参数在 first 26 是 777 对 680，在 last 52 是 1723 对 1476。三组方向一致。

产物在 `studies/history_4b_next52_confirm/runs/9d48dc5a82624d1a/`，不进 git。overall 行：52 条，`tau` 1.5635，`attempt_d1` 2960。速度不参与判定。
