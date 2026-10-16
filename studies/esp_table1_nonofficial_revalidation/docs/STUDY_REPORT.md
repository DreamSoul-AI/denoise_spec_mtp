# 非官方8B Table1独立复验

固定原480、Qwen3-8B BF16/T0、单mask、λ=.1 updating mean、动态树剪枝、256/EOS；无测速。

| BC | native | argmax checked/pass | pooled τ | prompt mean τ | category mean τ | pooled τ−论文 | pooled τ−旧结果 | AR exact/480 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | succeeded | 79757/True | 1.399047031 | 1.431765889 | 1.403033561 | n/a | 0.000000000 | 188/480 |
| 30 | succeeded | 79762/True | 1.563377504 | 1.593232237 | 1.563387272 | -0.066622496 | 0.000000000 | 175/480 |
| 60 | succeeded | 79618/True | 1.647301264 | 1.669498033 | 1.649693144 | -0.092698736 | 0.000000000 | 185/480 |

| BC | 聚合 | 原结果τ | 新τ−论文 | 新τ−原结果 |
| --- | --- | --- | --- | --- |
| 10 | pooled_tau | 1.399047031 | n/a | 0.000000000 |
| 10 | prompt_mean_tau | 1.431765889 | n/a | 0.000000000 |
| 10 | category_mean_pooled_tau | 1.403033561 | n/a | 0.000000000 |
| 30 | pooled_tau | 1.563377504 | -0.066622496 | 0.000000000 |
| 30 | prompt_mean_tau | 1.593232237 | -0.036767763 | 0.000000000 |
| 30 | category_mean_pooled_tau | 1.563387272 | -0.066612728 | 0.000000000 |
| 60 | pooled_tau | 1.647301264 | -0.092698736 | 0.000000000 |
| 60 | prompt_mean_tau | 1.669498033 | -0.070501967 | 0.000000000 |
| 60 | category_mean_pooled_tau | 1.649693144 | -0.090306856 | 0.000000000 |

主指标pooled τ=Σcommitted/Σdecode_calls，不含prefill；逐prompt等权及逐类别pooled后等权另列，均不是已确认的作者权重。AR一致率只诊断，不作失败门。

逐prompt accepted/calls/τ赢平输、输出长度、旧/新输出与AR摘要是否相同、AR首分叉及所有新旧目标差值见JSON；不同长度/轨迹的配对计数不能解释为速度或同前缀因果。

三格完整且原生process通过才生成正式repeat_evidence_v1.json；各已完成格可以单独列有效τ，但不称全矩阵完成。数学自检通过不等于论文目标数值已复现。

来源：`repeat_evidence_v1.json`，每格files_sha256给出Run原始结果/输入/审计路径与哈希；旧结果`studies/esp_table1_bf16_full_argmax/docs/protocol_evidence_v1.json`，新Run路径为每格run_path。原始tokens、logits、完整Run仅本机保留。
