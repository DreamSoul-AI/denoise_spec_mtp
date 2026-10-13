# 异机交接

## 2026-10-14 本机收尾状态

本次按用户要求先提交推送检查点，然后在另一设备接续。研究验收未完成，不能将本记录当作整体通过。接手先检查实际工作区、HEAD、远端和本机环境，保留已有修改，不切回默认分支旧设计。

| **项目** | **状态** |
| --- | --- |
| 仓库与工作分支 | DreamSoul-AI/denoising-speculative-decoding；refactor/spec-rpipe；本轮基于 dev 集成 1b6d59c，不改 branch spelling |
| 当前执行基线 | src/rpipe/ORIGIN 第一行 804b3823ab6d2af46cbda1a65688ca8b76c60b22，v0.3.0；101 个上游文件只有 Windows torch-first 例外，保留 MIT |
| 新上游固定参考 | v0.3.1 commit 7a15c46b75c5eb951cccd60ed7b9fc3463db90f5；annotated tag cd7a750de0d13889916eba84b53ed4a339d47a32；未更新 vendor |
| 已完成职责重构 | [rpipe-migration.md](rpipe-migration.md)；flow 阶段、API 桥、artifact 核验、数据 init 拆分与兼容 facade；没有第二套 runner |
| 新研究 Study | [input_mask_baseline PLAN](../studies/input_mask_baseline/docs/PLAN.md)：Qwen3-0.6B，q171 translation 新 prompt，frozen_mean / gamma_last / AR / alignment，seed123；未执行 |
| 工程证据 | [smoke 报告](../studies/smoke/docs/STUDY_REPORT.md#八职责重构检查点2026-10-14)、[本轮 JSON](../studies/smoke/docs/refactor_validation.json)：239 回归、Ruff、55 文件 mypy、36 格完整轨迹对照、4 Run 原生离线模板六阶段通过 |
| 分支政策 | main 为 default，工作 PR → dev → 同仓库 dev PR → main；保留 CI，不直接推长期分支，不自动合并/发布 |

## 接手顺序

1. clone/fetch 实际工作分支。先读 AGENTS、README、layout、architecture、testing、windows、rpipe-migration、bugs、record、studies 入口及目标计划/报告、history-extrapolation、brainstorm、research/readme 与 extraction。研究草案不自动成为实施合同；不要重复前次已完成的框架迁移和正式实验格子。
2. 核对固定 v0.3.1 的 README、发布报告、concept/layout/code/structure/flow、研究/反馈、Study 和测试规范以及实际源码。相对 804b3823，src 只有 __init__.py 版本号及 structure/artifact/readout/report.py 变化；后者先核当前 index 的 Study/Run/seed/factors 身份，再原子写 NUMBERS。它不是新的调度器/解码实现，也不自动修复 C-004。完整文档差异仍须按实际调用审阅。
3. 先同步升级设计和兼容记录，再更新完整 vendored 副本与 ORIGIN 到固定新提交，保留 Windows torch-first 例外和许可证，记录全部本地差异。上游 report 身份/保全门与本项目 Study exact-match/source/evidence/completeness 门必须共存；接口变化不得覆盖科学实现。复验当前 index 与旧 process、损坏/缺失 index、部分合法聚合、原子写失败和专项拒绝边界。
4. 新设备先记录 Python/torch/transformers/ModelScope、CUDA、实际 dtype、TF32、backend、硬件与资源。已有 GPU 环境只做 no-deps 项目安装并按需补缺，不覆盖 CUDA torch，不加 sitecustomize/全局补丁。ModelScope 权重缓存不会随 clone 提供；新 Study local_files_only=true，先按项目规则显式准备缓存，否则如实停在缺资源，不偷偷下载/改变配方。
5. 完成安装与新基线 smoke/失败回归，使用独立 pytest --basetemp。安装包须在源码目录外检查 wheel/sdist 的真实导入、ORIGIN/LICENSE、两个 console 入口和实际 make→launch→process/readout。历史 934dac3 安装通过只作旧证据；本轮尚未做 current-refactor 分发包全链和 windows_selfcheck。
6. 先保留固定 tiny 原始输出，再比较新链：`python studies/smoke/validate_migration.py --out .tmp/<new-id>/tiny.json --compare studies/smoke/docs/tiny_decode_reference.json`。36 格的 token、AR token、接受和 KV 轨迹是严格门。源码新增/删除/修改、输入/模型/tokenizer/运行环境漂移、exact-match 失败定稿、证据缺失、index 子集与 Study scope 也要覆盖，不能只查退出码。
7. 为 input_mask_baseline 设新的 algorithm.config.version（新设备/新基线/日期），PLAN 若调整先明确原因；冻结后不随意改 PLAN 或重签旧成功 Run。原配方 float32/eager/[14]/1mask/BC30/T0/100budget/seed123/thinking off，β/λ/γ/数据与 EOS 不选优调整；只验证已计划四格。先串行测量显存/主存/线程/I/O，四格独占状态/产物，不做竞争资源速度排名；原生 make/launch 参数以实际 CLI 为准。不得跑完整大模型矩阵、扩大并发或声称 KV/mask/RNG resume 已支持。
8. 将执行、原始 token/接受/cache、来源、失败与终验写入对应 Study。accepted 各深度、生成 token、τ 与速度口径分开，exact_match=1 是硬门。AR/alignment 不伪造 ESP 指标，四步 hindsight 不称 Figure 2 完整复现，未实现的输出空间/Kalman/PLD/STAND/LADE 不补写成支持。
9. 上游通用问题按固定 feedback.md：先本地记录、最小合成复现、检索 open/closed Issues 和 PR、脱敏，再可直接创建/补充 DreamSoul-AI/RPipe Issue（已有明确授权），回写真实 URL。C-004 须确认 v0.3.1/当前 main 是否仍有行为；未复现写疑似。此授权不含上游代码/PR/合并/权限修改。最后完成本项目文档、检查、分阶段 commit/push，PR 面向 dev；不自行合并新 PR 或发布。

## 证据和资源迁移边界

正式报告/参考 JSON/模板 YAML 在 Git 中；runs/shared/.tmp、原始日志、权重、缓存、凭据不在 Git，也不随 push/clone 提供。本机历史原始证据已随 checkout 补齐到新目录，其内部原执行路径未改写。异机需要新 version/Run，不可把新的 make 锁签在旧成功目录上。若要复制原始制品，先核对脱敏、来源与大小，复制不等于当前验收。

本机 checkout 已迁至 denoising-speculative-decoding，editable 指向新路径。Windows 返回错误导致部分移动后已逐文件补齐并核对 Git；原目录仅临时目录残留，没有继续强删。目标设备直接按新名称 clone 即可，不继承本机绝对路径。上游本机工作区的其他任务改动始终未触碰。

本机初轮 239 回归和 36 格对照在目录移动之前运行，执行树指纹见工程 JSON；目录移动及交接文档整理后再次全量 239 passed / 0 skipped，Ruff、55 文件 mypy、editable 导入、模块/console CLI 和 Git 连通性检查通过。GPU CUDA tiny、555 格和 wheel/sdist 的已有数字见各自历史提交/日期，不冒充本轮或新设备验收。

## 当前未完成

v0.3.1 源码升级与完整回归；当前重构安装包/Windows selfcheck；新真实模型四格 Study 与串行资源校准；上游 C-004 新最小复现和实际 Issue。真实权重 GPU 容量、并发、解码恢复、长矩阵与新设备科学验收均未完成。用户要求本机先收尾交接，因此本轮不启动新的正式解码任务。
