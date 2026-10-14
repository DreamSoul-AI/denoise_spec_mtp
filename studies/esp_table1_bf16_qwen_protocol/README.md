# ESP Table 1 corrected Qwen3 preflight

[PLAN](docs/PLAN.md): BC60/1 primary (29 nodes), BC60/2 control (19 nodes). One new Run fills the missing primary; three frozen earlier cells are reused. Both BC60 results and target deltas are always reported. BF16/T0/256/seed123/updating mean, no speed tests.

## 当前研究验收与后续入口

本预检已结束，代码/测试与结果已分别提交推送为ca7749e、b052636。冻结PLAN及历史native状态保留；其中独立AR失配只作报告指标，不构成当前数学正确性失败判定。该预检没有验证前向argmax审计，不能补造或冒充全覆盖自检。

当前执行入口为[全480 verifier argmax审计](../esp_table1_bf16_full_argmax/README.md)：主配置10/1、30/1、60/1，对照60/2，BF16/T0/默认设置、λ=.1 updating mean、dynamic+pruning。全部提交token等于对应验证前向logits argmax必须全过；三种τ和目标差值、AR一致率及首分叉分别报告。永久停止本条BF16相对AR的算子机理链；全480结束后继续4B BF16五方法加AR配对，不测速。
