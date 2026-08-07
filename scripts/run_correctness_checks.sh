#!/usr/bin/env bash
# CPU-only correctness checks: mask providers, trees, tree attention
# (naive == efficient), and end-to-end losslessness vs AR decoding.
set -euo pipefail
cd "$(dirname "$0")/.."
python tests/check_correctness.py
