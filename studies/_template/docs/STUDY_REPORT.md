# Study Report: my_study

## 摘要

| **项目** | **内容** |
| --- | --- |
| 研究目标 | 链接 [PLAN](<../../../docs/研究计划 Denoising Speculative Decoding.md#legacy-studies--template-docs-plan>)，填写问题与对照 |
| 记录日期 / 实验日期 | 分别填写，历史回顾注明实际执行日期 |
| 主要结果 | 按 Experiment 记录指标、单位、mean/std/min/max/n、阈值 |
| 当前状态 | 执行完成 / 质量通过 / 失败 / 跳过 / 未执行分别说明 |
| 验证边界 | 缺失证据、不可比条件和未完成项 |

本模板尚未执行；不能把占位表、示例配置或历史数字写成新结果。

## 1. 怎么跑的

记录实际 make/launch/process/report 命令、version、index 范围与 pack/wait 排班。写整轮 est/actual、预热、同步和实际任务量；缺失填未记录。CPU/GPU、安装和失败边界分开，不以导入成功或退出码代替阶段与质量验收。

## 2. Experiment 结果与结论

数字来自本轮 process/NUMBERS，回溯 Run 的原始观测与 CSV。accepted 是所有深度接受的 draft 数（原预算/EOS 截断前口径），accept_d1 等单列；new_tokens、committed、decode_calls、τ 和速度分别解释。exact_match_rate 必须为 1。单 seed 的 std=0 不能证明稳定性，τ 或吞吐不替代研究结论，γ 不叫 slope。

| **factors** | **n** | **指标 / 单位** | **mean** | **std** | **min** | **max** | **判定** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 待执行 | — | — | — | — | — | — | 未执行 |

## 3. 结果图

执行后把真实接受数或解码轨迹图放 `docs/figures/`，添加可点击的相对链接与图注；图注写来源/version、设备、数据、seed、精度/backend、指标口径和范围。training-free 解码没有训练 learning curve，不造曲线；未产生图片前不添加失效的图片链接。

## 4. Run 明细与失败证据

| **factors** | **seed** | **Run ID** | **status / exact-match** | **accepted / 深度诊断** | **est / actual (s)** | **证据** |
| --- | --- | --- | --- | --- | --- | --- |
| 待执行 | — | — | 未执行 | — | 未记录 | 未产生 |

原始日志在相对本报告的 `../runs/<id>/assets/logs/run.log`。runs 不入库，本机路径标记为文本；正式链接指向已入库的精选证据。保留 OOM、source drift、token mismatch、缺证据、不完整子集、失败与重复反例，不只列成功 Run。

## 5. 复现条件与终验

记录提交与 RPipe ORIGIN、来源锁/digest、模型/tokenizer、数据/prompt/配置、依赖与设备、实际 dtype/TF32/backend、随机性、seed、预算和停止规则。process 只聚合本轮 index，说明所有组合完整、来源一致和质量门的结论。

普通 run/launch 不刷新锁；源码/输入/配方改变采用新 version 和显式 make/remake，不重新签收旧成功产物。说明哪些原始产物仅本机保存；不把上游训练恢复写成已验证的解码 KV/mask/RNG 恢复。列出 GPU、并行、恢复、安装、长矩阵的未验证范围与运行前置条件。
