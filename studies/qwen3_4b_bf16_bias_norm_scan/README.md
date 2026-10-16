# 4B BF16 bias magnitude scan

Plan: [Chinese](<../../docs/研究计划 Denoising Speculative Decoding.md#current-execution-20261016>) / [English](<../../docs/Research Plan Denoising Speculative Decoding.md#current-execution-20261016>). Immutable preregistration commit085722e and blob identity are in docs/source_refs.json; no standalone plan.

Eight new full480 cells, BC30/two masks/nine drafts: template/random0/random1/random2, each .5 and2 times native step_scale. Original zero and four1x cells are reused by their formal evidence SHA, not rerun. Direction construction reuses the existing control(), mean/update uses the native provider. Same480 token IDs, BF16/eager/T0/256/EOS/seed123, no prompt/template changes, content direction, Kalman or timing. Shared old AR is diagnostic; every new committed token must pass native verifier-argmax audit.

No concurrent GPU queue: after the8B independent-repeat queue exits naturally and frees the GPU, one native launch chain runs all eight in declaration order. Actual GPU nonpreemption and measured-host-peak+2GiB admission; first4B cell conservatively borrows the larger8B measured RSS/workset budget (explicitly not a4B measurement). Capacity sampling records real4B RSS. No automatic execution-failure retry, oldRun re-signing, weights/cache publication or data deletion.

Native prepare/execute/collect/summarize/write/process are retained. Readout reports three tau aggregations, paired accepted/calls/tau WTL versus own1x andzero, each random seed and their mean, lengths, acceptance by depth, first same-prefix block and actual initial bias/mean norms. Later path divergence does not establish fixed-prefix causality. No new numerical-operator chain.

## CPU preparation status

Nine CPU checks cover unchanged mean/fixed direction across0/.5/1/2, declared eight-cell order and immutable references, native tiny BF16 verifier-argmax at .5/2, refusal to claim an unmade scan complete, and first-block pairing that excludes changed prefill tokens or absent blocks. The readout verifies all reused raw files against their formal hashes; first-block comparisons include only equal original-input-plus-prefill prefixes and report exclusions. New curves are written only after all eight native cells and process pass.

This source preparation does not make/launch a Study. Auto-review rejected an early make during the live8B queue, so wait for that queue to exit naturally. Do not retry via another checkout or indirect runner. The active execution worktree retains its original prepared-copy snapshot until it is idle; any later source synchronization must preserve those local files before replacing them.

Linux CI initially reported521passed/2failed because Git normalized the imported resource_admission.py to LF while this Study pinned the active Windows CRLF hash. Preserve that helper's actual bytes with -text, leaving the recorded hash and code unchanged. Active8B files are read only and untouched; no native make or model forward is needed for this correction.
