# Research notes

人写的研究计划，不是 Study 执行合同。Study 的 `PLAN.md` / `STUDY_REPORT.md` 仍在 `studies/<name>/docs/`。已记下的接受数在 [history-extrapolation.md](../history-extrapolation.md)。

当前结果速读：[SD 阶段报告：8B ESP 复现与 4B BF16 方法比较](sd-stage-report-2026-10-15.md)。集中列出已有结果的 τ、论文差值、全部逐 prompt 胜平负、正确性门、排名与局限，并逐表链接原始结果文件；下一步建议尚未执行。

Enmao 最新指示的独立诊断：[4B BF16 输出 mask 差距诊断](4b-mask-geometry-2026-10-15.md)、[全 480 条 CPU 证据](4b-mask-geometry-cpu-2026-10-15.json)、[固定预算观测协议](../../studies/qwen3_4b_bf16_five_methods/docs/GEOMETRY_PLAN.md)。只分析既有结果及小规模 4B 几何，不恢复其他研究或 8B 算子数值链。

后续[候选质量与固定窗口阶段报告](4b-mask-window-2026-10-15.md)推进到同前缀真实干预：输入一阶四窗口首目标排名更好，输出局部改法未增加接受；补充固定模板差分混杂、径向分解和树预算/Top-1父节点限制。追加2个条件窗口也已完成，未发现输出接受增益，正负结果分表保留；共享GPU释放后按准入执行，无遗留等待任务。

同报告第八节追加24格同mean模板/零速度控制，两批100次forward数学门全过，接受数对原生输入速度均持平；CPU定位旧480条有459条首次接受差异在root<8。下一假设前移prefill/早期差异块，目前未执行，不外推全量速度无用。

原作者官方代码复现仍有来源缺口：[ESP 官方代码复现报告与来源核查](esp-official-code-reproduction-2026-10-15.md)、[请求状态/commit/SHA 审计](esp-official-source-audit-2026-10-15.json)。尚未核验到可运行的作者实现，OpenReview 补充材料访问不完整；该次来源核查未启动 GPU。此前 8B 数字为自实现参考，不满足原作者代码要求。

| **文件** | **性质** |
| --- | --- |
| [research-plan-v6.md](research-plan-v6.md) | denoising speculative decoding 草案。主方法和卡尔曼变体均【待测】；附录 C 的输入空间 / 树形格子才是【实测】 |
| `research-plan-v6.pdf` | 同一份 PDF，gitignored |

本轮可独立验收的提取见 [rpipe-study-extraction.md](rpipe-study-extraction.md)，对应 [input_mask_baseline](../../studies/input_mask_baseline/README.md)。原 v6 的输出空间、Kalman 和外部 baseline 仍待实现/验证。

[跨任务证伪Study草案](../../studies/output_space_cross_task/README.md)固定另一任务四输入但未运行，含未执行的transformer固定行kernel隔离协议。[最小推送候选与清单](publication-plan.md)、[逐blob manifest](publication-manifest.json)和[PR说明草稿](pr-draft.md)只供本地评审，未推送／新建PR。

当前阶段结果（2026-10-15）：[ESP Table1全480](../../studies/esp_table1_bf16_full_argmax/docs/STUDY_REPORT.md)数学门/原生process通过，τ目标未复现；PR #10经CI合dev。[4B BF16五方法配对](../../studies/qwen3_4b_bf16_five_methods/docs/STUDY_REPORT.md)已完成11/11及原生process，809,118个Spec提交token自检全过，全部20组逐prompt对照及AR首分叉已保留。输入一阶本次总accepted最高、calls最少；两输出方法对mean基线有小幅总量改善，速度项相对输出零阶无稳定联合收益。[正式证据](../../studies/qwen3_4b_bf16_five_methods/docs/paired_evidence_v1.json)与真实图重复读出字节一致；[集成与CI](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/12)。[冻结计划](../../studies/qwen3_4b_bf16_five_methods/docs/PLAN.md)不回写执行状态。其他研究暂停，0.6B与4B FP32保留归档；未恢复算子机理或测速，8B仅限该Table1复现。
