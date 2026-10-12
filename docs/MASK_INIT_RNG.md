# sample_embedding mask init and the sampling RNG (branch `fix/mask-init-rng`)

**Status: separate branch, not merged into `refactor/rpipe-dependency`.** Needs a decision.

## Problem

`mask.init: sample_embedding` (Table 5 "Sample") draws `m_i ~ N(mu, sigma^2)` from the same `torch.Generator` that `SpecDecoder` uses to sample tokens. `ar_generate` has no such draw. At temperature > 0 the speculative token stream is therefore shifted by `k × d` normal draws against the AR reference, and `exact_match = 0` although the sampling distribution is correct. At temperature 0 the generator is not used for tokens and the outputs match. Found by the property tests on 2026-10-12.

## Change

`SpecDecoder.generate` gives the mask provider `_fork_generator(self.generator)`: a new Generator with the sampling generator's **current state**. So

- the mask noise is exactly what the shared generator would have produced (same masks, checked in `test_sample_init_noise_is_unchanged_by_the_fork`);
- the sampling generator is not consumed, so token sampling sees the same stream as `ar_generate`.

No other provider draws from the generator, so nothing else changes.

## Effect (measured with `tools/decode_fingerprint.py`, 555 cells)

- Changed: only `init_sample_bc30` at temperature > 0 (9 of 555 cells): tokens, `accepted`, `committed`, `decode_calls`, `tau`, depth counts. All of them now equal AR (`exact_match = 1`; context-limited cells equal AR at the reached budget).
- Unchanged: every other preset at every temperature, and `init_sample_bc30` at temperature 0 (masks identical, tokens identical).
- paper_hf dry run: all 59 Runs identical (the paper runs this ablation at temperature 0).
- Recorded results: history_extrapolation never used `sample_embedding`; nothing to rerun.

## Meaning of the numbers

Before, a T>0 `init_sample` run sampled from the right distribution but with a stream that cannot be audited against AR; its accept counts are one valid sample, not comparable token-for-token. After, the run is auditable and its stream matches the other presets' streams for the same seed. Accept statistics at T>0 for this preset change from one random draw to another; any T>0 `init_sample` numbers produced before this change are not reproducible by this branch (none are recorded in the repo).
