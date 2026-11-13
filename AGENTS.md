# 🤖 AI Agent Workspace Guidelines & Operating Rules

## 🎯 Workspace Structure & Architecture
This workspace has been structured for **Multi-Agent Concurrent Software Engineering**, allowing isolated feature development, cross-subagent coordination, and automated gate verification.

### 1. Directory Blueprint
```text
AI-Holding-Company-V8-Portable/
├── .agent-memory/                 # Central Brain & Persistent Memory for Sub-Agents
│   ├── orchestrator/MEMORY.md     # Gate controller & cross-agent synchronization
│   ├── backend-engine/MEMORY.md   # Core engines, database, server, APIs
│   ├── frontend-ui/MEMORY.md      # Isometric 3D, themes, dashboard components
│   ├── quant-analyst/MEMORY.md    # XAUUSD quantitative analysis & MT5
│   └── qa-tester/MEMORY.md        # Pytest suite & quality assurance
├── .claude/agent-memory -> ../.agent-memory (Symlink for Claude Code compatibility)
├── .gemini/agent-memory -> ../.agent-memory (Symlink for Antigravity compatibility)
├── .worktrees/                    # Isolated git worktrees for parallel agent development
├── scripts/
│   └── worktree_manager.sh        # Worktree creation, sync check, and cleanup
├── setup_and_start.sh             # One-click launch for macOS / Linux
├── start_company.sh               # Quick-start web server
├── run_tests.sh                   # Pytest runner (PYTHONPATH configured)
├── push_to_github.sh              # Safe sync to GitHub
└── AI-Holding-Company.code-workspace
```

## 🌿 Git Branching & Worktree Protocol
When agents work on tasks, follow this protocol:
1. **Branch Naming**:
   - `orchestrator/<feature-or-gate>`
   - `backend/<feature-name>`
   - `frontend/<ui-improvement>`
   - `quant/<strategy-adjustment>`
   - `test/<verification-task>`
2. **Worktree Creation**:
   ```bash
   ./scripts/worktree_manager.sh create backend/cache-optimizer
   ```
3. **Status Check & Gate Verification**:
   ```bash
   ./scripts/worktree_manager.sh status
   ./scripts/worktree_manager.sh merge-check backend/cache-optimizer
   ```
4. **Merge Requirement (Quality Gate)**:
   - All 7 automated pytest tests must pass: `./run_tests.sh`
   - Memory log in `.agent-memory/<role>/MEMORY.md` must be updated.

## ⚡ Quick Start Commands (macOS)
- **Run full setup and launch**: `./setup_and_start.sh`
- **Run tests**: `./run_tests.sh`
- **Start server only**: `./start_company.sh`
- **Open Web App**: [http://localhost:8080](http://localhost:8080)
