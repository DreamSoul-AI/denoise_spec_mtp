# ESP官方组织仓库README追加核查

本轮完成时间：`2026-10-16T01:00:38.012402+00:00`。仍未核验到作者ESP实现repo/commit/原生入口；本次不启动GPU、不改输入或算法。新增覆盖两个官方组织的215个公开仓库元数据、10个候选固定版本README。OpenReview最新note请求返回429，已停止进一步请求。

## 来源与实际覆盖

通过GitHub API分别取得[qualcomm](https://github.com/qualcomm)的163个、[Qualcomm-AI-research](https://github.com/Qualcomm-AI-research)的52个公开仓库元数据。按仓库名称与描述筛选语言模型、解码、多token及推理相关词，实际正则与字段见[审计JSON](esp-organization-readme-followup-2026-10-16.json)；选出10个候选。逐个取得默认分支head，再按该commit读取原始README，保存commit、blob SHA、原字节SHA256及关键词行号。

| 候选README（链接固定commit） | 实际commit | 检查结果 |
| --- | --- | --- |
| [qualcomm/cloud-ai-sdk](https://github.com/qualcomm/cloud-ai-sdk/blob/812c3852fdfe53c0579a858478a7313ca49ef117/README.md) | `812c3852fdfe53c0579a858478a7313ca49ef117` | L39：CodeGen speculative decoding示例，未形成ESP作者互指 |
| [qualcomm/efficient-transformers](https://github.com/qualcomm/efficient-transformers/blob/d4b48b333baecb8e18cefc38471016c1defd1ff4/README.md) | `d4b48b333baecb8e18cefc38471016c1defd1ff4` | L45/58：draft-based/多投影头及TLM功能，未形成ESP作者互指 |
| [qualcomm/llama.cpp](https://github.com/qualcomm/llama.cpp/blob/59d5fad7c111d30a547d690b69235ed9e05c035d/README.md) | `59d5fad7c111d30a547d690b69235ed9e05c035d` | 未命中论文号、ESP或论文标题关键词 |
| [qualcomm/vllm](https://github.com/qualcomm/vllm/blob/a810299838739b32fea9ecdb6eb32bc845aca6c5/README.md) | `a810299838739b32fea9ecdb6eb32bc845aca6c5` | L36：通用speculative decoding功能，未形成ESP作者互指 |
| [qualcomm/geniex-proc](https://github.com/qualcomm/geniex-proc/blob/6b68dd0de5b9a84c316cc3babfe9f2477d9c6079/README.md) | `6b68dd0de5b9a84c316cc3babfe9f2477d9c6079` | 未命中论文号、ESP或论文标题关键词 |
| [Qualcomm-AI-research/transformer-quantization](https://github.com/Qualcomm-AI-research/transformer-quantization/blob/8dbf3c6419691597de7997792d75e826b8f0efc7/README.md) | `8dbf3c6419691597de7997792d75e826b8f0efc7` | 未命中论文号、ESP或论文标题关键词 |
| [Qualcomm-AI-research/geometric-algebra-transformer](https://github.com/Qualcomm-AI-research/geometric-algebra-transformer/blob/6afc26f26b8fcf51136ae8c1d264a36e14b6e497/README.md) | `6afc26f26b8fcf51136ae8c1d264a36e14b6e497` | 未命中论文号、ESP或论文标题关键词 |
| [Qualcomm-AI-research/outlier-free-transformers](https://github.com/Qualcomm-AI-research/outlier-free-transformers/blob/1e59744972da808a90d9996027bfc274689594b8/README.md) | `1e59744972da808a90d9996027bfc274689594b8` | 未命中论文号、ESP或论文标题关键词 |
| [Qualcomm-AI-research/llm-surgeon](https://github.com/Qualcomm-AI-research/llm-surgeon/blob/726734425b6866782048877bac0c0d90e8cb36b3/README.md) | `726734425b6866782048877bac0c0d90e8cb36b3` | 未命中论文号、ESP或论文标题关键词 |
| [Qualcomm-AI-research/neodragon](https://github.com/Qualcomm-AI-research/neodragon/blob/d2abbe99f46577c4e1db682ad3c26832ec0c23b9/README.md) | `d2abbe99f46577c4e1db682ad3c26832ec0c23b9` | 未命中论文号、ESP或论文标题关键词 |

十个README中，论文号`2603.17942`、完整/短论文标题及独立ESP词均零命中；三个仓库包含一般speculative decoding条目。上述条目没有提供已确认的ESP论文作者代码关系，因此不将它们或组织归属本身当作官方复现入口。这里是README关键词及命中上下文核查，不声称审计了215个仓库全部源码、分支、历史、附件或链接下的全部文档；不能由零命中推出作者未开源。

23份API响应（两份组织列表、十份head、十份README响应、一份OpenReview响应）和十份原始README的本机快照全部SHA复核通过。原始第三方正文与完整API响应只保存在`.tmp/esp-organization-followup-20261016T005740Z/`；公开JSON记录来源、时间、SHA和关键词行号，不搬运第三方全文。

## OpenReview访问边界

本次唯一请求为[公开note API](https://api2.openreview.net/notes?id=mKj4fO0BU4)，实际返回HTTP429及HTML限流页面（162字节），未取得note字段或附件URL。未捕获Retry-After响应头，不编造等待秒数；本轮不继续请求OpenReview，也不切换路径绕过限制。此前403附件候选保留在[历史审计](esp-author-attachment-followup-2026-10-16.md)，不将它们写成本次新响应，亦不据此断言附件不存在。

## 启动清单与后续

官方实现repo、commit、entrypoint均继续为null。当前缺口是可验证的原作者入口及其协议，不是GPU授权；本次没有GPU容量检查、模型加载、新Study/Run或τ结果。旧自实现BC30/60的1.563378/1.647301仅为[历史差距参考](esp-table1-gap-analysis-2026-10-16.md)，目标仍为1.63/1.74，未冒充官方结果。

[启动清单](esp-official-launch-readiness-2026-10-16.md)继续适用：取得作者互指代码/附件后，固定原字节与来源manifest，核对原生入口能表达冻结480、Qwen3-8B BF16/T0、BC30/60单mask协议；随后实际nvidia-smi非抢占准入、原输入数学argmax预检，通过后串行跑全量。AR一致率只报告；不改prompt，不修失败第三方、不造新ESP方法、不恢复算子机理或测速。

本轮补正根README仍残留的旧“量化优先”调度文字为当前官方路径优先，研究计划经现有启动清单链接取得本次新增来源证据；不回写冻结Study合同。下一次来源核验应以可新增的作者/出版代码链接、可访问附件字段或外部状态变化为依据，不用相同限流请求循环代替复现进展。
