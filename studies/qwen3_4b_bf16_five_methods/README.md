# Qwen3-4B BF16五方法配对

[计划](docs/PLAN.md)按首次make冻结执行，11/11 Run及native Study process全部通过，原串行队列已正常退出。10个Spec Run共4,800条prompt、809,118个提交token的argmax审计全过，输出owner/观测路径/实际BF16 mask范数验收通过；独立AR只运行一次480条。完整[报告](docs/STUDY_REPORT.md)、[逐prompt配对证据](docs/paired_evidence_v1.json)、[原生终验摘要](docs/native-process-evidence-v1.json)和[数字表](docs/NUMBERS.md)均已生成；正式JSON与真实图重复读出字节一致，图已目检。集成与CI见[PR #12](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/12)。

两个预算均由输入一阶取得最高总accepted和最少主calls；两输出方法对frozen mean/输入零阶有小幅总量改善，但均落后输入一阶。输出一阶相对输出零阶，BC30 accepted+191/calls+139/new tokens+332，BC60为+75/+55/+132；逐prompt胜负混合，未显示稳定联合收益。独立AR一致率33.54%–38.33%及全部首分叉仅诊断，不宣称token exact或同输出加速。前置[8B Table1全480报告](../esp_table1_bf16_full_argmax/docs/STUDY_REPORT.md)与原生process已完成，PR #10经CI合dev；论文τ目标未复现，负结果保留。

已完成同一480条SpecBench上的五方法×BC30/60加独立AR（共11 Run），统一双mask动态剪枝树/BF16/T0/256。owner映射、BF16原生验收回归及模型/输入来源核验已完成。原生source digest为538e52c929a542a8（56文件），首次make代码8047281；每Run实际cuda BF16/tied-storage与480输入、权重SHA的首forward前检查全过。队列round1/单GPU，日志各Run仅一个execute finished事件；未使用旧FP32结果替代，未测速或恢复算子机理。模型、forward与最终mask为BF16，输出EMA/范数保留原生FP32内部状态，边界在报告单列。

配置和来源预检已完成：11格在原生RPipe展开检查中通过；4B 14文件与魔搭直接SHA256/历史检查点一致，480条4B tokenizer输入与前置Table1逐token一致。离线魔搭缓存已接入，缓存master revision身份无法确认的原始警告如实保留，内容SHA已核验。详见[模型来源](docs/modelscope-content-verification-v1.json)、[输入清单](docs/prompts_manifest.json)。无计时adapter在每Run首forward前核对冻结模型/输入，检查实际tied-storage；协议/恢复/CUDA loader及四phase导出回归通过。

配对阅读器`analyze_results.py`保留五方法全部两两对照、逐prompt接受/calls赢平输及AR首分叉，另显式列出每个方法相对同一独立AR的调用数赢平输、Δcalls和两侧输出长度。AR无draft接受数，该项不适用。复用native证据/source/Study冻结门，仅全11格与process通过后生成正式证据；未完成格保持pending。运行和结论见[当前报告](docs/STUDY_REPORT.md)，CPU tiny/合成回归不代替真实4B。

本次真实图`docs/figures/paired_outcomes.png`展示两个预算各自的接受数与调用数完整胜负矩阵，格内W/T/L、颜色W−L，固定范围±480，保留全部输局；正式JSON记录绘图器SHA。未完成、失败、缺失或重复配对不生成图。布局回归的合成计数仅用于测试，真实图来自本次完整正式证据并已目检，不表示测速或总体显著性。
