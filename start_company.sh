#!/usr/bin/env bash
# ============================================================================
# AI HOLDING COMPANY V8 — Quick Start Server
# ============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f "venv/bin/python3" ]; then
    PYTHON_BIN="venv/bin/python3"
else
    PYTHON_BIN="python3"
fi

PORT=${PORT:-8080}
echo "🚀 Starting AI Holding Company Server on http://localhost:$PORT..."
exec $PYTHON_BIN server.py --port "$PORT" --capital 1000 --risk 1.5 --interval 45
