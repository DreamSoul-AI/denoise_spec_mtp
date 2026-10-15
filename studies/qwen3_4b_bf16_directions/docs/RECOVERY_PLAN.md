# 外部GPU准入中断后的补齐协议

2026-10-16，原BC30队列的random0 Run `be910fe1fa042b28`在完成46条后遇到真实nvidia-smi外部Python PID65348。按冻结协议在下一prompt开始前停止；并非数学门或OOM失败。46条原始token/trace保留，原生argmax验证9,028个token通过，证据见[resource_interruption_v1.json](resource_interruption_v1.json)。该格没有有效全480τ，不将46条或旧四窗口拼成全量。

原队列已自动进入random1，不中断它，不另起GPU队列、不杀外部进程。先让原队列到终态，逐项核实哪些因素完整成功、哪些因资源中断失败。已成功template全480和旧zero全480绝不重跑。

队列退出后，仅对未完整成功的指定因素建立新recovery Study：换algorithm.config.version、新Run ID，完整480从头执行，不覆盖旧Run、不删数据、不宣称支持KV checkpoint恢复。不更改数据、prompt、模型、dtype、控制公式、seed、停止或正确性门。复用原direction_control.py原字节及全部科学/source/input引用，差异仅为Study路径、声明的失败因素和新version。原46条只作为保留的失败证据，不参与最终有效格的重复计数。

补跑前仍只看GPU实际驻留Python与可用显存，free≥14GiB后单队列round1串行；如果仍有外部占用，不启动第二队列，也不因CPU进程阻塞。新队列同样不自动重试失败格，后续根据真实终态再处理。

最终报告保留原Study的失败/终验结果，不将其改写成成功。每个指定方向只采纳唯一完整native成功Run：优先原成功格；只对原失败因素采用预先声明的补齐Run，不按τ挑选。补齐Study自身native process必须通过；组合验收逐因素核对480条、seed、参数、模型/runtime、原生argmax、科学源码与控制实现字节一致性。若任何方向仍缺失，整个方向目标仍不完成。零偏置继续明确复用原生输入零阶，不重新签收旧Run。

恢复会多产生失败前的真实计算工作量，报告单列，不作测速或性能数据。读出只在组合完整后给出最终六组矩阵与结论；PR合dev及远程分支删除仍待全部规定格通过，不因为补跑而缩小到已成功子集。
