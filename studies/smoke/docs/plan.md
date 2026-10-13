# plan — smoke

## 2026-10-13 v0.3.0 适配验收

目标：固定 RPipe 804b3823，保留 ESP/EMA/AR/alignment 的 training-free 语义，验证实际六阶段、来源冻结与拒绝成功边界。非大模型研究矩阵，不重跑历史正式接受数。

1. 同一设备和依赖上保存 c3263c0 工作区改动前的 555 格 fingerprint，再与当前来源对照；固定 tiny LLaMA、prompt、temperature 和 seed 不变。
2. 导出旧链 b1f6191 的 src，使用 [validate_migration.py](../validate_migration.py) 比较三种 smoke variant × T={0,0.7,1} × 四个固定 prompt。被动 Python line trace 读取接受路径/cache，不改旧源码；比较完整 token、接受/回退与 cache 轨迹。T=0 历史 tiny accept_d1 为 27/31/8。
3. 新 version rpipe-v030-20261013 走 make→launch→process/status/logs/report；AR/alignment 与失败边界由真实 CLI 回归验证。CPU 串行，不做吞吐排名。
4. wheel/sdist 各在源码目录外安装至隔离 .tmp，复用已有科学依赖，核对 import、console script、ORIGIN/LICENSE 和实际 tiny 阶段链。
5. Windows 双导入入口验证；CUDA 只允许随机 tiny 三 variant 串行门，不下载真实模型，不扩大并发，不宣称大模型/恢复已验收。

所有新实测采用新 Run ID/目录；失败日志留 .tmp（不会随 clone 提供）。正式结果和条件记 [study_report.md](study_report.md)。执行有不一致时保留反例，不放宽阈值。
