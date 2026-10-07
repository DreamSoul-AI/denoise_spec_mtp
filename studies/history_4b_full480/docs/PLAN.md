# PLAN — history_4b_full480

写在开跑之前。切片上的结论已经齐：4B、β = 0.9999、λ = 0.1、γ = 1 的均值加 gamma，在 first 26、next 52、last 52 上都高于各自记下的冻结均值。这一轮问同一对参数在 SpecBench 全部 480 条上是否仍高于冻结均值。

## 一、假设

均值加 gamma 的 overall `accept_d1` 大于冻结均值。两格都是新跑，不引用切片数字做分子。

若均值加 gamma 不高于冻结均值，切片上的超出不能当成全量结果。不改 β、λ、γ。

## 二、固定

Qwen3-4B，float32，ModelScope，树 `[14]`，一个槽，贪心，temperature 0，最多 100 个新 token，seed 123，thinking 关。不设 skip / take。`num_eval_prompts` 为 480。每一格 `exact_match_rate` 必须是 1，否则该格作废，不比较。

## 三、刻意不做

不把 480 条拿来重选参数。不扫 γ 和 β。不加深树。
