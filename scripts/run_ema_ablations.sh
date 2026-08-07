#!/usr/bin/env bash
# EMA-velocity (ours) design-space sweep at BC=30 (single mask [14]):
#   beta in {0.5, 0.9, 0.99}, step_scale in {0.5, 1.0, 2.0}, update off.
# The open choices are flagged in lark_transcripts/summary_july31.md.
#
#   bash scripts/run_ema_ablations.sh llama3_2_3b
set -euo pipefail
cd "$(dirname "$0")/.."

FAMILY="${1:-llama3_2_3b}"
CFG="configs/hf/${FAMILY}/run_0"

for beta in 0.5 0.9 0.99; do
  python src/main.py --cfg_file "${CFG}/ema_bc30.yaml" \
    --set spec.ema.beta="${beta}" \
    --save_name "ema_ablation_beta${beta}_bc30"
done

for scale in 0.5 1.0 2.0; do
  python src/main.py --cfg_file "${CFG}/ema_bc30.yaml" \
    --set spec.ema.step_scale="${scale}" \
    --save_name "ema_ablation_scale${scale}_bc30"
done

# Frozen velocity: prefill EMA only, no updates from generated tokens.
python src/main.py --cfg_file "${CFG}/ema_bc30.yaml" \
  --set spec.ema.update=false \
  --save_name "ema_ablation_update_off_bc30"
