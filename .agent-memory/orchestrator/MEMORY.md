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
- [x] Full circular 3D green island town canvas redesign with 2 giant glowing batteries, 8 specialized outer studios, and central plaza matching Exmple.mp4 (commit `0668363`).
- [x] Single-Page Fullscreen AI Town Model with 4 Fenced Outer Zones, 3-Button Segmented Atmosphere Bar, and elite `ui-inspector` subagent (commit `029e468`).
- [x] Enterprise AI Holding Company OS Upgrade: Multi-source live market data (`Yahoo Finance` + `Binance PAXG 24/7 Spot Gold`), SQLite `venture_revenue_ledger`, live portfolio execution commands (`OPEN_CIO_TRADE`, `BREAK_EVEN_ALL`, `CLOSE_TRADE`, `RESET_PORTFOLIO`), `.env` API Integration & Data Provenance Hub (`#liveIntegrationsModal`), and 6-page enterprise features (11/11 pytest PASSED).
- [x] Zero-Collision Aurum Isle Re-zoning & XM MT5 Live Bridge Terminal:
  - Fixed canvas label collisions (OpenClaw Pier moved to East shore, Critic & Risk to Civic Plaza, Tech Studio cottages spaced out, unified district badges).
  - Built XM MT5 Live Bridge Engine (`XMBridgeHub`, 0.05 max lot hard cap, 3.0% daily loss guardrail, demo account enforcement, kill switch & resume).
  - Native MQL5 Expert Advisor (`mt5/AurumBridgeEA.mq5`) with auto Gold symbol detection (`GOLD`, `XAUUSD`, variants).
  - Step-by-step Thai setup guide for MetaTrader 5 on macOS (`mt5/README_XM_SETUP.md`).
  - Top navigation cleanly organized into 6 District Groups (`Aurum Isle`, `Finance & MT5`, `Media`, `Store`, `Tech`, `Organization`).
  - Institutional Trading Terminal (`page-mt5-live`) with live KPIs, Risk Guard meter, open positions table, and emergency Kill Switch.
  - Resolved GitHub PAT push rejection by adding `exclude_workflows` fallback in `engine/github_pusher.py` and UI checkbox.
  - Automated test coverage expanded to 21/21 passing tests (100% pass rate).
- [x] XM Live & Demo Dual-Mode Authorization with Full Interactive Manual Order Deck:
  - Authorized XM Live account (#430446448) while preserving seamless Demo account testing.
  - Interactive Manual Trading Deck: 1-click BUY/SELL market execution, CLOSE ALL, CLOSE TICKET, and Auto-Trading ON/OFF mode toggle.
  - All 21 tests passing with 100% success rate. Server live at http://localhost:8080.
- [x] Interactive XAUUSD Comparison Chart, AI Bot Entry Markers, & Modern Executive Financial Cards:
  - Backend Engine: Added `get_trade_chart_data()` to `XMBridgeHub` with 36-point XAUUSD price series, Demo & Real equity curves, detailed AI Bot entry points (ICT FVG, Asian Range Grab, EMA Pullback, Volatility Breakout, MTF Confluence), financial KPI summary, and REST endpoint `GET /api/mt5/chart_comparison`.
  - Frontend UI: Redesigned financial KPI metrics into 5 frosted glassmorphic executive cards (`.exec-kpi-grid`, `.exec-kpi-card`) separating Real Account (#430446448) from Demo (#50892104). Implemented interactive retina-scaled Canvas chart (`#xauusdComparisonCanvas`) with buy/sell filters, glowing entry markers, hover/click tooltips, and bottom telemetry strip.
  - Verification Runner: 25/25 automated pytest tests passing in 1.95s (100% Green). Dashboard regenerated and server restarted at http://localhost:8080.
- [x] Japanese Candlestick (OHLC) Chart, Zero-Balance Real Account Invariant, Weekend Market Schedule Guard, & 5-Agent Trading War Room:
  - Backend Engine (`engine/mt5_bridge.py`, `server.py`):
    - Set Real Account default strictly to $0.00 Balance, $0.00 Equity, $0.00 PnL with status "รอเติมเงินทุนจริง (Pending Deposit)" when unbacked.
    - Implemented `check_xauusd_market_status()` detecting weekend market halts (Friday 22:00 UTC to Sunday 22:00 UTC) with automatic live order block (`REJECTED` status when market is closed).
    - Generated 36 realistic Japanese Candlestick OHLC bars (`high >= max(open, close)`, `low <= min(open, close)`).
    - Structured 5 distinct specialized bot roles (`macro_news`, `technical_chartist`, `quant_liquidity`, `risk_officer`, `chief_officer`).
  - Frontend UI (`engine/dashboard_generator.py`):
    - Rendered authentic Japanese Candlesticks (OHLC) with emerald green bullish bodies, crimson red bearish bodies, center wicks, and volume bars.
    - Added prominent Weekend Market Closed Banner with Sydney/Tokyo countdown pill.
    - Added 5-Agent Trading War Room Cards deck displaying each agent's specialized task.
    - Added Dual-Account Trade Ledger separating XM Demo live trades from Real Account zero-risk pending state.
  - Verification Runner: 27/27 automated pytest tests passing in 2.95s (100% Green). Verified via `./run_tests.sh` and full pytest suite.
- [x] 11-Agent Open-Source Domain Curriculum & 100% Full Daily Token Budget Burn:
  - Backend Engine (`engine/skill_harvester.py`, `engine/mt5_bridge.py`, `server.py`):
    - Added `OPEN_SOURCE_DOMAIN_CURRICULUM` with 11 specialized Open-Source repositories and quantitative/business skills tailored to all 11 agents (`FinBERT + OpenBB`, `TA-Lib + VectorBT`, `smart-money-concepts + NautilusTrader`, `Riskfolio-Lib + QuantLib`, `Microsoft Qlib + FinRL`, `MetaTrader5-Python-Bridge`, `PyPortfolioOpt + GARCH`, `GDELT`, `Freqtrade Hyperopt`, `MoneyPrinterTurbo`, `Microsoft GraphRAG`).
    - Implemented `train_all_agents_open_source_max_tokens()` switching all 11 agents into `OVERCLOCK` mode, consuming 100% of the daily token budget (`1,000,000 / 1,000,000 tokens`, `remaining_tokens = 0`, `utilization_pct = 100.0%`), upgrading agent levels (+2 to +5) and mastery (`96.8%` to `99.6%`).
    - Added `POST /api/train_open_source_max` endpoint.
  - Frontend UI (`engine/dashboard_generator.py`):
    - Added Open-Source Tech Stack pills and OVERCLOCK Mastery badges to the 5-Agent Trading War Room cards.
    - Added `#openSourceMaxBurnDeck` with 100.0% Daily Token Burn progress bar, 1-click `[🔥 สั่ง AI เรียน Open-Source ขั้นสุด & ใช้โทเคนเต็มพิกัด 100%]` button, and 11-Agent Open-Source Specialization Matrix.
  - Verification Runner: 28/28 automated pytest tests passing in 2.37s (100% Green).
- [x] Autonomous 24/7 Background Self-Learning Daemon & Continuous Open-Source Evolution:
  - Backend Engine (`server.py`, `engine/skill_harvester.py`, `engine/mt5_bridge.py`):
    - Added `start_autonomous_learning_daemon(interval_seconds=300)` running in background thread automatically when server starts.
    - Automatically executes continuous Open-Source curriculum learning, historical big data pattern backtesting, and full-day token budget burn whenever agents are idle or during weekend market closure without requiring any user button clicks.
    - Exposes `autonomous_learning_active`, `autonomous_learning_interval_seconds: 300`, `last_autonomous_cycle`, and `auto_mode_desc` across `/api/state` and `/api/mt5/status`.
  - Frontend UI (`engine/dashboard_generator.py`):
    - Added glowing `#osAutoLearningBanner`: "🟢 ระบบเรียนรู้อัตโนมัติ 24/7 กำลังทำงานในพื้นหลัง (Background Auto-Learner Active)" with real-time cycle timestamp and explanation.
    - Updated button to `[⚡ บังคับเรียนทันที (Instant Force Cycle)]` with hint explaining that learning runs 24/7 automatically.
  - Verification Runner: 31/31 automated pytest tests passing in 2.83s (100% Green). Dashboard regenerated and server live at http://localhost:8080.
- [x] UI Decluttering & 1-Click Native Git Pusher Overhaul:
  - Backend Engine (`engine/github_pusher.py`, `server.py`):
    - Added `_git_env()` with `GIT_TERMINAL_PROMPT="0"` preventing macOS terminal prompt hangs.
    - Removed Windows-only CLI dependencies (`cmdkey`, `git-credential-manager`) on macOS.
    - Added Native macOS / Linux Push Fallback: automatically commits changes and attempts native push via `osxkeychain`/SSH.
    - Added Token Persistence: automatically saves PAT to `.env` as `GITHUB_TOKEN=<token>` so all future clicks are instant 1-click pushes without re-entering the token.
  - Frontend UI (`engine/dashboard_generator.py`):
    - 5-Agent War Room Deck: Minimalist frosted Glass Cards (`.war-room-glass-card`) with expandable drawer for deep specs, eliminating font collision.
    - Unified Top Banner: merged market closed and 24/7 auto-learner into a single sleek executive bar above the Candlestick chart.
    - Open-Source Matrix: converted into a Collapsible Accordion Drawer (collapsed by default).
    - 3D Aurum Isle: Glass Badges with 60fps hover fade-in, eliminating font collision with buildings.
    - Top Navigation: Apple-style Segmented Navigation Bar with crisp icons and short readable labels.
  - Verification Runner: 32/32 automated pytest tests passing in 2.82s (100% Green). Dashboard regenerated and server restarted at http://localhost:8080.
- [x] Zero-Collision Card Layout & 3D Island Containment Fix:
  - Frontend UI (`engine/dashboard_generator.py`):
    - Fixed card layout in `.exec-kpi-grid` (`minmax(295px, 1fr)`) and `.card-head` (`flex-wrap: wrap`, `white-space: nowrap` on `.card-title`), completely preventing title breaking into vertical lines.
    - Fixed values row with rigid 2-column grid (`grid-template-columns: 1fr 1fr; gap: 12px`), completely eliminating the `$10,000.00$10,340.50` collision.
    - Fixed canvas clipping with `object-fit: contain` on `#isometricOfficeCanvas`, ensuring the full 1440x820 canvas is 100% visible on all viewports without cutting off words on the left.
    - Moved `TECH_STUDIO` inward to `x: 300` and `CRITIC_STUDIO` to `x: 580, y: 280`, eliminating overlap with central walking characters and speech bubbles.
    - Increased arch gate height in `drawWoodenArchGate` so "STORE"/"TECH" sign sits above walking agent heads.
  - Verification Runner: 32/32 automated pytest tests passing in 2.61s (100% Green). Dashboard regenerated and server live at http://localhost:8080.
- [x] Full 8-Zone Circular Town Symmetry & Missing Houses/Pathways Fixed:
  - Frontend UI (`engine/dashboard_generator.py`):
    - Added `drawGrowthStudioZone(ctx)` at North-East `(980, 310)`: Viral Hype building, animated golden horn, arch gate `GROWTH`, and 2 named cottages (`🚀 Turbo`, `📢 Hype`).
    - Added `drawCriticStudioZone(ctx)` at North-West `(450, 275)`: Audit & Quality building with gold shield, arch gate `AUDIT`, and 2 named cottages (`🔍 Audit`, `🛡️ Risk`), connecting perfectly to the 10:30 pathway.
    - Updated `radialPaths` in `drawLushCircularIsland` with all 8 symmetrical radial pathways: North (Town Hall), North-West (Critic Studio), West (Tech Studio), South-West (Online Store), South-East (Meme Studio), East (What-If & Quant), North-East (Growth Studio), and Far North-East Shore (OpenClaw Pier entrance).
    - Fully eliminated orphan roads, floating badges, and missing houses.
  - Verification Runner: 32/32 automated pytest tests passing in 2.77s (100% Green). Dashboard regenerated and server live at http://localhost:8080.
- [x] Streamlined 1-Click GitHub Repository Creator & Auto-Pusher (V8.2):
  - Diagnosed Git push failure: GitHub deprecated password authentication and requires Personal Access Tokens (PAT); macOS Keychain had no stored token.
  - Added `.gitignore` ignore patterns for SQLite temporary lock files (`*.db-shm`, `*.db-wal`, `*.db-journal`).
  - Added `GITHUB_TOKEN_CREATION_URL` pre-filled with `scopes=repo,workflow&description=AI-Holding-Company-V8`.
  - Added prominent 1-Click GitHub Token creation button in `githubPushModal` and informative 3-step guide on auth failure.
  - Staged and verified test suite with 32/32 passing tests (100% Green).


## ⚠️ Known Pitfalls
- Sandbox blocks writes to `.git/` → git branch/worktree/commit need sandbox bypass.
- User keeps uncommitted runtime changes on `main` (`data/company_hq.db`, `obsidian_vault/`, `reports/`) — never stage them.
- Homebrew binaries live in `/opt/homebrew/bin` (`node`, `npm`, `npx`, `codex`).
- [ ] Real MT5 bridge webhook testing (optional live demo).
- [ ] Graph-RAG latency profiling and token optimization metrics.
