# Input-mask baseline prerequisite

从 [宏观方案到 Study](../../docs/research/rpipe-study-extraction.md) 提取的真实 Qwen3-0.6B / SpecBench q171 前置门。先看 [PLAN](<../../docs/研究计划 Denoising Speculative Decoding.md#legacy-studies-input-mask-baseline-docs-plan>)，结果写 [STUDY_REPORT](docs/STUDY_REPORT.md)。四个 case 复用 src/spec_mtp 阶段，不含第二套算法或调度。

先按ModelScope显式下载准备snapshot到shared/model，实际Run保持离线加载；随后，从仓库根运行 `python -m spec_mtp make studies/input_mask_baseline --num-gpus 1 --init-gpu 0 --round 1`，再 `launch studies/input_mask_baseline --num-gpus 1 --init-gpu 0 --console shared`，最后 process/status/logs/report。offline 设置要求缓存可用；不默默联网替换权重。新复跑须新 version，旧证据保留。

本 Study 只验证已有输入空间 baseline、AR 与 alignment 的实际接口/数值合同，不检验输出空间/Kalman 假设或宣称完整论文复现。原始 Run/权重不随 clone 提供。

当前v4已完成q171四格真实前置门，过程包含B-008完整性误拒绝修复，v3证据保留。正式 [来源清单](docs/modelscope_snapshot.json)、[v4原始精选](docs/v4_execution.json)、[加载资源](docs/resource_load_calibration.json)、[数字表](docs/NUMBERS.md) 和 [结果图](docs/figures/input_mask_baseline_v4.png) 随Git；weights/raw仅本机。
