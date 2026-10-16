# 非官方8B独立复验：BC10/BC30全480检查点

BC10/BC30单mask均已原生成功，不是三格全矩阵结论。BC60已由原队列接续，等待实测峰值加2GiB的主机RAM准入。固定SpecBench480、Qwen3-8B BF16/eager/T0、lambda=.1 updating mean、动态树剪枝、256/EOS、seed123；无测速。

| 指标 | 新BC10 | 与旧BC10差值 |
| --- | --- | --- |
| pooled tau | 1.3990470307950233 | 0 |
| prompt mean tau | 1.43176588861066 | 0 |
| category mean pooled tau | 1.4030335607141575 | 0 |
| 接受draft数 | 22691 | 0 |
| decode calls / 含prefill总调用 | 56665 / 57145 | 0 / 0 |
| 实际新token / decode committed | 79757 / 79277 | 0 / 0 |
| verifier argmax覆盖 | 79757/79757，全过 | 与旧覆盖相同 |
| 独立AR完全一致 | 188/480，39.1667% | 0 |

逐prompt accepted、calls、tau三项均为0胜/480平/0负；输出摘要和独立AR摘要分别480/480与旧结果一致。argmax审计JSONL的SHA也与旧格相同。这证明当前本机同设置下BC10旧结果可完整重复；论文没有BC10目标，不能由此声称BC30=1.63或BC60=1.74已复现，也不能外推后两格。

所有数值来自[bc10_checkpoint_v1.json](bc10_checkpoint_v1.json)的totals、tau_deltas、vs_original；文件含逐qid计数、输出/AR摘要及首分叉。新Run80ff7a41958d8134的result、decode_observations、decode_inputs、argmax_audit路径和SHA见其run_path/files。旧Run为dfe1b9c8d5d12e92，原证据为studies/esp_table1_bf16_full_argmax/docs/protocol_evidence_v1.json。本机新Run位于4b-bf16-five-methods-20261015执行树，旧Run位于主仓；完整tokens、权重和Run不入Git。

原生result为succeeded，政策verifier-argmax-v1；数学门与独立AR诊断分开。该检查点用已提交f677479读出逐token重核，不修改执行源码或旧结果。8B清单本身无EOS字段，改从SHA已匹配的旧Run真实decode_inputs核EOS及派生device；新旧实际设置一致。完整三格报告须待BC30/60和native process完成后再写，保留一切负结果。

JSON逐条spec_time/ar_time的0为禁用解码时钟后的原生占位，不是测量。已保存的执行commit4bb28c7与读出commit f677479分开记录；不重签旧Run。

## BC30全480结果（2026-10-16）

| 指标 | 新BC30 | 新减论文1.63 | 新减旧BC30 |
| --- | --- | --- | --- |
| pooled tau | 1.5633775043382236 | -0.06662249566177625 | 0 |
| prompt mean tau | 1.5932322369198653 | -0.03676776308013463 | 0 |
| category mean pooled tau | 1.5633872721805147 | -0.06661272781948524 | 0 |
| 接受draft数 | 28684 | 不适用 | 0 |
| decode calls / 含prefill总调用 | 50712 / 51192 | 不适用 | 0 / 0 |
| 实际新token / decode committed | 79762 / 79282 | 不适用 | 0 / 0 |
| verifier argmax覆盖 | 79762/79762，全过 | 不适用 | 与旧相同 |
| 独立AR完全一致 | 175/480，36.4583% | 不适用 | 0 |

出处：[bc30_checkpoint_v1.json](bc30_checkpoint_v1.json)，含原始result/config/输入/审计SHA、实际Run路径、480条计数与输出/AR摘要。新Run88d13ec4ecf0023c对旧b9b54923b1b9ea9f逐prompt accepted、calls、tau均0胜/480平/0负，输出/AR摘要各480一致。与旧结果完全重复仍未达到论文1.63，不把另两种聚合选作主结果。BC60论文1.74待本轮完整读数。

CPU重核使用活动执行副本冻结验证器（source e963521adc8cb86f），逐token验argmax、旧真实输入合同、模型文件SHA、BF16默认数值设置；主仓已合的来源改动不能代替该冻结环境。第一次误用主仓验证器被来源检查拒绝，改用执行副本后全过，未修改或放宽验证器。

BC60 Runa8e6bba1dd1d80e2由原队列自然接续，worker PID66500；16:44日志available=13197508608字节，低于19452530688字节门，尚未载模。保持等待、不重开、不终止其他任务。后续进度以其实际资产和队列日志为准。

CPU队列另用现有4B读出函数重算正式paired_evidence_v1.json（SHA8e85ac6ea9984047abf0ffd5d6653b28b6aadd74aa876139fa10465dc5bbf274）：11格汇总、20对480条赢平输全部与已发布证据一致；源证据含809118个已审计Spec提交token。这只是汇总对账，不声称新增GPU或token审计。读取/门/配对18项及文档6项回归通过；BC30加入同一检查点回归后另验。

## 恢复核验（2026-10-16 16:33，北京时间）

目标状态为active。原队列PID50576、监控50640、BC30 worker72280及Run88d13ec4ecf0023c均已核实；未中断或重复启动。BC30进度文件已到367/480，该值仅表示进度，不是全480有效τ或终验。初始准入记录在15:18:33北京时间通过：host_available=22004486144字节，旧实测峰值17305047040加2GiB门为19452530688字节；没有放宽RAM门。BC60单mask Runa8e6bba1dd1d80e2仍由原队列后接。

进度及准入来源：执行副本studies/esp_table1_nonofficial_revalidation/runs/88d13ec4ecf0023c/assets/revalidation_progress.json、resource_admission_initial.json；进程命令已匹配同一Study/Run。CPU结果读取、数学门与4B配对回归18项通过（test_repeat_readout.py、test_nonofficial_revalidation.py、structure/algorithm/test_4b_bf16_readout.py），GPU不可见环境执行。PR44/45/46的cpu-checks和Branch flow均已通过；同主题后续证据攒到完整里程碑再收尾，不以代码检查代替GPU结果。
