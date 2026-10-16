# ESP Table 1 full SpecBench BF16 matrix

[PLAN](<../../docs/研究计划 Denoising Speculative Decoding.md#legacy-studies-esp-table1-bf16-full-docs-plan>): full480, BC10/1, BC30/1, BC60/1 primary and BC60/2 control. Both BC60 rows and target deltas are mandatory. Known preflight numerical failures are retained; full execution is evidence, not automatic reproduction success. No speed tests/FP32/new methods.

## 新合同替代

本v1启动后，用户要求全量验证前向argmax自检。v1未记录对应logits行的argmax，不能事后补证。原冻结合同及已有日志保留；当前全量入口为[full_argmax](../esp_table1_bf16_full_argmax/README.md)，不将本Run部分日志当成完整480或自检通过。
