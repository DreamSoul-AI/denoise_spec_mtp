# Output-space small-matrix Study Plan

## Question and selection

Read the latest output_space_prerequisite report and offline_diagnosis before selecting this stage. q171 showed input-chain accepted17 versus output-order0/order1=10/10, despite different owner-mask statistics and identical output-order verification trajectories. Does this descriptive pattern persist on three further predeclared prompts, and at which matched committed-prefix positions do the greedy trajectories differ? This reuses the working implementation; not a mechanism/novelty/Kalman test.

Selected by contiguous dataset order, without observing new outputs: translation skip11/take3, question_id172,173,174; first turn German->English, nonthinking Qwen template. [Prompt manifest](prompts_manifest.json) freezes exact text/reference and dataset hash. q171 is excluded and its raw/source/PLAN remain untouched. n=3 prompt units, not three independent seed replicates or a held-out population sample.

## Fixed model/method/budget

Same ModelScope Qwen3-0.6B snapshot and 11 file hashes, actually tied weights, FP32/eager/CUDA, T0, EOS stop, max_new_tokens100 per prompt, max_prompt_len2048. Source670c744e0535dcad on local9ba5c3a, upstream7a15c46 v0.3.1, existing torch2.11.0+cu130/Transformers5.12.1 maintained. No algorithm/source changes. Native Run seed123; per-prompt generators use seed+index123/124/125 (T0 gives no sampling selection).

Four Experiments, one Run each with all three prompts: frozen_mean input chain, output_order0, output_order1, independent AR. All spec methods: unpruned static[1,1], k2, BC9, efficient, same prefill input mean. Output order1 beta=.9/beta_prime=.99/gamma=rho=1 and mean embedding-row-norm mapping unchanged. No tuning/sweep, adaptive Kalman, untied/general tree or full matrix. Measured output budget at most4*3*100=1200 new tokens, plus at most900 tokens for three per-prompt AR audits; existing warmup8 per case and internal audit remain, up to56 additional warmup tokens. No replacement of a low-acceptance prompt.

## Design, expected information and diagnosis

Report all per-prompt accepted/depth1/depth2/calls/new/committed and pooled sums. Quality passes only if each speculative output and its internal AR equal the independent AR under identical prompt IDs and full budget, with no context-limit shortening. Acceptance improvement is not a pass threshold. Preserve negative/zero/mixed observations, do not prefer the best case.

For each same-prompt pair (input/order0/order1), align trace rows by absolute root_position and verify cache_before and committed prefix are equal. Compare accepted-node lengths and committed segments at these common positions; list noncommon positions, which arise because different acceptance lengths skip different future roots. Do not compare step number across different generated-prefix positions. Compare output0/order1 owner-mask difference statistics at matched roots, but do not call this full vector/logit agreement. Missing draft probabilities, full mask vectors and exact/proxy-hidden pairs prevent causal attribution: any mechanism explanation remains a hypothesis. This stage narrows whether q171 was the only observed pattern before instrumenting heavier diagnostics.

## Execution, provenance and stop

New version output-space-q172-174-20261014-v1 and new Run IDs, separate Study. Freeze PLAN/prompt/model manifest/declarations/recipe/phase files and SpecMTP source before make; actual input/model/runtime evidence recorded by existing stages. Source/freeze/gate check before execution; same architecture/science code as the just-passed270tests/36 strict cells and wheel/sdist checks, so do not repeat those hardware experiments or alter code to create new evidence.

Native make --num-gpus1 --init-gpu0 --round1; launch same queue, then process/status/logs/report. Existing verified serial capacity of same model6GB device-global sampled peak guides round1; sample new process RSS/thread/I/O/device memory and available host RAM, distinguish heuristic est from measured Flow/launch wall. OMP/MKL1, no competing experiment. Any OOM/token mismatch/source drift/missing raw/gate failure stops expansion and preserves failed Run. Successful old IDs never re-signed; corrected execution must newversion.

## Completion and limits

Execution complete if four new Runs succeed. Quality if all12 prompt outputs, full AR equality, current source/input/Study gates and independent prompt identity mapping pass. Save per-prompt paired trajectory diagnosis with actual raw hashes, NUMBERS/report/chart and redraw tool. Formal selected evidence local; full raw/log/modelcache ignored. No push, PR merge, data deletion or publication.

Three contiguous prompts are a small feasibility/development matrix; not a generalization, significance or method-superiority result. Negative evidence can motivate a predeclared proxy-vs-exact hidden diagnostic, but does not license immediate large-scale runs, retuning or declaring all output-space methods ineffective.
