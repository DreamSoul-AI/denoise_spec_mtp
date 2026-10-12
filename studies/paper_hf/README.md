# paper_hf — configs/hf 的 Study 形式

2026-10-12 由 `configs/hf/` 生成，**未运行**：需要 GPU 和 HF 权重（LLaMA-3.1-8B / 3.2-3B、Qwen3-8B / 32B）。本轮只验证：

- `migrate_configs.py --check`：生成文件与 `configs/hf/` 一致；
- 11 个 Study 经 RPipe `expand_study` 展开为 59 个 Run，与 59 个原 YAML 一一对应（data / model / task / eval / 生效 spec / seed 逐项相等）；
- 每个 Run 配置通过 `spec_mtp.recipe.validate`。

见 `tests/spec_mtp/test_paper_hf.py`。

| **Study** | **格子** |
| --- | --- |
| `<family>_main` | `run_0/esp_bc*`、`ema_bc*`（10 格） |
| `<family>_ar_baseline` | `run_0/ar_baseline` |
| `llama3_2_3b_alignment_probe` | `run_0/alignment_probe`（Dolly） |
| `llama3_2_3b_ablations` | `ablations/*`，temperature 0（12 格） |
| `llama3_2_3b_ablations_temp1p0` | `ablations/temp1_bc30`、`temp1_bc60` |

spec 块原样放在 `src/spec_mtp/structure/algorithm/paper_variants.py`，键 `llama3/<cell>` 或 `qwen3/<cell>`（两个 LLaMA 家族的 spec 相同，两个 Qwen 家族相同；生成器在不同时报错）。改格子：改 `configs/hf/` 再跑 `python studies/paper_hf/migrate_configs.py`。

与原 YAML 的差别只有承载方式：`eval.device: auto` 改由 `system.config.device: cuda` 给出；`model.type` 变成 `model.name`。
