# RPipe 依赖迁移说明（`refactor/rpipe-dependency`）

面向从 bundle / patch 导入本分支的读者。更细的开发流水账见 [RECORD.md](RECORD.md)；目录合同见 [LAYOUT.md](LAYOUT.md)；解码语义见 [ARCHITECTURE.md](ARCHITECTURE.md)。

**基线**：`dev` = `b1f6191`（已合入的「复制 RPipe」布局）。
**RPipe 钉扎**：`diaoenmao/RPipe` `dev` @ `ce8b3e6453d282711f0032b73409e147a49d49fa`（`pyproject.toml`）。
**本分支**：本地准备，**未推送**；GitHub Actions 未跑。验证用 `tools/ci_local.py` / `pytest`。

---

## 1. 架构变化

| **之前（复制）** | **之后（依赖）** |
| --- | --- |
| `src/rpipe/` 整包 + `src/spec_mtp/` 换包名复制的 Flow / Registry / Tracker … | 删除复制框架；安装钉扎的 RPipe |
| `api/spec_mtp/register.py` 导入时注册，并运行时补丁 `_shared_data_mapping` | Study `recipe.register(ctx)` 注册；`flow.prepare_shared: false` |
| console script 覆盖真正的 `rpipe` | 只保留 `spec-mtp` / `python -m spec_mtp`（薄封装） |
| 无质量门 | Study `flow/write` → `spec_mtp.flow.checks`；`exact_match_rate != 1` → failed Run |
| provenance 几乎只有包名 | SpecMTP 源码哈希 + git + 已装 RPipe 提交；`freeze: true` 时源码漂移失败 |

`src/spec_mtp/structure/<layer>/` 只保留 SpecMTP 算法与适配（mask、树、解码、esp / ar / alignment、数据、模型、门控）。调度与 Flow 阶段链全部来自已安装的 RPipe。

---

## 2. 保留的语义（算法未改）

- ESP / EMA-velocity 投机解码、sample matching、树构造与验证路径与迁移前一致。
- 冒烟回归：`studies/smoke_tiny_llama/regression/REFACTOR_REGRESSION.json`（相对 `b1f6191` 的 token / 指标对照）。
- 接受数、tau、投机侧 token 计数口径不变；研究结论仍以接受的 draft 数为准。
- **不改 RPipe 上游**；不重跑已有数字的 `history_extrapolation` 格子。

---

## 3. 方案 A（上下文上限与 exact_match）

投机块需要树 + k 个 mask 槽，会比纯 AR 更早撞 `max_positions`。迁移后 write 门要求 `exact_match_rate == 1`，6 个撞上限格子会因「输出是 AR 前缀、只差长度」而失败。

**采用方案 A**：撞上限时，AR 参照的 `max_new_tokens` 收到投机侧实际达到的 `new_tokens`。影响仅这些 prompt 的 `ar_calls` / `exact_match` / AR 计时 / `speedup`；接受数与投机 token 不变。证据：`CONTEXT_LIMIT_OPTION_A.json`。方案 B（前缀审计）留在本地分支 `fix/ctx-limit-prefix-audit`，**未采用**。详见 [CONTEXT_LIMIT.md](CONTEXT_LIMIT.md)。

---

## 4. RNG：`sample_embedding` 分叉

`SpecDecoder` 为 mask 初始化 `_fork_generator` 一份与采样 generator 同状态的独立 Generator，避免 `sample_embedding` 抽噪声抢走采样流。temperature > 0 时与 `ar_generate` 逐 token 一致。见 [MASK_INIT_RNG.md](MASK_INIT_RNG.md)；合入提交在本分支历史上。

---

## 5. 动态树 attention 缓存

`DynamicTreeAttentionCache`：动态树每步形状会变，对**同结构**做记忆化 / 向量化构建，与 naive `build_block_attention` 输出逐项一致（指纹与 dry-run 核对过）。`TreeAttentionCache`（efficient + static）的缓存键含 dtype / device / min_value，避免 bf16 复用 float32 结构。static + naive 仍走字面 builder（Table 4 消融）。

---

## 6. `alignment_probe` CSV

RPipe 适配层调用探针时曾传 `save_dir=None`，`alignment_metrics.csv` 从未写出，write 门必失败。现写到 Run 的 `assets/`；探针计算本身未改。paper_hf 无权重 dry-run 发现并回归。

---

## 7. 如何从 bundle / patch 导入

交付物在仓库外的 `out/`（本机打包目录，不进 git），通常包含：

- `denoise_spec_mtp-YYYY-MM-DD.bundle`
- `patches/refactor-rpipe-dependency/*.patch`
- 参考：`unadopted-fix-ctx-limit-prefix-audit`、`fix-mask-init-rng`、`perf-dynamic-tree-mask`
- `README.txt`（sha256、tip、验证说明）

**前置**：本地已有 `dev` = `b1f6191`（或能 fetch 到该提交）。

```bash
# 方式 A：bundle
git fetch /path/to/denoise_spec_mtp-YYYY-MM-DD.bundle \
  refactor/rpipe-dependency:refactor/rpipe-dependency

# 方式 B：patch（在干净的 dev 工作树上）
git checkout -b refactor/rpipe-dependency b1f6191
git am /path/to/patches/refactor-rpipe-dependency/*.patch
```

然后：

```bash
pip install -e ".[dev]"          # 拉取钉扎的 RPipe
python tools/ci_local.py         # 或：ruff / mypy / pytest tests/spec_mtp
```

未采用的方案 B、已合入前的独立 tip（mask-init-rng / dynamic-tree-mask）可用对应 patch 目录对照，不必再合。

---

## 8. 本分支上额外的本地加固（未推送）

在依赖迁移之后同一分支上陆续做了：方案 A；alignment_probe 产物；paper_hf Study 与无权重 dry-run；Windows 导入顺序开关；动态树缓存与 RNG 分叉合入；TreeAttentionCache 键；load_lock / freeze 损坏 JSON；ci_local 并发隔离；mypy 严格 / 中档；decoding / esp_mtp / tree / mask_providers 边界测试；CPU profile 与 decode fingerprint 工具等。每项本地提交并跑过 `ci_local`。

---

## 9. 未覆盖 / 明确未做

| **项** | **说明** |
| --- | --- |
| 推送 / PR / Actions | 未推；workflow 文件未改；本地绿 ≠ CI 绿 |
| GPU / 真实 HF 权重 | 未跑；paper_hf 仅配置展开 + tiny dry-run |
| Windows 真机 DLL 顺序 | 仅逻辑测试；需 `tools/windows_selfcheck.py` |
| 重跑 history_extrapolation | 按约定不重跑已有数字格子 |
| 改 RPipe / 改算法语义 | 禁止；本迁移与后续加固都不碰 |
| 方案 B | 仅本地分支保留，未采用 |

---

## 10. 相关入口

| **文档** | **内容** |
| --- | --- |
| [LAYOUT.md](LAYOUT.md) | 目录与 RPipe 钉扎 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 解码与 Flow 合同 |
| [CONTEXT_LIMIT.md](CONTEXT_LIMIT.md) | 方案 A |
| [MASK_INIT_RNG.md](MASK_INIT_RNG.md) | RNG 分叉 |
| [TESTING.md](TESTING.md) / [CI.md](CI.md) | 测试与本地重放 |
| [RECORD.md](RECORD.md) | 按日开发记录 |
| [WINDOWS.md](WINDOWS.md) | 导入顺序开关 |
