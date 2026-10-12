"""Compare two capture.py outputs; write a compact, commit-able summary.

usage: python compare.py <old.json> <new.json> <out.json>
Timing fields were already dropped by capture.py. Token streams are compared
in full and summarised by sha256 so the summary stays small.
"""
import hashlib
import json
import sys

old, new = (json.load(open(path)) for path in sys.argv[1:3])
cells, diffs = [], []
for key in sorted(set(old) | set(new)):
    a, b = old.get(key), new.get(key)
    if a != b:
        diffs.append(key)
    if key.endswith('|tokens'):
        digest = lambda v: hashlib.sha256(json.dumps(v).encode()).hexdigest()[:16] if v is not None else None
        cells.append({'key': key, 'sequences': len(a or []), 'old_sha256': digest(a), 'new_sha256': digest(b),
                      'equal': a == b})
        continue
    overall = [r for r in (a or {}).get('summary.csv', []) if r.get('category') == 'overall']
    rows = (a or {}).get('spec_metrics.csv', [])
    cells.append({'key': key, 'equal': a == b, 'status': (a or {}).get('status'),
                  'exact_match_rate': overall[0].get('exact_match_rate') if overall else None,
                  'accepted': sum(int(r['accepted']) for r in rows) if rows and 'accepted' in rows[0] else None,
                  'committed': sum(int(r['committed']) for r in rows) if rows and 'committed' in rows[0] else None,
                  'decode_calls': sum(int(r['decode_calls']) for r in rows) if rows and 'decode_calls' in rows[0] else None,
                  'hit_context_limit': sum(int(r['hit_context_limit']) for r in rows) if rows and 'hit_context_limit' in rows[0] else None})
body = {'equal': not diffs, 'differences': diffs, 'cells': cells}
json.dump(body, open(sys.argv[3], 'w'), indent=1)
print('equal' if not diffs else f'{len(diffs)} differences', len(cells))
