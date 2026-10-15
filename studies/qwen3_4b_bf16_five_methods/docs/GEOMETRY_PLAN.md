# 4B BF16 mask 几何与接受深度诊断

2026-10-15 Enmao 新指示：分析输出零/一阶为何落后输入一阶，先用既有结果做 CPU 分析，再按需要补最小 4B 观测。本文件是新诊断协议，不改首次 make 的 PLAN、配方、来源或成功 Run；本轮不是 ESP 原作者代码复现，不使用 8B。

## CPU 分析（零模型 forward）

- 读取全部 480 prompt、两个 BC、五方法的原始 decode_observations.json，并绑定 paired_evidence_v1.json 的原始 SHA；不重新执行 summarize 或签收 Run。
- 核对逐深度 attempt/accept、完整 trace 与总计数。深度条件接受率只使用真实 attempt 分母；按生成 root 索引分箱 [0,32)、[32,64)、[64,128)、[128,192)、[192,256)，报告每次验证块接受至少一个/两个候选的比例，不能冒充该位置的深度条件接受率。
- 用 τ = 1 + accept_d1/calls + accept_d2/calls − trim_loss/calls 分解差值；trim_loss=accepted+decode_calls−committed。它是计数恒等式，不是跨不同输出路径的因果分解。
- 检查输出 mask 的逐块 min/max 范数与记录的目标 r，核对固定 state/proxy 下速度项的作用槽位、EMA 更新、状态是否被预测污染。原日志没有 hidden 向量，不从范数或 token IDs 编造余弦分布。

## 最小 GPU 观测（须经非抢占准入）

固定选择原清单 coding、math_reasoning、summarization、translation 各第一条，选择不依赖结果；BC30，输入一阶/输出零阶/输出一阶，原 BF16/T0/eager/默认设置，max_new_tokens=64/EOS，共 12 个短诊断，生成上限 768 token、模型 forward 上限 768。复用已核验的 ModelScope Qwen3-4B，单进程串行，不下载新权重、不跑独立 AR forward、不测速。

启动前两次检查共享 GPU 显存与 Python 作业；没有其它 GPU/未知模型作业且可用显存至少 18 GiB 才加载。已有其它作业则不加载、记录 deferred；不抢占、不终止其它进程。每个短诊断前再核查新作业。桌面图形进程与已确认的 CPU CI 单列；这些检查是观测准入，不冒称跨进程的原子全局预约。

首次准入因发现未知 Python 作业延期，未加载模型。随后核验量化任务 `download_layers.py`：只调用下载和文件哈希，不加载模型；仅路径与 SHA256 `10689bac808d0e5fa1958d306508f459d3c4637dc92a51bf5b6c1bb915545026` 同时匹配时按已核验 CPU 下载作业放行，变化或其他未知作业仍延期。保留首次延期证据。

使用未修改的 SpecDecoder/HFCausalLM/真实 provider，只增加只读 hook，记录实际输入 mask、原生 final-normalized hidden、provider 的原始 state/proxy。只处理 root 与实际接受路径上的 owner；拒绝分支没有真实延续，不混入目标统计。槽 j 的目标为该 owner 之后第 j+1 个实际生成 token 的 embedding，末尾无目标者跳过并计数。另比较真实 owner hidden 与其预测的下一 token embedding，区分原始 hidden、范数缩放后的实际 BF16 mask、真实 embedding。

验证全部提交 token 的原生 verifier-argmax 审计、输出为原完整 Run 的前缀、hook 未增加 forward。独立 AR 前缀一致率只从已有共享 AR 读出，不作为失败门。完整向量/原始 token 仅本机保存，公开逐点几何标量、分位数、计数及 SHA。几何分析在 CPU 完成；不改变算子/归约开关，不分析 BF16 算子数值分叉。

## 假设与可证伪边界

1. H1：输出范数映射错误或偏离目标 r；用全部旧 trace 的范围及新实际 mask 范数检查。半径正确不证明方向或输入分布正确。
2. H2：last-hidden 与输入 embedding 的方向/分布不兼容；比较 raw hidden、actual mask、真实 owner hidden、目标 embedding 及输入 mask。tied 权重不等价于 hidden 到 embedding 的逆映射；余弦相关不等于接受因果。
3. H3：速度直接影响的槽与第二深度实际机会有限；联合源码槽位恒等式、深度条件接受率和每块深度收益检查。固定 state 下首槽不变不能推出整个后续轨迹完全无影响。
4. H4：代理 hidden 对真实 owner hidden 的误差掩盖速度收益；只在有真实 owner 的路径计算，两方法不同路径及共享前缀子集单列，不将拒绝 owner 当真值。
5. H5：输入/输出 β、初始化与阶数作用定义不匹配；报告实际速度/anchor 范数与槽间角度，不能把不同固定配方的差异全部归于空间。

当前只观测，不改默认配方或调参，不启动大矩阵、teacher 或算子机理。GPU 不获准时交付完整 CPU 证据、实现检查与未完成几何缺口；获准则按上述固定预算补采。结果写入 docs/research，并保留所有负结果与局限，按主题提交和 PR 合 dev。
