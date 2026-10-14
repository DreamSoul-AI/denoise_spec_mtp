# Cross-task falsification Study draft

Draft 2026-10-14, scientific source670c744e0535dcad after f3b95ea. This round prepares the Study and tokenizer input manifest only; no make, launch, native Run, source lock or result exists. Do not interpret expanded configs as measured results. Inputs and gates must be verified again before the first launch, then retain this contract byte-identical or use a new version if the contract changes.

## Evidence motivating the questions

Twelve translation development units q171–q182: pooled input/output0/output1 accepted60/45/47. Natural order1 gains occur atq173/q179, loss atq182; the remaining nine have equal pooled accepted, sometimes differing depth paths. Fixed bidirectional transfer changes accepted on4 units and not on8, including terminal/unused-owner controls. Q178 strict canonical states preserve8→9; q182 has a later valid second-slot restoration under equal source/root anchor/v but lacks a full canonical-state control. Seed changes alone do not imply accepted changes. This is development evidence, not random sampling or significance.

The executed provider arithmetic/norm controls in the extension preserve q178 full self/graft paths across all three operator substitutions. Transformer-created proxy hidden rounding remains open, covered by KERNEL_PLAN.md; this draft does not claim it is ruled out.

## Predeclared falsifiable hypotheses

H1 cross-task occurrence: at least one of four fixed summarization units has a natural output-order semantic difference or a fixed one-slot transfer semantic difference. If all four complete with none, reject this bounded occurrence prediction; do not replace prompts/windows after seeing nulls. Equal total accepted with different depth/owner/KV paths counts as semantic difference but must be distinguished from net gain.

H2 committed-state necessity: if a new unit has an accepted-count transfer change, it persists under a separately predeclared canonical anchor/v self-versus-graft comparison at the same fixed entry. A disappearing change with stable canonical self falsifies this local necessity exclusion; changed self constrains the comparison. Native and canonical results must be separate. The current cross-task budget does not include adaptive canonical Runs: retain the first eligible result and draft a new frozen protocol/version before such a run, rather than expanding this batch opportunistically. Q178 supports one instance, q179/q182 remain unresolved.

H3 first-slot-only explanation: any legal second-depth change while its first slot stays the same correct AR token falsifies it. Already contradicted onq178/q182; this batch tests whether that counterexample appears in another task. Never score second-depth margins when the first token is wrong or EOS removes the next target. Retain first-only gains/losses and no-change units.

H4 numeric-artifact explanation: q178 effect requires provider EMA/slot or norm rounding. Existing S64/N64/N32 controls contradict necessity of the post-entry provider stages in those fixed cells; initial root85 mapping was left native. The narrower untested transformer hypothesis is defined in KERNEL_PLAN.md; a kernel name alone is insufficient to accept it.

## Fixed inputs and conditions

Summarization file order skip0/take4, q241/242/243/244. DatasetSHA7dd26882f31ada100c2aa7447019b5349bddc55697021acbc5643fdc8740aa21; rendered input lengths692/647/595/901 with exact ID/template hashes in prompts_manifest.json. Same local ModelScope11-file Qwen3-0.6B snapshot, tied actual weights, FP32/eager/CUDA, nonthinking, T0/EOS/max100, static unpruned[1,1]/k2/BC9, beta.9/beta_prime.99, original native deterministicfalse. Seeds123+i; algorithm version output-space-summarization-241-244-draft-v1. No prompt shortening; any input mismatch, unsupported context or source drift stops the batch and is reported.

Four new native Runs: input frozen mean, output0, output1, independent AR. Native make→launch→process→report, all source/model/input/factor/raw/AR/Study gates, full output token equality required. No successful old Run is rerun or re-signed.

After native success, freeze a selection manifest using existing choose_window(), identical to the q175–q182 procedure: earliest shared acceptance with preceding common rejection; otherwise first continuing shared rejection; otherwise continuing unused-owner control; no feasible continuing root is retained explicitly. Capture full original-root union from entry; use actual visited roots and owners after transfer. Two baseline observations, both donor directions and order1 original-value placebo per feasible unit, owner0 second slot[0,1] once only; independent AR and through-entry semantic equality hard gates. Original baseline/placebo must reproduce full native trace. Reuse measured helpers without editing their bytes. The manifest must supply rendered_prompts/question_id for diagnose_study_windows.py; native rendered IDs must equal the preflight IDs, not just qids.

## Metrics, budget and decisions

For each unit report native accepted by depth, calls, all actual semantic trajectories, legal two-slot target margins, matched-state anchor/v equality, source owner and proxy/seed differences, gains and losses, infeasible/noncommon roots. Separate H1 occurrence, accepted net gain and H3 depth-only effects. No power/significance claim from n=4, no win-rate estimate from the prior12; no default retuning or speed conclusion.

Serial singleGPU/round1/OMP-MKL1. Native budget1600 new tokens+1200 internal AR audit+72 existing warmup; diagnostics at most20x100=2000 new tokens, no auxiliary transformer forward. Initial inputs are longer than the translation calibration, so first native Run calibrates actual host/KV/GPU usage before continuing. Prior6.7GB RSS/~6.3GiB globalGPU is context, not this batch's measurement. Sample.5s; retain est/actual and explicit background-memory limitation. Stop/preserve OOM, nonfinite, output/scope/source/hash/root failure, context shortening or resource pressure. No replacement prompt or relaxed gate.

Full weights/cache/Run/profiler traces/tensors local only; formal summaries and selected scalar provenance can be reviewed separately. No push/merge/delete. Next decision after this bounded batch: accept/reject the occurrence prediction, retain every positive/null, and choose a frozen canonical or transformer-operator follow-up based on the declared criterion. No full matrix is implied.
