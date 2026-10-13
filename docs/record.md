# 开发记录

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
