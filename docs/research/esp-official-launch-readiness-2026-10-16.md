# ESP官方Table1启动就绪与阻塞清单

最新来源核验：`2026-10-16T02:14:02.904081+00:00`；两位已确认作者的公开组织/事件/本人PR未带来可核验入口，OpenReview一次正常刷新仍429。
官方repo/实现commit/原生入口仍缺失；本轮无GPU操作、无新τ。入口到位后立即按固定480、8B BF16/T0、BC10/30/60单mask及同前向argmax门执行；4B后续对照排在官方8B之后。

初始GPU快照检查时间：`2026-10-15T23:54:54.960767+00:00`（历史快照，非本轮实时准入）。最新授权允许SD官方Table1/8B任务优先使用GPU；固定prompt、不新造方法、不抢占现有作业。

## 当前执行状态

- **尚无可执行官方入口**。本地交接、作者主页ESP条目、PMLR出版页及本轮有界公开检索未得到新增、可核验的作者repo/commit/原生入口。完整来源证据沿用[PR26重查](esp-official-recheck-2026-10-16.md)，不能把搜索不到写成未开源的证明。
- 实际GPU观测：`NVIDIA GeForce RTX 5090 D v2, 2035 MiB, 22001 MiB, 0 %`。最新实际GPU列表无实验Python，利用率0%、空闲22001MiB；Docker Desktop界面不当作实验作业。精简观测见[本次启动状态JSON](esp-official-launch-readiness-2026-10-16.json)。这是容量/占用快照，不是性能测速，也没有枚举CPU脚本作为准入门。
- 本次没有建立新Study/Run、加载权重或模型，没有抢占/杀进程。GPU现已空闲，当前可确定的前置缺口是官方入口未取得；GPU优先授权不能补出尚未核验的本地官方代码。

## 官方入口到位后的固定启动顺序（未执行）

| 顺序 | 必须具备的证据 | 当前状态 |
| --- | --- | --- |
| 1 | 作者身份与论文互相指向的repo/附件、实际commit/许可和原生入口 | 缺失；不建空壳src或编造manifest |
| 2 | 原字节源码与manifest；入口能表达Qwen3-8B BF16、T0、原480、BC10/30/60、Qwen3单mask/λ0.1/动态剪枝及停止规则 | 尚不能核验，不用自实现代替 |
| 3 | 实际nvidia-smi非抢占准入，容量满足该入口的模型工作集加余量、单串行队列 | 最新快照已空闲；取得官方入口后须再次核对实时占用及该入口容量，不能把单次快照当长期预约 |
| 4 | 原固定输入预检，每个提交token等于验证forward正确owner的argmax；AR只诊断 | 未执行官方入口，不沿用旧自实现数学门充数 |
| 5 | 通过后运行官方480（BC10/30/60单mask），报告τ与1.63/1.74差值及所有失败/边界 | 未执行；不能把旧1.563378/1.647301更名为官方结果 |

## 研究计划与可继续工作

当前CPU差距分析及出版版核验已经完成，见[差距报告](esp-table1-gap-analysis-2026-10-16.md)。作者侧逐任务计数、纳入/权重、输入/停止/预算合同仍缺失，当前没有能凭本地结果继续确认的作者因果结论；不循环重复同一矩阵或修失败第三方来占卡。研究计划按“官方入口与实际准入满足后SD优先”更新，bias/random/Kalman和算子机理继续后置。

本文件记录执行前置条件与实际阻塞，不把授权或计划当作已运行证据。没有向用户发起确认弹窗；待可核验入口或外部状态变化后执行后续步骤。

## 作者repo/commit与附件追加追踪

[本轮只读跟进](esp-author-attachment-followup-2026-10-16.md)核对15个响应：主页commit未变，三个作者/组织精确论文号代码查询各0项，论坛ID6个命中逐项仅识别为元数据/索引/第三方记录；PMLR固定出版元数据extras为空。三个OpenReview常规附件候选均403，字段存在性未核验，未取得ZIP/PDF。官方实现repo/commit/入口仍为null，未启动GPU；主页/出版commit不冒充实现版本。

## 共同作者与历史版本追加核查

[共同作者/历史跟进](esp-coauthor-history-followup-2026-10-16.md)扩展检查19份响应：第一作者index最近10个版本的ESP条目均只链接论文；Mukul Gagrani主页ESP条目只链接PDF，网站repo最新commit不当作实现commit；PMLR条目历史extras仍为空。标题README检索未形成作者互指入口。本轮未重复相同OpenReview403请求，官方实现仍未核验，未启动GPU；此前附件访问限制保留原时间。

## 官方组织README与最新访问状态

[官方组织追加核查](esp-organization-readme-followup-2026-10-16.md)覆盖两个组织215个公开仓库元数据和10个固定commit的候选README，未核验到ESP作者实现入口。一般speculative decoding条目不等于该论文实现，未声称完成全代码审计。本次OpenReview note请求实际返回429，已停止进一步请求；附件字段仍未知，不把旧403或新429当作未开源证明。官方repo/commit/entrypoint仍为null，本轮无GPU操作；入口到位后按上表重新核对实际准入。

## 作者公开议题、旧题名与代码发布线索

本轮来源时间及10份实际GitHub响应SHA见[启动审计JSON](esp-official-launch-readiness-2026-10-16.json)的`release_lead_followup`；响应与第三方正文仅留本机`.tmp/esp-release-leads-20261016T011943Z/`，没有迁入科学源码。

新增确认了[第一作者本人发布的论文议题](https://github.com/Xiaohao-Liu/Awesome-Multi-Token-Prediction/issues/2)：账号`RaghavvGoel`与已核验作者主页对应，2026-04-23发布、2026-04-28更新。正文只给论文题名与arXiv链接；唯一[维护者回复](https://github.com/Xiaohao-Liu/Awesome-Multi-Token-Prediction/issues/2#issuecomment-4331772613)确认已收录，没有代码或附件地址。此次只读核验未留言或联系作者。作者发帖身份是新增直接来源，但议题本身不是ESP实现repo/commit。

| 追加公开检索 | API实际结果 | 限制/解释 |
| --- | --- | --- |
| GitHub提交：精确论文号 | 0 | 提交消息检索，不覆盖所有代码正文/分支 |
| GitHub提交：Embedding-Space Probing | 返回17项，`incomplete_results=true` | 搜索并不完整，宽词命中不自动归属该论文；没有据此确认作者入口 |
| GitHub提交：早期完整题名Training-Free Multi-Token Prediction via Probing | 0 | 题名/索引限制，不证明无代码 |
| GitHub议题/PR：论文号、短题名 | 分别15、30项，API均未标记不完整 | 包含同一作者议题、论文清单、第三方agent候选及宽词噪声；并非45个独立官方资产，未逐个审计全部附件 |
| GitHub仓库：早期完整题名 | 0 | 不覆盖未在仓库元数据中标题的实现 |
| 已确认两位作者RaghavvGoel/mgagrani的公开gist列表 | 各0 | 仅公开列表，不涉及私有gist或其他作者同名身份 |

[ICML Downloads公开目录](https://icml.cc/Downloads/2026)包含该论文题名；会议poster候选`https://icml.cc/virtual/2026/poster/61857`仍未取得页面资源字段：本轮web搜索报告该路径被robots.txt阻止，未用其他工具绕过。第三方索引只能给候选URL，不能据此认证代码或附件。[旧题名论文](https://openreview.net/pdf?id=Drfx9Gnqrv)在搜索索引可见，不等于本轮成功取得OpenReview附件。近期429后本轮对OpenReview实际请求为0，访问状态沿用原时间，不虚报新请求。

**启动状态不变：官方repo/commit/entrypoint缺失，未启动GPU、没有新τ。** 目标仍为BC30/60的1.63/1.74；本次更新不改变480条prompt、BF16/T0、单mask、argmax门或冻结Study。后续只依据新增的作者/出版代码链接、可访问附件字段或身份可核验的发布事件继续；入口到位立即按上表原字节/协议/实际非抢占准入顺序执行，不再次等待授权。现有自实现与失败HF第三方仍不得改称官方。

### 作者arXiv v2源包核验

论文[固定v2页面](https://arxiv.org/abs/2603.17942v2)明确提供TeX Source链接；从该[官方源包](https://arxiv.org/src/2603.17942v2)实际取得HTTP200/application-gzip，1,895,189字节，SHA256=`734691dea1e1af91e8375a5306d1f0c0548677db44f86e6f6db0bab833811beb`。这是作者上传论文源包的版本/哈希，**不是ESP实现commit**。

只在内存读取tar目录和选定文本：37个条目（34个普通文件、3个目录），内容为TeX/参考文献/样式/论文图片；目录中没有Python/notebook/shell/ZIP实验文件或anc/code/src/scripts目录。16份TeX/JSON逐一记录原字节SHA，未找到GitHub/GitLab/HF代码仓库URL；扫描范围不含参考文献、样式、PDF和图片内部文本，不作更广的无链接断言。未解包到src、未执行任何源包内容。

现有审计JSON在10份GitHub响应之外追加这一份arXiv源包响应及其完整成员清单/16份文本SHA。本次补到了可访问的作者原始资料，但其中未识别到原生实验入口；因此官方实现与GPU启动状态保持缺失/未运行。不能用论文TeX中的算法描述自行重写来代替原码要求。

## 作者v1源包、公开分支与release附件核验

本轮实际时间、10份响应SHA、源包清单、20份文本成员SHA及固定branch commit见[启动审计JSON](esp-official-launch-readiness-2026-10-16.json)的`author_versions_followup`。原始响应留本机`.tmp/esp-author-versions-20261016T013746Z/`；没有重复请求OpenReview或操作GPU。

| 新来源 | 核验结果 | 边界 |
| --- | --- | --- |
| [作者arXiv v1源包](https://arxiv.org/src/2603.17942v1) | HTTP200/gzip，1,895,426字节；41条目、39普通文件，20份TeX/JSON；未识别实验脚本或anc/code/src/scripts目录 | 与v2压缩包字节不同，不能复用v2 SHA；只在内存读取，未解包/执行 |
| 第一作者主页repo公开分支/release | 1分支master，commit `039d875e79ee55a032f2f7ba6c58651825cdc0f0`；release 0 | 固定分支树160条目；路径筛查只命中论文图片，不称全文代码审计 |
| Mukul Gagrani主页repo公开分支/release | main `5eba01028084ccc00d1cbaad6212b2bf750e2579`、gh-pages `557f1837646967b032c9fb1e04de33f70b33a6cc`；release 0 | 固定分支树分别433/393条目；main命中普通网站notebook/引用更新脚本，未据此认定ESP实现 |
| [共同作者固定版本出版元数据](https://github.com/mgagrani/mgagrani.github.io/blob/5eba01028084ccc00d1cbaad6212b2bf750e2579/_bibliography/papers.bib) | 唯一匹配ESP题名的`ssd`条目有pdf字段，只链接arXiv论文；没有code字段 | 仅该已确认作者网站条目，不认领同名其他账号 |

v1源包SHA256为`6170a5b8a630017e3ff373b1285c312e5a6e21c15a54ebc2c33c8cba10667e83`。与此前v2做目录差集，v1独有15条、v2独有11条，涉及论文图表/参考文献及camera-ready布局；没有由此得到原生实验入口。20份TeX/JSON未命中GitHub/GitLab/HF仓库URL，扫描不包含参考文献/样式/图片内部文本。不能把历史表格或旧论文算法当作可执行官方代码。

三个分支树均由API完整返回（truncated=false），但本次只做路径筛查和指定出版条目核对，未声称逐个审计全部网站文件。两个release列表为空仅说明该两个主页repo未返回公开release，不代表全部作者仓库没有资产或作者未开源。10份响应、20份文本成员及1份出版原文SHA复核通过；没有新Study、Run或τ。

**当前仍缺可核验作者实现repo/commit/entrypoint，官方复现未执行。** 启动顺序补全为本次指定的SpecBench固定全480、Qwen3-8B BF16、T0、BC10/1、30/1、60/1；目标BC30 τ=1.63、BC60 τ=1.74。取得原生入口后固定原字节与manifest，实际nvidia-smi非抢占准入、单队列，数学门为每个提交token等于该次验证前向正确owner的argmax；独立AR仅报告。固定prompt，不用自实现/第三方冒充官方，不钻算子、不测速、不用逆映射，不因v1资料改变冻结主协议。

补查共同作者[mgagrani公开repo列表](https://api.github.com/users/mgagrani/repos?per_page=100&type=owner)：分页实际共9个，8个非主页仓库最后推送于2017–2020年，另一为上述主页。名称/描述/推送时间保留在同一审计JSON，未出现新的ESP命名线索；仅为元数据核验，不能据旧日期排除旧库其他分支内存在相关内容。该一份响应追加后，本轮共10份响应、20份成员与1份出版原文SHA复核通过。

## 已确认作者的公开发布渠道追踪

新增7份响应的URL/查询/时间/SHA见[启动审计JSON](esp-official-launch-readiness-2026-10-16.json)的`public_channels_followup`。本机原始响应保存在`.tmp/esp-author-publication-channels-20261016T021319Z/`；公开审计只保留必要计数/范围，不搬运无关早年PR正文。

| 公开渠道 | 第一作者RaghavvGoel | 共同作者mgagrani | 判断边界 |
| --- | --- | --- | --- |
| 公开组织列表 | 0 | 0 | 仅公开可见，不代表作者不属于机构或私有组织 |
| 公开事件列表 | 4项，均为已查主页的PushEvent，实际返回时间范围2026-09-20至10-13 | 0项 | 仅API实际返回窗口，不代表全部历史/隐藏活动 |
| 本人发起PR检索 | 7项，最近更新时间2019-10-30 | 1项，更新时间2017-08-25 | API均incomplete_results=false；未由这些记录取得ESP入口，不将旧日期当无代码证明 |

上述账号均沿用已核验作者主页身份，不给其他同名个人网页或GitHub账号自动归属。查询只读，没有发消息/议题或请求作者授权，未改变仓库或模型来源。

距离此前OpenReview note限流已超过一小时，本轮仅正常刷新一次同一[公开API](https://api2.openreview.net/notes?id=mKj4fO0BU4)：`2026-10-16T02:14:02.904037+00:00`实际仍返回429/text-html、162字节，未返回Retry-After；响应SHA与前次相同，为`413d294fad14524bf94e764b33ff0f327682549408545171fcf9240189c154ae`。未取得code/supplement字段；已停止进一步请求，不尝试替代路由、代理或受限附件路径。访问失败不证明未开源。

本轮7份响应SHA及公开查询计数复核通过；官方repo/实现commit/entrypoint仍null，没有GPU测量、模型加载、Run、τ或新方法。启动所需缺口仍为能核验作者来源的原生代码/附件，不将新增的公开活动记录、论文源包或历史自实现当作官方实现。按最新次序先解决并运行官方8B，再推进所需4B BF16五方法加AR；现有4B历史结果保留，本轮不重跑已有格子。固定prompt、argmax正确性门和AR仅诊断不变，不钻算子、不测速、不用逆映射、不合main。
