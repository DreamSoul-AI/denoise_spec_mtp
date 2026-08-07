# EMA-Velocity Masks (ours)

Proposed by 刁恩茂 in the 2026-07-24 call
([lark_transcripts/summary_july31.md](../lark_transcripts/summary_july31.md)):
replace ESP's mask-token init/update (Equations 4 and 5) with an explicit
velocity extrapolation, keep **everything else identical** — tree, pruning,
block complexity, verification.

## Motivation

ESP's update rule `m += λ(e_last − m)` is an EMA whose step direction is
"next token minus current mask" — under the flow-matching view of
autoregression, a *velocity*. ESP found this by trial and error; the mean-of-
prompt init is "almost, but not exactly, an EMA" and never uses the gradient
information already present in the prefill. Making the velocity explicit:

```
v_j    = e_{j+1} − e_j                      consecutive prompt-embedding diffs
vhat   = EMA_beta(v_1 .. v_{t−1})           biased, variance-reduced estimate
m_i    = e_last + step_scale · i · vhat     mask i extrapolates i steps
vhat  ← beta·vhat + (1−beta)(e_new − e_prev)   per committed token
```

Momentum tradeoff: the EMA is biased but variance-reduced (same argument as
momentum SGD). Folding an extrapolated step back into the EMA is a fixed
point, so within a block the masks are exactly linear in `i`.

## Code

- `src/spec/mask_providers.py::EMAVelocityMaskProvider`
- selected with `spec.method: ema_velocity`; knobs under `spec.ema:`
  - `beta` (default 0.9) — EMA decay over differences
  - `step_scale` (default 1.0) — extrapolation step size
  - `update` (default true) — fold generated-token diffs into vhat;
    `false` freezes the prefill velocity

## Open design choices (flagged in the call, not settled)

- differences are taken in the **input embedding space** to match ESP's
  probing space (mid-layer latents are the longer-term target);
- `beta` and `step_scale` have no theory — sweep via
  `scripts/run_ema_ablations.sh`;
- no non-linearity correction (Jason's GPT-variant #2 adjusted direction
  when the local trajectory bends; pure EMA does not).

## Success criterion

Beat the matched ESP config (`esp_bc*` vs `ema_bc*`) on SpecBench tau by any
margin at BC = 10/30/60 ("只要比他们效果好一点点，就已经很不错了"), then
either add theory or fine-tune a better velocity estimator.
