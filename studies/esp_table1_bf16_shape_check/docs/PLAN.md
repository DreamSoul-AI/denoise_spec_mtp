# ESP BF16 shape control — q81 / BC10 / 96 tokens

只服务8B ESP Table1复现的token exact门；不启动新mask方法/4B/Kalman。reduction=False/deterministic=False虽使q81前32token一致，原13条256长度BC10仅4/13 exact，q81在index74再次分叉。最小假设：相同线性投影随批量行数选择不同BF16 GEMM归约路径，导致树batch与AR单行边界差异。

两格固定同checkpoint/q81/input/seed123，BF16、T0/eager、BC10单mask、dynamic/pruning、λ=.1 updating mean、96上限/EOS。归约禁用/确定性false两格一致。唯一干预：第二格把模型内nn.Linear按单行调用其原始forward再拼回原形，同时用于ESP与AR，不改变权重/激活dtype、RMSNorm/attention/RoPE、树/cache/mask/接受语义。第一格原native路径用于核对256→96前缀一致性。父级LLM forward调用数保持原统计；内部GEMM调用变多，因此不能用此对照做速度或算力结论。

单行linear是显式数值约定控制，尚未宣称作者实现或通用修复；若AR输出也改变，完整列出，不能对旧AR强制对齐。只比较各自新鲜AR并保留所有失配。若此干预也未通过，线性批量行数不是充分解释，继续定位attention/norm的形状边界；不调参追τ。即使通过，下一步必须13条/三BC，再全480。

在当前reduction_check三个Run退出后串行执行，不自动retry。2×1×2×96=384生成token上界；无warmup/teacher/timing。原始失败与来源保留，新version/Run。所有patch用ExitStack在成功/异常恢复；CPU测试检查BF16的批量拆分/行置换一致性、dtype/权重不变与异常恢复。
