"""Option A check: old (b1f6191) vs new capture, context limit cells vs the rest.

Manual tool, like capture.py / compare.py.

    python ctx_check.py .tmp/regress/old.json .tmp/regress/new.json <out.json>

Passes when
- every cell without ``hit_context_limit`` is identical to the old code (rows,
  summary, metrics, status);
- in context-limit cells only the audit fields differ (``ar_calls``,
  ``exact_match``, ``ar_time``, summary ``exact_match_rate`` / AR timing and
  ``speedup``, Run status), ``exact_match_rate`` is 1 and the Run succeeded;
- every speculative token sequence is identical; every AR sequence that changed
  is a prefix of the old AR sequence.
"""
import json
import sys

AUDIT = {'ar_calls', 'exact_match', 'ar_time', 'exact_match_rate', 'speedup', 'ar_tok_per_s',
         'test_exactmatchrate', 'test_speedup', 'test_arcalls', 'status'}
TIMING = ('time', 'tok_per_s', 'speedup')
# Artifacts the old code never wrote (alignment_probe CSV, fixed 2026-10-12): new-only is allowed;
# their values match the old stdout log (layer / cos_* / n_* identical).
NEW_ONLY = {'alignment_metrics.csv'}


def strip(obj, drop):
    if isinstance(obj, dict):
        return {k: strip(v, drop) for k, v in obj.items()
                if k not in drop and not any(t in k for t in TIMING)}
    if isinstance(obj, list):
        return [strip(v, drop) for v in obj]
    return obj


def ctx_cell(cell):
    return any(str(r.get('hit_context_limit')) == '1' for r in cell.get('spec_metrics.csv', []))


old, new = (json.load(open(p)) for p in sys.argv[1:3])
report = {'cells': [], 'tokens': [], 'ok': True}
for key in sorted(new):
    if key.endswith('|tokens'):
        o, n = old[key], new[key]
        spec_same = [s for s in o if s[0] == 'spec'] == [s for s in n if s[0] == 'spec']
        ar_ok = len(o) == len(n) and all(
            a == b or (a[0] == b[0] == 'ar' and all(x[:len(y)] == y for x, y in zip(a[1], b[1])))
            for a, b in zip(o, n))
        changed = sum(a != b for a, b in zip(o, n))
        ok = spec_same and ar_ok
        report['tokens'].append({'key': key, 'sequences': len(n), 'spec_identical': spec_same,
                                 'changed_ar_are_old_prefixes': ar_ok, 'changed': changed, 'ok': ok})
        report['ok'] &= ok
        continue
    o, n = old[key], new[key]
    limited = ctx_cell(n)
    drop = AUDIT if limited else set()
    added = sorted(k for k in NEW_ONLY if k in n and k not in o)
    same = strip(o, drop) == strip(n, drop | set(added))
    rate = n['metrics'].get('test_exactmatchrate')
    ok = same and n['status'] == 'succeeded' and (rate is None or float(rate) == 1.0)
    report['cells'].append({'key': key, 'context_limit': limited, 'identical_outside_audit': same, 'new_artifacts': added,
                            'status_old': o['status'], 'status_new': n['status'],
                            'exact_match_rate_old': o['metrics'].get('test_exactmatchrate'),
                            'exact_match_rate_new': rate, 'ok': ok})
    report['ok'] &= ok
report['context_limit_cells'] = sum(c['context_limit'] for c in report['cells'])
report['other_cells'] = len(report['cells']) - report['context_limit_cells']
json.dump(report, open(sys.argv[3], 'w'), indent=1)
print('ok' if report['ok'] else 'FAIL', report['context_limit_cells'], 'context-limit cells,',
      report['other_cells'], 'other cells')
for c in report['cells'] + report['tokens']:
    if not c['ok']:
        print('  FAIL', c['key'])
sys.exit(0 if report['ok'] else 1)
