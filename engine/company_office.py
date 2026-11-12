"""
24/7 AI Holding Company & Virtual Office Operations Manager
Coordinates all 11 AI Agents across 5 Departments, Real-Time News Sentinel,
Proven Strategy Benchmark Lab, Auto-Portfolio Bot, and Daily Executive Work Summaries.
"""
from datetime import datetime
from data.database import CompanyDatabase


class VirtualOfficeManager:
    def __init__(self, db: CompanyDatabase | None = None):
        self.db = db or CompanyDatabase()

    def process_realtime_news(self, raw_news: list[dict]) -> list[dict]:
        """Maya Lin (Real-Time News Sentinel) วิเคราะห์ระดับผลกระทบของข่าวต่อทองคำแบบเรียลไทม์"""
        enriched = []
        high_impact_count = 0

        high_kw = ["fed", "rate", "inflation", "cpi", "war", "geopolit", "central bank", "powell", "yield", "treasury", "gold", "tariff"]
        bull_kw = ["cut", "war", "tension", "safe-haven", "purchases", "buying", "soft", "drop", "lower"]
        bear_kw = ["hike", "strong dollar", "higher yield", "surge", "hawkish", "sell"]

        for item in raw_news:
            title = item.get("title", "")
            low_t = title.lower()

            impact = "HIGH IMPACT 🔴" if any(k in low_t for k in high_kw) else "MEDIUM IMPACT 🟡"
            if "HIGH" in impact:
                high_impact_count += 1

            if any(k in low_t for k in bull_kw):
                bias = "BULLISH GOLD (Safe-Haven / Rate Support)"
            elif any(k in low_t for k in bear_kw):
                bias = "BEARISH GOLD (Strong USD / Yield Pressure)"
            else:
                bias = "NEUTRAL / MARKET WATCH"

            self.db.log_news_item(title, impact, bias, monitored_by="Maya Lin (News Sentinel)")
            enriched.append({
                "title": title,
                "date": item.get("date", datetime.now().strftime("%Y-%m-%d %H:%M")),
                "impact": impact,
                "sentiment_bias": bias,
                "monitored_by": "Maya Lin"
            })

        task_desc = f"สแกนข่าวเรียลไทม์ {len(enriched)} หัวข้อ (พบข่าวกระทบสูง {high_impact_count} ข่าว)"
        self.db.update_agent_activity(
            agent_id="ag_news",
            status="MONITORING 24/7",
            current_task=task_desc,
            action_type="REALTIME_NEWS_SCAN",
            log_summary=f"{task_desc} — ล่าสุด: \"{enriched[0]['title'][:75]}...\"" if enriched else task_desc
        )
        return enriched

    def record_committee_work(
        self,
        market_snapshot: dict,
        benchmark_suite: dict,
        ta_result: dict,
        macro_result: dict,
        debate_result: dict,
        risk_result: dict,
        cio_verdict: dict
    ):
        """บันทึกสถานะและผลการทำงานของพนักงาน AI ทุกตัวลงฐานข้อมูลสำนักงาน 24 ชม."""
        best_strat = benchmark_suite.get("best_strategy", {})

        self.db.update_agent_activity(
            agent_id="ag_quant",
            status="BENCHMARKING",
            current_task=f"ชนะเลิศ: {best_strat.get('strategy_name')} (Win Rate {best_strat.get('live_win_rate')}%, PF {best_strat.get('live_pf')})",
            action_type="STRATEGY_AUDIT",
            log_summary=f"ทดสอบเปรียบเทียบ 4 กลยุทธ์วิจัยระดับสถาบัน คัดเลือก '{best_strat.get('strategy_name')}' (Win Rate {best_strat.get('live_win_rate')}%)"
        )

        self.db.update_agent_activity(
            agent_id="ag_ta",
            status="ANALYZING CHARTS",
            current_task=f"สแกน XAUUSD ${market_snapshot.get('current_price'):,.2f} -> {ta_result.get('bias')} (Score {ta_result.get('score'):+d})",
            action_type="TECHNICAL_SCAN",
            log_summary=f"วิเคราะห์ D1 ({market_snapshot.get('d1_trend')}) + H1 ({market_snapshot.get('trend')}) เสนอจุดเข้า ${ta_result.get('suggested_entry'):,.2f}"
        )

        self.db.update_agent_activity(
            agent_id="ag_macro",
            status="MACRO WATCH",
            current_task=f"ติดตาม DXY ({market_snapshot.get('dxy_index')}) & US10Y ({market_snapshot.get('us10y_yield')}%) -> {macro_result.get('macro_bias')}",
            action_type="MACRO_ANALYSIS",
            log_summary=f"ประเมินเศรษฐกิจมหภาค คะแนน {macro_result.get('score'):+d}/100 ({macro_result.get('macro_bias')})"
        )

        self.db.update_agent_activity(
            agent_id="ag_bull",
            status="DEBATING (BULL)",
            current_task=f"ขึ้นดีเบตฝั่งซื้อ (Bull Power {debate_result.get('bull_power')}%) อ้างอิงแนวรับ ${market_snapshot.get('support'):,.2f}",
            action_type="BULL_DEBATE",
            log_summary=f"เสนอเหตุผลฝั่งกระทิงด้วยคะแนนโหวต {debate_result.get('bull_power')}%"
        )

        self.db.update_agent_activity(
            agent_id="ag_bear",
            status="DEBATING (BEAR/RED TEAM)",
            current_task=f"ขึ้นดีเบตฝั่งขาย/จับผิด (Bear Power {debate_result.get('bear_power')}%) เตือน Stop Hunt ${debate_result.get('trap_zone_low'):,.2f}",
            action_type="BEAR_REDTEAM_DEBATE",
            log_summary=f"ชี้จุดเสี่ยง Liquidity Sweep และโต้แย้งด้วยคะแนนโหวต {debate_result.get('bear_power')}%"
        )

        self.db.update_agent_activity(
            agent_id="ag_risk",
            status="RISK GUARD",
            current_task=f"ตรวจสอบ R:R ({risk_result.get('rr_ratio')}) และอนุมัติขนาด {risk_result.get('recommended_lot')} Lot",
            action_type="RISK_AUDIT",
            log_summary=f"อนุมัติขนาดออเดอร์ {risk_result.get('recommended_lot')} Lot (ความเสี่ยง ${risk_result.get('actual_dollar_risk'):,.2f}, R:R {risk_result.get('rr_ratio')})"
        )

        self.db.update_agent_activity(
            agent_id="ag_cio",
            status="DECISION ISSUED",
            current_task=f"ออกมติ '{cio_verdict.get('action')}' @ ${cio_verdict.get('final_entry'):,.2f} (ความเชื่อมั่น {cio_verdict.get('conviction_pct')}%)",
            action_type="CIO_VERDICT",
            log_summary=f"ฟันธงมติ '{cio_verdict.get('action')}' Entry ${cio_verdict.get('final_entry'):,.2f} | SL ${cio_verdict.get('final_sl'):,.2f} | TP1 ${cio_verdict.get('final_tp1'):,.2f}"
        )

        self.db.update_agent_activity(
            agent_id="ag_venture",
            status="INCUBATING IDEAS",
            current_task="ดูแลโครงสร้าง 5 แผนก พร้อมเชื่อมต่อไอเดียธุรกิจใหม่ (Crypto / SaaS / Automation)",
            action_type="VENTURE_CHECK",
            log_summary="ตรวจสอบความพร้อมของสล็อตแผนกธุรกิจใหม่ (Crypto Alpha Desk & AI Micro-SaaS Desk พร้อมใช้งาน)"
        )

    def generate_daily_executive_digest(self, portfolio_state: dict, benchmark_suite: dict, enriched_news: list[dict]) -> dict:
        """Sophia Chen (Chief of Staff) สรุปรายงานการทำงานตลอด 24 ชม. ของพนักงาน AI ทุกตัว"""
        agents = self.db.get_all_agents()
        recent_logs = self.db.get_recent_activity_logs(limit=20)
        divisions = self.db.get_business_divisions()

        total_tasks_today = sum(int(a.get("tasks_completed_today", 0)) for a in agents)
        best_strat = benchmark_suite.get("best_strategy", {})

        digest_text = (
            f"📋 [สรุปผลการปฏิบัติงานสำนักงาน AI ตลอด 24 ชม. — โดย Sophia Chen (Chief of Staff)]:\n"
            f"• พนักงาน AI ประจำการครบ {len(agents)} ตัว ใน {len(divisions)} แผนก ปฏิบัติภารกิจสำเร็จรวมวันนี้ {total_tasks_today} งาน\n"
            f"• หน่วยข่าวเรียลไทม์ (Maya Lin): เฝ้าติดตามข่าวสำคัญ {len(enriched_news)} ประเด็น โดยข่าวเด่นคือ \"{enriched_news[0]['title'] if enriched_news else 'Market Watch'}\" ({enriched_news[0]['impact'] if enriched_news else 'NORMAL'})\n"
            f"• ห้องแล็บวิจัยกลยุทธ์ (Dr. Kenji Sato): ทดสอบ 4 กลยุทธ์มาตรฐานระดับโลก พบว่า '{best_strat.get('strategy_name')}' ให้ความแม่นยำสูงสุดในตลาดปัจจุบัน (Win Rate {best_strat.get('live_win_rate')}%, PF {best_strat.get('live_pf')})\n"
            f"• บอทจัดการพอร์ตอัตโนมัติ (AutoBot X-1): สถานะโหมด {portfolio_state.get('execution_mode')} | Equity ปัจจุบัน ${portfolio_state.get('equity'):,.2f} (Floating PnL: ${portfolio_state.get('floating_pnl'):+.2f}) | ถือออเดอร์ {len(portfolio_state.get('open_positions', []))} ไม้ | Win Rate พอร์ตจริง {portfolio_state.get('live_win_rate_pct')}%"
        )

        self.db.update_agent_activity(
            agent_id="ag_cos",
            status="REPORTING 24/7",
            current_task=f"สรุปผลงานประจำวันรวม {total_tasks_today} งาน จากพนักงาน AI 11 ตัว",
            action_type="DAILY_SUMMARY",
            log_summary=f"จัดทำรายงานสรุปประจำวันเสร็จสิ้น (รวม {total_tasks_today} ภารกิจ, Equity พอร์ต ${portfolio_state.get('equity'):,.2f})"
        )

        return {
            "chief_of_staff": "Sophia Chen",
            "total_agents": len(agents),
            "total_tasks_today": total_tasks_today,
            "agents_roster": self.db.get_all_agents(),
            "recent_activity_logs": self.db.get_recent_activity_logs(limit=20),
            "business_divisions": divisions,
            "digest_summary": digest_text
        }
