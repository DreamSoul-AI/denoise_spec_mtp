# HF第三方ESP原码验收报告

当前状态：固定数据五方法加AR已完成11/11，指定四组方向对照已完成；PR20已合dev并删除对应远程分支。
最新发现：非官方ESP原码在8B BF16固定q121的BC10/30/60均首token失败，argmax margin为40.75/33.5/33.25，见[真实审计JSON](esp-third-party-audit-2026-10-15.json)。
执行范围：三预算共6次真实forward，在错误提交前停止；没有改prompt、第三方source、默认配方或测速。
下一步：本报告及原码/测试经PR合dev，随后删除该远程工作分支；不另立新方法或恢复算子排查。
阻塞边界：第三方数学门失败，不能给有效τ，未跑其全480；原作者官方来源仍未核验到，不冒称完成论文数值复现。

本报告沿用10月15日研究归档文件名；最后整理时间为北京时间2026-10-16凌晨（UTC仍为10月15日）。

## 一、来源、原字节和执行入口

来源为HF **dataset** [Harshvardhan-Mestha/esp-reproduction-artifacts](https://huggingface.co/datasets/Harshvardhan-Mestha/esp-reproduction-artifacts)，固定commit [`ad76f8da29f3bfc7faa20488193c6aa83a9f708c`](https://huggingface.co/datasets/Harshvardhan-Mestha/esp-reproduction-artifacts/tree/ad76f8da29f3bfc7faa20488193c6aa83a9f708c)。这是用户允许尝试的**第三方复现，不是ESP论文作者官方实现**。原作者来源核查结论见[此前报告](esp-official-code-reproduction-2026-10-15.md)。

全部四个code/入口文件原字节迁入[`src/spec_mtp/structure/algorithm/reference/esp_reproduction_artifacts/upstream/code/`](../../src/spec_mtp/structure/algorithm/reference/esp_reproduction_artifacts/upstream/code/esp_v6.py)，同时保留README和三个结果JSON；共八个文件逐一SHA绑定在[ORIGIN.json](../../src/spec_mtp/structure/algorithm/reference/esp_reproduction_artifacts/ORIGIN.json)。未迁入的非执行海报、logbook等列于同一manifest，完整Git clone保留在本机`.tmp/esp-third-party-upstream`。不是整个HF资产库的完整镜像。上游未附LICENSE，许可状态保留Unverified，不补写授权声明。

原`run.sh`会安装依赖，原runner硬编码FP16、10条示例prompt、BC60双mask并测速。为遵守本次BF16、固定数据、单mask及不测速要求，**未运行该shell或CLI主函数**；外部工具调用未改字节的原生`ESPDecoder.generate_esp` API，不改其候选或提交逻辑。模块作用域的时钟返回常量，计时/TPS不输出为实验结果，不更换全局时钟。故本次是原算法API在共同外部设定下的验收尝试，不能称原CLI无适配地完整复现Table1。

## 二、冻结设置和真实执行

预检先于GPU运行写入[THIRD_PARTY_PLAN](<../研究计划 Denoising Speculative Decoding.md#legacy-studies-esp-table1-bf16-full-argmax-docs-third-party-plan>)，工具与协议冻结于`237db03`（原码与验收主体为`f07f57d`）。复现命令：

```text
python tools/audit_esp_third_party.py --study studies/esp_table1_bf16_full_argmax --model-cache D:/models/Qwen3-8B --out .tmp/esp-third-party-v1
```

- 模型：已有ModelScope Qwen/Qwen3-8B快照，BF16、CUDA/eager、T0贪心、λ=0.1 mean更新；8B仅用于此Table1尝试。
- 输入：原SpecBench数据SHA及480条冻结manifest，先取原顺序第一条q121（38 tokens）；重新渲染只用于核对，实际输入与manifest逐token相同，不改内容、模板、顺序或截断来调结果。
- 三预算串行：BC10/1、30/1、60/1，原API的max_new_tokens=256、seed123不变，每格上限24次forward。只要数学门失败就不进入该算法全480，不自动修算法或重试。
- 准入：加载前实际空闲21,489MiB≥20,480MiB，无其他GPU驻留Python；预算间再核对实际GPU进程。没有检查CPU进程、抢占、杀进程或另起等待队列。加载后的显存门不重复扣除本模型。

全部设置、模型文件核验manifest SHA、数据/输入/工具/计划SHA、运行环境、实际前向长度和准入记录均见[审计JSON](esp-third-party-audit-2026-10-15.json)。环境为torch 2.11.0+cu130、RTX5090 D v2，模型浮点参数全部为torch.bfloat16。原文件在执行前后均重新通过SHA核验。没有新增FP32或FP16模型运行。

## 三、数学门和失败结果

硬门只核对**同一次verification forward**的正确前缀父行argmax，不使用独立AR作失败门。第一个拟提交token应取prompt末行37；其后应取对应已提交前驱的位置。不能用draft自身行或包含未提交候选的末mask行代替。审计在原函数返回、实际追加token之前拒绝错误提交，因此没有把错token先写入再宣称自检通过。

| BC/mask | 固定prompt | 完成forward | 检查位置 | 首个argmax−chosen logit | 数学门 | 有效τ / 论文差值 |
| --- | --- | --- | --- | --- | --- | --- |
| 10/1 | q121 | 2（proposal+verification） | 输出0、父行37 | 40.75 | 失败，追加前停止 | 不适用 |
| 30/1 | q121 | 2（proposal+verification） | 输出0、父行37 | 33.5 | 失败，追加前停止 | 不适用 / 对1.63不可计算 |
| 60/1 | q121 | 2（proposal+verification） | 输出0、父行37 | 33.25 | 失败，追加前停止 | 不适用 / 对1.74不可计算 |

来源：[审计JSON](esp-third-party-audit-2026-10-15.json)的`rows[]`、`first_rejection`、`forward_trace`。三个预算的`valid_tau`均为null；不是τ=0。三次拟提交首token均失败，共6次实际forward、3次检查；没有执行第三方全480，也没有可报告的三种τ聚合或AR一致率。私有token选择证据保留在`.tmp/esp-third-party-v1/private_decisions.json`，公开文件绑定其SHA `e4fa9934c19dbf75e1b5d87ee241c689ed902c4aada480fd1e32703e937cd3ab`，不上传完整token、权重或缓存。

这不是BF16与独立AR因形状不同而分叉：失败比较来自同一次验证前向的实际前缀父行。未进行归约、attention、linear或RMSNorm算子排查。

## 四、源码层解释与论文可比性

已确认的源码规则，见原[`verify_single_pass`及`generate_esp`](../../src/spec_mtp/structure/algorithm/reference/esp_reproduction_artifacts/upstream/code/esp_v6.py)：

1. 验证把prompt、全部候选、末mask拼接；用draft自身位置的argmax与该draft比较，命中数与最后命中索引单独累计。
2. 生成遇到任意命中，就追加直到最后命中索引的全部draft，包括前面未命中的候选；bonus取末mask位置。没有命中也取该末mask预测。两种路径都没有逐一核对真正已提交前缀的父行。
3. 候选是flat top-k，而非论文动态树加剪枝；draft softmax温度为1（top-k，不是随机抽样），原类无KV复用，也没有与主实验相同的EOS停止逻辑。声明的model calls只累计verification，proposal还另有forward，因此本工具记录实际前向，不接受其调用计数直接当同口径τ。

CPU回归直接调用未修改验证器，构造“自身位置命中但正确父行不命中”的例子，证明该规则不能推出数学无损。它说明结构性风险；真实三格的审计没有保存原`n_acc/accepted_idx`返回值，**不据此断言真实失败究竟走了哪条追加分支**。首token失败本身由同次logits直接确认，足以拒绝有效τ。未改源码去修复，也不把差异归因于数值算子。

上游仓库自带的Qwen3-8B v6数字：BC30 `avg_tau=2.906445541930953`，BC60双mask partial `avg_tau=3.689`、只完成6条。来源为[原结果JSON](../../src/spec_mtp/structure/algorithm/reference/esp_reproduction_artifacts/upstream/results/esp_v6_results.json)的`qwen3_8b`。它们是上游外部记录，不是本机测量；FP16/示例prompt/计数及数学门均与本任务不等价，不计算相对论文的复现差值，也不将其大于目标当作成功。上游对论文BC30目标的文字记录不沿用，本任务仍以1.63/1.74为准。

此前本仓自实现全480的有效pooled τ仍为BC30 **1.563378**（差−0.066622）、BC60单mask **1.647301**（差−0.092699），数学门全过，论文数值未复现。来源：[原protocol_evidence_v1.json](../../studies/esp_table1_bf16_full_argmax/docs/protocol_evidence_v1.json)；它不是作者或第三方原码结果，不能借本次尝试更名。

## 五、目标交付与后续边界

固定主实验已经完成：五方法×两个BC×480及共享AR，共11/11原生Run通过，809,118个Spec提交token自检通过；所有τ、逐prompt胜平负和AR诊断见[中文阶段报告](sd-stage-report-2026-10-15.md)。本轮没有重跑这些格子。

指定模板方向对照已经完成：原e2−e1、三个种子同范数随机、零偏置、内容初始化均在固定四窗口上执行；原方向对零为3胜0平1负，随机0为1胜2平1负，随机1/2与内容初始化各0胜3平1负。q241随机0也能提升，否定这批样本“唯有e2−e1有效”的强命题；内容初始化未做范数匹配，不能只按方向归因。来源：[方向读出JSON](4b-direction-controls-readout-2026-10-15.json)和[局部因果/边界报告](4b-mask-window-2026-10-15.md)第十至十二节。条件小样本不能替代主实验480条全量排名。

本次HF尝试按冻结停止规则完成，阻塞原因是第三方原算法未通过数学门。继续全480或修复第三方算法不属于当前交付；不启动新方法、新prompt筛选或算子机理。后续可由Enmao指定可靠作者实现/新的既定baseline来源，再另冻结协议。原作者来源缺口、论文τ缺口都保留，不宣称解决。

验证：第三方四项加窗口十一项，共15项CPU回归通过，Ruff及56文件mypy通过；真实GPU仅上述三格预检。授权依据为Enmao本会话长期授权正常提交、PR/dev流程及合后远程分支删除，无提问弹窗。PR20 CI通过并合dev，已删远程`feature/sd-stage-report`；此前`feature/output-space-prerequisite`也已删除，实际清单见[分支报告](remote-branch-cleanup-2026-10-15.md)。本次PR最终集成与删除证据在该PR说明和本机验收记录追加，避免为记录自身删除无限新开PR；本地分支与全部数据保留。
