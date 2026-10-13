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
