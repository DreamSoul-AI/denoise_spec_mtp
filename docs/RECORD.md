# RECORD

结构改动的开发记录。数字和研究结论留在对应 Study。

## 2026-10-12 依赖 RPipe，去掉复制框架（`refactor/rpipe-dependency`）

**起点**：`dev` = `b1f6191`（PR #3 合入 `refactor/spec-rpipe`，该分支没有未合并提交）。RPipe 采用 `diaoenmao/RPipe` `dev` 的 `ce8b3e6453d282711f0032b73409e147a49d49fa`（2026-10-12 HEAD，“align Study flow layout and explicit stage implementations (#28)”），从 GitHub 克隆，不用任何本机未提交改动。

**比较结论**：`src/spec_mtp/` 里的框架文件与 `src/rpipe/` 逐字相同（只换包名），而 `src/rpipe/` 是旧版 RPipe 0.2.0 本地 main，与 RPipe dev 已大量分叉（dev 新增 recipe、Study 阶段包、provenance / freeze、compare 等）。本项目真正的差异只有：SpecMTP 子模块、`api/spec_mtp/register.py` 里对 `_shared_data_mapping` 的运行时补丁、Windows 先 import torch。

**职责迁移**

| **旧** | **新** |
| --- | --- |
| `src/rpipe/`（整包复制） | 删除；`pyproject.toml` 依赖固定提交的 RPipe |
| `src/spec_mtp/flow/`、`structure/<layer>/` 框架复制 | 删除；用 RPipe 的 cli、FlowRunner、FlowContext、Factory / Registry、Tracker、Logger、result、make、provenance、process / readout |
| `structure/algorithm/eval/spec_mtp/*`、`structure/<layer>/spec_mtp/*` | `spec_mtp/structure/<layer>/*`（`git mv`，内容只改 import；`registry.py` 的 Algorithm → `algorithm/eval.py`） |
| `api/spec_mtp/register.py`（导入时注册 + 补丁 `_shared_data_mapping`） | `spec_mtp/recipe.py`（Study recipe 构造前注册 + 配置校验）；共享数据跳过改用 RPipe 的 `flow.prepare_shared: false` |
| `spec_mtp/__init__.py` 导入即注册 | 只保留 Windows 适配，不注册 |
| `spec_mtp.flow.cli`（复制的整套 CLI） | `spec_mtp/cli.py` 薄入口：make / run 写源码清单后转给 `rpipe.flow.cli.main` |
| console script `rpipe`（覆盖真正的 RPipe） | 删除；只保留 `spec-mtp` |
| 无质量门（`exact_match_rate=0` 也记 succeeded） | Study `flow/write` → `spec_mtp.flow.checks.run_gate`；Study scope `flow/process` → `study_gate` |
| provenance 只有包名 | `spec_mtp.structure.artifact.sources`：SpecMTP 源码哈希、git、RPipe 提交；make 时写锁，`freeze: true` 时源码变化在构造前失败 |

**验证**：见 [TESTING.md](TESTING.md)、[smoke 报告](../studies/smoke_tiny_llama/docs/STUDY_REPORT.md)。迁移提交时 72 个 pytest 全部通过：Python 3.13.5 主环境、独立 venv（`pip install -e ".[dev]"`，与 CI 同步骤）和 Python 3.12.15 venv（CI 版本）各一次，均为 torch 2.14.1+cpu、transformers 5.19.0；重构前后 26 格、249 条序列逐 token 一致；wheel 独立安装后在仓库外跑 smoke 通过。

**上下文上限（2026-10-12 采用方案 A）**：迁移后 6 个撞上限的格子 `exact_match_rate=0`（投机解码提前停在上限前，输出是 AR 的前缀，只差长度），新 write 门会判它们失败。采用方案 A：撞上限的 prompt 让 AR 参照只生成到投机解码达到的长度。口径影响只在这些 prompt 的 `ar_calls` / `exact_match` / AR 计时 / `speedup`；接受数、tau、投机解码 token 不变；其余格子与旧代码一致（`CONTEXT_LIMIT_OPTION_A.json`）。history_extrapolation 和论文设置碰不到上限，不受影响。方案 B 留在本地分支 `fix/ctx-limit-prefix-audit`，未采用。详见 [CONTEXT_LIMIT.md](CONTEXT_LIMIT.md)。

**alignment_probe 产物（2026-10-12 修）**：RPipe 适配层调用探针时传 `save_dir=None`（旧复制流水线同样如此），`alignment_metrics.csv` 从未写出，write 门因此必然判失败；paper_hf 无权重 dry-run 发现。现在写到 Run 的 `assets/`。探针计算不变。

**后续本地改进（2026-10-12，同一分支，未推送）**：动态树 mask 缓存（输出逐项一致，已合入）；sample_embedding RNG 分叉（T>0 exact_match，已合入）；TreeAttentionCache 签名含 dtype/device/min_value；load_lock 损坏 JSON 报路径；ci_local 并发隔离；tools/README 与 dry-run --list；解码边界测试套件；mypy 中档注解（kv_cache/common/mask_settings/tree_attention/csv_logger）；tree / mask_providers 边界测试；`tools/ci_local.py` 重放 CI；CI 增加 ruff（含 `tools/`）和 mypy（新模块严格档，见 [CI.md](CI.md)）；`studies/paper_hf/` 与无权重 dry-run（59 个 Run 全过）；alignment_probe 产物修复；hypothesis 属性测试与分支用例；配置错误给出近似建议并指出 Study；CPU 剖析工具与 [PROFILE.md](PROFILE.md)。每个提交都跑过 `tools/ci_local.py`（测试数随边界套件增加，以 tip 上 pytest 为准）。

**Windows**：旧包在 `sys.platform == 'win32'` 时先 import torch（注释说先 import NumPy 会在 `blas_fpe_check` 出错）。RPipe dev 已改成先 import NumPy（为与 Conda NumPy 共享 libiomp5md）。两者方向相反，Linux 上无法验证；默认保留旧包的 Torch 优先，可用 `SPEC_MTP_WIN_IMPORT_ORDER=torch|numpy|off` 切换，只在经 `spec_mtp` 入口（先于 rpipe 导入）时生效，经 `python -m rpipe` 时由 RPipe 的顺序决定。需在 Windows 本机跑 `tools/windows_selfcheck.py` 核对，见 [WINDOWS.md](WINDOWS.md)。

**未做**：不改 RPipe；不推送、不开 PR（本轮只在本地提交，交付 bundle / patch）；不重跑 history_extrapolation；`configs/hf/` 收成 `studies/paper_hf/`（11 个 Study、59 格，仅验证展开与配置一致）；GPU / 真实权重 / Windows 未运行；GitHub Actions 未运行（本地 3.12 通过不等于 CI 通过）。

**迁移总览（2026-10-12）**：面向从 bundle / patch 导入的读者，见 [MIGRATION_CHANGELOG.md](MIGRATION_CHANGELOG.md)（架构表、保留语义、方案 A、RNG、动态树缓存、alignment_probe CSV、导入步骤、未覆盖项）。日常流水仍记在本页。

**decoding / esp_mtp 边界（2026-10-12）**：`test_decoding_esp_boundaries.py` 钉死 select_token / tree_probs、budget=1、naive-static 字面 attention、EOS 中途截断与 AR 停词、`totals` / `_aggregate` / warmup 恢复 / 空 prompts / CSV / `run_ar_baseline=false` / `esp_mtp.test` 接线。不改算法。

