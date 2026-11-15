"""
Unit and Integration Tests for MetaTrader 5 (MT5) / XM Algorithmic Bridge Hub (V8)
Verifies:
1. Token authentication & verification (secure constant-time comparison).
2. Live telemetry recording, day-start equity, and daily loss calculation.
3. Hard lot cap rule (volume > 0.05 lot strictly rejected).
4. Strict Demo-only guardrail (live accounts automatically trip kill switch).
5. Max 3.0% daily drawdown guardrail (auto CLOSE_ALL and blocks new orders).
6. Kill switch activation, command queueing, and resume lifecycle.
7. Command dispatch & ACK feedback lifecycle.
8. Server REST API endpoints (/api/mt5/heartbeat, /api/mt5/ack, /api/mt5/status, etc.).
9. GitHubAutoPusher exclude_workflows fallback mechanism.
"""
import io
import json
import os
import tempfile
import pytest
from datetime import datetime, timezone
import pandas as pd
from engine.mt5_bridge import XMBridgeHub, MT5ExecutionBridge, check_xauusd_market_status
from engine.skill_trainer import SkillTrainerEngine
from data.database import CompanyDatabase
from engine.github_pusher import GitHubAutoPusher
from server import (
    V7RequestHandler,
    run_autonomous_learning_cycle,
    start_autonomous_learning_daemon,
    stop_autonomous_learning_daemon,
    AUTONOMOUS_LEARNING_CONFIG
)


def test_mt5_execution_bridge_backward_compatibility():
    """ยืนยันว่า MT5ExecutionBridge ดั้งเดิมยังคงทำงานได้ 100% ไม่กระทบโค้ดเดิม"""
    bridge = MT5ExecutionBridge()
    req = bridge.build_mt5_order_request("BUY", 0.02, 2685.0, 2667.0, 2720.0)
    assert req["symbol"] == "XAUUSD"
    assert req["volume"] == 0.02
    assert "BUY" in req["type"]

    sim = bridge.simulate_live_mt5_demo_execution(
        cio_verdict={"action": "BUY (LONG)", "final_entry": 2685.0, "recommended_lot": 0.02},
        market_data={"current_price": 2685.0},
        best_strategy_name="ICT London Sweep"
    )
    assert sim["direction"] == "BUY"
    assert len(sim["steps_telemetry"]) == 8
    assert len(sim["tick_series"]) > 20


def test_xm_bridge_token_generation_and_verification():
    """ตรวจสอบการสร้างโทเคน 32-char hex และการตรวจความถูกต้องของโทเคน"""
    hub = XMBridgeHub()
    assert isinstance(hub.token, str) and len(hub.token) >= 16
    assert hub.verify_token(hub.token) is True
    assert hub.verify_token("wrong_token_xyz") is False
    assert hub.verify_token("") is False

    custom_hub = XMBridgeHub(token="my_custom_xm_bridge_secret_token_1234")
    assert custom_hub.verify_token("my_custom_xm_bridge_secret_token_1234") is True
    assert custom_hub.verify_token("other_token") is False


def test_xm_bridge_heartbeat_and_status_summary():
    """ตรวจสอบการรับ Heartbeat จาก EA, คำนวณเงินทุนเริ่มต้นวัน และสรุปสถานะ"""
    hub = XMBridgeHub()
    assert hub.is_connected is False

    heartbeat_data = {
        "token": hub.token,
        "account": 8849201,
        "broker": "XM Global Limited",
        "server": "XMGlobal-Demo",
        "balance": 10000.0,
        "equity": 10050.0,
        "margin": 45.0,
        "free_margin": 10005.0,
        "floating_pnl": 50.0,
        "is_demo": True,
        "currency": "USD",
        "open_positions": [
            {"ticket": 123456, "symbol": "GOLD", "type": "BUY", "volume": 0.02, "profit": 50.0}
        ]
    }
    res = hub.record_heartbeat(heartbeat_data)
    assert res["status"] == "OK"
    assert hub.is_connected is True
    assert hub.account_info["account"] == 8849201
    assert hub.account_info["broker"] == "XM Global Limited"
    assert hub.account_info["balance"] == 10000.0
    assert hub.account_info["equity"] == 10050.0
    assert hub.day_start_equity == 10050.0
    assert hub.daily_loss_pct == 0.0

    summary = hub.get_status_summary()
    assert summary["is_connected"] is True
    assert summary["account_info"]["account"] == 8849201
    assert len(summary["open_positions"]) == 1
    assert summary["max_lot"] == 0.05
    assert summary["max_daily_loss_pct"] == 3.0


def test_xm_bridge_strict_demo_guardrail():
    """ตรวจสอบ Guardrail: บัญชีจริง (Live) จะถูกบล็อกและตัดวงจรฉุกเฉินทันทีหากไม่ได้รับอนุญาต"""
    hub = XMBridgeHub()
    hub.allow_live = False  # Strict Demo Mode

    live_heartbeat = {
        "token": hub.token,
        "account": 99887766,
        "broker": "XM Real Production",
        "server": "XMGlobal-Real-1",
        "balance": 50000.0,
        "equity": 50000.0,
        "is_demo": False,  # บัญชีจริง!
    }
    hub.record_heartbeat(live_heartbeat)

    assert hub.kill_switch is True
    pending = hub.pop_pending_commands()
    assert len(pending) >= 1
    assert pending[0]["cmd_type"] == "CLOSE_ALL"
    assert "Live account" in pending[0]["comment"]

    order = hub.queue_command("BUY", volume=0.01)
    assert order["status"] == "REJECTED"


def test_xm_bridge_hard_lot_cap_0_05():
    """ตรวจสอบ Guardrail: ห้ามส่งออเดอร์ขนาดเกิน 0.05 lot โดยเด็ดขาด"""
    hub = XMBridgeHub()

    # ไม้ขนาดปกติ <= 0.05 lot ผ่านเกณฑ์
    cmd_ok1 = hub.queue_command("BUY", volume=0.01)
    assert cmd_ok1["status"] == "PENDING"
    assert cmd_ok1["cmd_id"] is not None

    cmd_ok2 = hub.queue_command("SELL", volume=0.05)
    assert cmd_ok2["status"] == "PENDING"

    # ไม้ขนาดเกิน 0.05 lot ต้องถูกปฏิเสธทันที
    cmd_rejected1 = hub.queue_command("BUY", volume=0.06)
    assert cmd_rejected1["status"] == "REJECTED"
    assert "exceeds hard cap" in cmd_rejected1["reason"]
    assert cmd_rejected1["cmd_id"] is None

    cmd_rejected2 = hub.queue_command("OPEN_BUY", volume=0.50)
    assert cmd_rejected2["status"] == "REJECTED"


def test_xm_bridge_max_daily_loss_3_pct_guardrail():
    """ตรวจสอบ Guardrail: ขาดทุนแตะ 3.0% ของเงินต้นวันนั้น จะหยุดเทรดและปิดทุกออเดอร์"""
    hub = XMBridgeHub()

    # 1. เริ่มต้นวันด้วย Equity $10,000.00
    hub.record_heartbeat({"equity": 10000.0, "balance": 10000.0, "is_demo": True})
    assert hub.day_start_equity == 10000.0

    # 2. ขาดทุนลงมาเหลือ $9,800.00 (Drawdown = 2.0% < 3.0%) -> ยังอนุญาตให้เทรดได้
    hub.record_heartbeat({"equity": 9800.0, "balance": 10000.0, "is_demo": True})
    assert hub.daily_loss_pct == 2.0
    assert hub.kill_switch is False
    cmd = hub.queue_command("BUY", volume=0.02)
    assert cmd["status"] == "PENDING"

    # 3. ขาดทุนลงมาแตะ $9,690.00 (Drawdown = 3.1% >= 3.0%) -> ตัดวงจรทันที!
    hub.record_heartbeat({"equity": 9690.0, "balance": 10000.0, "is_demo": True})
    assert hub.daily_loss_pct == 3.1
    assert hub.kill_switch is True

    # ออเดอร์ใหม่หลังจากนี้ต้องถูกปฏิเสธ
    cmd_blocked = hub.queue_command("BUY", volume=0.01)
    assert cmd_blocked["status"] == "REJECTED"


def test_xm_bridge_kill_switch_and_resume_lifecycle():
    """ตรวจสอบการทำงานของ Kill Switch และการ Resume"""
    hub = XMBridgeHub()

    # กระตุ้น Kill Switch แบบ Manual
    res_kill = hub.trigger_kill_switch("Manual test emergency stop")
    assert res_kill["status"] == "HALTED"
    assert hub.kill_switch is True

    pending = hub.pop_pending_commands()
    assert len(pending) == 1
    assert pending[0]["cmd_type"] == "CLOSE_ALL"

    # ระหว่าง Kill Switch Active คำสั่งเปิดออเดอร์ใหม่จะถูกปฏิเสธ
    cmd_blocked = hub.queue_command("SELL", volume=0.01)
    assert cmd_blocked["status"] == "REJECTED"

    # สั่ง Resume
    res_resume = hub.resume_trading()
    assert res_resume["status"] == "RESUMED"
    assert hub.kill_switch is False

    # หลัง Resume สามารถส่งคำสั่งใหม่ได้ตามปกติ
    cmd_allowed = hub.queue_command("BUY", volume=0.01)
    assert cmd_allowed["status"] == "PENDING"


def test_xm_bridge_command_queue_and_ack_lifecycle():
    """ตรวจสอบวงจรคำสั่ง: Queue -> Drain (Pop) -> ACK จาก EA"""
    hub = XMBridgeHub()

    cmd = hub.queue_command("OPEN_BUY", symbol="XAUUSD", volume=0.02, sl_distance=18.0, tp_distance=35.0)
    cmd_id = cmd["cmd_id"]
    assert cmd_id is not None
    assert cmd["status"] == "PENDING"

    # จำลอง EA ส่ง Heartbeat มารับคำสั่ง
    dispatched = hub.pop_pending_commands()
    assert len(dispatched) == 1
    assert dispatched[0]["cmd_id"] == cmd_id

    # ตรวจสอบว่าคิวถูกดึงออกไปแล้ว (Drain)
    assert len(hub.pop_pending_commands()) == 0

    # จำลอง EA ส่งผลลัพธ์ ACK กลับมา
    ack_res = hub.acknowledge_command(
        cmd_id=cmd_id,
        status="DONE",
        ticket=84920188,
        fill_price=2685.25,
        error_msg=""
    )
    assert ack_res["status"] == "DONE"
    assert ack_res["ticket"] == 84920188
    assert ack_res["fill_price"] == 2685.25

    summary = hub.get_status_summary()
    assert any(c.get("cmd_id") == cmd_id and c.get("ticket") == 84920188 for c in summary["recent_commands"])


def test_xm_bridge_auto_trade_and_manual_controls():
    """ตรวจสอบฟังก์ชัน Auto-Trading Toggle, Close Ticket, Close All และ Live Mode"""
    hub = XMBridgeHub()
    # 1. Default auto_trade_enabled is False (Manual control safety default)
    assert hub.auto_trade_enabled is False

    # 2. Toggle auto_trade
    res_toggle = hub.set_auto_trade(True)
    assert res_toggle is True
    assert hub.auto_trade_enabled is True
    assert hub.get_status_summary()["auto_trade_enabled"] is True

    hub.set_auto_trade(False)
    assert hub.auto_trade_enabled is False

    # 3. Close ticket
    cmd_ticket = hub.close_ticket(ticket=778899)
    assert cmd_ticket["cmd_type"] == "CLOSE_TICKET"
    assert cmd_ticket["ticket"] == 778899
    assert cmd_ticket["status"] == "PENDING"
    assert hub.kill_switch is False

    # 4. Close all positions without tripping permanent kill switch
    cmd_close_all = hub.close_all_positions(reason="User request ปิดยาว")
    assert cmd_close_all["status"] == "QUEUED"
    assert cmd_close_all["command"]["cmd_type"] == "CLOSE_ALL"
    assert "ปิดยาว" in cmd_close_all["command"]["comment"]
    assert hub.kill_switch is False  # Does NOT permanently trip kill switch

    # 5. Live account heartbeat with allow_live=True
    hub.allow_live = True
    res_hb = hub.record_heartbeat({
        "account": 430446448,
        "broker": "XM Live",
        "server": "XMGlobal-Real-1",
        "balance": 25000.0,
        "equity": 25000.0,
        "is_demo": False
    })
    assert res_hb["status"] == "OK"
    assert hub.kill_switch is False


class MockServerHandler(V7RequestHandler):
    """Mock HTTP Request Handler เพื่อทดสอบ REST API endpoints โดยไม่ต้องเปิด Socket จริง"""
    def __init__(self, method: str, path: str, body_dict: dict | None = None):
        self.command = method
        self.path = path
        self.request_version = "HTTP/1.1"
        self.close_connection = True
        self.headers = {"Content-Type": "application/json"}
        payload_bytes = json.dumps(body_dict or {}).encode("utf-8") if body_dict else b""
        self.headers["Content-Length"] = str(len(payload_bytes))
        self.rfile = io.BytesIO(payload_bytes)
        self.wfile = io.BytesIO()
        self._response_status = 200
        self._response_headers = {}

    def send_response(self, code, message=None):
        self._response_status = code

    def send_header(self, keyword, value):
        self._response_headers[keyword] = value

    def end_headers(self):
        pass

    def get_json_response(self) -> dict:
        self.wfile.seek(0)
        content = self.wfile.read().decode("utf-8")
        return json.loads(content) if content else {}


def test_server_mt5_api_endpoints():
    """ทดสอบ REST API endpoints ทั้งหมดของ MT5 Bridge บน server.py"""
    from engine.mt5_bridge import xm_bridge_hub

    # 1. GET /api/mt5/token
    h_token = MockServerHandler("GET", "/api/mt5/token")
    h_token.do_GET()
    assert h_token._response_status == 200
    res_tok = h_token.get_json_response()
    assert res_tok["status"] == "ok"
    valid_token = res_tok["token"]
    assert len(valid_token) > 0

    # 2. GET /api/mt5/status
    h_status = MockServerHandler("GET", "/api/mt5/status")
    h_status.do_GET()
    assert h_status._response_status == 200
    res_status = h_status.get_json_response()
    assert "account_info" in res_status
    assert "kill_switch" in res_status
    assert "auto_trade_enabled" in res_status
    assert "allow_live" in res_status
    assert "performance_comparison" in res_status
    assert "learned_patterns" in res_status

    # 3. POST /api/mt5/heartbeat ด้วย Token ปลอม -> ต้องได้ 401 Unauthorized
    h_bad_hb = MockServerHandler("POST", "/api/mt5/heartbeat", {"token": "invalid_token"})
    h_bad_hb.do_POST()
    assert h_bad_hb._response_status == 401

    # 4. POST /api/mt5/heartbeat ด้วย Token ถูกต้อง -> 200 OK
    h_good_hb = MockServerHandler("POST", "/api/mt5/heartbeat", {
        "token": valid_token,
        "account": 776655,
        "broker": "XM Global",
        "server": "XMGlobal-Demo",
        "balance": 15000.0,
        "equity": 15000.0,
        "is_demo": True
    })
    h_good_hb.do_POST()
    assert h_good_hb._response_status == 200
    hb_res = h_good_hb.get_json_response()
    assert hb_res["status"] == "OK"
    assert "commands" in hb_res

    # 5. POST /api/mt5/manual: ขนาดเกิน 0.05 lot -> 400 REJECTED
    h_manual_bad = MockServerHandler("POST", "/api/mt5/manual", {
        "action": "BUY",
        "lot": 0.10
    })
    h_manual_bad.do_POST()
    assert h_manual_bad._response_status == 400
    assert h_manual_bad.get_json_response()["status"] == "REJECTED"

    # 6. POST /api/mt5/manual: ขนาดปกติ 0.02 lot -> 200 QUEUED
    h_manual_good = MockServerHandler("POST", "/api/mt5/manual", {
        "action": "BUY",
        "lot": 0.02,
        "sl_points": 18.0,
        "tp_points": 35.0
    })
    h_manual_good.do_POST()
    assert h_manual_good._response_status == 200
    manual_res = h_manual_good.get_json_response()
    assert manual_res["status"] == "QUEUED"
    queued_cmd_id = manual_res["command"]["cmd_id"]

    # 7. POST /api/mt5/ack
    h_ack = MockServerHandler("POST", "/api/mt5/ack", {
        "token": valid_token,
        "cmd_id": queued_cmd_id,
        "status": "DONE",
        "ticket": 1234567,
        "price": 2686.0
    })
    h_ack.do_POST()
    assert h_ack._response_status == 200
    assert h_ack.get_json_response()["status"] == "OK"

    # 8. POST /api/mt5/kill_switch
    h_kill = MockServerHandler("POST", "/api/mt5/kill_switch", {})
    h_kill.do_POST()
    assert h_kill._response_status == 200
    assert h_kill.get_json_response()["status"] == "HALTED"
    assert xm_bridge_hub.kill_switch is True

    # 9. POST /api/mt5/resume
    h_resume = MockServerHandler("POST", "/api/mt5/resume", {})
    h_resume.do_POST()
    assert h_resume._response_status == 200
    assert h_resume.get_json_response()["status"] == "RESUMED"
    assert xm_bridge_hub.kill_switch is False

    # 10. POST /api/mt5/auto_trade
    h_at = MockServerHandler("POST", "/api/mt5/auto_trade", {"enabled": True})
    h_at.do_POST()
    assert h_at._response_status == 200
    assert h_at.get_json_response()["auto_trade_enabled"] is True

    # 11. POST /api/mt5/close_all
    h_ca = MockServerHandler("POST", "/api/mt5/close_all", {"reason": "Test Close All"})
    h_ca.do_POST()
    assert h_ca._response_status == 200
    assert h_ca.get_json_response()["status"] == "QUEUED"

    # 12. POST /api/mt5/close_ticket
    h_ct = MockServerHandler("POST", "/api/mt5/close_ticket", {"ticket": 987654})
    h_ct.do_POST()
    assert h_ct._response_status == 200
    assert h_ct.get_json_response()["status"] == "QUEUED"

    # 13. POST /api/mt5/close_ticket (Missing ticket -> 400 ERROR)
    h_ct_bad = MockServerHandler("POST", "/api/mt5/close_ticket", {})
    h_ct_bad.do_POST()
    assert h_ct_bad._response_status == 400

    # 14. GET /api/mt5/comparison: ตารางเปรียบเทียบ Demo vs Big Data 60 วัน vs สถาบัน
    h_comp = MockServerHandler("GET", "/api/mt5/comparison")
    h_comp.do_GET()
    assert h_comp._response_status == 200
    comp_res = h_comp.get_json_response()
    assert "comparison_table" in comp_res
    assert len(comp_res["comparison_table"]) >= 4
    assert "demo_metrics" in comp_res
    assert "big_data_metrics" in comp_res
    assert "institutional_standards" in comp_res

    # 15. POST /api/mt5/train_patterns: สั่ง AI ฝึกฝน 5 สถาปัตยกรรมกลยุทธ์ทองคำย้อนหลัง 60 วัน
    h_train_pat = MockServerHandler("POST", "/api/mt5/train_patterns", {})
    h_train_pat.do_POST()
    assert h_train_pat._response_status == 200
    pat_res = h_train_pat.get_json_response()
    assert pat_res["status"] == "OK"
    assert "learned_patterns" in pat_res
    assert len(pat_res["learned_patterns"]) == 5
    assert "comparison" in pat_res
    assert pat_res["ai_confluence_score"] > 0.0


def test_train_on_historical_big_data_5_patterns():
    """
    ทดสอบระบบเรียนรู้และแบ็กเทสต์ 5 สถาปัตยกรรมกลยุทธ์ทองคำบน Big Data 60 วัน:
    1. ICT Fair Value Gap (FVG) & Killzone Liquidity Sweep
    2. EMA 50 / 200 Golden Confluence & Dynamic Pullback
    3. Asian Range High/Low Liquidity Sweep Reversal
    4. Volatility Breakout (1.8x ATR Expansion)
    5. Multi-Timeframe Confluence (H4 Trend + H1 Structure + M15 Entry)
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_skill.db")
        db = CompanyDatabase(db_path)
        trainer = SkillTrainerEngine(db)

        # รันการฝึกฝนบนชุดข้อมูลทองคำ 60 วัน
        res = trainer.train_on_historical_big_data()
        assert res["training_status"] == "SUCCESS"
        assert res["total_candles_analyzed"] >= 40
        assert res["ai_confluence_score"] > 50.0

        patterns = res["pattern_rankings"]
        assert len(patterns) == 5

        # ตรวจสอบ ID ของ 5 รูปแบบแพตเทิร์น
        pat_ids = [p["pattern_id"] for p in patterns]
        expected_ids = {
            "ict_fvg_sweep",
            "ema_golden_pullback",
            "asian_sweep_reversal",
            "volatility_breakout",
            "mtf_confluence"
        }
        assert set(pat_ids) == expected_ids

        # ตรวจสอบความสมบูรณ์ของ Metrics แต่ละแพตเทิร์น
        for p in patterns:
            assert p["win_rate"] > 0.0
            assert p["profit_factor"] > 0.0
            assert p["optimal_sl_pips"] > 0.0
            assert p["optimal_tp_pips"] > 0.0
            assert p["confidence_rating"] > 50.0
            assert p["sample_trades"] > 0
            assert "parameters" in p

        # ตรวจสอบว่าบันทึกลง SQLite `ai_skill_ledger`
        saved_patterns = db.get_learned_patterns(limit=10)
        assert len(saved_patterns) >= 5

        # ตรวจสอบ Central Knowledge Core ได้รับก้อนความรู้และ EXP
        knowledge = db.get_central_knowledge_core(limit=10)
        assert len(knowledge) > 0


def test_xm_bridge_performance_comparison_and_auto_trade():
    """ทดสอบเมธอด get_performance_comparison, set_auto_trade และ get_status_summary"""
    hub = XMBridgeHub()

    # ทดสอบการสลับโหมด Auto-Trade ("ออโต้" หรือ "หยุด")
    assert hub.auto_trade_enabled is False
    assert hub.set_auto_trade(True) is True
    assert hub.auto_trade_enabled is True
    assert hub.set_auto_trade(False) is False
    assert hub.auto_trade_enabled is False

    # ทดสอบการดึงตารางเปรียบเทียบประสิทธิภาพ Demo vs Big Data 60 วัน vs สถาบัน
    comp = hub.get_performance_comparison()
    assert "comparison_table" in comp
    assert len(comp["comparison_table"]) >= 4
    metrics_list = [row["metric"] for row in comp["comparison_table"]]
    assert "Win Rate (%)" in metrics_list
    assert "Profit Factor (PF)" in metrics_list
    assert "Max Drawdown (%)" in metrics_list

    # ตรวจสอบว่า summary snapshot มี performance_comparison และ auto_trade_enabled
    summary = hub.get_status_summary()
    assert "performance_comparison" in summary
    assert "learned_patterns" in summary
    assert "auto_trade_enabled" in summary
    assert summary["auto_trade_enabled"] is False


def test_xm_bridge_trade_chart_data_and_bot_entries():
    """
    ทดสอบชุดข้อมูลกราฟเปรียบเทียบพอร์ต XAUUSD (Demo vs Real),
    จุดเข้าเทรดของ AI Bot พร้อมระบุเทคนิค/แพตเทิร์น และ REST API endpoint /api/mt5/chart_comparison
    """
    hub = XMBridgeHub()
    chart_data = hub.get_trade_chart_data()

    # 1. โครงสร้างข้อมูลหลัก
    assert chart_data["symbol"] == "XAUUSD"
    assert isinstance(chart_data["current_price"], float)
    assert chart_data["current_price"] > 2000.0

    # 2. Price Series, Demo Curve และ Real Curve (30-50 จุด)
    price_series = chart_data["price_series"]
    assert 30 <= len(price_series) <= 50
    for pt in price_series:
        assert "time" in pt
        assert "price" in pt
        assert "high" in pt
        assert "low" in pt
        assert pt["high"] >= pt["price"] >= pt["low"]

    demo_curve = chart_data["demo_curve"]
    assert 30 <= len(demo_curve) <= 50
    for pt in demo_curve:
        assert "time" in pt
        assert "equity" in pt
        assert "balance" in pt
        assert pt["equity"] >= 9000.0

    real_curve = chart_data["real_curve"]
    assert 30 <= len(real_curve) <= 50
    for pt in real_curve:
        assert "time" in pt
        assert "equity" in pt
        assert "balance" in pt
        # พอร์ตจริงที่ยังไม่ได้เติมเงิน ต้องเริ่มต้นที่ $0.00 เสมอ
        assert pt["balance"] == 0.0
        assert pt["equity"] == 0.0

    # 3. 36-Candlestick OHLC Data
    assert "candlesticks" in chart_data
    candles = chart_data["candlesticks"]
    assert 30 <= len(candles) <= 50
    for c in candles:
        assert "time" in c
        assert "open" in c
        assert "high" in c
        assert "low" in c
        assert "close" in c
        assert "is_bullish" in c
        assert "volume" in c
        assert c["high"] >= max(c["open"], c["close"])
        assert c["low"] <= min(c["open"], c["close"])
        assert c["is_bullish"] == (c["close"] >= c["open"])
        assert c["volume"] > 0

    # 4. Specialized Trading Committee Roles
    assert "trading_committee_roles" in chart_data
    roles = chart_data["trading_committee_roles"]
    expected_roles = {"macro_news", "technical_chartist", "quant_liquidity", "risk_officer", "chief_officer"}
    assert set(roles.keys()) == expected_roles
    assert roles["macro_news"]["agent"] == "Dr. Marcus Sterling"
    assert "CPI" in roles["macro_news"]["role"]
    assert roles["technical_chartist"]["agent"] == "Alex 'ChartMaster' Vance"
    assert roles["quant_liquidity"]["agent"] == "Dr. Kenji Sato"
    assert "SMC/ICT" in roles["quant_liquidity"]["role"]
    assert roles["risk_officer"]["agent"] == "Viktor 'The Skeptic' Kane"
    assert "0.05 Lot" in roles["risk_officer"]["duty"]
    assert roles["chief_officer"]["agent"] == "Arthur Pendelton"

    # 5. Dynamic Market Schedule
    assert "market_session" in chart_data
    assert "is_market_open" in chart_data
    assert isinstance(chart_data["is_market_open"], bool)
    assert "status_label" in chart_data["market_session"]
    assert "next_open_str" in chart_data["market_session"]
    assert "trading_mode" in chart_data["market_session"]

    # 6. Separate Demo & Real Trades
    assert "demo_trades" in chart_data
    assert "real_trades" in chart_data
    assert len(chart_data["demo_trades"]) >= 3
    assert len(chart_data["real_trades"]) >= 1

    # 7. AI Bot Entry Points (จุดเข้าซื้อ/ขายของบอท พร้อมแพตเทิร์นและระดับราคา)
    entries = chart_data["bot_entry_points"]
    assert len(entries) >= 4
    types_found = {e["type"] for e in entries}
    assert "BUY" in types_found
    assert "SELL" in types_found

    account_modes = {e["account_mode"] for e in entries}
    assert "DEMO" in account_modes
    assert "REAL" in account_modes

    statuses = {e["status"] for e in entries}
    assert "OPEN" in statuses
    assert "CLOSED_WIN" in statuses

    for e in entries:
        assert isinstance(e["ticket"], int)
        assert len(e["time"]) >= 4
        assert e["price"] > 2000.0
        assert e["lots"] > 0.0
        assert e["sl"] > 0.0
        assert e["tp"] > 0.0
        assert len(e["pattern"]) > 5
        assert isinstance(e["pnl"], (int, float))

    # 8. Financial KPI Summary (สถิติการเงินพอร์ตจริง vs เดโม)
    kpi = chart_data["financial_kpi_summary"]
    assert "real_account" in kpi
    assert "demo_account" in kpi
    assert "combined_summary" in kpi

    real_acc = kpi["real_account"]
    assert real_acc["account_id"] == "430446448"
    assert real_acc["type"] == "Live Main Account"
    assert real_acc["is_authorized"] is True
    # พอร์ตจริงยังไม่เติมเงิน ต้องเป็น 0.00 และสถานะรอเติมเงิน
    assert real_acc["balance"] == 0.0
    assert real_acc["equity"] == 0.0
    assert real_acc["pnl"] == 0.0
    assert "รอเติมเงินทุนจริง" in real_acc["status"]

    demo_acc = kpi["demo_account"]
    assert demo_acc["account_id"] == "50892104"
    assert demo_acc["balance"] == 10000.0
    assert demo_acc["equity"] == 10340.50
    assert demo_acc["pnl"] == 340.50

    comb = kpi["combined_summary"]
    assert comb["total_net_pnl"] == 340.50
    assert comb["win_rate"] == 64.2
    assert comb["profit_factor"] == 1.88
    assert comb["daily_loss_cap_pct"] == 3.0

    # 9. Backward Compatibility ใน get_status_summary()
    summary = hub.get_status_summary()
    assert "trade_chart_data" in summary
    assert summary["trade_chart_data"]["symbol"] == "XAUUSD"
    assert "is_market_open" in summary
    assert "market_session" in summary
    assert "trading_committee_roles" in summary

    # 10. REST API Endpoint: GET /api/mt5/chart_comparison
    handler = MockServerHandler("GET", "/api/mt5/chart_comparison")
    handler.do_GET()
    assert handler._response_status == 200
    res_json = handler.get_json_response()
    assert res_json["symbol"] == "XAUUSD"
    assert "candlesticks" in res_json
    assert "price_series" in res_json
    assert "demo_curve" in res_json
    assert "real_curve" in res_json
    assert "bot_entry_points" in res_json
    assert "trading_committee_roles" in res_json
    assert "financial_kpi_summary" in res_json
    assert len(res_json["price_series"]) >= 30
    assert len(res_json["candlesticks"]) >= 30


def test_xauusd_market_schedule_and_weekend_detection():
    """
    ตรวจสอบระบบตรวจจับเวลาทำการของตลาดทองคำโลก (XAUUSD / Forex Schedule)
    - วันเสาร์: ตลาดปิดทำการตลอดวัน (Weekend Closed)
    - วันอาทิตย์ก่อน 22:00 UTC: ตลาดปิดทำการ
    - วันอาทิตย์หลัง 22:00 UTC: ตลาดเปิดทำการ (Sydney / Tokyo Open)
    - วันพุธ (กลางสัปดาห์): ตลาดเปิดทำการปกติ
    - วันศุกร์หลัง 22:00 UTC: ตลาดปิดทำการ
    """
    # 1. วันเสาร์ (2026-11-14 12:00 UTC) -> ปิด
    sat_dt = datetime(2026, 11, 14, 12, 0, 0, tzinfo=timezone.utc)
    sat_status = check_xauusd_market_status(sat_dt)
    assert sat_status["is_open"] is False
    assert sat_status["trading_mode"] == "WEEKEND_RESEARCH"
    assert "🔴 ตลาดปิดทำการ" in sat_status["status_label"]
    assert "วันจันทร์" in sat_status["next_open_str"]
    assert "ปิดทำการช่วงสุดสัปดาห์" in sat_status["market_closed_reason"]

    # 2. วันอาทิตย์บ่าย (2026-11-15 15:00 UTC) -> ยังปิด
    sun_early = datetime(2026, 11, 15, 15, 0, 0, tzinfo=timezone.utc)
    sun_early_status = check_xauusd_market_status(sun_early)
    assert sun_early_status["is_open"] is False

    # 3. วันอาทิตย์ค่ำหลัง 22:00 UTC (2026-11-15 22:30 UTC) -> เปิดตลาด Sydney
    sun_late = datetime(2026, 11, 15, 22, 30, 0, tzinfo=timezone.utc)
    sun_late_status = check_xauusd_market_status(sun_late)
    assert sun_late_status["is_open"] is True
    assert sun_late_status["trading_mode"] == "LIVE_EXECUTION"
    assert "🟢 ตลาดเปิดทำการ" in sun_late_status["status_label"]

    # 4. วันพุธกลางสัปดาห์ (2026-11-18 14:00 UTC) -> เปิดปกติ
    wed_dt = datetime(2026, 11, 18, 14, 0, 0, tzinfo=timezone.utc)
    wed_status = check_xauusd_market_status(wed_dt)
    assert wed_status["is_open"] is True
    assert wed_status["trading_mode"] == "LIVE_EXECUTION"

    # 5. วันศุกร์ดึกหลัง 22:00 UTC (2026-11-20 22:15 UTC) -> ตลาดปิดสุดสัปดาห์
    fri_late = datetime(2026, 11, 20, 22, 15, 0, tzinfo=timezone.utc)
    fri_late_status = check_xauusd_market_status(fri_late)
    assert fri_late_status["is_open"] is False

    # 6. ตรวจสอบการบล็อกคำสั่งพอร์ตจริงเมื่อตลาดปิด
    hub = XMBridgeHub()
    hub.allow_live = True
    hub.account_info["is_demo"] = False  # Live account

    current_market = check_xauusd_market_status()
    if not current_market["is_open"]:
        # วันหยุดสุดสัปดาห์ คำสั่งเปิดไม้พอร์ตจริงต้องถูก REJECTED ทันที
        cmd = hub.queue_command("BUY", volume=0.01)
        assert cmd["status"] == "REJECTED"
        assert "ปิดทำการ" in cmd["reason"]


def test_xm_bridge_live_account_deposit_and_unbacked_defaults():
    """
    ตรวจสอบว่าพอร์ตจริงที่ยังไม่ได้ฝากเงิน จะมี Balance/Equity = 0.00
    และเมื่อมี Heartbeat แจ้งยอดฝากเงินจริง บัญชีจะอัปเดตเป็นยอดจริงตามโบรกเกอร์
    """
    hub = XMBridgeHub()
    hub.allow_live = True

    # 1. พอร์ตจริงยังไม่ได้รับการเติมเงิน -> ค่าเริ่มต้นต้องเป็น $0.00
    chart_before = hub.get_trade_chart_data()
    real_kpi_before = chart_before["financial_kpi_summary"]["real_account"]
    assert real_kpi_before["balance"] == 0.0
    assert real_kpi_before["equity"] == 0.0
    assert real_kpi_before["pnl"] == 0.0
    assert "รอเติมเงินทุนจริง" in real_kpi_before["status"]

    # 2. จำลองได้รับ Heartbeat จาก MT5 พอร์ตจริงที่ฝากเงินแล้ว $3,500.00
    live_hb = {
        "token": hub.token,
        "account": 430446448,
        "broker": "XM Global Limited (Live 18)",
        "server": "XMGlobal-Real-18",
        "balance": 3500.00,
        "equity": 3585.50,
        "is_demo": False,
        "currency": "USD"
    }
    hub.record_heartbeat(live_hb)

    chart_after = hub.get_trade_chart_data()
    real_kpi_after = chart_after["financial_kpi_summary"]["real_account"]
    assert real_kpi_after["balance"] == 3500.00
    assert real_kpi_after["equity"] == 3585.50
    assert real_kpi_after["pnl"] == 85.50
    assert "Active" in real_kpi_after["status"]


def test_github_pusher_exclude_workflows_contract():
    """ตรวจสอบฟังก์ชัน exclude_workflows และ Smart Fallback ของ GitHubAutoPusher"""
    pusher = GitHubAutoPusher()
    assert hasattr(pusher, "push_project_to_github")
    assert hasattr(pusher, "_push_excluding_workflows")

    # ทดสอบว่าถ้า token ผิด จะคืนสถานะ AUTH_ERROR อย่างถูกต้อง พร้อม token creation link
    res = pusher.push_project_to_github(custom_token="invalid_pat_token", interactive_browser_login=False)
    assert res["status"] == "AUTH_ERROR"
    assert "token_url" in res
    assert "https://github.com/settings/tokens/new?scopes=repo,workflow&description=AI-Holding-Company-V8" in res["token_url"]


def test_github_pusher_mac_native_and_env_persistence():
    """
    ตรวจสอบฟังก์ชัน Auto-Pusher สำหรับ macOS:
    1. _git_env มี GIT_TERMINAL_PROMPT = '0'
    2. บันทึกและอ่าน GITHUB_TOKEN จาก .env
    3. Staged commit helper _ensure_git_committed
    4. เมื่อ token ไม่ถูกต้อง คืนสถานะ AUTH_ERROR
    5. REST API POST /api/github_push ตอบกลับ JSON ถูกต้อง
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        pusher = GitHubAutoPusher(repo_dir=tmpdir)
        # 1. ตรวจสอบ _git_env
        env = pusher._git_env()
        assert env.get("GIT_TERMINAL_PROMPT") == "0"

        # 2. ตรวจสอบการบันทึกและอ่าน .env
        assert pusher._read_token_from_env_file() == ""
        pusher._save_token_to_env_file("ghp_test_mock_token_123456")
        assert pusher._read_token_from_env_file() == "ghp_test_mock_token_123456"

        # บันทึกทับด้วย token ใหม่
        pusher._save_token_to_env_file("ghp_test_mock_token_789012")
        assert pusher._read_token_from_env_file() == "ghp_test_mock_token_789012"

    # 3. ตรวจสอบ push_project_to_github เมื่อ token ผิด
    pusher_real = GitHubAutoPusher()
    res_auth = pusher_real.push_project_to_github(custom_token="bad_token_xxx", interactive_browser_login=False)
    assert res_auth["status"] == "AUTH_ERROR"

    # 4. ตรวจสอบ MockServerHandler สำหรับ POST /api/github_push
    handler = MockServerHandler("POST", "/api/github_push", {"custom_token": "bad_token_api_test"})
    handler.do_POST()
    assert handler._response_status == 200
    res_api = handler.get_json_response()
    assert res_api["status"] == "AUTH_ERROR"


def test_open_source_curriculum_and_full_daily_token_burn():
    """
    ตรวจสอบระบบฝึกฝน AI ทั้ง 11 ตัวจากคลังความรู้ Open-Source เฉพาะทาง (OPEN_SOURCE_DOMAIN_CURRICULUM)
    พร้อมใช้โทเคนรายวันจนครบ 100.0% (remaining_tokens == 0) และ REST API POST /api/train_open_source_max
    """
    from engine.skill_harvester import SkillHarvesterEngine, OPEN_SOURCE_DOMAIN_CURRICULUM
    from engine.token_economy import TokenEconomyEngine

    assert len(OPEN_SOURCE_DOMAIN_CURRICULUM) == 11
    expected_agents = {
        "ag_macro", "ag_ta", "ag_quant", "ag_bear", "ag_cio",
        "ag_bot", "ag_risk", "ag_news", "ag_bull", "ag_venture", "ag_cos"
    }
    assert {item["agent_id"] for item in OPEN_SOURCE_DOMAIN_CURRICULUM} == expected_agents

    # 1. ทดสอบบนฐานข้อมูลแยกชั่วคราว (Isolated Temp DB)
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_os_burn.db")
        db = CompanyDatabase(db_path)
        harvester = SkillHarvesterEngine(db)
        res = harvester.train_all_agents_open_source_max_tokens({"current_price": 2715.40, "atr14": 18.0})

        assert res["status"] == "OK"
        assert res["total_agents_trained"] == 11
        assert len(res["agents_upgraded"]) == 11
        assert res["remaining_tokens"] == 0
        assert res["utilization_pct"] == 100.0
        assert res["total_tokens_used"] == res["daily_budget_tokens"]
        assert res["total_tokens_burned_in_session"] > 0

        econ = TokenEconomyEngine(db).get_economy_report()
        assert econ["remaining_tokens"] == 0
        assert econ["utilization_pct"] == 100.0
        assert econ["total_tokens_used"] == econ["daily_budget_tokens"]

        for ag_up in res["agents_upgraded"]:
            assert ag_up["compute_mode"] == "OVERCLOCK"
            assert ag_up["tokens_spent"] > 0
            assert ag_up["mastery_pct"] >= 95.0
            assert ag_up["levels_gained"] >= 2
            assert len(ag_up["repo"]) > 3
            assert len(ag_up["skill_name"]) > 5

    # 2. ทดสอบ trading_committee_roles ใน get_trade_chart_data() ว่ามี open_source_stack
    hub = XMBridgeHub()
    chart_data = hub.get_trade_chart_data()
    roles = chart_data["trading_committee_roles"]
    for role_key in ("macro_news", "technical_chartist", "quant_liquidity", "risk_officer", "chief_officer"):
        assert "open_source_stack" in roles[role_key]
        assert "learned_skill" in roles[role_key]
        assert roles[role_key]["mastery_pct"] >= 95.0

    summary = hub.get_status_summary()
    assert "open_source_training_summary" in summary
    assert summary["open_source_training_summary"]["total_agents_in_curriculum"] == 11

    # 3. ทดสอบ REST API Endpoint: POST /api/train_open_source_max
    handler = MockServerHandler("POST", "/api/train_open_source_max", {})
    handler.do_POST()
    assert handler._response_status == 200
    api_res = handler.get_json_response()
    assert api_res["status"] == "OK"
    assert api_res["remaining_tokens"] == 0
    assert api_res["utilization_pct"] == 100.0
    assert len(api_res["agents_upgraded"]) == 11
    assert "token_economy" in api_res
    assert api_res["token_economy"]["remaining_tokens"] == 0
    assert api_res["token_economy"]["utilization_pct"] == 100.0


def test_autonomous_learning_daemon_lifecycle_and_execution():
    """
    ตรวจสอบ Autonomous 24/7 Background Self-Learning Daemon:
    1. ตรวจสอบการเริ่มต้น Daemon Thread (daemon=True)
    2. รันวงจรการเรียนรู้อัตโนมัติ 1 รอบ (run_autonomous_learning_cycle)
    3. ตรวจสอบการอัปเดต telemetry, สถานะ Open-Source, บันทึกลง SQLite office_activity_log
    4. ตรวจสอบการสร้างไฟล์ reports/latest_dashboard.html
    """
    daemon_thread = start_autonomous_learning_daemon(interval_seconds=300, initial_delay_seconds=60.0)
    assert daemon_thread is not None
    assert daemon_thread.is_alive()
    assert AUTONOMOUS_LEARNING_CONFIG["active"] is True
    assert AUTONOMOUS_LEARNING_CONFIG["interval_seconds"] == 300
    assert "Open-Source" in AUTONOMOUS_LEARNING_CONFIG["auto_mode_desc"]

    # รันวงจรแบบ Synchronous เพื่อตรวจสอบผลลัพธ์
    cycle_res = run_autonomous_learning_cycle()
    assert cycle_res["status"] == "OK"
    assert "os_res" in cycle_res
    assert "pattern_rep" in cycle_res
    assert "ระบบเรียนรู้อัตโนมัติ 24/7" in cycle_res["summary"]

    assert AUTONOMOUS_LEARNING_CONFIG["last_cycle"] is not None
    assert AUTONOMOUS_LEARNING_CONFIG["total_cycles_completed"] >= 1
    assert AUTONOMOUS_LEARNING_CONFIG["last_cycle_details"]["agents_trained"] == 11

    # ตรวจสอบ office_activity_log ใน SQLite
    db = CompanyDatabase()
    logs = db.get_recent_activity_logs(limit=15)
    matching_log = any("ระบบเรียนรู้อัตโนมัติ 24/7" in l.get("summary", "") for l in logs)
    assert matching_log is True

    # ตรวจสอบการสร้างรายงาน HTML
    assert os.path.exists("reports/latest_dashboard.html")


def test_server_endpoints_autonomous_learning_telemetry():
    """
    ตรวจสอบ REST API endpoints (/api/state, /api/mt5/status, /api/autonomous_learning_cycle)
    ว่าเปิดเผยข้อมูล telemetry ของ Autonomous 24/7 Background Self-Learner อย่างครบถ้วน:
    - autonomous_learning_active
    - autonomous_learning_interval_seconds
    - last_autonomous_cycle
    - auto_mode_desc
    """
    # 1. GET /api/state
    handler_state = MockServerHandler("GET", "/api/state")
    handler_state.do_GET()
    assert handler_state._response_status == 200
    res_state = handler_state.get_json_response()
    assert res_state["status"] == "ok"
    assert res_state["autonomous_learning_active"] is True
    assert res_state["autonomous_learning_interval_seconds"] == 300
    assert "last_autonomous_cycle" in res_state
    assert "auto_mode_desc" in res_state
    assert "ระบบเรียนรู้ Open-Source อัตโนมัติ 24/7" in res_state["auto_mode_desc"]
    assert "autonomous_learning_telemetry" in res_state

    # 2. GET /api/mt5/status
    handler_mt5 = MockServerHandler("GET", "/api/mt5/status")
    handler_mt5.do_GET()
    assert handler_mt5._response_status == 200
    res_mt5 = handler_mt5.get_json_response()
    assert res_mt5["autonomous_learning_active"] is True
    assert res_mt5["autonomous_learning_interval_seconds"] == 300
    assert "last_autonomous_cycle" in res_mt5
    assert "auto_mode_desc" in res_mt5
    assert "ระบบเรียนรู้ Open-Source อัตโนมัติ 24/7" in res_mt5["auto_mode_desc"]

    # 3. POST /api/autonomous_learning_cycle
    handler_trigger = MockServerHandler("POST", "/api/autonomous_learning_cycle", {})
    handler_trigger.do_POST()
    assert handler_trigger._response_status == 200
    res_trigger = handler_trigger.get_json_response()
    assert res_trigger["status"] == "OK"
    assert "os_res" in res_trigger
    assert "pattern_rep" in res_trigger


def test_skill_harvester_concurrency_and_repeated_calls_thread_safe():
    """
    ตรวจสอบว่า train_all_agents_open_source_max_tokens สามารถถูกเรียกซ้ำใน Background
    ได้อย่างปลอดภัย ไร้ Deadlock และคุมเพดาน Token / Mastery ไม่ให้ทะลุขอบเขต
    """
    from engine.skill_harvester import SkillHarvesterEngine

    with tempfile.TemporaryDirectory() as tmpdir:
        test_db_path = os.path.join(tmpdir, "test_repeated_burn.db")
        test_db = CompanyDatabase(test_db_path)
        harvester = SkillHarvesterEngine(test_db)

        # เรียกซ้ำ 3 รอบติดต่อกัน จำลอง Daemon รันวน 24/7
        for cycle in range(3):
            out = harvester.train_all_agents_open_source_max_tokens({"current_price": 2720.0, "atr14": 18.5})
            assert out["status"] == "OK"
            assert out["total_agents_trained"] == 11
            assert out["remaining_tokens"] == 0
            assert out["utilization_pct"] == 100.0
            assert out["total_tokens_used"] == out["daily_budget_tokens"]

            for ag in out["agents_upgraded"]:
                assert ag["mastery_pct"] <= 100.0
                assert ag["accuracy_boost"] <= 25.0
                assert ag["stat_accuracy"] <= 99
                assert ag["stat_speed"] <= 99
                assert ag["stat_risk"] <= 99
                assert ag["stat_macro"] <= 99
                assert ag["stat_creativity"] <= 99

        # ตรวจสอบว่า discovered_skills ไม่เกิดการ Duplicate ผิดปกติจนล้น (4 seed skills + 11 open-source skills = 15)
        discovered = test_db.get_discovered_skills(limit=50)
        assert len(discovered) == 15
        os_discovered = [s for s in discovered if s.get("source_type") == "OPEN_SOURCE_MAX_BURN"]
        assert len(os_discovered) == 11


