#!/usr/bin/env bash
# CPU-only correctness checks: mask providers, trees, tree attention
# (naive == efficient), and end-to-end losslessness vs AR decoding.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONUTF8=1
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/src"
python tests/spec_mtp/spec/test_correctness.py
