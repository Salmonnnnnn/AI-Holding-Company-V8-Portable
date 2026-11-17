"""
Local HTTP/JSON Web Server for AI Holding Company V7 (Ultra-Detailed Cozy Isometric Visualizer,
Light/Dark Theme Switcher, 12+ Frontier Models & Custom Model Adder, Offline Shift Auto-Catchup,
True Historical Candle/Shift Replay, Token Treasury Allocator & Autonomous Skill Harvester)
"""
import os
import sys
import json
import threading
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from engine.committee_room import TradingCommitteeRoom
from engine.dashboard_generator import generate_html_dashboard
from engine.github_pusher import GitHubAutoPusher
from engine.llm_router import MultiLLMRouter
from engine.mt5_bridge import xm_bridge_hub, check_xauusd_market_status
from engine.token_economy import TokenEconomyEngine

GLOBAL_ROOM = None
LATEST_REPORT = None

# Autonomous 24/7 background self-learning daemon telemetry and state
AUTONOMOUS_LEARNING_CONFIG = {
    "active": True,
    "interval_seconds": 300,
    "last_cycle": None,
    "auto_mode_desc": "ระบบเรียนรู้ Open-Source อัตโนมัติ 24/7 ทำงานในพื้นหลังตลอดเวลาเมื่อ AI ว่าง",
    "total_cycles_completed": 0,
    "last_cycle_details": {}
}

_AUTONOMOUS_DAEMON_THREAD = None
_AUTONOMOUS_DAEMON_LOCK = threading.Lock()


def run_autonomous_learning_cycle() -> dict:
    """
    Executes one autonomous background self-learning cycle across all 11 AI agents:
    1. Trains all agents on open-source domain curriculum using reasoning tokens.
    2. Backtests 60-day historical gold candles for pattern recognition.
    3. Caches metrics in XMBridgeHub.
    4. Logs activity to office_activity_log and updates agent status in SQLite.
    5. Syncs Obsidian Vault and updates reports/latest_dashboard.html.
    6. Updates daemon telemetry.
    """
    global GLOBAL_ROOM, LATEST_REPORT
    room, report = ensure_state()
    market_session = check_xauusd_market_status()
    market_snapshot = report.get("market_snapshot", {})

    # 1. Open-source max token training
    os_res = room.skill_harvester.train_all_agents_open_source_max_tokens(market_snapshot)

    # 2. Historical 60-day big data pattern backtest
    df_h1 = getattr(room.market_engine, "last_h1_df", None)
    pattern_rep = room.skill_trainer.train_on_historical_big_data(df_h1)

    # 3. Update XMBridgeHub cache
    xm_bridge_hub._cached_comparison = pattern_rep.get("performance_comparison", {})
    xm_bridge_hub._cached_learned_patterns = pattern_rep.get("pattern_rankings", [])
    xm_bridge_hub._cached_open_source_summary = {
        "total_agents_in_curriculum": os_res.get("total_agents_trained", 11),
        "daily_budget_tokens": os_res.get("daily_budget_tokens", 1000000),
        "total_tokens_used": os_res.get("total_tokens_used", 1000000),
        "remaining_tokens": os_res.get("remaining_tokens", 0),
        "utilization_pct": os_res.get("utilization_pct", 100.0),
        "curriculum": os_res.get("curriculum", [])
    }

    # 4. Record background self-study in SQLite activity log
    summary_text = "ระบบเรียนรู้อัตโนมัติ 24/7 (Background Auto-Learner) ทำงานต่อเนื่อง: อัปเดตโมเดล Open-Source และแบ็กเทสต์กราฟย้อนหลัง"
    if hasattr(room.db, "add_office_activity_log"):
        room.db.add_office_activity_log(
            agent_name="Autonomous 24/7 Auto-Learner",
            department="Central Knowledge Core",
            action_type="BACKGROUND_SELF_LEARNING",
            summary=summary_text
        )
    room.db.update_agent_activity(
        agent_id="ag_cio",
        status="เรียนรู้อัตโนมัติ 24/7 🧠",
        current_task="ระบบเรียนรู้อัตโนมัติ 24/7 ทำงานต่อเนื่อง: อัปเดตโมเดล Open-Source และแบ็กเทสต์กราฟย้อนหลัง",
        action_type="BACKGROUND_AUTO_LEARN",
        log_summary=summary_text
    )

    # 5. Update latest report in memory
    report["token_economy"] = os_res.get("token_economy", {})
    report["discovered_skills"] = os_res.get("all_discovered_skills", [])
    report["agents"] = room.db.get_all_agents()
    report["pattern_training_report"] = pattern_rep

    # 6. Sync Obsidian Vault & regenerate HTML dashboard
    obs_info = room.obsidian_sync.sync_all(report)
    report["obsidian_status"] = obs_info
    dash_path = os.path.join(os.getcwd(), "reports", "latest_dashboard.html")
    os.makedirs(os.path.dirname(dash_path), exist_ok=True)
    generate_html_dashboard(report, dash_path)

    # 7. Update telemetry
    now_iso = datetime.now(timezone.utc).isoformat()
    AUTONOMOUS_LEARNING_CONFIG["last_cycle"] = now_iso
    AUTONOMOUS_LEARNING_CONFIG["total_cycles_completed"] += 1
    AUTONOMOUS_LEARNING_CONFIG["last_cycle_details"] = {
        "timestamp": now_iso,
        "agents_trained": os_res.get("total_agents_trained", 11),
        "tokens_burned": os_res.get("total_tokens_burned_in_session", 0),
        "patterns_learned": len(pattern_rep.get("pattern_rankings", [])),
        "ai_confluence_score": pattern_rep.get("ai_confluence_score", 0.0),
        "market_mode": "WEEKEND_RESEARCH" if not market_session.get("is_open") else "IDLE_SELF_STUDY"
    }

    xm_bridge_hub.update_autonomous_learning_status(
        active=AUTONOMOUS_LEARNING_CONFIG.get("active", True),
        interval_seconds=AUTONOMOUS_LEARNING_CONFIG.get("interval_seconds", 300),
        last_cycle=now_iso,
        desc=AUTONOMOUS_LEARNING_CONFIG.get("auto_mode_desc")
    )

    return {
        "status": "OK",
        "timestamp": now_iso,
        "os_res": os_res,
        "pattern_rep": pattern_rep,
        "summary": summary_text
    }


def start_autonomous_learning_daemon(interval_seconds: int = 300, initial_delay_seconds: float = 2.0) -> threading.Thread:
    """
    Spawns the Autonomous 24/7 Background Self-Learning Daemon Thread.
    Runs continuously, executing self-learning cycles periodically when agents are idle,
    during market closures, or whenever idle token budget is available.
    """
    global _AUTONOMOUS_DAEMON_THREAD
    with _AUTONOMOUS_DAEMON_LOCK:
        AUTONOMOUS_LEARNING_CONFIG["interval_seconds"] = interval_seconds
        AUTONOMOUS_LEARNING_CONFIG["active"] = True

        if _AUTONOMOUS_DAEMON_THREAD is not None and _AUTONOMOUS_DAEMON_THREAD.is_alive():
            return _AUTONOMOUS_DAEMON_THREAD

        def _daemon_loop():
            if initial_delay_seconds > 0:
                time.sleep(initial_delay_seconds)
            while AUTONOMOUS_LEARNING_CONFIG.get("active", True):
                try:
                    run_autonomous_learning_cycle()
                except Exception as ex:
                    print(f"⚠️ [Autonomous Learning Daemon] Error during cycle: {ex}")

                # Sleep in 1-second chunks so daemon responds quickly to shutdown
                elapsed = 0.0
                target_interval = AUTONOMOUS_LEARNING_CONFIG.get("interval_seconds", 300)
                sim_tick = 0
                while elapsed < target_interval and AUTONOMOUS_LEARNING_CONFIG.get("active", True):
                    time.sleep(1.0)
                    elapsed += 1.0
                    sim_tick += 1
                    if sim_tick >= 10:
                        sim_tick = 0
                        if not xm_bridge_hub.is_connected and xm_bridge_hub.auto_trade_enabled:
                            try:
                                xm_bridge_hub.simulate_step()
                            except Exception:
                                pass
                    target_interval = AUTONOMOUS_LEARNING_CONFIG.get("interval_seconds", 300)

        _AUTONOMOUS_DAEMON_THREAD = threading.Thread(
            target=_daemon_loop,
            name="Autonomous24x7LearningDaemon",
            daemon=True
        )
        _AUTONOMOUS_DAEMON_THREAD.start()
        return _AUTONOMOUS_DAEMON_THREAD


def stop_autonomous_learning_daemon():
    """Stops the autonomous 24/7 background learning daemon."""
    with _AUTONOMOUS_DAEMON_LOCK:
        AUTONOMOUS_LEARNING_CONFIG["active"] = False


def ensure_state():
    global GLOBAL_ROOM, LATEST_REPORT
    if GLOBAL_ROOM is None:
        GLOBAL_ROOM = TradingCommitteeRoom()
    if LATEST_REPORT is None:
        LATEST_REPORT = GLOBAL_ROOM.run_session(capital=1000.0, risk_pct=1.5)
        os.makedirs("reports", exist_ok=True)
        generate_html_dashboard(LATEST_REPORT, "reports/latest_dashboard.html")
    # Start autonomous background learning daemon automatically
    start_autonomous_learning_daemon()
    return GLOBAL_ROOM, LATEST_REPORT


class V7RequestHandler(BaseHTTPRequestHandler):
    @property
    def db(self):
        room, _ = ensure_state()
        return room.db

    def send_json_response(self, status: int, payload: dict):
        self._send_json(payload, status=status)

    def _send_json(self, payload: dict, status: int = 200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        room, report = ensure_state()
        if self.path in ("/", "/index.html", "/latest_dashboard.html"):
            dash_path = os.path.join(os.getcwd(), "reports", "latest_dashboard.html")
            if not os.path.exists(dash_path):
                generate_html_dashboard(report, dash_path)
            with open(dash_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        if self.path.startswith("/api/state"):
            venture_ledger = room.db.get_venture_ledger_summary(report.get("portfolio_state"))
            self._send_json({
                "status": "ok",
                "session_time": report.get("session_time"),
                "market_snapshot": report.get("market_snapshot", {}),
                "portfolio_state": report.get("portfolio_state", {}),
                "venture_ledger": venture_ledger,
                "integration_status": room.db.get_integration_status(),
                "agents": room.db.get_all_agents(),
                "available_models": room.llm_router.get_available_models(),
                "token_economy": room.token_economy.get_economy_report(),
                "discovered_skills": room.db.get_discovered_skills(20),
                "offline_catchup": report.get("offline_catchup", {}),
                "chat_history": room.db.get_chat_history(30),
                "obsidian_status": report.get("obsidian_status", {}),
                "autonomous_learning_active": AUTONOMOUS_LEARNING_CONFIG.get("active", True),
                "autonomous_learning_interval_seconds": AUTONOMOUS_LEARNING_CONFIG.get("interval_seconds", 300),
                "last_autonomous_cycle": AUTONOMOUS_LEARNING_CONFIG.get("last_cycle"),
                "auto_mode_desc": AUTONOMOUS_LEARNING_CONFIG.get("auto_mode_desc", "ระบบเรียนรู้ Open-Source อัตโนมัติ 24/7 ทำงานในพื้นหลังตลอดเวลาเมื่อ AI ว่าง"),
                "autonomous_learning_telemetry": {
                    "total_cycles_completed": AUTONOMOUS_LEARNING_CONFIG.get("total_cycles_completed", 0),
                    "last_cycle_details": AUTONOMOUS_LEARNING_CONFIG.get("last_cycle_details", {})
                }
            })
            return

        if self.path.startswith("/api/mt5/status"):
            # Update simulation step if in demo mode and not connected to real EA
            if not xm_bridge_hub.is_connected and xm_bridge_hub.auto_trade_enabled:
                try:
                    xm_bridge_hub.simulate_step()
                except Exception:
                    pass
            st = xm_bridge_hub.get_status_summary()
            st["autonomous_learning_active"] = AUTONOMOUS_LEARNING_CONFIG.get("active", True)
            st["autonomous_learning_interval_seconds"] = AUTONOMOUS_LEARNING_CONFIG.get("interval_seconds", 300)
            st["last_autonomous_cycle"] = AUTONOMOUS_LEARNING_CONFIG.get("last_cycle")
            st["auto_mode_desc"] = AUTONOMOUS_LEARNING_CONFIG.get("auto_mode_desc", "ระบบเรียนรู้ Open-Source อัตโนมัติ 24/7 ทำงานในพื้นหลังตลอดเวลาเมื่อ AI ว่าง")
            self._send_json(st)
            return

        if self.path.startswith("/api/mt5/positions"):
            self._send_json({
                "status": "OK",
                "open_positions": xm_bridge_hub.get_open_positions(),
                "count": len(xm_bridge_hub.open_positions),
                "auto_trade_enabled": xm_bridge_hub.auto_trade_enabled
            })
            return

        if self.path.startswith("/api/mt5/history"):
            self._send_json({
                "status": "OK",
                "closed_trades": xm_bridge_hub.get_closed_trades(),
                "count": len(xm_bridge_hub.closed_trades),
                "total_profit": round(sum(float(t.get("profit", 0.0)) for t in xm_bridge_hub.closed_trades), 2)
            })
            return

        if self.path.startswith("/api/mt5/chart_comparison"):
            self._send_json(xm_bridge_hub.get_trade_chart_data())
            return

        if self.path.startswith("/api/mt5/comparison"):
            self._send_json(xm_bridge_hub.get_performance_comparison())
            return

        if self.path.startswith("/api/mt5/token"):
            self._send_json({"status": "ok", "token": xm_bridge_hub.token})
            return

        path = self.path.split("?")[0]
        if path in ("/api/free_llm_quota", "/api/free_llm_quota/"):
            econ = getattr(room, "token_economy", None) or TokenEconomyEngine(self.db)
            rep = econ.get_economy_report()
            self.send_json_response(200, rep)
            return

        if self.path.startswith("/api/free_llm_quota") or self.path.startswith("/api/token_economy"):
            econ_rep = (getattr(room, "token_economy", None) or TokenEconomyEngine(self.db)).get_economy_report()
            self._send_json({
                "status": "ok",
                "total_company_used_today": econ_rep.get("total_company_used_today", 0),
                "total_company_ceiling_daily": econ_rep.get("total_company_ceiling_daily", 5300000),
                "total_company_display": econ_rep.get("total_company_display", ""),
                "total_lifetime_tokens": econ_rep.get("total_lifetime_tokens", 0),
                "total_usd_saved": econ_rep.get("total_usd_saved", 0.0),
                "bot_quotas": econ_rep.get("bot_quotas", []),
                "bot_quotas_dict": econ_rep.get("bot_quotas_dict", {}),
                "free_llm_providers": econ_rep.get("free_llm_providers", {}),
                "active_provider": econ_rep.get("active_provider", {}),
                "fallback_chain": econ_rep.get("fallback_chain", []),
                "bot_historical_token_table": econ_rep.get("bot_historical_token_table", []),
                "provider_telemetry": econ_rep.get("provider_telemetry", []),
                "failover_history": econ_rep.get("failover_history", []),
                "token_economy": econ_rep
            })
            return

        self._send_json({"error": "Not found"}, status=404)

    def do_POST(self):
        global LATEST_REPORT
        room, report = ensure_state()
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            body = json.loads(raw)
        except Exception:
            body = {}

        path = self.path.split("?")[0]
        if path in ("/api/failover_check", "/api/failover_check/", "/api/free_llm_quota", "/api/free_llm_quota/"):
            econ = getattr(room, "token_economy", None) or TokenEconomyEngine(self.db)
            res = econ.check_failover_status(body)
            self._send_json(res)
            return

        if self.path in ("/api/autonomous_learning_cycle", "/api/mt5/autonomous_learning_cycle"):
            res = run_autonomous_learning_cycle()
            self._send_json(res)
            return

        if self.path == "/api/chat":
            msg = body.get("message", "")
            target_agent = body.get("target_agent", "antigravity")
            res = room.chat_copilot.answer_user_message(msg, target_agent, report)
            self._send_json(res)
            return

        if self.path == "/api/summarize":
            date_str = body.get("date", datetime.now().strftime("%Y-%m-%d"))
            time_slot = body.get("time_slot", "FULL_24H")
            style = body.get("style", "EXECUTIVE_CUTE")
            res = room.chat_copilot.generate_time_window_summary(
                date_str=date_str,
                time_slot=time_slot,
                style=style,
                latest_report=report,
                df_h1=room.market_engine.last_h1_df
            )
            self._send_json(res)
            return

        if self.path == "/api/offline_catchup":
            hours = float(body.get("offline_hours", 12.0))
            res = room.offline_catchup.run_auto_catchup(
                df_h1=room.market_engine.last_h1_df,
                latest_report=report,
                simulated_offline_hours=hours
            )
            report["offline_catchup"] = res
            room.obsidian_sync.sync_all(report)
            self._send_json(res)
            return

        if self.path == "/api/add_custom_model":
            model_id = body.get("model_id", "GPT-5 Preview (256K)")
            specialty = body.get("specialty", "โมเดล AI ระดับท็อปที่ผู้บริหารเพิ่มเข้าระบบ")
            added = room.db.add_custom_model(model_id=model_id, specialty=specialty)
            report["available_models"] = room.llm_router.get_available_models()
            self._send_json({"status": "ok", "model": added, "available_models": report["available_models"]})
            return

        if self.path == "/api/allocate_tokens":
            agent_id = body.get("agent_id", "ag_cio")
            token_quota = int(body.get("token_quota", 80000))
            compute_mode = body.get("compute_mode", "BALANCED")
            llm_model = body.get("llm_model")
            instant_boost = int(body.get("instant_boost_tokens", 0))
            econ = room.token_economy.allocate_tokens_to_agent(
                agent_id=agent_id,
                token_quota=token_quota,
                compute_mode=compute_mode,
                llm_model=llm_model,
                instant_boost_tokens=instant_boost
            )
            report["token_economy"] = econ
            self._send_json(econ)
            return

        if self.path == "/api/learn_skill":
            agent_id = body.get("agent_id", "ag_quant")
            skill_topic = body.get("skill_topic", "ICT New York Killzone Silver Bullet")
            tokens_to_spend = int(body.get("tokens_to_spend", 50000))
            res = room.skill_harvester.discover_new_skill(
                agent_id=agent_id,
                skill_topic=skill_topic,
                tokens_to_spend=tokens_to_spend,
                market_snapshot=report.get("market_snapshot", {})
            )
            report["discovered_skills"] = res["all_discovered_skills"]
            report["token_economy"] = room.token_economy.get_economy_report()
            room.obsidian_sync.sync_all(report)
            self._send_json(res)
            return

        if self.path == "/api/switch_model":
            agent_id = body.get("agent_id", "ag_cio")
            llm_model = body.get("llm_model") or body.get("model_id") or "Claude 3.7 Sonnet (Extended Thinking 128K)"
            updated = room.db.update_agent_model(agent_id, llm_model)
            self._send_json({"status": "ok", **updated})
            return

        if self.path == "/api/train":
            market_data = report.get("market_snapshot", {})
            benchmarks = report.get("strategy_benchmarks", {})
            skill_rep = room.skill_trainer.run_self_training_cycle(room.market_engine.last_h1_df, market_data, benchmarks)
            # Train patterns on historical 60-day gold big data
            pattern_rep = room.skill_trainer.train_on_historical_big_data(room.market_engine.last_h1_df)
            xm_bridge_hub._cached_comparison = pattern_rep.get("performance_comparison", {})
            xm_bridge_hub._cached_learned_patterns = pattern_rep.get("pattern_rankings", [])
            skill_rep["pattern_training_report"] = pattern_rep
            report["skill_training_report"] = skill_rep
            report["pattern_training_report"] = pattern_rep
            self._send_json({"status": "ok", "skill_training_report": skill_rep, "pattern_training_report": pattern_rep})
            return

        if self.path == "/api/mt5/train_patterns":
            pattern_rep = room.skill_trainer.train_on_historical_big_data(room.market_engine.last_h1_df)
            xm_bridge_hub._cached_comparison = pattern_rep.get("performance_comparison", {})
            xm_bridge_hub._cached_learned_patterns = pattern_rep.get("pattern_rankings", [])
            report["pattern_training_report"] = pattern_rep
            self._send_json({
                "status": "OK",
                "learned_patterns": pattern_rep.get("pattern_rankings", []),
                "comparison": pattern_rep.get("performance_comparison", {}),
                "ai_confluence_score": pattern_rep.get("ai_confluence_score", 0.0),
                "total_candles_analyzed": pattern_rep.get("total_candles_analyzed", 0),
                "top_pattern": pattern_rep.get("top_pattern", {})
            })
            return

        if self.path in ("/api/train_open_source_max", "/api/mt5/train_open_source_max"):
            os_res = room.skill_harvester.train_all_agents_open_source_max_tokens(report.get("market_snapshot", {}))
            pattern_rep = room.skill_trainer.train_on_historical_big_data(room.market_engine.last_h1_df)
            xm_bridge_hub._cached_comparison = pattern_rep.get("performance_comparison", {})
            xm_bridge_hub._cached_learned_patterns = pattern_rep.get("pattern_rankings", [])
            xm_bridge_hub._cached_open_source_summary = {
                "total_agents_in_curriculum": os_res.get("total_agents_trained", 11),
                "daily_budget_tokens": os_res.get("daily_budget_tokens", 1000000),
                "total_tokens_used": os_res.get("total_tokens_used", 1000000),
                "remaining_tokens": os_res.get("remaining_tokens", 0),
                "utilization_pct": os_res.get("utilization_pct", 100.0),
                "curriculum": os_res.get("curriculum", [])
            }
            report["token_economy"] = os_res["token_economy"]
            report["discovered_skills"] = os_res["all_discovered_skills"]
            report["agents"] = room.db.get_all_agents()
            report["pattern_training_report"] = pattern_rep
            obs_info = room.obsidian_sync.sync_all(report)
            report["obsidian_status"] = obs_info
            self._send_json({
                **os_res,
                "agents": report["agents"],
                "pattern_training_report": pattern_rep,
                "learned_patterns": pattern_rep.get("pattern_rankings", []),
                "ai_confluence_score": pattern_rep.get("ai_confluence_score", 0.0),
                "obsidian_status": obs_info
            })
            return

        if self.path == "/api/sync_obsidian":
            obs_info = room.obsidian_sync.sync_all(report)
            report["obsidian_status"] = obs_info
            self._send_json({"status": "ok", "obsidian_status": obs_info})
            return

        if self.path == "/api/github_push":
            try:
                repo_name = body.get("repo_name", "AI-Holding-Company-V8-Portable")
                private = bool(body.get("private", False))
                custom_token = body.get("custom_token", "")
                exclude_workflows = bool(body.get("exclude_workflows", False))
                pusher = GitHubAutoPusher()
                res = pusher.push_project_to_github(
                    repo_name=repo_name,
                    private=private,
                    custom_token=custom_token,
                    interactive_browser_login=True,
                    exclude_workflows=exclude_workflows
                )
                self._send_json(res)
            except Exception as e:
                self._send_json({
                    "status": "ERROR",
                    "message": f"⚠️ เกิดข้อผิดพลาดขณะดึงขึ้น GitHub: {str(e)}",
                    "steps_log": [f"❌ Push Exception: {str(e)}"]
                }, status=500)
            return

        # ==========================================
        # MT5 EA Algorithmic Bridge Endpoints (XM / MetaTrader 5)
        # ==========================================
        if self.path == "/api/mt5/heartbeat":
            token = body.get("token", "")
            if not xm_bridge_hub.verify_token(token):
                self._send_json({"status": "UNAUTHORIZED", "error": "Invalid or missing MT5 bridge token"}, status=401)
                return
            xm_bridge_hub.record_heartbeat(body)
            pending_commands = xm_bridge_hub.pop_pending_commands()
            self._send_json({
                "status": "OK",
                "commands": pending_commands,
                "kill_switch": xm_bridge_hub.kill_switch,
                "daily_loss_pct": round(xm_bridge_hub.daily_loss_pct, 2),
                "server_time": datetime.now().isoformat()
            })
            return

        if self.path == "/api/mt5/ack":
            token = body.get("token", "")
            if not xm_bridge_hub.verify_token(token):
                self._send_json({"status": "UNAUTHORIZED", "error": "Invalid or missing MT5 bridge token"}, status=401)
                return
            cmd_id = str(body.get("cmd_id", ""))
            status = str(body.get("status", "DONE"))
            ticket = body.get("ticket")
            price = body.get("price")
            err_msg = str(body.get("error", ""))
            ack_rec = xm_bridge_hub.acknowledge_command(
                cmd_id=cmd_id,
                status=status,
                ticket=int(ticket) if ticket is not None else None,
                fill_price=float(price) if price is not None else None,
                error_msg=err_msg
            )
            self._send_json({"status": "OK", "cmd_id": cmd_id, "ack": ack_rec})
            return

        if self.path == "/api/mt5/kill_switch":
            res = xm_bridge_hub.trigger_kill_switch("Emergency stop commanded from Web UI / API")
            self._send_json({"status": "HALTED", "kill_switch": True, **res})
            return

        if self.path == "/api/mt5/resume":
            xm_bridge_hub.kill_switch = False
            res = xm_bridge_hub.resume_trading()
            self._send_json({"status": "RESUMED", "kill_switch": False, **res})
            return

        if self.path == "/api/mt5/auto_trade":
            if "enabled" in body:
                enabled = bool(body["enabled"])
            else:
                enabled = not xm_bridge_hub.auto_trade_enabled
            current = xm_bridge_hub.set_auto_trade(enabled)
            market_session = check_xauusd_market_status()
            notice = ""
            if enabled and not market_session["is_open"]:
                notice = f"เปิดโหมด Auto-Trade สำเร็จ แต่{market_session['market_closed_reason']} บอทจะวิจัยย้อนหลังและเตรียมส่งคำสั่งเมื่อตลาดเปิด"
            self._send_json({
                "status": "OK",
                "auto_trade_enabled": current,
                "is_market_open": market_session["is_open"],
                "market_session": market_session,
                "notice": notice,
                "open_positions": xm_bridge_hub.get_open_positions(),
                "closed_trades": xm_bridge_hub.get_closed_trades()
            })
            return

        if self.path == "/api/mt5/close_all":
            reason = str(body.get("reason", "Manual Close All"))
            res = xm_bridge_hub.close_all_positions(reason=reason)
            self._send_json({
                "status": "QUEUED",
                **res,
                "open_positions": xm_bridge_hub.get_open_positions(),
                "closed_trades": xm_bridge_hub.get_closed_trades()
            })
            return

        if self.path == "/api/mt5/close_ticket":
            ticket = body.get("ticket")
            if not ticket:
                self._send_json({"status": "ERROR", "reason": "Missing ticket number"}, status=400)
                return
            res = xm_bridge_hub.close_ticket(int(ticket))
            self._send_json({
                "status": "QUEUED",
                "command": res,
                "ticket": int(ticket),
                "closed_trade": res.get("closed_trade"),
                "open_positions": xm_bridge_hub.get_open_positions(),
                "closed_trades": xm_bridge_hub.get_closed_trades()
            })
            return

        if self.path in ("/api/mt5/simulate_step", "/api/mt5/step"):
            cur_p = body.get("current_price")
            res = xm_bridge_hub.simulate_step(cur_p)
            self._send_json({"status": "OK", **res})
            return

        if self.path == "/api/mt5/manual":
            action = body.get("action") or body.get("cmd_type") or "BUY"
            lot = float(body.get("lot") or body.get("volume") or 0.01)
            sl_points = float(body.get("sl_points") or body.get("sl_distance") or 18.0)
            tp_points = float(body.get("tp_points") or body.get("tp_distance") or 35.0)
            symbol = body.get("symbol", "XAUUSD")
            comment = body.get("comment", "WebUI_Manual_Order")

            cmd = xm_bridge_hub.queue_command(
                cmd_type=action,
                symbol=symbol,
                volume=lot,
                sl_distance=sl_points,
                tp_distance=tp_points,
                comment=comment
            )
            if cmd.get("status") == "REJECTED":
                self._send_json(cmd, status=400)
            else:
                self._send_json({"status": "QUEUED", "command": cmd})
            return

        if self.path == "/api/refresh_live_market":
            LATEST_REPORT = room.run_session(capital=1000.0, risk_pct=1.5)
            os.makedirs("reports", exist_ok=True)
            generate_html_dashboard(LATEST_REPORT, "reports/latest_dashboard.html")
            self._send_json({
                "status": "ok",
                "market_snapshot": LATEST_REPORT["market_snapshot"],
                "portfolio_state": LATEST_REPORT["portfolio_state"],
                "venture_ledger": LATEST_REPORT["venture_ledger"],
                "cio_verdict": LATEST_REPORT["cio_verdict"],
                "session_time": LATEST_REPORT["session_time"],
            })
            return

        if self.path == "/api/save_integrations":
            keys = body.get("keys", {})
            int_status = room.db.save_integration_keys(keys)
            room.llm_router = MultiLLMRouter(room.db)
            room.chat_copilot.llm_router = room.llm_router
            report["integration_status"] = int_status
            os.makedirs("reports", exist_ok=True)
            generate_html_dashboard(report, "reports/latest_dashboard.html")
            self._send_json({"status": "ok", "integration_status": int_status})
            return

        if self.path == "/api/add_venture_tx":
            studio_key = body.get("studio_key", "ONLINE_STORE")
            venture_name = body.get("venture_name", "Studio Product Sale")
            description = body.get("description", "Verified studio revenue")
            amount_usd = float(body.get("amount_usd", 25.0))
            ledger = room.db.add_venture_transaction(
                studio_key=studio_key,
                venture_name=venture_name,
                description=description,
                amount_usd=amount_usd,
                source_type="MANUAL_VERIFIED"
            )
            report["venture_ledger"] = ledger
            if "portfolio_state" in report and isinstance(report["portfolio_state"], dict):
                report["portfolio_state"]["ventures"] = {
                    "trading": ledger["trading"],
                    "store": ledger["store"],
                    "tech": ledger["tech"],
                    "media": ledger["media"],
                }
            os.makedirs("reports", exist_ok=True)
            generate_html_dashboard(report, "reports/latest_dashboard.html")
            self._send_json({"status": "ok", "venture_ledger": ledger})
            return

        if self.path == "/api/portfolio_action":
            command = body.get("command", "OPEN_CIO_TRADE")
            cur_price = float(body.get("market_price") or report.get("market_snapshot", {}).get("current_price", 2685.0))
            trade_id = body.get("trade_id")
            lot_size = float(body.get("lot_size", 0.02))
            port_state = room.db.execute_portfolio_command(
                command=command,
                market_price=cur_price,
                cio_verdict=report.get("cio_verdict", {}),
                trade_id=trade_id,
                lot_size=lot_size
            )
            ledger = room.db.get_venture_ledger_summary(port_state)
            port_state["ventures"] = {
                "trading": ledger["trading"],
                "store": ledger["store"],
                "tech": ledger["tech"],
                "media": ledger["media"],
            }
            report["portfolio_state"] = port_state
            report["venture_ledger"] = ledger
            os.makedirs("reports", exist_ok=True)
            generate_html_dashboard(report, "reports/latest_dashboard.html")
            self._send_json({
                "status": "ok",
                "portfolio_state": port_state,
                "venture_ledger": ledger,
            })
            return

        if self.path == "/api/viral_studio/approve":
            new_status = body.get("status", "APPROVED")
            if isinstance(LATEST_REPORT, dict) and "studio_deliverables" in LATEST_REPORT:
                meme_st = LATEST_REPORT["studio_deliverables"].get("MEME_STUDIO", {})
                if "current_script_package" in meme_st:
                    meme_st["current_script_package"]["status"] = new_status
            with room.db._get_conn() as conn:
                cur = conn.cursor()
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute("""
                    INSERT INTO office_activity_log (timestamp, agent_name, department, action_type, summary)
                    VALUES (?, ?, ?, ?, ?)
                """, (now, "The Boss", "YouTube & Viral Studio", "SCRIPT_APPROVED", f"ผู้บริหารตรวจและอนุมัติสคริปต์ลงช่อง (สถานะ: {new_status}) — วิดีโอยาว 10:24m พร้อม 3 Shorts"))
                conn.commit()
            os.makedirs("reports", exist_ok=True)
            generate_html_dashboard(LATEST_REPORT, "reports/latest_dashboard.html")
            self._send_json({"status": "ok", "package_status": new_status, "message": "อนุมัติสคริปต์ลงช่องสำเร็จ"})
            return

        if self.path == "/api/viral_studio/connect_business_email":
            biz_email = str(body.get("business_email", "")).strip()
            yt_handle = str(body.get("youtube_handle", "@TheDailyFindsMedia")).strip()
            tt_handle = str(body.get("tiktok_handle", "@thedailyfinds.media")).strip()
            fb_handle = str(body.get("facebook_handle", "The Daily Finds Official")).strip()
            conn_status = str(body.get("status", "CONNECTED" if biz_email else "PENDING_SETUP"))

            if isinstance(LATEST_REPORT, dict):
                if "studio_deliverables" not in LATEST_REPORT:
                    LATEST_REPORT["studio_deliverables"] = {}
                if "MEME_STUDIO" not in LATEST_REPORT["studio_deliverables"]:
                    LATEST_REPORT["studio_deliverables"]["MEME_STUDIO"] = {}
                meme_st = LATEST_REPORT["studio_deliverables"]["MEME_STUDIO"]
                meme_st["business_email"] = biz_email
                meme_st["business_email_status"] = conn_status
                meme_st["youtube_handle"] = yt_handle
                meme_st["tiktok_handle"] = tt_handle
                meme_st["facebook_handle"] = fb_handle
                if "youtube_progress" in meme_st and conn_status == "CONNECTED":
                    meme_st["youtube_progress"]["status"] = "CONNECTED"
                if "tiktok_metrics" in meme_st and conn_status == "CONNECTED":
                    meme_st["tiktok_metrics"]["status"] = "CONNECTED"
                if "facebook_metrics" in meme_st and conn_status == "CONNECTED":
                    meme_st["facebook_metrics"]["status"] = "CONNECTED"

            with room.db._get_conn() as conn:
                cur = conn.cursor()
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute("""
                    INSERT INTO office_activity_log (timestamp, agent_name, department, action_type, summary)
                    VALUES (?, ?, ?, ?, ?)
                """, (now, "The Boss", "YouTube & Viral Studio", "CONNECT_BUSINESS_EMAIL",
                      f"เชื่อมโยงอีเมลธุรกิจ '{biz_email or 'media.dailyfinds@gmail.com'}' (สถานะ: {conn_status}) เข้ากับ YouTube ({yt_handle}), TikTok ({tt_handle}), Facebook ({fb_handle})"))
                conn.commit()

            os.makedirs("reports", exist_ok=True)
            generate_html_dashboard(LATEST_REPORT, "reports/latest_dashboard.html")
            self._send_json({
                "status": "ok",
                "message": "บันทึกและเชื่อมโยงอีเมลธุรกิจกับช่องโซเชียลมีเดียเรียบร้อยแล้ว",
                "business_email": biz_email,
                "business_email_status": conn_status,
                "youtube_handle": yt_handle,
                "tiktok_handle": tt_handle,
                "facebook_handle": fb_handle,
            })
            return

        if self.path == "/api/viral_studio/adapt_trend_feed":
            trend_idx = int(body.get("trend_index", 0))
            topic = str(body.get("topic", "")).strip()
            platform = str(body.get("platform", "Multi-Platform Trending")).strip()

            if not topic:
                topic = "กลยุทธ์สร้างเครื่องจักรเงินสดอัตโนมัติในยุค AI"

            adapted_package = {
                "status": "READY_FOR_REVIEW",
                "title": f"แกะรอย {topic}: ความลับที่เปลี่ยนระบบการสร้างรายได้ (ดัดแปลงจาก {platform})",
                "adapted_from": {"topic": topic, "platform": platform, "trend_index": trend_idx},
                "youtube_longform": {
                    "duration": "10:15 นาที",
                    "midroll_breaks": ["03:45", "07:15"],
                    "sections": [
                        {
                            "time": "00:00 - 00:45",
                            "phase": f"Hook & Pattern Interrupt ({platform} Insight)",
                            "b_roll": f"พาดหัวข่าวด่วน คลิปกระแสไวรัลเกี่ยวกับ {topic} และสถิติที่น่าตกใจ",
                            "script": f"คุณรู้ไหมว่าทำไมประเด็น {topic} ถึงกลายเป็นกระแสที่มีคนดูหลายล้านวิว? แต่สิ่งที่ไม่มีใครยอมบอกคุณคือเบื้องหลังกลไกที่แท้จริง...",
                        },
                        {
                            "time": "00:45 - 03:45",
                            "phase": "The Core Shift: ปัญหาที่ 99% มองข้าม",
                            "b_roll": "กราฟิกเปรียบเทียบข้อมูล flow chart แผนภาพโมเดลระบบอัตโนมัติ",
                            "script": f"คนส่วนใหญ่เห็นเพียงยอดภูเขาน้ำแข็ง แต่โครงสร้างที่ขับเคลื่อน {topic} คือคานงัดที่เราสามารถนำมาปรับใช้ได้ทันที...",
                        },
                        {
                            "time": "03:45 - 07:15",
                            "phase": "Actionable Framework [จุดแทรกโฆษณา Ad #1 ที่ 03:45]",
                            "b_roll": "ภาพสตรีมมิ่งเซิร์ฟเวอร์ หน้าต่างการเทรด และการจัดการกระแสเงินสด",
                            "script": f"ขั้นตอนที่หนึ่งในการต่อยอดเรื่องนี้... [จุดแทรกโฆษณา Ad #1 ที่ 03:45 ค่าโฆษณา AdSense สูงสุด] ให้สร้างระบบทำงานแทนแรงกาย...",
                        },
                        {
                            "time": "07:15 - 09:15",
                            "phase": "Case Study & Reality Check [จุดแทรกโฆษณา Ad #2 ที่ 07:15]",
                            "b_roll": "ตารางตัวเลข Before/After และหลักฐานเชิงประจักษ์",
                            "script": f"มาดูตัวอย่างจริงเมื่อเราใช้สูตรนี้... [จุดแทรกโฆษณา Ad #2 ที่ 07:15 เพื่อดัน Watch Time สูงสุด] ผลลัพธ์ที่ได้จะทบต้นอย่างก้าวกระโดด...",
                        },
                        {
                            "time": "09:15 - 10:15",
                            "phase": "High-Retention Outro & CTA",
                            "b_roll": "ปุ่มกด Subscribe โลโก้ @TheDailyFindsMedia และคลิปแนะนำถัดไป",
                            "script": "กดติดตาม @TheDailyFindsMedia เพื่อไม่พลาดการวิเคราะห์เทรนด์และกลยุทธ์ธุรกิจ AI ก่อนใคร...",
                        },
                    ],
                },
                "shorts_derivatives": [
                    {
                        "platform": "YouTube Shorts (9:16)",
                        "duration": "55s",
                        "hook": f"ความจริง 1 นาทีเกี่ยวกับ {topic}!",
                        "script": f"หยุดเลื่อนผ่าน! ถ้าคุณกำลังตามเรื่อง {topic} นี่คือ 3 สิ่งที่คุณต้องรู้ก่อนเริ่ม...",
                    },
                    {
                        "platform": "Facebook Reels (9:16)",
                        "duration": "48s",
                        "hook": f"3 เรื่องจริงของ {topic} ที่คนส่วนใหญ่ไม่รู้",
                        "script": f"แชร์คลิปนี้เก็บไว้เลย! สรุปใจความสำคัญของ {topic} ใน 48 วินาที...",
                    },
                    {
                        "platform": "TikTok (9:16)",
                        "duration": "50s",
                        "hook": f"ทำไม {topic} ถึงกำลังเปลี่ยนทุกสิ่งในปี 2026?",
                        "script": f"อย่าเพิ่งเชื่อจนกว่าคุณจะได้ดูคลิปนี้... นี่คือเหตุผลที่ {topic} สำคัญกับคุณ...",
                    },
                ],
                "faceless_assets": {
                    "voiceover_tone": "เสียงสุขุม คมชัด น่าเชื่อถือ เว้นจังหวะ 0.5s ทุกจุดเน้น (Narrative Authority)",
                    "b_roll_prompts": f"Cinematic 4K, dark moody tech aesthetic, financial data animation for {topic}, high retention cuts",
                    "youtube_seo_tags": ["TheDailyFinds", "วิเคราะห์เทรนด์", "AdSense", "AI2026", "passive income", "สารคดีธุรกิจ"],
                },
            }

            if isinstance(LATEST_REPORT, dict):
                if "studio_deliverables" not in LATEST_REPORT:
                    LATEST_REPORT["studio_deliverables"] = {}
                if "MEME_STUDIO" not in LATEST_REPORT["studio_deliverables"]:
                    LATEST_REPORT["studio_deliverables"]["MEME_STUDIO"] = {}
                LATEST_REPORT["studio_deliverables"]["MEME_STUDIO"]["current_script_package"] = adapted_package

            with room.db._get_conn() as conn:
                cur = conn.cursor()
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute("""
                    INSERT INTO office_activity_log (timestamp, agent_name, department, action_type, summary)
                    VALUES (?, ?, ?, ?, ?)
                """, (now, "Maya Lin", "YouTube & Viral Studio", "ADAPT_TREND_FEED",
                      f"ดึงเทรนด์ '{topic}' ({platform}) มาดัดแปลงเป็นสคริปต์คลิปยาว 10:15m พร้อม 3 Shorts ประจำช่องสำเร็จ"))
                conn.commit()

            os.makedirs("reports", exist_ok=True)
            generate_html_dashboard(LATEST_REPORT, "reports/latest_dashboard.html")
            self._send_json({
                "status": "ok",
                "message": f"ดัดแปลงเทรนด์ '{topic}' เป็นแพ็กเกจสคริปต์เรียบร้อยแล้ว",
                "current_script_package": adapted_package,
            })
            return

        self._send_json({"error": "Unknown endpoint"}, status=404)

    def log_message(self, format, *args):
        return


def run_server(port: int = 8080):
    ensure_state()
    start_autonomous_learning_daemon()
    server = ThreadingHTTPServer(("127.0.0.1", port), V7RequestHandler)
    print(f"🚀 AI Holding Company V7 Live Server running at http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    port_arg = int(os.getenv("PORT", "8080"))
    run_server(port_arg)
