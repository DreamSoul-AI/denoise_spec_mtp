#!/usr/bin/env bash
# Main results (paper Table 1 / Figures 4-5): ESP + EMA-velocity + AR at
# BC = 10/30/60 for one model family.
#
#   bash scripts/run_main_results.sh llama3_2_3b
#   bash scripts/run_main_results.sh llama3_1_8b
#   bash scripts/run_main_results.sh qwen3_8b
#   bash scripts/run_main_results.sh qwen3_32b
set -euo pipefail
cd "$(dirname "$0")/.."

FAMILY="${1:-llama3_2_3b}"
CFG="configs/hf/${FAMILY}/run_0"

python src/main.py --cfg_file "${CFG}/ar_baseline.yaml"
for method in esp ema; do
  for bc in bc10 bc30 bc60; do
    python src/main.py --cfg_file "${CFG}/${method}_${bc}.yaml"
  done
done
