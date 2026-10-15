# Qwen3-4B BF16五方法配对

[计划](docs/PLAN.md)已写，尚未冻结、make或运行。前置[8B Table1全480报告](../esp_table1_bf16_full_argmax/docs/STUDY_REPORT.md)与原生process已完成，PR #10已经CI通过合dev；τ目标未复现，负结果保留。

拟在同一480条SpecBench上运行五方法×BC30/60加独立AR（共11 Run），统一双mask动态剪枝树/BF16/T0/256。先完成owner映射与BF16原生验收回归、模型/输入来源核验，再冻结并串行运行。当前没有4B BF16新结果；不使用旧FP32结果替代，不测速、不恢复算子机理。
