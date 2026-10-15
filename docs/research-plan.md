# SD研究计划：固定数据复现与mask方向对照

中文正本，更新于2026-10-16。[English translation](research-plan.en.md)。采用[新版规范与模板](research/standards/README.md)，来源为RPipe已合入dev的`e461133218deabf8755b3e8657650e1e4a3cd9f4`。本次是对已有研究与证据的整理，不是对已看到结果的实验重新预注册，也不改运行中的Study合同。

## 一、灵感与初步问题

研究类型为复现及固定条件下的方法比较。此前4B FP32局部结果使输出空间外推值得检查，但4B BF16全480比较中，输出零/一阶弱于输入一阶；这是当前问题的实际触发，而非输出空间优势已经成立。既有数字和执行范围见[阶段报告](research/sd-stage-report-2026-10-15.md)。

本计划回答三个问题：ESP论文的主要接受长度是否复现；五种现有mask在同一数据和模型上表现如何；输入一阶的收益是否依赖聊天模板首差分e2−e1这一特定方向。文献先用于明确比较对象和替代解释，再组织已有及正在运行的验证。新方法、新模型范围与创新性均不据旧草稿自动成立。

当前状态：五方法加AR及BC30方向六格各480均完整验收；新增405,073个token、连同复用zero共485,860个token全数学门通过。8B自实现未达到论文目标，作者官方入口未确认，非官方第三方预检数学门失败。计划经PR23合dev；[六格最终报告](research/4b-full-direction-controls-2026-10-16.md)与正式证据由[PR22](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/22)交付，本轮不追加方向BC60。

本次由本会话执行文档与既有实验收尾，路线和资源边界按Enmao当前指示。优先完成本次计划及PR流程，不停止现有GPU任务。共享一张24GB GPU，单队列、非抢占；不测速、不改prompt、不另起研究方法。后续新增研究的负责人、期限与预算待另定。旧[研究计划v6](research/research-plan-v6.md)保留为历史设想，Kalman、高阶和非tied映射不属于当前执行范围。

## 二、文献调研

本次为围绕上述问题的定向证据更新，不声称完成系统综述或重读旧稿全部60篇。信息截止及本次核对日期为2026-10-16。实际使用arXiv原文/摘要、Spec-Bench官方仓库、已有来源核查及结果文件；从旧v6参考文献追踪基础工作，并检索了“SpecBench official github hemingxia Spec-Bench”，核对当前官方入口为`hemingkx/Spec-Bench`。后续若补查，关键词围绕training-free multi-token prediction、embedding-space probing、speculative verification、dynamic draft tree和mask initialization，不扩大为新实验授权。

纳入与研究问题直接有关的作者论文、官方数据/实现来源，以及用户指定的第三方实现；跨模型、精度、树预算、训练式起草器或不同数据条件的数字只作背景，不放入本仓公平排名。排除营销综述、无法追溯的汇总数字及与当前范围无关的方法扩张。未查到可运行官方代码不等于证明作者未开源。阅读深度逐项列明，来源发现、论文主张、代码核查和实测分开记录。

| 文献与定位 | 问题与实际阅读范围 | 数据与模型 | 算法 | 指标及条件 | 证据、局限与用途 |
| --- | --- | --- | --- | --- | --- |
| [ESP v2](https://arxiv.org/html/2603.17942v2)，§3、Table1、Appendix G.2 | 本次核对摘要、Eq4/5、Table1及附录定位；既有相关正文分析见[复现计划](research/esp-table1-bf16-reproduction-plan.md) | SpecBench；本仓对应Qwen3-8B复现格 | embedding mask、动态树与剪枝 | 目标τ见第八章；不采用论文测速为本次产物 | 最接近基线；必须区分论文、作者实现、自实现与第三方，不能用自实现负结果判定原方法无效 |
| [Leviathan等，2211.17192v2](https://arxiv.org/abs/2211.17192v2) | 本次摘要核对；原论文采样论证没有在本次重新证明 | 原文Transformer设置，不是本仓4B配对 | speculative decoding及目标分布验证 | 原文条件与本批T0不同 | 支持草稿/验证职责区分；不能由本仓同次forward argmax审计声称覆盖所有采样分布 |
| [Chen等，2302.01318](https://arxiv.org/abs/2302.01318) | 本次摘要核对 | 原作者模型与采样实验，不并表 | speculative sampling | 非本次T0数值对照 | 作为正确性与随机采样背景；本次不新增采样实验 |
| [EAGLE-2，2406.16858v2](https://arxiv.org/abs/2406.16858v2) | 本次摘要核对动态树动机 | 作者训练式起草模型设置 | 动态draft tree | 与本仓免训练mask条件不同 | 提醒接受行为与上下文相关；不是已执行的本仓baseline |
| [Medusa，2401.10774](https://arxiv.org/abs/2401.10774) | 本次摘要核对多头路线 | 作者模型及额外预测头 | 多token head | 没有本仓同条件实测 | 保留训练式替代路线，不据此声称免训练自动免于分布偏差 |
| [Spec-Bench官方仓库](https://github.com/hemingkx/Spec-Bench)，data/spec_bench与Readme | 本次官方入口/仓库说明核对，实际样本分布从冻结manifest计算 | 原固定480条；本地13个category | 评价平台与原始问题来源 | 480条是输入单位，不是独立方向重复数 | 数据来源；repo标Apache-2.0，不据此替原始组成数据另行确定所有使用条件 |
| [指定HF第三方源码及审计](research/esp-third-party-reproduction-2026-10-15.md) | 既有源码/API与真实数学门审计，本次复查交付报告 | 原固定q121、8B BF16，三预算预检 | 原字节API，非作者官方；CLI协议另有差异 | 六次forward后首token门失败；无有效τ | 终止该尝试；不能当官方或全480复现，也不修成新方法继续跑 |

文献地图的选择结果是继续固定模型的免训练mask比较，同时收紧“输出空间更优”和“固定模板方向唯一有效”的解释。旧v6中Future Lens、LatentMAS、指数平滑和Kalman等文献仍作为历史线索保留，未在本次重新核对全部正文、定理条件或新颖性，不把它们升级为本轮方法贡献。文献中关于无损与吞吐的主张，也不替代本仓实际正确性门和未测速边界。

## 三、研究问题与假设

| 问题/假设 | 条件与可反驳预测 | 当前判断与下一证据 |
| --- | --- | --- |
| R1：8B论文主要τ能否复现 | 按Table1目标和Qwen3单mask主协议比较；若主要值仍有明显缺口，不宣布数值复现 | 自实现有缺口，作者官方入口未确认，第三方预检失败；缺口不归因为ESP方法无效 |
| H1：输出零/一阶在本批优于输入一阶 | 同480、4B BF16、同BC/树/停止条件；若两输出整体弱于输入一阶则不支持 | 原五方法全量不支持；速度项也未显示稳定联合收益，见第九章 |
| H2：输入收益只来自e2−e1特定方向 | 三个预先固定的同范数随机方向均无收益才与该解释相容；出现明确随机收益即反驳其“唯一”措辞 | 三个完整随机格均高于zero，random2也高于template，不支持唯一方向解释；不推出任意方向均有效 |
| R2：内容初始化在同条件下如何表现 | 保持原prompt与完整mean，只变原生速度初始化后缀；与template/zero配对 | content全480完成，τ1.364829262低于zero1.422420206；其范数未另匹配，不能解释为纯方向效应 |

本次贡献目标是可追溯的复现边界与现有方法/指定对照比较，不声称新算法或普遍最优。文献界定基线和验证责任，数据与模型限定推断范围，算法限定变化因素，指标和配对实验检验上述问题。参数β、状态空间、输出路径及范数差异仍是混杂，不能把输入/输出比较全部差异归于一个空间选择。

## 四、数据

使用既有`datasets/spec_bench/question.jsonl`，来源入口为上述Spec-Bench官方项目。本轮不重新拉取最新数据替换；固定字节SHA-256为`7dd26882f31ada100c2aa7447019b5349bddc55697021acbc5643fdc8740aa21`。数据来源、输入IDs、EOS及顺序的合同见[4B prompts_manifest](../studies/qwen3_4b_bf16_five_methods/docs/prompts_manifest.json)。历史下载的上游immutable commit未另确认，不用当前GitHub HEAD代替历史版本；组成数据许可/预训练污染的逐项审计未完成。

样本单位为原顺序480条首轮prompt，question_id首尾为121/90。分布：math_reasoning、qa、rag、summarization、translation各80条；coding、extraction、humanities、math、reasoning、roleplay、stem、writing各10条，共13个category。输入采用原non-thinking chat template，不换模板、删题、截断或改写来调结果；最长1500输入token已由原4B预检记录。指标按所有480条配对，并保留各category结果。

本研究没有训练或拟合划分，使用冻结评价集完成既定比较；固定480已被反复分析，不能称为全新独立holdout，也不能据此挑最佳随机种子后报总体泛化。未做完整重复/污染识别，无法排除预训练重叠。每Run核qid、顺序、input_ids、模型内容及停止条件；不会把不同模型tokenizer生成的IDs未经核对直接互换。完整Run、输出token、trace、权重和cache只留本机；Git保留manifest、汇总和可复查证据入口。

## 五、模型

目标模型为现有ModelScope `Qwen/Qwen3-4B`：qwen3、36层、hidden2560、vocab151936，tied embedding/output storage由每Run实际指针核对，而非只看配置。输入为固定token IDs与指定mask，输出为目标logits、末层hidden及已提交token。权重、forward和最终mask使用BF16/eager/T0；原生输出EMA/范数内部FP32状态保留，不称全部内部计算均为BF16，也不新开FP32模型对照。

来源与文件内容见[modelscope_snapshot](../studies/qwen3_4b_bf16_five_methods/docs/modelscope_snapshot.json)，实际dtype/tied-storage/model_digest/runtime在[paired evidence](../studies/qwen3_4b_bf16_five_methods/docs/paired_evidence_v1.json)。14个模型文件内容已核验；历史远端revision身份仍未完全确定，权重许可在本次未重新核验，记Unverified，不把本仓许可套到模型。运行环境为torch2.11.0+cu130、Transformers5.12.1、RTX5090 D v2；不同环境的细项以Run合同为准。安装依赖固定到已验证Transformers5.12.1，不适配5.20新缓存API，不替换正在执行的环境。

Qwen3-8B仅属于ESP Table1复现，现阶段不再为方向研究使用它。0.6B及4B FP32属于历史归档，与本批BF16结果分开。模型权重、解码树和停止规则在同预算比较中固定；新增因素仅为既有五方法或用户指定的方向控制，不新增训练式draft模型。

## 六、算法

复用现有[SpecMTP实现](../src/spec_mtp/structure/algorithm/)及原生RPipe Study生命周期，不另建实验框架。以下是本仓实际比较定义，不把用户定义的ESP frozen mean写成论文的updating mean。

| 现有方法 | mask及状态定义 | 固定参数与边界 |
| --- | --- | --- |
| ESP frozen mean | 原prompt embedding均值，生成中冻结 | `update=false`，用户指定基线 |
| 输入零阶 | 完整prompt mean初始化，提交embedding后按`mean ← mean + λ(e−mean)`更新 | λ=0.1；即updating mean，方向控制zero直接复用此格 |
| 输入一阶 | `mask_j = mean + γ j v`；原生embedding差分EMA更新v | β=0.9999、γ=1、λ=0.1、order0 level；normalize与extrapolate_ema关闭 |
| 输出零阶 | 原生末层normalized hidden及代理状态生成u，再以`r u/‖u‖`作为mask；r为词表embedding范数均值 | order0；保留原owner/history语义，非输入embedding的逆映射 |
| 输出一阶 | 在同一末层hidden预测中加入EMA速度，再做同一范数映射 | order1、β=0.9、代理β′=0.99；不是仅改空间而其他状态全部相同 |
| 独立AR | 同一模型、原prompt、seed及停止规则的逐token贪心生成 | 共享一次480条参考，不在每个Spec Run重复执行 |

tied模型不做逆映射。输出代理只按原生root/候选owner和已接受历史更新，不额外teacher纠正或增加验证forward。树构造、剪枝、KV cache、bonus和EOS/长度裁剪继续使用原实现；接受数是裁剪前候选接受计数，提交数按实际裁剪计算。模型无训练目标或梯度更新；本次也不优化超参数。详细实际配置以正式evidence的`actual_settings`为准。

指定方向控制只改上述输入速度构造：template固定`v=e2−e1`；random0/1/2分别用CPU Generator种子0/1/2取固定随机方向，FP32归一到同prompt模板差分范数后转BF16，生成中v固定；zero为v=0；content从原首个user内容token起的后缀初始化原生EMA速度，保留完整prompt mean并继续原生更新。content后缀包括原末尾模板，不改输入，范数不额外匹配。template不等于会持续EMA更新的原生input_first。

代码分类：当前ESP全480及五方法是本仓自实现/扩展；作者官方入口尚未核验到，不能称官方代码复现。指定HF来源为dataset `Harshvardhan-Mestha/esp-reproduction-artifacts`，commit `ad76f8da29f3bfc7faa20488193c6aa83a9f708c`，八文件按原字节保存于[reference及ORIGIN](../src/spec_mtp/structure/algorithm/reference/esp_reproduction_artifacts/ORIGIN.json)，未附LICENSE记Unverified。既有外部验收调用其原生API而非原CLI，适配与失败见[第三方报告](research/esp-third-party-reproduction-2026-10-15.md)。不把它修成新baseline继续跑。

正式配置变化必须新Study版本/Run，已有成功Run不重签。方向原协议`fe59d35`及资源补齐协议`0e7c46f`属于[PR22](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/22)；固定480的科学步骤不变，补齐版仅将实际GPU资源拒绝改为prompt边界等待。原失败Run与105次完整prompt执行的资源损耗单列，不拼接成有效480。

## 七、指标

| 角色与名称 | 定义、单位、方向 | 数据与聚合 | 实现及判据 |
| --- | --- | --- | --- |
| 主指标pooled τ | Σdecode committed / Σdecode calls，token/解码调用，越高越好 | 全480；不含prefill首token | 原生raw与共同CPU读出；按预定预算逐格报告，不择聚合宣布复现 |
| 辅助两聚合 | 逐prompt τ等权均值；先逐category pooled再13类等权均值 | 两者单列，不冒称论文任务权重 | 同一结果文件重算；不隐藏与pooled的差异 |
| 接受数/主调用数 | accepted越高越好；prefill+decode calls越低越好 | 按qid配对分别报胜/平/负、总差值 | 不强行合成单一赢家；输出路径/长度不同，不能解释为等输出加速 |
| 逐prompt τ配对 | 用整数交叉相乘比较两个比值，保留平局 | 方向对template及既有五方法 | 480条顺序/身份必须一致，报告全部输局 |
| 正确性硬门 | 每个提交token等于该次验证前向正确owner logits的argmax，含prefill | 全输出token覆盖、owner/hash链核验 | 必须全过；来源、非有限、计数及owner审计失败不能用AR诊断代替 |
| AR诊断 | 全序列一致率、逐条首分叉、输出长度 | 同一共享AR参考 | 只报告，不阻塞native summarize/process，不转向算子数值研究 |
| 资源工作量 | 模型调用数、提交token、失败格已消耗工作量 | 成功与失败分开 | 支持排班和BC60决定；不测时延/吞吐，零计时字段是占位 |

全部数字定位到结果文件、cell和Run；作者值、本地实测和未测项分开。没有另设“差距可接受”的数值阈值或事后显著性阈值，未达到既定论文目标就如实报差距。数学自检覆盖T0实际提交，不据此宣称任意温度分布或跨forward形状逐token必然等同。

## 八、实验设计与执行顺序

| 实验与问题 | 对照及变化因素 | 固定条件与重复 | 预算、状态与判读 |
| --- | --- | --- | --- |
| E1：ESP Table1来源与数值复现 | 作者入口核查、自实现参考、指定第三方预检分别记录 | 8B BF16/T0、原480；主BC10/1、30/1、60/1，60/2附加；λ0.1 updating mean | 自实现四格完成但未达到目标；官方入口未确认；第三方预检失败后停止，无新8B排队 |
| E2：五方法加AR | 六方法共享输入；BC30/60分别比较五种mask | 4B BF16/T0，双mask、naive动态树剪枝、draft budget9/19，seed123+index，max_new_tokens256/EOS，默认归约 | 1共享AR+10个Spec Run，共5280次prompt执行但只有480个评价输入；已11/11原生验收 |
| E3：指定方向全480 | template、random0/1/2、zero、content；每个方向相对template及旧五方法配对 | 同E2 BC30；mean/树/停止/输入全固定；方向种子提前指定，解码seed不变 | 五个新增完整路径+复用zero，新增有效预算2400次prompt执行；六格全完整，补齐Study process通过 |
| E4：范围与证据整合 | CPU重算、出处/边界、规范/中英文计划、PR/dev集成 | 复用同一raw及既有工具，保留所有有效/失败格 | 不增加GPU矩阵；E3终验/图/报告完成；BC60方向本轮不追加，理由见最终报告 |

### （一）基线复现与后续安排

实现来源与实际范围以[作者来源核查](research/esp-official-code-reproduction-2026-10-15.md)、[8B执行证据](../studies/esp_table1_bf16_full_argmax/docs/protocol_evidence_v1.json)及第三方报告为准。当前没有可运行作者入口的核验证据，不能用任意GitHub同名项目替代；后续若取得作者版本，再按Enmao范围对齐数据、模型和原生入口，记录必要适配。不凭模板再次自动启动8B。

| 目标与条件 | 计划目标及出处 | 本地实测及出处 | 差距与判断 |
| --- | --- | --- | --- |
| 8B BC10/1 | 用户要求的附加预算；Table1不填臆测目标 | τ1.399047，protocol_evidence的`cells` | 完整数学门通过；无对应Table1目标差值 |
| 8B BC30/1 | 论文Table1 τ1.63 | τ1.563378，同上 | −0.066622；自实现未达到主要目标 |
| 8B BC60/1 | 论文Table1 τ1.74；Qwen3单mask依据Appendix G.2 | τ1.647301，同上 | −0.092699；未复现目标 |
| 8B BC60/2 | 预先登记附加对照，不替代单mask主配置 | τ1.603729，同上 | 不据对照格或另选聚合宣称主目标复现 |
| HF第三方三预算 | 原API在共同BF16/T0/原q121的数学门预检 | 六次forward；首token argmax margin40.75/33.5/33.25，见[审计JSON](research/esp-third-party-audit-2026-10-15.json) | 无有效τ、未执行全480；非官方，负结果保留 |

以上复现缺口影响对“原ESP效果”的结论；本仓4B配对只能支持共同自实现条件下的比较。论文checkpoint历史revision、模板/长度/聚合等未完全固定，作为协议缺口列出，不写成已经证明的原因。永久停止BF16相对独立AR的算子级机理链。

### （二）消融覆盖与组成

E3是对既有输入速度解释的指定控制，不是新增方法主表。随机方向和template匹配原范数，但BF16量化后使用实际范数比记录；content没有范数匹配，初始化及后续状态也不同。固定v与原生input_first持续更新的差异另列；不能把它们称作同一方法。四窗口局部干预仅是历史分析，不能代替全480；最终报告保留各category及全部逐prompt输局。

### （三）执行安排与优化方法

原GPU单队列已自然exit0，content完成；CPU正式读出、来源/argmax/原生process核对通过。计划PR23已合dev，PR22收尾结果交付，不更改E3冻结PLAN。正常提交、push、PR合dev及合后远程工作分支清理按用户授权执行；不合main、不force push、不删本地分支、Run或数据。归档旧PR/issues只在状态和关联已核实后做，不因旧日期直接关闭。

GPU准入只看nvidia-smi实际占用与足够空闲显存，不把未识别CPU进程当GPU作业。每组完整结束后再让卡，共享GPU的量化插跑窗口已完成一次实际交接，不能中止当前组。资源短暂冲突在prompt边界等待同一Run，来源/argmax/OOM等失败仍如实终止该格并保留，不用改prompt修结果。既有成功template和zero不重跑。

这是预定离散对照而非参数搜索；无BO择优或根据测试结果换prompt。三种随机方向种子是三个固定偏置，不是三次训练种子重复；因为模板前两个token相同，每种子在480条中也给出相同方向。480条共享输入的配对有实际描述价值，不构成跨模型、独立训练或任意方向总体的置信证明。本轮不新增显著性宣称。方向BC60是否继续，在BC30全部结果后按实际token/forward成本和要回答的问题决定，不提前按优胜种子删减格子，也不把“尚未做”写成“已完成”。

## 九、执行记录与结论

| 记录 | 实际证据 | 结果与边界 |
| --- | --- | --- |
| E1自实现 | 8B protocol_evidence及[阶段报告](research/sd-stage-report-2026-10-15.md) | 四格数学门全过、共318830 token；BC30/60单mask目标未复现；不是作者代码复现 |
| E2五方法 | [paired_evidence_v1.json](../studies/qwen3_4b_bf16_five_methods/docs/paired_evidence_v1.json)，`cells`和`pairs` | 11/11原生验收；4800次Spec prompt执行共809118 token全argmax通过；主方法τ见下表 |
| E3完整证据 | [direction_evidence_v1.json](../studies/qwen3_4b_bf16_directions/docs/direction_evidence_v1.json)、[最终报告](research/4b-full-direction-controls-2026-10-16.md)、[PR22](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/22) | `complete=true`；六格各480完整。原资源失败Study仍passed=false；补齐Study passed=true，不改签旧失败 |
| 第三方与来源负结果 | 官方来源核查、第三方ORIGIN及审计JSON | 找不到核验入口不证明未开源；非官方首token门失败，不虚构τ、不重跑8B |

| 已验收主方法 | 4B BC30 pooled τ | 4B BC60 pooled τ |
| --- | --- | --- |
| ESP frozen mean | 1.402895 | 1.499079 |
| 输入零阶 | 1.422420 | 1.519109 |
| 输入一阶 | 1.511958 | 1.636340 |
| 输出零阶 | 1.433178 | 1.528922 |
| 输出一阶 | 1.435540 | 1.529836 |

表中每个值来自E2证据`cells[预算/方法].totals.pooled_tau`，共享AR作为诊断参考，不给AR虚构draft接受τ。逐prompt接受数/calls赢平输、AR首分叉及输出长度都在该文件，完整结果不被本表舍入替代。本批输入一阶整体最好；输出一阶相对输出零阶增量小，不能据接受数或调用数某一列单独宣布联合收益，更不能外推等输出速度。

E3有效pooled τ：template1.507777653、随机0为1.495188134、随机1为1.464349086、随机2为1.523884714、zero1.422420206、content1.364829262，均来自上述正式六格证据。随机2相对template逐promptτ267胜/47平/166负；三个随机种子均高于zero，故不支持本批收益只由e2−e1方向造成的解释。仍有逐prompt反例，content范数未匹配且输出长度不同；这不是推荐最佳随机种子作新方法，也不证明任意方向有效。零偏置复用和失败资源工作量单列，不能把补齐成功包装成原失败Study通过。

本轮不追加BC60方向矩阵：新增五个有效格已有2,400次prompt执行、405,073 token/276,523模型调用，三随机种子已否定本批e2−e1唯一性；BC60回答跨预算泛化，不能消除content范数混杂。失败完整partial另记20,977 token/13,854 calls，不拼接有效样本，细节见最终报告。下一步仅为CPU回归及PR22/dev闭环。旧0.6B罕见事件、算子归因、Kalman和新方法继续归档；开放问题不自行升级为额外实验。

## 十、GitHub使用与计划变更

本文件是当前宏观计划入口，英文版逐章对应；Study级`docs/PLAN.md`是先于make冻结的执行合同，数字/图在其`STUDY_REPORT.md`和evidence中。原始tokens/trace、完整Run、模型和cache不进Git。每次正式运行沿用原生记录的commit、source/input/model摘要、配置、实际环境、seed、命令、RunID、失败和结果路径，不重建同名Run或重签历史成功记录。

| 日期 | 变更与原因 | 影响范围 |
| --- | --- | --- |
| 2026-10-16 | 按Enmao新规范十章重写并补英文，导入RPipe固定来源规范/模板，纳入定向文献证据和当前结果 | 替换默认计划入口，旧v6历史稿保留；不是重新预注册，不改已冻结实验 |
| 2026-10-16 | 记录作者/自实现/第三方差异、正确性门与AR诊断、三随机方向及资源补齐状态 | 收紧结论，不扩大GPU预算或改prompt |
| 2026-10-16 | 安装依赖固定Transformers5.12.1，避免5.20缓存API漂移导致CPU CI失败 | 只固定已验证安装版本，不改科学缓存算法、不替换现有GPU环境 |

计划PR关联现有[PR22](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/22)及各结果报告，合dev后删除本次已合远程计划分支；运行中的方向工作分支保留到其结果PR合入为止。规范正本、译本、来源与SHA见[standards README](research/standards/README.md)。旧v6更广的60篇参考文献仅为历史线索，不能当本次已全部审阅的证据。本文献表各作者原文、官方数据入口和实际使用的本仓报告即本次参考资料，关键事实已就近定位。
