"""
Macro & Intermarket Strategist Agent for Gold (XAUUSD)
Analyzes US Dollar Index (DXY), US 10Y Treasury Yield, and Live News Headlines with Dynamic Reasoning.
"""
from agents.base_agent import BaseAgent


class MacroAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Dr. Marcus Sterling",
            role="Chief Global Macroeconomist",
            persona="คุณคือนักเศรษฐศาสตร์มหภาคระดับโลกที่เชี่ยวชาญนโยบายธนาคารกลางสหรัฐฯ (Fed), ค่าเงินดอลลาร์ (DXY), พันธบัตรสหรัฐฯ (US10Y) และปัจจัยภูมิรัฐศาสตร์ที่ส่งผลต่อทองคำ"
        )
        self._last_context = {}

    def analyze(self, market_data: dict, news_headlines: list) -> dict:
        dxy = float(market_data.get('dxy_index', 104.0))
        dxy_chg = float(market_data.get('dxy_change_pct', 0.0))
        yield_val = float(market_data.get('us10y_yield', 4.3))
        yield_chg = float(market_data.get('us10y_change_pct', 0.0))

        # คำนวณคะแนน Macro (-100 ถึง +100)
        score = 15  # Structural floor from central bank buying & geopolitics
        if dxy < 103.5:
            score += 25
        elif dxy > 105.5:
            score -= 25

        if dxy_chg < -0.1:
            score += 15
        elif dxy_chg > 0.15:
            score -= 15

        if yield_val > 4.6:
            score -= 20
        elif yield_val < 4.1:
            score += 20

        if yield_chg > 0.5:
            score -= 10
        elif yield_chg < -0.5:
            score += 10

        score = max(-100, min(100, score))

        if score >= 20:
            macro_bias = "BULLISH TAILWIND (Macro Supports Gold)"
        elif score <= -20:
            macro_bias = "BEARISH HEADWIND (Strong Dollar / High Yields)"
        else:
            macro_bias = "NEUTRAL / BALANCED MACRO FORCES"

        top_headline = news_headlines[0].get("title", "Central bank gold demand remains resilient") if news_headlines else "Global markets monitor Federal Reserve policy path"

        self._last_context = {
            "dxy": dxy,
            "dxy_chg": dxy_chg,
            "yield_val": yield_val,
            "yield_chg": yield_chg,
            "score": score,
            "macro_bias": macro_bias,
            "top_headline": top_headline
        }

        news_text = "\n".join([f"- {n.get('title')}" for n in news_headlines[:4]])
        prompt = f"""
วิเคราะห์ปัจจัยพื้นฐานและเศรษฐกิจมหภาคที่มีผลต่อราคาทองคำ:
- ดัชนีดอลลาร์สหรัฐ (DXY): {dxy} ({dxy_chg:+.2f}%)
- อัตราผลตอบแทนพันธบัตรสหรัฐ 10 ปี (US 10Y Yield): {yield_val}% ({yield_chg:+.2f}%)
- คะแนนเชิงมหภาค (Macro Score): {score:+d}/100 -> มุมมอง: {macro_bias}
- ข่าวเศรษฐกิจล่าสุด:
{news_text}

กรุณาสรุปอิทธิพลของดอลลาร์ บอนด์ยีลด์ และข่าวสารที่มีต่อทองคำอย่างชัดเจน
"""
        response_text = self.call_llm(prompt)

        return {
            "agent": self.name,
            "role": self.role,
            "macro_bias": macro_bias,
            "score": score,
            "commentary": response_text
        }

    def _fallback_reasoning(self, prompt: str) -> str:
        c = self._last_context
        dxy = c.get("dxy", 104.0)
        dxy_chg = c.get("dxy_chg", 0.0)
        y_val = c.get("yield_val", 4.3)
        score = c.get("score", 0)
        headline = c.get("top_headline", "")

        dxy_desc = (
            f"อ่อนค่าลงมาอยู่ที่ {dxy} ({dxy_chg:+.2f}%) ซึ่งเป็นปัจจัยบวกหนุนราคาทองคำโดยตรง"
            if dxy < 103.5 or dxy_chg < 0 else
            f"ทรงตัวในโซนแข็งค่าที่ {dxy} ({dxy_chg:+.2f}%) สร้างแรงกดดันจำกัด Upside ของทองคำระยะสั้น"
        )
        yield_desc = (
            f"อยู่ในระดับสูงที่ {y_val}% เพิ่มต้นทุนค่าเสียโอกาสในการถือครองทองคำ"
            if y_val >= 4.4 else
            f"เคลื่อนไหวที่ระดับ {y_val}% ไม่ได้สร้างแรงกดดันรุนแรงต่อสินทรัพย์ปลอดภัย"
        )

        return (
            f"1. ค่าเงินดอลลาร์และบอนด์ยีลด์: ดัชนี DXY ปัจจุบัน{dxy_desc} ขณะที่ US 10Y Yield {yield_desc}\n"
            f"2. บริบทข่าวและกระแสเงินทุน: ประเด็นสำคัญในตลาดคือ \"{headline}\" กอปรกับแรงซื้อสะสมของธนาคารกลางยังเป็นฐานรองรับ (Structural Floor)\n"
            f"3. สรุปคะแนนมหภาค ({score:+d}/100): ประเมินสภาวะแวดล้อมเป็น '{c.get('macro_bias')}'"
        )
