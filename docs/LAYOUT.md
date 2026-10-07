# LAYOUT

```text
src/
  rpipe/           vendored RPipe 0.2.0 (MIT, Enmao Diao)
  spec_mtp/        ESP + EMA-velocity research code and RPipe registrations
    algorithms/    esp_mtp, ar_baseline, alignment_probe
    data/          specbench, dolly, local_prompts
    models/        hf_causal / tiny_llama adapter
    spec/          mask_providers, tree, decoding
    rpipe/         Data / Model / Algorithm builders (source spec_mtp)
studies/           Study declarations (smoke_tiny_llama = CPU CI gate)
configs/           legacy single-run YAML (HF sweeps; migrate to studies/)
scripts/           run_ci_checks.py, download_data.sh, run_*.sh
tests/
  spec_mtp/spec/   CPU correctness scripts (219 checks)
  rpipe/           upstream RPipe unit tests (optional)
docs/              ARCHITECTURE, RESEARCH, CI, BRAINSTORM, LAYOUT, TESTING
```

Run artifacts: `studies/<name>/runs/<id>/` with `config.yaml`, `result.json`,
`assets/` (tracker, logs, `summary.csv`, `spec_metrics.csv`). Study-level
`runs/`, `shared/`, `index.json` are gitignored.
