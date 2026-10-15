# BC30四格完整补齐

已先登记[PLAN](PLAN.md)，四因素random0/1/2/content各完整480；原template全480成功和旧zero复用，不重跑。只有原资源assert改成同进程准入等待，方向control原文保持，CPU15项针对回归和Ruff通过。

random0/1均已全480并原生succeeded：τ分别1.495188134/1.464349086，81,425/81,356个提交token全argmax通过；完整来源与配对见[direction_partial_v3.json](../../qwen3_4b_bf16_directions/docs/direction_partial_v3.json)和[主报告](../../qwen3_4b_bf16_directions/docs/STUDY_REPORT.md)。random1完整后已组间让卡；量化限时窗口到期未启动，random2已恢复执行，content待接续。原队列自然结束和资源失败全部保留；本Study native process及四格均通过后才称补齐完成，整个目标保持active。

运行快照：random0新Run `2c3e7547a4f931a7`已完成220/480条，来源为本机`runs/2c3e7547a4f931a7/assets/direction_progress.json`。同一GPU进程PID61936在190条附近检测到外部GPU Python PID63780，准入输出`waiting`后自动`resumed`，Run没有失败或重启；随后继续超过220条。恢复状态来源为本机`.tmp/full-direction-resource-wait.json`，其中`status=admitted`、外部GPU Python列表为空、`initial=false`。加载后的准入排除自身模型占用，不将14GiB初始加载余量重复扣减。这是执行恢复证据，不是完整格或τ结果。

提交`e51b8b1`的远端验证全部通过：[PR CPU CI](https://github.com/DreamSoul-AI/denoising-speculative-decoding/actions/runs/38776456324)为502 passed、1 warning，push侧CPU CI和Branch flow亦通过。GPU全量未完成，PR22仍为draft；不以CPU通过替代四格原生数学门及Study终验。研究计划模板尚未收到，收到后用附加文档对齐，冻结PLAN与控制代码保持不变。

## 组间排班追加（最新用户指示）

random1完整结束后先让量化现有Q-only v3插跑一次，其原optimizer上限300秒；它终态并释放GPU后立即接random2/content。不在组中途停止，不改冻结数据、prompt或科学配置。为防原调度器抢先启动下一组，已验证父子PID/命令/创建时间后仅挂起调度父进程65876；random1子进程4196保持运行并已到380/480。原session23573及所有Run保留，未启动新队列。

量化现有排队进程59720对应`D:/GitHub/DreamSoul/quantization/.tmp/paroquant-reference/run_qonly_v3.py`，目标Run `ec12ed2e4d0633cc`；其脚本已设置单Run、optimizer300秒、14GiB显存/18GiB主存资源门且无自动重试。本次只为该既有任务释放组间窗口，不修改或另启动量化任务。当前尚未让卡，也未声称量化完成；恢复时核原父进程创建时间并resume同一调度器，避免PID复用或重叠队列。操作记录在本机`.tmp/sd-quantization-yield.json`；待实际让卡/终态后补证据。

实际让卡：random1于北京时间02:19:53原生succeeded，子进程4196随后退出，GPU可用显存约20GiB以上；原调度器仍挂起，random2没有加载。量化v3既有队列仍live，最近`pre_shared-*.json`的显存约21.5GiB空闲，主存仅约14.5GiB可用，低于其18GiB准入门，`ready=false`，尚未实际执行。其300秒是optimizer执行cap，不是已经开始计时的排队期限。不修改量化门、不终止别的CPU作业；该外部准入状态已如实报告，待量化终态且GPU释放后恢复原SD调度器。

最新排班裁定已执行：用户要求从02:25:01起最多再等5分钟，未启动则本窗口作废，先完整跑random2，再在content前重试。02:30:01截止时量化仍仅资源排队、无原生run-one子进程/启动标志；只挂起其未启动的CPU排队父进程59720，关闭启动竞争后立即resume原SD调度器65876。random2 Run `95aff7e5e533a947`的新子进程47012已于02:30:02进入原生流程，prepare通过，原session23573保持；随后只挂起调度父进程以保留下一组间窗口，random2本身保持运行且不被中途中断。没有新队列、没有科学配置/数据改动、没有杀进程或放宽资源门。量化没有获得实际执行结果，不将让卡写为量化成功；下一边界先恢复同一量化排队进程，再按最新裁定处理，全部本机状态在`.tmp/sd-quantization-yield.json`。

## CI安装版本漂移

后续[CI run38786263761](https://github.com/DreamSoul-AI/denoising-speculative-decoding/actions/runs/38786263761)实为75 failed/427 passed，而非先前502通过：`transformers>=4.45`解析为5.20.0，其缓存crop接口拒绝现有正数keep_len。结果文件`runtime.transformers`及本机实际安装均为5.12.1；本次把`pyproject.toml`安装版本固定到该已验收版本，不改`src/spec_mtp`、缓存算法、冻结Study、GPU依赖或任何Run。两Study科学source与RPipe冻结门复核通过，方向9项CPU回归通过；新完整CI待当前提交验证，不将旧失败标绿，也不宣称5.20兼容。该修复仅安装可复现性，不开展数值算子机理研究，random2继续原进程执行。
