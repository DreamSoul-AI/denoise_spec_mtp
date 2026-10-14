# ESP Table 1 Qwen3 BF16 protocol report

480 prompts; observed=False, token quality passed=False. BC60/1 is primary and BC60/2 is control, fixed before results.

| BC/masks | role | exact/n | pooled τ | τ − target | prompt mean τ | mean − target | category mean τ | category − target |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10/1 | auxiliary | pending | pending | n/a | pending | n/a | pending | n/a |
| 30/1 | primary | pending | pending | pending | pending | pending | pending | pending |
| 60/1 | primary | pending | pending | pending | pending | pending | pending | pending |
| 60/2 | control | pending | pending | pending | pending | pending | pending | pending |

目标BC30=1.63，BC60双方均列相对1.74差值，不按τ选主配置。失配格τ是诊断值，不能算复现成功；这是全480；预检不代替其结果。

[PLAN](PLAN.md)引用G.2具体说明：Qwen3 BC60单mask/29节点，双mask/19节点为对照；保持动态树剪枝，BF16/T0/256/seed123，无测速/预热。

Mean mask按Eq5 λ=.1更新，与后续4B用户指定的ESP frozen mean不同。四格全部新Run，原执行冻结PLAN不回写，原生exact门不放宽。

逐prompt计数、全部token及哈希见[protocol_pending.json](protocol_pending.json)。完整原始tokens/Run仅在本机保留，未运行格不能用预检外推。
