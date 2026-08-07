#!/usr/bin/env bash
# Appendix G.3: sampling mode, temperature = 1.0 (sample matching) at
# BC=30 (m1 [14]) and BC=60 (m1,m2 [15,4]).
#
#   bash scripts/run_ablation_temperature.sh llama3_2_3b
set -euo pipefail
cd "$(dirname "$0")/.."

FAMILY="${1:-llama3_2_3b}"
CFG="configs/hf/${FAMILY}/run_0"

python src/main.py --cfg_file "${CFG}/esp_bc30.yaml" \
  --set eval.temperature=1.0 \
  --save_name "ablation_temp1_bc30"
python src/main.py --cfg_file "${CFG}/esp_bc60_static.yaml" \
  --set eval.temperature=1.0 \
  --save_name "ablation_temp1_bc60"
