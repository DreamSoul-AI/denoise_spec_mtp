# BC30四格完整补齐

已先登记[PLAN](PLAN.md)，四因素random0/1/2/content各完整480；原template全480成功和旧zero复用，不重跑。只有原资源assert改成同进程准入等待，方向control原文保持，CPU15项针对回归和Ruff通过。

random0/1均已全480并原生succeeded：τ分别1.495188134/1.464349086，81,425/81,356个提交token全argmax通过；完整来源与配对见[direction_partial_v3.json](../../qwen3_4b_bf16_directions/docs/direction_partial_v3.json)和[主报告](../../qwen3_4b_bf16_directions/docs/STUDY_REPORT.md)。random1完整后按用户要求组间让卡，random2/content尚未启动。原队列自然结束和资源失败全部保留；本Study native process及四格均通过后才称补齐完成，整个目标保持active。

运行快照：random0新Run `2c3e7547a4f931a7`已完成220/480条，来源为本机`runs/2c3e7547a4f931a7/assets/direction_progress.json`。同一GPU进程PID61936在190条附近检测到外部GPU Python PID63780，准入输出`waiting`后自动`resumed`，Run没有失败或重启；随后继续超过220条。恢复状态来源为本机`.tmp/full-direction-resource-wait.json`，其中`status=admitted`、外部GPU Python列表为空、`initial=false`。加载后的准入排除自身模型占用，不将14GiB初始加载余量重复扣减。这是执行恢复证据，不是完整格或τ结果。

提交`e51b8b1`的远端验证全部通过：[PR CPU CI](https://github.com/DreamSoul-AI/denoising-speculative-decoding/actions/runs/38776456324)为502 passed、1 warning，push侧CPU CI和Branch flow亦通过。GPU全量未完成，PR22仍为draft；不以CPU通过替代四格原生数学门及Study终验。研究计划模板尚未收到，收到后用附加文档对齐，冻结PLAN与控制代码保持不变。

## 组间排班追加（最新用户指示）

random1完整结束后先让量化现有Q-only v3插跑一次，其原optimizer上限300秒；它终态并释放GPU后立即接random2/content。不在组中途停止，不改冻结数据、prompt或科学配置。为防原调度器抢先启动下一组，已验证父子PID/命令/创建时间后仅挂起调度父进程65876；random1子进程4196保持运行并已到380/480。原session23573及所有Run保留，未启动新队列。

量化现有排队进程59720对应`D:/GitHub/DreamSoul/quantization/.tmp/paroquant-reference/run_qonly_v3.py`，目标Run `ec12ed2e4d0633cc`；其脚本已设置单Run、optimizer300秒、14GiB显存/18GiB主存资源门且无自动重试。本次只为该既有任务释放组间窗口，不修改或另启动量化任务。当前尚未让卡，也未声称量化完成；恢复时核原父进程创建时间并resume同一调度器，避免PID复用或重叠队列。操作记录在本机`.tmp/sd-quantization-yield.json`；待实际让卡/终态后补证据。

实际让卡：random1于北京时间02:19:53原生succeeded，子进程4196随后退出，GPU可用显存约20GiB以上；原调度器仍挂起，random2没有加载。量化v3既有队列仍live，最近`pre_shared-*.json`的显存约21.5GiB空闲，主存仅约14.5GiB可用，低于其18GiB准入门，`ready=false`，尚未实际执行。其300秒是optimizer执行cap，不是已经开始计时的排队期限。不修改量化门、不终止别的CPU作业；该外部准入状态已如实报告，待量化终态且GPU释放后恢复原SD调度器。
