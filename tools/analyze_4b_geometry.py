"""Audit existing 4B acceptance traces without model forwards.

    python tools/analyze_4b_geometry.py --study studies/qwen3_4b_bf16_five_methods --out .tmp/4b-geometry-cpu-v1.json
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

POSITION_EDGES = (0, 32, 64, 128, 192, 256)


def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def distribution(values):
    values = np.asarray(values, dtype=float)
    if values.size == 0:
        return {'n': 0}
    assert np.isfinite(values).all()
    return dict(n=int(values.size), mean=float(values.mean()),
                **{name: float(np.quantile(values, q)) for name, q in
                   [('min', 0), ('p05', .05), ('p25', .25), ('median', .5), ('p75', .75), ('p95', .95), ('max', 1)]})


def trace_metrics(evidence, prompt_length):
    stats = evidence['stats']
    traces = stats['trace']
    assert len(traces) == stats['decode_calls']
    assert sum(len(t['accepted_nodes']) for t in traces) == stats['accepted']
    assert sum(len(t['committed_tokens']) for t in traces) == stats['committed']
    assert sum(stats['accept_by_depth']) == stats['accepted']
    events, offset = [], 0
    for t in traces:
        root = t['root_position'] - prompt_length
        assert root == offset and t['cache_before'] == t['root_position']
        accepted = len(t['accepted_nodes'])
        assert accepted <= 2
        events.append((root, accepted, len(t['committed_tokens'])))
        offset += len(t['committed_tokens'])
    assert stats['accepted'] + stats['decode_calls'] >= stats['committed']
    return events


def summarize_geometry(capture):
    assert capture['quality_passed'] and capture['status'] == 'complete'
    methods = ('input_first', 'output_zero', 'output_first')
    metrics = ('mask_norm', 'raw_norm', 'target_norm', 'mask_target_cos', 'raw_target_cos',
               'mask_target_norm_ratio', 'slot_pair_cos', 'velocity_anchor_ratio',
               'real_hidden_norm', 'real_hidden_target_cos', 'predicted_hidden_real_cos',
               'mask_scale_relative_error', 'reconstruction_direction_cos')
    result = {'groups': {}, 'slot_effects': {}, 'matched_shared_prefix': {}, 'capture_cases': len(capture['cases'])}
    for cohort in ('all', 'shared_prefix'):
        points = [p for p in capture['points'] if cohort == 'all' or p['shared_prefix']]
        for method in methods:
            indexed_slots = {(p['question_id'], p['root_index'], p['depth'], p['slot']): p
                             for p in points if p['case'] == method}
            pairs = [(p, indexed_slots[key[:-1] + (1,)]) for key, p in indexed_slots.items()
                     if key[-1] == 0 and key[:-1] + (1,) in indexed_slots]
            result['slot_effects'][f'{cohort}/{method}'] = {
                f'{field}_slot1_over_slot0': distribution([b[field] / a[field] for a, b in pairs])
                for field in ('raw_norm', 'mask_norm')}
            for slot in (0, 1):
                for depth in (None, 0, 1, 2):
                    rows = [p for p in points if p['case'] == method and p['slot'] == slot
                            and (depth is None or p['depth'] == depth)]
                    key = f'{cohort}/{method}/depth{depth}/slot{slot}'
                    result['groups'][key] = {m: distribution([p[m] for p in rows if m in p]) for m in metrics}
    indexed = {}
    for method in methods:
        rows = [p for p in capture['points'] if p['case'] == method and p['shared_prefix']]
        indexed[method] = {(p['question_id'], p['root_index'], p['depth'], p['slot']): p for p in rows}
        assert len(rows) == len(indexed[method]), 'Duplicate observed owner/slot'
    common = set.intersection(*(set(indexed[m]) for m in methods))
    for first, second in [('input_first', 'output_zero'), ('input_first', 'output_first'), ('output_zero', 'output_first')]:
        for slot in (0, 1):
            keys = sorted(k for k in common if k[-1] == slot)
            for key in keys:
                assert abs(indexed[first][key]['target_norm'] - indexed[second][key]['target_norm']) < 1e-6
            result['matched_shared_prefix'][f'{second}-{first}/slot{slot}'] = {
                metric: distribution([indexed[second][k][metric] - indexed[first][k][metric] for k in keys])
                for metric in ('mask_target_cos', 'mask_target_norm_ratio', 'velocity_anchor_ratio')}
    return result


def summarize_cell(raw):
    rows, evidence = raw['out']['rows'], raw['out']['evidence']
    assert len(rows) == len(evidence) == 480
    bins = [{'root_index_range': [a, b], 'calls': 0, 'accept_ge1': 0, 'accept_ge2': 0,
             'accepted': 0, 'committed': 0} for a, b in zip(POSITION_EDGES, POSITION_EDGES[1:])]
    attempts, accepts = [0, 0, 0, 0], [0, 0, 0, 0]
    norm_min, norm_max, norm_errors, owner_diffs, scales = [], [], [], [], []
    by_category = {}
    for row, e in zip(rows, evidence):
        stats = e['stats']
        events = trace_metrics(e, len(e['input_ids']))
        assert len(e['output_ids']) - len(e['input_ids']) == row['new_tokens'] == stats['new_tokens']
        assert stats['verification_argmax_audit']['passed']
        for d in (1, 2, 3):
            attempts[d] += row[f'attempt_d{d}']
            accepts[d] += row[f'accept_d{d}']
            assert row[f'attempt_d{d}'] == stats['attempt_by_depth'][d]
            assert row[f'accept_d{d}'] == stats['accept_by_depth'][d]
        category = by_category.setdefault(row['category'], {'calls': 0, 'accepted': 0, 'committed': 0, 'prompts': 0})
        category['prompts'] += 1
        for root, accepted, committed in events:
            cell = next(b for b in bins if b['root_index_range'][0] <= root < b['root_index_range'][1])
            for counter in (cell, category):
                counter['calls'] += 1
                counter['accepted'] += accepted
                counter['committed'] += committed
            cell['accept_ge1'] += accepted >= 1
            cell['accept_ge2'] += accepted >= 2
        if 'output_hidden_prefill' in stats:
            scale = stats['output_hidden_prefill']['scale']
            scales.append(scale)
            for t in stats['trace']:
                m = t['output_hidden']
                norm_min.append(m['mask_norm_min'])
                norm_max.append(m['mask_norm_max'])
                norm_errors.extend([abs(m['mask_norm_min'] / scale - 1), abs(m['mask_norm_max'] / scale - 1)])
                owner_diffs.append(m['last_owner_diff_from_root'])
    calls, accepted, committed = [sum(r[k] for r in rows) for k in ('decode_calls', 'accepted', 'committed')]
    assert accepts[1] + accepts[2] == accepted and attempts[1] == calls
    trim = accepted + calls - committed
    tau = committed / calls
    assert abs(tau - (1 + accepts[1] / calls + accepts[2] / calls - trim / calls)) < 1e-12
    for b in bins:
        b.update(accept_ge1_per_call=b['accept_ge1'] / b['calls'],
                 accept_ge2_per_call=b['accept_ge2'] / b['calls'],
                 accepted_per_call=b['accepted'] / b['calls'])
    return {'prompts': len(rows), 'decode_calls': calls, 'accepted': accepted, 'committed': committed,
            'tau': tau, 'trim_loss': trim, 'tau_components': {'d1': accepts[1] / calls, 'd2': accepts[2] / calls,
                                                           'negative_trim': -trim / calls},
            'depths': [{'depth': d, 'attempts': attempts[d], 'accepted': accepts[d],
                        'conditional_accept_rate': accepts[d] / attempts[d] if attempts[d] else None,
                        'attempts_per_decode_call': attempts[d] / calls} for d in (1, 2)],
            'position_bins': bins, 'categories': by_category,
            'norm_audit': {'scale': distribution(scales), 'block_min_norm': distribution(norm_min),
                           'block_max_norm': distribution(norm_max), 'relative_error_extrema': distribution(norm_errors),
                           'last_owner_diff_from_root': distribution(owner_diffs)},
            'hidden_vectors_saved': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--study', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--capture', type=Path, help='Completed scalar geometry.json; summarize without model forwards')
    args = parser.parse_args()
    assert not args.out.exists(), 'Use a new output path; previous observations are retained'
    study = args.study
    paired = json.loads((study / 'docs/paired_evidence_v1.json').read_text(encoding='utf-8'))
    assert paired['complete']
    report = {'scope': 'Existing full480 BF16 traces; zero model forwards',
              'paired_path': 'studies/qwen3_4b_bf16_five_methods/docs/paired_evidence_v1.json',
              'paired_local_sha256': sha(study / 'docs/paired_evidence_v1.json'),
              'analyzer_sha256': sha(__file__), 'cells': {}, 'tau_differences': [],
              'limitations': ['Position bins use actual method-specific paths, not shared prefixes.',
                              'Depth conditional attempts are available per prompt, not per-position trace.',
                              'Norm extrema do not contain hidden directions or individual mask distributions.']}
    for key, c in paired['cells'].items():
        if key == 'AR':
            continue
        path = study / 'runs' / c['run_id'] / 'assets/decode_observations.json'
        assert sha(path) == c['files_sha256']['assets/decode_observations.json']
        result = summarize_cell(json.loads(path.read_text(encoding='utf-8')))
        assert result['accepted'] == c['totals']['accepted'] and abs(result['tau'] - c['totals']['pooled_tau']) < 1e-12
        report['cells'][key] = dict(result, run_id=c['run_id'], raw_sha256=sha(path))
    for bc in (30, 60):
        for first, second in [('input_first', 'output_zero'), ('input_first', 'output_first'), ('output_zero', 'output_first')]:
            a, b = [report['cells'][f'{bc}/{method}'] for method in (first, second)]
            delta = {k: b['tau_components'][k] - a['tau_components'][k] for k in a['tau_components']}
            assert abs(sum(delta.values()) - (b['tau'] - a['tau'])) < 1e-12
            report['tau_differences'].append({'first': f'{bc}/{first}', 'second': f'{bc}/{second}',
                                              'tau_delta': b['tau'] - a['tau'], 'components': delta})
    if args.capture:
        report['geometry_capture_sha256'] = sha(args.capture)
        report['geometry'] = summarize_geometry(json.loads(args.capture.read_text(encoding='utf-8')))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('PASS: 10 full480 cells; all traces/counts/raw hashes/tau identities verified; no model forward')


if __name__ == '__main__':
    main()
