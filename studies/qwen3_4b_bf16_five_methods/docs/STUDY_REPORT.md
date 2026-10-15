# Qwen3-4B BF16 paired report

完整验收：False；已完成 6/11。

BC30五方法全480已收齐，十组逐prompt配对全部复核通过。输出一阶2593e53990f8b097原生succeeded，81,209提交token argmax全过，owner/观测路径/prefill/实际BF16 mask范数证据也通过。相对输出零阶，accepted+191但主calls+139、输出总长+332，接受数W/T/L=209/72/199、调用数201/64/215；pooled τ从1.433178微升至1.435540，prompt均值却从1.483601微降至1.482532，未显示稳定接受/调用联合收益。两种输出方法相对输入零阶的总接受数/调用数有小幅改善，相对输入一阶均更差；本格输入一阶总accepted最高、主calls最少。这些计数包含输出路径/长度不同的情况，不作同输出测速或总体优越性结论。输出一阶独立AR一致184/480（38.33%）仅诊断，全部反例及首分叉保留。BC60 frozen mean 7fbe139b5c648484已自动接续，实际模型digest/runtime/seed/480输入及tied-storage契约一致，双mask/动态剪枝/BC60/λ0冻结配置已核对。source538e52c929a542a8及冻结PLAN/配置保持，完整Study与正式图仍待BC60五格及process通过。

| Cell | native | accepted | calls (prefill+decode) | new tokens | pooled τ | prompt mean τ | AR exact/n (rate) | argmax checked |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AR | succeeded | n/a | 81880 | 81880 | n/a | n/a | n/a | n/a |
| 30/frozen_mean | succeeded | 23188 | 57825 | 80929 | 1.4028947597872525 | 1.4759377696433031 | 184/480 (38.33%) | 80929 |
| 30/input_zero | succeeded | 23926 | 56938 | 80787 | 1.422420206170959 | 1.4798374864700174 | 168/480 (35.00%) | 80787 |
| 30/input_first | succeeded | 27371 | 53668 | 80898 | 1.5119575844175377 | 1.5430074255436272 | 175/480 (36.46%) | 80898 |
| 30/output_zero | succeeded | 24382 | 56577 | 80877 | 1.4331782448259265 | 1.483601057341492 | 177/480 (36.88%) | 80877 |
| 30/output_first | succeeded | 24573 | 56716 | 81209 | 1.4355395120563341 | 1.4825319338594185 | 184/480 (38.33%) | 81209 |
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
| 30/output_zero | 472/1/7 | -25303 |
| 30/output_first | 475/0/5 | -25164 |

以下胜负指第二方法相对第一方法；accepted越高越好，calls越低越好，两个指标分别判定。

| first → second | accepted W/T/L | calls W/T/L | Δaccepted | Δcalls | Δnew tokens |
| --- | --- | --- | --- | --- | --- |
| 30/frozen_mean → 30/input_zero | 229/24/227 | 235/21/224 | 738 | -887 | -142 |
| 30/frozen_mean → 30/input_first | 301/34/145 | 294/31/155 | 4183 | -4157 | -31 |
| 30/frozen_mean → 30/output_zero | 245/28/207 | 239/30/211 | 1194 | -1248 | -52 |
| 30/frozen_mean → 30/output_first | 248/30/202 | 235/29/216 | 1385 | -1109 | 280 |
| 30/input_zero → 30/input_first | 364/35/81 | 352/24/104 | 3445 | -3270 | 111 |
| 30/input_zero → 30/output_zero | 231/38/211 | 236/34/210 | 456 | -361 | 90 |
| 30/input_zero → 30/output_first | 231/42/207 | 232/36/212 | 647 | -222 | 422 |
| 30/input_first → 30/output_zero | 106/40/334 | 116/42/322 | -2989 | 2909 | -21 |
| 30/input_first → 30/output_first | 118/31/331 | 121/33/326 | -2798 | 3048 | 311 |
| 30/output_zero → 30/output_first | 209/72/199 | 201/64/215 | 191 | 139 | 332 |

accepted为EOS/预算裁剪前候选接受数；committed及τ包含bonus、按裁剪后实际解码提交数计算，不含prefill首token。argmax审计含首token且必须全过；独立AR首分叉和输出长度全部保留，不作为失败门。AR参考不冒充Spec验证argmax审计。

模型、forward及最终mask为BF16；输出EMA/范数沿用原生FP32内部状态。不同方法β等沿用预先定义配方，不声称差异仅由输入/输出空间造成。单seed、固定480条，不推断总体优越或测速收益；零计时字段为占位。

尚无完整实测结论；本机pending文件不作为公开证据。

[冻结计划](PLAN.md)；原始tokens、完整Run和权重仅本机保留。
