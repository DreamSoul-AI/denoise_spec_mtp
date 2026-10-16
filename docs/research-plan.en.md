# SD research plan: fixed-data reproduction and mask-direction controls

English translation of the [Chinese master](research-plan.md), updated 2026-10-16. The Chinese version governs. This plan follows the [new standard and template](research/standards/README.md), pinned to RPipe commit `e461133218deabf8755b3e8657650e1e4a3cd9f4`, already merged into its dev branch. It organizes existing research and evidence; it does not retroactively preregister experiments whose results have been seen, or change frozen Study contracts.

## I. Inspiration and initial questions

This is reproduction research and a comparison under fixed conditions. Earlier local 4B FP32 observations motivated testing output-space extrapolation. The full480 4B BF16 comparison instead found output orders0/1 weaker than input order1. That discrepancy, rather than an established output-space advantage, motivates the current questions; see the [stage report](research/sd-stage-report-2026-10-15.md).

The current highest priority is R1: the ESP Table1 tau gap and the sources of demonstrated local gains, using existing evidence for CPU accounting and protocol reconciliation. The five-method and six-direction comparisons are complete background evidence; further fixed-bias, random-direction and Kalman research is deferred. Literature defines the comparison and alternatives before evidence is interpreted. Historical proposals do not establish novelty, feasibility or permission to implement new methods.

Current status: the five-method plus AR matrix and all six BC30 direction cells are complete and accepted. The five new paths audit405,073 tokens, or485,860 including reused zero, all passing the verifier-argmax gate. The 8B self-implementation missed the paper targets; an author-official executable entry remains unverified; the nonofficial third-party precheck failed. Plan PR23 is merged into dev; [PR22](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/22) delivers the [final report](research/4b-full-direction-controls-2026-10-16.md) and evidence. No directionBC60 extension is scheduled this round.

The GPU experiment and PR22/23 closeout are complete; current work is limited to CPU reconciliation of existing evidence, documentation and branch hygiene. Enmao now prioritizes GPU access for official ESP Table1/8B steps once a verified author entrypoint and actual nonpreemptive admission are available. The entrypoint is still missing; the latest GPU snapshot is idle, with no experiment Python present; see the [launch-readiness record](research/esp-official-launch-readiness-2026-10-16.md). Priority authorization does not turn self-written or failed third-party code into official code, or authorize other new SD experiments. One shared24GB GPU, nonpreemptive access, fixed prompts and no timing are retained. New research owners, deadlines and budgets remain unassigned. [Historical v6](research/research-plan-v6.md), including Kalman, higher orders and untied mappings, is retained as an exploratory record, outside current execution.

## II. Literature review

This is a targeted evidence update, not a systematic review or a rereading of all60 historical references. Information cutoff and this round's checks are dated2026-10-16. Sources are arXiv originals/abstracts, the official Spec-Bench repository, prior source audits and result files. Foundational references were followed from v6; the actual search “SpecBench official github hemingxia Spec-Bench” identified the current official entry `hemingkx/Spec-Bench`. Future checks may use training-free multi-token prediction, embedding-space probing, speculative verification, dynamic draft tree and mask initialization; this search scope does not authorize new experiments.

Include relevant author papers, official data/code sources and the user-specified third-party implementation. Different models, precision, trees, training-based drafters or datasets provide context, not a fair local ranking. Exclude unsupported aggregate numbers, marketing summaries and unrelated method expansion. Failure to verify official code does not prove it was never released. Discovery, reading depth, author claims, code audit and execution evidence are recorded separately.

| Source and location | Question and actual reading depth | Data/model | Algorithm | Metrics/conditions | Evidence, limits and use |
| --- | --- | --- | --- | --- | --- |
| [ESP v2](https://arxiv.org/html/2603.17942v2), §3, Table1, Appendix G.2 | Abstract, Eq4/5, Table1 and appendix locations checked this round; earlier relevant-text analysis in the [reproduction plan](research/esp-table1-bf16-reproduction-plan.md) | SpecBench; local8B reproduction cells | Embedding masks, dynamic tree, pruning | Targets in SectionVIII; paper timing is not a deliverable here | Closest baseline; distinguish paper, author implementation, self-implementation and third party. Local failure is not proof the original method fails |
| [Leviathan et al.,2211.17192v2](https://arxiv.org/abs/2211.17192v2) | Abstract checked; sampling proof not re-proved here | Original Transformer conditions, not our4B matrix | Speculative decoding and target verification | Original sampling differs from this T0 study | Separates drafting/verification responsibilities; our same-forward argmax audit does not establish every sampling distribution |
| [Chen et al.,2302.01318](https://arxiv.org/abs/2302.01318) | Abstract checked | Author models/sampling, not pooled with local results | Speculative sampling | Not a local T0 comparison | Correctness/sampling context; no new sampling experiment |
| [EAGLE-2,2406.16858v2](https://arxiv.org/abs/2406.16858v2) | Abstract checked for dynamic-tree motivation | Author trained-drafter setting | Dynamic draft trees | Different from training-free masks | Context dependence is an alternative explanation; no local baseline run is claimed |
| [Medusa,2401.10774](https://arxiv.org/abs/2401.10774) | Abstract checked for the multihead route | Author model plus prediction heads | Multi-token heads | No matched local measurement | Records a trained alternative; training-free does not imply immunity to distribution bias |
| [Official Spec-Bench](https://github.com/hemingkx/Spec-Bench), data/spec_bench and Readme | Official repository description checked; actual category counts computed from frozen manifest | Original480 inputs,13 local categories | Evaluation platform/data source |480 inputs are not independent direction draws | Repository shows Apache-2.0; this is not a separate audit of every constituent dataset's terms |
| [Specified HF source and audit](research/esp-third-party-reproduction-2026-10-15.md) | Existing source/API and real mathematical audit reviewed through its report | Originalq121,8B BF16, three precheck budgets | Unchanged third-party API, not author official; CLI conditions differ | Six forwards, first-token gate failure, no validτ | Attempt stopped; neither official nor full480 reproduction, and no algorithm repair/new method |

The selected route remains the existing frozen-model mask comparison, with narrower claims about output-space superiority and a unique template direction. Future Lens, LatentMAS, smoothing and Kalman references in v6 remain historical leads: all underlying texts, theorem assumptions and novelty claims were not rechecked here. Literature claims about losslessness or throughput do not replace the project's actual gate or its no-timing boundary.

## III. Research questions and hypotheses

| Question/hypothesis | Conditions and falsifiable observation | Current assessment and next evidence |
| --- | --- | --- |
| R1 (highest priority): do8B paperτ values reproduce? | Compare the principal Table1 targets under Qwen3 single-mask settings; a material gap is not a successful numerical reproduction | Self-implementation gap, unverified author entry point, failed third-party precheck; not evidence the original ESP method is ineffective |
| H1 (completed/archived): output orders0/1 outperform input order1 here | Same480,4B BF16, budget/tree/stopping; both outputs weaker overall fails to support H1 | Full main matrix does not support H1; the output velocity term lacks stable joint benefit; see SectionIX |
| H2 (archived/deferred): gains require the specific e2−e1 direction | Random directions with clear gains contradict the word “only”; failure of all three would merely be compatible with that explanation | All three predetermined random cells beat zero; random2 also beats template. This does not show arbitrary directions work |
| R2 (archived/deferred): how does content initialization behave? | Preserve original inputs and full-prompt mean, changing only the native velocity-initialization suffix | Full480 content is complete: pooled tau1.364829262 versus zero1.422420206. Its norm is not separately matched, so this is not a pure direction-effect comparison |

The contribution sought is traceable reproduction boundaries and comparisons of existing methods/specified controls, not a new algorithm or universal optimum. Literature motivates the route; data/model bound inference; algorithm choices define treatments; metrics and paired experiments test the questions. β, state definitions, output paths and norms remain confounders: input/output differences are not attributable solely to the choice of space.

Current CPU findings: single-mask BC30/60 remain0.066622/0.092699 below the paper. Prompt-average or six-source equal weighting still misses the targets; end-clipping accounting contributes only0.002248/0.003039. Author task counts and a complete protocol are missing, so the gap cannot be uniquely attributed. See the [gap report](research/esp-table1-gap-analysis-2026-10-16.md).

## IV. Data

Retain existing `datasets/spec_bench/question.jsonl` from the official Spec-Bench project, without replacing it with a fresh upstream download. SHA-256 is `7dd26882f31ada100c2aa7447019b5349bddc55697021acbc5643fdc8740aa21`. Source, input IDs, EOS and order contracts are in the [4B prompts manifest](../studies/qwen3_4b_bf16_five_methods/docs/prompts_manifest.json). The historical immutable upstream commit is not independently confirmed; current GitHub HEAD does not substitute for it. Constituent-license and pretraining-contamination audits are incomplete.

The unit is one original first-turn prompt,480 total in original order, first/last question_id121/90. math_reasoning, qa, rag, summarization and translation each contain80; coding, extraction, humanities, math, reasoning, roleplay, stem and writing each contain10:13 categories. Preserve the original non-thinking chat template, all questions and stopping rules; no rewriting, truncation or template tuning. The original4B precheck records a maximum input length1500. Pair all480 and retain category results.

There is no training/fitting split. This frozen evaluation set has been repeatedly inspected; it is not a fresh independent holdout for selecting the best direction seed. Full duplicate/contamination identification has not been done. Every Run checks identities, order, input IDs, model content and stopping settings; tokenizer IDs are not exchanged across models without verification. Raw tokens/traces, full Runs, weights and caches remain local. Git holds manifests, summaries and evidence links.

## V. Models

Use existing ModelScope `Qwen/Qwen3-4B`: qwen3,36 layers, hidden size2560, vocabulary151936. Each Run checks actual tied input/output storage rather than trusting the configuration. Inputs are frozen IDs and masks; outputs are target logits, final hidden states and committed tokens. Weights, forwards and final masks use BF16/eager/T0. Native output-EMA/norm internal FP32 states are retained: this is not a claim that every internal calculation is BF16, or an additional FP32-model experiment.

See [modelscope_snapshot](../studies/qwen3_4b_bf16_five_methods/docs/modelscope_snapshot.json) and the [paired evidence](../studies/qwen3_4b_bf16_five_methods/docs/paired_evidence_v1.json) for actual dtype, tied storage, model_digest and runtime. Fourteen model-file contents have been checked; historical remote revision identity remains incomplete. Weight licensing was not reverified this round and is Unverified, not inherited from this repository's license. Recorded environment is torch2.11.0+cu130, Transformers5.12.1 and RTX5090 D v2; finer details are Run-owned. Installation pins verified Transformers5.12.1; it does not adapt5.20's new cache API or replace the running environment.

Qwen3-8B belongs only to the ESP Table1 reproduction. 0.6B and4B FP32 remain separate historical archives. Weights, tree and stopping rules are fixed within a budget. Only the five existing methods or requested controls vary; no additional trained drafter is introduced.

## VI. Algorithms

Reuse [SpecMTP](../src/spec_mtp/structure/algorithm/) and the native RPipe Study lifecycle, without another experiment framework. These are the actual local definitions: the user-defined frozen-mean ESP baseline is distinct from the paper's updating mean.

| Existing method | Mask/state definition | Fixed parameters and boundary |
| --- | --- | --- |
| ESP frozen mean | Original prompt embedding mean, frozen throughout generation | `update=false`; user-specified baseline |
| Input order0 | Full prompt mean, then `mean ← mean + λ(e−mean)` on commits | λ=0.1; updating mean; the direction-control zero cell reuses it |
| Input order1 | `mask_j = mean + γ j v`; native EMA of embedding differences updates v | β=0.9999,γ=1,λ=0.1,order0 level; normalize/extrapolate_ema disabled |
| Output order0 | Native final-normalized hidden/proxy state predicts u; mask is `r u/‖u‖`, with r the mean vocabulary-embedding norm | order0; existing owner/history semantics; no inverse embedding map |
| Output order1 | Add native EMA velocity to the same hidden prediction, then apply the same norm mapping | order1,β=0.9,proxyβ′=0.99; other state definitions are not identical to input order1 |
| Independent AR | Tokenwise greedy generation with the same model, inputs, seed and stops | One shared480 reference, not repeated inside every Spec Run |

Tied models use no inverse mapping. Native proxy updates follow root/candidate owners and accepted history, without teacher correction or extra verification forwards. Tree/pruning, KV cache, bonus and EOS/length clipping remain native. Accepted counts are before clipping; committed counts reflect actual clipping. No training loss, gradients or hyperparameter optimization is introduced. Full actual settings are recorded in each evidence cell.

Requested controls change only input velocity construction: template fixes `v=e2−e1`; random0/1/2 use independent CPU Generator seeds0/1/2, normalize a random vector in FP32 to the same prompt-template-difference norm, cast to BF16 and keep v fixed during generation; zero sets v=0. Content initializes the original EMA on the suffix starting at the first user-content token, preserves the full-prompt mean and continues native updates. That suffix includes the original trailing template; inputs are unchanged and its norm is not separately matched. Fixed template is not native input_first, which keeps updating velocity.

Current ESP full480 and five-method results are local self-implementations/extensions, not author-code reproductions. The specified HF dataset `Harshvardhan-Mestha/esp-reproduction-artifacts` is pinned to `ad76f8da29f3bfc7faa20488193c6aa83a9f708c`; eight original files are retained in [reference/ORIGIN](../src/spec_mtp/structure/algorithm/reference/esp_reproduction_artifacts/ORIGIN.json). Its missing LICENSE remains Unverified. The external audit called the unchanged native API, not the CLI; deviations and failure are in the [third-party report](research/esp-third-party-reproduction-2026-10-15.md). It is not repaired into a new baseline.

Configuration/source changes require a new Study version/Run; successful historical Runs are not re-signed. Direction protocol `fe59d35` and recovery protocol `0e7c46f` are in [PR22](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/22). Recovery changes only real-GPU resource refusal into same-Run waiting at prompt boundaries. Original failures and105 complete prompt-executions of wasted work are retained, never stitched into a valid480.

## VII. Metrics

| Role | Definition, unit and direction | Aggregation | Implementation/criterion |
| --- | --- | --- | --- |
| Primary pooledτ | Σdecode committed / Σdecode calls, tokens/decode call, higher is better | All480; excludes prefill's first token | Native raw plus shared CPU readout; report each predetermined budget without choosing the favorable aggregation |
| Two supplementary aggregates | Equal prompt-meanτ; equal mean of13 category-pooledτ values | Both separate from pooledτ | Recomputed from the same result; not asserted to be the paper's task weighting |
| Accepted/main calls | Higher accepted is better; fewer prefill+decode calls is better | Separate per-qid W/T/L and total deltas | No forced joint winner; different output paths/lengths are not equal-output speedups |
| Paired promptτ | Integer cross-products compare two ratios exactly | Directions versus template and existing five methods | Matching480 identities/order required; retain all losses |
| Hard correctness gate | Every committed token equals the correct-owner argmax of that verification forward, including prefill | Full token coverage plus owner/hash chains | All must pass; source, nonfinite, count or owner failures cannot be replaced by AR diagnostics |
| AR diagnostics | Whole-sequence exact rate, each first divergence, output length | One shared independent AR reference | Reporting only; no native summarize/process blocker or operator-level numerical study |
| Resource work | Model calls, committed tokens, work consumed by failed cells | Successful and failed work separate | Scheduling/BC60 decisions, not latency/throughput; zero timing fields are placeholders |

Every number identifies a file, cell and Run. Author values, local measurements and unmeasured items are distinct. No retrospective significance threshold or numerical “acceptable gap” is invented. The T0 same-forward audit does not establish arbitrary-temperature distributional equivalence or token equality across independent forward shapes.

## VIII. Experimental design and order

| Experiment/question | Controls/treatments | Fixed conditions/repeats | Budget, state and interpretation |
| --- | --- | --- | --- |
| E1: ESP Table1 source and numbers | Author-source check, self-implementation reference and specified third-party precheck separated |8B BF16/T0, original480; primaryBC10/1,30/1,60/1; supplementary60/2; λ0.1 updating mean | Four self-implementation cells completed but miss targets; author entry unverified; third-party stopped after precheck failure; no new8B queue |
| E2: five methods plus AR | Six definitions share inputs; compare five masks withinBC30/60 |4B BF16/T0; two masks, naive dynamic/pruned tree, draft budgets9/19; seed123+index; max_new_tokens256/EOS; default reduction | One shared AR plus10 Spec Runs:5280 prompt-executions but only480 evaluation inputs;11/11 accepted |
| E3: requested full480 directions | Template,random0/1/2,zero,content; versus template and the five methods | E2 BC30 conditions; mean/tree/stops/inputs fixed; direction seeds predetermined, decoder seed unchanged | Five new full paths plus reused zero:2400 valid new prompt-executions; all six cells complete; recovery native process passed |
| E4: evidence/document integration | CPU recomputation, provenance/bounds, bilingual plan, PR/dev integration | Same raw data and existing tools; preserve successful/failed cells | No additional GPU matrix; formal E3 readout/plot/report complete; no directionBC60 this round, with reasons in the final report |

### A. Baseline reproduction and follow-up

See the [author-source check](research/esp-official-code-reproduction-2026-10-15.md), [8B execution evidence](../studies/esp_table1_bf16_full_argmax/docs/protocol_evidence_v1.json) and third-party report. No verified executable author entry is available; an arbitrary similarly named repository is not a substitute. If an author version is obtained later, align its data/model/native entry within Enmao's scope and disclose adaptations. Template adoption does not automatically launch8B again.

| Condition | Planned target/source | Local measurement/source | Gap/assessment |
| --- | --- | --- | --- |
|8B BC10/1 | Additional user-requested budget; no invented Table1 target |τ1.399047, protocol_evidence `cells` | Mathematical gate passes; no corresponding Table1 target delta |
|8B BC30/1 | Table1τ1.63 |τ1.563378, same file |−0.066622; self-implementation misses the main target |
|8B BC60/1 | Table1τ1.74; Qwen3 single mask follows AppendixG.2 |τ1.647301, same file |−0.092699; target not reproduced |
|8B BC60/2 | Predetermined supplementary control, not the single-mask primary setting |τ1.603729, same file | Cannot select this cell or another aggregation to claim the primary reproduction |
| HF third-party budgets | Mathematical precheck of the original API under BF16/T0/originalq121 | Six forwards; first-token argmax margins40.75/33.5/33.25 in the [audit JSON](research/esp-third-party-audit-2026-10-15.json) | No validτ or full480 run; nonofficial; negative result retained |

The reproduction gap limits conclusions about original ESP. Local4B pairs support comparisons only within the common self-implementation. Historical checkpoint revision, template/length/aggregation choices are incompletely aligned: they are protocol gaps, not proven causes. BF16-versus-independent-AR operator investigations remain stopped.

### B. Coverage and components

E3 is a requested explanatory control, not a new-method main table. Template/random norms match before BF16 casting, with actual norm ratios recorded afterward. Content changes initialization/subsequent state and is not norm matched. Fixed-v controls are separate from the continuing native input_first EMA. Four local windows remain historical analysis, never a substitute for480; final reporting retains categories and every paired loss.

### C. Execution and experimental selection

The original GPU queue ended naturally with exit0 after content completed. CPU source/argmax/native-process checks and the formal readout passed. Plan PR23 and result PR22 are merged into dev; their remote topics are deleted, with frozen E3 PLANs unchanged. Normal commits/pushes, dev merges and deletion of their merged remote work branches are authorized. No main merge, force push or local data/Run/branch deletion. Old PRs/issues are closed only after verifying status and relationships, not merely age.

GPU admission uses actual nvidia-smi occupancy and sufficient free memory, not unidentified CPU processes. Group-boundary handoffs happen after full groups finish; one real quantization interleave has completed, without interrupting SD groups. Brief resource conflicts wait at prompt boundaries in the same Run. Source/argmax/OOM failures remain real failures, never fixed by prompt changes. Successful template and old zero are not rerun.

This is a predetermined discrete comparison, not adaptive parameter search or prompt tuning. Three direction seeds are three fixed biases, not independent training repeats. Identical first template tokens make each seed's vector identical across480 prompts. Paired descriptions are useful, but do not establish confidence across models, training randomness or arbitrary directions. No new significance claim is made. Decide directionBC60 after fullBC30 using actual token/forward work and the remaining question; never discard losing cells or describe unrun work as complete.

## IX. Execution records and conclusions

| Record | Actual evidence | Outcome/boundary |
| --- | --- | --- |
| E1 self-implementation |8B protocol_evidence and [stage report](research/sd-stage-report-2026-10-15.md) | Four mathematical audits pass,318830 tokens;BC30/60 single-mask targets missed; not author-code reproduction |
| E2 main matrix |[paired_evidence_v1.json](../studies/qwen3_4b_bf16_five_methods/docs/paired_evidence_v1.json), `cells`/`pairs` |11/11 native acceptance;4800 Spec prompt-executions and809118 audited tokens;τ below |
| E3 complete evidence |[direction_evidence_v1.json](../studies/qwen3_4b_bf16_directions/docs/direction_evidence_v1.json), [final report](research/4b-full-direction-controls-2026-10-16.md), [PR22](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/22) |`complete=true`; all six cells complete480. Original resource-failed Study remains passed=false; recovery Study passed=true; no failed result is resigned |
| Source/third-party negative evidence | Author-source report, third-party ORIGIN and audit | Unverified source discovery is not proof of no release; no fabricatedτ or8B rerun after failure |

| Accepted main method |4B BC30 pooledτ |4B BC60 pooledτ |
| --- | --- | --- |
| ESP frozen mean |1.402895 |1.499079 |
| Input order0 |1.422420 |1.519109 |
| Input order1 |1.511958 |1.636340 |
| Output order0 |1.433178 |1.528922 |
| Output order1 |1.435540 |1.529836 |

Each value comes from E2 `cells[budget/method].totals.pooled_tau`. Shared AR is diagnostic and is not assigned a fabricated draft-acceptanceτ. All per-prompt accepted/calls pairs, AR divergence and lengths remain in the source file; rounding here does not replace them. Input order1 is strongest overall in this main batch. The output-order1 increment is small; one favorable count alone does not establish joint gains or equal-output speedup.

E3 valid pooledτ: template1.507777653,random0=1.495188134,random1=1.464349086,random2=1.523884714,zero1.422420206,content1.364829262, all in the linked formal six-cell evidence. Random2 versus template has pairedτ267 wins/47 ties/166 losses. All three random seeds exceed zero, contradicting the claim that gains here require only e2−e1. Per-prompt counterexamples, different output lengths and unmatched content norms remain. This is neither a recommendation to select the best seed as a new method nor proof every direction works. Zero reuse and failed resource work stay explicit; recovery success cannot turn the original failed Study into a passed one.

No directionBC60 matrix is added this round: the five valid new cells already consumed2400 prompt-executions,405073 tokens and276523 model calls, and all three random directions falsify direction uniqueness in this batch. BC60 would test cross-budget generalization rather than resolve the content-norm confound. Failed complete partial work separately records20977 tokens/13854 calls and is never stitched into valid cells. CPU regression and PR22/dev closeout are complete. The active CPU-only work is gap accounting and author-protocol reconciliation from existing8B/4B evidence, with P0/P1/P2 outputs and stop conditions in the [gap report](research/esp-table1-gap-analysis-2026-10-16.md). No prompt filtering, aggregation selection or budget changes to chase the target. Official SD Table1 steps now have GPU priority, subject to a verified author entrypoint and fresh nonpreemptive admission; no self-implementation rerun or unrelated new experiment starts. Old0.6B rare-event, operator, Kalman and new-method work remain archived; open questions do not authorize new experiments.

Latest CPU source refresh: the [official-path recheck](research/esp-official-recheck-2026-10-16.md) confirms unchanged published Table1 targets1.63/1.74. Ten Figure8 labels and eight sampling-table labels do not establish the Table1 inclusion/weighting contract. Keep all480/13 local categories. No verified runnable author entry exists in the checked accessible sources; OpenReview access remains incomplete. No GPU job is started merely because the GPU is idle, and neither self-implementation nor the failed third-party path is rerun.

The [author repository/commit/attachment follow-up](research/esp-author-attachment-followup-2026-10-16.md) completed this bounded check: unchanged homepage commit, zero hits in three exact code queries, and six forum-ID hits yielding no verified author implementation. Three conventional OpenReview attachment candidates returned403 without code. The official entrypoint remains missing; GPU execution is not claimed. Once it is available, verify provenance and fresh admission using the launch checklist without asking for authorization again.

## X. GitHub use and plan changes

This is the current project-level plan, with a chapter-matched English translation. Study `docs/PLAN.md` files are pre-make frozen contracts; results/figures live in their STUDY_REPORT/evidence. Raw tokens/traces, full Runs, weights and caches stay out of Git. Native records retain code/source/input/model identity, actual configuration/environment, seed, command, RunID, failures and artifacts. Do not recreate a historical Run ID or re-sign successful evidence.

| Date | Change/reason | Affected scope |
| --- | --- | --- |
|2026-10-16 | Rewrite under Enmao's new ten-chapter template, add English, import pinned RPipe standards/templates and integrate targeted literature/current evidence | New default plan entry; v6 retained as history; not retrospective preregistration or a frozen-experiment change |
|2026-10-16 | Record author/self/third-party distinctions, argmax gate versus AR diagnostics, three directions and recovery | Narrow conclusions without expanding GPU budget or changing prompts |
|2026-10-16 | Pin installed Transformers5.12.1 after5.20 cache-API drift broke CPU CI | Installation reproducibility only; no scientific cache change or replacement of the live environment |

Plan PR23 and result[PR22](https://github.com/DreamSoul-AI/denoising-speculative-decoding/pull/22) are merged into dev and their remote topics deleted; see the [cleanup record](research/remote-branch-cleanup-2026-10-15.md). [Standards README](research/standards/README.md) records originals/translations, source and SHA values. The historical60-reference bibliography is not claimed as fully reviewed this round. Author originals, official data entry and the local reports linked in the literature table form this round's references; factual claims are located beside their supporting sources.
