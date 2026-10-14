# Qwen3-4B matched recheck v2 — FP32 archive

精度标注：本 Study 已有模型实验全部使用 FP32，不能作为 BF16 证据。2026-10-15 起归档；新实验按 ESP Table 1 → Qwen3-4B BF16 五方法配对顺序执行。冻结的 PLAN、配置与执行证据保持原字节。


[PLAN](docs/PLAN.md) freezes the same first26/configs, plus explicit failed-stage repair. Original output_space_4b_recheck/df8ee598dbef53b4 failed at collect because phase run export was a module. Full execute26 token/AR outputs were equal, but no native quality success claimed. Failed raw/locks preserved, new version/Run required. This v2 exports callable native phase entrypoints and changes no scientific src/defaults. No speed testing, push or merge.

当前[报告](docs/STUDY_REPORT.md)已完成原生四格与配对计数，计时禁用；新4条负结果及历史输入EMA控制见报告后续，原0.6B机理阶段归档暂停。
