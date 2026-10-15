# Qwen3-4B BF16全480方向对照

原数据/模板/停止规则不变，先做BC30全480：严格固定e2−e1、同范数随机方向三个种子、零偏置、内容初始化。零偏置复用原输入零阶，新增五格使用原生Study流程。方向控制不是新增主方法，不能将原四窗口结果外推全量。

开跑依据：[PLAN](docs/PLAN.md)。结果：[阶段报告](docs/STUDY_REPORT.md)。原五方法和AR来源：[正式证据](../qwen3_4b_bf16_five_methods/docs/paired_evidence_v1.json)。
