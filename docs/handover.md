# 异机交接

## 输出空间最小阶段（2026-10-14）

用户要求自主继续，采用feature/output-space-prerequisite（父1219a1d/PR6；PR6当前CI全部成功但未合并）。输出零/一阶normalized final-hidden masks只支持实际tied模型与unpruned静态链，复用验证/KV/RPipe六阶段。先写[PLAN](../studies/output_space_prerequisite/docs/PLAN.md)再实现；270全量、Ruff、56文件mypy与旧36格严格轨迹通过。四个新真实Qwen3-0.6B/q171/FP32/seed123/100token Run已成功，来源/原始证据/Study完整性门通过。输入均值链accepted17，输出order0/order1均10，三者均与独立AR的47token完全一致。保留负结果，不调参、不扩大矩阵。报告、数字和图见[新Study](../studies/output_space_prerequisite/README.md)。源码digest670c744e0535dcad，旧input baseline历史证据未改、未重签。wheel/sdist 41条CLI命令及两独立安装target的output-hidden解码通过；正式材料已保留，最终提交按本地分支核验。本轮无新公开推送、合并或发布。

## ModelScope四格正式接续（2026-10-14）

用户已明确批准本轮代码、脱敏研究报告与验收证据公开推送及dev PR，权重/缓存/完整Run与内部资料仍排除。refactor/spec-rpipe已推送，实际 [PR #6](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/6) 已创建，base=dev、head=refactor/spec-rpipe、状态OPEN且可合并，无合并或发布。ae86c3c的Branch flow与push/PR cpu-checks已启动；本段文档提交后以PR最新head的实际checks为准，不把旧提交CI当成最终结果。下方拒绝/待授权文字为推送前历史检查点。

用户明确要求ModelScope下载并继续工作后，已显式准备新Qwen3-0.6B snapshot，保留CUDA torch，Run保持离线。加载与解码资源按单GPU/round1串行核验。v3四Run成功但Study因B-008嵌套轴期望误比较失败；修复从冻结基底/声明复用原生合并分组，不放宽门，v3 raw/失败完整保留。v4新身份四格全部成功，Study/source/evidence/有效因素/完整性质量门通过。科学decoder/Data/Model、q171/FP32/eager/T0/seed123/预算100/EOS/原mask配方未改。

两ESP各accepted19、生成47，独立AR相同输出；alignment四步accepted1/rejected3，28层raw核对通过。v3/v4全部token/接受/KV/AR计数/对齐sums等值（不比较耗时）。本次n=1只是实际前置门，不支持输出空间/Kalman或完整矩阵结论。正式资料见 [四格报告](../studies/input_mask_baseline/docs/STUDY_REPORT.md) / [v4证据](../studies/input_mask_baseline/docs/v4_execution.json)；下载snapshot、资源、原始证据与图均保存，weights/raw不入Git。

新工程验证已实际完成36格tiny严格等值及最终源码wheel/sdist双入口全链。B-008新增嵌套轴/子集回归通过；全量曾253通过/1复制fixture漏正式JSON失败，复制范围已修正并单独3声明用例通过，最终全量254 passed（177.46秒，0 failed/errors/skipped），Ruff与55文件mypy通过；正式增量记录在smoke/v031_validation.json，不将旧251批次替代新源码验收。上游Issues36/37保持真实链接，不改上游源码或权限。旧拒绝推送状态留在下方历史段；当前继续按工作分支→PR/dev流程，不自动合并或发布。

推送前历史检查点：本轮实现和验收已提交为5cfdacc9b0386d490cfc4d741b72305c450c5983。当时推送refactor/spec-rpipe再次被自动审批拒绝，理由是需对这批代码、研究报告和证据向该公开仓库/分支的特定授权；已向用户明确请求。实查远端仍49dec9c，dev仍1b6d59c，没有新PR，当前提交没有远端CI。旧49dec9c的cpu-checks成功不代表本轮；具体PR正文与同步状态保存在本机.tmp/input-mask-ms-20261014。除这一外部同步步骤外，当前范围本机实现、工程与真实四格前置验收均完成。

## v0.3.1原工程检查点（2026-10-14，95c0887）

补查缓存环境覆盖及本机模型目录仍未取得Qwen3-0.6B，4B/8B未替代。C-007的pending eval误显示train/过滤漏项已用原生CLI最小复现，读数不改变调度或文件；已提交 [Issue #37](https://github.com/DreamSoul-AI/RPipe/issues/37)。继续以真实config/jobs核对执行mode。工程逐项证据核对通过，四格真实解码、资源校准、推送/PR/新CI仍缺必要条件，整体目标未完成。

实现与本机证据已本地提交 cb5c36d57e02d068d42ad6b1f0d5195cf5fd1186。推送/草稿 PR 的组合操作被自动审批拒绝，未执行；随后确认目标仓库为公开仓库且当前账号有 push 权限。仍待明确外传批准，不绕过拒绝。当前新提交没有远端 CI 结果，交接49dec9c的绿色检查只证明旧提交。PR正文已备妥于本机.tmp/v031-20261014/pr-body.md。

已从交接提交49dec9c接续 refactor/spec-rpipe，保留未跟踪 history_mtp.code-workspace。当前完整 vendor 为固定7a15c46 / v0.3.1，Windows torch-first 唯一例外与MIT保留；旧副本只备份，不删除。职责映射沿用既有迁移，科学 Algorithm、Data、Model 与数值配方未改。

- report 采用上游身份/原子门，专项先只读身份校验再做真实 process envelope 质量写回。B-007 已修：缺 raw 拒绝并写 complete=false，旧身份与写入失败保全旧表。
- 新设备安装不覆盖CUDA torch；本机251项全量、Ruff、55文件mypy、固定36格CPU token/AR/接受/KV轨迹、Windows双导入与新version smoke、新设备三variant CUDA tiny、wheel/sdist真实全链均通过。模板与随机tiny不替代真实模型质量；正式证据在 smoke/v031_validation.json 与报告。
- C-004 在当前main同一v0.3.1的两步Toy/Stub新Run复现并备份前后result，已提交 [Issue #36](https://github.com/DreamSoul-AI/RPipe/issues/36)。未改上游代码或权限。
- input_mask_baseline 新version为input-mask-baseline-v031-win5090-20261014-v2，四Run已make，succeeded=0/failed=0/pending=4。Study/default ModelScope离线核验均CacheNotFound E1022；等待Qwen3-0.6B snapshot路径。资源inventory不等于校准，真实四格尚未launch，研究质量未通过。

接手先读取当前工作树、远端/CI与 [四格PLAN](../studies/input_mask_baseline/docs/PLAN.md) / [前检](../studies/input_mask_baseline/docs/v031_device_preflight.json)。权重可取得后只核对原配方并串行校准/执行四格，不能以其他规模模型或Tiny替代。PLAN已经进入锁；任何来源/输入调整先明确变更与新version，不对旧成功Run重新make。原始工程日志/raw在本机.tmp/v031-20261014，clone只有正式摘要；历史下面49dec9c段保留当时状态。

## 49dec9c 原交接（2026-10-14）

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
