#!/usr/bin/env bash
# ============================================================================
# AI HOLDING COMPANY V8 — Automated Test Suite Runner
# ============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f "venv/bin/python3" ]; then
    PYTHON_BIN="venv/bin/python3"
else
    PYTHON_BIN="python3"
fi

echo "🧪 Running 7/7 automated pytest suite..."
PYTHONPATH=. $PYTHON_BIN -m pytest tests/test_committee.py -v "$@"
