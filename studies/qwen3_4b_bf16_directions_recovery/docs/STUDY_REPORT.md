# BC30四格完整补齐

已先登记[PLAN](PLAN.md)，四因素random0/1/2/content各完整480；原template全480成功和旧zero复用，不重跑。只有原资源assert改成同进程准入等待，方向control原文保持，CPU15项针对回归和Ruff通过。

当前尚未产出新完整格，结果随后并入[主报告](../../qwen3_4b_bf16_directions/docs/STUDY_REPORT.md)。原队列自然结束和资源失败全部保留；本Study native process及四格均通过后才称补齐完成，整个目标保持active。

运行快照：random0新Run `2c3e7547a4f931a7`已完成220/480条，来源为本机`runs/2c3e7547a4f931a7/assets/direction_progress.json`。同一GPU进程PID61936在190条附近检测到外部GPU Python PID63780，准入输出`waiting`后自动`resumed`，Run没有失败或重启；随后继续超过220条。恢复状态来源为本机`.tmp/full-direction-resource-wait.json`，其中`status=admitted`、外部GPU Python列表为空、`initial=false`。加载后的准入排除自身模型占用，不将14GiB初始加载余量重复扣减。这是执行恢复证据，不是完整格或τ结果。

提交`e51b8b1`的远端验证全部通过：[PR CPU CI](https://github.com/DreamSoul-AI/denoising-speculative-decoding/actions/runs/38776456324)为502 passed、1 warning，push侧CPU CI和Branch flow亦通过。GPU全量未完成，PR22仍为draft；不以CPU通过替代四格原生数学门及Study终验。研究计划模板尚未收到，收到后用附加文档对齐，冻结PLAN与控制代码保持不变。
