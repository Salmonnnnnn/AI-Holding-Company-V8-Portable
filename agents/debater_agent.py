"""
Dual-Debate Engine: Bull Advocate vs. Bear & Red Team Advocate
Simulates an intense structured debate comparing the Bullish Case, Bearish Case, and Liquidity Trap Risks.
"""
from agents.base_agent import BaseAgent


class DebaterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Viktor Kane (Bear/Red Team) vs. Sarah Jenkins (Bull Advocate)",
            role="Head of Bull vs. Bear Debate & Red-Team Critique",
            persona="คุณเป็นผู้ดำเนินการถกเถียง (Debate Moderator) ระหว่าง ฝ่ายกระทิง (Bull Advocate) และ ฝ่ายหมี/นักจับผิด (Bear & Red Team) โดยทั้งสองฝ่ายต้องปะทะกันด้วยตัวเลขจริง เพื่อหาว่าฝั่งไหนมีเหตุผลเหนือกว่าและจุดไหนคือกับดักสภาพคล่อง (Stop Hunt)"
        )
        self._last_context = {}

    def debate(self, ta_opinion: dict, macro_opinion: dict, market_data: dict) -> dict:
        cur = float(market_data.get('current_price', 2685.0))
        ema20 = float(market_data.get('ema20', cur))
        ema50 = float(market_data.get('ema50', cur))
        rsi = float(market_data.get('rsi14', 50.0))
        atr = float(market_data.get('atr14', 10.0))
        sup = float(market_data.get('support', cur - 20.0))
        res = float(market_data.get('resistance', cur + 20.0))
        dxy = float(market_data.get('dxy_index', 104.0))
        y10 = float(market_data.get('us10y_yield', 4.35))
        fib = market_data.get('fib_levels', {"fib_382": cur, "fib_500": cur, "fib_618": cur})

        ta_score = int(ta_opinion.get('score', 0))
        macro_score = int(macro_opinion.get('score', 0))

        # คำนวณพลังโต้แย้งของฝั่งกระทิง (Bull Power: 0-100) และฝั่งหมี (Bear Power: 0-100)
        raw_net = (ta_score * 0.65) + (macro_score * 0.35)
        bull_power = int(min(92, max(15, round(50 + (raw_net * 0.45)))))
        bear_power = 100 - bull_power

        if abs(bull_power - bear_power) <= 10:
            debate_winner = "CONTESTED / BALANCED (สูสีกัน แนะนำรอราคาเลือกทางหรือเข้าที่กรอบ)"
        elif bull_power > bear_power:
            debate_winner = f"BULL ADVOCATE WINS ({bull_power}% vs {bear_power}% - ฝั่งซื้อได้เปรียบ)"
        else:
            debate_winner = f"BEAR / RED TEAM WINS ({bear_power}% vs {bull_power}% - ฝั่งขาย/ระวังความเสี่ยงได้เปรียบ)"

        bull_case = (
            f"🐂 [ฝ่ายกระทิง - Sarah Jenkins (พลังโหวต {bull_power}%)]: "
            f"ทองคำมีโซนแนวรับแข็งแกร่งที่ ${sup:,.2f} และระดับ Fibonacci 61.8% (${fib.get('fib_618')}) "
            f"{'อีกทั้งราคาปัจจุบัน ($' + f'{cur:,.2f}' + ') ยืนเหนือ EMA20 ($' + f'{ema20:,.2f}' + ') อย่างมั่นคง ' if cur >= ema20 else 'แม้ราคาย่อตัวลงมาต่ำกว่า EMA20 ($' + f'{ema20:,.2f}' + ') แต่ RSI ที่ ' + f'{rsi}' + ' เปิดรูมให้เกิดแรงซื้อกลับ (Mean Reversion) '}"
            f"ประกอบกับดอลลาร์ DXY ที่ {dxy} ไม่ได้พุ่งทะลุกรอบบน จึงเป็นจังหวะสะสม Buy เพื่อลุ้นทดสอบ ${res:,.2f}"
        )

        trap_zone_low = round(sup - (min(atr, 25.0) * 0.35), 2)
        trap_zone_high = round(res + (min(atr, 25.0) * 0.35), 2)

        bear_case = (
            f"🐻 [ฝ่ายหมี & Red Team - Viktor Kane (พลังโหวต {bear_power}%)]: "
            f"อย่ามองโลกในแง่ดีเกินไป! {'ราคาปัจจุบัน ($' + f'{cur:,.2f}' + ') ยังอยู่ต่ำกว่าเส้น H1 EMA20 ($' + f'{ema20:,.2f}' + ') ชัดเจน การรีบสวน Buy ตอนนี้เสี่ยงรับมีด! ' if cur < ema20 else 'แม้ราคาจะอยู่เหนือ EMA20 ($' + f'{ema20:,.2f}' + ') แต่ใกล้แนวต้าน $' + f'{res:,.2f}' + ' เสี่ยงเกิด Bull Trap! '}"
            f"นอกจากนี้ US 10Y Yield ที่ {y10}% ยังกดดันทองคำ และจ้าวตลาด (Smart Money) มักทุบกวาด Stop Loss ใต้แนวรับ ${sup:,.2f} ลงไปถึงโซน ${trap_zone_low:,.2f} "
            f"หรือลากไส้ทะลุ ${res:,.2f} ไปที่ ${trap_zone_high:,.2f} ก่อนกลับทิศ ดังนั้นห้ามไล่ราคาเด็ดขาด!"
        )

        self._last_context = {
            "bull_power": bull_power,
            "bear_power": bear_power,
            "debate_winner": debate_winner,
            "bull_case": bull_case,
            "bear_case": bear_case,
            "trap_zone_low": trap_zone_low,
            "trap_zone_high": trap_zone_high,
            "ta_entry": ta_opinion.get('suggested_entry'),
            "ta_sl": ta_opinion.get('suggested_sl')
        }

        prompt = f"""
จำลองการดีเบตปะทะกันระหว่าง ฝ่ายกระทิง (Bull Advocate) และ ฝ่ายหมี/นักจับผิด (Bear & Red Team) สำหรับทองคำ (XAUUSD):
- ราคาปัจจุบัน: ${cur:,.2f} | EMA20: ${ema20:,.2f} | EMA50: ${ema50:,.2f} | RSI: {rsi}
- แนวรับ: ${sup:,.2f} | แนวต้าน: ${res:,.2f} | DXY: {dxy} | US10Y Yield: {y10}%
- แผนจากฝ่ายเทคนิค: {ta_opinion.get('bias')} (Entry: ${ta_opinion.get('suggested_entry')}, SL: ${ta_opinion.get('suggested_sl')}, TP: ${ta_opinion.get('suggested_tp')})
- คะแนนโหวตจากการคำนวณ: Bull {bull_power}% vs Bear {bear_power}% -> ผลตัดสินดีเบต: {debate_winner}

กรุณาเขียนบทดีเบตที่แสดง:
1. ข้อโต้แย้งของฝ่ายกระทิง (Bull Case)
2. ข้อโต้แย้งและจุดจับผิด Stop Hunt ของฝ่ายหมี (Bear & Red Team Case)
3. บทสรุปผลการดีเบตว่าฝ่ายไหนมีน้ำหนักกว่ากัน
"""
        response_text = self.call_llm(prompt)

        return {
            "agent": self.name,
            "role": self.role,
            "bull_power": bull_power,
            "bear_power": bear_power,
            "debate_winner": debate_winner,
            "bull_case": bull_case,
            "bear_case": bear_case,
            "trap_zone_low": trap_zone_low,
            "trap_zone_high": trap_zone_high,
            "debate_critique": response_text
        }

    def _fallback_reasoning(self, prompt: str) -> str:
        c = self._last_context
        return (
            f"{c.get('bull_case')}\n\n"
            f"{c.get('bear_case')}\n\n"
            f"⚖️ [สรุปผลศึกดีเบต]: {c.get('debate_winner')} — "
            f"ระวังโซนกวาดสภาพคล่อง (Stop Hunt Zone) บริเวณ ${c.get('trap_zone_low'):,.2f} และ ${c.get('trap_zone_high'):,.2f} "
            f"โดยจุด Stop Loss ที่ ${c.get('ta_sl'):,.2f} ได้เผื่อระยะ ATR ป้องกันการสวอร์มไส้เทียนไว้แล้ว"
        )
