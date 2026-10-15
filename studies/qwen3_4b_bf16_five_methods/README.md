# Qwen3-4B BF16五方法配对

[计划](docs/PLAN.md)已首次make冻结，11格串行链已启动；独立AR先运行，尚无全矩阵结论。前置[8B Table1全480报告](../esp_table1_bf16_full_argmax/docs/STUDY_REPORT.md)与原生process已完成，PR #10已经CI通过合dev；τ目标未复现，负结果保留。

在同一480条SpecBench上运行五方法×BC30/60加独立AR（共11 Run），统一双mask动态剪枝树/BF16/T0/256。owner映射、BF16原生验收回归及模型/输入来源核验已完成。原生source digest为538e52c929a542a8（56文件），代码8047281；2026-10-15 12:09 +08:00独立AR 0e25348a3a60d601进入execute，实际cuda BF16/tied-storage与480输入、权重SHA的首forward前检查全过。队列round1/单GPU，不使用旧FP32结果替代，不测速、不恢复算子机理。

配置和来源预检已完成：11格在原生RPipe展开检查中通过；4B 14文件与魔搭直接SHA256/历史检查点一致，480条4B tokenizer输入与前置Table1逐token一致。离线魔搭缓存已接入，缓存master revision身份无法确认的原始警告如实保留，内容SHA已核验。详见[模型来源](docs/modelscope-content-verification-v1.json)、[输入清单](docs/prompts_manifest.json)。无计时adapter在每Run首forward前核对冻结模型/输入，检查实际tied-storage；协议/恢复/CUDA loader及四phase导出回归通过。

配对阅读器`analyze_results.py`保留五方法全部两两对照、逐prompt接受/calls赢平输及AR首分叉。复用native证据/source/Study冻结门，仅全11格与process通过后生成正式证据；未完成格保持pending。运行和结论见[当前报告](docs/STUDY_REPORT.md)，CPU tiny/合成回归不代替真实4B。
