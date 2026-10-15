# Research notes

当前计划：[中文十章计划](../research-plan.md)、[English translation](../research-plan.en.md)；[新版规范与模板来源](standards/README.md)。文献证据、问题、六方面安排、实际结果和未验收边界已整合；旧v6为历史设想，不作为当前Kalman/新方法执行授权。全480方向对照继续，实时结果在[PR22](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/22)，本次文档不改冻结Study。

当前执行主线：[4B BC30全480方向对照](../../studies/qwen3_4b_bf16_directions/README.md)。按10月16日追加指示扩大全量，五格新完整路径加复用旧零偏置；原四窗口仅保留局部证据。计划已冻结，正式状态以该Study报告为准；不修改数据或prompt、不新增方法。

人写的研究计划，不是 Study 执行合同。Study 的 `PLAN.md` / `STUDY_REPORT.md` 仍在 `studies/<name>/docs/`。已记下的接受数在 [history-extrapolation.md](../history-extrapolation.md)。

当前结果速读：[SD 阶段报告：8B ESP 复现与 4B BF16 方法比较](sd-stage-report-2026-10-15.md)。集中列出已有结果的τ、论文差值、全部逐prompt胜平负、正确性门、排名与局限，并逐表链接原始结果文件；最新目标交付及未复现边界另在顶部说明。

当前目标交付：[非官方HF第三方ESP原码验收](esp-third-party-reproduction-2026-10-15.md)。源commit/逐文件SHA固定、所有code原字节保留；真实8B BF16固定q121三预算共6次forward均首token数学门失败，未跑其全480、无有效τ，不改算法或prompt修结果。[审计JSON](esp-third-party-audit-2026-10-15.json)保留位置/margin/来源；现有五方法加AR和四窗口方向控制已完成，PR20已合dev并清理对应远程分支；追加全480方向对照仍在执行，不把四窗口交付视为全量完成。

Enmao 最新指示的独立诊断：[4B BF16 输出 mask 差距诊断](4b-mask-geometry-2026-10-15.md)、[全 480 条 CPU 证据](4b-mask-geometry-cpu-2026-10-15.json)、[固定预算观测协议](../../studies/qwen3_4b_bf16_five_methods/docs/GEOMETRY_PLAN.md)。只分析既有结果及小规模 4B 几何，不恢复其他研究或 8B 算子数值链。

后续[候选质量与固定窗口阶段报告](4b-mask-window-2026-10-15.md)推进到同前缀真实干预：输入一阶四窗口首目标排名更好，输出局部改法未增加接受；补充固定模板差分混杂、径向分解和树预算/Top-1父节点限制。追加2个条件窗口也已完成，未发现输出接受增益，正负结果分表保留；共享GPU释放后按准入执行，无遗留等待任务。

同报告第八节追加24格同mean模板/零速度控制，两批100次forward数学门全过，接受数对原生输入速度均持平；CPU定位旧480条有459条首次接受差异在root<8。后续早期差异块已经执行，见第九至十二节；不外推全量速度无用。

第九至十二节已补早期双向互换和Enmao指定的原方向/三种子同范数随机/零偏置/内容初始化。q121/q241出现可逆局部接受翻转；随机0也使q241提升，不能将收益限定为唯一模板方向。完整主实验仍为原固定数据11/11，未改prompt或发明新方法。[远程分支清理](remote-branch-cleanup-2026-10-15.md)记录实际删除与保留清单，后续PR合dev后删除相应工作远程分支。

原作者官方代码复现仍有来源缺口：[ESP 官方代码复现报告与来源核查](esp-official-code-reproduction-2026-10-15.md)、[请求状态/commit/SHA 审计](esp-official-source-audit-2026-10-15.json)。尚未核验到可运行的作者实现，OpenReview 补充材料访问不完整；该次来源核查未启动 GPU。此前 8B 数字为自实现参考，不满足原作者代码要求。

| **文件** | **性质** |
| --- | --- |
| [research-plan-v6.md](research-plan-v6.md) | denoising speculative decoding 草案。主方法和卡尔曼变体均【待测】；附录 C 的输入空间 / 树形格子才是【实测】 |
| `research-plan-v6.pdf` | 同一份 PDF，gitignored |

本轮可独立验收的提取见 [rpipe-study-extraction.md](rpipe-study-extraction.md)，对应 [input_mask_baseline](../../studies/input_mask_baseline/README.md)。原 v6 的输出空间、Kalman 和外部 baseline 仍待实现/验证。

[跨任务证伪Study草案](../../studies/output_space_cross_task/README.md)固定另一任务四输入但未运行，含未执行的transformer固定行kernel隔离协议。[最小推送候选与清单](publication-plan.md)、[逐blob manifest](publication-manifest.json)和[PR说明草稿](pr-draft.md)只供本地评审，未推送／新建PR。

当前阶段结果（2026-10-15）：[ESP Table1全480](../../studies/esp_table1_bf16_full_argmax/docs/STUDY_REPORT.md)数学门/原生process通过，τ目标未复现；PR #10经CI合dev。[4B BF16五方法配对](../../studies/qwen3_4b_bf16_five_methods/docs/STUDY_REPORT.md)已完成11/11及原生process，809,118个Spec提交token自检全过，全部20组逐prompt对照及AR首分叉已保留。输入一阶本次总accepted最高、calls最少；两输出方法对mean基线有小幅总量改善，速度项相对输出零阶无稳定联合收益。[正式证据](../../studies/qwen3_4b_bf16_five_methods/docs/paired_evidence_v1.json)与真实图重复读出字节一致；[集成与CI](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/12)。[冻结计划](../../studies/qwen3_4b_bf16_five_methods/docs/PLAN.md)不回写执行状态。其他研究暂停，0.6B与4B FP32保留归档；未恢复算子机理或测速，8B仅限该Table1复现。
