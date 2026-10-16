# ESP BF16 numerical controls — q81 / BC10 / 32 tokens

2026-10-15 已执行四格，只有一格原生全链通过，整个Study不完整通过。所有模型均BF16、T0/eager、dynamic+pruning、λ=.1 updating mean，无预热/测速。

| BF16 reduced precision reduction | deterministic | token exact | first new difference index | native result |
| --- | --- | --- | --- | --- |
| true | false | no | 9 | failed: raw exact |
| false | false | yes | none | succeeded |
| true | true | no | 9 | failed: raw exact |
| false | true | yes | none | failed: runtime changed before finalisation |

AR输出四格都与原始preflight的前32token完全相同；基线格的ESP32token也与原始完全相同，支持CUBLAS_WORKSPACE_CONFIG和长度缩短没有改变这个最早分叉对照。关闭BF16归约足以消除此单条/短长度的token分叉，不能推断其他prompt/256长度或全部BC也修复。单开deterministic不能修复此样本。不得把组合格的raw exact当作完整通过。

第四格失败是工具生命周期：Algorithm的finally恢复deterministic后，native write/summarize gate复查运行设置而拒绝，正确性门没有放宽。记录该限制；后续仅采用已全链通过的false/false组合，暂不采用deterministic=true。若后续需采用deterministic=true，应让设置覆盖prepare至finalisation并另建新Run验证，不能重签本Run。v1仅make/CPU恢复测试失败，未跑GPU；v2执行四格，旧pending目录保留。

[PLAN](<../../../docs/研究计划 Denoising Speculative Decoding.md#legacy-studies-esp-table1-bf16-numerics-docs-plan>)、[逐token/实际flags/哈希证据](numerics_evidence_v1.json)、[扩大验证](<../../../docs/研究计划 Denoising Speculative Decoding.md#legacy-studies-esp-table1-bf16-reduction-check-docs-plan>)。扩大验证沿用原13条/三BC/256上限与AR审计；三格全通过后才排全480。科学源码和默认配方没有修改，不进入4B五方法。
