# Output-space cross-task falsification draft

Status: DRAFT, not made or launched. Four fixed summarization prompts q241–q244, chosen before new outputs; independent tokenizer preflight only. No accepted counts or success claims exist for this Study.

[PLAN](docs/PLAN.md) defines falsifiable hypotheses, fixed native/transfer cells and stopping rules. [Kernel isolation protocol](docs/KERNEL_PLAN.md) separates an unexecuted transformer proxy experiment from the executed q178 provider controls. [Input manifest](docs/prompts_manifest.json) and ModelScope snapshot bind the draft inputs. Reuse current recipe and phase exports; scientific defaults and previous Studies are untouched.

The local q178 operator results are in [the extension report](../output_space_extension/docs/STUDY_REPORT.md). The twelve development prompts do not establish cross-task generality.

[证伪脚本](check_hypotheses.py)与[检查协议](docs/CHECKER_PROTOCOL.md)已提供可跑export/check/mre流程，当前只执行合成逻辑测试。[状态报告](docs/STUDY_REPORT.md)明确无真实q241–244 Run。固定q_proj协议已通过[执行增补](docs/KERNEL_EXECUTION_PLAN.md)在旧q178上完成，不混作新任务证据。
