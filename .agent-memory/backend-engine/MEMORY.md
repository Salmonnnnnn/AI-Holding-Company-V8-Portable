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
