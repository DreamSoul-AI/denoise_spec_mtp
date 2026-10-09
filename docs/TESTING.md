# TESTING

Tests live under `tests/spec_mtp/` and follow `src/spec_mtp/`. They cover the SpecMTP modules: the eval algorithm, prompt sets, the tiny model, and the small additions under system, control, artifact, and api. The copied RPipe files are not tested here.

## CPU gate (CI and local)

```text
set PYTHONUTF8=1
pip install -e .
python -m pytest tests/spec_mtp
```

That run includes the smoke Study `studies/smoke_tiny_llama`. Each of its three variants must have `exact_match_rate` 1. A person can also run the script that Study generates: `studies/smoke_tiny_llama/scripts/launch.ps1`.

| **tests** | **what they cover** |
| --- | --- |
| `structure/algorithm/eval/spec_mtp/` | masks, trees, lossless decode, EMA history, named mask settings, smoke Study |
| `structure/data/spec_mtp/` | category windows and synthetic prompts |
| `structure/model/spec_mtp/` | tiny LLaMA embed and forward |
| `structure/system/spec_mtp/` | device and dtype |
| `structure/control/spec_mtp/` | NamedDict |
| `structure/artifact/spec_mtp/` | CSV rows |
| `structure/api/spec_mtp/` | registration on spec_mtp's own registries |
