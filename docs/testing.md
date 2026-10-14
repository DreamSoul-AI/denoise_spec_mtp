# testing

`tests/spec_mtp/` 测 SpecMTP 以及它和这份 `src/rpipe/` 的合同。RPipe 自己的行为在上游测。

```text
set PYTHONUTF8=1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -e ".[dev]" --no-deps
ruff check src tests studies tools
mypy
python -m pytest tests/spec_mtp
```

工作流：`.github/workflows/cpu-checks.yml`。重放：`python tools/ci_local.py`。GPU Study 和真实权重不在 CI。冒烟必须 `exact_match_rate == 1`。

现有 GPU 环境不执行上面的 CPU torch 安装。测试使用独立 --basetemp=.tmp/<new-id>。Ruff 的 vendored facade 例外见 [兼容记录](bugs.md)。tiny 接受数是回归基线；完整链还检查原始 token、来源漂移、证据缺失和 Study 完整性。

CPU 剖析：`python tools/profile_cpu.py`。输出身份：`python tools/decode_fingerprint.py`。Windows：`python tools/windows_selfcheck.py`。

分支门：`.github/workflows/branch-flow.yml` 的 `Branch flow` 只核对 PR metadata，不 checkout 或运行 PR 代码。工作分支先进入 dev；main 只接受同仓库 dev。默认分支为 main，两个长期分支均要求现有 cpu-checks 与 Branch flow，保留既有审批、防强推和防删除规则。

本次职责重构新增初始化器无业务定义、ModelScope local_files_only 参数和真实 Study 无权重展开回归。结构检查补充实际 tiny CLI、source 增删改/证据失败门，不能替代数值验收。真实模型前置门及其来源/图留 [input_mask_baseline](../studies/input_mask_baseline/README.md)，Toy/Stub 模板检查与随机 tiny 分开报告。

## v0.3.1 与当前 Windows 设备

`tests/spec_mtp/structure/artifact/test_readout_report.py` 覆盖旧 process/new index、Study/Run/seed/factors 身份、缺失/损坏清单、上游合法部分聚合、原子写失败及旧表保全；实际专项 make→launch→process→report 共存回归检查缺 raw 后 complete=false。

```text
python studies/smoke/validate_migration.py --out .tmp/<new-id>/tiny.json --compare studies/smoke/docs/tiny_decode_reference.json
python tools/windows_selfcheck.py --smoke --out .tmp/<new-id>/windows.json
python tools/package_selfcheck.py --workspace .tmp/package-<new-id>
```

package_selfcheck 构建 wheel/sdist，分别 target 安装，不建新 venv、不替换 GPU 依赖；从源码外目录证明导入来自独立 installed，核 ORIGIN/LICENSE 和两个模块/console 入口，再跑四 Run native Toy/Stub 与三 Run SpecMTP tiny 的 make/launch/process/status/logs/report、重复 launch 保全。它不验证从零安装全部依赖或真实模型质量。正式结果见 smoke 的当前设备报告；真实模型资源边界见 input_mask_baseline。

## 固定窗口状态／舍入因素（2026-10-15）

本轮测试清单：test_state_rounding_factors.py覆盖Phi全native/full64端点及输入不变、RMS阶段形状与native数学、真实cache根选择、单坐标同步与另一坐标/proxy保全、异常清理、等计数但不同路径、非加性交互。保留test_phi_rms、test_q178_numerics、test_cross_task_hypotheses的旧门，不用合成fixture替代真实GPU结论。

GPU实际检查另见[状态因素报告](../studies/output_space_cross_task/docs/STUDY_REPORT.md)与[算术因素报告](../studies/output_space_extension/docs/STUDY_REPORT.md)：六生成AR／native全张量／单坐标门和80直接算术格原值门通过。原生16输出与旧8格不重跑；本轮算术格不声称新的下游接受路径验收。

本轮收尾核验：37项针对性测试及Ruff通过，5个Study的科学source/RPipe冻结门通过，80格保存向量的标量差重新计算一致，18个精确字节路径的暂存blob与本机文件一致。完整原生矩阵、安装包、更多seed/层未重跑；科学源码/default/旧helper/成功Run无改动。
