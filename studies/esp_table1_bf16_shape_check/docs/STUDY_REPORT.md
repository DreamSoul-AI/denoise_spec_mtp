# ESP BF16 linear geometry control — failed correctness gate

2026-10-15 两格均已execute/collect，并被原生exact门拒绝；不完整通过。q81/BC10/96上限、BF16/T0/eager/dynamic+pruning/λ=.1，reduction=False/deterministic=False，无warmup/测速。

| control | patched linear modules | first new difference index | token exact | native |
| --- | --- | --- | --- | --- |
| native | 0 | 74 | no | failed |
| rowwise Linear | 253 | 9 | no | failed |

第二格所有nn.Linear按单行调用原forward，模型权重digest两格相同，dtype不变；RMSNorm/attention/RoPE与ESP科学源码不改。CPU控制测试验证了拆分/行置换、权重/dtype不变以及成功/异常patch恢复，16项控制回归通过。线性批量行数单独不是充分修复，不能据此认定其是唯一来源。两格AR输出彼此一致：False；完整token与哈希见[证据](shape_evidence_v1.json)。不同数值约定不作同路径接受收益比较。

[PLAN](PLAN.md)。下一最小问题：树中被屏蔽的KV位置虽为零softmax权重，矩阵尺寸仍不同；是否要固定每查询的有效KV与归约形状，并同时固定linear/norm行几何，才能与AR一致？此为待验证假设，不是已归因。仅为8B ESP复现继续，完整480/4B五方法暂不启动。
