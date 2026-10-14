# ESP Table 1 BF16 reduction expansion — failed correctness gate

原13条/三BC/256上限均未通过；q81前32token的命中修复不能推广到整条输出。全480未启动，4B配对未启动。

| BC | exact / 13 | original setting exact / 13 | AR identical to original / 13 | pooled τ（失配诊断值） |
| --- | --- | --- | --- | --- |
| 10 | 4 | 6 | 5 | 1.365882 |
| 30 | 3 | 6 | 5 | 1.547541 |
| 60 | 5 | 5 | 5 | 1.600939 |

BF16、T0、eager、dynamic/pruning、λ=.1 updating mean及实际checkpoint均不变。实际控制为reduced_precision=False/deterministic=False，模型/输入/原生科学源码冻结；所有计时0为禁用占位，不测速。完整原生门拒绝失配，未重签旧Run、删失败或筛样本。

部分AR自身也随归约模式改变，不能把不同数值约定的接受数当作严格同AR路径增益。每格仍与自己的独立AR比较并保留原AR差异；逐条边界见[证据](reduction_evidence_v1.json)。q81 BC10第75个新token（index74）再分叉，原32-token观察只能限定为局部结果。

假设收紧：归约模式能影响BF16批量核行为与argmax边界，但关闭它不是充分修复；亦不说明树/cache语义错误。下一项[最小形状对照](../../esp_table1_bf16_shape_check/docs/PLAN.md)只控制nn.Linear的batch行几何，仍用于ESP8B正确性门。不触及mask新方法/default/src、4B或Kalman。若单行linear仍失配，不能宣称linear是唯一来源。

[冻结协议](PLAN.md)、[权重清单](modelscope_snapshot.json)、[完整token/flags/计数/哈希](reduction_evidence_v1.json)。整个Study质量不完整通过，没有可用Table1成功结论。
