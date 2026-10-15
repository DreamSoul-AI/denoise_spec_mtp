# SD 阶段报告：8B ESP 复现与 4B BF16 方法比较

截至 2026-10-15。**8B 的数学无损自检通过，但论文 Table 1 的 τ 数值未复现；4B 本批样本中输入一阶最好，输出速度项未显示稳定联合收益。** 两阶段已完成原生 Run/Study 验收，结果经 PR 合入 dev；本报告汇总已有结果，不新增模型运行或测速。历史 4B FP32 已独立标注归档，不混入以下 BF16 比较。

## 一、8B ESP Table 1 复现

### 设置与结果口径

Qwen/Qwen3-8B、BF16、T0；官方 SpecBench 全部 480 条、原顺序、首轮 non-thinking prompt；最大新输出 256，EOS 提前停止，seed 基数 123。ESP 按 Eq.5 用 λ=0.1 **updating mean**，动态树加剪枝，默认归约。BC10/1、30/1、60/1 为主配置；按论文 Appendix G.2，Qwen3 的 BC60 用单 mask、29 个 draft 节点；60/2（19 节点）只作预先固定的附加对照。8B 仅用于这项复现。

设置依据：[冻结协议](../../studies/esp_table1_bf16_full_argmax/docs/PLAN.md)及[复现计划](esp-table1-bf16-reproduction-plan.md)；实际各格 `actual_spec`、`dtype`、`numeric_policy`、`runtime` 与全部数字见 [`studies/esp_table1_bf16_full_argmax/docs/protocol_evidence_v1.json`](../../studies/esp_table1_bf16_full_argmax/docs/protocol_evidence_v1.json)。模型内容哈希见[来源核验](../../studies/esp_table1_bf16_full_argmax/docs/modelscope-content-verification-v1.json)。

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

**已确认的协议差异及缺口，不是已证明的原因**：论文 Table 1 表注与正文对长度上限、硬件的描述不一致；本次遵循表注的输出上限。论文未完整固定精度、模型 immutable revision、thinking/template、截断和跨任务聚合权重；本次采用的 BF16、首轮 non-thinking、不截断等选择已披露。实测硬件与软件环境也不同，见结果 `runtime`。模型文件已与魔搭内容哈希核验，但不能据此认定与论文的历史 checkpoint 完全相同。这些是后续协议对齐候选，当前没有因果证据解释 τ 缺口；不进入 BF16 算子机理排查。依据：[复现计划“论文目标与未决口径”](esp-table1-bf16-reproduction-plan.md)。

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

定义和实际参数来源：[`studies/qwen3_4b_bf16_five_methods/docs/paired_evidence_v1.json`](../../studies/qwen3_4b_bf16_five_methods/docs/paired_evidence_v1.json) 的 `cells[*].actual_settings`，配合[冻结 PLAN](../../studies/qwen3_4b_bf16_five_methods/docs/PLAN.md)；实现为 [mask_providers.py](../../src/spec_mtp/structure/algorithm/mask_providers.py) 及[输出 provider](../../src/spec_mtp/structure/algorithm/output_masks.py)。实际 tied-storage 核对通过，无逆映射。最终 mask 为 BF16，输出 EMA/范数保留原生 FP32 内部状态，不能称所有内部计算均为 BF16；没有新增 FP32 模型实验。

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

## 四、建议下一步（尚未执行）

1. **先对齐论文协议缺口**：核对作者实际 checkpoint、template、输出上限和任务聚合方式，用已有逐 prompt 文件重算可确定的口径；不按结果挑选设置，不恢复算子机理。协议未闭合前，保留“8B 数值未复现”的结论。
2. **后续 4B 比较保留输入一阶为强基线、输出零阶为输出基线**，输出一阶继续作为待证伪对照。若另立实验，先冻结独立 prompt 集及匹配参数，分别看 accepted、calls、长度与逐 prompt 反例；不因微小 pooled τ 变化直接升级更复杂方法。
3. **继续保留 argmax 硬门和 AR 诊断分列**，复用当前结果与回归证据。本次仅交付报告和 PR/dev 集成；不启动新模型批次、测速或其他研究。

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
