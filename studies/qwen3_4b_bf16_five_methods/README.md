# Qwen3-4B BF16五方法配对

[计划](docs/PLAN.md)已首次make冻结，11格串行链运行中；独立AR与BC30五方法各480条均已原生成功，五Spec格全部提交token的argmax审计全过，两种输出方法的owner/观测路径/实际BF16 mask范数验收也通过。当前6/11：BC30输入一阶总accepted最高、主calls最少；输出一阶相对输出零阶accepted+191但calls+139、输出总长+332，接受数W/T/L=209/72/199、调用数201/64/215，未显示稳定联合收益。BC60 frozen mean已接续，完整两预算结论仍待完成。独立AR差异及输出长度单列诊断，不阻止验收，也不作同输出测速结论。前置[8B Table1全480报告](../esp_table1_bf16_full_argmax/docs/STUDY_REPORT.md)与原生process已完成，PR #10已经CI通过合dev；τ目标未复现，负结果保留。

在同一480条SpecBench上运行五方法×BC30/60加独立AR（共11 Run），统一双mask动态剪枝树/BF16/T0/256。owner映射、BF16原生验收回归及模型/输入来源核验已完成。原生source digest为538e52c929a542a8（56文件），代码8047281；2026-10-15 12:09 +08:00独立AR 0e25348a3a60d601进入execute，实际cuda BF16/tied-storage与480输入、权重SHA的首forward前检查全过。队列round1/单GPU，不使用旧FP32结果替代，不测速、不恢复算子机理。

配置和来源预检已完成：11格在原生RPipe展开检查中通过；4B 14文件与魔搭直接SHA256/历史检查点一致，480条4B tokenizer输入与前置Table1逐token一致。离线魔搭缓存已接入，缓存master revision身份无法确认的原始警告如实保留，内容SHA已核验。详见[模型来源](docs/modelscope-content-verification-v1.json)、[输入清单](docs/prompts_manifest.json)。无计时adapter在每Run首forward前核对冻结模型/输入，检查实际tied-storage；协议/恢复/CUDA loader及四phase导出回归通过。

配对阅读器`analyze_results.py`保留五方法全部两两对照、逐prompt接受/calls赢平输及AR首分叉，另显式列出每个方法相对同一独立AR的调用数赢平输、Δcalls和两侧输出长度。AR无draft接受数，该项不适用。复用native证据/source/Study冻结门，仅全11格与process通过后生成正式证据；未完成格保持pending。运行和结论见[当前报告](docs/STUDY_REPORT.md)，CPU tiny/合成回归不代替真实4B。

全部11格验收后，阅读器同时生成`docs/figures/paired_outcomes.png`：两个预算各展示接受数和调用数的完整五方法胜负矩阵，格内W/T/L、颜色W−L，固定范围±480，保留全部输局；正式JSON记录绘图器SHA。未完成、失败、缺失或重复配对不生成图。布局回归使用明确标注的合成计数，真实图只来自完整正式证据；图不表示测速或总体显著性。
