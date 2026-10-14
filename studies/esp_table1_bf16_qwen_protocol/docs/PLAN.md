# ESP Table 1 reproduction — Qwen3-8B / BF16

状态：2026-10-15 计划已立项，未声称复现成功。优先于所有其他研究。此前 4B 证据全部 FP32，已按工具/测试与证据两个主题提交，并推送工作分支；PR #7 的 Branch flow/cpu-checks 已通过并合 dev（8677376e1ac878a159a3095711eac43420d97bde），不合 main。0.6B 罕见事件/局部机理和 4B FP32 扩展暂停。

## 1. 来源、目标与未公开细节

主来源：[ESP arXiv v2](https://arxiv.org/html/2603.17942v2)，§3.1/3.4/3.5、§4、Table 1/3、Appendix D/G.2。已读正文及本地 PDF 第 7 页表格。模型为 [Qwen/Qwen3-8B](https://modelscope.cn/models/Qwen/Qwen3-8B)，权重优先 ModelScope；仅用于本 ESP 复现，禁止拿 8B 做其他研究。

Table 1 Qwen3-8B 的 ESP τ 目标：BC30=1.63，BC60=1.74。BC10 是额外协议核验，Table 1 没有其目标。本文表注为 256-token 输出/H100，§4 正文为 100-token/A100；本次遵循 Table 1 的 256 上限，EOS 则提前停止，逐条记录实际输出长度。不得把原仓库 100-token 静态配置冒充本复现。

论文未明确公开 precision、模型 immutable revision、Qwen thinking 开关、prompt 截断策略与 τ 跨任务聚合权重。BF16 是当前用户明确要求。采用非 thinking chat template、首轮原始 prompt、不截断且纳入全部 480 条；输出单列这些实现选择，不称其为已获作者确认的配置。RTX 5090D v2 24GB 与 H100 不同，torch/transformers 版本差异也记录。用户不要求测速，因此不测 S/R。

官方 SpecBench：[hemingkx/Spec-Bench](https://github.com/hemingkx/Spec-Bench)，固定提交 fd2c1cd7d2201ef71db4c5f4e455008f017967bf，data/spec_bench/question.jsonl。本地 480 条 JSON 对象及顺序与官方完全一致；远端 SHA256=4b6d33e79484f9841c487ee87d1cf6aa8c6066f61d5d482ff09e5a007fafdf04，本地 SHA256=7dd26882f31ada100c2aa7447019b5349bddc55697021acbc5643fdc8740aa21。只存在字节排版差异。保存原文件并绑定两哈希；不得为了对齐目标筛掉难样本。

## 2. 当前协议（Qwen3 BC60 修订）

[Appendix G.2](https://arxiv.org/html/2603.17942v2#A7.SS2)，PDF第18页原句：

> For Qwen3 models, single mask token is used for BC=60 while for LLaMA3 model two mask tokens are used.

§4 的一般默认不能覆盖这条针对Qwen3的具体说明。[Table 3](https://arxiv.org/html/2603.17942v2#S4.T3)的单mask树宽[29]对应BC=2×(1+29)=60。Table 3的数值行是LLaMA，G.2语句在Figure8的附加结果语境中；Table1没有单独给出mask数。因此采用60/1为主配置是基于模型特定说明的协议判断，不冒称已经获得作者确认。60/2保留为预先声明的对照，不从结果中择优。

此前已执行的预检与数值控制以60/2为BC60格，属于对照结果，不能继续标为Qwen3 BC60主复现。原冻结PLAN/Run/证据保持原字节；修订预检采用新PLAN与新Run补60/1，并按冻结哈希复用原已执行三格，避免重跑已有数字。预检和全480报告均固定列60/1、60/2的τ及各自相对1.74的差值，标明AR质量，缺格写pending而不是0。

| 项目 | 本次值 |
| --- | --- |
| dtype / temperature | BF16 / T0，绝不新增 FP32 模型实验 |
| mean mask | prompt embedding mean 初始化；每个已生成 token 按 m←m+0.1(e−m) 更新 |
| BC / mask count | 主配置10/1、30/1、60/1；对照60/2 |
| tree | dynamic，Top-1 扩展，累计路径概率排序；父子同 token 替换为下一候选；pruning=true |
| implementation | native naive 动态树 attention/cache，保留原始模型与验证语义 |
| seed / outputs | seed123，max_new_tokens256，EOS 提前停止，warmup=false |
| input set | 全部 480 首轮，chat template enable_thinking=false；max_prompt_len40960，实际预检不丢任何条目 |
| audits | 每个 ESP 输出与该 BF16 模型独立 AR 逐 token 核验；报告所有不一致 |
| clocks | Study 局部禁用 decoding clock；零 timing 是原生字段占位，不是测量 |

BC=(k+1)(1+draft_nodes)，本次实际 draft budget=4/14/29，另保留60/2的19节点对照；检查每步真实 BC 不超过预算并记录树宽。论文 Algorithm 1 的 B 与正文 Eq7 表述存在歧义；遵循 Eq7 与当前 Top-1 实现并报告映射，不暗改预算来追目标。

主指标同时报告 pooled τ=sum(committed)/sum(decode_calls)、逐 prompt τ 的均值、逐 category pooled τ 后等权均值。committed 包含 bonus，不含 prefill；另列含 prefill 的实际 model calls、新 token 数与 accepted draft 数。尾部 EOS/长度裁剪口径明确，不混淆 accepted 与 τ。目标的近似程度报告原值/差值/按两位小数是否一致；不得预先把某个聚合方式定为作者确切口径。

## 3. 执行与停止规则

1. 复用 native RPipe Study prepare→execute→collect→summarize→write→process；新 Study/version/Run，原失败和成功 Run 不重签。权重逐文件哈希、官方 ModelScope 文件名/尺寸与实际 BF16参数核验；离线缓存 immutable revision 未确认则明确记录。
2. 先新建小样本协议检查 Study（每类首条，BC10/1、BC30/1、BC60/1主配置与BC60/2对照）。检查 BF16装载、动态树、256上限、精度及原生门；这只是预检，不能代替 480 条 Table 1。
3. 按本次四格协议冻结全480 Study，预检后串行执行主配置与双mask对照。预检失配不隐藏，也不替代全量：全量仍保留native exact_match_rate=1门，失败格τ仅标为诊断值并列差值，不宣称成功。若实际数据/模型来源或协议校验失败、OOM则先修复来源/容量，再用新Run；不得改FP32、teacher强制纠正、丢反例或放宽门。
4. OOM/其他任务占显存时保留失败、等资源或用新 Run 可逆验证，不停其他任务。单卡只启动一条实验调度链，不并发加载模型。
5. 全量完成后报告配置覆盖、精度、每任务/每 prompt计数、三种 τ聚合、对目标差值与失败边界。数值不符也输出可复核负结果，再按首个可证伪差异推进，不宣称强行成功。

四任务共用 24GB GPU。记录启动前空闲显存及运行容量采样（含其他进程，非精确 allocator peak）；不使用受干扰的墙钟或 timing 占位做性能比较。四格预检约 13×4×2×256=26624（其中旧三格已执行，新补单格上限6656） 生成 token 上界；全量四格含独立 AR 审计约 480×4×2×256=983040 上界。串行，没有额外 teacher/warmup。容量不足先暂停该 GPU 启动，继续证据/实现核对。

## 4. 后续 4B BF16 配对（ESP 复现之后）

同批 prompt、同树/预算/长度/随机种子，比较 ESP frozen mean、输入零阶 updating mean λ=0.1、输入一阶 mean+gamma、输出零阶 final-normalized hidden 范数映射、输出一阶 final hidden+EMA velocity，另跑独立 AR。逐 prompt 列 accepted/model calls、每个对照的赢平输及 token exact。不得用此前 FP32 数字代替。

这里的 ESP frozen mean 是用户指定的后续基线，区别于 Table 1 updating mean。tied 权重直接用输出 hidden 的尺度映射，不做逆映射。当前 output provider 只支持 unpruned static chain；后续若统一采用 dynamic/pruned，必须先最小扩展并验证 owner/proxy 对齐，不能让方法使用不同树再配对。4B 子实验开始前单独冻结 PLAN、beta/gamma、精度内部计算与实际 tied-storage 检查。本阶段仅排队，不先跑 4B。


## 本Study合同

这是修订预检PLAN。原esp_table1_bf16_preflight/docs/PLAN.md保持历史冻结字节；G.2原句与60/1主、60/2对照以上已明确。固定原13条首条/category、BF16/T0、256/EOS、seed123、lambda=.1 updating mean、动态树剪枝。新Run只补原未运行的BC60/1，draft budget29；原10/1、30/1、60/2三格按reused_preflight.json的冻结来源/哈希复用。不得再跑已有数字，不能把复用三格冒充新Run成功。预检总表固定四行，BC60双方分别报告pooled/prompt/category τ与1.74差值、AR质量，不择优、不因失配删除。

原生BF16精度策略不调整；实际归约/确定性记录在Run。原设置与reduction/shape控制的结果不混合为一张同设置表。独立AR审计与native exact_match_rate=1门保留；失败τ为诊断值。下一全量四格由独立Study冻结全部480且同时列两种BC60，预检失配作为已知风险，不替代全量结果。若来源不符/OOM才先处理该失败边界。

GPU排班：只启动本Study一条launch链，单Run串行，当前约21GiB空闲；不停止其他任务。容量记录包含背景，不做速度/墙钟比较。新格13×2×256=6656生成token上界，无warmup/teacher。命令：python -m spec_mtp make studies/esp_table1_bf16_qwen_protocol --round 1；python tools/launch_once.py launch studies/esp_table1_bf16_qwen_protocol --round 1 --console shared，使用native scheduler的retry_failed=False，不修改vendored RPipe。
