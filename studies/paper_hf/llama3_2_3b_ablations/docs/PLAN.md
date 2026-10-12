# PLAN — paper_hf/llama3_2_3b_ablations

由 `configs/hf/` 迁移（2026-10-12），只换承载方式，不改格子和取值。论文对照见 [README.md](../../../../README.md) 的 Config → Paper Map，读法差异见 [ARCHITECTURE.md](../../../../docs/ARCHITECTURE.md)。

**状态：未运行。** 需要 GPU 和权重（`meta-llama/Llama-3.2-3B-Instruct`，HF Hub，`local_files_only: false`）。CPU / CI 只验证展开和配置校验（`tests/spec_mtp/test_paper_hf.py`），不加载权重。

## 判定

1. `exact_match_rate` 必须是 1（write 门；bf16 下可能不成立，见 history_extrapolation 对 Qwen3-8B bf16 的记录）。
2. 主指标是接受的 draft 数；速度和 `tau` 不决定结论。

## 格子

| **variant** | **来源** |
| --- | --- |
| `llama3/bc120_masks3` | `configs/hf/llama3_2_3b/ablations/bc120_masks3.yaml` |
| `llama3/impl_naive_bc30` | `configs/hf/llama3_2_3b/ablations/impl_naive_bc30.yaml` |
| `llama3/init_lastk_bc30` | `configs/hf/llama3_2_3b/ablations/init_lastk_bc30.yaml` |
| `llama3/init_offset10_bc60` | `configs/hf/llama3_2_3b/ablations/init_offset10_bc60.yaml` |
| `llama3/init_offset5_bc60` | `configs/hf/llama3_2_3b/ablations/init_offset5_bc60.yaml` |
| `llama3/init_sample_bc30` | `configs/hf/llama3_2_3b/ablations/init_sample_bc30.yaml` |
| `llama3/lam001_bc30` | `configs/hf/llama3_2_3b/ablations/lam001_bc30.yaml` |
| `llama3/lam05_bc30` | `configs/hf/llama3_2_3b/ablations/lam05_bc30.yaml` |
| `llama3/masks1_bc60` | `configs/hf/llama3_2_3b/ablations/masks1_bc60.yaml` |
| `llama3/masks3_bc60` | `configs/hf/llama3_2_3b/ablations/masks3_bc60.yaml` |
| `llama3/pruner_off_bc30` | `configs/hf/llama3_2_3b/ablations/pruner_off_bc30.yaml` |
| `llama3/update_off_bc30` | `configs/hf/llama3_2_3b/ablations/update_off_bc30.yaml` |

固定：seed 123，`deterministic: false`，`system.config.device: cuda`（原 YAML 的 `eval.device: auto` 由 Run 设备代替）。

## 怎么跑

```text
set PYTHONUTF8=1
python -m spec_mtp make studies/paper_hf/llama3_2_3b_ablations
studies/paper_hf/llama3_2_3b_ablations/scripts/launch.ps1
```

开跑前补 §3 排班与时长预估（RPipe `studies/README.md`）。
