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
├── .claude/agents/                # Reusable subagent definitions (role, model, owned paths)
├── docs/ORCHESTRATION_PROTOCOL.md # Full orchestration rules (Orchestrator ↔ subagents)
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
   - All automated pytest tests must pass: `./run_tests.sh` (run only by `verification-runner`)
   - Memory log in `.agent-memory/<role>/MEMORY.md` must be updated.

## 🧭 Orchestration Protocol (บังคับใช้ทุกงาน)
ฉบับเต็ม: [`docs/ORCHESTRATION_PROTOCOL.md`](docs/ORCHESTRATION_PROTOCOL.md) — สรุปข้อบังคับหลักที่ปรับให้เข้ากับโปรเจกต์นี้:

1. **Orchestrator ไม่เขียน code เอง** — production/test code, config, scripts ทั้งหมดต้องทำโดย subagent. Orchestrator ทำเองได้เฉพาะ: สำรวจ, วางแผน, git branch/worktree/merge (ที่ไม่มี conflict ระดับ code), documentation, agent definitions และ agent memory.
2. **ลำดับงานเคร่งครัด**: Preparation → Implementation → Documentation → Verification. ห้ามเริ่มทดสอบขณะที่ยังมี implementation agent ทำงานอยู่.
3. **Implementation agent ห้ามรัน tests/lint/build** — เขียน code + test code, ตรวจ diff ตัวเอง, commit แล้วรายงาน. ผู้เขียน code ห้ามยืนยันผลงานตัวเอง.
4. **Verification** ทำโดย `verification-runner` เพียงตัวเดียว แบบ read-only และ sequential (`./run_tests.sh`).
5. **Anti-overengineering**: ทำเฉพาะ scope + acceptance criteria, ใช้ pattern เดิม, ห้ามเพิ่ม dependency/abstraction โดยไม่จำเป็น. Improvement นอก scope ให้บันทึกเป็น optional suggestion.
6. **Model**: ใช้รุ่นระดับ Sonnet ขึ้นไปเท่านั้น (ห้าม Haiku/Flash-Lite). งานซับซ้อน/ความเสี่ยงสูงใช้ Opus. ต้องระบุ model และเหตุผลในแผนและรายงานทุกครั้ง.
7. **Branch/Worktree**: integration branch `orchestrator/<task-slug>`, งานย่อย `agent/<task-slug>/<scope>`, worktree ที่ `.worktrees/<task-slug>-<scope>`. ห้ามแตะ uncommitted work ของผู้ใช้ (เช่น `data/company_hq.db`, `obsidian_vault/`, `reports/`).
8. **Conflict** ที่ต้องแก้ code → spawn `conflict-resolver` ห้าม Orchestrator แก้เอง.
9. **Agent definitions** อยู่ที่ `.claude/agents/*.md`; memory ราย agent อยู่ที่ `.agent-memory/<agent>/MEMORY.md` (สั้น เป็นข้อเท็จจริง ไม่มี secret/raw logs).
10. **ความปลอดภัย**: ขออนุญาตผู้ใช้ก่อน force push, deployment, destructive operation, external write, ลบ branch ที่ยังไม่ merge. ห้าม `git reset --hard` โดยไม่มีคำสั่ง.
11. **Final report** ต้องรายงาน agent/model/เหตุผล/skills/memory/branch/commit/verification ตามหลักฐานจริงเท่านั้น.

| Agent | Definition | Memory | Domain |
|---|---|---|---|
| `frontend-ui` | `.claude/agents/frontend-ui.md` | `.agent-memory/frontend-ui/` | `engine/dashboard_generator.py` |
| `backend-engine` | `.claude/agents/backend-engine.md` | `.agent-memory/backend-engine/` | `engine/` (ยกเว้น dashboard), `data/*.py`, `server.py`, `main.py` |
| `quant-analyst` | `.claude/agents/quant-analyst.md` | `.agent-memory/quant-analyst/` | `agents/`, `engine/mt5_bridge.py`, `engine/strategy_benchmark.py` |
| `conflict-resolver` | `.claude/agents/conflict-resolver.md` | `.agent-memory/conflict-resolver/` | merge conflicts เท่านั้น |
| `verification-runner` | `.claude/agents/verification-runner.md` | `.agent-memory/qa-tester/` | read-only review + `./run_tests.sh` |

> หมายเหตุ: `codex` CLI และ `npx` ยังไม่ได้ติดตั้งบนเครื่องนี้ จึงยังไม่มี `bin/ask-codex` และยังไม่ได้ติดตั้ง skills `find-skills` / `obra/superpowers` (ต้องขออนุญาตผู้ใช้ก่อนติดตั้ง).

## ⚡ Quick Start Commands (macOS)
- **Run full setup and launch**: `./setup_and_start.sh`
- **Run tests**: `./run_tests.sh`
- **Start server only**: `./start_company.sh`
- **Open Web App**: [http://localhost:8080](http://localhost:8080)
