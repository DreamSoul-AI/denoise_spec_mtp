# ESP Table1输入合同与计数聚合：CPU对账

当前步骤：对既有四格全480原始输入/输出与逐块trace做CPU核验；没有外部检索、下载、模型forward、GPU或新Run。
结论：480条首轮输入在四格重新渲染均逐token一致，无过滤；本地聚合权重与停止计数已可对账，仍不足以解释作者τ差距。
数字出处：[本轮CPU证据](esp-table1-cpu-contract-reconciliation-2026-10-16.json)，`input_summary`、`input_contract`、`cells`；绑定原正式证据与PR36审计的路径/SHA。
下一步：取得作者输入/停止/计数合同后按qid及token摘要对齐；仍无官方入口时不重跑已完整矩阵。
阻塞：作者Table1逐条输入、任务权重、精确停止/计数及checkpoint合同缺失；不能从本地一致性推导双方一致。

## 一、范围、入口和来源

按[缺口登记](esp-table1-protocol-gaps-2026-10-16.md)的P1输入合同、P2计数与聚合推进。复用既有输入加载/渲染函数和证据摘要函数，新增只读工具[reconcile_esp_table1_contract.py](../../tools/reconcile_esp_table1_contract.py)，没有修改解码器、冻结Study或原Run；旧[差距账本](esp-table1-gap-analysis-2026-10-16.json)保持原字节。

命令：`PYTHONPATH=src python tools/reconcile_esp_table1_contract.py --tokenizer D:/models/Qwen3-8B`。工具强制隐藏CUDA并离线加载已有tokenizer，只读本地小文件/数据与历史Run，不加载模型权重。公开JSON的sources记录原正式结果、PR36复核和三个当前数据加载/渲染文件SHA，analyzer_sha256记录工具版本；四格raw/inputs/argmax及其他文件先与PR36逐项核对哈希，沿用其已通过的数学门，不重新签收Run。

需要原始Run和同一tokenizer才能重放完整核验；公开摘要不包含prompt正文、token序列或logits，不把哈希当原始数据。已有证据不同时拒绝覆盖输出；首次未提交分析草稿留在`.tmp/`，不删除数据。

## 二、P1输入合同：本地能确认到哪里

原数据文件、Study共享数据文件均匹配历史输入记录的SHA，未筛prompt。复用`load_records`的category排序/文件内顺序及首轮选择，核对480个qid和category，并用原生`encode`及本地tokenizer重渲染，与四格`decode_inputs.json`逐token比较。四格的eval设置、数据设置、EOS、qid顺序、词表与chat template摘要也全部相同。

- 固定480条，输入共136183 token，最短21、最长1500、中位68.5；40960的输入上限没有过滤任何条目。
- 源数据有80条包含多轮，实际全部取`turns[0]`；不称为完整多轮评测。没有根据τ改模板、文本、顺序或截断。
- 本地使用chat template、`add_generation_prompt=True`、`enable_thinking=False`；重新加载tokenizer的类、词表、模板及special tokens与保存内容一致，EOS为151645。
- tokenizer历史commit为null。此次重渲染和文件/词表/模板绑定证明本地输入可恢复，不能补出作者历史模型revision、thinking、模板或qid清单。

数字在`input_summary`；摘要和配置在`input_contract`。四格相同输入排除了**本地BC格之间输入发生漂移**，没有排除**本地与作者输入不同**。

## 三、P2完整路径计数与停止原因

下表逐格来自`cells[BC/mask]`；论文目标BC30/60为1.63/1.74，60/2只是预先声明的附加对照，不参与挑优。

| BC/mask | pooled τ | prompt mean | 13类等权pooled mean | pooled−论文目标 | EOS低于256 / EOS恰256 / 达256无EOS |
| --- | --- | --- | --- | --- | --- |
| 10/1 | 1.399047 | 1.431766 | 1.403034 | — | 323 / 0 / 157 |
| 30/1 | 1.563378 | 1.593232 | 1.563387 | -0.066622 | 320 / 0 / 160 |
| 60/1 | 1.647301 | 1.669498 | 1.649693 | -0.092699 | 323 / 1 / 156 |
| 60/2 | 1.603729 | 1.664315 | 1.616079 | -0.136271 | 324 / 1 / 155 |

三聚合重算与原正式结果一致。逐条核对输出前缀等于输入、`new_tokens=committed+1`、decode_calls等于trace块数、逐块committed token串联等于prefill之后的输出；所有EOS若出现均是最后一个生成token。四格其他停止0、hit_context_limit均0；因此低于256的输出是记录的EOS停止，不是漏掉prompt或上下文溢出。BC60/1和60/2各有1条EOS恰好在256，两种条件同时满足，不能将这两条唯一归因于预算或EOS。

### 聚合差的精确拆分

令每条τ为t_i、decode calls为c_i，n=480。pooled−prompt mean恰为`Cov_n(c,t)/mean(c)`，其中Cov_n分母为n。再令q_g为类别样本占比，w_g为类别decode-call占比，T_g为类别pooled，M_g为类别prompt mean，则：

`pooled−prompt mean = Σ q_g(T_g−M_g) + Σ(w_g−q_g)T_g`。

| BC/mask | 总差 | 类内调用权重项 | 类间调用权重项 |
| --- | --- | --- | --- |
| 10/1 | -0.032718858 | -0.001859953 | -0.030858905 |
| 30/1 | -0.029854733 | -0.000668375 | -0.029186357 |
| 60/1 | -0.022196770 | +0.000394003 | -0.022590772 |
| 60/2 | -0.060585424 | -0.004980211 | -0.055605213 |

JSON同时保留协方差项，并对两种恒等式断言误差小于1e−12。BC30的负差主要来自类间项；BC60的类内项为正，抵消部分负的类间项。因此“pooled较低”不能简单理解为每一类中长输出都较差。这里分解的是**本地聚合差**，不是作者论文误差的因果归因。换成prompt等权后的BC30/60仍为1.593232/1.669498，未达目标；原13类等权也未达标。不从已有结果选择最有利权重作为新主指标。

## 四、已有trace的前100 token诊断

此前仅凭逐prompt总计不能恢复前100路径；本轮从保留的完整逐块trace取得已提交token，因此可以补出一个限定的CPU读出。每条保留prefill后的最多99个decode token，EOS提前结束则保留实际结束；把覆盖这些token所需的验证块计入分母，边界块只裁剪提交数，调用仍计一次。prefill不进下面τ的分子/分母，与全路径主口径一致。全部480条保留。

| BC/mask | decode committed/calls | pooled τ | prompt mean | 13类等权mean | pooled−论文目标 | 边界部分保留块 | EOS早于100条数 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10/1 | 40059 / 28566 | 1.402331 | 1.430982 | 1.404749 | — | 100 | 125 |
| 30/1 | 40023 / 25579 | 1.564682 | 1.590913 | 1.564924 | -0.065318 | 135 | 126 |
| 60/1 | 40093 / 24331 | 1.647816 | 1.667665 | 1.650875 | -0.092184 | 148 | 128 |
| 60/2 | 40088 / 24906 | 1.609572 | 1.663995 | 1.619464 | -0.130428 | 127 | 123 |

完整字段在`cells[*].observed_path_prefix100`。这只是历史256/EOS轨迹的前缀计数，**不是**把原生max_new_tokens设为100后重新生成，更不是作者100-token结果。预算边界的构树/前向形状若随停止配置变化，本读出没有对应反事实证据。不能将这些数字替换完整主结果或宣称已消除100/256歧义。

该限定检查下BC30/60 pooled仍低于目标，prompt/category均值也未达目标；不支持“只截取已有轨迹前100就能补齐缺口”的解释。它不能排除作者不同输入、停止实现、任务权重或模型版本产生不同结果。

## 五、结论与下一步

| 项目 | 本轮已收紧的结论 | 仍需的作者证据 |
| --- | --- | --- |
| P1输入 | 四格同一480首轮、token精确、无过滤；固定模板可重渲染 | Table1的qid/多轮选择、tokenizer与checkpoint revision、模板/thinking/截断合同及输入token摘要 |
| P2计数 | 本地全量恒等式、EOS与三个聚合可复算，类内/类间权重项精确闭合 | 作者逐qid的committed/accepted/bonus/calls、prefill/clip及任务权重 |
| 100/256 | 原完整轨迹前100诊断仍未达标，所有480保留 | 作者实际生成上限、EOS/stop配置；原始逐块计数或原生命令 |
| 官方实现 | 本轮不作新的外部状态声明 | 可核验作者repo/commit/许可/原生入口；到位后沿启动清单核协议并申请GPU |

当前可取得的输入/轨迹对账已完成；新增未知项不自动授权新GPU矩阵。作者合同到位后优先CPU比较qid、token摘要及原始分子/分母，再区分输入、停止和权重差异；缺材料时明确未知，不猜成已证实原因。保持固定prompt、数据和三种主聚合；bias/random/Kalman及算子链均后置，不测速、不改配方。独立AR一致率仍仅诊断，正确性门继续为同验证前向正确owner argmax全通过。
