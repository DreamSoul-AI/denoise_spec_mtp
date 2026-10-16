"""Relative links, including spaced angle targets, resolve in repo-owned Markdown."""

import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
LINK = re.compile(r'\]\((?:<([^>]+)>|([^\s)]+))\)')
# These four byte-pinned upstream texts retain DEM-only references documented in their README.
PINNED_STANDARDS = {
    'docs/research/standards/研究计划规范 Research Plan Standard.md',
    'docs/research/standards/研究计划模板 Research Plan Template.md',
    'docs/research/standards/research_plan_standard_en.md',
    'docs/research/standards/research_plan_template_en.md',
}


def test_relative_markdown_links_resolve():
    files = subprocess.check_output(['git', 'ls-files', '-z', '*.md'], cwd=ROOT, text=True, encoding='utf-8').rstrip('\0').split('\0')
    broken = []
    for name in files:
        text = (ROOT / name).read_text(encoding='utf-8')
        for match in LINK.finditer(text):
            raw = match[1] or match[2]
            if raw.startswith(('http://', 'https://', 'mailto:', '#', 'data:', 'file:')):
                continue
            target = unquote(raw.partition('#')[0])
            if name in PINNED_STANDARDS and target in {'../文献调研/文献调研规范 Literature Review Standard.md', '../../开发/通用调研规范 General Research Standard.md', '../../../../../研发/研究/校准 Calibration/校准 Calibration 文献调研 Literature Review 大纲.md'}:
                continue
            if not (ROOT / name).parent.joinpath(target).exists():
                broken.append(f'{name} -> {target}')
    assert not broken, broken


def test_one_bilingual_project_plan_preserves_all_historical_sources():
    manifest = json.loads((ROOT / 'docs/research/plan-consolidation-manifest.json').read_text(encoding='utf-8'))
    plans = [ROOT / manifest[key] for key in ('canonical_cn', 'canonical_en')]
    contents = [p.read_text(encoding='utf-8') for p in plans]
    assert len(manifest['plans']) == 60
    for item in manifest['plans']:
        assert not (ROOT / item['source_path']).exists()
        assert all(f'id="{item["anchor"]}"' in text for text in contents)
    assert 'translation in progress' not in contents[1]


def test_historical_plan_hashes_resolve_without_standalone_files(monkeypatch):
    import pytest

    monkeypatch.syspath_prepend(str(ROOT / 'tools'))
    from diagnose_output_windows import file_hash

    manifest = json.loads((ROOT / 'docs/research/plan-consolidation-manifest.json').read_text(encoding='utf-8'))
    for item in manifest['plans']:
        assert file_hash(ROOT / item['source_path']) == item['source_sha256']
    with pytest.raises(FileNotFoundError):
        file_hash(ROOT / 'docs/nonexistent-unregistered-plan.md')
