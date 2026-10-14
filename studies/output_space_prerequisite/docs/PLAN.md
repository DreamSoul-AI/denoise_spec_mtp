# Output-space prerequisite Study Plan

## Question and scope

Extracted from research-plan-v6 sections 5.1–5.8/5.11 and E2/E3: can normalized final-hidden masks, conditioned on each draft prefix, use the existing simultaneous verifier without changing the greedy AR tokens? Compare output order0/order1 against frozen_mean and independent AR under the same two-slot chain. This is the first output-space numerical prerequisite, not a Kalman/full-paper or superiority test. Parameters are predeclared, never chosen by acceptance.

## Fixed protocol

Qwen/Qwen3-0.6B from the already downloaded ModelScope snapshot (same file hashes as input_mask_baseline), local_files_only=true; tied weights required and verified, no untied fallback. SpecBench q171 translation skip10/take1, first turn, nonthinking template; FP32/eager/CUDA, seed123, T0, budget100, stop_on_eos=true. Four cases: frozen_mean chain, output_order0 chain, output_order1 chain, independent AR; each n=1. New version output-space-q171-20261014-v1. Tree static [1,1], k=2, pruning=false, actual BC=9; this differs from the earlier BC30 single-slot tree, so those older accepted counts are not a matched comparison. Reuse q171 as the predeclared development prompt, not a new held-out accuracy sample.

Output state FP32: order0 anchor; order1 anchor plus velocity. Exact observation y: anchor=y, velocity=beta*v+(1-beta)*(y-old_anchor), beta=.9. Node proxy observation uses beta_prime=.99 (conservative fixed choice, not estimated), chain-end has no proxy and only predicts h+v. Each owner starts from a private simulation state; slot j uses anchor+(j-1)*v, gamma=rho=1. Prompt warms exact state in position order. Prefill still uses mean-input masks, produces root token and k normalized final-mask hiddens; no extra target forward. The exact state ends at last prompt hidden, not the generated root: root hidden is unavailable until next block. After verification, observe root and accepted nodes in order; bonus hidden is observed next round. Proxy source is the preceding accepted owner's mask rows. All owner masks are fixed before the forward. Mapping Phi(h)=mean row norm of input embedding table * h/||h||; zero/nonfinite norms fail. Model weights never update.

## Implementation mapping and evidence

Existing decoder/provider loop remains for old methods. Output provider in structure/algorithm handles state and per-owner content only; HFCausalLM exposes final-normalized hidden from a temporary final-norm hook with try/finally removal (no all-layer storage). Decoder requests it only for the new method; attention/position/tree/cache algorithms remain unchanged. Config API supports explicit spec, no new task/runner. Collect/summarize/write/process reuse current raw correctness/source/evidence gates. Tests verify hook equality/logits, cleanup, state math, owner separation, rejection/acceptance/KV, T0 and shared-seed sampled equality, unsupported untied/nonchain rejection. Existing36-cell strict baseline and full regression must remain equal.

Native make/launch/process/report, round1 single GPU; no concurrent experiment. Prior load/serial resource calibration establishes capacity for same model; sample the new decoder RSS/thread/I/O and device memory, do not claim exact allocator peak from sampling or speed ranking. Model/input/PLAN/source manifests freeze before make. New source never signs an old succeeded Run; historical input baseline remains immutable evidence and is not rerun. Any token mismatch, source/input drift, missing observation, OOM or gate failure stops expansion; preserve failures, change version for a corrected execution.

## Success and interpretation

Execution: all four new Run statuses succeeded. Quality: exact_match=1 for all three speculative cases and independent full AR IDs equal, Run+Study source/evidence/complete gates pass, final hidden hook test proven, state/owner/observed position trace valid. Record accepted/depth/calls/new/committed separately, no speed pass threshold. n=1 cannot show mechanism advantage or support H1–H13. No full matrix, untied mapping, general trees, order>=2, adaptive Kalman, tuning, concurrent/recovery validation, merge or release.

## Sources and reading

Local research v6 method/implementation sections read in full for this stage; fixed RPipe7a15c46 research.md read. Knowledge09078015 four research/PyTorch skill references and guides were read in prior stage; no installation/dependency added. Qwen downloaded config declares tie_word_embeddings=true; actual tensor storage equality is required. Local Transformers5.12.1 Qwen3Model/LlamaModel.forward norm->last_hidden_state inspected; validate against output_hidden_states[-1] on tiny. Official references: https://huggingface.co/Qwen/Qwen3-0.6B and https://docs.pytorch.org/docs/stable/generated/torch.nn.Module.html#torch.nn.Module.register_forward_hook . No novelty claim or new literature review asserted.
