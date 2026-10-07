# STUDY_REPORT — history_4b_full480

2026-10-08 跑完。两格 `exact_match_rate` 都是 1。假设成立：全量 480 条上，均值加 gamma 的接受数高于冻结均值。

| **设定** | **接受数** | **exact_match_rate** | **run_id** |
| --- | ---: | ---: | --- |
| 冻结均值 | 12809 | 1 | `5035d03aed9c28c0` |
| 均值加 gamma，β=0.9999，λ=0.1，γ=1 | 15009 | 1 | `2645ebe241330750` |

差值是 15009 − 12809 = 2200。两格的 `new_tokens_per_prompt` 都是 84.7625。不改 β、λ、γ。

产物在 `studies/history_4b_full480/runs/`，不进 git。
