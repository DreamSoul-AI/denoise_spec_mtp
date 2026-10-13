# flow/

这些目录是可选的 Study 扩展位置，不是库默认阶段的副本。没有 hook 时仍执行 `src/rpipe/flow/` 的默认链，不必填写空函数。

SpecMTP 的专项职责：

- `collect/run.py`：raw 解码观测转换为 CSV 与 Tracker 指标
- `summarize/run.py`：exact-match 和证据成功门
- `write/run.py`：result 定稿前跑 `spec_mtp.flow.checks.run_gate`（`exact_match_rate` 必须是 1）
- `process/run.py`：只在 `ctx.scope == 'study'` 时跑 `study_gate`

`__init__.py` 只导出，不写实现。在 `study.yaml` 启用 `flow.study_phases: true`。helper 放独立模块。完整合同见 RPipe `docs/code/flow.md` §14。
