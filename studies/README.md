# Studies

RPipe 里一次研究是一个目录：`study.yaml` 声明因素，`docs/PLAN.md` 写问题和判定，`docs/STUDY_REPORT.md` 写结果。`runs/` 不进 git。

| **Study** | **状态** | **问题** |
| --- | --- | --- |
| [smoke_tiny_llama](smoke_tiny_llama/docs/PLAN.md) | 已跑，CPU 门 | 随机 tiny LLaMA 上三种 mask 是否与普通生成逐 token 一致 |
| [history_extrapolation](history_extrapolation/docs/STUDY_REPORT.md) | 已跑，数字在报告里 | 输入 embedding 上，长记忆 gamma 比冻结均值多接受多少 draft |
| [history_4b_next52_confirm](history_4b_next52_confirm/docs/STUDY_REPORT.md) | 2026-10-08 已跑 | next 52 上均值加 gamma 接受 1686，高于已记录的冻结均值 1462 |
| [history_4b_gamma_screen](history_4b_gamma_screen/docs/STUDY_REPORT.md) | 2026-10-08 已停 | first 26 上 γ=0.25/0.5/2/4 的接受数都不超过已记录的 777 |
| [history_4b_beta0](history_4b_beta0/docs/STUDY_REPORT.md) | 2026-10-08 已跑 | first 26 上 β=0 接受 622，不低于已记录的 β=0.5（620） |
| [history_4b_full480](history_4b_full480/docs/STUDY_REPORT.md) | 2026-10-08 已跑 | 全量 480 条上，均值加 gamma 接受 15009，冻结均值 12809 |
| [history_4b_depth2](history_4b_depth2/docs/STUDY_REPORT.md) | 2026-10-08 已跑 | 树 `[7, 2]` 上接受总数 704 对 621；第二层冻结均值更高 |

历史格子的逐格接受数在 [RESEARCH.md](../docs/RESEARCH.md)。确认 Study 不重跑那些格子。
