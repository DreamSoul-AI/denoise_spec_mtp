# 非官方8B独立复验：BC10全480检查点

本报告只验收BC10/单mask，不是三格全矩阵结论。原生队列已接续BC30；BC60待执行。固定SpecBench480、Qwen3-8B BF16/eager/T0、lambda=.1 updating mean、动态树剪枝、256/EOS、seed123；无测速。

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
