# Qwen3-4B BF16 paired report

完整验收：False；已完成 0/11。

| Cell | native | accepted | calls (prefill+decode) | new tokens | pooled τ | prompt mean τ | AR exact | argmax checked |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AR | pending | pending | pending | pending | pending | pending | pending | pending |
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

以下胜负指第二方法相对第一方法；accepted越高越好，calls越低越好，两个指标分别判定。

| first → second | accepted W/T/L | calls W/T/L | Δaccepted | Δcalls | Δnew tokens |
| --- | --- | --- | --- | --- | --- |

accepted为EOS/预算裁剪前候选接受数；committed及τ包含bonus、按裁剪后实际解码提交数计算，不含prefill首token。argmax审计含首token且必须全过；独立AR首分叉和输出长度全部保留，不作为失败门。AR参考不冒充Spec验证argmax审计。

模型、forward及最终mask为BF16；输出EMA/范数沿用原生FP32内部状态。不同方法β等沿用预先定义配方，不声称差异仅由输入/输出空间造成。单seed、固定480条，不推断总体优越或测速收益；零计时字段为占位。

尚无完整实测结论；本机pending文件不作为公开证据。

[冻结计划](PLAN.md)；原始tokens、完整Run和权重仅本机保留。
