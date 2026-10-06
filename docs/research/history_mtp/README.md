# History-based multi-token prediction: research index

Topic: does an EMA of input-embedding differences give a useful probe for
future tokens (EMA-Velocity masks), and how does it relate to Momentum
Guidance? Kickoff doc (read-only, maintained outside this repo):
`D:\360安全浏览器下载\Agent\DreamSoul\研发\研究\历史外推多 Token 预测 History-based Multi-Token Prediction\研究启动与 Cursor 任务.md`.

| **Doc** | **Content** |
| --- | --- |
| [report.md](report.md) | Current experiment report: setup, tables, conclusions |
| [study_plan.md](study_plan.md) | Notation, factors, decision rules, and the sweep plan |
| [formula_code_audit.md](formula_code_audit.md) | ESP / EMA-Velocity / MG formulas vs code, evidence labels |
| [experiment_log_20261006.md](experiment_log_20261006.md) | Commands, paths, and the raw result tables |
| [../../ci.md](../../ci.md) | CPU check entry, CI workflow, result protocol |

Code added on `feature/research-ema-history-audit`:

- `tests/check_ema_history.py`: alignment, synthetic geometry, rejection isolation
- `scripts/run_ci_checks.py`: single local/CI check entry
- `.github/workflows/cpu-checks.yml`: CPU CI
- `history_mtp.code-workspace`: multi-root workspace (this repo + research folder)

Result locations (gitignored, local):

- `results/cursor_20261006_history_audit/` for experiments
- `.test-results/<run_id>/` for check runs

The default `results/smoke/` and `results/hf/` paths are left to the existing
owners.

## Status (2026-10-06)

- Both orders, `m = m0 + i * vhat`, Qwen3-4B float32, tree `[14]`. On 26
  prompts the slope goes from −84 accepts at β=0.5 to +73 at β=0.9999 versus
  the updating prompt mean. A fresh 52-prompt holdout repeats the long-memory
  cell: +198 accepts, tau 1.589 versus 1.491, exact match 1. λ does not
  reverse the β result. Log section 8.
- Confirmation set (52 unused prompts, Qwen3-4B float32, tree `[14]`):
  exact match is 1.0 on all five cells, and every cell commits 4628 tokens.
  Frozen prompt-mean tau 1.454 versus last-token 1.393 (+139 drafts). ESP
  update 1.464 (+17 drafts over frozen, categories cancel). Following the
  difference EMA 1.391 versus step 0 at 1.393 (−4 drafts). The history
  direction is not separated from "mask = last token", so the Momentum
  Guidance cell stays out. Details in the experiment log, section 7.
- Exploration slice (26 prompts, same model): default EMA and step 0 both
  tau 1.385; ESP tau 1.475. Same sign as the confirmation set.
- History alignment and rejection isolation: verified on CPU, no bug found.
- Qwen3-8B bf16 on the exploration slice agreed in sign, but exact match was
  0.50–0.65 because top-2 logit gaps were at most one bf16 unit in the last
  place. The float32 runs are the lossless comparison.
- Not run: 480 prompts, a second model, depth beyond 1, Momentum Guidance.
