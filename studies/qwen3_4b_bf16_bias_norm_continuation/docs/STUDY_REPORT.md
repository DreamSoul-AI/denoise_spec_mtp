# 范数七格续跑与首格恢复

> 首格template/0.5已480/480，argmax80,940/80,940；pooled τ1.4713896458。
> 首格因阶段包未导出run而collect失败，使用原生collector/既有revalidate工具恢复；execute未重跑，原始SHA未变。
> 新Study仅七个剩余配置，原冻结Study七个未运行Run保留pending，配置、数据、prompt与科学代码不变。
> BC60正在运行，单队列在其自然退出后续跑；CPU入口/配置/显示分类检查通过，完整套件两项文档门已修复，89项定向检查通过。

首格Run `studies/qwen3_4b_bf16_bias_norm_scan/runs/6ee3f749ee20c450`：accepted25,882、committed80,460、decode_calls54,683、model_calls55,163、new_tokens80,940。pooled τ=1.4713896457765667，prompt等权1.5175764421300806，类别pooled后等权1.4791494036280022；AR exact177/480仅诊断。

对零偏置，当前格accepted胜/平/负322/43/115、calls311/46/123、τ328/40/112；对原template1×，分别134/52/294、138/55/287、136/51/293。均为480固定prompt配对，输出长度/轨迹可不同，不是等长速度或同前缀因果结论。0.5×处于已知0与1×之间，随机方向与2×未完成，不能据此声称完整范数曲线或主因。

公开聚合与恢复证据见[first_cell_recovery_v1.json](first_cell_recovery_v1.json)，仅计数/哈希、不含原始prompt/token/logits。数字严格派生自 `.tmp/norm-collect-recovery-20261016/readout/norm_pending.json` 的cells/template/0.5和paired_comparisons；恢复来源与raw六文件SHA见 `.tmp/norm-collect-recovery-20261016/recovery_evidence.json`。新版逐格入账在 `.tmp/norm-continuation-ledger-20261016/ledger.json`，第一条已核验成功，后续由原生Run验收，不签旧pending。

原生collector与冻结flow/collect/run.py指向同一个函数；仅旧包__init__漏导出导致调度失败。既有tools/revalidate_run.py将旧failed result按SHA归档到该Run assets/gate_revalidation，严格保留来源/输入/数学门。旧Study源不改，不make/remake；新Study正确导出四阶段，复用原NormEval及19:53显示分类。唯一计划与不可变commit见docs/source_refs.json。未测速、未新造方法、未改prompt；最终以七格process通过加首格恢复审计为完整矩阵门，不宣称旧Study全完成。
