# Study Plan: input_mask_baseline

## 一、问题与证伪条件

宏观依据：[研究提取](../../../docs/research/rpipe-study-extraction.md) 与 v6 §5.11 / E1–E2。真实预训练模型上，现有 frozen_mean / gamma_last 与 AR 能否逐 token 一致，并留下可靠的接受/cache、来源和阶段证据？任何 token mismatch、权重/runtime 漂移或缺证据均否决本轮流程质量。接受数增大不是门，不检验 H1–H13 或新颖性。

## 二、因素与固定条件

四 Experiment 的轴为完整 algorithm.config 补丁：ESP frozen_mean、ESP gamma_last、AR、alignment frozen_mean；基底保留共同 eval 与 version，每 case × seeds=[123] 为四个 Run。make 后核对父 config 的递归合并，避免丢失共同预算。新 version=input-mask-baseline-20261014-v1。

- 数据：本仓库 datasets/spec_bench/question.jsonl，translation skip=10/take=1，q171；第一回合、Qwen 非 thinking 聊天模板、max_prompt_len=2048。独立单位为一 prompt，未用于选参，不重跑历史前 10 条/类的正式格子。
- 模型：Qwen3-0.6B，使用既有 ModelScope 缓存；cache 首次准备到 shared/model/modelscope。local_files_only=true，不下载或替换 snapshot。实际权重/tokenizer/config 哈希由构造/执行与终验锁定；master 不是固定 revision，不能宣称已核对远端版本。
- 原协议：float32、eager、cuda，记录实际 TF32/matmul/随机性条件；T=0、max_new_tokens=100、EOS 停止、seed123、AR 对照与逐 prompt 观测开启。没有统一 FP32 化其他模型；此处沿历史真实 0.6B 原配方。
- mask：named mask 原定义；一 mask、static [14]、pruning、BC30 不变。gamma_last 保留 β=.9/λ=.1/γ=1；frozen_mean 保留均值初始化、不更新。training-free 权重和 mask autograd 边界不变。
- alignment：四个 hindsight 步，冻结均值，计数与各层 cos 分开报告；不是 Figure 2 的 100 条 Dolly 实验。

## 三、来源、阶段与成功条件

执行库固定 804b3823，唯一 Python 例外为 Windows torch-first；完整 ORIGIN/许可证保留。Study 的两份声明/recipe/阶段 Python 与 PLAN 显式进入 provenance，专项 manifest 补齐 src/spec_mtp；数据、模型/tokenizer、输入、配置和运行条件进入 raw 证据。文件新增/删除/修改与终验漂移必须拒绝。源码/输入变更先换 version，再 make/remake，不能签收旧成功 Run。

默认 prepare 构造输入与模型，execute 调用原 Algorithm；collect 写 CSV/Tracker，summarize/write 拒绝失配后才由库定稿，process 的 Study scope 只终验当前四个 case×seed。所有 Run succeeded、ESP exact_match_rate=1、来源一致且 complete/专项质量同时通过，才称前置门通过。AR 需真实 output/summary，alignment 需真实 sums/counts；二者不伪造投机 exact-match 指标。

主门为正确性/证据，accepted 是所有深度的原截断前 draft 数；深度接受、new_tokens、committed、decode_calls、τ 分别列出。速度只记录条件，不排名。n=1 不支持统计稳定性或机制优越性。

## 四、运行、资源和停止规则

先通过源码导入、离线 Toy/Stub 模板门、隔离 tiny/失败回归、36 格原轨迹对照，再执行这四个真实 Run。GPU 串行 --round 1，每 Run 独占状态与产物；记录本机显存/主存/线程/I/O 条件与峰值，未校准不扩大并发。性能期间不跑竞争任务，不拿训练预算装箱默认值作依据。

已有缓存可用时，将本机 .cache/modelscope/models/Qwen--Qwen3-0.6B 复制到本 Study shared/model/modelscope/models 下，保留 snapshots/master 与原文件；不提交权重。然后：

```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONPATH = 'src'
$env:OMP_NUM_THREADS = '1'
python -m spec_mtp make studies/input_mask_baseline --num-gpus 1 --init-gpu 0 --round 1
python -m spec_mtp launch studies/input_mask_baseline --num-gpus 1 --init-gpu 0 --console shared
python -m spec_mtp process studies/input_mask_baseline
python -m spec_mtp status studies/input_mask_baseline
python -m spec_mtp logs studies/input_mask_baseline
python -m spec_mtp report studies/input_mask_baseline
```

保留 make 的 est 与实际 wall，不把估计当实测。任何 OOM、数值/来源门失败停止扩大并保留证据；缺资源先报告具体条件。允许的规模仅四 case、单 prompt、seed123、原100-token预算。无并发、无调参、无新增输出空间实现、无完整矩阵或解码恢复验收。

## 五、报告与边界

结果、原始输出与图保留在本 Study，报告区分执行完成、流程质量与研究假设支持；n=1 前置门不证明接受率提升、跨域泛化或论文复现。raw runs/shared/.tmp 仅本机，正式精选 JSON/图/报告随 Git。旧失败和历史数字不改写。
