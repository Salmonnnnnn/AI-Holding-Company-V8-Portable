#!/usr/bin/env bash
# ============================================================================
# Git Worktree Manager for Multi-Agent Concurrent Development
# Allows AI sub-agents to develop features concurrently in isolated branches
# ============================================================================
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKTREE_DIR="$REPO_ROOT/.worktrees"
mkdir -p "$WORKTREE_DIR"

command_usage() {
    echo "Usage: $0 {create|list|status|merge-check|remove} [branch_name]"
    echo ""
    echo "Commands:"
    echo "  create <name>       Create an isolated worktree under .worktrees/<name>"
    echo "  list                List all active worktrees and branch tracking"
    echo "  status              Show current worktree/branch revision count vs main"
    echo "  merge-check <name>  Verify branch readiness, diff stats & gate check"
    echo "  remove <name>       Safely remove a worktree"
    exit 1
}

ACTION="$1"
BRANCH="$2"

case "$ACTION" in
    create)
        if [ -z "$BRANCH" ]; then
            echo "❌ Error: Branch name required. Example: $0 create feature/backend-cache"
            exit 1
        fi
        CLEAN_NAME=$(echo "$BRANCH" | tr '/' '-')
        TARGET_PATH="$WORKTREE_DIR/$CLEAN_NAME"

        if [ -d "$TARGET_PATH" ]; then
            echo "⚠️ Worktree already exists at $TARGET_PATH"
            exit 0
        fi

        echo "🌿 Creating worktree for branch '$BRANCH' at $TARGET_PATH..."
        cd "$REPO_ROOT"
        
        # Check if branch exists
        if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
            git worktree add "$TARGET_PATH" "$BRANCH"
        else
            git worktree add -b "$BRANCH" "$TARGET_PATH" HEAD
        fi

        # Link venv and .env for zero-config worktree execution
        if [ -d "$REPO_ROOT/venv" ]; then
            ln -s "$REPO_ROOT/venv" "$TARGET_PATH/venv" 2>/dev/null || true
        fi
        if [ -f "$REPO_ROOT/.env" ]; then
            ln -s "$REPO_ROOT/.env" "$TARGET_PATH/.env" 2>/dev/null || true
        fi

        echo "✅ Worktree created successfully!"
        echo "📂 Path: $TARGET_PATH"
        ;;

    list)
        echo "📋 Active Git Worktrees:"
        cd "$REPO_ROOT"
        git worktree list
        ;;

    status)
        cd "$REPO_ROOT"
        CURRENT_BRANCH=$(git branch --show-current)
        echo "📍 Current Branch: $CURRENT_BRANCH"
        echo "🔍 HEAD commit: $(git rev-parse --short HEAD)"
        if git show-ref --verify --quiet "refs/heads/main"; then
            echo "📊 Commits (main...HEAD) [behind / ahead]:"
            git rev-list --left-right --count main...HEAD
            echo "📝 Diff stat vs main:"
            git diff --stat main..HEAD || true
        fi
        echo "📌 Working Tree Status:"
        git status --short
        ;;

    merge-check)
        if [ -z "$BRANCH" ]; then
            echo "❌ Error: Branch name required. Example: $0 merge-check feature/backend-cache"
            exit 1
        fi
        cd "$REPO_ROOT"
        echo "🔍 Checking branch '$BRANCH' against 'main'..."
        echo "Revisions behind/ahead (main...$BRANCH):"
        git rev-list --left-right --count main..."$BRANCH"
        echo ""
        echo "Diff summary:"
        git diff --stat main..."$BRANCH"
        ;;

    remove)
        if [ -z "$BRANCH" ]; then
            echo "❌ Error: Branch or worktree name required."
            exit 1
        fi
        CLEAN_NAME=$(echo "$BRANCH" | tr '/' '-')
        TARGET_PATH="$WORKTREE_DIR/$CLEAN_NAME"
        cd "$REPO_ROOT"
        if [ -d "$TARGET_PATH" ]; then
            echo "🗑️ Removing worktree at $TARGET_PATH..."
            git worktree remove "$TARGET_PATH" --force || true
        fi
        git worktree prune
        echo "✅ Worktree removed and pruned."
        ;;

    *)
        command_usage
        ;;
esac
