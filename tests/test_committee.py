"""
Comprehensive Unit & Integration Tests for AI Holding Company V7:
Ultra-Detailed Cozy Isometric AI Visualizer (@ong_stw style), Light/Dark Theme Switcher,
12+ Frontier Models & Custom Model Registry, Offline Shift Auto-Catchup (for when PC is off),
True Historical Candle/Shift Replay, Token Treasury Allocator & Autonomous Skill Harvester.
"""
import os
import pytest
from data.market_data import MarketDataEngine
from data.database import CompanyDatabase
from agents.technical_agent import TechnicalAgent
from engine.llm_router import MultiLLMRouter
from engine.chat_copilot import ChatCopilotEngine
from engine.token_economy import TokenEconomyEngine
from engine.skill_harvester import SkillHarvesterEngine
from engine.offline_catchup import OfflineCatchupEngine
from engine.committee_room import TradingCommitteeRoom
from engine.dashboard_generator import generate_html_dashboard, compute_challenge_state
from datetime import datetime


def test_market_data_engine_multi_tf():
    engine = MarketDataEngine()
    data = engine.get_market_snapshot()
    assert "current_price" in data and data["current_price"] > 0
    assert "d1_trend" in data
    assert 0.0 < data["us10y_yield"] < 15.0


def test_historical_replay_distinct_dates_and_shifts(tmp_path):
    """ยืนยันว่าการดูสรุปย้อนหลังคนละวันหรือคนละกะเวลา จะได้ตัวเลขกราฟและข้อความสรุปที่ไม่ซ้ำกัน!"""
    db_file = os.path.join(str(tmp_path), "test_replay.db")
    db = CompanyDatabase(db_file)
    copilot = ChatCopilotEngine(db)
    fake_report = {"market_snapshot": {"current_price": 3860.0}}

    sum_day1_asia = copilot.generate_time_window_summary("2026-11-12", "MORNING_ASIA", "EXECUTIVE_CUTE", fake_report)
    sum_day1_ny = copilot.generate_time_window_summary("2026-11-12", "EVENING_NY", "EXECUTIVE_CUTE", fake_report)
    sum_day2_ny = copilot.generate_time_window_summary("2026-11-10", "EVENING_NY", "EXECUTIVE_CUTE", fake_report)

    assert sum_day1_asia["summary_text"] != sum_day1_ny["summary_text"]
    assert sum_day1_ny["summary_text"] != sum_day2_ny["summary_text"]
    assert (sum_day1_asia["open_price"], sum_day1_asia["close_price"]) != (sum_day2_ny["open_price"], sum_day2_ny["close_price"])


def test_frontier_models_and_custom_model_adder(tmp_path):
    db_file = os.path.join(str(tmp_path), "test_custom_models.db")
    db = CompanyDatabase(db_file)
    router = MultiLLMRouter(db)

    base_models = [m["id"] for m in router.get_available_models()]
    assert "OpenAI o1-Pro (Maximum Reasoning Compute)" in base_models
    assert "GPT-4.5 Preview (Orion Frontier Multimodal)" in base_models
    assert "Claude 3.7 Sonnet (Extended Thinking 128K)" in base_models

    db.add_custom_model("GPT-5 Ultra Reasoning (512K)", specialty="Custom Frontier Model")
    updated_models = [m["id"] for m in router.get_available_models()]
    assert "GPT-5 Ultra Reasoning (512K)" in updated_models


def test_offline_shift_auto_catchup_when_pc_off(tmp_path):
    db_file = os.path.join(str(tmp_path), "test_catchup.db")
    db = CompanyDatabase(db_file)
    catchup = OfflineCatchupEngine(db)

    res = catchup.run_auto_catchup(
        df_h1=None,
        latest_report={"market_snapshot": {"current_price": 3865.0}},
        simulated_offline_hours=18.0
    )
    assert res["status"] == "RECOVERED"
    assert res["shifts_recovered"] == 3
    assert len(res["recovered_shifts"]) == 3
    assert res["total_exp_awarded"] >= 300


def test_autonomous_skill_harvester_and_token_economy(tmp_path):
    db_file = os.path.join(str(tmp_path), "test_harvester.db")
    db = CompanyDatabase(db_file)
    harvester = SkillHarvesterEngine(db)
    econ = TokenEconomyEngine(db)

    before_tok = econ.get_economy_report()["total_tokens_used"]
    res = harvester.discover_new_skill(
        agent_id="ag_quant",
        skill_topic="Wyckoff Accumulation Spring & Volume POC",
        tokens_to_spend=50000,
        market_snapshot={"current_price": 3860.0, "atr14": 18.5, "rsi14": 44.0, "support": 3835.0}
    )
    after_tok = econ.get_economy_report()["total_tokens_used"]
    assert after_tok == before_tok + 50000
    assert res["new_skill"]["skill_name"] == "Wyckoff Accumulation Spring & Volume POC"


def test_v7_isometric_visualizer_dark_light_theme_and_obsidian(tmp_path):
    db_file = os.path.join(str(tmp_path), "test_v7.db")
    vault_dir = os.path.join(str(tmp_path), "test_obsidian_vault")
    room = TradingCommitteeRoom(db_path=db_file, vault_dir=vault_dir)

    report = room.run_session(capital=1000.0, risk_pct=1.5)
    assert "offline_catchup" in report
    assert "token_economy" in report

    dash_path = os.path.join(str(tmp_path), "v7_dashboard.html")
    generate_html_dashboard(report, dash_path)
    assert os.path.exists(dash_path)
    with open(dash_path, "r", encoding="utf-8") as f:
        html_text = f.read()
    assert "toggleThemeMode" in html_text
    assert "drawChibiAgent" in html_text
    assert "drawIsoWallWithDoor" in html_text
    assert "addNewCustomModel" in html_text
    assert "triggerOfflineCatchupSim" in html_text
    assert "openGitHubPushModal" in html_text
    assert "triggerGitHubPush" in html_text
    assert "Aurum Isle" in html_text
    assert "เกาะ AI ล่าทองคำ" in html_text
    assert "CAN A TOWN OF AI AGENTS MAKE US $1,000?" in html_text
    assert "OF 30" in html_text
    assert "drawAgentTownHouseAndBattery" in html_text
    assert "first_trade_at" in report["portfolio_state"]


def test_aurum_isle_challenge_state_calculation():
    """ยืนยันการคำนวณภารกิจ 30 วัน ปั้นกำไร $1,000 ของเมือง AI (Aurum Isle)"""
    now = datetime(2026, 11, 13, 12, 0, 0)

    # กรณีเพิ่งเริ่มหรือไม่มี first_trade_at -> Day 1, Profit $0
    s0 = compute_challenge_state({"initial_capital": 1000.0, "equity": 1000.0, "first_trade_at": None}, now)
    assert s0["day"] == 1
    assert s0["days_left"] == 29
    assert s0["profit"] == 0.0
    assert s0["pct"] == 0.0
    assert s0["is_negative"] is False

    # กรณีผ่านไป 4 วัน กำไร +$250 -> Day 5, 25.0%
    s1 = compute_challenge_state({
        "initial_capital": 1000.0,
        "equity": 1250.0,
        "first_trade_at": "2026-11-09 09:30:00"
    }, now)
    assert s1["day"] == 5
    assert s1["days_left"] == 25
    assert s1["profit"] == 250.0
    assert s1["pct"] == 25.0
    assert s1["is_negative"] is False

    # กรณีติดลบ -> is_negative = True, pct clamp ที่ 0.0
    s_neg = compute_challenge_state({
        "initial_capital": 1000.0,
        "equity": 945.5,
        "first_trade_at": "2026-11-12 08:00:00"
    }, now)
    assert s_neg["day"] == 2
    assert s_neg["profit"] == -54.5
    assert s_neg["pct"] == 0.0
    assert s_neg["is_negative"] is True



def test_obsidian_knowledge_graph_and_token_saving_router(tmp_path):
    """ทดสอบการสร้างผังโครงข่ายข้อมูล Obsidian Knowledge Graph + ไฟล์ .canvas + การประหยัดโทเคน 80%+"""
    db_file = os.path.join(str(tmp_path), "test_v8_graph.db")
    vault_dir = os.path.join(str(tmp_path), "test_v8_vault")
    room = TradingCommitteeRoom(db_path=db_file, vault_dir=vault_dir)

    report = room.run_session(capital=1000.0, risk_pct=1.5)
    obs = report["obsidian_status"]

    assert "knowledge_graph" in obs
    kg = obs["knowledge_graph"]
    assert kg["total_nodes"] >= 15
    assert kg["total_edges"] >= 20

    tok_sav = kg["token_savings_report"]
    assert tok_sav["savings_pct"] >= 80.0
    assert tok_sav["tokens_saved_per_call"] >= 14000
    assert len(tok_sav["agent_routing_matrix"]) == 11

    assert os.path.exists(obs["graph_topology_file"])
    assert os.path.exists(obs["canvas_file"])
    assert obs["canvas_file"].endswith("AI_Company_Knowledge_Map.canvas")

