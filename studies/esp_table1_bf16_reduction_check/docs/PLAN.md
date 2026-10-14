# ESP Table 1 BF16 reduction-control expansion

当前8B仅用于ESP复现，其他研究暂停。原13条/三BC分别只有6/6/5条与AR完全相同；q81最早分叉index9。q81新2×2控制的reduction=False/deterministic=False格32token已exact，AR输出与原设置相同。此Study预先固定原13条、BC10/30/60、256上限/EOS、T0/eager、dynamic/pruning、mean_prompt λ=.1 updating，与原始preflight同权重/tokenmanifest/source。唯一科学运算设置控制为allow_bf16_reduced_precision_reduction=False；deterministic=False，与原设置一致。CUBLAS_WORKSPACE_CONFIG=:4096:8固定，q81真值原设置控制已确认32token轨迹不受该环境变量影响。

全模型BF16，ESP状态也维持原生BF16，不转FP32；HF标准RMSNorm/softmax内部float32归约保持原实现。actualflags写入Run，原生fresh AR逐token门保持==1；三格先串行，禁止自动retry。三格全部通过才启动另一个新version全480三BC，任何不一致先保留反例并检查，不筛样本/追τ/使用teacher强制修正。即使这13条通过仍不是Table1成功，不把backend选择称为作者已确认配置。

13×3×2×256=19968生成token上界，没有warmup/teacher/计时；GPU只在numerics四格全部退出后使用。共享24GB，峰值采样包括背景，不比较墙钟。冻结前置raw哈希/权重文件/数据源/选定token；旧失败Run和未执行v1目录保留，新Run不重签。若失败，不切FP32或进入4B五方法。
