# ESP官方Table1启动就绪与阻塞清单

检查时间：`2026-10-15T23:54:54.960767+00:00`。最新授权允许SD官方Table1/8B任务优先使用GPU；固定prompt、不新造方法、不抢占现有作业。

## 当前执行状态

- **尚无可执行官方入口**。本地交接、作者主页ESP条目、PMLR出版页及本轮有界公开检索未得到新增、可核验的作者repo/commit/原生入口。完整来源证据沿用[PR26重查](esp-official-recheck-2026-10-16.md)，不能把搜索不到写成未开源的证明。
- 实际GPU观测：`NVIDIA GeForce RTX 5090 D v2, 2035 MiB, 22001 MiB, 0 %`。最新实际GPU列表无实验Python，利用率0%、空闲22001MiB；Docker Desktop界面不当作实验作业。精简观测见[本次启动状态JSON](esp-official-launch-readiness-2026-10-16.json)。这是容量/占用快照，不是性能测速，也没有枚举CPU脚本作为准入门。
- 本次没有建立新Study/Run、加载权重或模型，没有抢占/杀进程。GPU现已空闲，当前可确定的前置缺口是官方入口未取得；GPU优先授权不能补出尚未核验的本地官方代码。

## 官方入口到位后的固定启动顺序（未执行）

| 顺序 | 必须具备的证据 | 当前状态 |
| --- | --- | --- |
| 1 | 作者身份与论文互相指向的repo/附件、实际commit/许可和原生入口 | 缺失；不建空壳src或编造manifest |
| 2 | 原字节源码与manifest；入口能表达Qwen3-8B BF16、T0、原480、BC30/60、Qwen3单mask/λ0.1/动态剪枝及停止规则 | 尚不能核验，不用自实现代替 |
| 3 | 实际nvidia-smi非抢占准入，容量满足该入口的模型工作集加余量、单串行队列 | 最新快照已空闲；取得官方入口后须再次核对实时占用及该入口容量，不能把单次快照当长期预约 |
| 4 | 原固定输入预检，每个提交token等于验证forward正确owner的argmax；AR只诊断 | 未执行官方入口，不沿用旧自实现数学门充数 |
| 5 | 通过后运行官方480，报告τ与1.63/1.74差值及所有失败/边界 | 未执行；不能把旧1.563378/1.647301更名为官方结果 |

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
