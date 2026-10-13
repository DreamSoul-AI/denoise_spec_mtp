# Numbers: smoke

Generated from `process.json`. The conclusion stays in `STUDY_REPORT.md`.

## Experiments

| factors | metric | mean | std | min | max | n |
|---|---|---:|---:|---:|---:|---:|
| algorithm.config.variant=esp_static | test_accepted | 28.0000 | 0.0000 | 28.0000 | 28.0000 | 1 |
| algorithm.config.variant=esp_static | test_committed | 124.0000 | 0.0000 | 124.0000 | 124.0000 | 1 |
| algorithm.config.variant=esp_static | test_decodecalls | 97.0000 | 0.0000 | 97.0000 | 97.0000 | 1 |
| algorithm.config.variant=esp_static | test_exactmatchrate | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 1 |
| algorithm.config.variant=esp_static | test_tau | 1.2784 | 0.0000 | 1.2784 | 1.2784 | 1 |
| algorithm.config.variant=esp_dynamic | test_accepted | 31.0000 | 0.0000 | 31.0000 | 31.0000 | 1 |
| algorithm.config.variant=esp_dynamic | test_committed | 124.0000 | 0.0000 | 124.0000 | 124.0000 | 1 |
| algorithm.config.variant=esp_dynamic | test_decodecalls | 94.0000 | 0.0000 | 94.0000 | 94.0000 | 1 |
| algorithm.config.variant=esp_dynamic | test_exactmatchrate | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 1 |
| algorithm.config.variant=esp_dynamic | test_tau | 1.3191 | 0.0000 | 1.3191 | 1.3191 | 1 |
| algorithm.config.variant=ema_velocity | test_accepted | 8.0000 | 0.0000 | 8.0000 | 8.0000 | 1 |
| algorithm.config.variant=ema_velocity | test_committed | 124.0000 | 0.0000 | 124.0000 | 124.0000 | 1 |
| algorithm.config.variant=ema_velocity | test_decodecalls | 116.0000 | 0.0000 | 116.0000 | 116.0000 | 1 |
| algorithm.config.variant=ema_velocity | test_exactmatchrate | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 1 |
| algorithm.config.variant=ema_velocity | test_tau | 1.0690 | 0.0000 | 1.0690 | 1.0690 | 1 |

## Runs

| factors | seed | id | metrics | log |
|---|---:|---|---|---|
| algorithm.config.variant=esp_static | 123 | `5afa2281f1bdb3e4` | test_accepted=28.0000, test_committed=124.0000, test_decodecalls=97.0000, test_exactmatchrate=1.0000, test_tau=1.2784 | [run.log](../runs/5afa2281f1bdb3e4/assets/logs/run.log) |
| algorithm.config.variant=esp_dynamic | 123 | `0ebb2f566e0b46b5` | test_accepted=31.0000, test_committed=124.0000, test_decodecalls=94.0000, test_exactmatchrate=1.0000, test_tau=1.3191 | [run.log](../runs/0ebb2f566e0b46b5/assets/logs/run.log) |
| algorithm.config.variant=ema_velocity | 123 | `de876f8232440e79` | test_accepted=8.0000, test_committed=124.0000, test_decodecalls=116.0000, test_exactmatchrate=1.0000, test_tau=1.0690 | [run.log](../runs/de876f8232440e79/assets/logs/run.log) |
