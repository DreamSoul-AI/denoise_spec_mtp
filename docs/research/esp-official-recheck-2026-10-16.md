# ESP官方路径重查与出版版协议核验

当前状态：2026-10-16重新检查可访问作者/出版方/HF入口，仍未核验到可运行作者代码或论文专用checkpoint。
新证据：PMLR正式PDF的Table1目标仍为BC30 τ=1.63、BC60 τ=1.74；本地差距不由目标值改版解释。
出处：[请求与SHA审计](esp-official-recheck-2026-10-16.json)，UTC检查时间为`2026-10-15T23:43:17.031227+00:00`。
执行：本轮只做HTTP/API与PDF文本核验，未加载模型、未申请GPU、未开8B/4B Run、未测速。
下一步：保留Table1任务/权重、作者入口及完整输入/停止/预算合同缺口；不因GPU空闲重复自实现或已失败第三方路径。

## 一、当前是否有可执行官方路径

| 直接来源 | 本次实际结果 | 判断边界 |
| --- | --- | --- |
| [PMLR正式出版页](https://proceedings.mlr.press/v306/goel26a.html) | HTTP200，Related Material链接PDF及OpenReview | 未得到ESP实现入口；网页编辑/出版方GitHub不是作者算法仓库 |
| [作者主页](https://raghavvgoel.github.io/) | HTTP200；ESP条目只链arXiv论文 | 不能把其他作者项目当本论文实现 |
| [作者公开仓库API](https://api.github.com/users/RaghavvGoel/repos?per_page=100) | HTTP200，返回22个仓库元数据，未识别到可相互核验的ESP实现 | 不是22个仓库逐文件审计，不涵盖私有资产；本轮未重新枚举Qualcomm两组织全部仓库 |
| [HF论文API](https://huggingface.co/api/papers/2603.17942)及作者model/dataset/Space列表 | 论文关联三类发布物计数均0，作者三类列表各0 | HF关联可能不完整；通用Qwen3-8B权重不能补足ESP作者入口 |
| [OpenReview](https://openreview.net/forum?id=mKj4fO0BU4)及API | 论坛跳转浏览器验证页，API403 | 未绕过验证，无法核验潜在补充代码，不能宣称不存在附件 |
| [出版方paper目录API](https://api.github.com/repos/mlresearch/v306/contents/assets/goel26a) | HTTP404，但正式页链接PDF实际HTTP200 | 只记录不一致响应；不由404推断该目录或全部补充材料不存在 |

本次没有可固定的作者实现repo/commit/entrypoint或论文实际checkpoint revision，相应审计值为null；没有建立空壳src目录或编造可运行manifest。公开检索未核验到入口不是“作者没有开源”的证明。旧[完整来源核查](esp-official-code-reproduction-2026-10-15.md)独立保留；本次为有界刷新，不冒称重做所有组织仓库/附件检查。

指定HF第三方仍是[非官方失败尝试](esp-third-party-reproduction-2026-10-15.md)：原预检首token数学门失败、有效τ为null。本次没有更新其算法、换prompt、借用其上游τ或再次占GPU。此前4B五方法加AR和方向六格已经完成，不以本次空闲为由重跑已有数字。

## 二、PMLR出版版与当前差距

来源：[正式PDF](https://raw.githubusercontent.com/mlresearch/v306/main/assets/goel26a/goel26a.pdf)，22页，SHA256 `436c32dc4580f3f3eeae88c0f99140289576f2ddd7a5984ad0105ab9f1ddd36a`。本机原PDF及逐页提取文本只留审计所指`.tmp`，Git保存URL、响应SHA、页码、表数值及边界，不上传整篇第三方论文。

| 核验项 | 正式PDF定位 | 当前结论 |
| --- | --- | --- |
| Qwen3-8B Table1 | PDF第7页；交错τ/SR的16个表值在审计JSON | ESP BC30/60 τ=1.63/1.74，与原arXiv v2目标一致；未把SR当τ |
| Table1长度/硬件 | 同页表注 | 仍为256-token/H100；本轮未全文逐字对比版本，不能据目标相同宣称所有协议无变动 |
| Qwen3 BC60 mask | 第18页G.2 | 仍写Qwen3用单mask；不能拿一般双mask默认覆盖模型特定说明 |
| Figure8任务标签 | 第18页 | WRIT、ROLE、CODE、TRANS、SUMM、QA、RAG、M/R、STEM、HUM.，共10类 |
| 采样附表任务标签 | 第18页Table7、第19页Table8 | 共8类，少于图中10类；这是T1采样附加结果，不确认Table1的T0任务清单 |
| PDF中的URI注释 | 22页链接注释枚举 | 只有引用论文、数据说明和PLD基线等链接；未识别到ESP作者代码，注释检查不代表所有文本/附件全面审计 |

PMLR目标确认后，旧[CPU差距账本](esp-table1-gap-analysis-2026-10-16.json)仍适用：本仓8B BC30/1 pooled τ=1.563377504、BC60/1=1.647301264，差−0.066622496/−0.092698736。这里只复核来源与目标，不改旧账本SHA、Run、来源锁或冻结PLAN，也不新增模型执行。

## 三、对任务/权重缺口的收紧

本地原数据是固定480条、13个原category：五类各80条，MT-Bench八类各10条。当前不能由Figure8十类标签推断Table1恰用哪450条，也不能由采样表八类推断另一子集；更不能筛掉其余category后把较高τ当完整复现。图标签、样本纳入规则和聚合权重是三个不同合同项。

这次比仅写“任务权重不明”更具体：作者需要给出Table1使用的question_id/各类样本数、单轮/多轮、逐任务committed和forward分母，以及最终聚合代码。已有480输入与四种CPU聚合均保留不变。在获得这些材料前，不挑标签子集、不改prompt，不宣布任务重加权已经解释缺口。

## 四、下一步与GPU边界

1. 优先取得可核验的作者入口与Table1合同；若后续出现实际repo/附件，先核身份、许可、commit、原字节及原生入口能否表达共同协议，再谈GPU准入。当前没有可启动项。
2. 作者计数可访问后，按固定qid进行CPU差距对账；缺数据则保留null和访问限制，不用自实现补作者数据。
3. GPU空闲本身不构成重跑旧8B/4B矩阵的理由。本次按用户“无官方路径则CPU继续”的分支执行，量化可继续使用GPU；不新造ESP idea，不恢复bias/random/Kalman或算子链。

验证：逐请求实际状态/时间/字节/SHA已保存，表行解析断言16个数字且目标列为1.63/1.74；作者ESP条目链接已逐项提取，PDF页码/任务标签已核对。未声称全网检索完整、官方路径数学门通过或Table1数值复现。
