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

# Read GITHUB_TOKEN or GH_TOKEN from .env if present
if [ -f ".env" ]; then
    ENV_TOKEN=$(grep -E '^(GITHUB_TOKEN|GH_TOKEN)=' .env | head -n 1 | cut -d'=' -f2- | tr -d '\r"' | tr -d "'")
    if [ -n "$ENV_TOKEN" ]; then
        GITHUB_TOKEN="$ENV_TOKEN"
    fi
fi

CLEAN_REMOTE="https://github.com/Salmonnnnnn/AI-Holding-Company-V8-Portable.git"

if [ -n "$GITHUB_TOKEN" ]; then
    AUTH_REMOTE="https://Salmonnnnnn:${GITHUB_TOKEN}@github.com/Salmonnnnnn/AI-Holding-Company-V8-Portable.git"
    echo "🔑 Found GITHUB_TOKEN. Pushing via authenticated remote..."

    # Configure authenticated remote temporarily
    git remote set-url origin "$AUTH_REMOTE" 2>/dev/null || git remote add origin "$AUTH_REMOTE"

    # Ensure remote is always reset back to clean URL on script exit or interruption
    cleanup() {
        git remote set-url origin "$CLEAN_REMOTE" 2>/dev/null || true
    }
    trap cleanup EXIT

    git push -u origin HEAD || git push origin main --force || echo "Push failed or already up-to-date."

    cleanup
    trap - EXIT
    echo "🔒 Git remote restored to clean URL."
else
    echo "ℹ️ No GITHUB_TOKEN found; pushing via default git credentials..."
    git push origin HEAD || echo "Push failed or already up-to-date."
fi

echo "✅ Done!"
