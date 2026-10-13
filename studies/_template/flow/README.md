# flow/

可选 Study 阶段扩展，不能复制库默认链或填写空 hook。当前模板保留四个有专项职责的包，复用 `src/spec_mtp/` 的共享实现：

- collect：从 execute 的 raw 解码观测计算 CSV/Tracker。
- summarize：核验真实 token、接受/cache、来源/输入和 exact-match，失败拒绝成功。
- write：在库写 succeeded result 前再次核验证据。
- process：Run scope 直接返回，Study scope 只终验当前 index 的组合/seed/来源/证据，并同步完整性。

prepare/execute 使用默认阶段、recipe 与专项 builder/Algorithm，没有空壳包。`__init__.py` 仅导出，实现放 `run.py`/helper。`flow.study_phases: true` 启用加载；write 先 Study 后库，其余阶段先库后 Study。需要 prepare 构造前 hook 时才添加 before(ctx)。见 [Study 指南](../../README.md#3-阶段职责与成功条件)。
