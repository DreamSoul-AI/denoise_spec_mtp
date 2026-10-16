# SD 阶段报告：8B ESP 复现与 4B BF16 方法比较

最新研究重点：[Table1差距分析](esp-table1-gap-analysis-2026-10-16.md)。仅CPU重算既有证据，BC30/60差距不能由prefill/尾部统计单独解释，聚合变化仅部分缩小缺口；作者合同与逐任务数据缺失仍限制归因。偏置/random/Kalman后置，GPU留给量化，不开新矩阵。

当前状态：五方法加AR及BC30全480方向六格均完成，数学门全过；新中英文计划已由PR23合dev。
最新结论：random0/1/2 τ=1.495188134/1.464349086/1.523884714，均高于zero1.422420206；content1.364829262低于zero，不支持收益只来自e2−e1。
出处：[六格最终报告](4b-full-direction-controls-2026-10-16.md)与[正式JSON](../../studies/qwen3_4b_bf16_directions/docs/direction_evidence_v1.json)，含全部配对、来源、归档失败与BC60不追加理由。
下一步：CPU回归、PR22合dev及删除对应远程分支；无新方法或GPU矩阵，无测速。
阻塞：无。8B自实现τ目标仍未复现；指定非官方HF原码预检失败，没有其有效τ。

<details>
<summary>历史阶段快照（保留出处；其中运行中表述不代表当前状态）</summary>

最新完整格：随机2 τ=1.523884714、80,583个提交token全argmax通过；相对固定e2−e1（τ=1.507777653）的逐promptτ为267胜/47平/166负，相对zero为401/17/62。出处：[五格有效快照](../../studies/qwen3_4b_bf16_directions/docs/direction_partial_v4.json)。三个预定随机种子均高于zero，随机2也高于template及原生input_first，不支持“收益只来自e2−e1”；随机0/1弱于template同样保留，不挑种子回写主方法。content尚未完整，不作全矩阵排名。量化v3第二窗口已单Run终态并释放GPU，原SD队列已接content，见[实际交接记录](../../studies/qwen3_4b_bf16_directions_recovery/docs/STUDY_REPORT.md)。数据和prompt不改。

全480方向对照新增完整格：同范数随机0 τ=1.495188134，81,425个提交token全argmax通过；相对zero的accepted胜/平/负为363/29/88、逐promptτ为360/27/93，template对应τ仍为1.507777653。来源：[三格有效结果快照](../../studies/qwen3_4b_bf16_directions/docs/direction_partial_v2.json)与[方向报告](../../studies/qwen3_4b_bf16_directions/docs/STUDY_REPORT.md)。本批收益并非仅e2−e1方向出现；其余随机种子与content仍待完整，不能推断任意方向有效或全矩阵排名。队列已自动进入随机1，不改数据/配置。

2026-10-16追加指示：四窗口不足以回答方向唯一性；现已冻结[BC30全480方向对照计划](<../研究计划 Denoising Speculative Decoding.md#legacy-studies-qwen3-4b-bf16-directions-docs-plan>)，新增严格固定e2−e1、三个同范数随机方向和内容初始化五格，零偏置复用旧输入零阶。执行与结果另见[新Study报告](../../studies/qwen3_4b_bf16_directions/docs/STUDY_REPORT.md)，未完成格子不填数字，BC60待本轮完成后再决定。目标模式继续active。

首格已完整验收：严格固定e2−e1全480的pooled τ=1.507777653（80,932个提交token自检全过），原生输入一阶含EMA更新的旧值为1.511957584，二者不能混称同一方法。出处：[完整首格/旧零阶证据快照](../../studies/qwen3_4b_bf16_directions/docs/direction_partial_v1.json)；随机三种子及内容初始化仍在单队列执行，整个方向Study未完成，暂不判唯一方向或全量排名。

资源事件追加：原队列已自然结束，三个随机格分别完成46/50/9条后遇真实GPU外部Python，content在加载前未获准入；105次完整prompt执行的20,977个提交token复核全过，仅记资源损耗，不拼接为全量。原Study保留failed终验。独立补齐Study仅重跑四个未完整因素，按prompt边界等待外部GPU释放，单队列继续；成功template及旧zero不重跑。出处：[四格资源记录](../../studies/qwen3_4b_bf16_directions/docs/resource_interruptions_v2.json)、[补齐协议](<../研究计划 Denoising Speculative Decoding.md#legacy-studies-qwen3-4b-bf16-directions-docs-recovery-plan>)及[补齐执行PLAN](<../研究计划 Denoising Speculative Decoding.md#legacy-studies-qwen3-4b-bf16-directions-recovery-docs-plan>)。未完成因素仍不计完整结果。

此前交付状态：固定数据五方法加AR完整11/11通过；指定四组方向的四窗口控制完成，未改prompt，全480扩展仍在执行。[非官方HF原码尝试](esp-third-party-reproduction-2026-10-15.md)已完成三预算8B BF16预检，BC10/30/60在固定q121首token的数学门均失败（同次验证logit差40.75/33.5/33.25），共6次forward，未跑该原码全480、没有有效τ。原码、冻结协议和[真实结果](esp-third-party-audit-2026-10-15.json)独立保留；不把它与下文自实现全480混为同一baseline。PR20已合dev并删除远程工作分支，本报告追加项继续按PR/dev流程交付。

最新 4B 追加阶段见[候选质量与固定窗口报告](4b-mask-window-2026-10-15.md)。同一输出零阶前缀下，输入一阶在4个窗口的首目标排名更好，其中q121接受0→1；输出四种局部改法均未增益。CPU还发现，保存的138个输入速度状态接近固定聊天模板首差分（最大相对误差0.095%），不能把当前优势直接解读成内容速度预测成功。追加2个条件窗口没有输出增益，输入局部排名反而更低。全部数字、树结构限制、条件样本局限在该报告逐项标出处；原全量τ和下文历史建议不回写成新矩阵结论。

后续同mean模板/零速度24格、100次forward全部完成数学自检：两种控制对原生输入速度的实际接受数均为无条件0胜4平、条件0胜2平，不能把q121局部增益单独归因于速度。CPU定位旧480条：459条首次同前缀接受差异位于root<8；早期块随后已按冻结窗口执行，结果见下段。第八节的原阶段结论保留，没有重跑全量τ。

最新早期/双向/指定方向控制已完成，见同报告第九至十二节：q121/q241换入输入一阶接受0→1、反向换回输出0/1阶为1→0；其他prompt保留反例。固定e2−e1对零偏置为3胜1负，随机0为1胜2平1负，随机1/2与内容初始化均0胜3平1负；q241随机0也有提升，否定本批“只有原方向有效”。这些仅为分析对照，原11/11主实验、数据及prompt不改，不是新增方法排名。当前GPU准入只看实际nvidia-smi进程和显存，不登记CPU脚本。已合远程分支[清理清单](remote-branch-cleanup-2026-10-15.md)另列；最新授权为本批PR合dev后删除相应远程工作分支。

口径更新：本报告的 8B 数字为此前按论文自实现的结果，不满足后续“必须运行原作者官方代码”的复现要求。原始数字与结论保留；来源核查见[官方代码复现报告](esp-official-code-reproduction-2026-10-15.md)。最新 4B 输出方法差距分析见[独立诊断](4b-mask-geometry-2026-10-15.md)，不替代作者代码复现。

截至 2026-10-15。**8B 的数学无损自检通过，但论文 Table 1 的 τ 数值未复现；4B 本批样本中输入一阶最好，输出速度项未显示稳定联合收益。** 两阶段已完成原生 Run/Study 验收，结果经 PR 合入 dev；本报告汇总已有结果，不新增模型运行或测速。历史 4B FP32 已独立标注归档，不混入以下 BF16 比较。


</details>

## 一、8B ESP Table 1 复现

### 设置与结果口径

Qwen/Qwen3-8B、BF16、T0；官方 SpecBench 全部 480 条、原顺序、首轮 non-thinking prompt；最大新输出 256，EOS 提前停止，seed 基数 123。ESP 按 Eq.5 用 λ=0.1 **updating mean**，动态树加剪枝，默认归约。BC10/1、30/1、60/1 为主配置；按论文 Appendix G.2，Qwen3 的 BC60 用单 mask、29 个 draft 节点；60/2（19 节点）只作预先固定的附加对照。8B 仅用于这项复现。

设置依据：[冻结协议](<../研究计划 Denoising Speculative Decoding.md#legacy-studies-esp-table1-bf16-full-argmax-docs-plan>)及[复现计划](<../研究计划 Denoising Speculative Decoding.md#legacy-docs-research-esp-table1-bf16-reproduction-plan>)；实际各格 `actual_spec`、`dtype`、`numeric_policy`、`runtime` 与全部数字见 [`studies/esp_table1_bf16_full_argmax/docs/protocol_evidence_v1.json`](../../studies/esp_table1_bf16_full_argmax/docs/protocol_evidence_v1.json)。模型内容哈希见[来源核验](../../studies/esp_table1_bf16_full_argmax/docs/modelscope-content-verification-v1.json)。

τ 主口径为 `Σcommitted / Σdecode_calls`；committed 包含 bonus、按 EOS/长度裁剪后计数，不含 prefill 首 token。另报告逐 prompt τ 等权均值，以及先逐原始 category 算 pooled τ、再对类别等权的均值。后者不冒称论文已确认的任务权重。以下保留六位小数，论文目标取结果文件的 `target`，差值为 pooled τ 减目标。

| BC/mask | pooled τ | 论文目标 | 差值 | prompt mean τ | category mean τ | 独立 AR 完全一致 | argmax 审计 token |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10/1 | 1.399047 | — | — | 1.431766 | 1.403034 | 188/480 | 79,757 / 全过 |
| 30/1 | 1.563378 | 1.63 | -0.066622 | 1.593232 | 1.563387 | 175/480 | 79,762 / 全过 |
| 60/1 | 1.647301 | 1.74 | -0.092699 | 1.669498 | 1.649693 | 185/480 | 79,618 / 全过 |
| 60/2（对照） | 1.603729 | 1.74 | -0.136271 | 1.664315 | 1.616079 | 187/480 | 79,693 / 全过 |

表来源：[`studies/esp_table1_bf16_full_argmax/docs/protocol_evidence_v1.json`](../../studies/esp_table1_bf16_full_argmax/docs/protocol_evidence_v1.json) 的 `cells[]`：`pooled_tau`、`target`、`pooled_tau_target_delta`、`prompt_mean_tau`、`category_mean_pooled_tau`、`exact_count`、`argmax_checked_tokens`；逐条计数及首分叉在 `rows`，Run ID 在同一 cell 的 `run_id`。三种聚合均低于对应论文目标，按两位小数也未复现；不事后挑聚合或 mask 数。

### 正确性与未复现原因的边界

正确性门是**每个提交 token 等于对应验证前向 logits 的 argmax**，含 prefill 首 token。四格全部通过，共 318,830 个 token；四个原生 Run 和 Study process 均通过。独立 AR 的全序列一致条数如表，只作诊断。旧门失败格保留原失败证据，仅重新 summarize/write 验收，未重跑 execute。来源：上述结果的 `argmax_all_passed`、`native_status`、`gate_revalidation` 与[原生终验证据](../../studies/esp_table1_bf16_full_argmax/docs/native-process-revalidation-v1.json)。

**已确认的协议差异及缺口，不是已证明的原因**：论文 Table 1 表注与正文对长度上限、硬件的描述不一致；本次遵循表注的输出上限。论文未完整固定精度、模型 immutable revision、thinking/template、截断和跨任务聚合权重；本次采用的 BF16、首轮 non-thinking、不截断等选择已披露。实测硬件与软件环境也不同，见结果 `runtime`。模型文件已与魔搭内容哈希核验，但不能据此认定与论文的历史 checkpoint 完全相同。这些是后续协议对齐候选，当前没有因果证据解释 τ 缺口；不进入 BF16 算子机理排查。依据：[复现计划“论文目标与未决口径”](<../研究计划 Denoising Speculative Decoding.md#legacy-docs-research-esp-table1-bf16-reproduction-plan>)。

## 二、4B BF16 五方法加 AR

### 方法与共同设置

同一批 SpecBench 全 480 条、T0、最大新输出 256/EOS、seed 基数 123；模型和 forward 为 Qwen3-4B BF16。BC30、BC60 各比较五方法，均为**双 mask 动态剪枝树**，draft 节点预算分别为 9、19；保留第二 mask 的速度外推。这与前述 8B 的单 mask 主配置不同，不可直接跨模型比较排名。独立 AR 只运行一次，供所有方法共用。

| 方法 | 本次实际定义 |
| --- | --- |
| ESP frozen mean | prompt 输入 embedding 均值固定不更新，λ=0、update=false；用户指定基线，与论文 updating mean 不同。 |
| 输入零阶 | prompt embedding 均值初始化，以已验证 token 的输入 embedding 更新 mean/EMA，λ=0.1。 |
| 输入一阶（mean+γ） | updating mean 作原点，加输入 embedding 差分的 EMA 速度外推；β=0.9999、λ=0.1、γ=1，level=order0，normalize=false、extrapolate_ema=false。 |
| 输出零阶 | 末层 final-normalized hidden 经范数缩放后填入 mask，目标范数 r=mean_v‖W_v‖；order=0，沿用已验证/代理历史状态，β=0.9、β′=0.99。 |
| 输出一阶 | 与输出零阶相同 hidden 映射和范数缩放，order=1 加 EMA 速度；β=0.9、β′=0.99。 |
| 独立 AR | 同模型、输入、seed 和停止规则的逐 token greedy 参考，无 draft 接受数或 speculative τ。 |

定义和实际参数来源：[`studies/qwen3_4b_bf16_five_methods/docs/paired_evidence_v1.json`](../../studies/qwen3_4b_bf16_five_methods/docs/paired_evidence_v1.json) 的 `cells[*].actual_settings`，配合[冻结 PLAN](<../研究计划 Denoising Speculative Decoding.md#legacy-studies-qwen3-4b-bf16-five-methods-docs-plan>)；实现为 [mask_providers.py](../../src/spec_mtp/structure/algorithm/mask_providers.py) 及[输出 provider](../../src/spec_mtp/structure/algorithm/output_masks.py)。实际 tied-storage 核对通过，无逆映射。最终 mask 为 BF16，输出 EMA/范数保留原生 FP32 内部状态，不能称所有内部计算均为 BF16；没有新增 FP32 模型实验。

### 各格 τ、计数与正确性门

accepted 为 EOS/预算裁剪前接受的候选数，不能替代 τ 分子；主 calls 为 prefill+decode。独立 AR 新输出和主 calls 均为 81,880，accepted/τ 不适用。

| BC | 方法 | pooled τ | prompt mean τ | accepted | 主 calls | 新输出 token | 独立 AR 完全一致 | argmax 审计 token |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 30 | ESP frozen mean | 1.402895 | 1.475938 | 23,188 | 57,825 | 80,929 | 184/480 | 80,929 / 全过 |
| 30 | 输入零阶 | 1.422420 | 1.479837 | 23,926 | 56,938 | 80,787 | 168/480 | 80,787 / 全过 |
| 30 | 输入一阶 | 1.511958 | 1.543007 | 27,371 | 53,668 | 80,898 | 175/480 | 80,898 / 全过 |
| 30 | 输出零阶 | 1.433178 | 1.483601 | 24,382 | 56,577 | 80,877 | 177/480 | 80,877 / 全过 |
| 30 | 输出一阶 | 1.435540 | 1.482532 | 24,573 | 56,716 | 81,209 | 184/480 | 81,209 / 全过 |
| 60 | ESP frozen mean | 1.499079 | 1.571032 | 26,913 | 54,197 | 81,006 | 165/480 | 81,006 / 全过 |
| 60 | 输入零阶 | 1.519109 | 1.578924 | 27,523 | 53,309 | 80,733 | 167/480 | 80,733 / 全过 |
| 60 | 输入一阶 | 1.636340 | 1.665860 | 31,611 | 49,875 | 81,307 | 162/480 | 81,307 / 全过 |
| 60 | 输出零阶 | 1.528922 | 1.579126 | 27,828 | 52,896 | 80,620 | 172/480 | 80,620 / 全过 |
| 60 | 输出一阶 | 1.529836 | 1.576289 | 27,903 | 52,951 | 80,752 | 161/480 | 80,752 / 全过 |

表来源：[`studies/qwen3_4b_bf16_five_methods/docs/paired_evidence_v1.json`](../../studies/qwen3_4b_bf16_five_methods/docs/paired_evidence_v1.json) 的 `cells[*].totals`；每格完整 480 条计数、输出长度、输出 SHA、AR 首分叉在 `rows`，实际 Run ID 在 `run_id`。全部 4,800 条 Spec prompt、809,118 个提交 token 的 argmax 自检通过；含共享 AR 的全部原生 Run 及 Study process 通过。来源：[`studies/qwen3_4b_bf16_five_methods/docs/native-process-evidence-v1.json`](../../studies/qwen3_4b_bf16_five_methods/docs/native-process-evidence-v1.json) 的 `runs`、`speculative_prompt_rows`、`argmax_checked_speculative_tokens`。AR 参考不冒充 Spec 自检。

### 逐 prompt 胜平负

每组按同一 question_id 配对，**箭头右侧方法相对左侧方法**，W/T/L=胜/平/负；accepted 越多越好，calls 越少越好，分别判定。各组均为全部 480 条，以下覆盖五方法所有两两对照，保留反例。

| 左 → 右（右侧判胜） | BC30 accepted W/T/L | BC30 calls W/T/L | BC60 accepted W/T/L | BC60 calls W/T/L |
| --- | --- | --- | --- | --- |
| ESP frozen mean → 输入零阶 | 229/24/227 | 235/21/224 | 225/29/226 | 232/35/213 |
| ESP frozen mean → 输入一阶 | 301/34/145 | 294/31/155 | 317/41/122 | 300/33/147 |
| ESP frozen mean → 输出零阶 | 245/28/207 | 239/30/211 | 246/23/211 | 245/27/208 |
| ESP frozen mean → 输出一阶 | 248/30/202 | 235/29/216 | 238/32/210 | 235/29/216 |
| 输入零阶 → 输入一阶 | 364/35/81 | 352/24/104 | 374/36/70 | 354/28/98 |
| 输入零阶 → 输出零阶 | 231/38/211 | 236/34/210 | 216/48/216 | 229/39/212 |
| 输入零阶 → 输出一阶 | 231/42/207 | 232/36/212 | 241/41/198 | 227/44/209 |
| 输入一阶 → 输出零阶 | 106/40/334 | 116/42/322 | 90/28/362 | 114/40/326 |
| 输入一阶 → 输出一阶 | 118/31/331 | 121/33/326 | 84/43/353 | 105/51/324 |
| 输出零阶 → 输出一阶 | 209/72/199 | 201/64/215 | 206/69/205 | 202/61/217 |

来源：[`studies/qwen3_4b_bf16_five_methods/docs/paired_evidence_v1.json`](../../studies/qwen3_4b_bf16_five_methods/docs/paired_evidence_v1.json) 的 `pairs[]`：`first`、`second`、`accepted`、`calls`；每条 prompt 的判定和差值保留在 `pairs[].rows`。

相对独立 AR 的**调用数**胜平负如下；AR 没有 accepted 对照项。

| 方法（相对 AR） | BC30 calls W/T/L | BC60 calls W/T/L |
| --- | --- | --- |
| ESP frozen mean | 469/1/10 | 475/1/4 |
| 输入零阶 | 476/0/4 | 478/0/2 |
| 输入一阶 | 477/0/3 | 478/0/2 |
| 输出零阶 | 472/1/7 | 476/0/4 |
| 输出一阶 | 475/0/5 | 477/0/3 |

来源：同一结果的 `cells[*].totals.calls_vs_AR`。这些计数不表示同输出长度下的加速比。

## 三、结论、排名与局限

在本批固定样本与固定配方下，两个 BC 的排序一致：

- 总 accepted / pooled τ 从高到低：**输入一阶 > 输出一阶 > 输出零阶 > 输入零阶 > frozen mean**。
- 总主 calls 从少到多：**输入一阶 < 输出零阶 < 输出一阶 < 输入零阶 < frozen mean**。

依据为上表和 `cells[*].totals`。两输出方法相对 frozen mean、输入零阶有小幅总量改善，但均落后输入一阶；不能写成输出空间普遍优于输入空间。

输出一阶相对输出零阶的关键变化（右减左）：

| BC | Δaccepted | Δ主 calls | Δ新输出 token |
| --- | --- | --- | --- |
| 30 | +191 | +139 | +332 |
| 60 | +75 | +55 | +132 |

来源：`pairs[]` 中 output_zero → output_first 的 `total_delta_second_minus_first`。两个预算 pooled τ 略升，但 prompt mean τ 均下降，总 calls 也增加；结合上面的逐 prompt 胜平负，**速度项未显示稳定联合收益**。

主要局限：

- 各方法实际输出长度和 token 路径不同；表中已列新输出数，结果文件保留 AR 首分叉。calls 或 accepted 总量的差不等于同输出加速，更不等于质量改善。未测速。
- 独立 AR 一致率只作诊断；argmax 门通过只证明本次提交选择与对应验证前向一致，不证明与独立 AR 逐 token 一致。
- 当前为固定样本、单 seed 设置；各方法 β 等沿用预先冻结配方，未做等参数控制，不能将差异全部归因于输入/输出空间或阶数，亦未建立总体显著性。
- 两阶段树的 mask 数不同；4B frozen mean 也不同于 8B 论文 updating mean。历史 FP32 结果独立归档，不可与本轮拼接成 BF16 结论。

## 四、当前交付边界与建议

1. 现有五方法加AR完整测试和逐prompt读出已完成，不重跑已有格子；输入一阶在当前固定配方最好，输出一阶无稳定联合收益。后续指定模板方向控制和双向互换已完成，局部样本边界见独立报告，不能升级为全480新排名。
2. 作者代码来源仍有缺口；获准HF第三方原码已实际试验但数学门失败，未取得有效τ。保留“8B论文数值未复现”的结论，不能以其外部高τ替换本机结果。若Enmao提供可靠既定baseline来源，再按新指示处理。
3. 保留argmax硬门、AR诊断分列、固定数据和全部失败证据；本目标收尾为报告、PR合dev及远程工作分支清理，不自行新增方法、改prompt调结果或恢复算子链。

## 结果文件索引

所有表格均从以下已验收结果文件读取；显示值为舍入值，完整精度与逐条记录以 JSON 为准。链接相对本报告，路径相对仓库根目录。

- 8B 数字、四格参数、论文目标、逐 prompt 计数及首分叉：[`studies/esp_table1_bf16_full_argmax/docs/protocol_evidence_v1.json`](../../studies/esp_table1_bf16_full_argmax/docs/protocol_evidence_v1.json)。
- 8B 原生验收与保留旧失败证据：[`studies/esp_table1_bf16_full_argmax/docs/native-process-revalidation-v1.json`](../../studies/esp_table1_bf16_full_argmax/docs/native-process-revalidation-v1.json)。
- 4B 全部格子、两两逐 prompt 对照及 AR 诊断：[`studies/qwen3_4b_bf16_five_methods/docs/paired_evidence_v1.json`](../../studies/qwen3_4b_bf16_five_methods/docs/paired_evidence_v1.json)。
- 4B 正确性门、实际来源与原生产物哈希：[`studies/qwen3_4b_bf16_five_methods/docs/native-process-evidence-v1.json`](../../studies/qwen3_4b_bf16_five_methods/docs/native-process-evidence-v1.json)。
- 原生 Experiment/Run 数字表：[8B NUMBERS](../../studies/esp_table1_bf16_full_argmax/docs/NUMBERS.md)、[4B NUMBERS](../../studies/qwen3_4b_bf16_five_methods/docs/NUMBERS.md)。完整 Run、原始 token、权重与缓存留在本机，不随报告提交。

## 五、已合并远程分支清理记录

执行时间：2026-10-15 12:05:33 UTC（北京时间 20:05:33）。依据 Enmao 本次明确授权，删除已合入 dev 的远程工作分支；当前工作分支及明确指定保留的分支不删。本次授权仅用于以下远程分支清理，不扩展为删除本地分支、worktree、Run 或数据的授权。

删除前已 fetch 并核对 GitHub 实际分支列表、打开的 PR 和提交祖先关系。核验基准为 `dev@b22e513319803c449060a9771d20ea8ff3f24ebc`；以下三个分支头均通过 `git merge-base --is-ancestor <head> origin/dev`，没有打开的 PR。

| 已删除远程分支 | 删除前 head SHA | 对应已合入 dev 的 PR | 执行结果 |
| --- | --- | --- | --- |
| `feature/4b-bf16-five-methods` | `5840ea2d0c877f2571ac57a4e9dc80c02562551e` | [#12](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/12) | 已删除，远端复查不存在 |
| `fix/verifier-argmax-gate` | `c9367661c5c5c84eae797e0040784fcf60768ee1` | [#10](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/10) | 已删除，远端复查不存在 |
| `refactor/spec-rpipe` | `1219a1d88f10c2faee345b8d9bf6a42fd1e0110e` | [#6](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/6) | 已删除，远端复查不存在 |

实际执行命令（正常远程删除，无强推）：

```text
git push --atomic origin --delete feature/4b-bf16-five-methods fix/verifier-argmax-gate refactor/spec-rpipe
```

命令成功后用 `git ls-remote --heads origin` 复查：远程仅剩 `main`、`dev`、`feature/sd-stage-report`、`feature/output-space-prerequisite`。`main`/`dev` 为长期主线；后两个分支按用户明确要求保留，其中 `feature/sd-stage-report` 也是当前报告工作分支。删除未改变 dev 已合并内容，本地分支、worktree、权重、缓存及实验数据均保留。此清单记录清理完成时的远程状态，后续报告提交会正常推进保留的工作分支。
