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
