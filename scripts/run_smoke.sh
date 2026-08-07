#!/usr/bin/env bash
# CPU smoke run: tiny random LLaMA, synthetic prompts, no downloads.
# exact_match_rate must be 1.0000 in every summary (lossless audit).
set -euo pipefail
cd "$(dirname "$0")/.."

python src/main.py --cfg_file configs/smoke/tiny_llama/run_0/esp_dynamic.yaml
python src/main.py --cfg_file configs/smoke/tiny_llama/run_0/esp_static.yaml
python src/main.py --cfg_file configs/smoke/tiny_llama/run_0/ema_velocity.yaml
