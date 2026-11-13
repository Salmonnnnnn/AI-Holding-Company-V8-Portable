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
