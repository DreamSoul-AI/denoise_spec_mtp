"""Prompt windows and the synthetic set. No SpecBench download."""

from types import SimpleNamespace

from spec_mtp.structure.data.spec_mtp.local_prompts import load_records
from spec_mtp.structure.data.spec_mtp.registry import _build
from spec_mtp.structure.data.spec_mtp.specbench import window_by_category


def test_window_is_per_category_in_name_order():
    questions = [
        {'category': 'b', 'question_id': 1},
        {'category': 'b', 'question_id': 2},
        {'category': 'a', 'question_id': 3},
        {'category': 'a', 'question_id': 4},
        {'category': 'a', 'question_id': 5},
    ]
    window = window_by_category(questions, skip=1, take=1)
    assert [item['question_id'] for item in window] == [4, 2]


def test_synthetic_prompts_are_seeded():
    cfg = {'mode': 'synthetic', 'num_prompts': 2, 'prompt_len': 4, 'vocab_size': 32, 'seed': 7}
    first = load_records(cfg)
    second = load_records(cfg)
    assert len(first) == 2
    assert first[0]['input_ids'].shape == (1, 4)
    assert (first[0]['input_ids'] == second[0]['input_ids']).all()


def test_registry_builds_synthetic_prompts_without_a_tokenizer():
    config = SimpleNamespace(name='local_prompts', config={
        'mode': 'synthetic', 'num_prompts': 3, 'prompt_len': 4, 'vocab_size': 16, 'seed': 1,
    })
    data = _build(config, None)
    assert data.source == 'spec_mtp'
    assert data.meta['prompt_count'] == 3
