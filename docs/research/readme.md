# Research notes

人写的研究计划，不是 Study 执行合同。Study 的 `PLAN.md` / `STUDY_REPORT.md` 仍在 `studies/<name>/docs/`。已记下的接受数在 [history-extrapolation.md](../history-extrapolation.md)。

| **文件** | **性质** |
| --- | --- |
| [research-plan-v6.md](research-plan-v6.md) | denoising speculative decoding 草案。主方法和卡尔曼变体均【待测】；附录 C 的输入空间 / 树形格子才是【实测】 |
| `research-plan-v6.pdf` | 同一份 PDF，gitignored |

本轮可独立验收的提取见 [rpipe-study-extraction.md](rpipe-study-extraction.md)，对应 [input_mask_baseline](../../studies/input_mask_baseline/README.md)。原 v6 的输出空间、Kalman 和外部 baseline 仍待实现/验证。

[跨任务证伪Study草案](../../studies/output_space_cross_task/README.md)固定另一任务四输入但未运行，含未执行的transformer固定行kernel隔离协议。[最小推送候选与清单](publication-plan.md)、[逐blob manifest](publication-manifest.json)和[PR说明草稿](pr-draft.md)只供本地评审，未推送／新建PR。

当前执行进度（2026-10-15）：[ESP Table1全480](../../studies/esp_table1_bf16_full_argmax/docs/STUDY_REPORT.md)已完成且数学门/原生process通过，τ目标未复现；PR #10经CI合dev。[4B BF16五方法配对](../../studies/qwen3_4b_bf16_five_methods/docs/STUDY_REPORT.md)已冻结并串行运行，独立AR、BC30五方法和BC60 frozen mean/输入零阶共8/11格各480条原生成功，全部Spec提交token的argmax审计通过。BC60其余三格尚未完成，完整两预算结论待验收；[冻结计划](../../studies/qwen3_4b_bf16_five_methods/docs/PLAN.md)不回写运行状态。其他研究暂停，0.6B与4B FP32保留归档；不恢复算子机理、不测速，8B仅限已完成的Table1复现。
