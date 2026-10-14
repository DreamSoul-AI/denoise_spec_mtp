# q173 single-slot historical-proxy transfer plan

Predeclared 2026-10-14, before the three intervention replays. Version: output-space-q173-transfer-20261014-v1. Builds on the retained matrix, WINDOW_PLAN, SCALE_PLAN and post hoc structural diagnosis; it does not replace an original Run or add a formal acceptance cell.

## Question and fixed intervention

At saved root83, output0/1 owner0 slot0 vectors are identical. Their slot1 vectors have the same observed norm (about .92507) but cosine .99831766. Both original paths accept one draft at root84 and next visit root86. Only exchange the returned owner0 slot1 vector at root83 (zero-based indices [0,1]), using the saved opposite-order current_masks tensor. Leave all other vectors, committed state, logits, decoder, cache, gains and defaults intact. This tests whether a single earlier mask can propagate through proxy history to later candidates without a direct slot0 velocity term. It cannot isolate all earlier velocity history or establish a general method advantage.

Three serial cases, no additional selections or reruns for an unfavorable result:

| recipient | root83 slot1 donor | role |
| --- | --- | --- |
| output_order1 | saved output_order0 | one-to-zero transfer |
| output_order0 | saved output_order1 | zero-to-one transfer |
| output_order1 | saved output_order1 | original-value placebo |

Replay the unchanged SpecDecoder directly with a scoped provider patch, following existing tools/profile_cpu.py and window tools. Do not use the unchanged-window observer's baseline acceptance path for post-intervention seed ownership. Infer the preceding selected owner from actual root progress, then check against actual returned trace. Observe only predeclared roots83/84/86/94/97 if visited; a root skipped by a changed acceptance path is recorded as unvisited, not forced or silently substituted. Capture first-seed margin, actual seed source owner/position, incoming proxies/anchor/velocity, current masks and mask hidden rows. Report all three cases, including null and adverse effects. No search over seed, root, scale or donor.

## Bindings, budget and execution gates

Bind scientific source670c744e0535dcad, unchanged original execution_v1.json, original Run config/decode_inputs/decode_observations, WINDOW_PLAN and observer JSON, this PLAN, tool/helper hashes and selected_tensors SHA47166a3b41e0c00ed39110593fe7f83b20323c2e3714fe0355f2a43aaa9dc14c. Reuse the same locally prepared ModelScope Qwen3-0.6B 11-file snapshot, verify all hashes before/after, actual model digest and runtime equality. Tied model, FP32/eager/CUDA, unpruned static[1,1], k2/BC9, beta .9/beta_prime .99, T0/EOS, seed124, max_new_tokens100. No download, src or default recipe edit.

Budget at most three decoder generations x100 new tokens, no auxiliary teacher/prefix forwards and no warmup. Each generation must reproduce all saved independent-AR tokens (33 for this q173) without context shortening. Instrumentation forwards must equal1+actual decode_calls. Select the intervention call from the original root83 index; at actual forward assert it is root83 and exactly one provider call was modified. Before/through root83 verify full semantic verification/commit/KV trace and original root83 masks. Nonselected tensor coordinates must remain bit-identical, the replacement must equal its predeclared donor, and the patch/hooks must be restored even on failure. Placebo must reproduce original full tokens/semantic trace. Post-intervention semantic changes are permitted in the two transfer cases and must be retained.

Use a new .tmp/output-transfer-20261014-v1 output directory; refuse existing outputs. Preserve failed output and all earlier data, no push/merge/delete. Formal scalar JSON/report stays in this Study; local tensor payload stays ignored. Sample process-tree RSS/threads, device-global GPU memory, available RAM and I/O at .5s; these are approximate peaks with background occupancy, not allocator or speed rankings. Prior observed capacity is about6.1GB RSS and5.7GiB device-global GPU memory; serial execution only. Stop on binding/replay/ownership/scope gate failure, nonfinite tensor, OOM or resource failure; preserve failure and do not change contract to pass.

## Interpretation boundary

If an exchanged second slot changes the next proxy and subsequent first-seed direction/margin while the first seed at83 is unchanged, this supports a local historical propagation route. If only immediate proxy changes or the later94/97 margins/acceptances persist, record that this single early intervention does not explain those later gains. Neither outcome identifies all hidden mediation or the contribution of current velocity in later slots. No stable benefit, global EMA causal claim, new optimized default or performance ranking follows from this one q173 window.
