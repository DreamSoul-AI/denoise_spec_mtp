# Qwen3-4B output-space count recheck — FP32 archive

精度标注：本 Study 已有模型实验全部使用 FP32，不能作为 BF16 证据。2026-10-15 起归档；新实验按 ESP Table 1 → Qwen3-4B BF16 五方法配对顺序执行。冻结的 PLAN、配置与执行证据保持原字节。


[PLAN](docs/PLAN.md) and [historical inventory](docs/history_inventory.json). Fixed26 prompts, matched input/output0/output1 plusAR; timing disabled. No new result before launch. Native source/defaults unchanged.

Archived failed activation: df8ee598dbef53b4 completed execute26/AR but failed collect entry export. Do not launch remaining v1 jobs or re-sign locks. Continue [v2](../output_space_4b_recheck_v2/README.md); old raw/source/config preserved.


FP32 收尾状态：[PR #7](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/7) 经 CI 已合 dev，merge8677376；main未操作。
