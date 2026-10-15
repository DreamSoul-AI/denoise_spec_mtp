# Qwen3-4B BF16 paired report

完整验收：False；已完成 4/11。

运行检查点：输入一阶45c0823a28799080全480原生succeeded，80,898提交token的argmax全过；阅读器再次通过原始证据、全部模型/输入SHA与冻结门。相对输入零阶，accepted总数+3,445、主calls−3,270，逐prompt接受数W/T/L=364/35/81、调用数352/24/104，输出总长+111；相对frozen mean，accepted+4,183、主calls−4,157，接受数301/34/145、调用数294/31/155，输出总长−31。独立AR一致175/480（36.46%）仅诊断，首分叉及全部反例保留；不同输出长度与路径下不作同输出测速结论。输出零阶fb6416c3a8a77ec3已自动接续，实际模型digest/runtime/seed/480输入及tied-storage契约与AR一致，order0/β=.9/β′=.99符合冻结配置。source538e52c929a542a8及冻结PLAN/配置保持；输出方法和BC60仍待完整验收。

| Cell | native | accepted | calls (prefill+decode) | new tokens | pooled τ | prompt mean τ | AR exact/n (rate) | argmax checked |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AR | succeeded | n/a | 81880 | 81880 | n/a | n/a | n/a | n/a |
| 30/frozen_mean | succeeded | 23188 | 57825 | 80929 | 1.4028947597872525 | 1.4759377696433031 | 184/480 (38.33%) | 80929 |
| 30/input_zero | succeeded | 23926 | 56938 | 80787 | 1.422420206170959 | 1.4798374864700174 | 168/480 (35.00%) | 80787 |
| 30/input_first | succeeded | 27371 | 53668 | 80898 | 1.5119575844175377 | 1.5430074255436272 | 175/480 (36.46%) | 80898 |
| 30/output_zero | pending | pending | pending | pending | pending | pending | pending | pending |
| 30/output_first | pending | pending | pending | pending | pending | pending | pending | pending |
| 60/frozen_mean | pending | pending | pending | pending | pending | pending | pending | pending |
| 60/input_zero | pending | pending | pending | pending | pending | pending | pending | pending |
| 60/input_first | pending | pending | pending | pending | pending | pending | pending | pending |
| 60/output_zero | pending | pending | pending | pending | pending | pending | pending | pending |
| 60/output_first | pending | pending | pending | pending | pending | pending | pending | pending |

相对独立AR的逐prompt调用数比较；calls越低越好。AR没有draft接受数，该指标不适用。输出长度及AR首分叉单列，不能将不同长度的调用数直接解释为等长加速。

| Cell | calls vs AR W/T/L | Δcalls vs AR |
| --- | --- | --- |
| 30/frozen_mean | 469/1/10 | -24055 |
| 30/input_zero | 476/0/4 | -24942 |
| 30/input_first | 477/0/3 | -28212 |

以下胜负指第二方法相对第一方法；accepted越高越好，calls越低越好，两个指标分别判定。

| first → second | accepted W/T/L | calls W/T/L | Δaccepted | Δcalls | Δnew tokens |
| --- | --- | --- | --- | --- | --- |
| 30/frozen_mean → 30/input_zero | 229/24/227 | 235/21/224 | 738 | -887 | -142 |
| 30/frozen_mean → 30/input_first | 301/34/145 | 294/31/155 | 4183 | -4157 | -31 |
| 30/input_zero → 30/input_first | 364/35/81 | 352/24/104 | 3445 | -3270 | 111 |

accepted为EOS/预算裁剪前候选接受数；committed及τ包含bonus、按裁剪后实际解码提交数计算，不含prefill首token。argmax审计含首token且必须全过；独立AR首分叉和输出长度全部保留，不作为失败门。AR参考不冒充Spec验证argmax审计。

模型、forward及最终mask为BF16；输出EMA/范数沿用原生FP32内部状态。不同方法β等沿用预先定义配方，不声称差异仅由输入/输出空间造成。单seed、固定480条，不推断总体优越或测速收益；零计时字段为占位。

尚无完整实测结论；本机pending文件不作为公开证据。

[冻结计划](PLAN.md)；原始tokens、完整Run和权重仅本机保留。
