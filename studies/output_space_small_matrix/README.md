# Output-space small matrix

Predeclared fresh q172–q174, unchanged frozen-input/output-order0/output-order1 chain and independent AR. [PLAN](docs/PLAN.md), [prompts](docs/prompts_manifest.json), [report](docs/STUDY_REPORT.md), [execution evidence](docs/execution_v1.json), [NUMBERS](docs/NUMBERS.md) and [paired-prefix diagnosis](docs/trajectory_diagnosis.json).

All four new Runs (3 prompts per Run) and raw/source/correctness/Study gates passed. Accepted drafts per prompt for input/order0/order1: q172=1/1/1, q173=5/1/3, q174=0/1/1. All outputs exactly match independent AR. This mixed small-sample evidence does not establish stable superiority or a proxy-hidden mechanism.

Rebuild saved analysis with `python studies/output_space_small_matrix/analyze_trajectories.py`; redraw with `python studies/output_space_small_matrix/plot_results.py`. Neither runs a model. Native make/launch/process/report are reused; new execution requires fresh version/Run IDs and verified ModelScope cache. No pushed branch, PR merge or data cleanup.

Follow-up: [window plan](docs/WINDOW_PLAN.md)/[evidence](docs/window_diagnosis_v1.json), [fixed scale plan](docs/SCALE_PLAN.md)/[counterfactual results](docs/scale_diagnosis_v1.json), and [offline structural check](docs/structural_diagnosis_v1.json). Replays preserve original tokens/traces; local margins explain two q173 acceptance differences. Root83 errors persist when only the observed norm is changed; no global benefit claim or recipe change.
