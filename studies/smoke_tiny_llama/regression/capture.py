"""Refactor regression capture: token streams + metrics, before vs after.

Manual tool (no ``__init__.py``; not a Flow phase, not collected by pytest).

    old: PYTHONPATH=<b1f6191 checkout>/src python capture.py old .tmp/regress/old.json <study>...
    new: python capture.py new .tmp/regress/new.json <study>...
    python compare.py .tmp/regress/old.json .tmp/regress/new.json <out.json>

Each Study is copied under ``.tmp/regress/work/<mode>/`` and run through the
entry of that code base (old: copied ``spec_mtp.flow.cli``; new: RPipe
``rpipe.flow.cli`` with ``spec_mtp.recipe``). Study phase hooks are not
enabled here, so a cell that breaks exact match is still captured instead of
failing; the Run gate is tested separately in tests/. Every SpecDecoder and
AR output sequence is recorded in call order (warm-up included).
"""
import csv, importlib, json, os, shutil, sys
import yaml
from pathlib import Path
mode, out, studies = sys.argv[1], sys.argv[2], sys.argv[3:]
if mode == 'old':
    import spec_mtp  # registers
    from spec_mtp.flow.cli import run_study
    dec_mod = 'spec_mtp.structure.algorithm.eval.spec_mtp.decoding'
    prefix = 'spec_mtp.structure.algorithm.eval.spec_mtp'
else:
    from rpipe.flow.cli import run_study
    dec_mod = 'spec_mtp.structure.algorithm.decoding'
    prefix = 'spec_mtp.structure.algorithm'
dec = importlib.import_module(dec_mod)
LOG = []
orig_gen = dec.SpecDecoder.generate
def gen(self, ids):
    o, s = orig_gen(self, ids); LOG.append(('spec', o.tolist())); return o, s
dec.SpecDecoder.generate = gen
orig_ar = dec.ar_generate
def ar(*a, **k):
    o, s = orig_ar(*a, **k); LOG.append(('ar', o.tolist())); return o, s
for name in list(sys.modules):
    if name.startswith(prefix) and hasattr(sys.modules[name], 'ar_generate'):
        sys.modules[name].ar_generate = ar
for name in ['alignment_probe','ar_baseline','esp_mtp']:
    m = importlib.import_module(f'{prefix}.{name}'); m.ar_generate = ar
TIME = ('time', 'tokens_per_s', 'tokenspers', 'speedup', 'elapsed')
def clean(row): return {k: v for k, v in row.items() if not any(t in k for t in TIME)}
res = {}
for s in studies:
    work = Path('.tmp/regress/work') / mode / Path(s).name
    if work.exists(): shutil.rmtree(work)
    shutil.copytree(s, work, ignore=shutil.ignore_patterns('runs', 'docs', 'regression', 'flow', 'recipe.py', '*.json', 'scripts'))
    sy = yaml.safe_load(open(work / 'study.yaml'))
    sy.pop('flow', None); sy.pop('recipe', None)
    if mode == 'new':
        sy['recipe'] = 'recipe.py'; sy['flow'] = {'prepare_shared': False}
        (work / 'recipe.py').write_text('from spec_mtp.recipe import register\n')
        yaml.safe_dump(sy, open(work / 'study.yaml', 'w'), sort_keys=False)
    run_study(work)
    idx = json.load(open(work / 'index.json'))
    for e in idx['experiments']:
        key = Path(s).name + '|' + json.dumps(e['factors'], sort_keys=True)
        rid = e['runs'][0]['id']; a = work / 'runs' / rid / 'assets'
        r = json.load(open(work / 'runs' / rid / 'result.json'))
        ent = {'status': r['status'], 'metrics': clean(r.get('metrics', {}))}
        for f in ('spec_metrics.csv', 'summary.csv', 'alignment_metrics.csv'):
            if (a / f).exists(): ent[f] = [clean(x) for x in csv.DictReader(open(a / f))]
        res[key] = ent
    res[Path(s).name + '|tokens'] = LOG[:]; LOG.clear()
json.dump(res, open(out, 'w'), indent=1, sort_keys=True)
print('captured', len(res))
