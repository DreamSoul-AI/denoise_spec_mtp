"""Decompose saved mask velocities and seed-depth transitions on CPU.

    python tools/analyze_4b_velocity.py --study studies/qwen3_4b_bf16_five_methods --capture docs/research/4b-mask-geometry-observations-2026-10-15.json --vectors .tmp/4b-geometry-capture-v5/vectors.pt --out .tmp/4b-velocity-v1.json
"""
import argparse
import json
from pathlib import Path

import torch

def velocity_geometry(anchor, velocity):
    a, v = anchor.float(), velocity.float()
    assert a.norm() > 0 and v.norm() > 0 and (a + v).norm() > 0
    radial = a * (v @ a) / (a @ a)
    tangent = v - radial
    normalized_move = (a + v) / (a + v).norm() - a / a.norm()
    return {'velocity_over_anchor': float(v.norm() / a.norm()),
            'radial_signed_over_velocity': float((v @ a) / (a.norm() * v.norm())),
            'tangent_over_velocity': float(tangent.norm() / v.norm()),
            'normalized_movement_retention': float(normalized_move.norm() / (v.norm() / a.norm())),
            'raw_slot_norm_ratio': float((a + v).norm() / a.norm())}


def transition_counts(evidence):
    from analyze_4b_geometry import trace_metrics
    result = {str(d): {'transitions': 0, 'next_accept_d1': 0, 'next_accept_d2': 0} for d in (0, 1, 2)}
    for e in evidence:
        trace_metrics(e, len(e['input_ids']))
        for previous, current in zip(e['stats']['trace'], e['stats']['trace'][1:]):
            assert not previous['stopped']
            cell = result[str(len(previous['accepted_nodes']))]
            cell['transitions'] += 1
            cell['next_accept_d1'] += bool(current['accepted_nodes'])
            cell['next_accept_d2'] += len(current['accepted_nodes']) == 2
    for cell in result.values():
        n = cell['transitions']
        cell['next_accept_d1_rate'] = cell['next_accept_d1'] / n if n else None
        cell['next_accept_d2_rate'] = cell['next_accept_d2'] / n if n else None
    return result


def main():
    from analyze_4b_geometry import distribution, sha
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--study', required=True, type=Path)
    parser.add_argument('--capture', required=True, type=Path)
    parser.add_argument('--vectors', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    assert not args.out.exists()
    capture = json.loads(args.capture.read_text())
    assert capture['quality_passed'] and sha(args.vectors) == capture['raw_vectors_sha256']
    vectors = torch.load(args.vectors, map_location='cpu', weights_only=True)
    report = {'analyzer_sha256': sha(__file__), 'capture_sha256': sha(args.capture),
              'vectors_sha256': sha(args.vectors), 'no_model_forward': True, 'velocity': {}, 'transitions': {}}
    for method in ('input_first', 'output_first'):
        points = []
        for key, case in vectors.items():
            if not key.endswith('/' + method):
                continue
            qid = int(key.split('/')[0])
            length = next(c['new_tokens'] for c in capture['cases'] if c['question_id'] == qid and c['case'] == method)
            for frame in case['frames']:
                for i, depth in enumerate(frame['depths']):
                    if frame['root_index'] + depth + 2 >= length:
                        continue
                    a, b = frame['raw_predictions'][i].float()
                    point = velocity_geometry(a, b - a)
                    point.update(question_id=qid, root_index=frame['root_index'], depth=depth)
                    points.append(point)
        metrics = ('velocity_over_anchor', 'radial_signed_over_velocity', 'tangent_over_velocity',
                   'normalized_movement_retention', 'raw_slot_norm_ratio')
        report['velocity'][method] = {'points': points, 'distribution': {
            k: distribution([p[k] for p in points]) for k in metrics}}
    paired = json.loads((args.study / 'docs/paired_evidence_v1.json').read_text())
    for bc in (30, 60):
        for method in ('input_first', 'output_zero', 'output_first'):
            cell = paired['cells'][f'{bc}/{method}']
            path = args.study / 'runs' / cell['run_id'] / 'assets/decode_observations.json'
            assert sha(path) == cell['files_sha256']['assets/decode_observations.json']
            raw = json.loads(path.read_text())
            counts = transition_counts(raw['out']['evidence'])
            report['transitions'][f'{bc}/{method}'] = {'run_id': cell['run_id'], 'raw_sha256': sha(path),
                'counts': counts, 'total': sum(c['transitions'] for c in counts.values())}
    args.out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('PASS: saved vectors and six full480 Run hashes/seed-depth transitions; zero model forwards')


if __name__ == '__main__':
    main()
