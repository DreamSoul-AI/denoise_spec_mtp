# 问题与兼容性记录

## 2026-10-13

| **编号 / 来源** | **复现与影响** | **处理 / 验证** |
| --- | --- | --- |
| C-001 / 固定 RPipe v0.3.0 接口边界 | SpecMTP 注册 Data 后仍不能使用 make 的默认共享预构造：prepare_shared_data 先调用 endpoint_for，local_prompts/SpecBench 没有 torchvision host。Recipe 在 Run prepare 才运行，无法改写 make 下载职责 | 保留当前工作区已做的 prepare_shared:false；Run Data/Model builder 继续落 shared/data 与 shared/model。make→launch 回归验证，不修改 vendored 下载逻辑 |
| C-002 / 固定 RPipe 源码与下游 lint 策略 | 对固定副本运行 Ruff F401，train/__init__ 与三个 api facade 的公开转导出触发 8 项错误 | pyproject.toml 精确到四文件忽略 F401；保留上游源码与公开接口。Ruff 仍检查其余规则和全部专项代码 |
| C-003 / Windows 本机导入兼容 | 固定上游 numpy-first 与本机科学依赖 DLL 顺序不兼容，当前分支已有 torch-first 例外 | 保留唯一 src/rpipe/__init__.py 例外；windows_selfcheck 分别验证两种入口。非逐字节未改的副本 |
| B-001 / 下游证据门 | 只读 summary.csv 和 sources digest，可能接受缺失 raw token、执行后源码变更或手改摘要 | execute 保存 inputs/observations；summarize/write/process 校验真实 token、接受/cache 轨迹、配置、输入文件和来源；失败门回归 |
| B-002 / 下游历史 Run 验收 | 仓库 smoke 已有旧源码锁；新源码普通 run 的首轮测试被拒绝 | 保留失败日志与旧产物；测试改隔离目录，正式 smoke 加新 version。禁止对旧结果重新签收 |
| B-003 / 下游 CUDA 证据核对 | GPU tiny 原始 exact-match=1，但 legacy settings.device=cuda 与实际 model.device=cuda:0 被误判配置漂移，summarize 正确留下 failed 而未定稿成功 | 用已记录的实际 settings 表示重建有效 eval 配置；完整 config digest 仍拒绝真正变化，实际设备独立记录。新增别名回归，保留 final02 失败，用 final03 复验 |

上述 C 项描述固定上游与本项目的边界，不是对 RPipe 上游的修改请求。正式数字与验证范围见 [smoke 报告](../studies/smoke/docs/study_report.md)。
