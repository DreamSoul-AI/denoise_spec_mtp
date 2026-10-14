# 开发记录

## 2026-10-14

- 继续 refactor/spec-rpipe，保留用户及上游工作区修改。前次 PR #5 已进入 dev（1b6d59c），当前分支快进到同树集成提交后继续；不推送 dev/main，不发布版本。
- 先写 rpipe-migration 职责映射，再迁移专项阶段、API 桥和证据核验。Study 阶段仅导入 src；默认 prepare/execute 不复制空壳，旧 CLI/recipe/checks/prompts 只保留兼容导出。业务从 data/__init__ 移出；科学解码核心保持。ModelScope 的现有 local_files_only 传至 snapshot_download，并有边界回归。
- 从宏观方案提取 input_mask_baseline 的四格真实模型前置门，先写 PLAN，核对研究六方面与固定 knowledge skills。只完成配置/来源和离线缓存解析，未运行真实模型；研究范围见该 Study。工程验证、失败和 tiny 轨迹见 [smoke 本轮报告](../studies/smoke/docs/STUDY_REPORT.md#八职责重构检查点2026-10-14)，不把旧正式接受数改成新结果。
- 用户要求改本地目录：Windows Move-Item 返回错误并部分移动。逐文件核对目的路径与碰撞后补齐 28875 个文件，无覆盖；Git HEAD/索引及历史证据保留。实际 checkout 为 denoising-speculative-decoding，editable 无依赖重装并核对 import / direct_url。旧路径只剩临时目录残留，未强删或修改系统设置。历史证据中的执行路径原样保留。
- 改名与交接文档后再次全量 239 passed / 0 skipped，Ruff、55 文件 mypy、模块/console CLI 和 Git 连通性门通过；没有重复历史正式模型格子。
- 用户要求本机收尾、push 并异机交接。已查 RPipe v0.3.1 的 annotated tag cd7a750de0d13889916eba84b53ed4a339d47a32，实际 commit 为 7a15c46b75c5eb951cccd60ed7b9fc3463db90f5。两项 src 变化为版本号和 readout/report.py 的 B-030 身份与原子写入修复；实际 research/feedback/README/flow 文档已取得。当前执行副本仍是 v0.3.0，升级及异机验证按 [交接记录](handover.md) 接续，不提前报告通过。

## 2026-10-13

- 按用户要求继续 refactor/spec-rpipe；fetch 后工作树与 origin/dev 的科学内容一致，保留当前分支，未修改 RPipe 上游。依据固定 v0.3.0 Study 合同重写指南、模板和 smoke 计划，统一 README / PLAN / STUDY_REPORT 命名并更新导航。历史计划保留，正式 JSON、smoke 配方与 accepted 数字不变。
- 模板修正“注册即下载”的说明和未展开的 {mask} description，改用上游支持的 experiment/seed 占位符，扩展现有配置展开回归；数据、模型、算法、seed 和预算不变。报告模板区分 all-depth accepted 与深度诊断，并记录阶段/来源、排班、失败/恢复边界。
- Study 报告补充由旧交付 JSON 生成的真实 tiny 结果图与同 Study 手动绘图入口，不执行解码或重新签收旧 Run。首轮 NumPy-first 绘图在本机触发已知 C-003 DLL 导入故障；torch-first 重放通过，脚本沿用本仓库局部导入顺序，未修改环境/系统。图源、指标和研究边界见 [smoke 报告](../studies/smoke/docs/STUDY_REPORT.md)，临时故障脚本和验证日志留 .tmp/studies-rewrite-20261013。

- 本次 Study 重写验证：236 个现有回归全部通过（独立 --basetemp），覆盖模板/三 variant 配置展开、隔离 CPU tiny 实际 CLI 和失败门；Ruff 0.17.0 与 mypy 2.4.0（40 源文件）通过。另核对 Git 索引大小写敏感链接、完整 YAML 语义和三个历史 JSON 保留；图脚本实际执行并检查输出。未重复数值矩阵、GPU/安装包/恢复/并发验收，科学源码及包配置未改。

- 仓库改名为 DreamSoul-AI/denoising-speculative-decoding，默认分支从 dev 调整为 main；同步当前 checkout 的 origin。工作分支 → PR → dev → 同仓库 dev 的 PR → main，补充只读 metadata 的 Branch flow 门，不合并当前 PR 或发布版本。保留原审批、CPU CI、禁止直接推送/强推/删除规则。

- refactor/spec-rpipe 初始 HEAD c3263c0，与远端一致；保留并纳入既有 8 文件 prepare_shared 修改。远端 fetch 原指向已删除分支，显式获取实际 refs 完成同步，没有切分支。
- 固定上游 804b3823ab6d2af46cbda1a65688ca8b76c60b22；101 个文件经 Git 对象核对，仅 Windows torch-first __init__.py 不同，新增 ORIGIN 和匹配的 MIT 许可证。
- 复用现有 RPipe 执行库，专项 collect/summarize/write/process 经 Study 扩展接入；新增原始解码和输入证据、源码及输入漂移门。旧兼容 evaluate/test 调用保留，采样与 mask 更新不迁移到框架。
- 安装与 CI 工作流保留。兼容差异、首轮失败与处理见 [问题记录](bugs.md)；数值、Run ID、环境和复跑代码见 [smoke 报告](../studies/smoke/docs/STUDY_REPORT.md)。
- 首轮全测试 222 passed；补齐 Study 来源、AR/alignment 证据和 seed 轴合同后 224 passed。全流程最终来源验收以报告所列新 version 为准。

- 实现提交 7c89d7c 后，全测试 227 passed；新 CPU/CUDA tiny Run 和 wheel/sdist 各自完成实际阶段链，正式证据见 smoke 报告。CUDA 名称误报 B-003 已修复，final02 失败保留。未改 Actions 配置。
- 最终实现提交 934dac3：CLI 前置来源拒绝保全旧 result，Study 终验同步通用 envelope，report 先复验当前 index。最终 229 passed、Ruff/mypy 通过；该提交新 CPU/CUDA tiny 与 wheel/sdist 各自通过。C-004 的首次旧 Run 终态未备份无法恢复，未编造恢复结果。最终证据见 smoke delivery_validation.json。
- PR #4 面向 dev；首次 push CI 38367588147 发现本项目既有 tomllib.loads(bytes) 安装脚本错误，未进入 lint/tests。仅改 UTF-8 文本读取并执行同一依赖提取片段验证，不覆盖本机 GPU 环境、不关闭 Actions，后续远端门单独核对。
- 60fd569 的远端安装/lint 通过，mypy 38367956325 复现本项目 datasets/ namespace 遮蔽。设置 namespace_packages=false（所有 src 包已有 __init__.py），不屏蔽 attr-defined 或模块检查；在仓库根目录固定 mypy 复验全部 40 文件通过。科学源码与 Run 配方仍与 934dac3 一致。
- 4f104bb 的远端门已通过安装/lint/mypy/入口，运行测试 228 passed，仅正式 NUMBERS 的本机 raw log 链接失败（B-006）。保留数字、改为明确本机文本路径，正式链接只依赖入库报告/JSON，未改测试门限或科学实现。

## 2026-10-14 v0.3.1 当前设备接续

从49dec9c接续，交接提交cpu-checks已通过。先审阅固定新版本文档/接口并改设计，再备份/比较101文件、升级完整vendor到7a15c46；唯一源码差异Windows torch-first和MIT保留，不改上游仓库。发现并修复下游report拒绝raw缺失后旧complete仍true的问题，专项门与上游身份/原子门共存。固定36格严格相等，新设备251回归、Ruff/mypy、Windows与wheel/sdist全链通过；失败日志和边界见smoke报告/JSON。

C-004全新Toy/Stub最小复现、公开Issue/PR去重及脱敏完成，实际提交 [RPipe#36](https://github.com/DreamSoul-AI/RPipe/issues/36)。真实四格只make新version，缓存缺失有ModelScope E1022证据，未launch/未校准/未声明研究质量通过。阶段commit/push与面向dev草稿PR按当次授权进行，不自动合并、发布或改变远端规则。

本轮实现本地提交 cb5c36d；自动审批拒绝组合 push/草稿PR，理由为当前可信消息未明确确认外传目标及公开资料风险。已只读核实目标DreamSoul-AI/denoising-speculative-decoding为public且有push权限；未推送、未创建PR、未触发新提交CI。保留完整本地提交与待审PR文本，等待明确批准。

接续补查：缓存环境覆盖为空，本机D盘模型目录只有4B/8B。四个0.6B Run仍无result，未launch；不把缓存目录未知写成整个设备绝对不存在权重。核对当前源码digest、251项JUnit、41条包验收命令、CUDA raw源码身份及Data/Model/Algorithm与交接的空diff，工程证据保持成立。CUDA实测发生在49dec9c的未提交树，源digest8573dfa6b73d44fb已与当前实现核对相同。

C-007使用新Toy/Stub make及三条status命令复现，原生config/jobs为eval而pending读数train，eval过滤0条；readout保持文件哈希。已按授权去重脱敏反馈 [Issue #37](https://github.com/DreamSoul-AI/RPipe/issues/37)。源码未改；仅补充兼容事实、正式精选证据及本地交接，不重新运行已通过的工程批次。

## 2026-10-14 ModelScope四格与B-008纠错

用户要求ModelScope下载并继续工作后，在Study shared准备新0.6B缓存，记录实际文件哈希和加载/解码资源，保留CUDA torch及全部科学配方。v3四Run成功，但整轮因素门误拒绝；先设计、红例，再从声明/基底复用Rpipe有效合并分组修复B-008，不信任当前index作为期望，不放宽子集/seed/source/evidence门。新的v4四Run/Study全部通过，v3-v4原始token/AR/接受/KV和alignment数值相等；AR计时误比较仅修对照脚本，所有失败保留。正式事实在四格报告/JSON/图，不重复长矩阵。

新增来源JSON使复制fixture的*.json排除过宽，最终首轮253 passed/1 failed；已只排除生成artifact，声明3用例复验通过。36格tiny等值，最终源码wheel/sdist全链通过，Ruff/mypy通过；最终全量单独保存，未把Toy/Stub或旧批次算真实模型质量。

最终本机全量254 passed（177.46秒，0 failed/errors/skipped），Ruff/mypy、36格严格数值、wheel/sdist 41命令全部通过。正式证据追加smoke/v031_validation.json，不覆盖历史来源；真实v4 complete/passed=true，v3拒绝保留。

用户明确批准具体公开内容与仓库/分支后，推送ae86c3c成功并创建PR #6（refactor/spec-rpipe→dev）：https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/6 。Branch flow和push/PR cpu-checks已启动，本交接更新后核验PR最新head检查；不自动合并或发布。既有用户workspace文件保持未跟踪。

2026-10-14 用户要求自主继续，不反复询问。下一最小阶段在feature/output-space-prerequisite上按v6提取tied零/一阶链式Study，先写PLAN与职责映射再实现。已接入最后归一化hidden、按owner代理状态和精确观测时序，12初轮针对性通过，后补EOS/真实前缀hidden等值共14项通过；原生CLI专项门通过，owner证据篡改拒绝。尚未声明真实模型结果/整体完成，完整回归与旧轨迹对照继续。

输出空间v1四格真实Run已成功、Study complete/passed=true；源码670c744e0535dcad，三个投机输出均与47token独立AR相同。匹配输入均值链17、输出零阶10、一阶10；负结果保留，没有调整超参或扩大矩阵。串行资源与正式JSON/图/报告已记录，完整270测试/36格严格对照通过。

最终源码wheel/sdist 41CLI命令全部通过，两安装target的新输出方法真实解码均与AR一致；来源/PLAN/inputs最终只读核验，无重复实验或重新签来源。正式成果本地分支保存，PR6保持原提交与绿色CI，不自动合并。

2026-10-14 按监督请求接续，先读最新STUDY_REPORT/offline_diagnosis，选最低新增实现成本的3新prompt小矩阵。预声明q172–174、4Runs、固定配方/预算，源码670c744e0535dcad不改；串行make/launch/process/report及9投机输出对独立AR完全一致。accepted为输入6/零阶3/一阶5，逐prompt和匹配prefix差异全保留；q173一阶与零阶root94/97接受差异对应2次calls减少，机制原因仍缺hidden/logit观测。正式报告/复算工具和资源证据保存；没有调参、大矩阵、远端写入或数据清理。

2026-10-14 接续三prompt矩阵，先写WINDOW_PLAN并对q173 root83/94/97只读重放：三case token/语义轨迹复现，正确seed时序/teacher/isolatedprefix门通过。再固定2×2实测方向/范数4查询，root83输出方向换成输入范数仍错，输入方向扩大范数仍对，未据此调配方。事后离线源状态重构说明slot1无当前velocity直接项；各类测量与有限机制解释正式归档，raw selected张量仅本机。新增工具6项针对性通过，一次unused import的Ruff问题已去除并复验，科学src/原Run保持。

2026-10-14 接续77fe411，先固定q173 root83 owner0第二槽的零/一阶互换与一阶原值回填三case，无搜索/新增默认。实测99token全部与独立AR一致、单槽scope与实际接受owner门通过；一阶←零阶accepted3→1且两后期seed/logits等于零阶，反向零阶←一阶accepted1→2仅恢复root94。离线核验两段代理传播，前一方向五固定根committed anchor/v仍与一阶原值完全相同，后一方向v仍0，收紧历史/当前速度解释但保留单窗口边界。源码/旧Run/权重不改，资源与失败边界入库，新3项针对性通过；不推送、合并或删数据。
