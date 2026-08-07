#!/usr/bin/env bash
# Table 4: naive vs efficient tree-attention/PID construction at
# m1(30) [14], m1m2(30) [7,2], m1(60) [29], m1m2(60) [15,4].
# tau must be identical between impls; only wall time should differ.
#
#   bash scripts/run_ablation_impl.sh llama3_2_3b
set -euo pipefail
cd "$(dirname "$0")/.."

FAMILY="${1:-llama3_2_3b}"
CFG="configs/hf/${FAMILY}/run_0"

for impl in efficient naive; do
  python src/main.py --cfg_file "${CFG}/esp_bc30.yaml" \
    --set spec.impl="${impl}" \
    --save_name "ablation_impl_${impl}_m1_bc30"
  python src/main.py --cfg_file "${CFG}/esp_bc30.yaml" \
    --set spec.impl="${impl}" \
    --set "spec.tree.branches=[29]" \
    --save_name "ablation_impl_${impl}_m1_bc60"
  python src/main.py --cfg_file "${CFG}/esp_bc60_static.yaml" \
    --set spec.impl="${impl}" \
    --set "spec.tree.branches=[7,2]" \
    --save_name "ablation_impl_${impl}_m1m2_bc30"
  python src/main.py --cfg_file "${CFG}/esp_bc60_static.yaml" \
    --set spec.impl="${impl}" \
    --save_name "ablation_impl_${impl}_m1m2_bc60"
done
