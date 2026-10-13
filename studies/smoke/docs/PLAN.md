# Study Plan: smoke

## 1. 目标与范围

固定 RPipe v0.3.0 (`804b3823ab6d2af46cbda1a65688ca8b76c60b22`)，验证随机 tiny 的 losslessness 和实际六阶段证据门，保持 ESP/EMA/AR/alignment 的 training-free 语义。历史验收见 [STUDY_REPORT](STUDY_REPORT.md)，下面的复跑合同不把旧成功签收为新结果，不启动真实模型矩阵。

## 2. Study / Experiment / Run

`experiment_config.yaml` 是基底，`fixed` 覆盖同名条件，唯一轴为 `algorithm.config.variant = [esp_static, esp_dynamic, ema_velocity]`。三个 Experiment × seeds=[123] 为三个 Run。无独立 Experiment 文件夹，当前 index 是唯一终验集合。

声明中的 `rpipe-v030-20261013-delivery` 是历史交付版本。新实测复制到隔离 `.tmp/` 目录，改 Study 名与 `fixed.algorithm.config.version`，核对实际 config/index 后 make/launch；不得追加写入旧 Run。

## 3. 固定条件与数值门

| **项** | **原配方 / 验收条件** |
| --- | --- |
| 模型 | 随机 tiny LLaMA，vocab=256、hidden=64、intermediate=128、layers=2、heads=4、KV heads=2、position limit=1024 |
| 输入 | synthetic，四个长度 32 的 prompt，data seed=0；模型/Run seed=123 |
| 计算 | CPU，eager，随机 tiny 的实际 dtype float32；记录 TF32、matmul 精度与依赖，不自行更改 |
| 解码 | 三个既有 variant 的 mask/树/EMA 配方保持，32 新 token、T=0、stop_on_eos=false、AR 与逐 prompt 证据开启 |
| 质量 | 每个 Run exact_match_rate=1；完整 token、接受/回退、KV cache 和输入/权重/runtime 来源可复验 |
| 数字 | 旧 tiny accept_d1=27/31/8；对应 all-depth accepted=28/31/8；深度统计和总接受口径分开 |

上述固定计数仅适用于记录的模型/input/依赖/设备条件。同设备旧新数值比较保留原始 token/完整轨迹；改变环境后重新建立参考，不能用调温度、FP32 化真实模型或挑选重复来消除反例。τ 与速度不是质量门，smoke 不做性能排名。

## 4. 阶段、来源和失败边界

prepare 通过 recipe 和 builder 检查来源/输入并构造；execute 保存真实观测；collect 计算指标；summarize 拒绝 exact-match 和证据失败；write 复验后由 RPipe 定稿；process 的 Run scope 用默认职责，Study scope 只验当前 index 的因素/seed、来源和质量。

覆盖 source 新增/删除/修改、输入/配置漂移、raw 缺失、真实 token mismatch、不完整子集/seed、混合来源和 Study scope。安装验证分别说明 wheel/sdist/console scripts/实际 CLI 链，不能只报 import 或退出码。专项包锁与 RPipe provenance 配合，细则见 [指南](../../README.md#4-来源冻结与复跑)。

## 5. 排班与命令

三个 CPU Run 串行，make 使用 `--round 1`，使用现有科学依赖和 `OMP_NUM_THREADS=1` 的小规模验证条件；不叠加资源竞争的测试或计时任务。新目录确认后使用 `python -m spec_mtp make <copy> --round 1`、`launch <copy>`，再 process/status/logs/report。运行前记录新 version、Run ID 和输入；失败及旧产物保留。

| **排班** | **任务** | **est / actual** |
| --- | --- | --- |
| 串行，三个独立 Run | 每个 variant × seed=123 | 新复跑在 make 后填 est，执行后填 actual；历史证据未保留统一墙钟，不补造 |

CUDA 仅另行授权的随机 tiny 串行门；实际 dtype、TF32、attention 与输入必须按原配方记录。没有真实模型容量测量前不增加 GPU 并发；不会将训练 `resume: latest` 当作解码恢复。

## 6. 成功与报告

所有声明组合的 Run succeeded、exact-match=1、证据/来源一致且 Study `complete` 与质量门通过，才能报告完整通过。报告按三个 Experiment 给指标与 n=1 的统计边界，附真实历史结果图和独立 Run/失败引用，保留静态/CPU/GPU/安装的区分。正式参考 JSON、图与报告随 Git；原始 runs/shared/.tmp 日志只在本机。

## 7. 历史迁移计划（2026-10-13 原记录）

以下保存当时的迁移执行计划；其中初始 version 后续使用 final03/delivery 等新版本复验，实际提交、Run、失败和数字以报告/JSON 为准。


目标：固定 RPipe 804b3823，保留 ESP/EMA/AR/alignment 的 training-free 语义，验证实际六阶段、来源冻结与拒绝成功边界。非大模型研究矩阵，不重跑历史正式接受数。

1. 同一设备和依赖上保存 c3263c0 工作区改动前的 555 格 fingerprint，再与当前来源对照；固定 tiny LLaMA、prompt、temperature 和 seed 不变。
2. 导出旧链 b1f6191 的 src，使用 [validate_migration.py](../validate_migration.py) 比较三种 smoke variant × T={0,0.7,1} × 四个固定 prompt。被动 Python line trace 读取接受路径/cache，不改旧源码；比较完整 token、接受/回退与 cache 轨迹。T=0 历史 tiny accept_d1 为 27/31/8。
3. 新 version rpipe-v030-20261013 走 make→launch→process/status/logs/report；AR/alignment 与失败边界由真实 CLI 回归验证。CPU 串行，不做吞吐排名。
4. wheel/sdist 各在源码目录外安装至隔离 .tmp，复用已有科学依赖，核对 import、console script、ORIGIN/LICENSE 和实际 tiny 阶段链。
5. Windows 双导入入口验证；CUDA 只允许随机 tiny 三 variant 串行门，不下载真实模型，不扩大并发，不宣称大模型/恢复已验收。

所有新实测采用新 Run ID/目录；失败日志留 .tmp（不会随 clone 提供）。正式结果和条件记 [STUDY_REPORT.md](STUDY_REPORT.md)。执行有不一致时保留反例，不放宽阈值。
