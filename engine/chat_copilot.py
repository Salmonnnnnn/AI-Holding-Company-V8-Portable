"""
Interactive Live Chat Copilot (Antigravity & 11 AI Agents) + Historical Candle Time-Machine Summarizer (V6)
"""
from datetime import datetime
from data.database import CompanyDatabase
from engine.llm_router import MultiLLMRouter
from engine.historical_replay import HistoricalReplayEngine


class ChatCopilotEngine:
    def __init__(self, db: CompanyDatabase | None = None):
        self.db = db or CompanyDatabase()
        self.router = MultiLLMRouter()
        self.replay_engine = HistoricalReplayEngine(self.db)

    def answer_user_message(self, user_message: str, target_agent_id: str, latest_report: dict) -> dict:
        """ตอบคำถามสดที่ผู้ใช้พิมพ์เข้ามาในหน้าเว็บ ผ่าน Antigravity หรือ AI Agent ที่เลือก"""
        market = latest_report.get("market_snapshot", {})
        cio = latest_report.get("cio_verdict", {})
        bench = latest_report.get("strategy_benchmarks", {})
        port = latest_report.get("portfolio_state", {})
        skill_rep = latest_report.get("skill_training_report", {})
        tok_rep = latest_report.get("token_economy", {})
        agents = self.db.get_all_agents()

        selected_ag = None
        for ag in agents:
            if ag["agent_id"] == target_agent_id:
                selected_ag = ag
                break

        if not selected_ag or target_agent_id in ("antigravity", "Antigravity Copilot"):
            speaker_name = "🤖 Antigravity (Head AI Architect & Copilot)"
            speaker_role = "Lead System Architect & Trading Firm Orchestrator"
            model_used = "Claude 3.7 Sonnet (Extended Thinking 128K) + Gemini 2.5 Pro Hybrid"
            ag_id_for_tok = "ag_cio"
        else:
            speaker_name = f"{selected_ag.get('avatar', '🤖')} {selected_ag.get('name')}"
            speaker_role = selected_ag.get("role", "AI Specialist")
            model_used = selected_ag.get("llm_model", "Claude 3.7 Sonnet (Extended Thinking 128K)")
            ag_id_for_tok = selected_ag["agent_id"]

        best_strat = bench.get("best_strategy", {})

        sys_prompt = (
            f"คุณคือ {speaker_name} ({speaker_role}) ประจำบริษัท AI Holding Company V6 (Cozy Isometric AI Visualizer).\n"
            f"ข้อมูลสดของบริษัทในขณะนี้:\n"
            f"- ราคาทองคำ (XAUUSD): ${market.get('current_price', 3900):,.2f} (D1: {market.get('d1_trend')}, H1: {market.get('trend')}, RSI: {market.get('rsi14')}, H1 ATR: ${market.get('atr14')})\n"
            f"- แนวรับ H1: ${market.get('support'):,.2f} | แนวต้าน H1: ${market.get('resistance'):,.2f} | DXY: {market.get('dxy_index')} | US10Y: {market.get('us10y_yield')}%\n"
            f"- มติ CIO ล่าสุด: {cio.get('action')} @ Entry ${cio.get('final_entry'):,.2f} | SL ${cio.get('final_sl'):,.2f} | TP1 ${cio.get('final_tp1'):,.2f} | TP2 ${cio.get('final_tp2'):,.2f} ({cio.get('recommended_lot')} Lot)\n"
            f"- กลยุทธ์วิจัยที่แม่นที่สุดในตลาดตอนนี้: {best_strat.get('strategy_name')} (Win Rate จริง {best_strat.get('live_win_rate')}%, PF {best_strat.get('live_pf')})\n"
            f"- งบโทเคนบริษัทวันนี้: ใช้ไป {tok_rep.get('total_tokens_used', 280000):,} / {tok_rep.get('daily_budget_tokens', 1000000):,} Tokens\n"
            f"ตอบคำถามของผู้ใช้เป็นภาษาไทยอย่างกระชับ ฉลาด เป็นกันเอง และอ้างอิงตัวเลขจริงข้างต้น"
        )

        def smart_local_reply(q: str) -> str:
            ql = q.lower()
            cur = market.get('current_price', 3900.0)
            act = cio.get('action', 'SELL (SHORT)')
            ent = cio.get('final_entry', cur)
            sl = cio.get('final_sl', cur + 25)
            tp1 = cio.get('final_tp1', cur - 45)
            tp2 = cio.get('final_tp2', cur - 70)

            if any(k in ql for k in ["ทอง", "เทรด", "เข้า", "buy", "sell", "ซิก", "แผน", "xau", "ราคา"]):
                return (
                    f"📊 **สรุปแผนเทรดทองคำสดจาก {speaker_name} ({model_used}):**\n"
                    f"• **ราคาทองคำปัจจุบัน:** `${cur:,.2f}` (โครงสร้าง D1: `{market.get('d1_trend')}` | H1: `{market.get('trend')}` | RSI: `{market.get('rsi14')}`)\n"
                    f"• **มติเอกฉันท์จากห้องดีเบต:** **`{act}`**\n"
                    f"• **จุดเข้า (Entry):** `${ent:,.2f}` | **Stop Loss (1.5x ATR):** `${sl:,.2f}`\n"
                    f"• **เป้าหมายกำไร:** TP1 `${tp1:,.2f}` (ขยับ SL บังทุนอัตโนมัติ) และ TP2 `${tp2:,.2f}` (ขนาดแนะนำ `{cio.get('recommended_lot')} Lot`)\n"
                    f"• **กลยุทธ์ที่ชนะตลาดตอนนี้:** `{best_strat.get('strategy_name')}` (Win Rate ทดสอบจริง `{best_strat.get('live_win_rate')}%`, Profit Factor `{best_strat.get('live_pf')}`)"
                )
            if any(k in ql for k in ["โทเคน", "token", "สกิล", "เรียน", "อัปเกรด", "overclock"]):
                disc = self.db.get_discovered_skills(3)
                disc_names = ", ".join([d["skill_name"] for d in disc])
                return (
                    f"🪙 **รายงานระบบจัดสรรโทเคน & การเรียนรู้สกิลใหม่โดย {speaker_name}:**\n"
                    f"• **การใช้โทเคนวันนี้:** `{tok_rep.get('total_tokens_used', 280000):,} / {tok_rep.get('daily_budget_tokens', 1000000):,} Tokens` (เป็น Reasoning Tokens สำหรับคิดลึกถึง `{tok_rep.get('reasoning_tokens', 140000):,} Tokens`)\n"
                    f"• **สกิลใหม่ล่าสุดที่ทีม AI เพิ่งไปค้นคว้ามาได้:** `{disc_names}`\n"
                    f"• คุณสามารถเข้าไปที่แท็บ **'🪙 2. จัดสรรงบ Token & สั่งเรียนสกิลใหม่'** เพื่อปรับโควต้าโทเคน เปิดโหมด `🔥 OVERCLOCK` หรือพิมพ์สั่งให้ AI ไปเรียนสกิลใหม่ได้ทันทีครับ!"
                )
            if any(k in ql for k in ["ธุรกิจ", "ไอเดีย", "แผนก", "บริษัท", "venture", "ต่อยอด"]):
                return (
                    f"🚀 **ไอเดียต่อยอดธุรกิจใหม่ในเครือ AI Holding จาก {speaker_name}:**\n"
                    f"1. **AI Prop-Firm Challenge Passer Bot:** ใช้โหมด Overclock ของ `Dr. Kenji (o3-mini)` คุม Drawdown ไม่เกิน 3% เพื่อสอบกองทุน Prop Firm อัตโนมัติ\n"
                    f"2. **VIP Gold & Macro Debate Signal SaaS:** ส่งบทสรุปดีเบต Bull vs Bear และจุดเข้า-ออกเข้ากลุ่มสมาชิก VIP พร้อมเชื่อม Obsidian\n"
                    f"3. **24/7 Crypto Funding & Liquidity Sweep Desk:** นำสกิล `ICT Killzone Silver Bullet` ที่เพิ่งค้นพบไปรันกับ BTCUSDT / SOLUSDT"
                )
            return (
                f"👋 สวัสดีครับ! ผม **{speaker_name}** ขับเคลื่อนด้วยสมองกลระดับท็อป `{model_used}` พร้อมดูแลคุณตลอด 24 ชม.\n"
                f"• **สถานะตลาดทองคำล่าสุด:** `${cur:,.2f}` ➔ มติคณะกรรมการคือ **`{act}`** (Entry `${ent:,.2f}`, SL `${sl:,.2f}`, TP1 `${tp1:,.2f}`)\n"
                f"• **พอร์ตอัตโนมัติ AutoBot X-1:** Equity `${port.get('equity', 1000):,.2f}` (Win Rate `{port.get('live_win_rate_pct')}%`)\n"
                f"• พิมพ์ถามผมได้ทุกเรื่องทั้ง **'ขอแผนเทรดทองตอนนี้'**, **'ดูการใช้โทเคนและสกิลใหม่'**, หรือ **'ขอไอเดียธุรกิจใหม่'** ได้เลยครับ!"
            )

        reply_text = self.router.generate(model_used, sys_prompt, user_message, fallback_fn=smart_local_reply)

        # หักโทเคนจากการสนทนาจริง
        self.db.spend_agent_tokens(ag_id_for_tok, 1200, 2800, 950, 0.0045)
        self.db.log_chat_message("คุณ (Founder)", target_agent_id, "user", user_message, "Founder Input")
        self.db.log_chat_message(speaker_name, target_agent_id, "assistant", reply_text, model_used)

        return {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "speaker_name": speaker_name,
            "speaker_role": speaker_role,
            "model_used": model_used,
            "tokens_used": 4950,
            "reply": reply_text
        }

    def generate_time_window_summary(
        self,
        date_str: str,
        time_slot: str,
        style: str,
        latest_report: dict,
        df_h1=None
    ) -> dict:
        """ดึงกราฟแท่งเทียนย้อนหลังจริงของวันที่และกะเวลาที่เลือกมาสรุป (ไม่ซ้ำเดิม!)"""
        return self.replay_engine.reconstruct_shift_report(
            date_str=date_str,
            time_slot=time_slot,
            style=style,
            df_h1=df_h1,
            latest_report=latest_report
        )
