# study_report — smoke

## 一、摘要

- 目标：接通固定 RPipe v0.3.0 的真实阶段职责，保留 ESP/EMA/AR/alignment 研究语义，拒绝无证据的成功。
- 实现提交：`7c89d7cb1abbf5560a842b4ff52e571b59984437`，工作分支 `refactor/spec-rpipe`；上游固定 `804b3823ab6d2af46cbda1a65688ca8b76c60b22`。接入主体在本次开始前的 c3263c0 已存在，本次只补齐缺口。
- 结果：227 passed；固定版本 Ruff/mypy 通过；旧/新 36 格 token/接受/cache 完全相同，555 格改动前/后 fingerprint 完全相同。CPU/CUDA tiny 三 variant 均 exact-match=1，wheel/sdist 各通过实际安装与阶段链。
- 边界：真实预训练模型、ModelScope 下载、严格解码恢复、GPU 并发容量、完整大模型矩阵未验收；没有重跑历史正式接受数。

详细机器数字与来源见 [migration_validation.json](migration_validation.json)，固定原始 token/接受/cache 参考见 [tiny_decode_reference.json](tiny_decode_reference.json)。它们是正式 tiny 验收证据，不是历史论文实验的新结果。

## 二、实现与兼容边界

RPipe 提供 Factory/Registry、配置展开、调度、六阶段、Tracker、日志、result/provenance 和 readout。专项 prepare 经 recipe 注册和构造检查；execute 保存真实观测；collect 计算 CSV/Tracker；summarize 执行成功门；write 再核对来源、配置、输入、权重和运行条件，库才定稿；process 只读当前 index 并复验证据、声明 factors/seeds 和来源一致性。

vendored 的 101 个上游文件仅 Windows torch-first `__init__.py` 有差异；ORIGIN 和 MIT 许可证额外保留。Ruff 的四文件 F401 例外只解决公开转导出与下游 lint 的冲突，不修改上游源码。make 的 torchvision-only endpoint 边界通过已有 prepare_shared:false 适配；Run prepare 继续 shared/data 与 shared/model。[问题与兼容记录](../../../docs/bugs.md) 区分上游边界和下游缺陷。

保留 decoder 的 mask/autograd/树/cache/位置/attention/接受/EOS/预算逻辑，trace 只读取已算出的状态；legacy evaluate/test 调用仍可用。历史 history_extrapolation 的报告与切片在 c3263c0 前已迁入 docs/history-extrapolation.md 和 datasets/spec_bench，核对 Git rename 和章节后未重复搬迁。hw_probe 是 2026-10-07 的旧容量探针，不拿它授权当前并发。现有可执行 Study 是 smoke 与模板；AR/alignment 由同一 recipe 支持并通过实际 CLI 测试。PLD/STAND/LADE 与输出空间研究草案未补写为已实现。

## 三、数值与环境

### （一）旧链与当前链

旧链：Git archive 导出 b1f6191 的 src；当前链：本次适配。用 [validate_migration.py](../validate_migration.py) 在同设备、同依赖上运行三 variant × T={0,0.7,1} × 四 prompt，Python line trace 被动读取接受路径与 KV cache，不改旧源码。36 格全部 token-for-token 等于 AR，完整 token、计数和每步轨迹完全相同，digest `12a8ce5363f1118a2dc651805c24b95682e759e5204349c90455a4dcef903493`。

另用现有 decode_fingerprint 覆盖全部 paper/smoke preset、短上下文与温度的 555 格，改动前工作区和当前链相同：`84d3a1b6fe65811c8094ca545db97d5aa80cb218923197413c56470d66c03ceb`。context-limit 格比较的是工具原有 full-AR 标志；工具记录的 shorter-prefix 不被删掉或改写成 full-AR 相等。实际 Flow 的 context-limit 回归仍按方案 A 对齐已达到的预算。

### （二）提交后的真实 Run

Python 3.13.9，torch 2.11.0+cu130，transformers 5.12.1，NumPy 2.3.5；Windows。CUDA tiny：NVIDIA GeForce RTX 5090 D v2，CUDA 13.0。随机 LLaMA vocab=256/hidden=64/layers=2、四个 synthetic prompt 长 32、seed=123、max_new_tokens=32、T=0、stop_on_eos=false、eager；实际 dtype float32（随机 tiny 原配方），matmul TF32=False、cuDNN TF32=True。没有改真实模型的 bf16/fp32 配方，也没有为了通过改变温度或阈值。

| **设备 / variant** | **Run ID** | **accept_d1** | **accepted** | **new_tokens** | **committed** | **decode_calls** | **τ** | **exact_match** |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| CPU / esp_static | 30528cdb12db5445 | 27 | 28 | 128 | 124 | 97 | 1.278351 | 1 |
| CPU / esp_dynamic | b1aa481f093871ea | 31 | 31 | 128 | 124 | 94 | 1.319149 | 1 |
| CPU / ema_velocity | eac77a3957d6ca55 | 8 | 8 | 128 | 124 | 116 | 1.068966 | 1 |
| CUDA tiny / esp_static | 3bf7ac9df250954f | 27 | 28 | 128 | 124 | 97 | 1.278351 | 1 |
| CUDA tiny / esp_dynamic | b5da1caba330b3e7 | 31 | 31 | 128 | 124 | 94 | 1.319149 | 1 |
| CUDA tiny / ema_velocity | 5bc84e19861a7b71 | 8 | 8 | 128 | 124 | 116 | 1.068966 | 1 |

accept_d1 是深度 1 的接受；accepted 是所有深度的接受（沿用原实现的预算/EOS 截断前统计）。new_tokens 包含 prefill 的第一个新 token，committed 是 decode pass 提交的 token，τ=sum(committed)/sum(decode_calls)，prefill 不进分母。速度与 τ 不替代正确性或研究结论，未做性能排名。旧 tiny 的 27/31/8 是 accept_d1 回归口径，不等同所有深度 accepted。

提交后版本为 commit-7c89d7c-cpu/cuda，源码包 dirty=false，完整 source/模型/input digest 见 JSON。仓库 smoke 另用 rpipe-v030-20261013-final03 运行 make --round 1→launch→process/readout，三 Run 通过，生成 [NUMBERS.md](NUMBERS.md)。首轮 default make 曾派发三个独立 CPU Run；数值对照 probe 与最终 smoke/提交后 tiny 均串行，没有比较竞争资源时的速度。

## 四、失败、静态门与安装

1. 首轮仓库 smoke 的旧锁拒绝新的源码（1 failed/8 passed），旧 Run 3b0724f5e0396351 被库回写 failed；执行前未备份 result，原终态无法确认/恢复。raw/log 未删；后续改隔离目录与新 version，并在薄 CLI 前置来源核对，回归证明拒绝不再改写旧 result。
2. CUDA final02 的原始 exact-match=1，但 `cuda`/`cuda:0` 名称比较产生下游配置漂移误报，Run failed；修复只改有效配置核对，加入别名回归，final03 与提交后新 Run 通过。失败 Run ID 与索引留在正式 JSON，raw/log 保留本机 `.tmp/acceptance-20261013/`。
3. 最终 pytest：227 passed、0 skipped。包含真实 raw token mismatch 在 summarize 拒绝成功、来源新增/删除/修改、配置/输入漂移、证据缺失、子集/seed/混合来源、AR/alignment 实际阶段链。Ruff 0.17.0 passed；mypy 2.4.0 对全部 40 源文件通过。早期本机工具依赖缺失/版本不匹配日志保留，最终工具装在 .tmp，没有覆盖 CUDA torch。
4. wheel/sdist 在源码目录外分别安装到独立 target，每种六条命令验证实际导入路径、ORIGIN/LICENSE、两个 console script 与 make→launch→process，三 variant 27/31/8，exact-match=1。复用本机科学依赖，不能当成全新机器依赖安装验收；包哈希和安装 Run 见 JSON。Windows 两种 import 入口 selfcheck 通过。
5. ci_local.py 的 POSIX bash/venv-bin 重放不适用于本次 Windows 原生环境，未运行；保留原有 Actions 启用状态与 workflow，远端 CI 另以 PR 检查结果为准。

## 五、复跑与未执行项

先读 [plan.md](plan.md)。普通 run/launch 不刷新现有专项锁；源码/输入变更先设置新的 algorithm.config.version，再 make/remake。make 已有对应 Run result 时不能用新源码重新签收。终验同时比较 Study/RPipe/专项来源、实际 config 和输入文件；make 尚未下载的远端资源只能在构造后记录实际权重/tokenizer，真实 Hub 环境另行验收。

旧/新 probe 可由 Git archive b1f6191 src 后设 PYTHONPATH 指向归档 src，调用 validate_migration.py --out；切回当前 src，再加 --compare。完整 token/trace 参考已经入库；完整 555 格原始文件、实际 Run/assets/logs 和安装目录在 `.tmp/acceptance-20261013/`，不会随 clone 提供。Study 的正式报告与参考 JSON 可独立取得，完整 Run 需要按新 version 重跑。

GPU 仅完成随机 tiny 串行门。没有校准真实权重的 KV/树/mask/进程预算，没有扩大 GPU 并发、执行完整大模型矩阵或新增 baseline。解码状态/采样 RNG/KV/mask 的 checkpoint/resume 不宣称已实现或验收。保持论文解释差异与历史接受数原记录。
