# STUDY_REPORT — smoke_tiny_llama

2026-10-08，本机 CPU，`python -m rpipe run studies/smoke_tiny_llama`。随机 tiny LLaMA，四条合成 prompt，seed 123。三格 `exact_match_rate` 都是 1。

`accept_d1` 与重构前旧入口一致。这是流水线核对，不是方法比较。

| **variant** | **accept_d1** | **exact_match_rate** |
| --- | ---: | ---: |
| esp_static | 27 | 1 |
| esp_dynamic | 31 | 1 |
| ema_velocity | 8 | 1 |

Run 目录在 `studies/smoke_tiny_llama/runs/`，不进 git。
