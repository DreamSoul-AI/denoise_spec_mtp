# Output-space chain prerequisite

Tied final-normalized hidden masks, order0/order1, two-slot unpruned chain, matched frozen-input chain and independent AR. [PLAN](docs/PLAN.md) fixes method/protocol before execution; [report](docs/STUDY_REPORT.md), [raw selection](docs/execution_v1.json), [NUMBERS](docs/NUMBERS.md) and [figure](docs/figures/acceptance_v1.png) preserve actual results and their scope.

2026-10-14: all four Runs and source/evidence/correctness/completeness gates passed. All speculative outputs exactly match the independent 47-token AR. Accepted drafts: frozen-input chain17, output order0=10, output order1=10. This is a negative acceptance observation on one development prompt, not a full-method/Kalman claim; no tuning or expanded matrix.

Use the native `python -m spec_mtp make studies/output_space_prerequisite --num-gpus 1 --init-gpu 0 --round 1`, then launch/process/status/logs/report. Prepare the verified ModelScope snapshot first; Runs are local_files_only. The machine-local cache junction/raw artifacts are excluded from Git. New execution requires a new version/Run ID. `python studies/output_space_prerequisite/plot_results.py` only redraws the saved figure.
