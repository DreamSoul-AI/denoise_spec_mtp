# Four-prompt extension and fixed single-slot intervention plan

Predeclared 2026-10-14 on parent7a02501. Version output-space-q175-178-20261014-v1. Same scientific source670c744e0535dcad, model/snapshot/default gains/decoder/sampler/cache. Existing native Study machinery and observe()/transfer()/compare_window() are reused. No code in scientific src is changed.

## Existing q173 evidence and hypotheses

Evidence sources: output_space_small_matrix/docs/trajectory_diagnosis.json, window_diagnosis_v1.json, transfer_diagnosis_v1.json, cross_prompt_diagnosis_v1.json and cross_prompt_path_v1.json. These are development observations, not independent confirmation. q173's 29 common output0/1 roots differ in acceptance only at94/97; q171's36, q172's12 and q174's11 have no output-order acceptance difference. Full q173 mask/logit measurements exist only at the prior five fixed transfer roots, not every earlier root.

| qid | intervention root | root minus input length | first common hit | output0/1 accepted | transplant vector L2 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 171 | 63 | 0 | 64 | 10/10 | .09785780 |
| 172 | 42 | 3 | 43 | 1/1 | .05879461 |
| 173 | 83 | 14 | 84 | 1/3 | .05366028 |
| 174 | 41 | 9 | 42 (terminal) | 1/1 | .06347270 |

Q173 did not have the largest injected vector difference, and late window position alone is insufficient (q174 terminates; q171 has more remaining roots but no hit transfer). At q17394/97, baseline order0/1 target margins have opposite signs, deltas about+4.00275/+5.11003. The order1<-order0 transplant removes both hits with same committed anchor/v at five measured roots; reverse order0<-order1 restores94 but not97. Q171/172 transfers change margins by at most.42729/.59764 without sign crossing, and all semantic trajectories remain equal. Q174 has no continuing owner1 propagation after EOS.

H1 (rank-boundary hypothesis): historical proxy perturbation can alter candidate directions without acceptance change; q173's local gain requires specific candidate rankings to cross the correct-target top1 boundary. Mere nonzero velocity, displacement amplitude or propagated seed difference is insufficient. In new prompts report natural baseline margin sign opposition at all common visited roots, and actual matched acceptance/sign changes after fixed transfers. Natural acceptance differences with no transfer would bound this single-entry sufficiency, not invalidate the T0 ranking identity.

H2 (owner-path history hypothesis): the first common accepted-owner transition allows the preceding second slot to influence later first-seed proxies. A donor-like first seed may persist along owner0-only blocks, while later accepted-owner transitions can mix it back into recipient-specific history/velocity; this could explain q173 reverse transfer restoring94 but not97. Measure actual source owners, donor-first-seed equality/L2 at common roots, and alignment of equality loss with subsequent accepted roots. This is observational mediation after one intervention, not an independent test of every intermediate slot; retain exceptions.

H3 (terminal/unused-owner boundary): if no continuing accepted-owner path uses the injected slot, a null acceptance result is expected and is not evidence against all historical effects. Explicitly classify terminal/no-shared-hit/unused-owner controls instead of combining them with continuing propagation cases.

These hypotheses were written before observing new q175–q178 outputs. Do not retune or pick another window after seeing new margins.

## Fixed new inputs and native matrix

Select contiguous next translation records, file order skip14/take4, q175/176/177/178. Freeze text, datasetSHA and independent tokenizer-rendered input IDs in prompts_manifest.json before make. Same locally prepared ModelScope Qwen3-0.6B 11-file snapshot, tied weights, FP32/eager/CUDA, nonthinking, T0/EOS, max_new_tokens100, unpruned static[1,1]/k2/BC9, beta.9/beta_prime.99. Seed123 with per-prompt generators123/124/125/126; these are four prompts, not stochastic seed replications.

Four native Experiments/Runs (input frozen mean, output0, output1, independent AR), each containing four prompts, new version/IDs. Run make/launch/process/report, round1 single GPU. Gate exact_match1, no context shortening, input/model/source/factor/provenance/raw/Study quality all pass. No warmup changes. At most1600 new tokens in native runs plus1200 internal AR-audit tokens and at most72 unchanged warmup tokens. Do not rerun already successful Run IDs or replace a null prompt.

## Predeclared transfer selection and diagnostics

For each prompt using native output0/1 semantic traces only: choose the earliest common acceptance root whose immediately preceding common visited root is rejected by both; intervene at that preceding root. If none, choose the earliest common root rejected by both that has a later root. If still none, choose the earliest common nonterminal root and label unused-owner control. If no continuing common root exists, report no feasible slot-use window rather than replace the prompt. This is an explicitly planned fallback, not hidden selection by logits.

Freeze the resulting root/selection reason and complete union of all baseline roots at/after it in window_selection_v1.json before any hidden/margin observation. Each original-order observation captures only targets it actually visits; changed paths in transfers retain unvisited/new roots. No forced baseline owner or extra window search. Intervene only once at owner0 second slot[0,1]. Cross-order first-slot equality is measured, not a universal requirement; recipient first seed and all unselected tensor coordinates must remain unchanged at the intervention.

Two unchanged baseline observations plus order1<-order0, order0<-order1 and order1 original-value placebo for each feasible prompt, using frozen donor tensors. Budget at most20 diagnostic generations x100=2000 new tokens, no teacher/isolated-prefix/warmup forwards. Existing observe/transfer restore hooks/provider on failure and require unchanged baseline/placebo semantic paths, correct actual seed owner, only selected coordinate replaced, unchanged pre/through-intervention semantic trace and complete independent-AR tokens. Post-intervention semantic changes are retained, not rejected merely because a hit appears/disappears. Record per-root margin/state and all losses/gains, including changed/noncommon paths. Compare anchor/v with recipient at all matched roots, report bit/L2 differences rather than assume equality; zero-order velocity remains0.

Bind source/model/snapshot/runtime, native inputs/config/raw, original execution JSON, this PLAN, frozen selection, runner and unchanged helpers before/after. Stop on source drift, hash/token/scope/ownership/nonfinite/OOM/gate failure and preserve it, without swapping prompts, re-signing old outputs or tuning defaults. New .tmp/extension-native-20261014 and .tmp/extension-transfer-20261014-v1 hold local logs/tensors. Formal scalar/full-trace JSON and reports live here; do not export weights/raw tensors.

## Capacity and completion

Same-model prior sampled RSS~6.1GB/device-global~5.8GiB guides serial capacity. OMP/MKL1, single GPU, no competing launch chain. Sample process-tree RSS/threads/IO, device-global memory and available RAM at.5s. Record actual wall times; heuristic make est is separate and observer synchronization precludes performance ranking. No full matrix or concurrency experiment.

Complete when four native Runs and available fixed transfers pass correctness/scope/provenance, all four prompt outcomes including unfeasible/negative cases and hypothesis boundaries are in STUDY_REPORT with a small combined matrix, and appropriate tests/static/docs checks/local commit are done. No pushes/merges/deletions. These eight accumulated development prompts (q171–q178) remain a small nonrandom sample, not significance or universal EMA attribution.
