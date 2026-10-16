# ESP Table1 BF16 全480与验证argmax自检

[PLAN](<../../docs/研究计划 Denoising Speculative Decoding.md#legacy-studies-esp-table1-bf16-full-argmax-docs-plan>)冻结原设置与自检合同。[报告](docs/STUDY_REPORT.md)按pooled、prompt mean、category mean列τ；独立AR一致率和首分叉不作为τ执行门，每个提交token的验证前向argmax自检必须全过。BC60单mask为主，双mask对照。不测速、不改数值算子。

`python -m spec_mtp make studies/esp_table1_bf16_full_argmax --round 1`

`python tools/launch_once.py launch studies/esp_table1_bf16_full_argmax --round 1 --console shared`

`python studies/esp_table1_bf16_full_argmax/analyze_results.py`

四格均完成全480条，verifier argmax全过，原生summarize/process成功。BC10/1、BC30/1、BC60/1、BC60/2的pooled τ分别为1.399047、1.563378、1.647301、1.603729；BC30与BC60未达到论文目标1.63/1.74。AR一致率与逐条首分叉仅作诊断，三种τ聚合、目标差值及正式证据见[报告](docs/STUDY_REPORT.md)。

[原生数字表](docs/NUMBERS.md)从已验收process只读生成，绑定process与原生formatter SHA；保留Experiment/Run数字，去掉仅本机存在的日志超链接。每格一个Run，std=0不代表稳定性；未新增模型执行或测速。

上列命令为本轮原执行入口；已有Run不重跑或重新冻结。后续复现实验使用新Study版本，保留本轮原始来源锁。原始Run、逐prompt argmax JSONL、完整tokens、权重与缓存只保留本机。

首次v2四Run均在模型加载前报ModelScope CacheNotFound，未执行解码；失败Run保留。补接shared/model/modelscope/Qwen/Qwen3-8B到此前同一已校验本地snapshot后，以v3新Run执行，不覆盖/重签v2。只修本地缓存接入，配置设置及源代码不变。

按用户最终指示，四格旧AR门失败结果均只重做summarize gate与write，execute_rerun=false；旧失败result按SHA保留，raw、输入、argmax JSONL和执行来源锁字节不变，新validator SHA另列。原队列退出后用同一门运行原生process，来源、配置与seed检查全过，旧process也已归档。[重新验收记录](docs/native-process-revalidation-v1.json)不替代原始执行来源。串行入口显式retry_failed=False，未因AR失配重跑任何已完成格；此后进入4B BF16配对，不恢复算子机理或测速。
