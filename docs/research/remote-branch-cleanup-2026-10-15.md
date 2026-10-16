# 已合dev远程分支清理

执行状态：2026-10-15已完成。按Enmao最新明确授权，删除已合dev的远程工作分支，保留当前工作分支；该指令覆盖此前对输出前置远程分支“先保留”的临时安排。长期主线main/dev不属于此次临时工作分支清理范围。

| 远程分支 | 删除前tip | 核验与结果 |
| --- | --- | --- |
| feature/output-space-prerequisite | bb4b526a3b85ac569bc67d13d8326e7c30494271 | `git merge-base --is-ancestor`确认包含于dev；重新读取远程tip未变后，`git push origin --delete feature/output-space-prerequisite`成功 |

核验基准dev：`f1a67894ddb0756e0cb1ce5a12d573d1e8de8b38`。删除后再次`git ls-remote --heads origin`，只剩：

| 保留远程分支 | tip | 原因 |
| --- | --- | --- |
| main | b636f90e54c7641be6914fbccec13f64bd9cc04c | 长期主线 |
| dev | f1a67894ddb0756e0cb1ce5a12d573d1e8de8b38 | 集成主线 |
| feature/sd-stage-report | f363ddad56adeac1080c51a15edcb11c8e3d6e89 | 当前正在使用的工作分支 |

本地主仓checkout删除前为干净状态；未删除本地分支、worktree、commit或实验数据，未强推或合main。后续提交会继续推进当前工作分支，此表tip为清理核验时快照。

## PR20合并后的追加清理

PR [#20](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/20) 的两项CPU检查及Branch flow通过，已合dev，merge commit为`7f91bbb7e84e2b9e6a91ead3f7d1e92e2c6d2ac9`。切换到`feature/esp-third-party-reproduction`后，确认`759b119caae0da73275300807c85f926de155b2d`包含于dev且远程tip未变，执行`git push origin --delete feature/sd-stage-report`成功。该删除不影响本地分支和数据。后续第三方验收PR合并后的最终分支清单记录在该PR说明及本地验收证据中，避免为记录自身删除反复新开PR。

## PR23研究计划合并后的清理（2026-10-16）

新模板中英文计划及文献证据经[PR23](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/23)两项CPU CI与Branch flow通过后，普通merge进入dev：`b00ecc0a188bb1a2845f061e958fdac37da7bcce`。GitHub未启用AutoMerge，本轮没有修改仓库设置或跳过保护，实际在检查通过后普通合并。

| 远程分支 | 删除前tip | 实际结果 |
| --- | --- | --- |
| feature/sd-research-plan-template | cd0a2fae3569bc15eb57c2abb79e276942538963 | 核dev包含head、远程tip未变，主仓切回dev并fast-forward后，`git push origin --delete feature/sd-research-plan-template`成功；ls-remote确认不存在 |

删除后远程仅剩dev（上述merge）、main（`b636f90e54c7641be6914fbccec13f64bd9cc04c`，未变）及仍在运行的`feature/4b-full-direction-controls`（本次核验tip `b9e45d6352a37e11860b81634a6da19cddc9bc7f`）。本地计划分支、Run、worktree和数据保留；content全480原进程继续，不把计划PR完成记作整个方向目标完成。合并及删除的闭环同时记录在PR23说明和主仓本机`.tmp/research-plan-template-20261016/closure.json`。

## PR22全量方向结果合并后的清理（2026-10-16）

[PR22](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/22)两项CPU CI及Branch flow全部通过，普通merge进入dev：`d792ca57872b1138e09302ec51bebcdf8e61da2e`。

| 远程分支 | 删除前tip | 实际结果 |
| --- | --- | --- |
| feature/4b-full-direction-controls | 0aad4d16b6016f002681e411616bedcc06906204 | 确认dev包含head且远程tip未变后删除；ls-remote确认不存在 |

删除后仅余dev（上述merge）与main（`b636f90e54c7641be6914fbccec13f64bd9cc04c`，未变）。本地主仓dev已同步且干净；本地分支、worktree、Run及数据保留。此为该次清理快照，后续文档分支按相同PR流程维护，其自身删除闭环记录在对应PR说明，避免为记载自身删除重复开PR。

## 2026-10-16 周期性本地、远端与worktree清理

授权依据：Enmao本轮更正“此前不删分支作废”，已合入dev的本地/远端/废弃worktree清理，正在跑GPU者保留，未合过时项先列清单；以后约每合5个PR执行一次。已合判定为逐分支tip是origin/dev的祖先，并在删除前复核tip未变；仅git branch -d和普通远程delete，无强删/force。

PR #41已于2026-10-16T05:47:26Z合dev，merge5ef98ba0c2dcd8187b557cd46652d1dcd74c49fa；Branch flow3s、cpu-checks4m12s通过。本地完整CPU511项通过，另10项迁移/原字节专项通过，ruff/mypy通过；原始本机检查日志保留.tmp/plan-consolidation-20261016。唯一中英文项目计划及60子计划归并已完成。

### 实际删除分支

| 范围 | 分支 | 删除前tip |
| --- | --- | --- |
| 本地 | `analysis/esp-cpu-contract-reconciliation` | `34b25d8d1ff0f23d8f9df1a545e49bc84548d1b7` |
| 本地 | `analysis/esp-tau-attribution-hypotheses` | `0899fdb80c2f79389d2aef6c03b84cec1b33ae08` |
| 本地 | `docs/esp-author-hf-channel` | `2967400739a1146b926ea46fe838e5dae2039219` |
| 本地 | `docs/esp-author-public-channels` | `aeae7fbef2a141d7d46e4ec5c38b4fca4f69898a` |
| 本地 | `docs/esp-author-release-leads` | `82857a620107dab324b154b77b746e180c8bacc9` |
| 本地 | `docs/esp-author-repository-assets` | `8d2a10fc80e83129d91ab3df5961509425c1dcb3` |
| 本地 | `docs/esp-author-version-assets` | `2a350036a00eab1218b4a7de2c1853e8cd96e8f6` |
| 本地 | `docs/esp-nonofficial-full480-recheck` | `df9a28cbd6c8c00ac5fe71d5ab44ffb37a51c366` |
| 本地 | `docs/esp-official-org-code-search` | `0696bfc489ceebd53244c3dfe39406ace1dbe270` |
| 本地 | `docs/esp-protocol-gap-register` | `11ad94317092dd26ac3f8af2d1f39d231d92fce0` |
| 本地 | `docs/unified-project-research-plan` | `10b1cf89606cd537a4aa894b003196252931a3e9` |
| 本地 | `feature/4b-bf16-five-methods` | `5840ea2d0c877f2571ac57a4e9dc80c02562551e` |
| 本地 | `feature/4b-full-direction-controls` | `0aad4d16b6016f002681e411616bedcc06906204` |
| 本地 | `feature/esp-author-attachment-followup` | `1eb4aed24719c9fe41d33f7fef2e10978cb13949` |
| 本地 | `feature/esp-coauthor-history-followup` | `3b6cb9ed00a2e0166e9b0e8792bfa2f5775e2f88` |
| 本地 | `feature/esp-official-launch-readiness` | `1a31be7c9f2a06694d4055937f9617b0e9b82497` |
| 本地 | `feature/esp-official-source-recheck` | `08fef38fc4398bf9ce6922f0b65af620b2ba2aea` |
| 本地 | `feature/esp-organization-readme-followup` | `6a6b00651b27c27f4416965c9c398ba8a01ae422` |
| 本地 | `feature/esp-table1-gap-analysis` | `9c8768fd108f11309a2b5fc35442e6a4b6d37c73` |
| 本地 | `feature/esp-third-party-reproduction` | `44d90562c460c43018064938b01738d392e0d1f6` |
| 本地 | `feature/output-space-prerequisite` | `bb4b526a3b85ac569bc67d13d8326e7c30494271` |
| 本地 | `feature/research-ema-history-audit` | `9329cc347e3bd56ebc8bc6d1522d02f3c354e0a0` |
| 本地 | `feature/sd-postmatrix-handoff` | `69af089f33f49e6343f2455f66fff6fd1235869e` |
| 本地 | `feature/sd-research-plan-template` | `cd0a2fae3569bc15eb57c2abb79e276942538963` |
| 本地 | `feature/sd-stage-report` | `759b119caae0da73275300807c85f926de155b2d` |
| 本地 | `fix/verifier-argmax-gate` | `c9367661c5c5c84eae797e0040784fcf60768ee1` |
| 本地 | `refactor/spec-rpipe` | `1219a1d88f10c2faee345b8d9bf6a42fd1e0110e` |
| 远端origin | `docs/unified-project-research-plan` | `10b1cf89606cd537a4aa894b003196252931a3e9` |

合计：本地27条，远端1条（其余旧远端在先前PR已清理）；均已包含于dev。删除后本地只剩main/dev、本轮清理工作分支与正在GPU执行的experiment/sd-nonofficial-repeat-norm。main仍为b636f90e54c7641be6914fbccec13f64bd9cc04c，未操作。

### worktree、数据与未合清单

- 废弃esp-native-gate-20261015：原tip c9367661c5c5c84eae797e0040784fcf60768ee1，tracked干净、未发现引用该目录的运行进程。该目录含历史实验数据，因此只把单文件.git指针原地改名为.git.worktree-archived-20261016，并在确认prune dry-run仅列此登记后移除Git worktree登记；没有删除目录、实验数据、缓存或结果。859份decode输入/观测、result/process/index及tensor/权重类证据逐文件尺寸/SHA核验前后不变。完整清单保留本机.tmp/branch-cleanup-20261016，原Git指针内容也可恢复。该目录是静态历史快照，不能再当活动checkout。
- 正在跑GPU的experiment/sd-nonofficial-repeat-norm及4b-bf16-five-methods-20261015工作树完整保留；新范数扫描准备也在该执行树，未启动重叠GPU链。此分支未合且有效，不列为过时。
- 当前chore/merged-branch-cleanup-20261016是本报告的活动分支，PR通过合dev后清理自身本地/远端；此刻不提前删除。没有其他未合、已过时候选需要裁定。
- 查询时open PR=0、open issue=0，无可关闭的已处理开放项；PR #41已合。没有批量关闭未完成事项。

### 后续规则

本轮计数基线为合入PR #41之后的清理，随后每约5个合dev的PR复查一次；每次先核tip祖先关系、工作树/进程及数据，未合过时项先列清单。已合普通topic立即清远程，本地在退出该分支后删除；GPU活动分支/worktree、main/dev不动。数据目录即使来自废弃worktree也保留，清理的是Git登记与已合分支。

### 自动审批记录：范数Study make延后

工作目录：本机活动执行树`tmp/4b-bf16-five-methods-20261015`。命令：`D:/anaconda3/python.exe -m spec_mtp make studies/qwen3_4b_bf16_bias_norm_scan --round 1 --num-gpus 1 --init-gpu 0`（输出拟写入`.tmp/sd-repeat-20261016/norm-make.log`）。自动审批拒绝整条工具执行，理由为：8B GPU队列仍在运行，此时make可能重叠GPU/模型准备，违反显式单任务先后顺序；须等待8B队列退出，不得间接绕过。该make未执行，未触碰运行中8B源码/配置/队列；范数脚本及9项CPU测试就绪，但未make/launch。后续等8B自然退出再执行；不重复申请或启动旁路队列。

### PR42实际收尾补记

PR42已双CI通过合dev（8bc2df1，cpu-checks5m41s、Branch flow2s），其自身chore/merged-branch-cleanup-20261016已退出并删除本地/远端。因此最终为**28个本地、2个远端**；上表27/1以外新增这条自身分支（tip ddb1101cf3d016ec9b3444514cddf8d87e4f4dac）。周期复查基线更新为PR42合入后。活动8B分支和数据仍保留。

PR43的Linux CI为513 passed/1 failed，失败仅是新复制helper被Git转为LF、原字节CRLF断言不等。另用主仓集成分支保留原Git字节并补-text属性，保留严格字节断言；没有编辑活动GPU工作树、原Run或科学包。替代PR包含原8B执行代码，原PR按替代关系关闭但保留未合活动分支；不因CI问题重跑GPU。

### 2026-10-16 16:57里程碑合批与清理

BC10/30全480均原生成功并CPU逐token复核，PR44/45/46各自cpu-checks及Branch flow通过后，按长期授权合入dev：44→17ad1de0caaa3ebb35058ec991126f74f81f76b7；45→f83155c196e3d62422ef8b0ce815972b53dccc02；46→03a8f529c30f0061b7a6523c53fc7e5e1dd4f95d。PR45只集成后续范数扫描代码，未make或启动。CPU检查不是其尚未取得的GPU实验结果。

| 本地与远端均已删除的分支 | 删除前tip |
| --- | --- |
| fix/nonofficial-repeat-byte-provenance | 3a9d3a6b0233757f6a119fc845426b4215258f4d |
| experiment/4b-bias-norm-scan | 924ab4d8e5a7a660cf6c631b9983f0babf9ea907 |
| analysis/nonofficial-repeat-readout | 3393c26568536dbcdb3d3d663b502e4d058e7d09 |

三条各核本地/远端tip一致且是origin/dev祖先，主仓先退出到dev后git branch -d删除；远端普通push --delete，无强推。相对此前28/2，累计已清**31个本地、5个远端**。后续成果在analysis/sd-repeat-norm-results合批，不单开清理PR。

活动experiment/sd-nonofficial-repeat-norm虽已随PR44成为dev祖先，仍是BC60原队列的冻结执行分支，按活动例外保留本地、远端和工作树。集成前后HEAD均4bb28c79830b8f1db7cddf30cf80d6ddd5bd6e98；study.yaml SHA256均545c64f9fdf9e73582f929e5e6033d9f78eeb648f9bfcd8ffc37667b01cc08ae，未编辑活动源码/声明或重签Run。BC60 worker66500已自然接续，等待实测峰值加2GiB主机RAM准入；不可把“接续”等同于已载模。此分支在队列自然终结、保存证据且退出后再清，不删除数据。

合批后组合CPU检查34项通过（bias_norm_scan、repeat_readout、nonofficial_revalidation、docs、docs_index、4b_bf16_readout）；未启动额外GPU任务。活动执行树17份未跟踪旧范数准备源码已只读复制到本机.tmp/legacy-norm-preparation-20261016，逐文件尺寸/SHA及与已合dev版本的比较见manifest.json（4份字节不同）。原17份未移动、未覆盖，活动Run不变；待8B自然退出后仍需再次核验来源，保存完整旧目录（含被忽略缓存）再切换，不把这份源码副本当成实验结果备份。

### PR47 CPU队列交付后的自身清理

PR47已双CI通过合dev，merge4856cee0d86c1c80c4215b7e330878901890fb13；分析工作分支analysis/sd-repeat-norm-results在退出后删除本地和远端，tip fee5c066b18f9857f48803ff8bc4f27ffa91ebb7，已核为origin/dev祖先。累计清理为**32个本地、6个远端**；main仍b636f90e54c7641be6914fbccec13f64bd9cc04c。原BC60 worker66500、队列50576保留，活动执行树HEAD仍4bb28c7；未删除数据。

后续同主题结果在analysis/sd-bc60-norm-results攒到里程碑再PR，当前未合分支不删。CPU验收与只读4B对账已落dev，不以此声称BC60或范数八格完成；量化PPL实际占卡期间，原准入门继续非抢占等待。

### PR48与第五次合dev后的周期复查

PR48双CI通过合dev（25d07e9030ed94baed4d556481d8b88c192abc6f），完整CPU套件548 passed。已退出并删除analysis/sd-bc60-norm-results本地/远端，tip0531ad7c2ef2766fc1d4eb379f0a21e6ee94fcbe已核包含于origin/dev。累计**33个本地、7个远端**。从PR42基线后，44/45/46/47/48共5个合dev PR触发本次全面复查：其余已合普通topic无遗漏，open PR/issue均0，Git worktree只有主仓和仍活动的4b-bf16-five-methods-20261015；后者HEAD仍4bb28c7，BC60原队列保留。没有废弃新worktree或未合过时分支要删，没有删除数据。main仍b636f90e54c7641be6914fbccec13f64bd9cc04c。

下一周期从PR48之后计数；后续既有4B计数/深度CPU对账在analysis/4b-paired-depth-readout合批，未合分支保留。

### PR49完整CPU原始审计后的清理

PR49两项CI通过，已合dev（16d04f87ba52f8f20a018aecfb14ed88b5785993），本地完整CPU套件550项通过。analysis/4b-paired-depth-readout的tip bef77db已核为origin/dev祖先、本地与远端tip一致；主仓退出至dev后，普通push --delete及git branch -d分别删除远端和本地。累计**34个本地、8个远端**。这是PR48周期基线后第1个合dev PR；活动experiment/sd-nonofficial-repeat-norm及工作树保留，BC60原worker66500/队列50576未干预，不删数据、不改main。

当前后续结果分支analysis/sd-pending-results只登记实际清理，未合入前保留，等完整实验/CPU里程碑合批，不为本段单开PR。
