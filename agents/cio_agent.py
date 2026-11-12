"""
Chief Investment Officer (CIO) Agent - Weighted Consensus & Final Executive Decision
"""
from agents.base_agent import BaseAgent


class CIOAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Arthur Pendelton",
            role="Chief Investment Officer (CIO) & Chairman of the Trading Committee",
            persona="คุณคือประธานคณะกรรมการการลงทุนและผู้นำสูงสุดของกองทุน คุณรับฟังการถกเถียงของทุกฝ่าย รวมคะแนนโหวตเชิงปริมาณ และฟันธงแผนการเทรดทั้งแผนหลัก (Primary Plan) และแผนสำรอง (Alternative Plan) อย่างเด็ดขาด"
        )
        self._last_context = {}

    def formulate_verdict(
        self,
        ta_result: dict,
        macro_result: dict,
        debate_result: dict,
        risk_result: dict,
        market_data: dict
    ) -> dict:
        cur = float(market_data.get('current_price', 2685.0))
        ta_score = int(ta_result.get('score', 0))
        macro_score = int(macro_result.get('score', 0))
        bull_power = int(debate_result.get('bull_power', 50))
        bear_power = int(debate_result.get('bear_power', 50))
        bt = risk_result.get('backtest', {})

        # คำนวณ Weighted Consensus (-100 ถึง +100)
        weighted_score = round((ta_score * 0.55) + (macro_score * 0.25) + ((bull_power - bear_power) * 0.20), 1)
        conviction_pct = min(95, max(50, int(50 + abs(weighted_score) * 0.45)))

        entry = round(float(ta_result.get('suggested_entry', cur)), 2)
        sl = round(float(ta_result.get('suggested_sl', entry - 15.0)), 2)
        tp1 = round(float(ta_result.get('suggested_tp', entry + 27.0)), 2)
        sl_dist = abs(entry - sl)
        tp2 = round(entry + (sl_dist * 2.8), 2) if tp1 > entry else round(entry - (sl_dist * 2.8), 2)

        if not risk_result.get('approved', True):
            action = "WAIT / NO TRADE (Risk Parameters Unfavorable)"
        elif weighted_score >= 18:
            action = "BUY (LONG)"
        elif weighted_score <= -18:
            action = "SELL (SHORT)"
        else:
            # กรณีคะแนนก้ำกึ่ง ให้วางแผนดัก Pending Limit ตามทิศทางที่ได้เปรียบกว่า
            direction_hint = "BUY LIMIT ON DIP" if tp1 > entry else "SELL LIMIT ON RALLY"
            action = f"WAIT & PENDING ORDER ({direction_hint})"

        alt_plan = (
            f"หากราคาทะลุจุด Stop Loss ที่ ${sl:,.2f} พร้อมแท่งเทียน H1 ปิดเต็มแท่ง แสดงว่าโครงสร้างเดิมถูกทำลาย (Invalidation) "
            f"ให้หยุดรอและพิจารณาหาจังหวะเข้าตามน้ำในทิศทางตรงข้ามเมื่อย่อตัวทดสอบ ${sl:,.2f}"
        )

        self._last_context = {
            "cur": cur,
            "action": action,
            "weighted_score": weighted_score,
            "conviction_pct": conviction_pct,
            "bull_power": bull_power,
            "bear_power": bear_power,
            "debate_winner": debate_result.get('debate_winner', ''),
            "entry": entry,
            "sl": sl,
            "tp1": tp1,
            "tp2": tp2,
            "lot": risk_result.get('recommended_lot', 0.01),
            "risk_dollar": risk_result.get('actual_dollar_risk', 15.0),
            "rr_ratio": risk_result.get('rr_ratio', '1:1.8'),
            "bt": bt,
            "alt_plan": alt_plan
        }

        prompt = f"""
คุณในฐานะ Chief Investment Officer (CIO) ได้รับฟังการประชุมคณะกรรมการ AI Investment Firm ครบทุกฝ่ายแล้ว:
- ราคาทองคำปัจจุบัน: ${cur:,.2f} (D1 Trend: {market_data.get('d1_trend')}, H1 Trend: {market_data.get('trend')})
- คะแนนเทคนิค (TA Score): {ta_score:+d}/100 | คะแนนมหภาค (Macro Score): {macro_score:+d}/100
- ผลการดีเบต Bull vs Bear: Bull {bull_power}% vs Bear {bear_power}% ({debate_result.get('debate_winner')})
- ผล Backtest ย้อนหลัง: Win Rate {bt.get('win_rate_pct')}%, Profit Factor {bt.get('profit_factor')} ({bt.get('strategy_grade')})
- มติเอกฉันท์ถ่วงน้ำหนัก (Weighted Score): {weighted_score:+.1f} (ความเชื่อมั่น {conviction_pct}%) -> คำสั่ง: {action}
- แผนเทรดหลัก: Entry ${entry:,.2f} | SL ${sl:,.2f} | TP1 ${tp1:,.2f} | TP2 ${tp2:,.2f} | ขนาด {risk_result.get('recommended_lot')} Lot (R:R {risk_result.get('rr_ratio')})

สรุปมติผู้บริหาร (Executive Summary) อย่างชัดเจน เด็ดขาด และระบุทั้งแผนหลักและแผนสำรอง
"""
        verdict_commentary = self.call_llm(prompt)

        return {
            "cio_name": self.name,
            "action": action,
            "weighted_score": weighted_score,
            "conviction_pct": conviction_pct,
            "bull_power": bull_power,
            "bear_power": bear_power,
            "final_entry": entry,
            "final_sl": sl,
            "final_tp1": tp1,
            "final_tp2": tp2,
            "recommended_lot": risk_result.get('recommended_lot', 0.01),
            "risk_dollar": risk_result.get('actual_dollar_risk', 15.0),
            "rr_ratio": risk_result.get('rr_ratio', '1:1.8'),
            "alternative_plan": alt_plan,
            "executive_summary": verdict_commentary
        }

    def _fallback_reasoning(self, prompt: str) -> str:
        c = self._last_context
        bt = c.get("bt", {})
        return (
            f"1. มติคณะกรรมการ (Weighted Score {c.get('weighted_score'):+.1f} | ความเชื่อมั่น {c.get('conviction_pct')}%): "
            f"จากการดีเบตระหว่างฝั่งกระทิง ({c.get('bull_power')}%) และฝั่งหมี ({c.get('bear_power')}%) มีมติชี้ขาดให้ดำเนินการ '{c.get('action')}'\n"
            f"2. แผนปฏิบัติการหลัก (Primary Execution): เข้าออเดอร์ที่ ${c.get('entry'):,.2f} ตั้ง Stop Loss ที่ ${c.get('sl'):,.2f} "
            f"โดยแบ่งทำกำไร TP1 ที่ ${c.get('tp1'):,.2f} ({c.get('rr_ratio')}) และถือลุ้น TP2 ที่ ${c.get('tp2'):,.2f} ด้วยขนาด {c.get('lot')} Lot "
            f"(ผ่านเกณฑ์ Backtest Win Rate {bt.get('win_rate_pct')}%, Profit Factor {bt.get('profit_factor')})\n"
            f"3. แผนสำรองและจุดยกเลิกแผน (Invalidation Plan): {c.get('alt_plan')}"
        )
