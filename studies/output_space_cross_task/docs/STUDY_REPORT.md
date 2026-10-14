# Cross-task Study status and falsification implementation

2026-10-14. This Study remains unexecuted on real prompts. q241–244 have fixed summarization inputs and tokenizer hashes only. There are no native Run IDs, accepted numbers, model speed results or real H1/H3 verdicts.

The [checker protocol](CHECKER_PROTOCOL.md) and [executable checker](../check_hypotheses.py) implement native evidence export, source/input/raw/AR completeness gates, fixed window freezing and H1/H3 decisions. The synthetic minimal reproduction and boundary tests verify decision logic only. H1 distinguishes bounded rejection from infeasible-window uncertainty; equal counts can still have semantic changes. H3 excludes wrong-first/EOS/missing-second cases; a missing witness does not confirm a global explanation. H2 canonical mediation remains untested. The checker is included in future source provenance; current draft-only artifacts are not re-signed as measurements.

The related [fixed q_proj execution addendum](KERNEL_EXECUTION_PLAN.md) was executed locally on old q178, separately from this cross-task Study. Its [actual results](../../output_space_extension/docs/STUDY_REPORT.md) show effective linear microdelta substitutions and unchanged acceptance paths. That does not count as cross-task replication.

Follow-up questions, in execution order: complete a freshly frozen q241–244 native+fixed-window batch; select the first accepted-changing feasible unit for a separately declared canonical self/graft protocol; retain all nulls and infeasible units; decide whether an effective entry Phi rounding contrast is needed on q178. No new default, remote push/PR or data deletion.

判定脚本15项边界检查包含直接验证baseline／placebo实际trace，质量标志为true但trace不一致也拒绝；本轮整体28项相关检查、Ruff/mypy56通过。这些是实现验证，不是q241–244模型验收。
