#!/usr/bin/env bash
# EMA-velocity (ours) design-space sweep at BC=30 (single mask [14]).
# Three formulations of the extrapolation step (spec.ema):
#   1. raw vhat, gamma=1      — the meeting spec (ema_bc30.yaml default)
#   2. raw vhat, gamma swept  — magnitude keeps the confidence signal
#   3. normalized + gamma     — unit direction; gamma alone sets step length
#                               (in units of the EMA'd per-token diff norm)
# Plus: beta sweep and frozen-velocity. Open choices are flagged in
# lark_transcripts/summary_july31.md.
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

# Formulation 2: raw vhat scaled by gamma (gamma=1.0 run doubles as
# formulation 1, the ema_bc30 default).
for scale in 0.5 1.0 2.0; do
  python src/main.py --cfg_file "${CFG}/ema_bc30.yaml" \
    --set spec.ema.step_scale="${scale}" \
    --save_name "ema_ablation_scale${scale}_bc30"
done

# Formulation 3: unit direction; gamma = step length in typical-diff units.
for scale in 0.25 0.5 1.0 2.0; do
  python src/main.py --cfg_file "${CFG}/ema_bc30.yaml" \
    --set spec.ema.normalize=true \
    --set spec.ema.step_scale="${scale}" \
    --save_name "ema_ablation_norm_scale${scale}_bc30"
done

# Extrapolation behavior (needs >= 2 masks to differ): one shared vhat for
# all steps (extrapolate_ema=false) vs the EMA rolling forward through the
# extrapolation (true). Identical at gamma=1, so sweep at gamma=0.5 where
# the per-step trust decay bites. Uses the BC=60 two-mask static tree.
for xema in false true; do
  python src/main.py --cfg_file "${CFG}/ema_bc60.yaml" \
    --set spec.ema.step_scale=0.5 \
    --set spec.ema.extrapolate_ema="${xema}" \
    --save_name "ema_ablation_xema_${xema}_bc60"
  python src/main.py --cfg_file "${CFG}/ema_bc60.yaml" \
    --set spec.ema.normalize=true \
    --set spec.ema.step_scale=0.5 \
    --set spec.ema.extrapolate_ema="${xema}" \
    --save_name "ema_ablation_xema_${xema}_norm_bc60"
done

# Frozen velocity: prefill EMA only, no updates from generated tokens.
python src/main.py --cfg_file "${CFG}/ema_bc30.yaml" \
  --set spec.ema.update=false \
  --save_name "ema_ablation_update_off_bc30"
