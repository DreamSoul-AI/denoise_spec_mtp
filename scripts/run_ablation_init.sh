#!/usr/bin/env bash
# Table 5: mask-token initialization strategies (Last K / Sample / Mean) at
# m1(10), m1(30), m1m2(60 static [15,4]) for a LLaMA family.
#
#   bash scripts/run_ablation_init.sh llama3_2_3b
#   bash scripts/run_ablation_init.sh llama3_1_8b
set -euo pipefail
cd "$(dirname "$0")/.."

FAMILY="${1:-llama3_2_3b}"
CFG="configs/hf/${FAMILY}/run_0"

for init in last_k sample_embedding mean_prompt; do
  python src/main.py --cfg_file "${CFG}/esp_bc10.yaml" \
    --set spec.mask.init="${init}" \
    --save_name "ablation_init_${init}_m1_bc10"
  python src/main.py --cfg_file "${CFG}/esp_bc30.yaml" \
    --set spec.mask.init="${init}" \
    --save_name "ablation_init_${init}_m1_bc30"
  python src/main.py --cfg_file "${CFG}/esp_bc60_static.yaml" \
    --set spec.mask.init="${init}" \
    --save_name "ablation_init_${init}_m1m2_bc60"
done

# Appendix G.8: out-of-distribution init mu + {5,10} sigma at BC=60.
for scale in 5.0 10.0; do
  python src/main.py --cfg_file "${CFG}/esp_bc60_static.yaml" \
    --set spec.mask.init=offset_embedding \
    --set spec.mask.offset_scale="${scale}" \
    --save_name "ablation_init_offset${scale%%.*}_bc60"
done
