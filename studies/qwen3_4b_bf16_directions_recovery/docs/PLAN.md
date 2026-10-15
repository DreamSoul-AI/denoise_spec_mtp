# BC30全480资源补齐计划

2026-10-16，原单队列已自然结束，无运行任务被中断。原template全480成功；random0/1/2分别在46/50/9条遇真实GPU外部Python而终止，content在加载前未获准入，均未产生有效全480τ。原Run、失败result和partial token/argmax全部保留。

本Study仅补四个未完整因素，全部480从头跑，新version/Run，不能把partial拼成全量。不重跑成功template或旧zero，不修改原Study或失败记录。模型、数据、prompt、T0、BF16/eager、BC30双mask、动态树、seed123+index、max256/EOS、mean/方向/EMA规则与[原冻结协议](../../qwen3_4b_bf16_directions/docs/PLAN.md)完全相同；同范数随机0/1/2是固定方向，content是原后缀初始化后native EMA，内容范数不额外匹配。

唯一执行差异是资源控制：原实现在发现外部GPU进程时直接失败，重复浪费完整prompt。新版本加载前及每个prompt开始前仅查询真实nvidia-smi，满足原14GiB初始空闲及无外部GPU Python条件后执行；不满足则本进程sleep5秒后再查，保留当前Run、模型和已完成prompt，不重启、不做GPU前向、不枚举CPU进程、不抢占或杀其他作业。等待状态写本机`.tmp/full-direction-resource-wait.json`。睡眠不进入测速，decoder模块计时仍为常量。

只在prompt边界等待，不宣称KV/checkpoint恢复；OOM、来源或数学门错误仍原样失败，不自动重试。单队列round1，原队列已确认terminal exit1后才允许启动本队列。当前GPU任务不被文档或后续研究计划模板对齐打断；模板补全使用附加文档，不改已冻结执行PLAN字节。

科学包56文件、旧输入/权重合同及source_refs原字节保持；`control()`完整方向公式与原Study AST/字节保持，资源等待helper和两个调用点是已披露的新Study来源差异。开跑前CPU回归验证不满足准入会等且恢复、不把CPU进程当GPU、控制函数一致，并运行既有tiny BF16控制门。

四格各完整480、native Run和本Study process通过才算补齐成功；原Study保留资源失败终验，不假装其通过。最终跨Study只选原template成功格和本Study四个预定因素，zero引用旧input_zero；每因素只有一个完整有效Run，不按τ选结果。组合验收逐项核对数据/模型/runtime/参数/seed、480条全argmax和原生来源，任何一格缺失则目标不完成。全量报告输出三种τ、相对template及原五方法的accepted/calls/τ配对胜平负，并保留AR诊断、输出长度和资源浪费工作量。

BC60仍等BC30完整后按实际token/forward工作量决定；8B/HF第三方不再推进，新方法/调prompt/测速/算子机理均不做。结果主题提交推工作分支，PR22完整后ready/合dev/删远程分支，不合main、不强推、不删本地数据、不弹窗。
