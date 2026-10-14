# ESP Table 1 Qwen3-8B / BF16 preflight — failed correctness gate

2026-10-15：13条/category-first，三个动态树+剪枝格均未通过独立AR逐token核验。**尚未复现Table1，完整480条尚未启动，4B五方法仍暂停。**

| BC | exact / 13 | accepted drafts | main calls | pooled τ（失配格诊断值） | mean prompt τ（诊断值） |
| --- | --- | --- | --- | --- | --- |
| 10 | 6 | 634 | 1726 | 1.369527 | 1.404570 |
| 30 | 6 | 831 | 1525 | 1.548280 | 1.558478 |
| 60 | 5 | 868 | 1499 | 1.579408 | 1.601749 |

这些τ来自不等于独立AR的输出，不能作为论文数值复现成功证据；即使某种聚合接近目标，也不越过正确性门。256上限/提前EOS、T0/BF16/eager、λ=.1 updating mean、BC10/30单mask、BC60双mask；全部实际clock字段为0占位，未测速。

[冻结协议](PLAN.md)、[官方数据与本地检查点清单](modelscope_snapshot.json)、[所选token manifest](prompts_manifest.json)、[原始token与首分叉/计数/哈希证据](preflight_evidence_v1.json)。SpecMTP源码digest670c744e0535dcad不变。

BC10最早分叉为q81新token零基index9；BC30同一位置也分叉。没有证据把它归因到某个kernel或认为模型语义错误。当前假设：BF16批量几何/归约舍入导致低margin argmax边界变化；仍待可控证伪。下一步已冻结[BF16数值控制](../../esp_table1_bf16_numerics/docs/PLAN.md)，只服务8B ESP门。

三格第一轮execute/collect完成，summarize分别拒绝exact=6/13、6/13、5/13。native launch默认自动retry，BC10重复准备后已停止本任务的重试链；raw/input绑定再次校验一致。第一轮原始观测保留，BC10当前生命周期不冒称成功/完整终验。后续明确retry_failed=false，失败不重签。其他任务未停止。

共享GPU容量采样包括背景进程，不用于性能排名。缓存immutable revision未核实，实际16文件SHA与ModelScope名/尺寸匹配。未切FP32、未teacher强制修正、未删反例或筛样本。
