# ESP Table1 非作者官方本地栈：全480原始证据复核

本轮状态：BC10/1、30/1、60/1三主格均有完整480条且原始数学门复核通过，不是待执行格。
结论：BC30/60 pooled τ=1.563378/1.647301，低于论文1.63/1.74；本地有效结果，不是作者官方复现。
执行范围：CPU只读复核历史Run；本轮GPU执行0，未重跑或重签Run，不测速。
下一步：继续核验作者入口；只对明确缺格/新协议建立新Study，保留全部现有负结果。

## 范围与复用依据

最新用户允许官方入口仍缺时使用本地或HF第三方栈，并标明非作者官方。本地实现已经在[冻结Study](../../studies/esp_table1_bf16_full_argmax/README.md)完成同一480条、相同三主格，另有60/2对照。按[仓库规则](../../AGENTS.md)“已有数字的格子不重跑”，本次逐项复核原始记录后复用，没有为了占卡重复相同矩阵。未改旧PLAN、原始观测、result、来源锁或旧native process，未把已见结果重新预注册。

下表所有数字来自[原正式结果](../../studies/esp_table1_bf16_full_argmax/docs/protocol_evidence_v1.json)的四个cells及本次[复核审计](esp-table1-nonofficial-full480-recheck-2026-10-16.json)。审计逐格列config、decode_inputs、decode_observations、argmax JSONL、numeric policy、source manifest、result的路径/SHA；完整Run/token只留本机。

实际设置为Qwen3-8B、BF16/eager、T0、256上限/EOS/seed123，同一ModelScope模型内容哈希、固定480首轮，dynamic/pruning、updating mean λ=0.1；BC60主格单mask/29 draft节点，60/2仅对照。不改prompt、模板或样本筛选。enable_thinking=false是本地协议选择，并非作者已确认配置；该updating mean区别于4B用户定义的ESP frozen mean。

## 全量结果

| BC/mask | 角色 | 原Run | n | pooled τ | 论文τ | 差值 | prompt mean τ | category mean τ | AR exact（仅诊断） | argmax token |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 10/1 | 主 | `dfe1b9c8d5d12e92` | 480 | 1.399047 | — | — | 1.431766 | 1.403034 | 188/480（39.17%） | 79,757 / 全过 |
| 30/1 | 主 | `b9b54923b1b9ea9f` | 480 | 1.563378 | 1.63 | -0.066622 | 1.593232 | 1.563387 | 175/480（36.46%） | 79,762 / 全过 |
| 60/1 | 主 | `3f3d0f9a84341c0b` | 480 | 1.647301 | 1.74 | -0.092699 | 1.669498 | 1.649693 | 185/480（38.54%） | 79,618 / 全过 |
| 60/2 | 对照 | `555ff70d57ce05b0` | 480 | 1.603729 | 1.74 | -0.136271 | 1.664315 | 1.616079 | 187/480（38.96%） | 79,693 / 全过 |

pooled τ=Σcommitted/Σdecode_calls；prompt mean为480条比值等权均值；category mean先对本地13类分别pooled再等权。三种都保留，不挑最接近论文者。committed含bonus且经EOS/预算裁剪，不含prefill首token；argmax检查含prefill，实际model_calls=decode_calls+480。逐prompt AR首分叉和输出长度仍在原正式结果中，AR失配不作失败门。

三主格共1,440次prompt执行、239,137个输出token检查；含60/2共1,920次、318,830个token。始终为同一批480条，不是1,920条独立问题。每格只有一个seed/Run，复核不是新的重复实验，也不建立稳定性结论。

## 本轮实际复核与可重放入口

- raw、inputs、argmax JSONL的SHA与原正式结果逐格一致；raw.inputs_digest、原config_digest、冻结480条token序列/顺序一致。模型文件绑定与原ModelScope snapshot全部16项一致；本轮未重新读16GB权重或加载模型。
- 调用已有`src/spec_mtp/structure/artifact/validation.py:evaluate_run`，从原始观测/JSONL检查全部提交token的chosen/argmax、forward/正确owner行、数量、输入/输出token哈希；四格全过。逐prompt trace的accepted、committed、decode calls与正式行逐项一致，三种τ重算一致。
- 原执行source digest为`670c744e0535dcad`、git head为`b052636c98543ff518e3d1057b6a22d06342275b`、package_dirty=false，保持原记录。本次只读validator SHA为`bade4aaea923d3495ca970d02fb1c9ed188bf50061a9ed5db932a7dc26e147a2`，与历史重新验收validator分开记录，不以当前源码重签旧Run，未再次运行native summarize/process。

在保留完整原始Run的仓库根目录，设置`PYTHONPATH=src`、`CUDA_VISIBLE_DEVICES`为空后，可运行以下Python复核核心哈希及数学门。已有`python tools/analyze_esp_table1_gap.py`重算三种聚合/目标差值，输出与原账本逐字一致才通过。

```python
from pathlib import Path
import hashlib, json, yaml
from spec_mtp.structure.artifact.validation import evaluate_run
p = json.loads(Path('docs/research/esp-table1-nonofficial-full480-recheck-2026-10-16.json').read_text(encoding='utf-8'))
for cell in p['cells']:
    for file, expected in cell['files'].items():
        assert hashlib.sha256(Path(file).read_bytes()).hexdigest() == expected
    run = Path('studies/esp_table1_bf16_full_argmax/runs') / cell['run_id']
    gate = evaluate_run(yaml.safe_load((run/'config.yaml').read_text(encoding='utf-8')), run/'assets')
    assert gate['passed'] and gate['argmax_all_passed']
    assert gate['argmax_checked_tokens'] == cell['argmax_checked_tokens']
    assert gate['validator_sha256'] == cell['readout_validator_sha256']
    print(cell['BC'], cell['num_masks'], gate['argmax_checked_tokens'], cell['pooled_tau'])
```

一次性额外协议/逐prompt复核脚本指纹也保存在审计JSON。长期入口是已有验证器/分析器，不新增算法或框架。公开JSON只包含标量与哈希；外部读者未持有本机完整Run不能进行raw token重放，不能将摘要当原始logits。

## 官方与HF第三方状态

本轮刷新PMLR条目历史及固定出版文件，仍为commit `2c576965bd7afea1251244b16f5140a3ff26ef70`、`extras: []`。HF论文索引200、关联models/datasets/spaces各0，无新增代码字段；HF索引不是作者身份凭据。三份响应和出版原文SHA见审计official_source_refresh，OpenReview请求0。作者官方ESP入口仍未核验；这只阻塞官方归属，**不再把本地非官方全480标为未运行**。

[指定HF第三方原码](esp-third-party-reproduction-2026-10-15.md)仍非官方：此前固定q121的BC10/30/60均首token argmax失败，valid_tau=null，未跑其全480。允许第三方栈不等于放宽数学门，因此本轮选择已有有效本地栈，而非扩跑失败原算法；未改其算法追数。原CLI的FP16/示例prompt/测速、flat候选等差异不满足完整主协议。

## 结论与边界

所有请求主格有效、覆盖全480，但BC30/60分别差−0.066622/−0.092699，论文τ目标尚未数值复现。AR exact约36–39%仅作诊断，数学门全过，不能声称与独立AR完全一致。输出长度不同，接受数/调用数比较应结合逐prompt长度，不能由总量推出纯候选质量的因果优势。不测TPS/SR，不用占位timing作性能结论。

论文精度、immutable checkpoint revision、thinking/template、任务纳入/权重及100/256长度表述仍有作者侧未确认项；本地16项模型内容哈希固定，但Run中model_commit=null。既有[差距分析](esp-table1-gap-analysis-2026-10-16.md)保留这些替代解释；不钻算子、不改数据追目标。继续只读追作者原码，入口到位后实际非抢占准入，不把本报告改标为官方成功。
