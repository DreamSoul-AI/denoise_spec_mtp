# Input-mask baseline prerequisite

从 [宏观方案到 Study](../../docs/research/rpipe-study-extraction.md) 提取的真实 Qwen3-0.6B / SpecBench q171 前置门。先看 [PLAN](docs/PLAN.md)，结果写 [STUDY_REPORT](docs/STUDY_REPORT.md)。四个 case 复用 src/spec_mtp 阶段，不含第二套算法或调度。

在既有 ModelScope 缓存准备到 shared/model 后，从仓库根运行 `python -m spec_mtp make studies/input_mask_baseline --num-gpus 1 --init-gpu 0 --round 1`，再 `launch studies/input_mask_baseline --num-gpus 1 --init-gpu 0 --console shared`，最后 process/status/logs/report。offline 设置要求缓存可用；不默默联网替换权重。新复跑须新 version，旧证据保留。

本 Study 只验证已有输入空间 baseline、AR 与 alignment 的实际接口/数值合同，不检验输出空间/Kalman 假设或宣称完整论文复现。原始 Run/权重不随 clone 提供。
