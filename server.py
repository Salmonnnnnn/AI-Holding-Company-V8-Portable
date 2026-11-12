"""
Local HTTP/JSON Web Server for AI Holding Company V7 (Ultra-Detailed Cozy Isometric Visualizer,
Light/Dark Theme Switcher, 12+ Frontier Models & Custom Model Adder, Offline Shift Auto-Catchup,
True Historical Candle/Shift Replay, Token Treasury Allocator & Autonomous Skill Harvester)
"""
import os
import sys
import json
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from datetime import datetime

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from engine.committee_room import TradingCommitteeRoom
from engine.dashboard_generator import generate_html_dashboard

GLOBAL_ROOM = None
LATEST_REPORT = None


def ensure_state():
    global GLOBAL_ROOM, LATEST_REPORT
    if GLOBAL_ROOM is None:
        GLOBAL_ROOM = TradingCommitteeRoom()
    if LATEST_REPORT is None:
        LATEST_REPORT = GLOBAL_ROOM.run_session(capital=1000.0, risk_pct=1.5)
        os.makedirs("reports", exist_ok=True)
        generate_html_dashboard(LATEST_REPORT, "reports/latest_dashboard.html")
    return GLOBAL_ROOM, LATEST_REPORT


class V7RequestHandler(BaseHTTPRequestHandler):
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
            self._send_json({
                "status": "ok",
                "session_time": report.get("session_time"),
                "agents": room.db.get_all_agents(),
                "available_models": room.llm_router.get_available_models(),
                "token_economy": room.token_economy.get_economy_report(),
                "discovered_skills": room.db.get_discovered_skills(20),
                "offline_catchup": report.get("offline_catchup", {}),
                "chat_history": room.db.get_chat_history(30),
                "obsidian_status": report.get("obsidian_status", {}),
            })
            return

        self._send_json({"error": "Not found"}, status=404)

    def do_POST(self):
        room, report = ensure_state()
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            body = json.loads(raw)
        except Exception:
            body = {}

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
            report["skill_training_report"] = skill_rep
            self._send_json({"status": "ok", "skill_training_report": skill_rep})
            return

        if self.path == "/api/sync_obsidian":
            obs_info = room.obsidian_sync.sync_all(report)
            report["obsidian_status"] = obs_info
            self._send_json({"status": "ok", "obsidian_status": obs_info})
            return

        self._send_json({"error": "Unknown endpoint"}, status=404)

    def log_message(self, format, *args):
        return


def run_server(port: int = 8080):
    ensure_state()
    server = ThreadingHTTPServer(("127.0.0.1", port), V7RequestHandler)
    print(f"🚀 AI Holding Company V7 Live Server running at http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    port_arg = int(os.getenv("PORT", "8080"))
    run_server(port_arg)
