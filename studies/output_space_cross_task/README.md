# Output-space cross-task falsification

Status: four real native Runs/16 outputs and 20 fixed-window diagnostics completed, all AR-identical. Separate first-unit q241 canonical follow-up completed. Original draft PLAN history is retained; activation is in docs/EXECUTION_PLAN.md.

[PLAN](<../../docs/研究计划 Denoising Speculative Decoding.md#legacy-studies-output-space-cross-task-docs-plan>) defines falsifiable hypotheses, fixed native/transfer cells and stopping rules. [Kernel isolation protocol](<../../docs/研究计划 Denoising Speculative Decoding.md#legacy-studies-output-space-cross-task-docs-kernel-plan>) preserves the initial protocol; its fixed-row q_proj execution and the subsequent entry Phi/RMSNorm controls are recorded in the extension report. [Input manifest](docs/prompts_manifest.json) and ModelScope snapshot bind the executed inputs. Reuse current recipe and phase exports; scientific defaults and previous Studies are untouched.

The local q178 operator results are in [the extension report](../output_space_extension/docs/STUDY_REPORT.md). The twelve development prompts do not establish cross-task generality.

[证伪脚本](check_hypotheses.py)与[检查协议](docs/CHECKER_PROTOCOL.md)已提供可跑export/check/mre流程，现已完成真实批次和独立canonical跟进。[状态报告](docs/STUDY_REPORT.md)保存实际Run、正负结果与范围。固定q_proj协议已通过[执行增补](<../../docs/研究计划 Denoising Speculative Decoding.md#legacy-studies-output-space-cross-task-docs-kernel-execution-plan>)在旧q178上完成，不混作新任务证据。

真实输入／零／一汇总85/58/45；q241 native11→12，canonical14→14且路径仍不同。完整事实与图见[STUDY_REPORT](docs/STUDY_REPORT.md)，计数对比不代替语义轨迹或纯因果证明。

2026-10-15：新冻结STATE_FACTOR_PLAN完成六生成与H5/H6反例，anchor-only/velocity-only13／13，双canonical等数但路径不同的root720归因见[最新报告](docs/STUDY_REPORT.md)。

新固定帧对照在source719分离即时state与代理，并新增q242/q243两greedy seed因素矩阵；q242零交互、q243非零，root720当前映射与候选构建时序见[最新报告](docs/STUDY_REPORT.md)。

非T0两完整采样路径独立AR一致，移植效果-1/+1；原source719条件随机验证恢复，另一owner1候选改变但未恢复命中。新协议、概率数值口径和回归见[最新报告](docs/STUDY_REPORT.md)。

完整4prompt×3seed含旧2、新10，6增6减；rare4096draw仍零但功效不足。报告更新后继续H7得到首变负、最终正的两新反例，见[最新报告](docs/STUDY_REPORT.md)。

新扩展六单位补q245/246及seed126/127，q242/244既有方向均在新seed反转；另冻T=2条件压力测试见实际罕见命中2/7，原温度16384次仍零且功效不足。报告写回后继续H10，34共有捕获窗口未出现合法depth2翻转。完整证据、首命中seed、边界与下一项固定帧问题见[最新报告](docs/STUDY_REPORT.md)。
