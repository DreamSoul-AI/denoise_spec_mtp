# Qwen3-4B fixed input EMA control — FP32 archive

精度标注：本 Study 已有模型实验全部使用 FP32，不能作为 BF16 证据。2026-10-15 起归档；新实验按 ESP Table 1 → Qwen3-4B BF16 五方法配对顺序执行。冻结的 PLAN、配置与执行证据保持原字节。


[PLAN](docs/PLAN.md), same original two input sets; two new EMA-only native Runs. Previously measured output0/output1/AR reused, no timing or tuning.

[正式结果](docs/STUDY_REPORT.md)：first26零/一相对固定输入EMA仍增，新4条零阶持平、一阶增加但都不胜冻结均值；仅新增EMA两Run，旧output/AR复用。
