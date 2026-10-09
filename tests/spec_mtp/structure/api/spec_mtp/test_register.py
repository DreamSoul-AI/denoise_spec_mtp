"""SpecMTP builders register on spec_mtp's own copied registries."""

import spec_mtp  # noqa: F401
from spec_mtp.structure.algorithm.factory import AlgorithmRegistry
from spec_mtp.structure.data.factory import DataRegistry
from spec_mtp.structure.model.factory import ModelRegistry


def test_eval_algorithm_is_registered():
    assert ('eval', 'spec_mtp') in AlgorithmRegistry.list()


def test_prompt_sets_are_registered():
    names = {name for name, source in DataRegistry.list() if source == 'spec_mtp'}
    assert {'specbench', 'local_prompts', 'dolly'} <= names


def test_models_are_registered():
    names = {name for name, source in ModelRegistry.list() if source == 'spec_mtp'}
    assert names == {'hf_causal', 'tiny_llama'}
