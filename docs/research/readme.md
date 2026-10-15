# Research notes

人写的研究计划，不是 Study 执行合同。Study 的 `PLAN.md` / `STUDY_REPORT.md` 仍在 `studies/<name>/docs/`。已记下的接受数在 [history-extrapolation.md](../history-extrapolation.md)。

| **文件** | **性质** |
| --- | --- |
| [research-plan-v6.md](research-plan-v6.md) | denoising speculative decoding 草案。主方法和卡尔曼变体均【待测】；附录 C 的输入空间 / 树形格子才是【实测】 |
| `research-plan-v6.pdf` | 同一份 PDF，gitignored |

本轮可独立验收的提取见 [rpipe-study-extraction.md](rpipe-study-extraction.md)，对应 [input_mask_baseline](../../studies/input_mask_baseline/README.md)。原 v6 的输出空间、Kalman 和外部 baseline 仍待实现/验证。

[跨任务证伪Study草案](../../studies/output_space_cross_task/README.md)固定另一任务四输入但未运行，含未执行的transformer固定行kernel隔离协议。[最小推送候选与清单](publication-plan.md)、[逐blob manifest](publication-manifest.json)和[PR说明草稿](pr-draft.md)只供本地评审，未推送／新建PR。

当前阶段结果（2026-10-15）：[ESP Table1全480](../../studies/esp_table1_bf16_full_argmax/docs/STUDY_REPORT.md)数学门/原生process通过，τ目标未复现；PR #10经CI合dev。[4B BF16五方法配对](../../studies/qwen3_4b_bf16_five_methods/docs/STUDY_REPORT.md)已完成11/11及原生process，809,118个Spec提交token自检全过，全部20组逐prompt对照及AR首分叉已保留。输入一阶本次总accepted最高、calls最少；两输出方法对mean基线有小幅总量改善，速度项相对输出零阶无稳定联合收益。[正式证据](../../studies/qwen3_4b_bf16_five_methods/docs/paired_evidence_v1.json)与真实图重复读出字节一致；[集成与CI](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/12)。[冻结计划](../../studies/qwen3_4b_bf16_five_methods/docs/PLAN.md)不回写执行状态。其他研究暂停，0.6B与4B FP32保留归档；未恢复算子机理或测速，8B仅限该Table1复现。
