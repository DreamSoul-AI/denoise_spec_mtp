# Output-space cross-task falsification

Status: four real native Runs/16 outputs and 20 fixed-window diagnostics completed, all AR-identical. Separate first-unit q241 canonical follow-up completed. Original draft PLAN history is retained; activation is in docs/EXECUTION_PLAN.md.

[PLAN](docs/PLAN.md) defines falsifiable hypotheses, fixed native/transfer cells and stopping rules. [Kernel isolation protocol](docs/KERNEL_PLAN.md) preserves the initial protocol; its fixed-row q_proj execution and the subsequent entry Phi/RMSNorm controls are recorded in the extension report. [Input manifest](docs/prompts_manifest.json) and ModelScope snapshot bind the executed inputs. Reuse current recipe and phase exports; scientific defaults and previous Studies are untouched.

The local q178 operator results are in [the extension report](../output_space_extension/docs/STUDY_REPORT.md). The twelve development prompts do not establish cross-task generality.

[证伪脚本](check_hypotheses.py)与[检查协议](docs/CHECKER_PROTOCOL.md)已提供可跑export/check/mre流程，现已完成真实批次和独立canonical跟进。[状态报告](docs/STUDY_REPORT.md)保存实际Run、正负结果与范围。固定q_proj协议已通过[执行增补](docs/KERNEL_EXECUTION_PLAN.md)在旧q178上完成，不混作新任务证据。

真实输入／零／一汇总85/58/45；q241 native11→12，canonical14→14且路径仍不同。完整事实与图见[STUDY_REPORT](docs/STUDY_REPORT.md)，计数对比不代替语义轨迹或纯因果证明。

2026-10-15：新冻结STATE_FACTOR_PLAN完成六生成与H5/H6反例，anchor-only/velocity-only13／13，双canonical等数但路径不同的root720归因见[最新报告](docs/STUDY_REPORT.md)。

新固定帧对照在source719分离即时state与代理，并新增q242/q243两greedy seed因素矩阵；q242零交互、q243非零，root720当前映射与候选构建时序见[最新报告](docs/STUDY_REPORT.md)。

非T0两完整采样路径独立AR一致，移植效果-1/+1；原source719条件随机验证恢复，另一owner1候选改变但未恢复命中。新协议、概率数值口径和回归见[最新报告](docs/STUDY_REPORT.md)。
