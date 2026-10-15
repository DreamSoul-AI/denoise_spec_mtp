# ESP Table 1 Qwen3 BF16 protocol report

480 prompts; completed=3/4; 全四格验收=pending. 已完成格的τ/argmax有效性单列，AR失配不否定该格。BC60/1 is primary and BC60/2 is control, fixed before results.

| BC/masks | role | τ/argmax结果 | native状态 | AR exact/n (rate) | argmax checked/pass | pooled τ | τ − target | prompt mean τ | mean − target | category mean τ | category − target |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10/1 | primary | valid | succeeded | 188/480 (39.17%) | 79757/True | 1.399047 | n/a | 1.431766 | n/a | 1.403034 | n/a |
| 30/1 | primary | valid | succeeded | 175/480 (36.46%) | 79762/True | 1.563378 | -0.066622 | 1.593232 | -0.036768 | 1.563387 | -0.066613 |
| 60/1 | primary | valid | succeeded | 185/480 (38.54%) | 79618/True | 1.647301 | -0.092699 | 1.669498 | -0.070502 | 1.649693 | -0.090307 |
| 60/2 | control | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |

目标BC30=1.63，BC60双方均列相对1.74差值，不按τ选主配置。AR独立审计失配单列，不能宣称与独立AR一致；不阻止τ计算。τ验收要求全480、全部提交token的验证前向argmax自检通过，不以预检替代结果。

[PLAN](PLAN.md)引用G.2具体说明：Qwen3 BC60单mask/29节点，双mask/19节点为对照；保持动态树剪枝，BF16/T0/256/seed123，无测速/预热。

Mean mask按Eq5 λ=.1更新，与后续4B用户指定的ESP frozen mean不同。四格全部新Run，旧冻结PLAN不回写；旧AR门失败result归档；仅重新验收后记录真实native状态及新validator SHA，不重跑execute。新增argmax必须全过；独立AR差异不阻塞native summarize/process。

逐prompt计数、AR首分叉位置和自检覆盖及哈希见本机临时文件 `protocol_pending.json`（未入Git）。完整原始tokens/argmax选择记录/Run仅在本机保留，未运行格不能用预检外推。
