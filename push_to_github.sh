#!/usr/bin/env bash
# ============================================================================
# AI HOLDING COMPANY V8 — Sync & Push to GitHub (macOS)
# ============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Syncing AI Holding Company to GitHub..."
git status --short

COMMIT_MSG="${1:-Update AI Holding Company progress and memory}"
git add .
git commit -m "$COMMIT_MSG" || echo "No changes to commit."
git push origin HEAD || echo "Push failed or already up-to-date."

echo "✅ Done!"
