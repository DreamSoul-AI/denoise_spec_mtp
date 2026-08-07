#!/usr/bin/env bash
# Appendix G.9: mask update rate lambda in {0.01, 0.1, 0.5} at BC=30 and
# BC=60, plus the frozen-mask extra ablation (update=false).
#
#   bash scripts/run_ablation_lambda.sh llama3_2_3b
set -euo pipefail
cd "$(dirname "$0")/.."

FAMILY="${1:-llama3_2_3b}"
CFG="configs/hf/${FAMILY}/run_0"

for lam in 0.01 0.1 0.5; do
  python src/main.py --cfg_file "${CFG}/esp_bc30.yaml" \
    --set spec.mask.lam="${lam}" \
    --save_name "ablation_lam${lam}_bc30"
  python src/main.py --cfg_file "${CFG}/esp_bc60_static.yaml" \
    --set spec.mask.lam="${lam}" \
    --save_name "ablation_lam${lam}_bc60"
done

python src/main.py --cfg_file "${CFG}/esp_bc30.yaml" \
  --set spec.mask.update=false \
  --save_name "ablation_update_off_bc30"
