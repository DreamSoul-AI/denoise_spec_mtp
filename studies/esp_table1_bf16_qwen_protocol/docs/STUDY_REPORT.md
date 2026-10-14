# ESP Table 1 Qwen3 BF16 protocol report

13 prompts; observed=True, token quality passed=False. BC60/1 is primary and BC60/2 is control, fixed before results.

| BC/masks | role | exact/n | pooled τ | τ − target | prompt mean τ | mean − target | category mean τ | category − target |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10/1 | auxiliary | 6/13 | 1.369527 | n/a | 1.404570 | n/a | 1.404570 | n/a |
| 30/1 | primary | 6/13 | 1.548280 | -0.081720 | 1.558478 | -0.071522 | 1.558478 | -0.071522 |
| 60/1 | primary | 3/13 | 1.636982 | -0.103018 | 1.628615 | -0.111385 | 1.628615 | -0.111385 |
| 60/2 | control | 5/13 | 1.579408 | -0.160592 | 1.601749 | -0.138251 | 1.601749 | -0.138251 |

目标BC30=1.63，BC60双方均列相对1.74差值，不按τ选主配置。失配格τ是诊断值，不能算复现成功；预检不代替全480。

[PLAN](PLAN.md)引用G.2具体说明：Qwen3 BC60单mask/29节点，双mask/19节点为对照；保持动态树剪枝，BF16/T0/256/seed123，无测速/预热。

Mean mask按Eq5 λ=.1更新，与后续4B用户指定的ESP frozen mean不同。原执行冻结PLAN不回写，已有三格按哈希复用，原生exact门不放宽。

逐prompt计数、全部token及哈希见[protocol_evidence_v1.json](protocol_evidence_v1.json)。全部480的差值须另列，未运行不能用预检外推。
