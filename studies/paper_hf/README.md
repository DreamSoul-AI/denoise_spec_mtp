# paper_hf — configs/hf 的 Study 形式

2026-10-12 由 `configs/hf/` 生成，**未运行**：需要 GPU 和 HF 权重（LLaMA-3.1-8B / 3.2-3B、Qwen3-8B / 32B）。本轮只验证：

- `migrate_configs.py --check`：生成文件与 `configs/hf/` 一致；
- 11 个 Study 经 RPipe `expand_study` 展开为 59 个 Run，与 59 个原 YAML 一一对应（data / model / task / eval / 生效 spec / seed 逐项相等）；
- 每个 Run 配置通过 `spec_mtp.recipe.validate`。

见 `tests/spec_mtp/test_paper_hf.py`。

## 无权重 dry-run

`python tools/paper_hf_dryrun.py [--study <name>] [--cells N] [--out report.json]`：把每个 Study 复制到临时目录，只换底座：模型换成随机 tiny LLaMA（2 层、vocab 256，不下载），数据换成 2 条合成 prompt，`max_new_tokens` 16、`num_eval_prompts` 2、`probe_steps_per_prompt` 4，设备 CPU。task、temperature、`stop_on_eos`、`run_ar_baseline`、全部 variant 预设、seed、recipe、flow 钩子和 exact_match 门原样保留，再走 `python -m spec_mtp run`。

2026-10-12：11 个 Study、59 个 Run 全部成功，esp_mtp 格子 `exact_match_rate` 全为 1，Study 级门通过（约 1 分钟）。这只说明每个论文预设能被接受、能在真实 transformer 结构上无损解码、能过门；不说明真实模型上的接受数、GPU、bf16 或显存。dry-run 首轮发现 alignment_probe 从不写 `alignment_metrics.csv`（已修，见 RECORD）。CI 里 `test_paper_hf_dryrun.py` 每种 task 跑 1 格。

| **Study** | **格子** |
| --- | --- |
| `<family>_main` | `run_0/esp_bc*`、`ema_bc*`（10 格） |
| `<family>_ar_baseline` | `run_0/ar_baseline` |
| `llama3_2_3b_alignment_probe` | `run_0/alignment_probe`（Dolly） |
| `llama3_2_3b_ablations` | `ablations/*`，temperature 0（12 格） |
| `llama3_2_3b_ablations_temp1p0` | `ablations/temp1_bc30`、`temp1_bc60` |

spec 块原样放在 `src/spec_mtp/structure/algorithm/paper_variants.py`，键 `llama3/<cell>` 或 `qwen3/<cell>`（两个 LLaMA 家族的 spec 相同，两个 Qwen 家族相同；生成器在不同时报错）。改格子：改 `configs/hf/` 再跑 `python studies/paper_hf/migrate_configs.py`。

与原 YAML 的差别只有承载方式：`eval.device: auto` 改由 `system.config.device: cuda` 给出；`model.type` 变成 `model.name`。
