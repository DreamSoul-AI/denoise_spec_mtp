# ESP Table 1 BF16 numerical gate isolation

仅服务当前8B ESP复现，不启动其他方法/4B。前置BC10的13条只有6条exact，q81最早分叉在新token index9（40233 vs20397）。先在q81、BC10、动态树/剪枝、lambda=.1、T0、32-token上限下，固定checkpoint/prompt与原生算法；比较2×2控制：allow_bf16_reduced_precision_reduction True/False × deterministic False/True。所有权重/模型activation保持BF16；正常HF RMSNorm/softmax的内部高精度归约是原生实现，不切FP32模型。全部禁用解码计时/预热。

CUBLAS_WORKSPACE_CONFIG=:4096:8 对四格一致，recipe设置在模型首次CUDA计算之前。首格重复原条件用于核对该环境配置和长度变化是否改变早期分叉；不是重签旧Run。其余格单因子与交互比较，不能把组合控制结果叫单kernel归因。Run内记录实际flags且成功/失败均恢复进程先前设置。若最早分叉未消失，不能把deterministic或reduction解释为充分修复；若消失仍只是一条短样本，下一步必须扩大前置13条/三BC。

原生exact_match_rate==1门保持；失败输出/Run不删，最大上限4×1×2×32=256生成token，另计checkpoint哈希成本。共享24GB卡只在preflight三个Run退出/显存释放后串行启动，一条launch链。无FP32、无速度、无teacher强制接受或筛样本。冻结前置raw SHA256/同tokenmanifest/本地16文件权重哈希；该对照不能替代Table1全480。


v1仅make，未启动GPU；CPU注入失败测试发现patch.object不支持CUDA后台属性删除恢复。v2改为显式try/finally赋值恢复并使用新version/Run，旧pending目录保留，不作为已执行结果。
