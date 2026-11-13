# 🧪 QA & Test Engineer Memory

## 🎯 Test Suite Status
- **Test Target**: `tests/test_committee.py`
- **Current Health**: 7/7 PASSED (100% Green)
- **Execution Command**: `PYTHONPATH=. python3 -m pytest tests/test_committee.py -v` (or `./run_tests.sh`)

## 📋 Test Matrix & Coverage
1. `test_market_data_engine_multi_tf`: Validates D1/H4/H1 data generation, ATR and EMA indicators.
2. `test_historical_replay_distinct_dates_and_shifts`: Confirms shift replay integrity across trading sessions.
3. `test_frontier_models_and_custom_model_adder`: Verifies 12+ Frontier LLM configurations & dynamic model additions.
4. `test_offline_shift_auto_catchup_when_pc_off`: Checks accurate backfilling of missed shifts without duplicating records.
5. `test_autonomous_skill_harvester_and_token_economy`: Validates token debit/credit calculations and skill unlocks.
6. `test_v7_isometric_visualizer_dark_light_theme_and_obsidian`: Verifies HTML/CSS rendering of both color themes.
7. `test_obsidian_knowledge_graph_and_token_saving_router`: Confirms 1-hop topology generation and >80% token reduction calculation.

## 🛡️ Pre-Commit Verification Checklist
- Run `./run_tests.sh` prior to pushing or merging any worktree.
- Verify that SQLite database files are not locked after test runs.
