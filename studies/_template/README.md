# 新 Study 模板

对照 [Study 使用指南](../README.md)，复制此目录到 `studies/<name>/`，不要直接运行 `_template`。

1. 改 `study`、experiment 名称和新的 `algorithm.config.version`，核对基底 → fixed → axes/seed 的完整配置。
2. 写 [PLAN](<../../docs/研究计划 Denoising Speculative Decoding.md#legacy-studies--template-docs-plan>)：问题、对照、因素/seed、精度/backend、数据/停止规则、硬门、执行授权与排班。
3. 保留已有 recipe 和四个有职责的 [flow 扩展](flow/README.md)；没有本轮专用建构时不增加 [structure](structure/README.md) 包。
4. 先做隔离 CPU tiny 与失败边界，真实模型按计划做同设备数值前置门，再决定是否扩大矩阵。串行校准后才能增加独立 Run 并发。
5. 使用 `python -m spec_mtp make/launch/process/status/logs/report`；按 [报告模板](docs/STUDY_REPORT.md)写结论与真实图，NUMBERS 只提供数字。

当前 YAML 只是既有 Qwen3-0.6B / SpecBench first26 / frozen_mean / seed=123 的示例配方，没有 axes，因此展开为一个 Experiment、一个 Run。它不是本次新实验或已验收 baseline；不要自动复制温度、dtype 或预算到另一项研究。`fixed` 保留已确认配方，基底只给结构默认，避免误把基底当作最终 Run。

注册不解码或下载。`prepare_shared: false` 仅跳过 torchvision make 预构造，Run prepare 仍填 `shared/data` 与 `shared/model`。正式研究建议启用 `freeze: true`；ModelScope 与省略 origin 的合同见 [layout](../../docs/layout.md)。

新Study在项目唯一中英文计划增加章节并冻结Git commit/blob引用；不复制或创建独立PLAN.md。
