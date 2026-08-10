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
  - `step_scale` (default 1.0) — gamma, extrapolation step size
  - `normalize` (default false) — formulation switch, see below
  - `update` (default true) — fold generated-token diffs into vhat;
    `false` freezes the prefill velocity

Three formulations of the extrapolation step, switchable in YAML:

| # | `normalize` | `step_scale` | mask formula | reading |
|---|---|---|---|---|
| 1 | false | 1.0 | `m_i = e_last + i*vhat` | meeting spec; \|\|vhat\|\| doubles as confidence (scattered history -> small step) |
| 2 | false | gamma | `m_i = e_last + gamma*i*vhat` | shrink/stretch: gamma is the regression / trust-region coefficient; gamma=1/(1-beta) recovers raw-momentum semantics |
| 3 | true | gamma | `m_i = e_last + gamma*i*r*vhat/\|\|vhat\|\|` | unit direction: confidence signal removed, gamma alone sets step length in units of r = EMA of per-token diff norms (dimensionless, model-agnostic); \|\|vhat\|\|~0 collapses to the anchor |

Comparing 1/2 vs 3 tests whether vhat's data-dependent magnitude helps
(adaptive confidence) or hurts (outlier diffs inflating the step).
`scripts/run_ema_ablations.sh` sweeps all three.

Orthogonal extrapolation switch (`extrapolate_ema`, needs >= 2 masks to
matter):

| value | behavior |
|---|---|
| `false` (default) | every step extrapolates with the same vhat: `m_i = anchor + i*step`. Exact closed form of iterated extrapolate-and-fold at gamma=1 (folding the extrapolated diff into the EMA is a fixed point). |
| `true` | the EMA rolls forward through the k extrapolation steps: each realized step is folded into (vhat, r) before the next. Equals `false` at gamma=1; at gamma != 1 the per-step size scales geometrically by `rho = beta + (1-beta)*gamma` — a smooth depth-decaying (gamma<1) or growing (gamma>1) trust schedule. Within-block simulation only; committed-token state is untouched. |

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
