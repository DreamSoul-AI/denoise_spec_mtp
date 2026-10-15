"""Read fixed-window logits on CPU and distinguish rank, budget and parent coverage.

    python tools/analyze_4b_window_results.py --study studies/qwen3_4b_bf16_five_methods --windows .tmp/4b-mask-windows-v1/windows.json --logits .tmp/4b-mask-windows-v1/private_logits.pt --out .tmp/4b-window-readout-v1.json
"""
import argparse
from collections import Counter
import json
from pathlib import Path

import torch


def rank_interval(logits, target, banned):
    if target == banned:
        return None
    greater = int((logits > logits[target]).sum()) - int(logits[banned] > logits[target])
    equal = int((logits == logits[target]).sum()) - int(logits[banned] == logits[target])
    return greater + 1, greater + equal


def coverage(logits, root, truth, budget=9, tree=None):
    from spec_mtp.structure.algorithm.decoding import tree_probs
    from spec_mtp.structure.algorithm.tree import build_dynamic_tree
    if tree is None:
        tree = build_dynamic_tree(tree_probs(logits, 0.), budget, root, pruning=True)
    first = tree.children_of(0)
    correct = next((c for c in first if tree.tokens[c - 1] == truth[0]), None)
    depth2_width = sum(d == 2 for d in tree.depths)
    d1_rank = rank_interval(logits[0], truth[0], root)
    d2_rank = rank_interval(logits[1], truth[1], truth[0])
    return tree, {'actual_d1_width': len(first), 'actual_d2_width': depth2_width,
        'reference_d1_is_expanded_top1': bool(first) and tree.tokens[first[0] - 1] == truth[0],
        'reference_d1_in_tree': correct is not None,
        'reference_d2_in_actual_tree': correct is not None and any(tree.tokens[c - 1] == truth[1] for c in tree.children_of(correct)),
        'd1_pruned_rank_interval': d1_rank, 'd2_oracle_parent_pruned_rank_interval': d2_rank,
        'all_budget_to_d1_definite_coverage_only': d1_rank is not None and d1_rank[1] <= budget,
        'all_budget_to_d1_possible_coverage_only': d1_rank is not None and d1_rank[0] <= budget,
        'oracle_parent_d2_definite_coverage_only': correct is not None and d2_rank is not None and d2_rank[1] <= depth2_width,
        'oracle_parent_d2_possible_coverage_only': correct is not None and d2_rank is not None and d2_rank[0] <= depth2_width,
        'repeat_pruning_bans_d1': truth[0] == root}


def main():
    from analyze_4b_geometry import sha
    from spec_mtp.structure.algorithm.tree import DraftTree
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--study', required=True, type=Path)
    parser.add_argument('--windows', required=True, type=Path)
    parser.add_argument('--logits', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    assert not args.out.exists()
    torch.set_num_threads(1)
    windows = json.loads(args.windows.read_text())
    assert windows['quality_passed'] and windows['private_logits_sha256'] == sha(args.logits)
    private = torch.load(args.logits, map_location='cpu', weights_only=True)
    raw_path = args.study / 'runs' / windows['reference_run'] / 'assets/decode_observations.json'
    assert sha(raw_path) == windows['reference_raw_sha256']
    evidence = json.loads(raw_path.read_text())['out']['evidence']
    prompts = json.loads((args.study / 'docs/prompts_manifest.json').read_text())['rendered_prompts']
    report = {'no_model_forward': True, 'analyzer_sha256': sha(__file__), 'windows_sha256': sha(args.windows),
              'private_logits_sha256': sha(args.logits), 'rows': [], 'comparisons': {}}
    for row in windows['rows']:
        qid, variant = row['question_id'], row['variant']
        index = next(i for i, p in enumerate(prompts) if p['question_id'] == qid)
        reference = evidence[index]['output_ids'][len(evidence[index]['input_ids']):]
        pos = row['next_root_index']
        logits = private[str(qid)][variant]['seed_logits']
        tree = DraftTree(**private[str(qid)][variant]['next_tree'])
        _, metrics = coverage(logits, reference[pos], reference[pos + 1:pos + 3], tree=tree)
        assert metrics['reference_d1_in_tree'] == row['reference_d1_in_tree']
        assert metrics['reference_d2_in_actual_tree'] == row['reference_d2_under_d1']
        report['rows'].append(dict(row, **{k: v for k, v in metrics.items() if k not in row}))
    methods = sorted({r['variant'] for r in report['rows']} - {'zero'})
    for method in methods:
        counts = Counter()
        for row in report['rows']:
            if row['variant'] == method:
                base = next(r for r in report['rows'] if r['variant'] == 'zero' and r['question_id'] == row['question_id'])
                delta = row['next_accept_depth'] - base['next_accept_depth']
                counts['win' if delta > 0 else 'loss' if delta < 0 else 'tie'] += 1
        report['comparisons'][method + '-zero'] = {key: counts[key] for key in ('win', 'tie', 'loss')}
    args.out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('PASS: saved GPU native trees verified; tie-aware candidate coverage bounds are not verified acceptance')


if __name__ == '__main__':
    main()
