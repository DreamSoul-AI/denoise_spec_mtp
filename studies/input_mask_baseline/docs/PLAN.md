# Study Plan: input_mask_baseline

## 一、问题与证伪条件

宏观依据：[研究提取](../../../docs/research/rpipe-study-extraction.md) 与 v6 §5.11 / E1–E2。真实预训练模型上，现有 frozen_mean / gamma_last 与 AR 能否逐 token 一致，并留下可靠的接受/cache、来源和阶段证据？任何 token mismatch、权重/runtime 漂移或缺证据均否决本轮流程质量。接受数增大不是门，不检验 H1–H13 或新颖性。

## 二、因素与固定条件

四 Experiment 的轴为完整 algorithm.config 补丁：ESP frozen_mean、ESP gamma_last、AR、alignment frozen_mean；基底保留共同 eval 与 version，每 case × seeds=[123] 为四个 Run。make 后核对父 config 的递归合并，避免丢失共同预算。新 version=input-mask-baseline-v031-ms-20261014-v4。

- 数据：本仓库 datasets/spec_bench/question.jsonl，translation skip=10/take=1，q171；第一回合、Qwen 非 thinking 聊天模板、max_prompt_len=2048。独立单位为一 prompt，未用于选参，不重跑历史前 10 条/类的正式格子。
- 模型：Qwen3-0.6B，按用户2026-10-14明确要求从ModelScope显式下载并准备新缓存到 shared/model/modelscope；Run保持local_files_only=true，不在执行期下载或替换snapshot。实际权重/tokenizer/config 哈希由构造/执行与终验锁定；master 不是固定 revision，不能宣称已核对远端版本。
- 原协议：float32、eager、cuda，记录实际 TF32/matmul/随机性条件；T=0、max_new_tokens=100、EOS 停止、seed123、AR 对照与逐 prompt 观测开启。没有统一 FP32 化其他模型；此处沿历史真实 0.6B 原配方。
- mask：named mask 原定义；一 mask、static [14]、pruning、BC30 不变。gamma_last 保留 β=.9/λ=.1/γ=1；frozen_mean 保留均值初始化、不更新。training-free 权重和 mask autograd 边界不变。
- alignment：四个 hindsight 步，冻结均值，计数与各层 cos 分开报告；不是 Figure 2 的 100 条 Dolly 实验。

## 三、来源、阶段与成功条件

执行库固定 v0.3.1 / 7a15c46，唯一 Python 例外为 Windows torch-first；完整 ORIGIN/许可证保留。Study 的两份声明/recipe/阶段 Python 与 PLAN 显式进入 provenance，专项 manifest 补齐 src/spec_mtp；数据、模型/tokenizer、输入、配置和运行条件进入 raw 证据。文件新增/删除/修改与终验漂移必须拒绝。源码/输入变更先换 version，再 make/remake，不能签收旧成功 Run。

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

## 六、2026-10-14 新设备执行准备

v0.3.1 升级及下游 report 质量写回修复改变源码来源，采用新 version / Run ID；原 v1 无真实成功格子，不复用历史正式输入空间格子。Qwen3-0.6B、q171、float32/eager/CUDA、seed123、100-token、EOS、mask 配方与四 case 不变。设备为 RTX 5090 D v2，torch 2.11.0+cu130、CUDA13、Transformers5.12.1。资源清单不等于真实模型串行校准。

检查本项目缓存、用户 ModelScope 默认缓存及常见 Hugging Face 缓存，未找到计划所需 Qwen3-0.6B snapshot。不同规模 Qwen 或图像模型不替代本模型；local_files_only=true 保持。先完成无权重展开与明确离线缺资源核验，不 launch 真实 Run，不补造 token、接受数或峰值。提供原 snapshot 后，先复核来源/模型文件，再串行校准并按当前 PLAN 执行四格；若需要下载新 snapshot，须明确实际来源与原缓存协议的差异，不能悄然替换。

## 七、ModelScope 显式准备（2026-10-14）

用户回复“记得在modelscope下载”，授权准备Qwen3-0.6B。此前v2的缺缓存事实与四个未执行Run保留；采用v3身份，不用新snapshot冒充旧设备缓存。显式snapshot_download在make/Run之前执行，记录provider、实际缓存snapshot、模型/tokenizer/config文件哈希；可变master不伪称固定revision。下载完成后离线解析，同一snapshot用于四格，原q171/FP32/eager/T0/seed123/预算100/EOS与mask配方不改。

先单进程仅加载模型并测资源，再按原生round1串行四格。校准不更换科学精度或额外生成正式格子；记录显存/主存/线程/I/O、实际环境与外部负载，速度不排名。任一correctness/source/evidence门失败保留原Run并停止扩大，不自动放宽门或复跑旧ID。

加载校准已完成（仅加载，不生成正式token）：596049920参数，FP32/eager/cuda:0；CUDA allocator峰值2384724992 bytes，RSS采样峰值5139087360 bytes，torch intra-op线程1。运行前同时冻结snapshot文件哈希与加载校准JSON。load-only的cuDNN benchmark默认为false，没有cuDNN计算；正式Run由原生System按deterministic=false设置benchmark=true，并在raw记录实际标志，不把校准默认值覆盖到科学配置。

第一格frozen_mean用原生run-one作为正式运行同时测解码资源，不额外生成或重复此格。通过后原生launch读取round1计划，跳过第一格成功result并串行运行其余三格；不另建runner。外部0.5秒采样记录进程RSS/线程/I/O及nvidia-smi设备memory.used/利用率，设备采样峰值含背景占用且可能漏掉短峰，不冒称allocator精确峰或性能优势。实际allocator加载峰和解码采样峰分开。

## 八、B-008纠错验收（2026-10-14）

v3四格均Run成功：两ESP exact_match=1，AR真实输出，alignment原始sums/counts完整；Study因嵌套配置轴的期望因素误比较未通过。v3证据和终验失败完整保留，不能标成整轮质量通过。修复仅将期望因素从冻结基底/声明按原生合并与Experiment分组独立推导，不改decoder/Data/Model、轴、输入、精度、预算或数值门。通过CPU嵌套轴/子集回归与完整工程门后以v4重新执行同四case，禁止给v3成功Run重新签来源。资源测量沿已验证加载器；v4继续串行并保存原始观测，与v3逐项对照不包括墙钟。
