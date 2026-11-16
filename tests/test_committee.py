"""
Comprehensive Unit & Integration Tests for AI Holding Company V7:
Ultra-Detailed Cozy Isometric AI Visualizer (@ong_stw style), Light/Dark Theme Switcher,
12+ Frontier Models & Custom Model Registry, Offline Shift Auto-Catchup (for when PC is off),
True Historical Candle/Shift Replay, Token Treasury Allocator & Autonomous Skill Harvester.
"""
import os
import subprocess
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
    assert "daily_candles" in data and len(data["daily_candles"]) >= 20


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
    assert "ventures" in s_neg
    assert s_neg["ventures"]["total"] == -54.5

    # ยืนยันการแจกแจงรายได้หลายช่องทาง (Multi-Stream Breakdown)
    assert "ventures" in s0
    assert s0["ventures"]["total"] == 0.0
    assert "ventures" in s1
    assert s1["ventures"]["trading"] == round(250.0 * 0.45, 2)
    assert s1["ventures"]["total"] == 250.0

    # กรณีส่ง ventures กำหนดเองมาใน port
    custom_ventures = {"trading": 120.0, "store": 60.0, "tech": 40.0, "media": 30.0}
    s_custom = compute_challenge_state({
        "initial_capital": 1000.0,
        "equity": 1250.0,
        "first_trade_at": "2026-11-09 09:30:00",
        "ventures": custom_ventures
    }, now)
    assert s_custom["ventures"]["trading"] == 120.0
    assert s_custom["ventures"]["store"] == 60.0
    assert s_custom["ventures"]["tech"] == 40.0
    assert s_custom["ventures"]["media"] == 30.0
    assert s_custom["ventures"]["total"] == 250.0


def test_multi_venture_ai_town_studios_and_deliverables_modal(tmp_path):
    """ทดสอบการสร้างผัง 8 สตูดิโอเฉพาะทางของเมือง AI Multi-Venture Town และหน้าต่างผลงานจริง (Deliverables Viewer Modal)"""
    db_file = os.path.join(str(tmp_path), "test_town.db")
    vault_dir = os.path.join(str(tmp_path), "test_vault")
    room = TradingCommitteeRoom(db_path=db_file, vault_dir=vault_dir)
    report = room.run_session(capital=1000.0, risk_pct=1.5)

    dash_path = os.path.join(str(tmp_path), "town_dashboard.html")
    generate_html_dashboard(report, dash_path)
    assert os.path.exists(dash_path)

    with open(dash_path, "r", encoding="utf-8") as f:
        html_text = f.read()

    # 1. ยืนยันการมีอยู่ของ Deliverables Modal และฟังก์ชันเปิด/ปิด
    assert "studioDeliverablesModal" in html_text
    assert "openStudioDeliverablesModal" in html_text
    assert "closeStudioDeliverablesModal" in html_text
    assert "switchDeliverableStudio" in html_text

    # 2. ยืนยัน 8 สตูดิโอเฉพาะทางในเมือง AI Town
    for studio_id in [
        "TOWN_HALL", "TECH_STUDIO", "MEME_STUDIO", "ONLINE_STORE",
        "TRADING_LAB", "CRITIC_STUDIO", "GROWTH_STUDIO", "COURIER_DISPATCH"
    ]:
        assert studio_id in html_text

    # 3. ยืนยันแถบแยกรายได้หลายช่องทาง (Multi-Venture Breakdown) ใน Challenge Banner
    assert "challengeVenturesStrip" in html_text
    assert "vTradingVal" in html_text
    assert "vStoreVal" in html_text
    assert "vTechVal" in html_text
    assert "vMediaVal" in html_text

    # 4. ยืนยันเนื้อหาผลงานจริงของสตูดิโอ (Deliverables)
    assert "#aurumisle" in html_text
    assert "liquidity_sweep_bot.py" in html_text
    assert "VIP Gold Signal Bot" in html_text
    assert "STUDIO_COLLAB_PIPELINES" in html_text

    # 5. ยืนยัน Single-Page Fullscreen Town Model HUD, 3-Button Segmented Atmosphere Bar และ 4 Outer Fenced Zones
    assert "atmosphereSegmentBar" in html_text
    assert "setTownSkyAtmosphere" in html_text
    assert "toggleTownPause" in html_text
    assert "toggleTownMessagesBox" in html_text
    assert "TECH STUDIO" in html_text
    assert "ONLINE SHIRTS" in html_text
    assert "MEME STUDIO" in html_text
    assert "WHAT IF STUDIO" in html_text
    assert "OpenClaw" in html_text
    assert ("AI DATA CENTER" in html_text or "5-HOUR" in html_text)
    assert ("KNOWLEDGE VAULT" in html_text or "7-DAY" in html_text)
    assert "The Boss" in html_text
    assert "Cutaway #1 render APPROVED!" in html_text
    assert "Sprocket" in html_text
    assert "Whiskers" in html_text
    assert "Jester" in html_text
    assert "Atlas" in html_text
    assert "townMessagesBox" in html_text
    assert "townZoneSwitcherBar" in html_text

    # 6. ยืนยันการแก้บั๊กป้าย Canvas บน macOS (fillCenteredText), ปฏิทิน P&L รายเดือน และ 3 สตูดิโอธุรกิจเต็มรูปแบบ
    assert "fillCenteredText" in html_text
    assert "monthlyPnlCalendarCard" in html_text
    assert "monthlyCalendarGrid" in html_text
    assert "changeCalendarMonth" in html_text
    assert "page-meme-studio" in html_text
    assert "page-store-studio" in html_text
    assert "page-tech-studio" in html_text
    assert "calculateStoreUnitEconomics" in html_text
    assert "generateEnterpriseViralScript" in html_text
    assert "selectTechStudioModule" in html_text



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


def test_ask_codex_advisor_script_contract():
    """ยืนยันว่าสคริปต์ที่ปรึกษา bin/ask-codex มีอยู่จริง รันได้ บังคับ read-only ephemeral sandbox และแสดง Usage เมื่อไม่ส่งคำถาม"""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    script_path = os.path.join(repo_root, "bin", "ask-codex")

    assert os.path.isfile(script_path), "bin/ask-codex must exist"
    assert os.access(script_path, os.X_OK), "bin/ask-codex must be executable"

    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "--sandbox read-only" in content
    assert "--ephemeral" in content
    assert "--cd" in content
    assert "danger-full-access" not in content

    proc = subprocess.run([script_path], capture_output=True, text=True)
    assert proc.returncode != 0
    combined_out = (proc.stdout or "") + (proc.stderr or "")
    assert "usage:" in combined_out.lower()


def test_real_venture_ledger_portfolio_commands_and_integrations(tmp_path):
    """ยืนยันการทำงานของสมุดบัญชีรายได้จริง (venture_revenue_ledger), คำสั่งควบคุมพอร์ตจริง และสถานะ API Integration"""
    db_file = os.path.join(str(tmp_path), "test_real_ledger.db")
    db = CompanyDatabase(db_file)

    # 1. ตรวจสอบยอดเริ่มต้นจาก SQLite venture_revenue_ledger
    ledger0 = db.get_venture_ledger_summary()
    assert ledger0["store"] == 145.0
    assert ledger0["tech"] == 98.0
    assert ledger0["media"] == 64.5
    assert ledger0["trading"] == 0.0
    assert ledger0["total"] == 307.5
    assert "live_account" in ledger0 and "test_account" in ledger0
    assert ledger0["live_account"]["total_profit"] == 0.0
    assert ledger0["test_account"]["total_profit"] == 307.5
    assert 5.0 <= ledger0["battery_5h_pct"] <= 100.0
    assert 10.0 <= ledger0["battery_7d_pct"] <= 100.0
    assert len(ledger0["entries"]) >= 4

    # 2. บันทึกรายได้ใหม่เข้าสตูดิโอจริง
    ledger1 = db.add_venture_transaction(
        studio_key="ONLINE_STORE",
        venture_name="Gold Sniper Indicator Pack",
        description="ลูกค้าสั่งซื้อแพ็กเกจอินดิเคเตอร์",
        amount_usd=55.0
    )
    assert ledger1["store"] == 200.0
    assert ledger1["total"] == 362.5

    # 3. ทดสอบคำสั่งควบคุมพอร์ตจริง (OPEN_CIO_TRADE -> BREAK_EVEN_ALL -> CLOSE_TRADE)
    p_open = db.execute_portfolio_command(
        command="OPEN_CIO_TRADE",
        market_price=2680.0,
        cio_verdict={"action": "BUY", "final_entry": 2680.0, "final_sl": 2665.0, "final_tp1": 2705.0, "final_tp2": 2720.0},
        lot_size=0.05
    )
    assert len(p_open["open_positions"]) == 1
    tid = p_open["open_positions"][0]["id"]

    p_be = db.execute_portfolio_command(command="BREAK_EVEN_ALL", market_price=2690.0)
    assert p_be["open_positions"][0]["status"] == "TP1_PARTIAL"
    assert p_be["open_positions"][0]["sl_price"] == 2680.0

    p_close = db.execute_portfolio_command(command="CLOSE_TRADE", market_price=2700.0, trade_id=tid)
    assert len(p_close["open_positions"]) == 0
    assert p_close["total_closed_trades"] == 1
    assert p_close["balance"] == 1100.0
    assert p_close["equity"] == 1100.0

    # ยืนยันว่ากำไรเทรดจริงไหลเข้าสู่สมุดบัญชีรวมอัตโนมัติ
    ledger2 = db.get_venture_ledger_summary(p_close)
    assert ledger2["trading"] == 100.0
    assert ledger2["total"] == 462.5

    # 4. ตรวจสอบรายงานสถานะการเชื่อมต่อ API & Data Provenance
    int_status = db.get_integration_status()
    assert "items" in int_status and len(int_status["items"]) >= 6
    assert "data_provenance" in int_status and len(int_status["data_provenance"]) >= 6
    assert all(p["is_real"] is True for p in int_status["data_provenance"])

    # 5. ยืนยันการแสดงผล Enterprise UI ครบทั้ง 6 หน้า และ Modal ตรวจสอบที่มาตัวเลขจริง
    vault_dir = os.path.join(str(tmp_path), "test_real_ledger_vault")
    room = TradingCommitteeRoom(db_path=db_file, vault_dir=vault_dir)
    report = room.run_session(capital=1000.0, risk_pct=1.5)
    dash_path = os.path.join(str(tmp_path), "test_enterprise_dashboard.html")
    generate_html_dashboard(report, dash_path)
    with open(dash_path, "r", encoding="utf-8") as f:
        html_text = f.read()

    assert "liveIntegrationsModal" in html_text
    assert "ventureLedgerCard" in html_text
    assert "liveOrderBookCard" in html_text
    assert "triggerLiveMarketRefresh" in html_text
    assert "submitNewVentureTransaction" in html_text
    assert "executePortfolioAction" in html_text
    assert "hrScorecardTableBody" in html_text
    assert "triggerAllHandsBoardMeeting" in html_text
    assert "downloadReplayMarkdownReport" in html_text
    assert "githubPushModal" in html_text
    assert "scopes=repo,workflow&description=AI-Holding-Company-V8" in html_text



