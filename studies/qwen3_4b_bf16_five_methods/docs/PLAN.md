# Qwen3-4B BF16 five-method paired comparison

状态：计划已写，尚未冻结、make或运行。前置ESP Table1四格全480、argmax与原生process已完成；PR #10经CI合dev（fafed614）。论文τ目标未达到，完整负结果保留。本Study不再使用8B，不恢复算子机理。

## 问题与固定范围

检验4B/BF16下输出零阶和一阶的接受收益，并在同一批480条SpecBench首轮prompt、同一设置下比较五方法加独立AR。不能用旧4B FP32或26条链式结果冒充本轮。

主预算BC30，另预先固定BC60复核；两者均用两个mask、naive动态树和重复剪枝（节点预算9/19），不按结果选预算。选择两mask是延续既有4B输出零/一阶定义，使第二mask保留显式速度外推；它不是8B Table1单mask主协议的新复现。所有五方法使用相同树/预算/长度/种子，不能给输出方法换成更窄单链。

| 方法 | 固定实现与参数 |
| --- | --- |
| ESP frozen mean | prompt embedding mean，update=false；用户指定基线，区别于论文updating mean |
| 输入零阶 | prompt mean初始化，embedding EMA λ=.1；直接复用ESP updating mean |
| 输入一阶 | mean_plus_gamma原配方：level=order0、λ=.1、β=.9999、γ=1、normalize=false、extrapolate_ema=false |
| 输出零阶 | final-normalized hidden，order=0，按r=mean_v norm(W_v)缩放；保留既有代理状态定义 |
| 输出一阶 | 同一hidden映射，order=1，已验证历史β=.9、代理历史β′=.99；沿用既有4B配方，不事后调参 |
| 独立AR | 同一模型/输入/seed/停止规则，仅执行一次480条，供两个预算全部方法离线配对 |

共11个Run：1个AR，5方法×2预算。Spec Run关闭重复内部AR；完整输出与独立AR逐token对比在统一阅读器完成，保留所有首分叉。没有额外teacher、warmup或速度基准。

## 模型、输入与精度

Qwen/Qwen3-4B，优先复用ModelScope既有检查点；冻结实际文件SHA、ModelScope可核验来源、model digest与实际tied-storage指针检查。不得用8B或未确认权重代替。权重、forward及输入mask为BF16，eager、默认归约、deterministic=false；不做FP32模型实验。复用原生内部计算：输出EMA/范数映射保留FP32状态，输入EMA保留其原生dtype，最终mask转模型BF16；明确记录，不能称所有内部算子均为BF16，不另开精度对照。

数据沿用Table1官方SpecBench固定480条及原顺序，skip=0/take=all、首轮、non-thinking chat template、max_prompt_len=40960，不截断/丢样本。用4B tokenizer生成并冻结prompt manifest，核对qid/category/顺序与文本来源；不能未经核验直接复制8B token IDs。T0、seed123（逐prompt 123+index）、max_new_tokens256、EOS停止、warmup=false；所有Run设置相同。

## 开跑前必须完成

1. 输出provider仍生成原k+1个深度代理状态，按[0]+tree.depths映射至实际root/候选owner；同深度兄弟共享同一已有代理预测。forward后仅真实root/accepted路径更新已验证hidden，bonus延后，拒绝分支不写历史；不增加forward，不改候选/树算法或默认配方。
2. 原生验收按实际配置的树规模核对owner数，按模型dtype的量化精度核对实际BF16 mask范数，保留非有限/零范数和篡改拒绝。提交token的对应forward argmax门不得放宽。
3. 回归覆盖多兄弟/多深度、动态剪枝、被接受的非首兄弟、EOS/预算裁剪、mask state不被代理污染、旧单链行为及实际BF16原生CLI验收；检查所有调用者、证据验证和文档。
4. 校验模型/数据、source pin及无测速适配器，完成来源manifest后再冻结本PLAN与recipe/配置。源码或输入变化必须新版本/新Run，已有成功数字不重跑或重签。

## 指标、正确性与停止规则

按qid和实际输入/模型/seed配对，逐prompt报告accepted（裁剪前）、committed/new_tokens、主model calls（prefill+decode）、pooled与prompt τ、独立AR exact和首分叉。对五方法所有两两对照分别报告accepted较高和calls较低的赢/平/输，另列相对frozen mean、updating mean及output1-output0；两个指标不强行合成单一胜负，不拿不同输出长度隐藏EOS影响。两个预算的正负/平局全部保留，单seed不声称总体优越或测速收益。

正确性门：全部实际提交token等于对应验证forward logits的argmax，包含prefill首token且覆盖输出全长；独立AR逐token一致率仅诊断，不阻止收齐矩阵，不触发BF16算子机理。来源/配置/计数/cache/owner/范数或argmax证据失败、OOM/非有限立即保留失败格并处理真实问题，不能切FP32、teacher纠正、删除反例或以局部成功替代全量。

## 排班、产物与验收

共用单张24GB GPU，一次只开一条round1/num-gpus1调度链，先独立AR，再BC30五方法、BC60五方法，组间确认进程退出。开跑前核对其他GPU任务，不能杀其他任务；无预热、无decode计时、无latency/throughput结论，原生计时字段仅零占位。

报告需包含每个Run真实状态、实际dtype/参数/输入与来源SHA、完整逐prompt赢平输和AR差异、argmax覆盖及失败边界；原始tokens/Run/权重/cache留本机。正常工作分支提交/推送、PR和合dev按长期授权执行，不合main、不强推、不删除数据/分支、不花钱。
