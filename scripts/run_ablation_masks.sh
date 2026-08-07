#!/usr/bin/env bash
# Table 3 + Appendix G.4: number of mask tokens.
#   BC=60:  [29] (m1) / [15,4] (m1,m2) / [7,5,3] (m1,m2,m3; paper-literal)
#   G.4:    BC=30 [14] (m1) -> BC=60 [15,4] -> BC=120 [15,10,4]
#
#   bash scripts/run_ablation_masks.sh llama3_2_3b
set -euo pipefail
cd "$(dirname "$0")/.."

FAMILY="${1:-llama3_2_3b}"
CFG="configs/hf/${FAMILY}/run_0"

python src/main.py --cfg_file "${CFG}/esp_bc30.yaml" \
  --set "spec.tree.branches=[29]" \
  --save_name "ablation_masks1_bc60"
python src/main.py --cfg_file "${CFG}/esp_bc60_static.yaml" \
  --save_name "ablation_masks2_bc60"
python src/main.py --cfg_file "${CFG}/esp_bc60_static.yaml" \
  --set spec.num_masks=3 \
  --set "spec.tree.branches=[7,5,3]" \
  --save_name "ablation_masks3_bc60"

python src/main.py --cfg_file "${CFG}/esp_bc60_static.yaml" \
  --set spec.num_masks=3 \
  --set "spec.tree.branches=[15,10,4]" \
  --save_name "ablation_masks3_bc120"
