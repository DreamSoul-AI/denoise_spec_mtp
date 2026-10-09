# LAYOUT

```text
src/
  rpipe/           full RPipe 0.2.0 package (local RPipe main, MIT, Enmao Diao), unchanged
  spec_mtp/        rpipe/ copied file for file (rpipe. → spec_mtp.); SpecMTP sits in spec_mtp/ submodules
    flow/          prepare → execute → collect → summarize → write → process
    structure/
      algorithm/   RPipe base, factory, train/, eval/
        eval/spec_mtp/   masks, tree, decoder, esp / ar / alignment, the eval Algorithm
      data/        RPipe config, factory, prepare, profile
        spec_mtp/        SpecBench, Dolly, local prompts
      model/       RPipe config, factory, ...
        spec_mtp/        hf_causal, tiny LLaMA
      system/      RPipe System, Logger, runtime
        spec_mtp/        device, dtype, seed helpers
      control/     RPipe Control, layers, run_config
        spec_mtp/        NamedDict for the decoder cfg
      artifact/    RPipe layout, result, index
        spec_mtp/        per-prompt CSV rows
      api/         RPipe layer facades
        spec_mtp/        register SpecMTP builders
      make/        RPipe make; writes studies/<name>/scripts/
studies/           code and data stay; scripts/, runs/, and results/ stay local
configs/           legacy single-run YAML (HF sweeps; migrate to studies/)
tests/
  spec_mtp/        mirrors src/spec_mtp; SpecMTP modules only
docs/              ARCHITECTURE, CI, BRAINSTORM, LAYOUT, TESTING
AGENTS.md          how to work in this repo; points at docs/
```

Run artifacts: `studies/<name>/runs/<id>/` with `config.yaml`, `result.json`,
`assets/` (tracker, logs, `summary.csv`, `spec_metrics.csv`). Study-level
`runs/`, `shared/`, `index.json` are gitignored.
