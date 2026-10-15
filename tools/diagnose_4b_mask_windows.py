"""Probe a fixed 4B prefix/tree with output interventions and an input control, without timing.

    python tools/diagnose_4b_mask_windows.py --study studies/qwen3_4b_bf16_five_methods --out .tmp/4b-mask-windows-v1
"""
import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import time
from types import SimpleNamespace
from unittest.mock import patch

import torch


VARIANTS = ('zero', 'input_first', 'first', 'shifted', 'radial', 'both')


def admission(initial=True):
    from analyze_4b_geometry import sha
    gpu = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free,memory.used',
                                   '--format=csv,noheader,nounits'], text=True).strip().split(', ')
    command = ("Get-CimInstance Win32_Process | Where-Object {$_.Name -eq 'python.exe'} | "
               'Select-Object ProcessId,ParentProcessId,CommandLine | ConvertTo-Json -Compress')
    raw = subprocess.check_output(['powershell', '-NoProfile', '-Command', command], text=True)
    processes = json.loads(raw) if raw.strip() else []
    if isinstance(processes, dict):
        processes = [processes]
    processes = [p for p in processes if p['ProcessId'] != os.getpid()]
    inspected = {
        'D:/GitHub/diaoenmao/RPipe/.tmp/systematic-contracts-20261015/watch-first.py':
            '08bd5e0fb31e1d7d453827879e5c82e6b84f708794bda8e2135357a75558ebce',
        'D:/GitHub/diaoenmao/RPipe/.tmp/systematic-contracts-20261015/watch-second.py':
            'c10313215b37de40ec62d6dd96ed6d4d5ef868a9f87cf21f6c6df9898d57516a',
        'D:/GitHub/DreamSoul/quantization/.tmp/paroquant-reference/build_official_container_v3.py':
            'bc206af76763f1364fe2565be1be8cf2294342aaa414f3b263cbf115dafcceec'}
    known = []
    for p in processes:
        cmd = p['CommandLine'] or ''
        if ('release-ci.py' in cmd or ('RPipe' in cmd and 'and not gpu and not slow' in cmd)
                or any(Path(name).name in cmd and Path(name).is_file() and sha(name) == digest
                       for name, digest in inspected.items())):
            known.append(p['ProcessId'])
    for _ in processes:
        children = [p['ProcessId'] for p in processes if p['ProcessId'] not in known and p.get('ParentProcessId') in known]
        if not children:
            break
        known.extend(children)
    unknown = [p['ProcessId'] for p in processes if p['ProcessId'] not in known]
    return {'passed': not unknown and (not initial or int(gpu[0]) >= 18 * 1024),
            'free_mib': int(gpu[0]), 'used_mib': int(gpu[1]), 'foreign_python_count': len(processes),
            'verified_cpu_count': len(known), 'unknown_python_count': len(unknown), 'initial': initial}


def intervention_masks(shadow, proxies, zero):
    """Native state simulation; only the slot offset and radial mapping vary."""
    a, v = shadow.anchor.clone(), shadow.velocity.clone()
    anchors, velocities = [], []
    for depth in range(3):
        if depth < 2:
            y = proxies[depth].detach().float()
            v = shadow.beta_prime * v + (1 - shadow.beta_prime) * (y - a)
            a = y
        else:
            a = a + v
        anchors.append(a)
        velocities.append(v)
    a, v = torch.stack(anchors)[:, None], torch.stack(velocities)[:, None]
    masks = {'zero': zero}
    for name in ('first', 'shifted', 'radial', 'both'):
        offset = int(name in ('shifted', 'both'))
        slots = a + (torch.arange(2, device=a.device) + offset)[None, :, None] * v
        norms = a.norm(dim=-1, keepdim=True) if name in ('radial', 'both') else slots.norm(dim=-1, keepdim=True)
        assert torch.isfinite(slots).all() and (norms > 0).all()
        masks[name] = (shadow.scale * slots / norms).to(zero.dtype)
    masks['first'] = shadow.masks_per_owner(proxies).to(zero.dtype)
    return masks


def walk(tree, logits):
    from spec_mtp.structure.algorithm.decoding import select_token
    owner, accepted, chosen = 0, [], []
    while True:
        token = select_token(logits[owner], 0., None)
        assert token == int(logits[owner].argmax())
        chosen.append(token)
        child = next((c for c in tree.children_of(owner) if tree.tokens[c - 1] == token), None)
        if child is None:
            return accepted, chosen
        accepted.append(child)
        owner = child


def active_predecessor(trace, prompt_length):
    for previous, current in zip(trace, trace[1:]):
        if current['accepted_nodes'] == [1]:
            return previous['root_position'] - prompt_length
    raise ValueError('No predefined top1-only control opportunity; do not replace the prompt')


@torch.no_grad()
def input_control(model, prompt, generated_prefix, spec):
    from spec_mtp.structure.algorithm.mask_providers import build_mask_provider
    from spec_mtp.structure.control.named import _convert
    provider = build_mask_provider(_convert(spec), model.embedding_table)
    embeds = model.embed(prompt)[0]
    provider.init_from_prompt(embeds)
    previous = embeds[-1]
    for token in generated_prefix:
        current = model.embedding_table[token]
        provider.on_token_committed(current, previous)
        previous = current
    return provider.masks().to(model.dtype)[None].expand(3, -1, -1).clone()


class WindowCaptured(Exception):
    pass


@torch.no_grad()
def capture_window(model, prompt, spec, eval_cfg, eos, seed, minimum=8):
    from spec_mtp.structure.algorithm import decoding
    from spec_mtp.structure.algorithm.output_masks import OutputHiddenMaskProvider
    from spec_mtp.structure.control.named import _convert
    original_build, original_tree = decoding.build_mask_provider, decoding.build_tree
    original_observe, original_masks = OutputHiddenMaskProvider.observe_committed, OutputHiddenMaskProvider.masks_per_owner
    active, packet, generated = {}, {}, []

    def build(*args, **kwargs):
        provider = original_build(*args, **kwargs)
        active.update(provider=provider, shadow=OutputHiddenMaskProvider(2, model.embedding_table, order=1, beta=.9, beta_prime=.99))
        return provider

    def observe(provider, hidden):
        original_observe(provider, hidden)
        if provider is active['provider']:
            original_observe(active['shadow'], hidden)

    def masks(provider, proxies):
        zero = original_masks(provider, proxies)
        if provider is active['provider']:
            active.update(proxies=proxies, zero=zero)
        return zero

    def tree_builder(*args, **kwargs):
        tree = original_tree(*args, **kwargs)
        active['tree'] = tree
        return tree

    def before(_module, args, kwargs):
        active['prefill'] = kwargs.get('attention_mask_4d') is None
        if not active['prefill']:
            root = int(args[1][0, 0]) - prompt.shape[1]
            if root >= minimum and not packet:
                packet.update(root_index=root, inputs=args[0].clone(), positions=args[1].clone(),
                    kwargs={**kwargs, 'past_key_values': deepcopy(kwargs['past_key_values'])}, tree=deepcopy(active['tree']),
                    masks=intervention_masks(active['shadow'], active['proxies'], active['zero'].to(model.dtype)))

    def after(_module, _args, _kwargs, output):
        if active['prefill']:
            generated.append(int(output.logits[0, prompt.shape[1] - 1].argmax()))
            return
        accepted, chosen = walk(active['tree'], output.logits[0])
        generated.extend(chosen)
        if packet:
            packet.update(baseline=output, prefix_generated=list(generated), accepted=accepted, chosen=chosen,
                          zero_provider=active['provider'])
            raise WindowCaptured()

    handles = [model.register_forward_pre_hook(before, with_kwargs=True), model.register_forward_hook(after, with_kwargs=True)]
    try:
        with patch.object(decoding, 'build_mask_provider', build), patch.object(decoding, 'build_tree', tree_builder), \
                patch.object(OutputHiddenMaskProvider, 'observe_committed', observe), \
                patch.object(OutputHiddenMaskProvider, 'masks_per_owner', masks), \
                patch.object(decoding, 'time', SimpleNamespace(perf_counter=lambda: 0.)):
            try:
                decoding.SpecDecoder(model, _convert(spec), _convert(dict(eval_cfg, max_new_tokens=32)), eos,
                    torch.Generator(device=model.device).manual_seed(seed)).generate(prompt)
            except WindowCaptured:
                pass
    finally:
        for handle in handles:
            handle.remove()
    assert packet and packet['root_index'] < 32, 'No admissible fixed window; do not choose a result-dependent replacement'
    return packet


@torch.no_grad()
def probe_window(model, packet, spec, reference):
    from spec_mtp.structure.algorithm import decoding, kv_cache
    from spec_mtp.structure.algorithm.tree_attention import DynamicTreeAttentionCache, mask_indices_of
    from spec_mtp.structure.control.named import _convert
    tree, baseline = packet['tree'], packet['baseline']
    accepted, chosen = packet['accepted'], packet['chosen']
    assert packet['prefix_generated'] == reference[:len(packet['prefix_generated'])]
    owner = accepted[-1] if accepted else 0
    seed_rows = mask_indices_of(tree, 2, owner)
    next_zero = packet['zero_provider'].masks_per_owner(baseline.last_hidden_state[0, seed_rows]).to(model.dtype)
    next_index = packet['root_index'] + len(chosen)
    assert next_index + 2 < len(reference) and chosen[-1] == reference[next_index]
    truth = reference[next_index + 1:next_index + 3]
    rows, local = [], {}
    for name in VARIANTS:
        inputs = packet['inputs'].clone()
        inputs[0, 1 + tree.num_nodes:] = packet['masks'][name][[0] + tree.depths].reshape(-1, inputs.shape[-1])
        kwargs = {**packet['kwargs'], 'past_key_values': deepcopy(packet['kwargs']['past_key_values'])}
        output = model(inputs, packet['positions'], **kwargs)
        assert torch.equal(output.logits[0, :1 + tree.num_nodes].argmax(-1), baseline.logits[0, :1 + tree.num_nodes].argmax(-1))
        current_accepted, current_chosen = walk(tree, output.logits[0])
        assert current_accepted == accepted and current_chosen == chosen
        logits = output.logits[0, seed_rows]
        probs = decoding.tree_probs(logits, 0.)
        next_tree = decoding.build_tree(_convert(spec), probs, chosen[-1])
        cache = output.past_key_values
        length = int(packet['positions'][0, 0])
        kv_cache.keep_block_positions(cache, length, [0] + accepted)
        next_position = length + len(chosen)
        assert kv_cache.cache_len(cache) == next_position
        ids = torch.tensor([[chosen[-1]] + next_tree.tokens], device=model.device)
        embeds = model.embed(ids)[0]
        owner_masks = next_zero[[0] + next_tree.depths].reshape(-1, embeds.shape[-1])
        block = torch.cat([embeds, owner_masks])[None]
        attn, positions = DynamicTreeAttentionCache().get(next_tree, 2, next_position, next_position,
                                                         model.dtype, model.device, model.min_mask_value())
        verified = model(block, positions, attention_mask_4d=attn, past_key_values=cache)
        next_accepted, next_chosen = walk(next_tree, verified.logits[0])
        matching = next((c for c in next_tree.children_of(0) if next_tree.tokens[c - 1] == truth[0]), None)
        ranks = [1 + int((logits[j] > logits[j, truth[j]]).sum()) for j in (0, 1)]
        row = {'variant': name, 'root_index': packet['root_index'], 'source_owner_depth': len(accepted),
               'next_root_index': next_index, 'mask_logit_target_ranks': ranks,
               'mask_logit_target_probs': [float(probs[j, truth[j]]) for j in (0, 1)],
               'next_tree_widths': next_tree.branch_widths(), 'reference_d1_in_tree': matching is not None,
               'reference_d2_under_d1': matching is not None and any(next_tree.tokens[c - 1] == truth[1] for c in next_tree.children_of(matching)),
               'current_owner_argmax_unchanged': True, 'next_accept_depth': len(next_accepted),
               'next_root_argmax_matches_reference': next_chosen[0] == truth[0],
               'next_verified_chain_equals_reference': next_chosen == reference[next_index + 1:next_index + 1 + len(next_chosen)],
               'argmax_passed': True, 'argmax_checked_tokens': len(chosen) + len(next_chosen)}
        rows.append(row)
        local[name] = {'seed_logits': logits.detach().cpu(), 'next_tree': vars(next_tree), 'next_chosen': next_chosen}
    for row in rows:
        row['d1_seed_logits_equal_zero'] = torch.equal(local[row['variant']]['seed_logits'][0], local['zero']['seed_logits'][0])
    assert rows[0]['next_verified_chain_equals_reference'], 'Zero-control continuation differs from old Run; stop, no numerical study'
    return rows, local


def main():
    from analyze_4b_geometry import sha
    from spec_mtp.structure.artifact.sources import manifest
    from spec_mtp.structure.artifact.evidence import model_digest, runtime
    from spec_mtp.structure.model.hf_causal import HFCausalLM
    from transformers import AutoModelForCausalLM
    from rpipe.structure.system.runtime import apply_runtime
    from rpipe.structure.system.config import SystemConfig
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--study', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--active-depth', action='store_true', help='Separate conditioned q121/q401 protocol; not a random-sample extension')
    args = parser.parse_args()
    assert not args.out.exists()
    args.out.mkdir(parents=True)
    qids, limit = ((121, 401), 64) if args.active_depth else ((121, 401, 241, 161), 128)
    plan = 'MASK_ACTIVE_PLAN.md' if args.active_depth else 'MASK_WINDOW_PLAN.md'
    report = {'status': 'preflight', 'quality_passed': False, 'admission': [], 'rows': [], 'model_calls': 0,
              'forward_limit': limit, 'no_timing': True, 'no_8b': True, 'tool_sha256': sha(__file__),
              'sample_mode': 'conditioned_top1_only' if args.active_depth else 'unconditioned_first_root_ge8',
              'plan_sha256': sha(args.study / ('docs/' + plan))}
    def save():
        (args.out / 'windows.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    local = {}
    try:
        for _ in range(2):
            check = admission()
            report['admission'].append(check)
            if not check['passed']:
                report['status'] = 'deferred_nonpreemptive_admission'
                save()
                return
            time.sleep(5)
        study = args.study
        paired = json.loads((study / 'docs/paired_evidence_v1.json').read_text())
        prompts = json.loads((study / 'docs/prompts_manifest.json').read_text())
        cell = paired['cells']['30/output_zero']
        raw_path = study / 'runs' / cell['run_id'] / 'assets/decode_observations.json'
        assert sha(raw_path) == cell['files_sha256']['assets/decode_observations.json']
        raw = json.loads(raw_path.read_text())['out']['evidence']
        snapshot = json.loads((study / 'docs/modelscope_snapshot.json').read_text())
        cache = study / 'shared/model/modelscope/Qwen/Qwen3-4B'
        for f in snapshot['files']:
            assert sha(cache / f['path']) == f['sha256']
        check = admission()
        report['admission'].append(check)
        if not check['passed']:
            report['status'] = 'deferred_after_model_hash_check'
            save()
            return
        assert manifest()['digest'] == '538e52c929a542a8'
        apply_runtime(123, SystemConfig.from_mapping({'config': {'deterministic': False}}))
        torch.set_num_threads(1)
        load = AutoModelForCausalLM.from_pretrained
        with patch.object(AutoModelForCausalLM, 'from_pretrained', side_effect=lambda *a, **kw: load(*a, **dict(kw, device_map='cuda'))):
            model = HFCausalLM(str(cache), local_files_only=True, torch_dtype='bfloat16', attn_implementation='eager')
        assert model.device.type == 'cuda' and model.dtype == torch.bfloat16
        assert model.embedding_table.data_ptr() == model.hf.get_output_embeddings().weight.data_ptr()
        assert model_digest(model) == cell['model_digest']
        report.update(source_digest=manifest()['digest'], model_digest=cell['model_digest'], runtime=runtime(),
                      reference_run=cell['run_id'], reference_raw_sha256=sha(raw_path))
        def count(_module, _args):
            report['model_calls'] += 1
            assert report['model_calls'] <= limit
        handle = model.register_forward_pre_hook(count)
        try:
            for qid in qids:
                check = admission(initial=False)
                report['admission'].append(check)
                assert check['passed'], 'New foreign work; stop this diagnostic'
                index = next(i for i, p in enumerate(prompts['rendered_prompts']) if p['question_id'] == qid)
                p = prompts['rendered_prompts'][index]
                assert p['input_ids'] == raw[index]['input_ids']
                seed = cell['rows'][index]['generator_seed']
                apply_runtime(seed, SystemConfig.from_mapping({'config': {'deterministic': False}}))
                ids = torch.tensor([p['input_ids']], device=model.device)
                minimum = active_predecessor(raw[index]['stats']['trace'], len(p['input_ids'])) if args.active_depth else 8
                if args.active_depth:
                    assert minimum == {121: 3, 401: 19}[qid]
                packet = capture_window(model, ids, cell['actual_settings']['spec'], cell['actual_settings']['eval'], prompts['eos_token_ids'], seed, minimum=minimum)
                packet['masks']['input_first'] = input_control(model, ids,
                    raw[index]['output_ids'][len(p['input_ids']):len(p['input_ids']) + packet['root_index'] + 1],
                    paired['cells']['30/input_first']['actual_settings']['spec'])
                rows, tensors = probe_window(model, packet, cell['actual_settings']['spec'], raw[index]['output_ids'][len(p['input_ids']):])
                if args.active_depth:
                    control = tensors['zero']
                    assert packet['root_index'] == minimum and rows[0]['next_accept_depth'] == 1
                    assert len(rows[0]['next_tree_widths']) == 2 and rows[0]['next_tree_widths'][1] > 0
                    assert control['next_tree']['tokens'][0] == control['next_chosen'][0]
                for row in rows:
                    row['question_id'] = qid
                report['rows'].extend(rows)
                local[str(qid)] = tensors
                save()
                print(qid, 'six fixed-window variants passed', flush=True)
                del packet
        finally:
            handle.remove()
        assert len(report['rows']) == len(qids) * 6 and manifest()['digest'] == report['source_digest']
        torch.save(local, args.out / 'private_logits.pt')
        report.update(status='complete', quality_passed=True, private_logits_sha256=sha(args.out / 'private_logits.pt'))
    except Exception as error:
        report.update(status='failed_preserved', error=repr(error))
        save()
        raise
    save()
    print('Complete:', len(report['rows']), 'local interventions; no full generation or timing', flush=True)


if __name__ == '__main__':
    main()
