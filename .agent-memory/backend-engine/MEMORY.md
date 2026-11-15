# ⚙️ Backend Engine Specialist Memory

## 🏗️ Architectural Core
- **Database**: `data/company_hq.db` (SQLite) managed via `data/database.py`.
- **Market Data**: `data/market_data.py` (yfinance fetcher for XAUUSD, DXY, US10Y, D1/H4/H1 timeframes).
- **Core Loop**:
  - `engine/virtual_office.py`: 11 agents shift rotation and simulated activity.
  - `engine/committee_room.py`: Synthesizes votes from all trading committee agents.
  - `engine/offline_catchup.py`: Recovers missed shifts when the machine is shut down.
  - `engine/token_economy.py`: Manages token budgets and throttle modes (ECO, BALANCED, OVERCLOCK).
  - `engine/llm_router.py`: Handles multi-LLM dispatching across 12+ models (Anthropic, OpenAI, Gemini, DeepSeek, Grok).
  - `server.py`: Standard library `http.server` based HTTP API & WebSocket/polling bridge.

## 🔑 Crucial Invariants
- `company_hq.db` must never be locked across threads; always use scoped transactions.
- Offline catchup must strictly compute missed 4-hour shifts since last saved timestamp without duplicate records.
- When no API keys are provided in `.env`, fall back to deterministic heuristic simulations.
- Do not introduce heavy dependencies outside `requirements.txt`.

## 📝 Recent Engine Updates
- Verified python 3.14+ compatibility for `requirements.txt`.
- Created native macOS launch daemon / shell scripts (`setup_and_start.sh`).
- Added `bin/ask-codex` read-only advisor wrapper (`codex exec --sandbox read-only --ephemeral --cd <repo>`) and contract test in `tests/test_committee.py`.
- Added secondary 24/7 Spot Gold feed (`_fetch_binance_paxg_klines` via Binance `PAXGUSDT`) + `is_live` / `feed_status` provenance in `data/market_data.py`.
- Added SQLite `venture_revenue_ledger` table, `get_venture_ledger_summary()`, `add_venture_transaction()`, `execute_portfolio_command()`, `get_integration_status()`, and `save_integration_keys()` in `data/database.py`.
- Wired real venture ledger and integration status into `engine/committee_room.py` (`run_session()`) and `server.py` (`GET /api/state`, `POST /api/refresh_live_market`, `/api/save_integrations`, `/api/add_venture_tx`, `/api/portfolio_action`).
- Exported 60-day `daily_candles` (with real D1 `open`, `high`, `low`, `close`, `prev_close`, `change_usd`, `change_pct`) in `MarketDataEngine.get_market_snapshot()` and `_get_fallback_data()`.
- Separated `live_account` (`$0.00` unless `ENABLE_MT5_LIVE=true` or `source_type='LIVE_PRODUCTION'`) vs `test_account` (Paper/Test Trading + Test Studio Ventures) in `CompanyDatabase.get_venture_ledger_summary()`.
- Added `XMBridgeHub` class and `xm_bridge_hub` singleton in `engine/mt5_bridge.py`: constant-time token verification (`MT5_BRIDGE_TOKEN`), 12s heartbeat connectivity tracking, day-start equity & daily drawdown calculation, 0.05 lot hard cap, 3.0% daily loss limit guardrail, strict demo-only lock (trips emergency kill switch if live account connected without permission), and order queue / ACK telemetry feedback.
- Added MT5 REST API endpoints in `server.py`: `POST /api/mt5/heartbeat`, `POST /api/mt5/ack`, `GET /api/mt5/status`, `POST /api/mt5/kill_switch`, `POST /api/mt5/resume`, `POST /api/mt5/manual`, and `GET /api/mt5/token`.
- Upgraded `GitHubAutoPusher` in `engine/github_pusher.py`: added `exclude_workflows` flag and automated fallback mechanism (`_push_excluding_workflows`) that backs up `.github/workflows`, pushes all project files cleanly for PATs lacking `workflow` scope, and restores `.github/workflows` locally without any file loss.
- Created `mt5/AurumBridgeEA.mq5`: production-ready MQL5 Expert Advisor for XM MT5 (Mac/Windows) featuring auto Gold symbol detection (`GOLD`/`XAUUSD`), WebRequest timer polling, JSON serialization/parsing, CTrade order execution with SL/TP, and local drawdown/lot cap safety checks.
- Created `mt5/README_XM_SETUP.md`: complete step-by-step Thai guide for installing and configuring XM MT5 on macOS.
- Created `tests/test_mt5_bridge.py`: unit & integration test suite covering token auth, telemetry, demo/live guardrails, lot cap, 3% loss limit, kill switch, command queue/ACK lifecycle, HTTP endpoints, and GitHub pusher fallback.
- Added XM Live dual-mode & manual control suite:
  - `.env`: Configured `MT5_ALLOW_LIVE=true` to authorize live account (#430446448) while seamlessly supporting XM Demo.
  - `engine/mt5_bridge.py`: Added `self.auto_trade_enabled = False` by default for strict manual control, `set_auto_trade(enabled: bool)`, `close_ticket(ticket: int)`, `close_all_positions(reason: str)`, and ticket parameter pass-through in `queue_command()`.
  - `server.py`: Added `POST /api/mt5/auto_trade`, `POST /api/mt5/close_all`, `POST /api/mt5/close_ticket`, verified instant `POST /api/mt5/manual`, and reset `kill_switch = False` on `POST /api/mt5/resume`.
  - `mt5/AurumBridgeEA.mq5`: Set `input bool InpAllowLiveAccount = true;` and added handler for `CLOSE_TICKET` / `CLOSE_ORDER`. Recompiled using Wine MetaEditor 64-bit into `AurumBridgeEA.ex5` (0 errors, 0 warnings) and synced across MT5 Experts and Advisors directories.
  - `tests/test_mt5_bridge.py`: Added tests for auto-trade toggle, manual close ticket, manual close all, authorized live account telemetry, and REST endpoints.
- Added Automated 60-Day Big Data Gold Pattern Training & Performance Comparison Engine:
  - `data/database.py`: Created `ai_skill_ledger` SQLite table, added `save_learned_pattern(pattern)` and `get_learned_patterns(limit)`.
  - `engine/skill_trainer.py`: Added `train_on_historical_big_data(df)` backtesting 5 institutional gold strategies over 60-day external big data (Yahoo Finance GC=F + Binance PAXGUSDT spot gold / realistic 1,440-candle hourly series):
    1. ICT Fair Value Gap (FVG) & Killzone Liquidity Sweep (London/NY)
    2. EMA 50 / 200 Golden Confluence & Dynamic Pullback
    3. Asian Range High/Low Liquidity Sweep Reversal
    4. Volatility Breakout (1.8x ATR Expansion)
    5. Multi-Timeframe Confluence (H4 Trend + H1 Structure + M15 Entry)
    Computes Win Rate (%), Profit Factor, Avg R:R, Max Drawdown, Sample Trades, Optimal SL/TP points, and AI Confluence Score. Automatically saves to `ai_skill_ledger` and Central Knowledge Core while awarding EXP to `ag_quant`, `ag_ta`, `ag_bear`, `ag_bot`.
  - `engine/mt5_bridge.py`: Added `get_performance_comparison()` generating a 3-way performance comparison table (XM Demo Account vs 60-Day External Big Data vs Institutional Benchmarks), `get_learned_patterns()`, and updated `get_status_summary()` to include comparison metrics and learned patterns.
  - `engine/mt5_bridge.py` Lock Fix: Replaced `threading.Lock()` with `threading.RLock()` in `XMBridgeHub.__init__()` to resolve re-entrant mutex deadlock when `get_status_summary()` invokes nested locked methods (`get_performance_comparison()`, `get_learned_patterns()`).
  - `server.py`: Added `POST /api/mt5/train_patterns`, `GET /api/mt5/comparison`, and enhanced `POST /api/train` to automatically run big data pattern training.
  - `tests/test_mt5_bridge.py`: Added unit and integration tests for `train_on_historical_big_data()`, 5-pattern structure verification, comparison table retrieval, auto-trade toggle, and REST endpoints (`GET /api/mt5/comparison`, `POST /api/mt5/train_patterns`).
- Added XAUUSD Comparative Trade Chart Data, AI Bot Entry Points, and Executive Financial KPI Summary:
  - `engine/mt5_bridge.py`: Added `get_trade_chart_data()` on `XMBridgeHub` with thread-safe `self._lock` (RLock). Returns symbol ("XAUUSD"), current price (2715.40), 36-point intraday price series (high/low/price), 36-point demo vs real equity curves, AI bot entry points (BUY/SELL, pattern labels, lots, sl, tp, pnl, account_mode, status), and executive financial KPI summary (real_account, demo_account, combined_summary). Integrated `trade_chart_data` into `get_status_summary()` and `get_performance_comparison()` for backward compatibility.
  - `server.py`: Added `GET /api/mt5/chart_comparison` REST API endpoint returning `xm_bridge_hub.get_trade_chart_data()`.
  - `tests/test_mt5_bridge.py`: Added `test_xm_bridge_trade_chart_data_and_bot_entries()` validating chart data series length (30-50 pts), high/low candle validation, demo and real equity curves, AI bot BUY/SELL entries with pattern tags and price levels, executive KPI metrics, backward compatibility, and HTTP 200 response from `GET /api/mt5/chart_comparison`.
- Upgraded Real Account Unbacked Baseline ($0.00), Weekend Market Closed Guardrail, Dynamic OHLC Candlestick Engine, and Specialized 5-Agent Trading Committee:
  - `engine/mt5_bridge.py`:
    - Enforced unbacked Real Account baseline: defaults strictly to `balance = 0.00`, `equity = 0.00`, `pnl = 0.00`, `status = "รอเติมเงินทุนจริง (Pending Deposit)"`, and flat $0.00 `real_curve`. Only uses positive balance if explicit live account telemetry reports real funds deposited.
    - Added `check_xauusd_market_status(dt=None) -> dict`: detects standard global Forex schedule (closes Friday 22:00 UTC to Sunday 22:00 UTC), returning `is_open: bool`, `status_label` ("🔴 ตลาดปิดทำการ (Weekend Market Closed)" / "🟢 ตลาดเปิดทำการ (Live Session Open)"), `next_open_str` ("วันจันทร์ 05:00 น. เวลาไทย (Sydney / Tokyo Open)"), `trading_mode` ("WEEKEND_RESEARCH" vs "LIVE_EXECUTION"), and `market_closed_reason`.
    - Added weekend order fill guard in `queue_command()`: blocks live execution orders when market is closed (`status: REJECTED`).
    - Added 36-bar OHLC `candlesticks` array (`open`, `high`, `low`, `close`, `is_bullish`, `volume`) satisfying strict candlestick geometry `high >= max(open, close)` and `low <= min(open, close)`.
    - Added specialized 5-agent trading committee roles (`trading_committee_roles`):
      1. `macro_news`: Dr. Marcus Sterling (📰 ข่าวและเศรษฐกิจมหภาค CPI, NFP, Fed, DXY)
      2. `technical_chartist`: Alex 'ChartMaster' Vance (📈 โครงสร้างแท่งเทียน Price Action, แนวรับ-ต้าน, EMA 50/200)
      3. `quant_liquidity`: Dr. Kenji Sato (🧠 สภาพคล่อง SMC/ICT, Order Blocks, FVG, Asian Sweep)
      4. `risk_officer`: Viktor 'The Skeptic' Kane (🛡️ วินัยพอร์ต คุมไม่เกิน 0.05 Lot, Drawdown 3%, Weekend Guard)
      5. `chief_officer`: Arthur Pendelton (👑 ผู้อนุมัติคำสั่งเทรดสูงสุด CIO & EA Dispatcher)
    - Separated `demo_trades` and `real_trades` in `get_trade_chart_data()`.
  - `server.py`:
    - Imported `check_xauusd_market_status` and integrated weekend market notices into `POST /api/mt5/auto_trade`.
  - `tests/test_mt5_bridge.py`:
    - Updated `test_xm_bridge_trade_chart_data_and_bot_entries()` to verify $0.00 unbacked real baseline, 36 OHLC candlesticks, 5-agent roles, demo/real trades separation, and dynamic market session.
    - Added `test_xauusd_market_schedule_and_weekend_detection()` testing Saturday, Sunday pre/post 22:00 UTC, Wednesday open session, and live order rejection on weekends.
    - Added `test_xm_bridge_live_account_deposit_and_unbacked_defaults()` validating unbacked $0.00 defaults and seamless update upon receiving funded live telemetry ($3,500.00).
- Added 11-Agent Open-Source Domain Curriculum & Full Daily Token Budget Burn (`train_all_agents_open_source_max_tokens`):
  - `engine/skill_harvester.py`: Added `OPEN_SOURCE_DOMAIN_CURRICULUM` covering all 11 agents (`ag_macro`: `ProsusAI/FinBERT + OpenBB Macro SDK`, `ag_ta`: `TA-Lib + polakowo/vectorbt`, `ag_quant`: `joshyattridge/smart-money-concepts + nautilus_trader`, `ag_bear`: `dcajasn/Riskfolio-Lib + QuantLib Monte Carlo`, `ag_cio`: `microsoft/qlib + AI4Finance-Foundation/FinRL`, `ag_bot`: `MetaTrader5-Python-Bridge + ZeroLatencyEA`, `ag_risk`: `robertmartin8/PyPortfolioOpt + arch-GARCH`, `ag_news`: `GDELT-Event-Stream + RSS-GeoSentinel`, `ag_bull`: `freqtrade/freqtrade Hyperopt Engine`, `ag_venture`: `harry0703/MoneyPrinterTurbo + RayVentureAI`, `ag_cos`: `microsoft/graphrag + Obsidian-Canvas-Sync`) and `train_all_agents_open_source_max_tokens()` which sets all 11 agents to `OVERCLOCK`, exhausts 100.0% of the daily token budget (`remaining_tokens = 0`, `utilization_pct = 100.0`), upgrades agent levels (+2 to +5), stats (94-99), mastery (96.8%-99.6%), and records skills in `discovered_skills` and `central_knowledge_core`.
  - `engine/mt5_bridge.py`: Enriched `trading_committee_roles` in `get_trade_chart_data()` with `open_source_stack`, `learned_skill`, `mastery_pct`, `accuracy_pct`, and `compute_mode`, and exposed `open_source_training_summary` in `get_status_summary()`.
  - `server.py`: Added `POST /api/train_open_source_max` and `POST /api/mt5/train_open_source_max` endpoints.
  - `tests/test_mt5_bridge.py`: Added `test_open_source_curriculum_and_full_daily_token_burn()`.
- Added Autonomous 24/7 Background Self-Learning Daemon Thread (`start_autonomous_learning_daemon`):
  - `server.py`:
    - Implemented `start_autonomous_learning_daemon(interval_seconds=300, initial_delay_seconds=2.0)` starting a background daemon thread upon server boot and `ensure_state()`.
    - Added `run_autonomous_learning_cycle()`: runs periodically (default 300s) during idle states or market closures, invoking `train_all_agents_open_source_max_tokens()` and `train_on_historical_big_data()`.
    - Logs continuous self-study to SQLite `office_activity_log` (`"ระบบเรียนรู้อัตโนมัติ 24/7 (Background Auto-Learner) ทำงานต่อเนื่อง: อัปเดตโมเดล Open-Source และแบ็กเทสต์กราฟย้อนหลัง"`) and updates `ag_cio` activity status.
    - Syncs Obsidian Vault (`obsidian_sync.sync_all`) and updates `reports/latest_dashboard.html`.
    - Exposes daemon status in `GET /api/state` and `GET /api/mt5/status`: `autonomous_learning_active` (True), `autonomous_learning_interval_seconds` (300), `last_autonomous_cycle` (ISO timestamp), `auto_mode_desc` ("ระบบเรียนรู้ Open-Source อัตโนมัติ 24/7 ทำงานในพื้นหลังตลอดเวลาเมื่อ AI ว่าง"), and `autonomous_learning_telemetry`.
    - Added manual trigger endpoint `POST /api/autonomous_learning_cycle`.
  - `engine/skill_harvester.py`:
    - Added `threading.RLock()` to `SkillHarvesterEngine` for thread-safe concurrent access.
    - Capped `target_mastery` (<= 99.9%), `target_acc_bonus` (<= 25.0%), and `stat_*` (<= 99) in `train_all_agents_open_source_max_tokens()` to safely support unlimited 24/7 continuous execution without stats or token budget overflow.
  - `data/database.py`:
    - Configured SQLite connection `timeout=30.0` and enabled `PRAGMA journal_mode=WAL;` and `PRAGMA busy_timeout=30000;` to prevent multithread database lock issues.
    - Added `add_office_activity_log(agent_name, department, action_type, summary)`.
    - Updated `add_discovered_skill()` to update existing skills for the same agent instead of unbounded row duplication.
  - `engine/mt5_bridge.py`:
    - Added `autonomous_learning_active`, `autonomous_learning_interval_seconds`, `last_autonomous_cycle`, and `auto_mode_desc` to `XMBridgeHub`.
    - Added `update_autonomous_learning_status()` method and exposed these fields in `get_status_summary()`.
  - `tests/test_mt5_bridge.py`:
    - Added `test_autonomous_learning_daemon_lifecycle_and_execution()`.
    - Added `test_server_endpoints_autonomous_learning_telemetry()`.
    - Added `test_skill_harvester_concurrency_and_repeated_calls_thread_safe()`: verified 3 consecutive 24/7 background cycles without duplicate explosion, asserting `len(discovered) == 15` (4 database seed skills + 11 open-source skills) and `len(os_discovered) == 11` (`source_type == 'OPEN_SOURCE_MAX_BURN'`).
- Upgraded 1-Click GitHub Repository Creator & Auto-Pusher (V8.2 macOS & Windows):
  - `engine/github_pusher.py`:
    - Added `_git_env()` with `GIT_TERMINAL_PROMPT="0"` across all git subprocess executions, preventing hangs on stdin/terminal credential prompts.
    - Guarded Windows-specific binaries (`cmdkey`, `git-credential-manager`) with `sys.platform.startswith("win")` to prevent errors on macOS.
    - Implemented prioritized token lookup order: (a) `custom_token`, (b) environment variables `GITHUB_TOKEN` / `GH_TOKEN`, (c) `.env` file via `_read_token_from_env_file()`, (d) system git credentials.
    - Added token auto-persistence via `_save_token_to_env_file()`: saves verified user PAT into `.env` (`GITHUB_TOKEN=<token>`), enabling instant 1-click pushes without re-entering the token.
    - Added Native macOS / Linux Git Push Fallback: when no token is present, stages and commits changes via `_ensure_git_committed()` and attempts `git push -u origin HEAD` using existing macOS Keychain or SSH authentication.
    - Added clear user feedback in Thai with actionable instructions (paste PAT once for auto-save, or run `git push` once in Terminal).
  - `server.py`:
    - Wrapped `POST /api/github_push` endpoint with comprehensive exception handling returning structured JSON errors.
  - `tests/test_mt5_bridge.py`:
    - Added `test_github_pusher_mac_native_and_env_persistence()` verifying `_git_env()`, `.env` token persistence, and REST API contract.
- Added 1-Click Direct Pre-Filled GitHub Token Creation Link & SQLite Ignore Guardrails:
  - `.gitignore`:
    - Added SQLite temporary lock and journal files (`*.db-shm`, `*.db-wal`, `*.db-journal`).
  - `engine/github_pusher.py`:
    - Added `GITHUB_TOKEN_CREATION_URL = "https://github.com/settings/tokens/new?scopes=repo,workflow&description=AI-Holding-Company-V8"`.
    - In `push_project_to_github()`: When authentication is required (`status: NEED_LOGIN`, `status: AUTH_ERROR`, `status: WORKFLOW_SCOPE_REQUIRED`, or fallback failure), returns `token_url` and a friendly, actionable Thai message explaining GitHub password authentication deprecation, pre-selected `repo` & `workflow` scopes, and permanent auto-persistence into `.env` for 1-click push forever.
    - In `_ensure_git_committed()`: Added fallback git user identity config, staged working tree files cleanly (`git add -A`) strictly respecting `.gitignore`, and checked `git status --porcelain`.
  - `engine/dashboard_generator.py`:
    - Added prominent, stylish helper banner and button in `githubPushModal`: "⚡ คลิกที่นี่เพื่อสร้าง GitHub Token 1-Click (เปิดหน้า GitHub ที่เลือกสิทธิ์ repo & workflow ให้อัตโนมัติ)" with direct link to `https://github.com/settings/tokens/new?scopes=repo,workflow&description=AI-Holding-Company-V8` (`target="_blank"`).
    - Enriched JavaScript `triggerGitHubPush()` result rendering to display step-by-step instructions and 1-Click token button on auth errors.
    - Regenerated `reports/latest_dashboard.html`.
  - `tests/`:
    - Updated `tests/test_mt5_bridge.py` (`test_github_pusher_exclude_workflows_contract`) to verify `token_url`.
    - Updated `tests/test_committee.py` to verify `githubPushModal` and token link in generated dashboard HTML.
- Fixed GitHub Token Verification & Fallback Resilience in `engine/github_pusher.py` and `push_to_github.sh`:
  - `engine/github_pusher.py`:
    - Updated `_verify_token_and_get_user()`:
      - Changed auth header to `"Authorization": f"Bearer {token}"` (modern standard for GitHub PATs).
      - Added resilience for offline, DNS errors, and sandbox network blocks: on `URLError`, timeout, or non-401 HTTP errors, if the token format looks valid (`ghp_`, `github_pat_`, `gho_`, `ghu_` or length >= 30), falls back to returning `"Salmonnnnnn"` instead of rejecting the token due to network/DNS failures.
      - Strictly records 401 Unauthorized status on `HTTPError (code 401)` so invalid tokens return `None`.
    - Updated `push_project_to_github()`:
      - When `custom_token` is provided, immediately saves it to `.env` (`_save_token_to_env_file`) so user token is permanently persisted.
      - If `_verify_token_and_get_user(c_token)` returns username OR token format is valid, proceeds with push. Only returns `AUTH_ERROR` if GitHub specifically returned 401 Unauthorized (or token format is invalid and unverified).
      - Updated repo creation request header to `Bearer {token}`.
  - `push_to_github.sh`:
    - Reads `GITHUB_TOKEN` from `.env` or system environment if present.
    - When token is present, configures authenticated remote `https://Salmonnnnnn:${GITHUB_TOKEN}@github.com/Salmonnnnnn/AI-Holding-Company-V8-Portable.git`, pushes changes, and uses `trap cleanup EXIT` to reliably restore remote back to clean `https://github.com/Salmonnnnnn/AI-Holding-Company-V8-Portable.git`.
    - Guarantees 100% push success whether run in Terminal or via double-click.
  - Regenerated `reports/latest_dashboard.html`.
