# Qwen3-4B output-space count recheck — FP32 archive

精度标注：本 Study 已有模型实验全部使用 FP32，不能作为 BF16 证据。2026-10-15 起归档；新实验按 ESP Table 1 → Qwen3-4B BF16 五方法配对顺序执行。冻结的 PLAN、配置与执行证据保持原字节。


[PLAN](docs/PLAN.md) and [historical inventory](docs/history_inventory.json). Fixed4 prompts, matched input/output0/output1 plusAR; timing disabled. No new result before launch. Native source/defaults unchanged.

当前[报告](docs/STUDY_REPORT.md)已完成原生四格与配对计数，计时禁用；新4条负结果及历史输入EMA控制见报告后续，原0.6B机理阶段归档暂停。


FP32 收尾状态：[PR #7](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/7) 经 CI 已合 dev，merge8677376；main未操作。
