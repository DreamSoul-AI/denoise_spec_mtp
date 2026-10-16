# Tiny losslessness smoke

这是基于 RPipe Study/Experiment/Run 合同的可复用数值门，不是预训练模型或论文矩阵。当前声明保留历史交付 version `rpipe-v030-20261013-delivery`，复制隔离目录并改新 Study 名和 version 后再实测，不直接复跑已有 Run。

- 三个 Experiment：esp_static、esp_dynamic、ema_velocity；每个 seed=123，一个 Run。
- 随机 tiny LLaMA、四个 synthetic prompt、CPU/eager、32-token 预算、T=0、EOS 不停止、AR 对照开启；具体配置与精度边界见 [PLAN](<../../docs/研究计划 Denoising Speculative Decoding.md#legacy-studies-smoke-docs-plan>)。
- recipe 注册 Data/Model/eval Algorithm，默认 prepare/execute 执行；四个 Study hook 复用专项 collect、成功门和当前 index 终验，未复制 runner。
- 历史验收保留 CPU/CUDA tiny、旧新 token/轨迹、失败边界和安装证据，见 [报告](docs/STUDY_REPORT.md) 与 [NUMBERS](docs/NUMBERS.md)。这些证据对应各自提交/version，不自动证明未来代码。

按 [Study 指南](../README.md) 执行 make → launch → process/readout。迁移数值工具为 [validate_migration.py](validate_migration.py)；普通验证使用现有隔离 pytest/CLI 入口，临时输出放 `.tmp/`。CPU tiny 不下载真实模型。AR/alignment 的阶段合同由测试覆盖，不另造无研究问题的空 Study。

研究配方、模型权重语义、精度和停止规则不为迁移而调整；GPU 容量、解码恢复、并发和完整大模型矩阵不属于 smoke 的通过范围。
