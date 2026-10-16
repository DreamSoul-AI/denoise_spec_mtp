# Study Report: output_space_followup

2026-10-14：q179–q182四个新原生Run、16prompt outputs和20次固定窗口诊断通过完整独立AR/来源/范围门。q179原零/一accepted8/9，双向均10；q182原4/3，双向均4；q180/181保留null。原配方与科学source670c744e0535dcad不改，未推送、合并或删数据。它扩大了局部接受变化的观察，不建立普遍一阶优势。

## 固定协议与证据

[PLAN](<../../../docs/研究计划 Denoising Speculative Decoding.md#legacy-studies-output-space-followup-docs-plan>)冻结下一连续translation skip18/take4、q179/180/181/182和两槽/窗口/停止规则；[prompt清单](prompts_manifest.json)先冻结文本/hash与独立渲染IDs，input长度99/35/37/38。ModelScope同一11文件快照/tied Qwen3-0.6B、FP32/eager/CUDA、非thinking、T0/EOS/预算100、static unpruned[1,1]/k2/BC9、beta.9/beta_prime.99、seed123+i。Native runtime仍deterministic=false/原TF32配置；q178严格精度覆盖只在独立子进程，没有传递到新Run。

[原生执行](execution_v1.json)、[NUMBERS](NUMBERS.md)、[逐prefix轨迹](trajectory_diagnosis.json)、[冻结窗口](window_selection_v1.json)、[双向执行](transfer_diagnosis_v1.json)、[离线范围/state汇总](analysis_v1.json)保留所有正负点。PLAN未修改，结果和后续假设在[PLAN_REVIEW](<../../../docs/研究计划 Denoising Speculative Decoding.md#legacy-studies-output-space-followup-docs-plan-review>)，避免重签已成功Run。

## 小矩阵

| qid/seed | new tokens | 输入 | 原零阶 | 原一阶 | 固定根 | 一阶←零阶 | 零阶←一阶 | 一阶原值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 179/123 | 55 | 8 | 8 | 9 | 103 | 10 | 10 | 9 |
| 180/124 | 16 | 2 | 3 | 3 | 35 | 3 | 3 | 3 |
| 181/125 | 18 | 4 | 2 | 2 | 43 | 2 | 2 | 2 |
| 182/126 | 18 | 4 | 4 | 3 | 44 | 4 | 4 | 3 |

数字是all-depth accepted，不是译文质量/速度。原生new107/committed103，输入/零/一合计accepted18/17/17、calls85/87/87。Q179一阶自然胜1，q182自然负1，pooled恰同17；所有四条保留，std0只来自单Run，不当四seed重复或总体方差。

窗口规则复用前批choose_window：先首个共同命中的共同拒绝前根，预声明fallback不按margin择优。本批四条都用首规则，观察target union根数44/13/9/8。baseline只观测实际访问子集，transfer按实际seed owner行进；未匹配根/未捕获hidden/new roots全列出。所有原值回填复现原一阶完整语义路径。

## 收益与损失的具体位置

Q179一阶←零阶：原accepted9→10/calls45→44，root112/119/141各失去1个depth1，root115/123/125/128/134各新增1。原值回填9/45。反向零阶←一阶：原8→10/calls46→44，root125新增1，root128 0→2，root147新增1，但root135失去1。实际新增/跳过根保存，不把同step当同prefix。自然两方法first-slot margin在root112/119/123/135/147异号，方向混合，不是全段一阶better。

Q182一阶←零阶：root47接受[1]→[1,2]，净3→4/calls14→13，跳过root49；反向总4/calls13、接受语义路径不变但seed方向变化。root47第一draft正确，两槽路径合法；其第二槽原零/一margin+.481377/-.039644，一阶←零阶变+.334106，零阶←一阶+.309990。该root以及source root45的committed anchor/v与recipient原值逐元素相同，较后根才因不同路径出现微差。它提供root44→45(owner0)→47(owner1)历史后续第二层命中例子，与q178root85直接影响下一root86第二层的时序不同；仍未独立介入全部中介。

Q180/181双向分别11/7个first seed发生逐元素变化，接受/提交/KV完全不变，同位anchor/v全部相同。这再次否定扰动或seed变化存在就必有接受收益；原值回填seed未变。

## 数值与因果边界

本批没有运行q178那套canonical state同步，不将它的结论直接推广。Q179一阶←零阶36个匹配窗口只有9个anchor/v同时逐元素相同，max_abs anchor3.05176e-5/v2.98023e-6；反向38个只有25个anchor相同，anchor最大5.34058e-5且v始终0。Q182一阶←零阶7个匹配根前三个44/45/47相同，后期anchor最大2.67029e-5/v2.62260e-6；反向7个全相同且v0。小差异保留，未声称后期pureproxy归因。

q178独立对照结果见[数值报告](../../output_space_extension/docs/STUDY_REPORT.md)及[规范评审](<../../../docs/研究计划 Denoising Speculative Decoding.md#legacy-studies-output-space-extension-docs-numerical-plan-review>)：严格FP32重复全部已捕获张量相同，规范anchor/v同步后两个self控制8、双移植9且全语义路径仍同。这说明q178本固定committed-state微差并非必要，同时代理内数值与具体CUDA kernel仍未隔离。

排序边界是即时T0判定，owner历史会改变之后的seed和排序，不能作为二选一机制。累计12个同模型/任务开发prompt只有q173/178/179/182在固定移植后出现接受数变化，其余8个null（包括未利用owner/终止控制），不是发生概率估计。原一阶总数自然胜零阶的只有q173/q179，q182负1；总体accepted输入60/零45/一47为描述，不能推稳定方法优势、显著性或跨任务普遍性。第二层只有合法first prefix下才解释，不记碰巧匹配为depth2收益。

## 实际资源与验收

| case | Run ID | make est秒 | 实际Flow秒 |
| --- | --- | ---: | ---: |
| frozen_mean_chain | a6b19d2bd87b599e | 3 | 22.280 |
| output_order0 | 8fd106b0824511ba | 3 | 22.107 |
| output_order1 | 24d9d0f6056827ff | 3 | 21.702 |
| AR | 7635a9a39af40273 | 3 | 19.779 |

原生launch wall107.424秒，.5秒采样进程树RSS6724042752 bytes、线程57、GPU全局6191MiB、可用主存最低11497598976 bytes。诊断wall34.334秒，RSS4904353792 bytes、线程13、GPU全局6190MiB、最低主存12067713024 bytes；均含背景/漏短峰，不作allocator或方法速度排名。诊断20次生成535newtokens/451model forwards（各1+实际calls），辅助forward0，低于固定预算；16原生prompt outputs全部独立AR相同、无context缩短。

源码/model/runtime/11文件snapshot/native raw/PLAN/selection/tool/helpers前后绑定一致。ModelScope缓存junction复用不重下，默认master来源不冒称remoteimmutable revision。17项本轮针对性/新Study展开/docs、Ruff、mypy56通过，旧全量科学测试对应同一src但不改写为本轮新全量数。

[diagnose_study_windows.py](../../../tools/diagnose_study_windows.py)为manifest绑定四prompt协调器，复用旧choose/observe/transfer/compare/slots，不改它们；[analyze_results.py](../analyze_results.py)离线检查scope和state并拒绝覆盖不同旧JSON。selected452824221 bytes，仅本机.tmp/followup-transfer-20261014-v1，SHA9907581d885d9481ecb1977fee44b39bc6168ab266b2272f1bf66f07e62e46b6。完整权重/cache/Run/raw tensors不进Git，旧失败和workspace文件保持，未推送、合并、删除。
