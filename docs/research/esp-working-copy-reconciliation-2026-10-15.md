# ESP 主仓工作副本证据对账

核对日期：2026-10-15。当前阶段实验已结束；本轮仅补齐主仓未提交的正式文档和证据，整理本机临时文件归档，不新增 GPU 执行或测速。

## 正式成果与 dev 的关系

核验基准为 `dev@be352f107d59d84a5b9cf70569b2b934163b5bd7`。主仓工作分支为 `feature/output-space-prerequisite`，旧提交未追踪本机后来生成的完整验收成果，因此会显示未提交/未追踪；这些成果已通过 [PR #10](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/10) 及后续报告 PR 集成进 dev，并非尚未完成的实验。

| 主题 | 正式文件 | 对账结果 |
| --- | --- | --- |
| 原生验收 | [BC60/2 revalidation](../../studies/esp_table1_bf16_full_argmax/docs/bc60-m2-native-revalidation-v1.json)、[Study process revalidation](../../studies/esp_table1_bf16_full_argmax/docs/native-process-revalidation-v1.json) | 与 dev 归一化换行后字节一致；仅补齐主仓分支提交。 |
| 完整 protocol | [protocol_evidence_v1.json](../../studies/esp_table1_bf16_full_argmax/docs/protocol_evidence_v1.json) | 与 dev 归一化换行后字节一致；四格完整，逐 prompt 计数与原始证据哈希通过核对。 |
| 图与绘图 | [tau_acceptance.png](../../studies/esp_table1_bf16_full_argmax/docs/figures/tau_acceptance.png)、[plot_results.py](../../studies/esp_table1_bf16_full_argmax/plot_results.py) | PNG 字节完全一致，绘图器归一化换行后字节一致；未重新绘制或改动结果。 |
| 报告与数字入口 | [STUDY_REPORT](../../studies/esp_table1_bf16_full_argmax/docs/STUDY_REPORT.md)、[NUMBERS](../../studies/esp_table1_bf16_full_argmax/docs/NUMBERS.md) | 保留 dev 最新报告及后补的原生数字链接，主仓同步该两份文档，避免以旧副本覆盖新内容。 |

正式证据、报告/图分主题提交，随后单独提交本对账与索引。重复内容只补齐执行副本的 Git 历史，不重复签收 Run，不改变 dev 已验收数值。主仓 `src/spec_mtp` 科学源码摘要仍为 `670c744e0535dcad`；未合入新的科学源码、未改冻结 PLAN、配方、模型或输入。原有 raw、argmax、source 和 native process 文件哈希检查通过；这些本机产物未重写。

## 本机归档，不作为正式结果

以下文件保留原位置和原字节，仅加入本仓库本机 `.git/info/exclude`，不加入公共 `.gitignore`，不上传原始 token 或个人 workspace。两个 pending 快照的 `all_cells_observed` 和 `quality_passed` 均为 false，不能将其当作当前完整验收；当前结果以上表正式文件为准。SHA 为本机原始文件字节的 SHA256。

| 本机保留路径（相对主仓） | 原始 SHA256 | 状态 |
| --- | --- | --- |
| `history_mtp.code-workspace` | `c5952e06bd5964770e0ec46e9c8c1ff58ab6509a5b0f99f2166db87af5a3fa2c` | 个人编辑器 workspace，未纳入公共仓库。 |
| `studies/esp_table1_bf16_full_argmax/docs/protocol_pending.json` | `e65c3aa67986b70b0eefd75dc89a98a7a41506d3463f29061035087e3a98d76f` | 早期未完成诊断快照，不作为当前结果。 |
| `studies/esp_table1_bf16_qwen_protocol/docs/protocol_pending.json` | `934c4f4eae8029dc26b676aa860878b379f1b23844dabc443b0d4b016780e411` | 早期未完成诊断快照，不作为当前结果。 |

本机 exclude 仅停止将这些已归档文件列为未追踪改动，未删除或移动文件。原主仓报告的修改前副本及核对清单另保留在本机 `.tmp/esp-worktree-reconciliation-20261015/`。本轮不删除分支、worktree、权重、缓存或实验数据，不强推、不合 main。
