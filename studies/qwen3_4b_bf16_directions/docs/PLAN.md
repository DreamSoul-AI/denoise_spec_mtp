# 固定480条BC30方向对照

2026-10-16，接续Enmao监督指示：四窗口不足以回答方向是否特殊，先完成BC30全480，再按实际资源工作量决定BC60。只比较指定方向控制，不发明新方法，不改变prompt或主实验数据，不测速。

## 一、固定条件

使用`qwen3_4b_bf16_five_methods`已验收的480条SpecBench，顺序、首轮non-thinking模板、input_ids、EOS、seed123+index、max_new_tokens256完全相同。ModelScope Qwen3-4B BF16/eager，T0、双mask、动态树剪枝、BC30/draft budget9，level为原输入updating mean、λ0.1、γ1、normalize=false、extrapolate_ema=false。模型/source/输入内容校验后才forward。8B、测速、算子机理和新prompt筛选不在本轮。

## 二、六组与既有方法的关系

| 组 | 完整解码定义 | 执行 |
| --- | --- | --- |
| template | v固定为原prompt e2−e1，m_i=updating mean+i*v，每次提交只更新mean，v始终不变 | 新完整480 |
| random0/1/2 | CPU独立Generator种子0/1/2采样标准正态方向，FP32归一至同prompt e2−e1范数再转BF16；每次提交只更新mean，v始终不变 | 三个新完整480 |
| zero | v恒零，完全等价于已有输入零阶updating mean，不是frozen mean | 复用已验收30/input_zero的480条，不重跑 |
| content | 原输入一阶β0.9999的初始化从原序列首个user内容token起的后缀计算，保留完整prompt mean；随后按原生EMA更新v及mean | 新完整480 |

template与随机组是严格固定偏置，和四窗口干预的读出方向定义一致；不能用已有原生input_first（β0.9999且有更新）冒充template。content沿用先前控制定义：后缀包括原末尾模板，不改模型输入，不另行范数匹配。其余mean/anchor/树/cache/验证/停止语义由原生decoder保留。

四窗口原生input_first与template接受数相同不意味着全480相同；全量报告明确列template对原input_first的配对，检验差异。原五方法和共享AR全部复用旧正式结果，保留原source_digest；新Study的源码摘要会因已迁入第三方参考文件而不同，核对科学decoder/provider/模型文件逐字节相同，不重签旧结果。

## 三、指标与停止

主τ=Σdecode committed/Σdecode_calls，另报逐promptτ均值、category pooled等权均值；accepted包含预算/EOS裁剪前接受数，主calls=prefill+decode。逐question_id报告各组相对template的accepted、calls和τ胜/平/负；另列与旧五方法的全部配对，输出长度和AR首分叉并列，不声称同输出测速收益。

硬门：每个提交token等于该次验证前向正确owner logits的argmax，全覆盖/hash/owner链由原生validation核验。独立AR仅复用旧参考作诊断，不新增AR GPU、不作失败门。各新格完整480并原生Run和Study process通过后才能称完成；pending不补零、不当平局。科学门失败、来源不符、OOM均保留新Run失败，不自动重试或修prompt。

## 四、执行与资源

走原生SpecMTP/RPipe make/launch，Study专用provider作用域只替换指定方向并复用原native untimed输入合同。五个新增Run单队列`--round 1`串行，禁止第二队列。加载前只看GPU0 nvidia-smi实际驻留外部Python与空闲显存≥14GiB，各prompt再次检查驻留作业；不读取CPU进程/脚本SHA，不抢占不杀进程。外部实验出现则该格保留停止状态，GPU释放后用新version/Run继续，不覆写失败。

每格写原始token/trace/argmax和方向初值标量证据，完整Run/model/cache留本机。执行前提交冻结声明、Study代码与输入来源manifest。CPU测试覆盖固定v跨提交不漂移、mean与零阶完全一致、随机同范数/种子、content保留完整mean及原生tiny BF16硬门。没有GPU测速计时；只记录总forward/token工作量供BC60决策，未测墙钟不得填性能数。

首轮只声明BC30五个新Run，BC60在其完成后依据资源负担与信息量再写补充冻结计划，不提前暗中筛选优胜方向。阶段报告持续列实际状态、来源与局限；主题commit/push、PR合dev，合后删远程分支。保留全部本地分支/数据，不合main、不强推、不弹窗。
