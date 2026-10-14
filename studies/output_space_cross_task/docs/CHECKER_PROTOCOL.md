# q241–q244 executable falsification checks

Current state: only synthetic decision tests and config expansion; no real-model cross-task Run was launched. Synthetic H1 rejection is a test fixture outcome, not a scientific result. Original PLAN remains the draft history. This checker and this protocol are explicitly included in future provenance; any changes after make require a new version/identity.

check_hypotheses.py export verifies current RPipe/SpecMTP source and PLAN freezes, complete native Study/process and all four raw/AR/config/input gates. Native rendered IDs must match the fixed manifest, not only qids. It exports execution_v1.json and freezes choose_window() results for the unchanged four-prompt diagnostic runner. Different prior exports are preserved and rejected. check repeats those native gates, binds diagnostic matrix/tensor SHA, then evaluates the full fixed group; quality failure, missing/duplicate case, incomplete unit or failed placebo cannot produce a verdict.

H1 uses TRACE_KEYS semantic paths, excluding float mask diagnostics. A semantic difference counts even when total accepted is unchanged. All four complete feasible comparisons with no natural/transfer difference falsify only the bounded occurrence prediction. An infeasible window is not a null transfer: without other positive evidence the verdict is inconclusive, with explicit qids.

H3 requires a matched true root, both paths accepting at least depth1, the same correct first AR candidate, an available second target, first token not EOS, and opposite actual depth2 acceptance. It checks captured natural pair rankings and recipient-versus-transfer rankings. It never infers a witness from second margin alone or a wrong first token. No witness means not falsified in captured windows, not proof of the first-slot-only explanation. H2 explicitly remains untested until a separately frozen canonical protocol; H4 belongs to operator experiments, not this cross-task batch.

## Runnable sequence for a future fresh execution

Use current local environment with PYTHONUTF8=1, PYTHONPATH=<repo>/src, OMP_NUM_THREADS=1, MKL_NUM_THREADS=1. Before first real make, write the execution addendum/new algorithm version and calibrate the first serial Run as PLAN requires. Reuse the hash-verified local ModelScope snapshot in this Study's shared/model/modelscope/Qwen/Qwen3-0.6B via an independent directory junction; do not copy weights into Git or download from another provider. No source/default modification is needed.

From repo root, after that preflight:

```text
python -m spec_mtp make studies/output_space_cross_task --num-gpus 1 --init-gpu 0 --round 1
python -m spec_mtp launch studies/output_space_cross_task --num-gpus 1 --init-gpu 0
python -m spec_mtp process studies/output_space_cross_task
python -m spec_mtp report studies/output_space_cross_task
python studies/output_space_cross_task/check_hypotheses.py export
python tools/diagnose_study_windows.py --study studies/output_space_cross_task --out .tmp/cross-task-<new-id>
python studies/output_space_cross_task/check_hypotheses.py check --diagnostic .tmp/cross-task-<new-id>
```

CPU-only minimal logical reproduction now: python studies/output_space_cross_task/check_hypotheses.py mre. It labels output synthetic_only_no_model_evidence=true and does not make/launch/load weights. Tests cover complete-null rejection, count-equal semantic change, legal depth2, wrong first token, EOS, absent second target, natural depth2, infeasible windows, quality/missing/duplicate/failed-placebo rejection. No actual accepted counts for q241–244 are recorded.
