# 🧪 QA & Test Engineer Memory

## 🎯 Test Suite Status
- **Test Target**: `tests/test_committee.py`
- **Current Health**: 11/11 PASSED (100% Green)
- **Execution Command**: `PYTHONPATH=. python3 -m pytest tests/test_committee.py -v` (or `./run_tests.sh`)

## 📋 Test Matrix & Coverage
1. `test_market_data_engine_multi_tf`: Validates D1/H4/H1 data generation, ATR and EMA indicators.
2. `test_historical_replay_distinct_dates_and_shifts`: Confirms shift replay integrity across trading sessions.
3. `test_frontier_models_and_custom_model_adder`: Verifies 12+ Frontier LLM configurations & dynamic model additions.
4. `test_offline_shift_auto_catchup_when_pc_off`: Checks accurate backfilling of missed shifts without duplicating records.
5. `test_autonomous_skill_harvester_and_token_economy`: Validates token debit/credit calculations and skill unlocks.
6. `test_v7_isometric_visualizer_dark_light_theme_and_obsidian`: Verifies HTML/CSS rendering of both color themes, Aurum Isle branding (`Aurum Isle`, `เกาะ AI ล่าทองคำ`), 30-day $1,000 challenge banner (`CAN A TOWN OF AI AGENTS MAKE US $1,000?`, `OF 30`), AI Town house & battery pillar renderer (`drawAgentTownHouseAndBattery`), and `first_trade_at` in `portfolio_state`.
7. `test_aurum_isle_challenge_state_calculation`: Validates `compute_challenge_state` for Day 1 initial state, positive profit progression, negative profit clamping (`pct == 0.0`, `is_negative is True`), and multi-venture revenue breakdown (`ventures`).
8. `test_multi_venture_ai_town_studios_and_deliverables_modal`: Validates the 8 AI Town specialized studios (`TOWN_HALL`, `TECH_STUDIO`, `MEME_STUDIO`, `ONLINE_STORE`, `TRADING_LAB`, `CRITIC_STUDIO`, `GROWTH_STUDIO`, `COURIER_DISPATCH`), circular 3D island town renderers (`drawLushCircularIsland`, `drawGiantBattery`, `drawCentralSquareBuilding`), deliverables modal (`studioDeliverablesModal`, `openStudioDeliverablesModal`, `closeStudioDeliverablesModal`, `switchDeliverableStudio`), multi-venture banner strip (`challengeVenturesStrip`), and collaboration pipelines (`STUDIO_COLLAB_PIPELINES`).
9. `test_obsidian_knowledge_graph_and_token_saving_router`: Confirms 1-hop topology generation and >80% token reduction calculation.
10. `test_ask_codex_advisor_script_contract`: Validates `bin/ask-codex` executable permissions, read-only ephemeral sandbox flags (`--sandbox read-only --ephemeral`), absence of dangerous bypass flags, and non-zero usage exit on empty arguments.
11. `test_real_venture_ledger_portfolio_commands_and_integrations`: Validates real venture revenue/expense ledger (`add_venture_transaction`, `venture_ledger`, dynamic `challenge_state["ventures"]` aggregation), manual portfolio commands (`close_position`, `close_all_positions`, `set_risk_guardrails`), agent HR scorecard (`agent_hr_scorecard`, `update_agent_hr_status` including `PROMOTED`/`PROBATION`), live market quote fetcher (`fetch_live_xauusd_quote`), and Enterprise Holding Company OS dashboard components (`liveIntegrationsModal`, `ventureLedgerCard`, `liveOrderBookCard`, `hrScorecardTableBody`, `triggerLiveMarketRefresh`, `submitNewVentureTransaction`, `executePortfolioAction`).

## 🛡️ Pre-Commit Verification Checklist
- Run `./run_tests.sh` sequentially (only by `verification-runner`) prior to merging/releasing.
- Smoke-test `generate_html_dashboard(report, "/tmp/...")` using `TradingCommitteeRoom(db_path=..., vault_dir=...).run_session(...)` on temporary paths so uncommitted runtime files (`data/company_hq.db`, `obsidian_vault/`, `reports/latest_dashboard.html`) are never touched.
- Verify that SQLite database files are not locked after test runs.

## 🔍 Verification Log: Enterprise Holding Company OS (orchestrator/real-venture-os)
- **Bytecode Compile**: `venv/bin/python -m py_compile engine/committee_room.py engine/dashboard_generator.py engine/mt5_bridge.py server.py data/market_data.py tests/test_committee.py` -> Exit code 0 (Pass)
- **Pytest Suite**: `./run_tests.sh` -> 11/11 passed in 0.66s (Exit code 0)
- **Live Dashboard Regeneration**: `venv/bin/python -c "import server; server.ensure_state()"` -> Exit code 0; `reports/latest_dashboard.html` generated (408,729 bytes)
- **Enterprise Component Verification (`reports/latest_dashboard.html`)**:
  - `liveIntegrationsModal`: 3 occurrences
  - `ventureLedgerCard`: 1 occurrence
  - `liveOrderBookCard`: 1 occurrence
  - `hrScorecardTableBody`: 2 occurrences
  - `triggerLiveMarketRefresh`: 4 occurrences
  - `submitNewVentureTransaction`: 2 occurrences
  - `executePortfolioAction`: 6 occurrences

## 🔍 Verification Log: Fullscreen Town & UI Inspector (orchestrator/fullscreen-town-and-ui-inspector)
- **Branch**: `orchestrator/fullscreen-town-and-ui-inspector` vs base `main` (`9a051a4`)
- **Bytecode Compile**: `venv/bin/python3 -m py_compile engine/dashboard_generator.py tests/test_committee.py` -> Exit code 0 (Pass)
- **Pytest Suite**: `./run_tests.sh` -> 10/10 passed in 0.45s (Exit code 0)
- **Smoke Test**: Rendered temporary dashboard to `/tmp/verify_fullscreen_town.html` (339,095 bytes)
  - Fullscreen card & HUD elements present: `townFullscreenCard`, `btnTownStatus`, `btnTownPause`, `btnTownViewAll`, `atmosphereSegmentBar`, `townMessagesBox`
  - Battery indicators present: `5-HOUR`, `7-DAY`
  - Specialized 4 fenced zones present in visualizer canvas: `TECH STUDIO` (`drawTechStudioZone`), `ONLINE SHIRTS` (`drawOnlineShirtsZone`), `MEME STUDIO` (`drawMemeStudioZone`), `WHAT IF STUDIO` (`drawWhatIfQuantZone`), along with `drawCircularPicketFence` and `drawWoodenArchGate`. Note: Generic token `drawFencedWorkZone` was not used in implementation; specialized per-zone functions are used instead.
- **Safety**: Uncommitted runtime user files untouched (`data/company_hq.db`, `obsidian_vault/`, `reports/`).
