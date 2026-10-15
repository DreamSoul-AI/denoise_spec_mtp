# 4B 输出 mask 固定窗口对照

2026-10-15，接续 Enmao 对输出侧差距的诊断要求。PR #17 的全量深度/位置分解与 12 格只读几何已完成。本协议新增 CPU 向量分解及有限窗口干预，不改原科学源码、配方、PLAN 或 Run，不跑 8B、FP32 模型、测速或算子数值链。

## 一、CPU 先行

1. 绑定已有 geometry.json、vectors.pt 和原始 Run SHA。对同 owner 的原始槽差 v 做径向/切向分解，计算统一范数映射保留的相对移动量，检验“归一化消掉大部分速度”的具体版本。这里只看原始向量的几何运算，不追踪 BF16 算子。
2. 全 480 条 BC30/60 的三方法按上一块接受深度分组，报告下块 d1 接受率与下一树 seed owner 深度。它是条件统计，不作跨路径因果结论。
3. 对照 decoder：mask 槽位输入对应 owner+1/owner+2，槽位 logits 则预测 owner+2/owner+3。下一树以 deepest accepted owner 的 bonus 为 root。固定当前树时，mask 不参与当前 owner 的验证注意力；不能把当前 mask 改动误算为当前接受率收益。

## 二、GPU 最小固定窗口

沿用预先选定的 q121/q401/q241/q161，各从已完成输出零阶 Run 的原设置重建前缀，只取第一个 root_index >=8 的验证块，最多重建到 32 新 token。选择与接受结果无关。4 个上下文、5 种输出局部干预加输入一阶同历史控制，共24格，最多 128 次总模型 forward，不生成完整轨迹或矩阵。输入控制用于直接核对同一窗口内的两端差距，不以不同原生成轨迹冒充控制。

同一个输出零阶真实前缀、cache、当前树、真实已验证 hidden 历史和代理观测上，并行维护 order1 shadow state（β=.9、β′=.99），不把 shadow 预测写入真实历史。局部 2×2：速度从槽0还是槽1开始、逐槽固定半径还是保留槽间径向幅度。另设原输出零阶对照。位移系数固定为 1，不搜索参数。

| 名称 | 预测槽（j=0,1） | 范数映射 |
| --- | --- | --- |
| zero | 原 order0 anchor | 原 r·a/范数(a) |
| input_first | 原 β=.9999、λ=.1 mean+gamma，gamma=1，按相同输出零阶真实 token 历史更新输入 provider | 原输入配方，不缩放 |
| first | 原 order1 a+j·v | 原逐槽固定半径 |
| shifted | a+(j+1)·v | 原逐槽固定半径 |
| radial | 原 order1 a+j·v | 统一用本 owner 的原 a 范数作分母 |
| both | a+(j+1)·v | 统一用本 owner 的原 a 范数作分母 |

order1 的 a/v 由原生 shadow.masks_per_owner 对同一代理作纯推演。深度0/1令 a=对应代理，深度2沿原规则 a+=v；只改变表中局部槽公式与映射。保持原 BF16/T0/eager/默认归约和双 mask BC30/9 节点。

每格先在同一当前块/cache 上前向，核对 root/真实接受 owner 的 argmax 与原控制完全一致，且控制重放与原输出零阶 Run 对齐。随后用 deepest owner 的两行 mask logits 原生 build_tree 生成下一树，记录目标 token 的原始 rank、剪枝/预算后是否入树、d1/d2 宽度。目标来自已有输出零阶轨迹，只是诊断，不是 teacher 强制纠正。

再用该格下一树和同一真实前缀 cache 做一个原生验证块，mask 内容使用相同控制规则，只读 owner logits 的 argmax 路径。报告实际接受深度、数学 argmax 自检、与原控制及旧轨迹是否一致。每个干预仅两次局部前向；不沿干预结果继续生成。独立 AR 不新增 forward、不作门。

准入已核验的 CPU 准备作业包括量化容器 build_v3（无 Docker GPU/device 参数，SHA bc206af76763f1364fe2565be1be8cf2294342aaa414f3b263cbf115dafcceec）、RPipe watch-first/second 的远端 CI 查询及其子进程。工具按实际脚本 SHA 检查并记录计数，未知作业继续拒绝。检查只针对资源准入，不运行或修改这些外部脚本。

## 三、准入、停止与证据

复用已核验的 ModelScope Qwen3-4B，加载前两次非抢占检查和内容 SHA 检查，每个上下文再查。若未知 GPU/模型作业存在或初始可用显存不足18 GiB，保留 deferred，不抢占或杀其他作业。此为观测准入，不冒称全局原子锁。

模型/source/输入不符、控制前缀或当前 owner argmax 不符、forward 超128、非有限或 OOM 则保留证据并停止，不切精度、不追算子分叉。未获准就交付 CPU 结果与明确几何缺口，不编造实验。

正式报告和可公开标量放 docs/research，完整 cache/权重/logits/token IDs 留本机 .tmp。保留全部零收益/负收益。固定窗口可区分局部作用，不能说明全 480 条 τ 会改善。工具、协议、模型、来源与原始证据绑定 SHA，按主题提交、PR 合 dev，保留分支和数据。
