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
