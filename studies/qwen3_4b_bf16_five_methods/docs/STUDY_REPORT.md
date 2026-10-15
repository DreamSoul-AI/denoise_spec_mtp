# Qwen3-4B BF16 paired report

完整验收：False；已完成 1/11。

运行检查点：独立AR 0e25348a3a60d601全480条原生succeeded，阅读器再次通过verify_evidence、来源/Study冻结门及480输入/14模型文件SHA核对，共81,880新token和81,880主model calls。source digest 538e52c929a542a8，实际BF16 model digest 535de659a78af3855c5eafe361e9244ec4d793fc2abd2e95e24a71debe64605f。BC30 frozen mean 30d0bfa0924c4478已自动接续；首forward前已实测与AR的model digest、runtime、seed和全部prompt相同，双mask/BC30/动态剪枝/λ=0/update=false符合冻结配置。方法格尚无终态，不能据此推断收益；完整paired证据仍待11格与native process全部通过。

| Cell | native | accepted | calls (prefill+decode) | new tokens | pooled τ | prompt mean τ | AR exact | argmax checked |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AR | succeeded | n/a | 81880 | 81880 | n/a | n/a | n/a | n/a |
| 30/frozen_mean | pending | pending | pending | pending | pending | pending | pending | pending |
| 30/input_zero | pending | pending | pending | pending | pending | pending | pending | pending |
| 30/input_first | pending | pending | pending | pending | pending | pending | pending | pending |
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

以下胜负指第二方法相对第一方法；accepted越高越好，calls越低越好，两个指标分别判定。

| first → second | accepted W/T/L | calls W/T/L | Δaccepted | Δcalls | Δnew tokens |
| --- | --- | --- | --- | --- | --- |

accepted为EOS/预算裁剪前候选接受数；committed及τ包含bonus、按裁剪后实际解码提交数计算，不含prefill首token。argmax审计含首token且必须全过；独立AR首分叉和输出长度全部保留，不作为失败门。AR参考不冒充Spec验证argmax审计。

模型、forward及最终mask为BF16；输出EMA/范数沿用原生FP32内部状态。不同方法β等沿用预先定义配方，不声称差异仅由输入/输出空间造成。单seed、固定480条，不推断总体优越或测速收益；零计时字段为占位。

尚无完整实测结论；本机pending文件不作为公开证据。

[冻结计划](PLAN.md)；原始tokens、完整Run和权重仅本机保留。
