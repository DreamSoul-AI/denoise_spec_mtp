# ESP Table1协议缺口登记与启动条件

当前状态：PR36已合dev，非官方四格全480复核完成；本轮只读跟进公开作者线索并整理合同，不重跑GPU矩阵。
最新结论：BC30/60 pooled τ为1.563378/1.647301，距论文1.63/1.74为−0.066622/−0.092699；尚不能唯一归因。
数字出处：[全480复核报告及原始结果路径](esp-table1-nonofficial-full480-recheck-2026-10-16.md)、[CPU账本](esp-table1-gap-analysis-2026-10-16.json)。
下一步：取得作者实现及Table1合同后先做来源/配置/计数对账；仅可核验官方原生路径通过预检后申请GPU。
阻塞：作者repo、实现commit、原生入口及逐任务计数未取得；官方复现未完成，非官方结果有效但目标未复现。

## 一、本轮公开来源跟进

核查日期：2026-10-16，约11:49（Asia/Shanghai）。执行两项公开网页搜索：`"Embedding-Space Probing" "code" Goel ESP github`、`"2603.17942" repository implementation authors`。搜索摘要只作线索，未把搜索排序或无命中当成发布状态证明。

直接读取[作者Raghavv Goel的ICML公开帖](https://www.linkedin.com/posts/raghavv-goel_icml2026-machinelearning-generativeai-activity-7478283197508759553-p_ob)。返回的公开页面正文同时列出ESP、ConFu和diffusion workshop三项工作；ESP条目对应Poster #191。可见相关旧帖将training-free MTP的论文指向短链[ga9T4p7r](https://lnkd.in/ga9T4p7r)，没有可核验的ESP实现repo/commit/原生入口。

该页面下关于等待代码发布的评论明确针对ConFu，不能转写成ESP未发布代码的证据。没有把同作者其他论文的实现或通用推测解码代码当作ESP。公开页的相对发布时间只作页面显示，未据此推算准确发布日期。

| 本次动作 | 观测 | 可作出的判断与限制 |
| --- | --- | --- |
| 读取作者公开帖 | 返回可读正文，ESP论文/会议信息可定位；未返回ESP代码入口 | 在本次可见正文中没有取得入口，不代表作者所有帖子/登录后评论均无代码 |
| 点击该页training-free MTP短链 | 工具返回`Failed to fetch`及`Cache miss`，未取得最终目的页 | 短链目标未核验；不把获取失败写成404或代码不存在，不绕过访问限制 |
| 搜索返回HF artifacts | 命中已审计的非作者第三方仓库 | 沿用[第三方验收](esp-third-party-reproduction-2026-10-15.md)，首token数学门失败，无有效τ，不重跑 |
| OpenReview、作者全部repo与PMLR | 本轮未刷新 | 沿用[启动清单](esp-official-launch-readiness-2026-10-16.md)各自时间戳；429不冒称本轮成功读取 |

本轮未下载或执行新源码，未得到新实现commit。以上是公开网页可见内容的阅读记录，不是作者全渠道审计，也不声称取得原始HTTP字节/SHA。既有31仓库/40分支、组织代码索引、arXiv源包、出版元数据审计仍由启动清单及其JSON承担，不重复搜索同一批入口来制造新增结果。

## 二、先排除已有证据不足以支持的解释

| 已完成检查 | 结果文件及字段/定位 | 当前边界 |
| --- | --- | --- |
| 原始四格输入/输出、owner和argmax全覆盖 | [全480复核JSON](esp-table1-nonofficial-full480-recheck-2026-10-16.json)及报告；四格318830 token通过 | 支持本地同次验证前向提交正确；不是作者实现认证，也不是独立AR全序列一致 |
| 逐prompt均值、13类等权、六来源组诊断 | [CPU差距报告](esp-table1-gap-analysis-2026-10-16.md)第二节及其JSON `eight_b` | 已检查聚合均未达到目标；作者权重未知，不能声称所有可能权重均已排除，也不能事后选权重报达标 |
| 尾部裁剪和prefill计数 | 同报告第二节；BC30/60加回未提交尾部只增加0.002248/0.003039，含prefill反而降低τ | 这两种简单账面变化不足以补主缺口；未提交token不能计作真实输出 |
| 预算增大与主/对照mask | 同报告第四节，30/1→60/1逐prompt τ为406胜/62平/12负 | 本地候选预算有效；不同输出轨迹及mask/深度/节点预算混杂，不能反推作者缺口原因 |
| 模型与数据的本地来源绑定 | 全480复核报告“范围与复用依据”“本轮实际复核与可重放入口”及原Study的modelscope/protocol证据 | 证明本地使用了已记录文件，不证明作者历史checkpoint或输入模板完全相同 |

## 三、作者合同缺口：什么证据才能收紧结论

下列是待核验条件，不是已证实的误差原因。优先级表示依赖关系，不是追加实验授权。

| 优先级/合同项 | 本地已固定 | 作者侧需要的最小证据 | 到位后先做的无GPU核验 |
| --- | --- | --- | --- |
| P0 来源、许可、入口 | 本地自实现及HF第三方已分开标注 | 作者身份与论文互相指向的repo/附件、不可变commit、许可、实际运行命令 | 核验身份/版本/许可，原字节manifest；确认真实入口而非空壳或索引 |
| P1 checkpoint/精度 | ModelScope Qwen3-8B文件绑定，BF16；作者历史revision未知 | Table1 checkpoint/tokenizer revision及作者精度配置 | 对比文件/配置，不把目前最新权重当历史作者权重；本项目仍仅运行BF16 |
| P1 数据/任务权重 | 原480/13类、qid顺序、首轮固定 | Table1实际qid、来源版本、任务清单、平均权重 | 按qid作集合/顺序/来源与权重对账；Figure8十标签或采样表八标签不能替代实际清单 |
| P1 输入token合同 | non-thinking模板、无改prompt；input_ids已锁定 | thinking、chat template、tokenizer及截断设置/输入摘要 | 对齐token IDs或模板配置；保留本批数据，差异只登记，不调prompt追τ |
| P1 长度/停止 | 256上限、EOS停止 | §4的100与Table1的256冲突的实际执行配置、EOS/stop列表 | 比较停止配置；现有总计不能重建前100 token轨迹，不将总计截断伪装成重放 |
| P1 BC/树/mean | 单mask主10/30/60，节点4/14/29；λ0.1逐提交token更新 | Algorithm1的B与BC映射、pruning/top1语义、块内mean更新顺序 | 阅读原生配置与调用链，逐项记录相同/不同/未知；60/2保持附加对照身份 |
| P2 τ计数与聚合 | decode committed/decode calls，另列两种主聚合及计数敏感性 | 逐prompt/逐任务accepted、bonus、calls、clip、prefill及最终权重 | 先CPU重算恒等式并按qid对齐；没有作者计数不估造“作者调用数” |
| P2 运行环境 | 历史环境随Run保留 | 作者依赖锁定与原生命令 | 记录可运行性和协议差异，不展开算子精度机理或测速 |

仅配置/计数到位但作者入口仍缺时，可以继续CPU对账，不启动8B。若作者只能提供FP32入口，记录协议不兼容，不能自行切换本项目精度；未知合同不自动等于允许改默认配方。作者侧qid或模板若与本批不同，先报告不可比之处，保留现有480，不将其偷偷替换成更有利的集合。

## 四、启动与停止规则

1. **当前不启动。** 官方实现和原生入口尚未取得，PR36复核已经覆盖本地全部主格；空闲GPU不是重复运行或修第三方的理由。
2. **新证据触发。** 仅当可访问的作者repo/附件、不可变commit、许可与原生入口能核验时，依[启动清单](esp-official-launch-readiness-2026-10-16.md)先迁入原字节源码/manifest，再核对固定Table1协议。外部状态未变化时不循环刷新同一搜索或受限附件。
3. **实际执行前。** 记录真实配置和已知合同差异，建立新Run而非重签旧成功记录；实时nvidia-smi确认GPU实际计算占用及显存余量，单队列、非抢占。CPU进程不作阻塞门。
4. **正确性门。** 原生入口预检必须每个提交token等于验证前向正确owner的logits argmax；独立AR一致率只报告。失败保留证据并停止该路径扩展，不编造τ，不启动算子数值链。
5. **通过后。** Qwen3-8B BF16、T0、固定SpecBench480、BC10/30/60，Qwen3 BC60单mask，λ0.1 mean及动态树剪枝；报告三种聚合、目标差值、AR诊断、失败与合同不一致。不测速；不因已见结果选择模板、样本或权重。

## 五、交付范围

本轮仅新增此缺口登记，并局部链接中英文研究计划、研究索引与启动清单；冻结Study、源码、原始Run和历史数字保持原样。提交/推工作分支/PR合dev及合后删除该已合远程分支沿用Enmao长期授权；不合main、不强推、不删本地分支或数据。实际检查、PR及远程分支清理结果以本轮PR记录为准，未执行动作不预写为通过。

## 六、会议记录与作者HF发布渠道追加核验

本轮继续执行只读来源追踪，不重跑PR36已完整的GPU矩阵。网页读取时间为2026-10-16约12:09–12:10（Asia/Shanghai），API实际时间见下表。

- [SlidesLive条目39075543](https://slideslive.com/39075543/efficient-trainingfree-multitoken-prediction-via-embeddingspace-probing)可读，面包屑列ICML2026/Posters，题名及四名作者对应本论文，页面日期为2026-07-06。可见文本为会议条目与摘要，未给出ESP repo、实现commit或原生运行命令。只读取网页文本，没有观看录屏、提取幻灯片/二维码或检查视频帧；不能据此断言视频中没有代码链接。页面日期不替代作者帖子列的海报场次日期。
- [HF论文页](https://huggingface.co/papers/2603.17942)的提交者链接指向[RaghavvGoel](https://huggingface.co/RaghavvGoel)，其账号公开链接指向已核验作者主页`raghavvgoel.github.io`。论文下可见作者评论说明免训练MTP方法，没有提供代码URL；自动推荐的其他论文不是ESP实现。本次身份关联来自这些公开链接，不声称平台完成了实名认证。
- 本轮另做`site.qualcomm.com "Embedding-Space Probing"`及论文号/GitHub定向网页检索，没有取得可核验新入口；摘要命中只作线索，未审计Qualcomm整站。直接读取既有论文短链仍返回工具`Internal Error`，未核验最终目标；没有绕过访问限制。OpenReview本轮未请求。

| 作者公开HF仓库API | 实际响应时间UTC | HTTP / 返回数 / 后续分页 |
| --- | --- | --- |
| [models](https://huggingface.co/api/models?author=RaghavvGoel&limit=100) | 2026-10-16T04:10:45.334443+00:00 | 200 / 0 / 无Link header |
| [datasets](https://huggingface.co/api/datasets?author=RaghavvGoel&limit=100) | 2026-10-16T04:10:45.335578+00:00 | 200 / 0 / 无Link header |
| [spaces](https://huggingface.co/api/spaces?author=RaghavvGoel&limit=100) | 2026-10-16T04:10:45.320613+00:00 | 200 / 0 / 无Link header |

三份原始响应均为2字节`[]`，SHA256均为`4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`，逐份重读哈希断言通过。[启动审计JSON](esp-official-launch-readiness-2026-10-16.json)的`author_hf_followup`记录三个URL/时间/哈希/计数；原始字节保留本机`.tmp/esp-author-hf-20261016T041044Z/`。网页阅读不冒称具有原始HTTP SHA。

这补齐了先前HF论文关联资产计数之外的**作者账号公开仓库列表**范围；仍不覆盖私有/组织所属资产、历史删除仓库、所有帖子或视频内链接。当前未取得作者原生入口，不能由三个空列表推断ESP未发布。后续新线索优先核验作者主动给出的repo/附件/原生命令；会议录屏内资源是未审阅项，不将其升级成完整源码已可下载或立即可运行。官方GPU启动顺序仍按第四节，本轮模型加载/Run/GPU执行均为0。
