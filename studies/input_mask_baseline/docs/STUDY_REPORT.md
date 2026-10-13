# Study Report: input_mask_baseline

本轮计划已确认，尚未执行。问题、条件和停止门见 [PLAN](PLAN.md)。四个真实模型 case 的结果不能由 Toy/Stub 或随机 tiny 代替；没有执行的数字留空。

## 2026-10-14 新设备前置状态

执行来源升级为固定 RPipe v0.3.1 / 7a15c46；采用 input-mask-baseline-v031-win5090-20261014-v2。实际 make 展开四格成功，配置保留模型/输入/精度/seed/预算和离线门；[设备前检](v031_device_preflight.json) 保存四 Run ID 与来源。make 的通用模型估算为每 Run 26.5GiB/3秒，round1 独占；这是启发式估计，不是0.6B实际资源或 wall 测量，不能用于资源/速度结论。

Study/default ModelScope local_files_only 核验均返回 CacheNotFound E1022；没有已确认 Qwen3-0.6B snapshot。当前仅有资源 inventory，未进行真实模型串行校准，也未 launch 四 Run。执行完成=false，研究质量通过=false；frozen_mean、gamma_last、AR、alignment 均无新数字、图或 raw token。未使用其他规模模型替代，也未下载/替换 snapshot、放宽 exact_match=1 或扩大矩阵。等待缓存路径后继续来源核对与原 PLAN。

| case | Run ID | 状态 |
| --- | --- | --- |
| frozen_mean | 2e1ef22e0f4ae1de | 未执行，缺权重 |
| gamma_last | 718122580b383b67 | 未执行，缺权重 |
| AR | 40bd71c3d907ba5a | 未执行，缺权重 |
| alignment | 1bbbabc47cdc703c | 未执行，缺权重 |

本轮n=1工程前置门不支持宏观H1–H13或方法优越性。源码升级的工程门在 smoke 报告单列，不替代本表。
