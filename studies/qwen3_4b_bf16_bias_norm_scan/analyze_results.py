"""CPU-only native readout of eight norm cells and the five reused endpoints."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[2]
STUDY = Path(__file__).resolve().parent
BASE = ROOT / 'studies/qwen3_4b_bf16_five_methods'
sys.path.insert(0, str(ROOT / 'tools'))
import analyze_4b_full_directions as directions  # noqa: E402
_spec = importlib.util.spec_from_file_location('norm_pair_readout', BASE / 'analyze_results.py')
_pair = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pair)


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()



def depth_rows(raw, prompts):
    assert len(raw) == len(prompts)
    rows = []
    for item, prompt in zip(raw, prompts):
        assert item['input_ids'] == prompt['input_ids']
        stats = item['stats']
        assert stats['prefill_calls'] == 1 and len(stats['trace']) == stats['decode_calls']
        prefix = item['output_ids'][:len(prompt['input_ids']) + 1]
        assert len(prefix) == len(prompt['input_ids']) + 1
        rows.append({'question_id': prompt['question_id'],
            'initial_prefix_sha256': hashlib.sha256(json.dumps(prefix).encode()).hexdigest(),
            'attempt_by_depth': stats['attempt_by_depth'], 'accept_by_depth': stats['accept_by_depth'],
            'first_block_accepted': len(stats['trace'][0]['accepted_nodes']) if stats['trace'] else None})
    return rows


def first_block_compare(first, second):
    assert len(first) == len(second)
    result = {'total': len(first), 'same_prefix_with_block': 0, 'different_prefix': 0,
              'missing_block': 0, 'accepted': {'win': 0, 'tie': 0, 'loss': 0}}
    for a, b in zip(first, second):
        assert a['question_id'] == b['question_id']
        if a['first_block_accepted'] is None or b['first_block_accepted'] is None:
            result['missing_block'] += 1
        elif a['initial_prefix_sha256'] != b['initial_prefix_sha256']:
            result['different_prefix'] += 1
        else:
            result['same_prefix_with_block'] += 1
            delta = b['first_block_accepted'] - a['first_block_accepted']
            result['accepted']['win' if delta > 0 else 'loss' if delta < 0 else 'tie'] += 1
    assert sum(result['accepted'].values()) == result['same_prefix_with_block']
    return result


def plot(cells, means, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    x = [0., .5, 1., 2.]
    zero = cells['zero/0']['totals']['pooled_tau']
    fig, ax = plt.subplots(figsize=(8, 5), layout='constrained')
    try:
        for mode in ('template', 'random0', 'random1', 'random2'):
            y = [zero] + [cells[f'{mode}/{scale:g}']['totals']['pooled_tau'] for scale in x[1:]]
            ax.plot(x, y, marker='o', label=mode)
        ax.plot(x, [zero] + [means[f'{scale:g}'] for scale in x[1:]], 'k--', label='three-random mean')
        ax.set(xlabel='Native step_scale / original direction norm multiplier',
               ylabel='Pooled committed / decode calls', xticks=x, title='Fixed480, Qwen3-4B BF16/T0, BC30')
        ax.legend()
        fig.supxlabel('0 and1 reuse frozen evidence; only0.5 and2 are new. Output lengths may differ; no speed claim.')
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=160)
    finally:
        plt.close(fig)

def main():
    from norm_control import check_refs
    from rpipe.structure.artifact.provenance import check_frozen as pcheck
    from rpipe.structure.make.expand import load_study_yaml
    from spec_mtp.structure.artifact.sources import check_frozen, manifest
    check_refs()
    decl = load_study_yaml(STUDY)
    check_frozen(STUDY, decl, manifest())
    pcheck(STUDY, decl)
    formal = read(BASE / 'docs/paired_evidence_v1.json')
    original = read(ROOT / 'studies/qwen3_4b_bf16_directions/docs/direction_evidence_v1.json')
    prompts, snapshot = (read(BASE / 'docs' / n) for n in ('prompts_manifest.json', 'modelscope_snapshot.json'))
    old_ar = formal['cells']['AR']
    arpath = BASE / 'runs' / old_ar['run_id'] / 'assets/decode_observations.json'
    assert sha(arpath) == old_ar['files_sha256']['assets/decode_observations.json']
    reference = [{'question_id': p['question_id'], 'output_ids': r['output_ids'][len(p['input_ids']):],
                  'model_calls': r['stats']['ar_calls']} for p, r in zip(prompts['rendered_prompts'], read(arpath)['out']['evidence'])]
    assert len(reference) == 480
    cells = {'zero/0': dict(original['cells']['zero'], reused=True)}
    for mode in ('template', 'random0', 'random1', 'random2'):
        cells[mode + '/1'] = dict(original['cells'][mode], reused=True)
    for cell in cells.values():
        owner = ROOT / cell.get('study_path', 'studies/qwen3_4b_bf16_five_methods')
        path = owner / 'runs' / cell['run_id'] / 'assets/decode_observations.json'
        assert sha(path) == cell['files_sha256']['assets/decode_observations.json']
        cell['depth_rows'] = depth_rows(read(path)['out']['evidence'], prompts['rendered_prompts'])
    for exp in read(STUDY / 'index.json')['experiments']:
        setting = exp['factors']['algorithm.config']
        mode, scale = setting['direction'], setting['spec']['ema']['step_scale']
        name = f'{mode}/{scale:g}'
        assert name not in cells and len(exp['runs']) == 1
        folder = STUDY / 'runs' / exp['runs'][0]['id']
        result = read(folder / 'result.json') if (folder / 'result.json').exists() else {}
        cells[name] = {'run_id': folder.name, 'native_status': result.get('status', 'pending')}
        if result.get('status') != 'succeeded':
            continue
        cfg = yaml.safe_load((folder / 'config.yaml').read_text(encoding='utf-8'))
        assert cfg['seed'] == 123 and cfg['algorithm']['config']['direction'] == mode
        assert cfg['algorithm']['config']['spec']['ema']['step_scale'] == scale
        cell, _ = _pair.load_cell(STUDY, folder, cfg, prompts['rendered_prompts'], prompts, snapshot, reference)
        assert cell['model_digest'] == formal['cells']['30/input_first']['model_digest']
        assert cell['runtime'] == formal['cells']['30/input_first']['runtime']
        progress = read(folder / 'assets/norm_progress.json')
        assert progress['completed'] == len(progress['rows']) == 480
        assert progress['direction'] == mode and progress['step_scale'] == scale
        for p, r, canonical in zip(progress['rows'], cell['rows'], prompts['rendered_prompts']):
            assert p['question_id'] == r['question_id'] == canonical['question_id']
            assert all(p[k] == r[k] for k in ('accepted', 'committed', 'decode_calls', 'new_tokens', 'argmax_checked_tokens'))
            assert p['bias']['step_scale'] == scale and p['bias']['full_prompt_mean_preserved']
        cell.update(progress_sha256=sha(folder / 'assets/norm_progress.json'),
            bias_and_depth_rows=[{k: v for k, v in r.items() if k != 'gpu_admission'} for r in progress['rows']])
        cell['depth_rows'] = depth_rows(read(folder / 'assets/decode_observations.json')['out']['evidence'], prompts['rendered_prompts'])
        cells[name] = cell
    ready = all('rows' in cell for cell in cells.values())
    pairs = []
    for name, cell in cells.items():
        if 'rows' not in cell:
            continue
        cell['totals']['category_mean_pooled_tau'] = directions.category_mean(cell['rows'])
        if name == 'zero/0':
            continue
        mode = name.split('/')[0]
        for base in ('zero/0', mode + '/1'):
            pairs.append(dict(first=base, second=name,
                first_block_same_prefix=first_block_compare(cells[base]['depth_rows'], cell['depth_rows']),
                **directions.compare(cells[base]['rows'], cell['rows'])))
    means = {}
    for scale in (.5, 1., 2.):
        rows = [cells[f'random{i}/{scale:g}'] for i in range(3)]
        if all('rows' in c for c in rows):
            means[f'{scale:g}'] = sum(c['totals']['pooled_tau'] for c in rows) / 3
    if ready:
        native = read(STUDY / 'spec_mtp_study_check.json')
        process = read(STUDY / 'process.json')
        assert native['passed'] and native['complete'] and process['complete'] and process['spec_mtp']['passed']
    body = {'complete': ready, 'author_official': False, 'no_timing': True, 'fixed_prompts': 480,
        'budget': 30, 'mask_count': 2, 'new_cells': 8, 'reused_cells': 5,
        'source_refs_sha256': sha(STUDY / 'docs/source_refs.json'), 'analyzer_sha256': sha(Path(__file__)),
        'paired_formal_sha256': sha(BASE / 'docs/paired_evidence_v1.json'),
        'direction_formal_sha256': sha(ROOT / 'studies/qwen3_4b_bf16_directions/docs/direction_evidence_v1.json'),
        'cells': cells, 'paired_comparisons': pairs, 'random_three_seed_mean_pooled_tau': means}
    target = STUDY / 'docs' / ('norm_evidence_v1.json' if ready else 'norm_pending.json')
    text = json.dumps(body, indent=2, allow_nan=False) + '\n'
    if ready and target.exists():
        assert target.read_text(encoding='utf-8') == text
    else:
        target.write_text(text, encoding='utf-8')
    if ready:
        plot(cells, means, STUDY / 'docs/figures/bc30_norm_scan.png')
    print(json.dumps({'complete': ready, 'valid_cells': sum('rows' in c for c in cells.values())}))


if __name__ == '__main__':
    main()
