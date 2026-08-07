#!/usr/bin/env bash
# Table 2: dynamic vs static branch configurations with two mask tokens.
#   BC=30: dynamic, [7,2], [5,4], [3,6]
#   BC=60: dynamic, [15,4], [12,7], [10,9], [8,11], [6,13]
#
#   bash scripts/run_ablation_tree.sh llama3_2_3b
set -euo pipefail
cd "$(dirname "$0")/.."

FAMILY="${1:-llama3_2_3b}"
CFG="configs/hf/${FAMILY}/run_0"

python src/main.py --cfg_file "${CFG}/esp_bc60_dynamic.yaml" \
  --set spec.block_complexity=30 \
  --save_name "ablation_tree_dynamic_bc30"
for b in "7,2" "5,4" "3,6"; do
  python src/main.py --cfg_file "${CFG}/esp_bc60_static.yaml" \
    --set "spec.tree.branches=[${b}]" \
    --save_name "ablation_tree_static_${b/,/x}_bc30"
done

python src/main.py --cfg_file "${CFG}/esp_bc60_dynamic.yaml" \
  --save_name "ablation_tree_dynamic_bc60"
for b in "15,4" "12,7" "10,9" "8,11" "6,13"; do
  python src/main.py --cfg_file "${CFG}/esp_bc60_static.yaml" \
    --set "spec.tree.branches=[${b}]" \
    --save_name "ablation_tree_static_${b/,/x}_bc60"
done
