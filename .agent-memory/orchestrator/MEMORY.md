# 🏛️ Orchestrator Memory & Mission Log

## 🎯 Executive Overview
- **Project**: AI Holding Company V8 (Portable Edition)
- **Architecture**: Autonomous Multi-Agent Gold Trading Firm & 24/7 Virtual Enterprise
- **Core Mission**: Maintain stability across 11 AI specialists, manage token budget, orchestrate feature branches, and guarantee 100% test pass rate.

## 👥 Sub-Agent Registry & Responsibilities
| Role | Domain | Primary Focus |
|---|---|---|
| **`orchestrator`** | Cross-Agent Governance | Gate reviews, git worktree merging, high-level task planning |
| **`backend-engine`** | `engine/`, `data/`, `server.py` | Virtual office loop, LLM router, DB operations, Offline Catchup |
| **`frontend-ui`** | `engine/dashboard_generator.py` | Isometric cutaway office 3D, WebGL, themes, live dashboard |
| **`quant-analyst`** | `agents/`, `engine/mt5_executor.py` | XAUUSD technicals, macro news, Kelly sizing, MT5 execution |
| **`qa-tester`** | `tests/` | 7/7 automated pytest suite, simulation integrity, regression tests |

## 🛡️ Gate Merge Protocol (Definition of Done)
1. **Pass Test Suite**: `PYTHONPATH=. pytest tests/test_committee.py -v` must return 7/7 PASSED.
2. **Worktree Cleanliness**: Feature branch must be isolated in `.worktrees/<branch-name>`.
3. **Diff Review**: Inspect `git diff --stat main..<branch>` before merging.
4. **Memory Synchronization**: Update corresponding `MEMORY.md` in `.agent-memory/` upon task completion.

## 📌 Active Initiatives & Roadmap
- [x] Initial portable migration & setup (V8).
- [x] macOS / POSIX native execution environment (`setup_and_start.sh`, `venv`).
- [x] Multi-Agent Memory & Git Worktree workspace integration.
- [x] Adopted `docs/ORCHESTRATION_PROTOCOL.md` (2026-11-13) — agent defs in `.claude/agents/`.
- [x] Aurum Isle rebrand + 30-day $1,000 Agent Town challenge (`orchestrator/aurum-isle-town`, commit `02200a6`).
- [x] Installed Homebrew `node`/`npx`, `@openai/codex` CLI, `bin/ask-codex` read-only wrapper, and `find-skills` + `obra/superpowers` (`.agents/skills/`).
- [x] Multi-Venture AI Town Studios & Deliverables Viewer (`Exmple.mp4`) with animated task pipelines & multi-stream revenue breakdown (commit `f5dfe32`).

## ⚠️ Known Pitfalls
- Sandbox blocks writes to `.git/` → git branch/worktree/commit need sandbox bypass.
- User keeps uncommitted runtime changes on `main` (`data/company_hq.db`, `obsidian_vault/`, `reports/`) — never stage them.
- Homebrew binaries live in `/opt/homebrew/bin` (`node`, `npm`, `npx`, `codex`).
- [ ] Real MT5 bridge webhook testing (optional live demo).
- [ ] Graph-RAG latency profiling and token optimization metrics.
