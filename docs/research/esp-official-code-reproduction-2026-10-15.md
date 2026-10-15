# ESP 原作者官方代码复现报告：来源核查与执行边界

核查日期：2026-10-15。**本轮未核验到可按原字节迁入并使用原生入口运行的 ESP 作者官方实现，故未启动新的 8B 复现。** 这是公开来源核查结论，不能写成“已证实作者没有公开代码”：OpenReview 的补充材料/代码字段访问尚不完整。本次按“查不到官方代码则记录证据交回”的指示交付；不以第三方包或已有自实现替代。

本报告负责 SD / ESP。量化任务的作者代码、baseline 和结果不在本仓证据范围内，未借用其他任务数字，也不宣称量化复现完成。

## 一、来源与身份核查

逐次请求时间、HTTP/API 状态、查询参数、返回计数和响应 SHA256 见 [esp-official-source-audit-2026-10-15.json](esp-official-source-audit-2026-10-15.json) 的 `sources`。原始网页/API 响应在本机 `.tmp/esp-official-source-20261015/` 保留，未将整页第三方正文或代码提交进仓库。

| 来源 | 实际核查 | 结论与边界 |
| --- | --- | --- |
| [arXiv 摘要](https://arxiv.org/abs/2603.17942)、[v2 正文](https://arxiv.org/html/2603.17942v2) | 读取全文外链及方法/实验章节 | 未发现作者 ESP 仓库/项目/专用 checkpoint 链接。正文的 Prompt Lookup Decoding 仓库属于 baseline，页脚 GitHub issue 属于 arXiv HTML 服务，均不是 ESP 代码。 |
| [PMLR 正式出版页](https://proceedings.mlr.press/v306/goel26a.html) | 读取 Related Material / 外链 | 提供论文 PDF 及 [OpenReview](https://openreview.net/forum?id=mKj4fO0BU4)，未给出可直接核验的 ESP 仓库或下载包。 |
| [ICML 官方 poster 页面](https://icml.cc/virtual/2026/poster/61857) | 从会议 Downloads 标题链接定位，直接请求成功并读取外链 | 链接同一 OpenReview；未发现 ESP 代码/项目/HF 下载链接。导航中的 Code of Conduct 不是源码入口。 |
| [第一作者主页](https://raghavvgoel.github.io/)及其 GitHub | 固定主页仓库 commit `039d875e79ee55a032f2f7ba6c58651825cdc0f0`；公开仓库列表返回 22 个 | ESP 条目仅链接 Paper；未识别出作者 ESP 实现。该 commit 是主页版本，不是 ESP 实现版本。 |
| [qualcomm](https://github.com/qualcomm)、[Qualcomm-AI-research](https://github.com/Qualcomm-AI-research) | 分页读取公开仓库元数据，分别 163 / 52 个；按论文号查询代码 | 未核验到与论文/作者相互印证的 ESP 实现。元数据和索引检索不等于逐文件审计所有仓库。 |
| GitHub 仓库/代码搜索 | 精确论文标题、加引号论文号；分别检索作者及两组织中的论文号 | 命中列表保留在审计文件；作者/两组织限定代码查询均为零。全局结果含本项目、论文列表及无关命中，不能因名称或提及论文就认定为官方。 |
| [HF 论文页](https://huggingface.co/papers/2603.17942)及[提交作者账号](https://huggingface.co/RaghavvGoel) | 论文 API 的关联 model/dataset/Space 均为零；作者公开 model/dataset/Space 列表均为空 | 未得到作者 ESP 发布物。HF 关联元数据不完整的可能性保留。 |
| OpenReview | PMLR 链接的论坛及 API；另核对搜索发现的早期稿入口 | 论坛返回浏览器验证页，API 返回 HTTP403；不能据此声称补充材料不存在。未绕过验证，未核验任何可能的附件源码。 |

官方 ESP 仓库 URL、实现 commit、原生入口和论文实际 checkpoint revision 目前均为未核验，审计文件相应值为 `null`；未编造源码 manifest，未建立空壳“官方实现”目录。若后续得到可访问的作者发布物，再按实际文件形成逐文件来源及 SHA manifest。

## 二、发现但不采用的第三方包与通用权重

[Harshvardhan-Mestha/esp-reproduction-artifacts](https://huggingface.co/datasets/Harshvardhan-Mestha/esp-reproduction-artifacts) 的固定 revision 为 `ad76f8da29f3bfc7faa20488193c6aa83a9f708c`。其 README 将自身称为复现产物，发布者未在本次核查中获得论文作者身份或官方背书验证，且其代码使用自己的 prompt 与设置。因此不迁入 `src`、不执行、也不引用其中 τ 冒充本项目原生复现。只下载本机核查的 `code/esp_v6.py` SHA256 为 `089192cd3b47b3b3d32b19963b0c8d5ca0c71f23fbd4eda8a214b2b8b1cae3b2`；这只是排除候选的证据，不是官方代码 manifest。来源为审计文件 `rejected_third_party` 和固定版本响应。

[Qwen/Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B) 通用基座仍可获得；本次 HF API 返回 revision `b968826d9c46dd6066d109eabc6255188de91218`，它不是已确认的论文实际 revision。此前 [ModelScope 内容核验](../../studies/esp_table1_bf16_full_argmax/docs/modelscope-content-verification-v1.json)保留，未重新下载权重。ESP 不修改模型权重的性质不能补足作者代码与作者运行设置的缺口。

## 三、原作者代码协议下的 baseline 执行清单

**以下均未执行，没有本轮 observed τ、差值或 Run 文件。** 论文目标来自 [arXiv v2 Table 1](https://arxiv.org/html/2603.17942v2#S4.T1) 的 Qwen3-8B 行，已从原始 HTML 表格提取到审计文件的 `paper_table` 与 `official_protocol_baselines`，不是本机运行结果。未执行项保留 `null`，不填零、不用历史数替代。

| 方法 | BC | 论文 τ | 本轮官方代码 τ | 相对论文差值 | 本轮结果文件 |
| --- | --- | --- | --- | --- | --- |
| ESP | 10 | 无 Table 1 目标 | 未执行 | 不可计算 | 无 |
| ESP | 30 | 1.63 | 未执行 | 不可计算 | 无 |
| LADE | 30 | 1.55 | 未执行 | 不可计算 | 无 |
| PLD | 30 | 1.31 | 未执行 | 不可计算 | 无 |
| STAND | 30 | 1.42 | 未执行 | 不可计算 | 无 |
| ESP | 60 | 1.74 | 未执行 | 不可计算 | 无 |
| LADE | 60 | 1.73 | 未执行 | 不可计算 | 无 |
| PLD | 60 | 1.31 | 未执行 | 不可计算 | 无 |
| STAND | 60 | 1.48 | 未执行 | 不可计算 | 无 |

Table 1 的 PLD 使用固定 depth-10 树、BC 约为 10，只是重复列于两个预算栏供参考，不能写成 PLD 已按 BC30/60 执行。ESP 的 BC10 没有 Table 1 目标。PLD/STAND/LADE 的本次官方代码结果也均缺失，不将其论文数字当作已复现。

## 四、历史自实现结果：仅作参考，不满足本轮要求

以下来自已验收 [protocol_evidence_v1.json](../../studies/esp_table1_bf16_full_argmax/docs/protocol_evidence_v1.json) 的 `cells[]`，完整精度与逐 prompt 证据仍在原文件；审计 JSON 的 `historical_self_implementation` 另存本次引用值和原文件哈希。它们是此前按论文自行实现的结果，**不能称为原作者官方代码运行结果**，本轮没有重新执行或重新签收。

| BC/mask | 历史 Run ID | pooled τ | 论文目标 | 历史值−目标 | 独立 AR 完全一致 | 历史 argmax 审计 token |
| --- | --- | --- | --- | --- | --- | --- |
| 10/1 | dfe1b9c8d5d12e92 | 1.399047 | 无目标 | 不适用 | 188/480 | 79,757 / 全过 |
| 30/1 | b9b54923b1b9ea9f | 1.563378 | 1.63 | -0.066622 | 175/480 | 79,762 / 全过 |
| 60/1 | 3f3d0f9a84341c0b | 1.647301 | 1.74 | -0.092699 | 185/480 | 79,618 / 全过 |
| 60/2 | 555ff70d57ce05b0 | 1.603729 | 1.74 | -0.136271 | 187/480 | 79,693 / 全过 |

这些旧格的数学自检及原生生命周期通过，BC30 与 BC60 单 mask 的 τ 目标仍未达到。三种聚合及双 mask 对照见 [历史报告](../../studies/esp_table1_bf16_full_argmax/docs/STUDY_REPORT.md)；不能事后选聚合、预算或 mask 数来宣称复现。新的官方代码协议下正确性门尚未执行，旧审计通过不替代新协议验收。

## 五、拿到官方代码后的执行边界（尚未执行）

- 作者身份及论文链接先交叉核验；固定实际 repo/commit/license，按原始字节迁入 `src`，逐文件 SHA manifest 核对，保持作者原生入口。若原入口无法表达目标协议或无法审计提交 token，则先报告真实差异，不自行重写解码器或偷偷改入口。
- 仅此 ESP 复现使用 Qwen3-8B，BF16、T0、SpecBench 全 480、BC10/30/60；Qwen3 BC60 按 Appendix G.2 用单 mask，λ=0.1 updating mean；停止规则与长度等设置必须与作者实际入口核对、披露，不自行冒充已确认。
- 启动前采用非抢占准入：检查共享 GPU 任务、显存及已有预约；资源被占用时不启动、不抢、不杀其他进程。当前没有官方可运行入口，本轮未请求 GPU 准入、未排队或启动模型任务。
- 每个提交 token 必须等于对应验证前向 logits 的 argmax，覆盖输出全长；独立 AR 一致率及首分叉只报告，不作失败门。逐 prompt 原始计数形成结果文件后再算 τ 和论文差值；不测速、不恢复 BF16 算子机理、不新增 FP32 模型实验。

当前交回事项：官方实现/附件仍未核验，需可访问的作者来源才能进入按原字节迁入与原生执行阶段。未用自实现再跑矩阵，未将检索不全包装成“作者未开源”的定论。本轮交付为来源核查、baseline 未执行清单与旧结果边界；量化任务另需其自身作者实现和结果证据。
