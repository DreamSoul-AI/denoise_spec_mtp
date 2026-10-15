# 4B 早期同前缀双向mask替换

2026-10-15，按Enmao追加指令直接做GPU因果验证，不再扩CPU筛选。已完成的早期模板16格保留，不重签。本次补输出一阶，并从原输入一阶路径执行反向替换，科学src和配方不改。

## 一、固定设计

两个origin分批串行：原BC30输出零阶Run、原BC30输入一阶Run。各固定q121/R1、q401/R0、q241/R1、q161/R2，实际必须存在该root；不按本轮结果换位置。每origin每prompt三格：同历史下的输出零阶、输入一阶、输出一阶，仅替换当前验证块各owner的mask构造，prefix/cache/tree/位置/注意力不改。输入使用原β=.9999/λ=.1/γ=1；输出使用原β=.9/β′=.99与范数映射。

输出origin复用原输出零阶capture，并行只读更新输出一阶shadow。输入origin重建原输入一阶路径，以原生last_hidden_only观察接口收集已验证prompt/committed hidden，按相同真实历史更新两种输出shadow；proxy只取上一个真实验证块最深owner的mask hidden。shadow不写回生成状态、不做独立AR或teacher前向。

每格当前owner argmax及当前接受路径必须与origin原控制相同；使用该格当前mask logits建下一树，执行一个下一验证块，未来mask保持origin原规则（输入origin继续原输入mask，输出origin继续原输出零阶mask）。每个提交选择必须等于对应验证前向argmax。native控制mask逐元素等于重建块的实际mask，控制续接旧Run，来源和预算均为硬门。

## 二、指标与边界

每origin12格，上限64次总forward。记录目标排名、下一树宽、实际下一块接受数、当前argmax/本地数学自检及旧轨迹诊断。CPU读出默认相对输出零阶；报告另外逐origin明确其native控制：输出origin为zero，输入origin为input_first。保留所有正负与无收益结果，不将两个origin不同真实prefix和树混成同一对照。

输出origin的下一root固定2/1/3/4；输入origin固定2/1/3/3，q161两条原路径不同，不能宣称跨origin位置完全相同。选点来自前批已有结果，有条件选择偏差。若接受数随构造改变，支持该固定状态下的局部因果作用；不能据此分配全480差距的因果份额。没有改prefill本体，不将root0 decode称作prefill替换。

## 三、执行与停止

使用`--template-control --early-template --reciprocal`，输入origin另加`--input-origin`，两个新目录顺次执行，只有一个串行命令，无后台/重叠队列。准入只查GPU0实际nvidia-smi计算进程和空闲显存，初始≥14GiB、无其他GPU驻留Python即运行；CPU进程不检查、不登记SHA。未知GPU Python、容量不足则保留deferred，不抢占或杀外部作业。

仅魔搭缓存Qwen3-4B BF16/T0/eager/default，不跑8B、FP32模型、测速或算子机理。控制、数学门、来源、非有限、OOM、预算失败均保留并停止，不自动重跑。工具/协议/model/source/raw/private logits绑定SHA；完整权重/cache/token/logits留本机，标量与报告按主题提交、推工作分支、PR合dev；不合main、不强推、不删数据和分支。
