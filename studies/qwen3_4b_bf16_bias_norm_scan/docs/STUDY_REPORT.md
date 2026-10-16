# 4B BF16范数扫描：首格恢复与复用端点验收

> 最新：template/0.5×首格Run6ee3f749ee20c450全480完成，pooled τ1.4713896458，argmax80,940/80,940。
> collect包导出故障已用同一原生collector与既有重验工具恢复，execute未重跑，原始SHA/冻结源未改，旧失败result保留。
> 剩余七格在独立continuation Study续跑，旧七pending不记成功，完整范数矩阵未完成。
> BC60已自然获得原准入并在运行；新单队列等待其退出。详情见[续跑报告](../../qwen3_4b_bf16_bias_norm_continuation/docs/STUDY_REPORT.md)。

## 已复核的0×/1×端点

固定SpecBench480、Qwen3-4B BF16/T0、BC30/双mask、256/EOS；来源为既有六格方向证据及五方法证据，保留一个共享零偏置。

| 端点 | pooled τ | 重核提交token数 | 原始文件数 |
| --- | --- | --- | --- |
| zero/0 | 1.422420206170959 | 80787 | 6 |
| template/1 | 1.5077776528355635 | 80932 | 6 |
| random0/1 | 1.4951881338086705 | 81425 | 6 |
| random1/1 | 1.4643490856418613 | 81356 | 6 |
| random2/1 | 1.5238847141634166 | 80583 | 6 |

数据均在[reused_readiness_v1.json](reused_readiness_v1.json)的cells/totals；formal_sources给出两份正式源文件及SHA，data_root、study_path、run_id、files_sha256定位30份实际源文件。共享AR另核原始观测SHA和原输入IDs、81880个生成token/调用计数。check_refs核原始模型清单、480输入和固定数据SHA；未读模型权重或执行forward。

每个Spec端点从原始stats重对accepted/committed/decode_calls/new_tokens和含prefill调用，复用现有数学检查函数逐token核已存argmax、实际输出、前向owner与覆盖；汇总与公开行计数一致。原始result/source/config等6文件均匹配正式源SHA，不以当前验证器重签历史Run或声称重算验证logits。

## 同前缀首块与完整路径边界

| 相对zero/0的第二方法 | 首块接受数胜/平/负 | 相同前缀且有块 | 前缀不同 / 缺块 |
| --- | --- | --- | --- |
| template/1 | 26 / 341 / 113 | 480 | 0 / 0 |
| random0/1 | 56 / 361 / 63 | 480 | 0 / 0 |
| random1/1 | 55 / 367 / 58 | 480 | 0 / 0 |
| random2/1 | 30 / 361 / 89 | 480 | 0 / 0 |

来源为同一JSON的paired_comparisons中first=zero/0的first_block_same_prefix。前缀按原input IDs加实际prefill首token的摘要匹配；首块接受数取trace[0].accepted_nodes长度。此四格在该指标上均输局多于赢局，普遍初始化获益的解释受到限制；该胜负计数不等于均值接受差，也不推断后续分叉路径的因果。完整路径τ受调用权重、输出长度与路径分布影响，不能用首块统计单独解释全部收益。

范数扫描的template/1沿用E3固定v（1.5077776528355635）；E2五方法原生更新输入一阶（1.51195758，完整值在原paired_evidence_v1.json）分别保留。这轮只复用0/1端点，0.5/2未观测；没有拟合、插值或选择最优倍率。

## 后续脚本与成功门

只读入口、CPU环境和跨执行副本参数见[README](../README.md#只读端点准备与后续验收)。--check-reused不调用make、新Run验收或绘图，输出complete=false/reused_only=true/new_cells_inspected=false。正常读出仍先核原生来源；索引必须逐项匹配预注册八格及其顺序、每格一个Run，成功cfg的完整spec也须匹配。缺格、重复、乱序、错误倍率/配方、多Run均拒绝。

BC60及8B队列自然结束后，保存原始证据并保留旧未提交范数准备，才同步已合代码、make和单队列执行八格。每格480、同固定prompt/模板、数学门全过；独立AR仅诊断且复用既有参考。完整13端点及native process通过后生成norm_evidence_v1.json/曲线，再报告三种τ、逐prompt接受/calls/τ赢平输、长度、首块和深度；不能以本CPU检查点代替新格。

18项范数CPU回归及相关读出/配对/文档共50项通过，新增缺格/重复/乱序/倍率或spec漂移/多Run拒绝，以及只读模式不验收新格、不绘图、缺少本机原始证据不输出成功。tiny CPU回归和本次旧记录重核均不代替新的4B GPU扫描。

PR48首轮Linux CI为547 passed/1 failed，唯一失败是公开formal_sources键由Windows反斜杠序列化，Linux无法定位相对源路径。写出端改用as_posix统一仓库相对路径，并增加公开检查点不得含反斜杠的断言；原始文件、SHA和数学门未改。
