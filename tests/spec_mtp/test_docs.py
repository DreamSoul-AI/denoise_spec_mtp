"""Relative links in tracked Markdown point at files that exist."""

import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LINK = re.compile(r'\]\(([^)#\s]+)(#[^)]*)?\)')


def test_relative_markdown_links_resolve():
    files = subprocess.check_output(['git', 'ls-files', '-z', '*.md'], cwd=ROOT, text=True, encoding='utf-8').rstrip('\0').split('\0')
    broken = []
    for name in files:
        text = (ROOT / name).read_text(encoding='utf-8')
        for match in LINK.finditer(text):
            target = match.group(1).strip('<>')
            if target.startswith(('http://', 'https://', 'mailto:')):
                continue
            if not (ROOT / os.path.dirname(name) / target).exists():
                broken.append(f'{name} -> {target}')
    assert not broken, broken
