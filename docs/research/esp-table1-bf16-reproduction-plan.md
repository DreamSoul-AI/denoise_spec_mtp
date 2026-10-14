# ESP Table 1 reproduction — Qwen3-8B / BF16

状态：2026-10-15 计划已立项，未声称复现成功。优先于所有其他研究。此前 4B 证据全部 FP32，已按工具/测试与证据两个主题提交，并推送工作分支；PR #7 的 Branch flow/cpu-checks 已通过并合 dev（8677376e1ac878a159a3095711eac43420d97bde），不合 main。0.6B 罕见事件/局部机理和 4B FP32 扩展暂停。

## 1. 来源、目标与未公开细节

主来源：[ESP arXiv v2](https://arxiv.org/html/2603.17942v2)，§3.1/3.4/3.5、§4、Table 1/3、Appendix D/G.2。已读正文及本地 PDF 第 7 页表格。模型为 [Qwen/Qwen3-8B](https://modelscope.cn/models/Qwen/Qwen3-8B)，权重优先 ModelScope；仅用于本 ESP 复现，禁止拿 8B 做其他研究。

Table 1 Qwen3-8B 的 ESP τ 目标：BC30=1.63，BC60=1.74。BC10 是额外协议核验，Table 1 没有其目标。本文表注为 256-token 输出/H100，§4 正文为 100-token/A100；本次遵循 Table 1 的 256 上限，EOS 则提前停止，逐条记录实际输出长度。不得把原仓库 100-token 静态配置冒充本复现。

论文未明确公开 precision、模型 immutable revision、Qwen thinking 开关、prompt 截断策略与 τ 跨任务聚合权重。BF16 是当前用户明确要求。采用非 thinking chat template、首轮原始 prompt、不截断且纳入全部 480 条；输出单列这些实现选择，不称其为已获作者确认的配置。RTX 5090D v2 24GB 与 H100 不同，torch/transformers 版本差异也记录。用户不要求测速，因此不测 S/R。

官方 SpecBench：[hemingkx/Spec-Bench](https://github.com/hemingkx/Spec-Bench)，固定提交 fd2c1cd7d2201ef71db4c5f4e455008f017967bf，data/spec_bench/question.jsonl。本地 480 条 JSON 对象及顺序与官方完全一致；远端 SHA256=4b6d33e79484f9841c487ee87d1cf6aa8c6066f61d5d482ff09e5a007fafdf04，本地 SHA256=7dd26882f31ada100c2aa7447019b5349bddc55697021acbc5643fdc8740aa21。只存在字节排版差异。保存原文件并绑定两哈希；不得为了对齐目标筛掉难样本。

2026-10-15 模型内容补核验：[官方SHA256证据](../../studies/esp_table1_bf16_full_argmax/docs/modelscope-content-verification-v1.json)记录ModelScope master直接返回的Sha256。16个文件（含5个权重分片）均与原冻结模型清单及BC10 Run实际输入哈希一致。原冻结文件不修改、不重签；这证明核验时的官方内容一致，论文未给出immutable revision及历史下载渠道仍未确认，不冒称论文指定commit已验证。

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
| correctness gate | 每个提交 token 等于产生它的验证前向 logits 的 argmax，全部 token 覆盖且必须全过；包括 prefill 首 token |
| AR diagnostic | 独立 AR 一致率及每条首分叉位置仅作报告指标，不阻塞 τ 执行或本次正确性验收 |
| numerical settings | BF16、默认归约及默认算子；不运行归约开关、单行 linear/RMSNorm、compact attention 或逐层追踪 |
| clocks | Study 局部禁用 decoding clock；零 timing 是原生字段占位，不是测量 |

BC=(k+1)(1+draft_nodes)，本次实际 draft budget=4/14/29，另保留60/2的19节点对照；检查每步真实 BC 不超过预算并记录树宽。论文 Algorithm 1 的 B 与正文 Eq7 表述存在歧义；遵循 Eq7 与当前 Top-1 实现并报告映射，不暗改预算来追目标。

主指标同时报告 pooled τ=sum(committed)/sum(decode_calls)、逐 prompt τ 的均值、逐 category pooled τ 后等权均值。committed 包含 bonus，不含 prefill；另列含 prefill 的实际 model calls、新 token 数与 accepted draft 数。尾部 EOS/长度裁剪口径明确，不混淆 accepted 与 τ。目标的近似程度报告原值/差值/按两位小数是否一致；不得预先把某个聚合方式定为作者确切口径。

## 3. 执行与停止规则

1. 复用 native RPipe Study prepare→execute→collect→summarize→write→process；新 Study/version/Run，原失败和成功 Run 不重签。权重逐文件哈希、官方 ModelScope 文件名/尺寸与实际 BF16参数核验；离线缓存 immutable revision 未确认则明确记录。
2. 先新建小样本协议检查 Study（每类首条，BC10/1、BC30/1、BC60/1主配置与BC60/2对照）。检查 BF16装载、动态树、256上限、精度及原生门；这只是预检，不能代替 480 条 Table 1。
3. 按本次四格协议冻结全480 Study，串行执行BC10/1、BC30/1、BC60/1主配置及BC60/2附加对照。正确性门是数学无损自检：每个提交 token 都等于该次验证前向 logits 的 argmax，覆盖所有实际输出 token，并且必须全过；可记录 logits 差值，但不要求额外算子分析。与独立 AR 的一致率及逐条首分叉只作为报告指标，不阻塞 τ 执行或正确性验收。BF16树验证与逐token AR的前向形状不同，AR不一致本身不判定方法错误。数据、模型来源、BF16装载、树预算及自检覆盖仍须核验；来源/协议不符或OOM先修复，再用新Run，不切FP32、不用teacher纠正、不筛除反例。
4. OOM/其他任务占显存时保留失败、等资源或用新 Run 可逆验证，不停其他任务。单卡只启动一条实验调度链，不并发加载模型。
5. 全量完成后报告配置覆盖、精度、每任务/每 prompt计数、三种 τ聚合、BC30相对1.63与BC60相对1.74的差值、argmax自检覆盖/通过率、独立AR一致率及逐条首分叉。数值不符也保留可复核负结果；仅核对数据、配置和统计口径，不转入算子级数值排查，不按结果挑聚合或mask数。

四任务共用 24GB GPU。记录启动前空闲显存及运行容量采样（含其他进程，非精确 allocator peak）；不使用受干扰的墙钟或 timing 占位做性能比较。四格预检约 13×4×2×256=26624（其中旧三格已执行，新补单格上限6656） 生成 token 上界；全量四格含独立 AR 审计约 480×4×2×256=983040 上界。串行，没有额外 teacher/warmup。容量不足先暂停该 GPU 启动，继续证据/实现核对。

## 4. 全480完成后的4B BF16配对

同批 prompt、同树/预算/长度/随机种子，比较 ESP frozen mean、输入零阶 updating mean λ=0.1、输入一阶 mean+gamma、输出零阶 final-normalized hidden 范数映射、输出一阶 final hidden+EMA velocity，另跑独立 AR。逐 prompt 列 accepted/model calls、每个对照的赢平输及 token exact。不得用此前 FP32 数字代替。

这里的 ESP frozen mean 是用户指定的后续基线，区别于 Table 1 updating mean。tied 权重直接用输出 hidden 的尺度映射，不做逆映射。当前 output provider 只支持 unpruned static chain；后续若统一采用 dynamic/pruned，必须先最小扩展并验证 owner/proxy 对齐，不能让方法使用不同树再配对。4B 子实验开始前单独冻结 PLAN、beta/gamma、精度内部计算与实际 tied-storage 检查。按最新最终指示，先完成8B四格全480并写回三种τ、目标差值、AR一致率及verifier argmax自检，再启动4B BF16五方法加AR的同prompt配对；不因BF16相对独立AR的数值失配转入算子机理。不得提前与8B矩阵并发启动4B。

## 5. 当前执行与归档（2026-10-15）

FP32收尾：PR #7 已经CI通过并合dev，merge8677376；main未操作。此前4B FP32及0.6B局部研究原位保留，本轮不扩展。

当前唯一GPU调度链为[全480 argmax审计](../../studies/esp_table1_bf16_full_argmax/README.md)，正式结果见[STUDY_REPORT](../../studies/esp_table1_bf16_full_argmax/docs/STUDY_REPORT.md)。四格固定顺序为10/1、30/1、60/1、60/2；保持Qwen3-8B/BF16/T0/默认归约、λ=.1 updating mean、动态树+剪枝、256/EOS/seed123及全部480条。60/1为主，60/2仅附加对照，两者均报告相对1.74差值，不择优。

当前首格BC10 Run `dfe1b9c8d5d12e92`正在执行；随后BC30 `b9b54923b1b9ea9f`、BC60/1 `3f3d0f9a84341c0b`、BC60/2 `555ff70d57ce05b0`串行排队。尚无完整480条τ结果，不用预检或部分日志替代。

Study局部观察器绑定每个选择行到对应验证forward的logits，记录argmax/选择值及forward/行号；覆盖prefill首token和全部实际提交token，EOS/预算裁剪后的未提交尾部不混入覆盖数。不增加模型前向，不改精度、算子、采样或树。argmax自检失败立即阻止该Run的execute完成；独立AR运行不安装此观察器。

原有native生命周期可能含旧AR严格门产生的失败状态，原记录如实保留，不重签；该历史状态不得作为本次研究的失败门或阻塞下一τ格。本次研究报告只按全480覆盖、协议核验及数学argmax自检验收，AR一致率独立列示。关闭自动失败重试，避免因AR诊断重复运行。旧冻结Run/PLAN不回写、不重签。

无argmax记录的全量v1部分日志保留。新argmax Study v2首次四Run在模型加载前因ModelScope缓存接入失败，未执行解码；失败Run保留。补接此前同一已校验本地snapshot后以v3新Run执行，未改模型或实验设置。

永久停止BF16 ESP相对独立AR的全部算子级数值机理排查。既有[reduction报告](../../studies/esp_table1_bf16_reduction_check/docs/STUDY_REPORT.md)、[shape报告](../../studies/esp_table1_bf16_shape_check/docs/STUDY_REPORT.md)和测试已按主题提交推送，仅作历史归档；不再启动归约开关、单行linear/RMSNorm、compact attention或逐层BF16算子追踪。权重、缓存和完整Run留本机；全480结束后仅按第4节推进4B BF16五方法加AR，不测速、不恢复机理链、不合main、不force push。

## 6. 执行授权与检查依据

依据2026-10-15 Enmao本任务长期授权，正常工作分支推送、PR、合dev、本地检查替代远端CI直接执行；不使用提问弹窗。报告注明实际验证命令、结果及覆盖范围；保留平台强制分支保护。删除数据/分支、强推、合main、花钱前暂停相应动作并写报告。自动审批拒绝记录具体命令、拒绝理由及执行状态，继续未受阻工作，交监督助手处理。[授权与审批记录](../handover.md)。

2026-10-15原生验收门修订：用户明确要求summarize/process也以完整verifier argmax为门，AR仅诊断。在隔离工作树更新validation与原生T0审计元数据，当前GPU执行包保持冻结；已完成的旧AR门失败格只重新验收并归档原失败result，禁止重跑BC10 execute。执行来源与验收validator SHA分开记录；全四格原始execute全部结束后再按原顺序做4B，不恢复算子机理或测速。
