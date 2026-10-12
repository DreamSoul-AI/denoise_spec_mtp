# STUDY_REPORT — smoke_tiny_llama

## 历史记录（2026-10-08，复制框架时期）

本机 CPU，`python -m rpipe run studies/smoke_tiny_llama`（当时是仓库内复制的 RPipe）。随机 tiny LLaMA，四条合成 prompt，seed 123。三格 `exact_match_rate` 都是 1，`accept_d1` 与更早的旧入口一致。

## 本轮实测（2026-10-12，依赖 RPipe `ce8b3e6`）

环境：Linux box，CPU，Python 3.13.5，torch 2.14.1+cpu，transformers 5.19.0，float32，eager attention。随机初始化 tiny LLaMA（无下载），四条合成 prompt，seed 123。入口 `python -m spec_mtp run` 与 `python -m rpipe run` 都跑过，另走过 `make` + `launch` 脚本路径，以及 wheel 独立安装后在仓库外运行。这是流水线核对，不是方法比较。

| **variant** | **accept_d1** | **accepted** | **exact_match_rate** | **Run 状态** |
| --- | ---: | ---: | ---: | --- |
| esp_static | 27 | 28 | 1 | succeeded |
| esp_dynamic | 31 | 31 | 1 | succeeded |
| ema_velocity | 8 | 8 | 1 | succeeded |

Study scope：`spec_mtp_study_check.json` 为 `complete: true, passed: true`，三条 Run 同一 SpecMTP 源码 digest。

### 重构前后对照

`regression/REFACTOR_REGRESSION.json`：旧代码 `b1f6191`（复制框架）与新代码同条件运行 5 个 Study、26 个格子、249 条解码 / AR 输出序列，token 序列、逐 prompt 行（accepted、committed、decode_calls、tau、hit_context_limit、exact_match）、summary 与 Run 状态全部一致；只排除计时字段。覆盖 temperature 0 / 0.8（采样 RNG 顺序）、静态 / 动态树、naive / efficient、EOS 停止、context limit、六个命名 mask、`ar_baseline`、`alignment_probe`。

### 本轮发现（未改算法）

`max_position_embeddings=56`（prompt 32 + 32 新 token 触及上下文上限）的 6 个格子，新旧代码都得到 `exact_match_rate = 0`：投机解码按 `root + 1 + 树深 + k` 提前停在上下文上限前，AR 继续生成到上限，两者长度不同。旧流水线把这些 Run 记为 `succeeded`；新的 write 门把它们记为 `failed`（`test_exact_match_failure_fails_the_run`）。这是既有停止条件的口径差异，迁移本身保留了它（`REFACTOR_REGRESSION.json` 记录的是纯迁移）。

2026-10-12 采用方案 A（[CONTEXT_LIMIT.md](../../../docs/CONTEXT_LIMIT.md)）：撞上限的 prompt，AR 参照只生成到投机解码实际达到的长度，再整段比较。`regression/CONTEXT_LIMIT_OPTION_A.json`：这 6 格 `exact_match_rate` 0 → 1、Run 成功；口径变化只在 `ar_calls`、`exact_match`、AR 计时和 `speedup`（这些 prompt 的 speedup 按较短长度算）；其余 20 格与旧代码完全一致；投机解码 token 序列全部不变。解码算法未改。

### 未覆盖

GPU、真实权重（Qwen3 / LLaMA）、bf16、sdpa、Windows、GitHub Actions 均未在本轮运行。Python 3.12.15 只在本地 venv 跑过 pytest。

Run 目录在 `studies/smoke_tiny_llama/runs/`，不进 git。
