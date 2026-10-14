# ESP Table1 BF16 全480与验证argmax自检

[PLAN](docs/PLAN.md)冻结原设置与自检合同。[报告](docs/STUDY_REPORT.md)按pooled、prompt mean、category mean列τ；独立AR一致率和首分叉不作为τ执行门，每个提交token的验证前向argmax自检必须全过。BC60单mask为主，双mask对照。不测速、不改数值算子。

`python -m spec_mtp make studies/esp_table1_bf16_full_argmax --round 1`

`python tools/launch_once.py launch studies/esp_table1_bf16_full_argmax --round 1 --console shared`

`python studies/esp_table1_bf16_full_argmax/analyze_results.py`

原始Run、逐prompt argmax JSONL与完整tokens只保留本机。原生AR严格门状态如实保留，正式τ验收另列。

首次v2四Run均在模型加载前报ModelScope CacheNotFound，未执行解码；失败Run保留。补接shared/model/modelscope/Qwen/Qwen3-8B到此前同一已校验本地snapshot后，以v3新Run执行，不覆盖/重签v2。只修本地缓存接入，配置设置及源代码不变。
