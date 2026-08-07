#!/usr/bin/env bash
# Table 13: tree pruner on/off at m1(10), m1(30), m1m2(30 [7,2]),
# m1m2(60 [15,4]).
#
#   bash scripts/run_ablation_pruner.sh llama3_2_3b
set -euo pipefail
cd "$(dirname "$0")/.."

FAMILY="${1:-llama3_2_3b}"
CFG="configs/hf/${FAMILY}/run_0"

for pruning in true false; do
  python src/main.py --cfg_file "${CFG}/esp_bc10.yaml" \
    --set spec.tree.pruning="${pruning}" \
    --save_name "ablation_pruner_${pruning}_m1_bc10"
  python src/main.py --cfg_file "${CFG}/esp_bc30.yaml" \
    --set spec.tree.pruning="${pruning}" \
    --save_name "ablation_pruner_${pruning}_m1_bc30"
  python src/main.py --cfg_file "${CFG}/esp_bc60_static.yaml" \
    --set "spec.tree.branches=[7,2]" \
    --set spec.tree.pruning="${pruning}" \
    --save_name "ablation_pruner_${pruning}_m1m2_bc30"
  python src/main.py --cfg_file "${CFG}/esp_bc60_static.yaml" \
    --set spec.tree.pruning="${pruning}" \
    --save_name "ablation_pruner_${pruning}_m1m2_bc60"
done
