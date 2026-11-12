"""
Offline Shift Auto-Catchup Engine (V7)
When the user turns off their PC and turns it back on later (or triggers a catch-up),
this engine checks how many hours/shifts elapsed while offline, reconstructs the missing
shifts from real historical gold candles, awards EXP & skills to the AI agents,
and logs a complete Catch-Up Summary into SQLite & Obsidian.
"""
from datetime import datetime, timedelta
from data.database import CompanyDatabase
from engine.historical_replay import HistoricalReplayEngine


SHIFT_SEQUENCE = ["NIGHT_AUDIT", "MORNING_ASIA", "AFTERNOON_LONDON", "EVENING_NY"]


class OfflineCatchupEngine:
    def __init__(self, db: CompanyDatabase | None = None):
        self.db = db or CompanyDatabase()
        self.replay = HistoricalReplayEngine(self.db)

    def run_auto_catchup(
        self,
        df_h1,
        latest_report: dict,
        simulated_offline_hours: float | None = None
    ) -> dict:
        """ตรวจสอบและเก็บตกงานย้อนหลังทุกกะในช่วงที่ปิดคอมไป"""
        agents = self.db.get_all_agents()
        now = datetime.now()

        if simulated_offline_hours is not None:
            offline_hours = float(simulated_offline_hours)
        else:
            last_str = agents[0].get("last_active") if agents else None
            try:
                last_dt = datetime.strptime(last_str, "%Y-%m-%d %H:%M:%S")
                diff_h = (now - last_dt).total_seconds() / 3600.0
                offline_hours = max(0.5, diff_h)
            except Exception:
                offline_hours = 6.0

        # คำนวณจำนวนกะที่ต้องเก็บตก (1 กะ = 6 ชม., เก็บตกอย่างน้อย 1 กะเพื่อให้ข้อมูลครบเสมอยามเปิดเครื่อง)
        shifts_to_recover = max(1, min(8, int(round(offline_hours / 6.0)) or 1))
        recovered_snapshots = []
        total_tokens_burned = 0
        total_exp_awarded = 0

        for i in range(shifts_to_recover):
            shift_dt = now - timedelta(hours=6 * (shifts_to_recover - 1 - i))
            date_str = shift_dt.strftime("%Y-%m-%d")
            hr = shift_dt.hour
            if 0 <= hr < 6:
                slot = "NIGHT_AUDIT"
            elif 6 <= hr < 12:
                slot = "MORNING_ASIA"
            elif 12 <= hr < 18:
                slot = "AFTERNOON_LONDON"
            else:
                slot = "EVENING_NY"

            snap = self.replay.reconstruct_shift_report(
                date_str=date_str,
                time_slot=slot,
                style="EXECUTIVE_CUTE",
                df_h1=df_h1,
                latest_report=latest_report
            )
            recovered_snapshots.append({
                "date_str": date_str,
                "time_slot": slot,
                "slot_label": snap["slot_label"],
                "open_price": snap["open_price"],
                "close_price": snap["close_price"],
                "change_dollar": snap["change_dollar"],
                "verdict_action": snap["verdict_action"],
                "tokens_burned": snap["tokens_burned"]
            })
            total_tokens_burned += int(snap["tokens_burned"])
            total_exp_awarded += 120

        # แจก EXP ชดเชยช่วงปิดคอมให้หัวหน้าทีมวิจัยและ CIO
        self.db.add_agent_exp_and_knowledge(
            agent_id="ag_quant",
            exp_gain=total_exp_awarded,
            skill_domain="Offline Shift Catch-Up",
            insight_title=f"เก็บตกกราฟย้อนหลังช่วงปิดคอม ({shifts_to_recover} กะ)",
            learned_parameters=f"Offline={offline_hours:.1f}h | Shifts={shifts_to_recover} | Tokens={total_tokens_burned:,}",
            confidence_boost=0.8
        )

        summary_msg = (
            f"⚡ ระบบ Auto-Catchup เก็บตกงานช่วงปิดคอม ({offline_hours:.1f} ชม. / {shifts_to_recover} กะเวลา) เรียบร้อยแล้ว! "
            f"ดึงกราฟย้อนหลังจริง คำนวณมติทุกกะ และแจก +{total_exp_awarded} EXP ให้ทีม AI ครบถ้วน"
        )
        log_entry = self.db.log_offline_catchup(
            offline_hours=offline_hours,
            shifts_recovered=shifts_to_recover,
            tokens_burned=total_tokens_burned,
            exp_awarded=total_exp_awarded,
            summary=summary_msg
        )

        return {
            "status": "RECOVERED",
            "offline_hours": round(offline_hours, 1),
            "shifts_recovered": shifts_to_recover,
            "total_tokens_burned": total_tokens_burned,
            "total_exp_awarded": total_exp_awarded,
            "summary": summary_msg,
            "recovered_shifts": recovered_snapshots,
            "recent_catchup_logs": self.db.get_recent_catchup_logs(8),
            "latest_log": log_entry
        }
