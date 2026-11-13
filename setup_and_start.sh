#!/usr/bin/env bash
# ============================================================================
# AI HOLDING COMPANY V8 — macOS / Linux One-Click Setup & Launch Script
# ============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🏝️ ========================================================="
echo "   AI Holding Company V8 (Portable Edition) — macOS Launcher"
echo "========================================================="

# 1. Virtual Environment Setup
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment (venv)..."
    python3 -m venv venv
fi

echo "📦 Upgrading pip and installing dependencies..."
./venv/bin/pip install --upgrade pip --quiet
./venv/bin/pip install -r requirements.txt --quiet

# 2. Check environment config
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env configuration from .env.example..."
    cp .env.example .env
fi

# 3. Offline shift auto-catchup
echo "⚡ Running Offline Shift Catchup & Obsidian Graph Sync..."
./venv/bin/python3 main.py --capital 1000 --risk 1.5 || true

# 4. Launch web application
PORT=${PORT:-8080}
echo ""
echo "🚀 Launching AI Company Web Server at http://localhost:$PORT"
echo "   Press Ctrl+C to stop the server."
echo ""
./venv/bin/python3 server.py --port "$PORT" --capital 1000 --risk 1.5 --interval 45
