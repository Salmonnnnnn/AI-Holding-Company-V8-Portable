"""
Multi-Timeframe Technical Analyst Agent for Gold (XAUUSD)
Analyzes D1 Major Structure + H1 Execution Setup with ATR-calibrated SL/TP and Dynamic Reasoning.
"""
from agents.base_agent import BaseAgent


class TechnicalAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Alex 'ChartMaster' Vance",
            role="Senior Multi-Timeframe Technical Analyst",
            persona="คุณคือนักวิเคราะห์เทคนิคระดับสถาบันการเงินที่เชี่ยวชาญตลาดทองคำ (XAUUSD) วิเคราะห์ผสาน Multi-Timeframe (D1 + H1), EMA 20/50/200, RSI, MACD, Bollinger Bands, Fibonacci และตั้งระยะ SL/TP ตามค่า ATR จริง"
        )
        self._last_context = {}

    def analyze(self, market_data: dict) -> dict:
        current = float(market_data.get('current_price', 2685.0))
        ema20 = float(market_data.get('ema20', current))
        ema50 = float(market_data.get('ema50', current))
        ema200 = float(market_data.get('ema200', current))
        d1_trend = market_data.get('d1_trend', 'SIDEWAY')
        h1_trend = market_data.get('trend', 'SIDEWAY')
        rsi = float(market_data.get('rsi14', 50.0))
        d1_rsi = float(market_data.get('d1_rsi', 50.0))
        atr_h1 = float(market_data.get('atr14', 10.0))
        support = float(market_data.get('support', current - 20.0))
        resistance = float(market_data.get('resistance', current + 20.0))
        macd_info = market_data.get('macd', {"macd": 0.0, "signal": 0.0, "histogram": 0.0, "state": "NEUTRAL"})
        fib = market_data.get('fib_levels', {"fib_382": current, "fib_500": current, "fib_618": current})

        # คำนวณ Technical Score (-100 ถึง +100)
        score = 0
        if current > ema20:
            score += 20
        else:
            score -= 20

        if ema20 > ema50:
            score += 20
        else:
            score -= 20

        if d1_trend == "BULLISH":
            score += 25
        elif d1_trend == "BEARISH":
            score -= 25

        if macd_info.get("state") == "BULLISH":
            score += 15
        else:
            score -= 15

        if rsi < 32:
            score += 25  # Oversold bounce potential
        elif rsi > 68:
            score -= 25  # Overbought pullback potential
        elif 50 <= rsi <= 65:
            score += 10
        elif 35 <= rsi < 50:
            score -= 10

        score = max(-100, min(100, score))

        # ปรับกรอบ ATR สำหรับการเทรด Intraday/Swing ไม่ให้แคบหรือกว้างผิดปกติ
        effective_atr = max(min(atr_h1, current * 0.012), 4.0)
        sl_dist = round(effective_atr * 1.5, 2)
        tp1_dist = round(effective_atr * 2.7, 2)  # R:R = 1:1.8

        if score >= 20:
            bias = "BUY (Bullish Setup)"
            # เข้าที่ราคาปัจจุบันหรือย่อตัวเล็กน้อยใกล้ Fib/EMA
            suggested_entry = round(current, 2)
            suggested_sl = round(suggested_entry - sl_dist, 2)
            suggested_tp = round(suggested_entry + tp1_dist, 2)
        elif score <= -20:
            bias = "SELL (Bearish Setup)"
            suggested_entry = round(current, 2)
            suggested_sl = round(suggested_entry + sl_dist, 2)
            suggested_tp = round(suggested_entry - tp1_dist, 2)
        else:
            # Sideway / Range-bound: เสนอแผนดักเข้าตามกรอบพร้อมระยะ ATR มาตรฐาน
            if current <= fib.get('fib_500', current):
                bias = "WAIT / BUY ON DIP (Range Support)"
                suggested_entry = round(max(support + (effective_atr * 0.3), current - (effective_atr * 0.4)), 2)
                suggested_sl = round(suggested_entry - sl_dist, 2)
                suggested_tp = round(suggested_entry + tp1_dist, 2)
            else:
                bias = "WAIT / SELL ON RALLY (Range Resistance)"
                suggested_entry = round(min(resistance - (effective_atr * 0.3), current + (effective_atr * 0.4)), 2)
                suggested_sl = round(suggested_entry + sl_dist, 2)
                suggested_tp = round(suggested_entry - tp1_dist, 2)

        self._last_context = {
            "current": current,
            "ema20": ema20,
            "ema50": ema50,
            "ema200": ema200,
            "d1_trend": d1_trend,
            "h1_trend": h1_trend,
            "rsi": rsi,
            "d1_rsi": d1_rsi,
            "atr_h1": atr_h1,
            "effective_atr": effective_atr,
            "support": support,
            "resistance": resistance,
            "macd_info": macd_info,
            "fib": fib,
            "score": score,
            "bias": bias,
            "suggested_entry": suggested_entry,
            "suggested_sl": suggested_sl,
            "suggested_tp": suggested_tp
        }

        prompt = f"""
วิเคราะห์ราคาทองคำแบบ Multi-Timeframe (D1 + H1) จากข้อมูลจริงล่าสุด:
- ราคาปัจจุบัน: ${current:,.2f} (เปลี่ยนแปลง 24 ชม.: {market_data.get('change_pct')}%)
- โครงสร้างภาพใหญ่ (D1 Trend): {d1_trend} (D1 EMA20: ${market_data.get('d1_ema20')}, D1 RSI: {d1_rsi})
- โครงสร้างรายชั่วโมง (H1 Trend): {h1_trend} (H1 EMA20: ${ema20:,.2f}, EMA50: ${ema50:,.2f}, EMA200: ${ema200:,.2f})
- โมเมนตัม H1: RSI(14) = {rsi} | MACD = {macd_info.get('macd')} (Signal: {macd_info.get('signal')}, State: {macd_info.get('state')})
- กรอบแนวรับ-แนวต้าน H1: แนวรับ ${support:,.2f} | แนวต้าน ${resistance:,.2f}
- Fibonacci Retracement: 38.2% (${fib.get('fib_382')}), 50.0% (${fib.get('fib_500')}), 61.8% (${fib.get('fib_618')})
- ค่าความผันผวน H1 ATR(14): ${atr_h1:,.2f}
- คะแนนเชิงปริมาณ (Technical Score): {score}/100 -> แผน: {bias}
- จุดเข้า (Entry): ${suggested_entry:,.2f} | SL: ${suggested_sl:,.2f} | TP1: ${suggested_tp:,.2f}

กรุณาสรุปการวิเคราะห์ทางเทคนิคอย่างกระชับ แม่นยำ และตรงตามตัวเลขจริงทุกประการ
"""
        response_text = self.call_llm(prompt)

        return {
            "agent": self.name,
            "role": self.role,
            "bias": bias,
            "score": score,
            "confidence": min(95, max(50, abs(score) + 35)),
            "suggested_entry": suggested_entry,
            "suggested_sl": suggested_sl,
            "suggested_tp": suggested_tp,
            "atr_used": round(effective_atr, 2),
            "commentary": response_text
        }

    def _fallback_reasoning(self, prompt: str) -> str:
        c = self._last_context
        cur = c.get("current", 2685.0)
        ema20 = c.get("ema20", cur)
        ema50 = c.get("ema50", cur)
        rsi = c.get("rsi", 50.0)
        macd = c.get("macd_info", {})
        fib = c.get("fib", {})
        sup = c.get("support", cur - 20)
        res = c.get("resistance", cur + 20)
        score = c.get("score", 0)

        ema_pos_str = (
            f"เคลื่อนไหวอยู่เหนือเส้นค่าเฉลี่ย H1 EMA20 (${ema20:,.2f}) และ EMA50 (${ema50:,.2f}) สะท้อนแรงซื้อคุมจังหวะระยะสั้น"
            if cur > ema20 and cur > ema50 else
            f"เคลื่อนไหวอยู่ต่ำกว่าเส้นค่าเฉลี่ย H1 EMA20 (${ema20:,.2f}) สะท้อนแรงกดดันฝั่งขายในระยะสั้น"
            if cur < ema20 else
            f"แกว่งตัวทดสอบระหว่างเส้น H1 EMA20 (${ema20:,.2f}) และ EMA50 (${ema50:,.2f}) ในสภาวะพักฐานเลือกทาง"
        )

        rsi_str = (
            f"เข้าใกล้โซน Oversold ({rsi}) มีโอกาสเกิด Technical Rebound"
            if rsi < 35 else
            f"เข้าใกล้โซน Overbought ({rsi}) เสี่ยงต่อการย่อตัวพักฐาน"
            if rsi > 68 else
            f"อยู่ที่ระดับ {rsi} ร่วมกับสัญญาณ MACD ในโหมด {macd.get('state', 'NEUTRAL')} (Histogram: {macd.get('histogram', 0)})"
        )

        return (
            f"1. โครงสร้าง Multi-Timeframe: ภาพใหญ่ D1 อยู่ในโหมด {c.get('d1_trend')} ขณะที่ราคาปัจจุบัน (${cur:,.2f}) {ema_pos_str}\n"
            f"2. โมเมนตัมและโซนสำคัญ: ดัชนี RSI(14) {rsi_str} โดยมีแนวรับสำคัญที่ ${sup:,.2f} (Fib 61.8%: ${fib.get('fib_618')}) และแนวต้านที่ ${res:,.2f} (Fib 38.2%: ${fib.get('fib_382')})\n"
            f"3. แผนเข้าเทรดตามค่า ATR: คะแนนเทคนิครวมอยู่ที่ {score:+d}/100 แนะนำกลยุทธ์ '{c.get('bias')}' ที่จุดเข้า ${c.get('suggested_entry'):,.2f} "
            f"วาง Stop Loss ตามระยะ 1.5x ATR ที่ ${c.get('suggested_sl'):,.2f} และเป้าหมาย TP1 ที่ ${c.get('suggested_tp'):,.2f} (R:R 1:1.8)"
        )
