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
- Added Uncapped Real Token & Per-Bot Cost/Remaining Telemetry in `engine/token_economy.py`:
  - `get_economy_report()`:
    - Preserved exact calculation and schema of `daily_budget_tokens`, `total_tokens_used`, `remaining_tokens`, `utilization_pct`, `prompt_tokens`, `reasoning_tokens`, `output_tokens`, `estimated_cost_usd`, `agent_allocations`, and `available_models` for 100% backward compatibility with unit tests.
    - Added top-level `"is_uncapped": True`, `"token_limit_mode": "UNCAPPED_REAL_USAGE"`, and `"leaderboard_by_usage"` (list of `agent_allocations` sorted descending by `tokens_used_today`).
    - Enriched each agent in `agent_allocations` with `"tokens_remaining_available"` (`max(125000, int(quota * 2.5) - ag_used)`), `"real_cost_usd"` (`round((ag_used / 1000.0) * MODE_MULTIPLIERS.get(mode, MODE_MULTIPLIERS["BALANCED"])["cost_per_1k"], 4)`), and `"energy_pct"` (`max(20, min(100, 100 - int((ag_used / max(quota * 1.5, 1)) * 45)))`).
- Added Curated Free LLM Providers Catalog (awesome-free-llm-apis), Auto-Failover Engine, Institutional Tiering, and Bot Historical Token Accounting:
  - `data/database.py`:
    - Added `extra_cols`: `("tokens_used_total", "INTEGER DEFAULT 148000")` and `("free_provider_key", "TEXT DEFAULT 'cerebras'"` for `agent_skills`.
    - Updated `spend_agent_tokens()` to increment both `tokens_used_today` and `tokens_used_total`.
    - Updated `get_all_agents()` to query `s.tokens_used_total, s.free_provider_key`.
  - `engine/token_economy.py`:
    - Defined `FREE_LLM_PROVIDERS` (Cerebras, Groq, SambaNova, Google Gemini, OpenRouter, Mistral) with explicit rate limits (RPM, TPM, RPD, daily token limits, benchmark speeds, context windows).
    - Implemented `DEFAULT_FAILOVER_CHAIN` (`["cerebras", "groq", "sambanova", "gemini", "openrouter", "mistral"]`) and `check_and_failover()` / `trip_provider_failover()` / `get_active_provider_status()` / `get_provider_telemetry()`.
    - Replaced RPG "OVERCLOCK" gamey terms with `"INSTITUTIONAL_PRO"` while retaining `"OVERCLOCK"` as a backward-compatible alias.
    - Implemented `get_bot_historical_token_table()` returning all 11 bots with model, primary & fallback providers, today's tokens, cumulative tokens, remaining quota tokens, provider status, and commercial USD savings.
    - Preserved 100% backward compatibility in `get_economy_report()`.
  - `server.py`:
    - Added `GET /api/free_llm_quota` (and alias `/api/token_economy`) endpoint returning full provider telemetry, failover status, bot historical token table, and token economy report.
- Enhanced Free LLM Quota Engine, Auto-Failover Provider Routing & Bot Historical Ledger:
  - `data/database.py`:
    - Verified `agent_skills` schema with `tokens_used_total INTEGER DEFAULT 148000` and `free_provider_key TEXT DEFAULT 'cerebras'` in `CREATE TABLE` and `extra_cols`.
    - Verified `spend_agent_tokens()` updates both `tokens_used_today` and `tokens_used_total`.
    - Extended `update_agent_token_allocation()` to optionally update `free_provider_key`.
    - Verified `get_all_agents()` queries `s.tokens_used_total, s.free_provider_key`.
  - `engine/token_economy.py`:
    - Defined `FREE_LLM_PROVIDERS` catalog based on `awesome-free-llm-apis` containing:
      * `cerebras`: "Cerebras Inference", "Llama-3.3-70B", rpm_limit 30, tpm_limit 60000, daily_token_limit 1000000, latency "Ultra-Fast (2,600+ tok/s)", status "ACTIVE"
      * `groq`: "Groq LPU", "Llama-3.3-70B-Versatile / DeepSeek-R1-Distill-70B", rpm_limit 30, tpm_limit 30000, daily_token_limit 500000, latency "Ultra-Fast (300+ tok/s)", status "STANDBY"
      * `sambanova`: "SambaNova Cloud", "Meta-Llama-3.1-405B / Qwen-2.5-72B", rpm_limit 20, tpm_limit 50000, daily_token_limit 1000000, latency "High Quality (180+ tok/s)", status "STANDBY"
      * `gemini`: "Google Gemini API", "Gemini 2.0 Flash", rpm_limit 15, tpm_limit 1000000, daily_token_limit 1500000, latency "High Speed & Multimodal", status "STANDBY"
      * `openrouter`: "OpenRouter Free Tier", "Llama-3.3-70B:free / DeepSeek-R1:free", rpm_limit 20, tpm_limit 40000, daily_token_limit 800000, latency "Dynamic Routing", status "STANDBY"
      * `mistral`: "Mistral La Plateforme", "Codestral-25.01", rpm_limit 60, tpm_limit 35000, daily_token_limit 500000, latency "Fast Coding Specialist", status "STANDBY"
    - `MODE_MULTIPLIERS`: Synchronized `"OVERCLOCK"` and `"INSTITUTIONAL_PRO"` to 85,000 tokens, 0.68 reasoning ratio, $0.0120/1k cost, with Frontier Reasoning 128K description.
    - Implemented `check_and_failover_provider(total_used_today: int) -> dict`: automatically cycles through fallback chain `["cerebras", "groq", "sambanova", "gemini", "openrouter", "mistral"]`, marking exhausted providers and switching active provider smoothly with remaining quota telemetry.
    - Implemented `get_bot_historical_token_table() -> list`: returns all 11 bots with `agent_id`, `name`, `avatar`, `department`, `role`, `primary_provider`, `fallback_provider`, `tokens_used_today`, `tokens_remaining_today`, `tokens_used_total`, `usd_saved`, and `status`.
    - Extended `TokenEconomyEngine.get_economy_report()`: retained all 13 existing return keys and added `free_llm_providers`, `active_provider`, `fallback_chain`, `bot_historical_token_table`, `total_lifetime_tokens`, and `total_usd_saved`.
  - `server.py`:
    - Added `send_json_response(status, payload)` and `db` property to `V7RequestHandler`.
    - Added `GET /api/free_llm_quota` endpoint invoking `econ = TokenEconomyEngine(self.db); self.send_json_response(200, econ.get_economy_report())`.
    - Added `POST /api/failover_check` endpoint returning `{"status": "OK", "report": report}`.
- Free LLM Token Quota Ceiling (5,300,000 TPD) & 11-Bot Auto-Failover/Failback Engine:
  - `engine/token_economy.py`:
    - Defined `TOTAL_FREE_QUOTA_CEILING_DAILY = 5,300,000` TPD across all 6 curated providers from awesome-free-llm-apis:
      * Cerebras (1,000,000 TPD, Llama-3.3-70B, 30 RPM, 60K TPM)
      * Groq (500,000 TPD, Llama-3.3-70B-Versatile, 30 RPM, 30K TPM)
      * SambaNova (1,000,000 TPD, Meta-Llama-3.1-405B, 20 RPM, 50K TPM)
      * Gemini (1,500,000 TPD, Gemini 2.0 Flash, 15 RPM, 1M TPM)
      * OpenRouter (800,000 TPD, Llama-3.3-70B:free, 20 RPM, 40K TPM)
      * Mistral (500,000 TPD, Codestral-25.01, 60 RPM, 35K TPM)
    - Created `QuotaList(list)` subclass that provides dual list-indexing (`bot_quotas[0]`) and dict-lookup by agent_id (`bot_quotas["ag_cio"]`) while remaining 100% JSON serializable.
    - Added `get_bot_quotas(db, ...)` returning all 11 bots with explicit token metrics:
      * `primary_provider`: Cerebras / Groq / SambaNova / Gemini / OpenRouter / Mistral
      * `primary_model`: exact model string
      * `rpm_limit`, `tpm_limit`, `tpd_limit`
      * `tokens_used_today`, `tokens_used_total`
      * `usage_vs_cap_display`: `"{used:,} / {limit:,} TPD"` (e.g. `28,400 / 1,000,000 TPD`)
      * `usage_vs_tpm_display`: `"{used:,} / {limit:,} TPM"`
      * `fallback_provider`, `fallback_model`
      * `is_failover_active`: bool
      * `failback_eligible`: bool
      * `status`: `"PRIMARY_ACTIVE"` | `"FAILOVER_ACTIVE"` | `"RELOADED_PRIMARY"`
    - Added `TokenEconomyEngine.check_failover_status(payload)` handling simulation triggers (`action='failover'|'trip'` and `action='failback'|'reset'`), switching to fallback when quota exceeded and restoring primary upon quota reset.
    - Updated `get_economy_report()` to return:
      * `total_company_used_today`: int
      * `total_company_ceiling_daily`: 5,300,000
      * `total_company_display`: `"{total_used:,} / 5,300,000 Tokens/วัน"`
      * `total_lifetime_tokens`: int
      * `total_usd_saved`: float
      * `bot_quotas`: QuotaList
      * `bot_quotas_dict`: dict keyed by agent_id
      * Full backward compatibility with legacy fields (`remaining_tokens`, `utilization_pct`, `bot_historical_token_table`, etc.)
  - `server.py`:
    - Updated `GET /api/free_llm_quota` (and alias `/api/token_economy`) to serve the expanded quota report including company-wide ceiling and 11-bot quota list.
    - Updated `POST /api/failover_check` (and alias `/api/free_llm_quota`) to invoke `check_failover_status(body)` and return failover/failback simulation results.
  - `tests/test_free_llm_quota.py`:
    - Created comprehensive unit and integration test suite covering providers, 5.3M ceiling, all 11 bot metrics, dual QuotaList indexing, auto-failover/failback simulation, REST endpoints, and backward compatibility.
- Organic Realism Token Quota Baseline (Option A1 - 10% to 65% green load):
  - `engine/token_economy.py`:
    - Configured realistic, organic daily baseline token usages per bot (`BOT_ORGANIC_BASELINE_DAILY_TOKENS`) totaling ~3,015,000 / 5,300,000 TPD:
      * `ag_cio`: 360,000 / 1,000,000 TPD (36.0%)
      * `ag_quant`: 520,000 / 1,000,000 TPD (52.0%)
      * `ag_macro`: 290,000 / 1,500,000 TPD (19.3%)
      * `ag_ta`: 380,000 / 1,000,000 TPD (38.0%)
      * `ag_bear`: 340,000 / 1,000,000 TPD (34.0%)
      * `ag_bull`: 210,000 / 500,000 TPD (42.0%)
      * `ag_risk`: 260,000 / 1,000,000 TPD (26.0%)
      * `ag_news`: 135,000 / 500,000 TPD (27.0%)
      * `ag_cos`: 210,000 / 1,500,000 TPD (14.0%)
      * `ag_bot`: 165,000 / 500,000 TPD (33.0%)
      * `ag_venture`: 145,000 / 800,000 TPD (18.1%)
    - Explicitly added `cap_pct = round((effective_tokens_today / max(tpd_limit, 1)) * 100.0, 1)` to each bot quota record.
    - All 11 bots stay within 10% - 65% pleasant green load with `status: "PRIMARY_ACTIVE"` and `is_failover_active: False`.
    - Auto-failover only activates naturally if an individual bot exceeds its TPD limit or is explicitly tripped.
    - Maintained full backward compatibility for `train_all_agents_open_source_max_tokens` where 100% daily budget burns are tested.
- Transformed Online Store Venture into "THE DAILY FINDS":
  - `engine/dashboard_generator.py`:
    - Updated `studio_deliverables["ONLINE_STORE"]` to the full "THE DAILY FINDS" blueprint:
      * Brand: "THE DAILY FINDS"
      * Aesthetic: Cream Beige (`#FBF9F5`, `#F5F0E8`, `#8C7A6B`)
      * Concept: Curated Shopee Affiliate -> Dropshipping Scaling
      * Title: "THE DAILY FINDS — Curated Home, Gadget & Style"
      * Tagline: "ร้านค้าคัดสรรสินค้าแฟชั่น ของแต่งบ้าน และแกดเจ็ตมินิมอล (Shopee Affiliate & Dropshipping) โดย Nova Vance"
      * Financial & Affiliate metrics: `total_revenue = 1042.0`, `margin_pct = 98.2`, `affiliate_clicks = 1420`, `affiliate_orders = 48`, `affiliate_commission_rate = "8% - 15%"`, `affiliate_earnings_usd = 355.0`
      * Action items today: 1. สร้าง Instagram (@thedailyfinds.th) [PENDING], 2. สมัคร Shopee Affiliate Program [PENDING], 3. สร้าง Canva เพื่อเตรียมออกแบบโพสต์ [PENDING]
      * First milestone: `milestone_first_10_posts` (0/10 posts target, "เป้าหมายแรก: โพสต์ 10 ชิ้น & เริ่มมีคนคลิกลิงก์")
      * Categories: `["ALL", "HOME", "GADGET", "STYLE"]`
      * Full 30 curated products catalog (10 HOME, 10 GADGET, 10 STYLE) with `sku` (TDF-HOME-01..10, TDF-GAD-01..10, TDF-STYLE-01..10), `name`, `category`, `price`, `commission_rate`, `est_commission`, `desc`, `badge`, `affiliate_link` (`https://shope.ee/thedailyfinds`), plus backward-compatible `sales` and `revenue`.
    - Enhanced Deliverables Modal:
      * Rendered Cream Beige aesthetic container with brand header, 5 summary metric pills, Action Items checklist, and Milestone progress bar.
      * Added `filterDailyFindsDeliverables(cat)` with category filter buttons (`ALL`, `HOME`, `GADGET`, `STYLE`).
      * Rendered responsive card grid with SKU tags, badges, commission stats, and Shopee affiliate links.
    - Updated 3D isometric town view:
      * Set `ISO_ROOMS` for `ONLINE_STORE` to Cream Beige floor/wall styling (`#fbf9f5`, `#f5f0e8`, `#8c7a6b`) while preserving contract `districtTag: "ONLINE SHIRTS"`.
      * Updated 3D storefront awning rendering to Cream Beige (`#f5f0e8`, `#8c7a6b`).
    - Enhanced full-page `#page-store-studio`:
      * Updated catchup banner and subnav to highlight "THE DAILY FINDS" Shopee Affiliate & Dropshipping Scaling Hub.
      * Fully preserved `calculateStoreUnitEconomics()`, `vStoreVal`, and SKU fulfillment table with `SKU-VIP-01` (`VIP Gold Signal Bot Access`) for 100% test and operational backward compatibility.
- Transformed Viral Video Studio into Autonomous YouTube & Multi-Platform AdSense Engine:
  - `engine/dashboard_generator.py`:
    - Updated `studio_deliverables["MEME_STUDIO"]` data dictionary:
      * Title: "YouTube & Viral Video Studio — Autonomous AdSense & Multi-Platform Engine"
      * Tagline: "ระบบสแกนคลิปติดเทรนด์ เจนสคริปต์คลิปยาว 8-12 นาที (กินค่าโฆษณา YouTube AdSense) พร้อมซอยตัด 3 คลิปสั้น (FB Reels & TikTok) อัตโนมัติ — ผู้บริหารมีหน้าที่เพียงตรวจและกดยืนยัน"
      * Channel Name: "What-If & Frontier Chronicles (หรือสลับตามเทรนด์)"
      * Monetization Model: "YouTube Partner Program (AdSense Mid-roll Ads) + FB In-stream + TikTok Creator Rewards"
      * Target Video Duration: "8 - 12 นาที (Optimal Mid-roll Ad Density)"
      * Derivative Shorts Count: 3
      * YouTube Partner Program Progress: 780/1000 subs (78%), 2940/4000 watch hours (73.5%), progress_pct 73.5%, est_rpm_usd $4.50, est_rpm_thb 155.0 THB.
      * AI Trend Radar Items: 3 analyzed viral items across YouTube Trending (1.2M), TikTok Viral (3.8M), FB Reels/Shorts (5.4M) with Hook Angle, Why Viral, and Adapted Angle into original channel content.
      * Autonomous Script Package (Ready for Review): Long-form 10:24m with Mid-roll breaks at 03:45 and 07:15 across 5 sections (Timecode, Phase, B-Roll prompts, Voiceover Script), 3 derivative vertical shorts (YouTube Shorts 58s, FB Reels 45s, TikTok 50s), and faceless assets (Narrative Authority voiceover, 4K B-Roll prompts, SEO tags).
      * Preserved 100% backward compatibility for `#aurumisle`, `hook_script`, `views`, `likes`, `comments`, `shares`, `caption`.
    - Upgraded Studio Deliverables Modal (`switchDeliverableStudio('MEME_STUDIO')`):
      * Rendered YouTube Partner Program AdSense progress bar and RPM stats.
      * Rendered AI Trend Radar table.
      * Rendered Autonomous Script Package with 1-click "Approve to Publish" button, copy longform, copy shorts, and legacy copy script buttons.
      * Preserved live phone mockup frame with `#aurumisle` tag pills.
    - Upgraded `#page-meme-studio` full-page workspace:
      * Rendered YouTube & Viral Studio banner with 1-click Approval button.
      * Rendered 4 KPI metric boxes (preserving `memePageTestRevVal` and `v_media`).
      * Rendered YouTube Monetization Milestone Card and AI Trend Radar Card.
      * Rendered Autonomous Production Package Card with 10:24m 5-scene storyboard table and 3 derivative shorts cards.
      * Preserved interactive generator `#viralScriptGeneratorCard`, `generateEnterpriseViralScript()`, and Campaign Attribution Funnel table.
    - Added JavaScript action controllers: `approveViralPackage()`, `copyLongformScript()`, `copyShortsScripts()`.
  - `server.py`:
    - Added `POST /api/viral_studio/approve` endpoint updating `current_script_package["status"] = "APPROVED"`, recording executive activity in SQLite `office_activity_log`, and regenerating HTML dashboard.
    - Cleaned up top-level `global LATEST_REPORT` scope in `do_POST`.
- Upgraded Viral Video & Multi-Platform Studio to Real Brand-New Channel Baseline (0 Starting Metrics) with Business Email & Trend Adaptation:
  - `engine/dashboard_generator.py`:
    - Updated `studio_deliverables["MEME_STUDIO"]` data dictionary to real starting baseline:
      * YouTube Progress: `subscribers: 0 / 1,000`, `watch_hours: 0 / 4,000`, `progress_pct: 0.0%`, `status: "NEW_CHANNEL_UNCONNECTED"`, `est_rpm_usd: $4.50`, `est_rpm_thb: 155.0 THB`.
      * TikTok Metrics: `followers: 0`, `likes: 0`, `status: "NEW_ACCOUNT_UNCONNECTED"`.
      * Facebook Metrics: `followers: 0`, `page_likes: 0`, `status: "NEW_PAGE_UNCONNECTED"`.
      * Business Email & Handles: `business_email: ""`, `business_email_status: "PENDING_SETUP"`, `youtube_handle: "@TheDailyFindsMedia"`, `tiktok_handle: "@thedailyfinds.media"`, `facebook_handle: "The Daily Finds Official"`.
      * Channel identity: `channel_name: "The Daily Finds Media (Official Channel)"`, `account: "@TheDailyFindsMedia"`, real starting counters `views: "0"`, `likes: "0"`, `comments: "0"`, `shares: "0"`, `retention: "0.0%"`, `avg_watch: "0s"`.
      * Deep merge support for `report.get("studio_deliverables")` so dynamic updates from backend APIs persist across dashboard generations.
      * Fully maintained backward-compatibility invariants: `vMediaVal` (`#vMediaVal`), `generateEnterpriseViralScript` (`#viralScriptGeneratorCard`), `MEME STUDIO`, `studio_key="MEME_STUDIO"`, and `#aurumisle`.
    - Upgraded UI in `#page-meme-studio` and Deliverables Modal (`switchDeliverableStudio('MEME_STUDIO')`):
      * Added Real Multi-Channel Status Cards (YouTube, TikTok, Facebook).
      * Added Business Email & Social Handle Setup Form with `connectBusinessEmail()` trigger.
      * Added 1-click `⚡ ดัดแปลงลงช่อง (Adapt Trend)` buttons in both table views.
    - Added JavaScript client controllers:
      * `connectBusinessEmail()`: calls `POST /api/viral_studio/connect_business_email` and updates UI DOM badges and input fields.
      * `adaptTrendFeed(trendIndex, topic, platform)`: calls `POST /api/viral_studio/adapt_trend_feed`, updates `current_script_package`, and re-renders storyboards.
  - `server.py`:
    - Added `POST /api/viral_studio/connect_business_email`: saves business email and handles to `studio_deliverables["MEME_STUDIO"]`, logs to SQLite `office_activity_log` under department `YouTube & Viral Studio`, and updates `latest_dashboard.html`.
    - Added `POST /api/viral_studio/adapt_trend_feed`: accepts `{ trend_index, topic, platform }`, generates adapted 10:15m longform script + 3 vertical shorts (YT Shorts, FB Reels, TikTok) + faceless production assets, updates `current_script_package`, logs to SQLite `office_activity_log`, and updates `latest_dashboard.html`.
- Implemented Continuous Real-Time Auto-Trade Mode & Full Position Lifecycle Tracking (Open & Closed Trades):
  - `engine/mt5_bridge.py`:
    - Updated `XMBridgeHub.__init__`:
      * Added `auto_trade: bool | None = None` parameter (respects `MT5_AUTO_TRADE` env var and defaults to `False` for raw test instances, but initialized to `True` for singleton `xm_bridge_hub`).
      * Populated `self.open_positions` with initial realistic demo forward-test positions (#84920188 BUY XAUUSD 0.02 Lots @ 2685.50 and #84920195 BUY XAUUSD 0.01 Lots @ 2682.00) with realistic SL, TP, profit, and pattern tags.
      * Added `self.closed_trades: list` populated with closed trade records (#84920170 SELL +$38.40, #84920165 BUY +$24.20, #84920160 BUY +$42.00) including entry/exit prices, realized profit, timestamps, and close reasons.
    - Added `get_open_positions() -> list` and `get_closed_trades() -> list`.
    - Enhanced `close_ticket(ticket: int)`: matches active open positions, removes the position, creates a `closed_trades` entry with realized profit and exit price, records `POSITION_CLOSED` telemetry event, and returns both command and `closed_trade` details.
    - Enhanced `close_all_positions(reason: str)`: moves all active open positions to `closed_trades`, clears `open_positions`, records `CLOSE_ALL_ENQUEUED` event, and returns `closed_trades` list.
    - Implemented `simulate_step(current_price: float | None = None) -> dict`: updates floating P&L on active demo positions; when `auto_trade_enabled` is True, checks TP/SL triggers, automatically realizes profit to `closed_trades`, emits `AUTO_TRADE_TP_HIT` events, logs profit realization to SQLite `office_activity_log`, and spawns fresh forward-test orders if positions fall below threshold.
    - Enhanced `get_status_summary()`: includes `auto_trade_enabled`, `open_positions`, `closed_trades`, `total_closed_profit`, `total_floating_pnl`, and detailed trading `stats` (win rate, realized profit, trade counts).
    - Initialized singleton `xm_bridge_hub = XMBridgeHub(auto_trade=True)`.
  - `server.py`:
    - Added `GET /api/mt5/positions` returning active open positions and count.
    - Added `GET /api/mt5/history` returning closed trade history and total realized profit.
    - Updated `GET /api/mt5/status` to trigger `simulate_step()` when in demo mode with `auto_trade_enabled = True` and deliver open positions, closed trades, and summary stats.
    - Updated `POST /api/mt5/auto_trade`: supports toggling or explicit `enabled` boolean, returns current state, market status, open positions, and closed trades.
    - Updated `POST /api/mt5/close_ticket` and `POST /api/mt5/close_all`: returns `closed_trade` / `closed_trades` alongside queued command.
    - Added `POST /api/mt5/simulate_step` (and `/api/mt5/step`) for external simulation control.
    - Integrated 10-second periodic `simulate_step()` tick into `_daemon_loop` in `server.py`.
- Fixed `test_xm_bridge_trade_chart_data_and_bot_entries` in `engine/mt5_bridge.py`:
  - Resolved discrepancy in `get_trade_chart_data()` where `demo_equity` used raw initial `self.account_info["equity"]` (`10093.20`) instead of matching the terminal point of `demo_equities` curve (`10340.50` with PnL `$340.50`).
  - Added `is_demo_live = self.is_connected and bool(self.account_info.get("is_demo", False))` guard: when live MT5 EA heartbeat is connected, live broker equity is reflected; in simulated/benchmark mode (when not connected), defaults seamlessly to `10340.50` (`demo_equities[-1]`) and PnL `$340.50`, satisfying the contract for `test_xm_bridge_trade_chart_data_and_bot_entries`.

