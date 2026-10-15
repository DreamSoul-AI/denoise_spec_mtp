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

工作流：`.github/workflows/cpu-checks.yml`。重放：`python tools/ci_local.py`。GPU Study 和真实权重不在 CI。CPU冒烟仍检查独立AR exact=1作为固定fixture回归；原生成功门是完整verifier argmax审计，AR差异仅诊断。

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

## source719／root720与跨prompt因素扩展（2026-10-15）

test_local_state_proxy.py覆盖固定state/proxy输入保全、fresh cache与因果attention阻止未来mask影响当前验证、mask变化确实改变后续输出、冻结六窗口、T0 seed不抽样、真实root720 source-owner与候选时序回归。实际24固定块三次bit重复、两canonical原值生成全张量/AR重现、四单位36生成AR/单坐标/teacher门见[最新报告](../studies/output_space_cross_task/docs/STUDY_REPORT.md)。不将greedy seed当独立随机样本，也不将direct block当完整生成。

收尾核验：42项针对性测试、Ruff与5个Study科学source/RPipe冻结门通过；新分析重跑保持原证据逐项一致，26个精确字节路径暂存blob与本机文件一致。旧helper/协议/科学src/default无改动，本轮3800生成新token、24额外固定块、4teacher均在预声明预算内。完整安装包/长矩阵/随机采样温度未重跑。

## 非T0耦合与owner1（2026-10-15）

test_sampling_causality.py检查原multinomial RNG被消耗且四因素共享draw、seed重复可复现而抽样token有变化、positive-temperature draft仍按top1构树、output_hidden在两温度／两seed／两order下等于fresh AR，以及owner1 rows5/6/PIDs719/720。真实权重另完成两条T=.8完整AR路径／self/graft门、原owner0和新owner1各128条件draw、12owner1固定块三重复，见[最新报告](../studies/output_space_cross_task/docs/STUDY_REPORT.md)。条件draw不是完整生成，也不以64次罕见候选零命中证明概率为零。

收尾核验：47项针对性测试、Ruff与5个Study科学source/RPipe冻结门通过；联合分析重跑与原formal证据一致，34个精确字节路径暂存blob与本机文件一致。1600生成new、12额外块、256条件draw在新协议预算内；旧source/default/配方/工具/Run未改。未做多prompt采样泛化、罕见事件统计检验或安装包／长矩阵重跑。

## 多prompt采样与罕见事件边界（2026-10-15）

test_rare_path_boundaries.py新增p=0/1端点、越界/N0拒绝、tiny p非零概率稳定计算、零观测单侧上界与最小95%命中检测数回归。真实10新单位70生成／7000new全部sampled AR／self／单槽scope门通过；两温度各4096native条件draw均零候选命中但不能排除10^-11～10^-9质量，见[报告](../studies/output_space_cross_task/docs/STUDY_REPORT.md)。不以分布质量证明有限精度sampler的极小概率可达性。

H7轨迹计数回归继续覆盖第一次收益／最终损失、净零抵消、方向保留、非语义metadata忽略、错误总计数与不共享前缀拒绝。真实新10单位中q242/123及125首变-1而净+5/+2，报告写回后实际执行下一假设，零额外model forward。

收尾核验：58项针对性测试、Ruff与5个Study科学source/RPipe冻结门通过；矩阵/rare/H7分析重跑与正式证据一致，45个精确字节路径暂存blob与本机文件一致。新7000生成new、8192条件draw、H7零新forward均在新合同范围。旧science/default/helper/Run不改，未扩展多任务/多温度/硬件，也未证明native rare尾可达性。

## 新seed方向反例与罕见条件压力测试（2026-10-15）

test_sampling_continuation.py新增12项：首命中使用真实seed、零/全命中Clopper-Pearson端点、空/错位/非法观察拒绝、压力条件命中不能提高原条件检测力、H8零/反向/保留/infeasible判读。test_sampled_depth.py新增7项：两侧相同正确第一候选且实际node1接受、合法node2翻转、第一候选不同/错误、未接受、EOS/缺少第二目标/无翻转控制。

真实六单位4200new/3806forward全AR；163840native条件draw含T=2命中2/7，原温度仍零且检测力不足。H10检查34共有原冻结窗口无合法depth2翻转；回归与合成fixture不替代上述GPU或有限捕获边界。

收尾核验：80项相关回归、Ruff与5个Study科学source/RPipe冻结门通过。新增19项统计/合法性回归，六单位42生成4200new3806forward、163840native条件draw、H10零新增forward均在冻结预算；正式分析再次执行逐项一致，来源/model/输入/旧helpers核对保持。源/default/旧合同/成功Run未改，未推送/PR/合并/删除。新sampled同KV四因素、原温度native极小尾可达性、安装包/速度/多设备/长矩阵未重验。

## 4B模型接续与禁用计时（2026-10-15）

`test_4b_pairing_contract.py`核对11格BF16配置、480条同输入、来源/输入不符在forward前拒绝、时钟与capture异常恢复、CUDA loader保持BF16；`test_output_hidden.py`覆盖BF16多深度/兄弟树与非首兄弟真实hidden/cache路径，`test_smoke_study.py`新增tiny HF BF16五方法+独立AR六Run原生CLI及owner/范数篡改拒绝。均为CPU tiny/Stub回归，不代表真实4B结果；实际运行与赢平输见[4B PLAN](../studies/qwen3_4b_bf16_five_methods/docs/PLAN.md)。

`test_4b_bf16_readout.py`覆盖接受数/calls各自赢平输、调用数反向判赢、缺失/错位/重复拒绝、AR长度分叉、11格pending不补零，以及native验收后480条合成读出格式；相对AR调用数控制涵盖胜/平/负和qid错位拒绝，保留长度不同的反例。该测试的mock仅验证读出与保留反例，不冒充真实模型或独立native验收。

test_4b_untimed验证三method tiny token/全部语义/calls保持、全局时钟不改及异常恢复、CUDA loader dtype/kwargs/恢复。test_4b_phases验证四phase的函数导出；test_4b_pairs保留正负零及拒绝缺配对。test_4b_input_control验证历史EMA字段/同链/原26与4输入manifest复用。原native配置展开新增4B Study，仍不加载真实权重。实际模型硬门来自10个成功4B native Runs，而非tiny fixture：first26/new4四格+EMA两格，所有输出和两类AR逐token一致。
