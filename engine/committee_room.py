"""
Committee Room V7 - Orchestrating the Ultra-Detailed Cozy Isometric AI Visualizer (@ong_stw style),
Light/Dark Mode Theme Support, 12 Frontier Heavy-Reasoning Models + Custom Model Registry,
Offline Shift Auto-Catchup (for when PC is turned off), Historical Candle/Shift Replay,
Token Treasury Allocator, Autonomous Skill Harvester, 4 Proven Quant Strategies & Live Chat.
"""
from datetime import datetime
from data.market_data import MarketDataEngine
from data.news_fetcher import NewsFetcher
from data.database import CompanyDatabase
from agents.technical_agent import TechnicalAgent
from agents.macro_agent import MacroAgent
from agents.debater_agent import DebaterAgent
from agents.risk_agent import RiskAgent
from agents.cio_agent import CIOAgent
from engine.backtester import StrategyBacktester
from engine.strategy_benchmark import StrategyBenchmarkLab
from engine.portfolio_bot import AutoPortfolioBot
from engine.company_office import VirtualOfficeManager
from engine.skill_trainer import SkillTrainerEngine
from engine.mt5_bridge import MT5ExecutionBridge
from engine.obsidian_sync import ObsidianVaultSync
from engine.llm_router import MultiLLMRouter
from engine.chat_copilot import ChatCopilotEngine
from engine.token_economy import TokenEconomyEngine
from engine.skill_harvester import SkillHarvesterEngine
from engine.historical_replay import HistoricalReplayEngine
from engine.offline_catchup import OfflineCatchupEngine


class TradingCommitteeRoom:
    def __init__(self, db_path: str | None = None, vault_dir: str | None = None):
        self.db = CompanyDatabase(db_path) if db_path else CompanyDatabase()
        self.market_engine = MarketDataEngine()
        self.news_fetcher = NewsFetcher()
        self.ta_agent = TechnicalAgent()
        self.macro_agent = MacroAgent()
        self.debater_agent = DebaterAgent()
        self.risk_agent = RiskAgent()
        self.cio_agent = CIOAgent()
        self.backtester = StrategyBacktester()
        self.benchmark_lab = StrategyBenchmarkLab()
        self.portfolio_bot = AutoPortfolioBot(self.db)
        self.office_manager = VirtualOfficeManager(self.db)
        self.skill_trainer = SkillTrainerEngine(self.db)
        self.mt5_bridge = MT5ExecutionBridge()
        self.obsidian_sync = ObsidianVaultSync(vault_dir) if vault_dir else ObsidianVaultSync()
        self.llm_router = MultiLLMRouter(self.db)
        self.chat_copilot = ChatCopilotEngine(self.db)
        self.token_economy = TokenEconomyEngine(self.db)
        self.skill_harvester = SkillHarvesterEngine(self.db)
        self.replay_engine = HistoricalReplayEngine(self.db)
        self.offline_catchup = OfflineCatchupEngine(self.db)

    def run_session(self, capital: float = 1000.0, risk_pct: float = 1.5) -> dict:
        """รันการทำงานครบวงจรของสำนักงาน AI V7 พร้อมเก็บตกงานช่วงที่ปิดคอม (Offline Auto-Catchup)"""
        now_hm = datetime.now().strftime("%H:%M")

        # 1. ดึงข้อมูลตลาด Multi-Timeframe (D1 + H1) และข่าวสาร
        market_snapshot = self.market_engine.get_market_snapshot()
        raw_news = self.news_fetcher.get_latest_news()

        # 2. หน่วยข่าวเรียลไทม์ (Maya Lin) สแกนและจัดลำดับความแรงของข่าว
        enriched_news = self.office_manager.process_realtime_news(raw_news)

        # 3. ห้องแล็บวิจัย (Dr. Kenji Sato) ทดสอบเปรียบเทียบ 4 กลยุทธ์มาตรฐานระดับโลกบนกราฟจริง
        benchmark_suite = self.benchmark_lab.run_all_benchmarks(self.market_engine.last_h1_df)
        backtest_stats = self.backtester.run_backtest(self.market_engine.last_h1_df)

        # 4. ห้องฝึกสกิล (AI Skill Academy) รัน Self-Training
        skill_training_report = self.skill_trainer.run_self_training_cycle(
            df=self.market_engine.last_h1_df,
            market_snapshot=market_snapshot,
            benchmark_suite=benchmark_suite
        )

        # 5. วิเคราะห์ทางเทคนิค (D1 + H1 + ATR) และมหภาค (DXY + US10Y + News)
        ta_result = self.ta_agent.analyze(market_snapshot)
        macro_result = self.macro_agent.analyze(market_snapshot, enriched_news)

        # 6. เปิดห้องดีเบต Bull Advocate vs. Bear & Red Team
        debate_result = self.debater_agent.debate(ta_result, macro_result, market_snapshot)

        # 7. ฝ่ายบริหารความเสี่ยงคำนวณ Lot Size และตรวจสอบสถิติ
        risk_result = self.risk_agent.evaluate_risk(
            entry=ta_result['suggested_entry'],
            sl=ta_result['suggested_sl'],
            tp=ta_result['suggested_tp'],
            capital=capital,
            risk_pct=risk_pct,
            backtest_stats=backtest_stats
        )

        # 8. ประธาน CIO ออกมติชี้ขาด
        verdict = self.cio_agent.formulate_verdict(
            ta_result=ta_result,
            macro_result=macro_result,
            debate_result=debate_result,
            risk_result=risk_result,
            market_data=market_snapshot
        )

        # 9. บันทึกการทำงานของทีมวิเคราะห์ลงฐานข้อมูลสำนักงาน
        self.office_manager.record_committee_work(
            market_snapshot=market_snapshot,
            benchmark_suite=benchmark_suite,
            ta_result=ta_result,
            macro_result=macro_result,
            debate_result=debate_result,
            risk_result=risk_result,
            cio_verdict=verdict
        )

        # 10. บอทจัดการพอร์ตอัตโนมัติ (AutoBot X-1)
        best_strat_name = benchmark_suite.get("best_strategy", {}).get("strategy_name", "Donchian 20 Breakout")
        portfolio_state = self.portfolio_bot.sync_and_execute(
            market_data=market_snapshot,
            cio_verdict=verdict,
            best_strategy_name=best_strat_name,
            capital=capital
        )
        venture_ledger = self.db.get_venture_ledger_summary(portfolio_state)
        portfolio_state["ventures"] = {
            "trading": venture_ledger["trading"],
            "store": venture_ledger["store"],
            "tech": venture_ledger["tech"],
            "media": venture_ledger["media"],
        }

        # 11. จำลองและบันทึกขั้นตอนการยิงออเดอร์ MT5 Demo สดๆ 8 ขั้นตอน
        mt5_demo_telemetry = self.mt5_bridge.simulate_live_mt5_demo_execution(
            cio_verdict=verdict,
            market_data=market_snapshot,
            best_strategy_name=best_strat_name
        )

        # 12. เลขาธิการ (Sophia Chen) สรุปรายงานการทำงาน 24 ชม.
        office_digest = self.office_manager.generate_daily_executive_digest(
            portfolio_state=portfolio_state,
            benchmark_suite=benchmark_suite,
            enriched_news=enriched_news
        )

        # 13. สร้างรายการเช็กลิสต์ "ภารกิจวันนี้" สไตล์คลิป @ong_stw (8 ขั้นตอนครบวงจร)
        workflow_checklist = [
            {"step": 1, "agent": "Sophia Chen", "room": "ห้องต้อนรับ & รับบรีฟ", "title": "รับบรีฟภารกิจ & จัดสรรงบ Token", "detail": "เปิดรอบงาน จัดสรรโควต้าโทเคนให้ 11 แผนก", "time": now_hm, "status": "DONE"},
            {"step": 2, "agent": "Maya Lin", "room": "ห้องเรดาร์ข่าวสาร", "title": "สแกนข่าวด่วน Fed & ภูมิรัฐศาสตร์", "detail": f"ตรวจพบข่าวสำคัญ {len(enriched_news)} รายการ (Grok-3 Thinking)", "time": now_hm, "status": "DONE"},
            {"step": 3, "agent": "Dr. Kenji Sato", "room": "ห้องแล็บวิจัย & สกิล", "title": "ทดสอบ 4 กลยุทธ์ & วิจัยสกิลใหม่", "detail": f"ชนะเลิศ: {best_strat_name} (o1-Pro Reasoning)", "time": now_hm, "status": "DONE"},
            {"step": 4, "agent": "Alex Vance", "room": "ห้องวิเคราะห์กราฟ", "title": "สแกนกราฟทองคำ D1/H1 & ATR", "detail": f"ราคา ${market_snapshot.get('current_price'):,.2f} | ATR ${market_snapshot.get('atr14')}", "time": now_hm, "status": "DONE"},
            {"step": 5, "agent": "Dr. Marcus Sterling", "room": "ห้องวิจัยมหภาค", "title": "วิเคราะห์ค่าเงิน DXY & บอนด์ยีลด์", "detail": f"DXY {market_snapshot.get('dxy_index')} | US10Y {market_snapshot.get('us10y_yield')}%", "time": now_hm, "status": "DONE"},
            {"step": 6, "agent": "Sarah vs Viktor", "room": "ห้องดีเบตกลยุทธ์", "title": "ดีเบต Bull vs Bear & จับผิดแผน", "detail": f"Bull {debate_result.get('bull_power')}% vs Bear {debate_result.get('bear_power')}%", "time": now_hm, "status": "DONE"},
            {"step": 7, "agent": "Elena Rostova", "room": "ห้องตรวจสอบความเสี่ยง", "title": "คำนวณ Lot Size & เพดานความเสี่ยง", "detail": f"อนุมัติ {verdict.get('recommended_lot')} Lot (R:R {verdict.get('rr_ratio')})", "time": now_hm, "status": "DONE"},
            {"step": 8, "agent": "Arthur & AutoBot", "room": "ห้องตัดสินใจ CIO & MT5", "title": "ฟันธงมติ CIO & ส่งคำสั่ง MT5", "detail": f"สั่ง {verdict.get('action')} @ ${verdict.get('final_entry'):,.2f}", "time": now_hm, "status": "DONE"}
        ]

        report = {
            "session_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "market_snapshot": market_snapshot,
            "latest_news": enriched_news,
            "backtest_stats": backtest_stats,
            "strategy_benchmarks": benchmark_suite,
            "skill_training_report": skill_training_report,
            "technical_analysis": ta_result,
            "macro_analysis": macro_result,
            "debate_critique": debate_result,
            "risk_assessment": risk_result,
            "cio_verdict": verdict,
            "portfolio_state": portfolio_state,
            "venture_ledger": venture_ledger,
            "integration_status": self.db.get_integration_status(),
            "mt5_demo_telemetry": mt5_demo_telemetry,
            "office_digest": office_digest,
            "available_models": self.llm_router.get_available_models(),
            "token_economy": self.token_economy.get_economy_report(),
            "discovered_skills": self.db.get_discovered_skills(20),
            "workflow_checklist": workflow_checklist,
            "chat_history": self.db.get_chat_history(limit=30)
        }

        # 14. รันระบบ Offline Shift Auto-Catchup เก็บตกงานย้อนหลังช่วงที่ปิดคอมไป
        catchup_info = self.offline_catchup.run_auto_catchup(
            df_h1=self.market_engine.last_h1_df,
            latest_report=report
        )
        report["offline_catchup"] = catchup_info

        # 15. ซิงค์ข้อมูลทั้งหมดลง Obsidian Second-Brain Vault
        obsidian_info = self.obsidian_sync.sync_all(report)
        report["obsidian_status"] = obsidian_info

        return report
