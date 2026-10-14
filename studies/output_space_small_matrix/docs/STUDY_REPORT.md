# Study Report: output_space_small_matrix

2026-10-14：按预先固定的q172–q174完成四个新Run（每Run三个prompt），执行与来源/证据/正确性/Study完整性门均通过。三种投机方法的9份输出和独立AR的3份输出逐token相同，没有context-limit缩短。结果是小样本混合观察：一阶在q173比零阶多接受2个draft，但仍少于输入链；q174两输出方法各胜输入链1个。不能把q171负结果或这三条新观察直接推广。

## 固定协议与原始证据

[PLAN](PLAN.md)在执行前声明选择、预算、停止门和匹配前缀分析；[prompt manifest](prompts_manifest.json)冻结数据hash、qid、文本及独立tokenizer渲染后的输入IDs。[执行原始精选](execution_v1.json)、[原生NUMBERS](NUMBERS.md)、[轨迹诊断](trajectory_diagnosis.json)保存所有结果而非只保留最好的prompt。

模型同一ModelScope Qwen3-0.6B、实际tied权重、FP32/eager/CUDA、非thinking、T0、100-token/EOS、seed123。prompt窗口translation skip11/take3，输入长度39/69/32；原生per-prompt生成器seed123/124/125，T0不依赖抽样。匹配unpruned static[1,1]链、k2/BC9、原输入均值/输出0/1配方；beta=.9、beta_prime=.99、gamma/rho=1无改动。源码670c744e0535dcad及数据/modelhash均与前置阶段绑定一致。不是旧BC30/[14]的跨协议比较。

## 每prompt结果

| qid | case | new tokens | accepted所有深度 | depth1 | depth2 | decode calls | tau |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 172 | frozen_mean_chain | 14 | 1 | 1 | 0 | 12 | 1.083333 |
| 172 | output_order0 | 14 | 1 | 1 | 0 | 12 | 1.083333 |
| 172 | output_order1 | 14 | 1 | 1 | 0 | 12 | 1.083333 |
| 173 | frozen_mean_chain | 33 | 5 | 4 | 1 | 27 | 1.185185 |
| 173 | output_order0 | 33 | 1 | 1 | 0 | 31 | 1.032258 |
| 173 | output_order1 | 33 | 3 | 3 | 0 | 29 | 1.103448 |
| 174 | frozen_mean_chain | 13 | 0 | 0 | 0 | 12 | 1.0 |
| 174 | output_order0 | 13 | 1 | 1 | 0 | 11 | 1.090909 |
| 174 | output_order1 | 13 | 1 | 1 | 0 | 11 | 1.090909 |

独立AR对应生成14/33/13 token。三个prompt各先prefill提交1token，合计new60、committed57。汇总accepted为输入链6、零阶3、一阶5，decode calls为51/54/52；pooled tau按57除各自calls计算，不平均不同长度prompt的tau。输入链唯一depth2接受发生在q173（1个），两输出depth2均0。接受数沿既有截断前口径，不等于额外新token；没有BLEU或参考译文质量结论，只验证与当前目标模型AR相同。

各方法单Run/单seed，n=3是相邻prompt数量，并非三个seed重复。NUMBERS里的std=0来自单Run。样本数量和选择不足以作显著性、稳定收益或跨域泛化结论；未做性能排名。

![三prompt匹配链接受计数](figures/acceptance_v1.png)

图源execution_v1.json，每个柱是一prompt/一方法的原始all-depth接受计数。重画 `python studies/output_space_small_matrix/plot_results.py`，不执行Run。

## 匹配前缀轨迹诊断

分析按同qid、同absolute root_position对齐，并验证完整AR输入/output前缀相同及cache_before相同；不同方法的第i次forward往往不是同一个前缀，因此不按step编号匹配。可重建脚本 [analyze_trajectories.py](../analyze_trajectories.py) 从正式执行JSON复算并要求与既存诊断逐项一致，没有新增模型forward。

- q172：三方法accepted都1，但输入与输出匹配的11个根位置中有2处接受长度不同：root41输入1/输出0，root43输入0/输出1。一致汇总并不意味着同一位置命中。零阶与一阶的12个根及完整验证/提交/KV轨迹一致。
- q173：零阶与一阶29个共同根中只有root94与97接受长度不同，均为零阶0/一阶1。每次一阶连续提交2token、零阶仅1，后者还需要root95/98两次额外decode，所以实际calls31→29且总accepted1→3。这个观测定位了调用差异，未证明由EMA速度方向或代理hidden校正直接造成。两方法所有29个共同根的owner差异范数统计不同。
- q173：输入链在root79/83/88/92分别接受1/2/1/1，输出一阶均0；一阶又在root94/97各接受1而输入均0。不同方法命中不同区间，输入最终5、一阶3，不能只展示一阶胜的两个区间。
- q174：共同root42输入0/输出1；输出提交句号token13及bonus EOS151645并终止，输入需要下一root43取EOS。因而输出11calls、输入12calls；收益集中在该句末位置，不能宣称整段机制优势。

完整未共同访问根列表、停止标志、提交token与两两比较都在trajectory_diagnosis.json保留。保存数据缺草稿logits、完整mask向量及同位proxy/exact hidden配对，故无法计算候选概率margin/hidden误差或作机制归因。范数差异是统计量差异，不声称证明完整向量关系。

## Run与资源

| case | Run ID | est秒 | 实际Flow秒 |
| --- | --- | ---: | ---: |
| frozen_mean_chain | 4f87c26584a1a6a1 | 3 | 21.056 |
| output_order0 | 8abcc1a22086bcc7 | 3 | 21.757 |
| output_order1 | 824b1fe0b8578349 | 3 | 20.838 |
| AR | 632786e445329297 | 3 | 19.321 |

使用原生make→launch→process→report、round1单GPU串行，权重11文件hash复核且同snapshot通过cache junction复用，Run保持local_files_only。启动前可用主存15.19GiB、GPU21GiB以上；既有同模型串行容量校准复用而非冒充新测量。launch总wall 102.159秒（含初始化/hash/Study终验），make每格3秒/26.5GiB为启发式，不是实测。0.5秒采样进程树RSS峰 6710669312 bytes、线程峰 49、GPU全局memory.used峰 5267 MiB、系统可用主存最低 11050160128 bytes。包含背景占用且可能漏短峰，不等于CUDA allocator峰；I/O计数不等于物理吞吐。OMP/MKL1，无本任务竞争实验。完整runtime/TF32及采样边界见JSON。

实验源码与算法未修改；旧270项、36格严格轨迹与wheel/sdist源码验证仍对应同一源码digest，不重跑其硬件任务冒充本轮。仅新增Study声明/报告/离线工具，完成本轮声明展开、来源锁/四Run原始证据、脚本复算和文档/静态检查。旧q171/失败/权重/raw未覆盖或重签。本地分支feature/output-space-prerequisite，不推送、不合并、不删数据。

## 结论与可复现下一步

执行完成=true；质量通过=true；稳定方法优势尚未建立。q173首次出现一阶超过零阶的两个具体匹配前缀，q174有单个句末优势，整体输入链在此三prompt仍领先。下一项高信息量诊断应冻结q173的root94/97及输入领先的root83作为正/负窗口，记录同位proxy/exact hidden误差、映射后mask和top1/top2 margin；同时重放token与接受链必须一致，禁止为了得到改善而调beta/映射或换窗口。它需要另写instrumentation合同、版本与额外前向预算；当前数据无法提供这些未记录值，故本轮不补造机制结论、不直接扩完整矩阵。

复跑本矩阵：准备同ModelScope来源后改新version，`python -m spec_mtp make studies/output_space_small_matrix --num-gpus 1 --init-gpu 0 --round 1`，再launch/process/status/logs/report。正式JSON/图/PLAN/报告与只读分析/图工具可随源码复现；Run/raw/log/weights和.tmp/output-matrix-20261014仅本机，不随clone。NUMBERS仅将本机log引用改为文本，数值不变。
