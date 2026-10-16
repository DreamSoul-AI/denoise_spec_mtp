# ESP Table 1 BF16 preflight

Only ESP / Qwen3-8B; dynamic/pruned BC10/30/60, 13 fixed prompts, T0, 256-token cap, no timing. [PLAN](<../../docs/研究计划 Denoising Speculative Decoding.md#legacy-studies-esp-table1-bf16-preflight-docs-plan>). Full480 follows only after exact BF16 AR validation. Failed cells remain evidence.


协议更正（2026-10-15）：本Study冻结PLAN中的BC60/2现在仅作为对照，不能作Qwen3主复现。G.2具体说明与当前主配置见[修订预检PLAN](<../../docs/研究计划 Denoising Speculative Decoding.md#legacy-studies-esp-table1-bf16-qwen-protocol-docs-plan>)；旧PLAN/Run不修改、不重签，单mask/29节点采用新身份补跑。
