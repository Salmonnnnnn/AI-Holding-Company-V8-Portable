"""
Telegram Notifier for AI Trading Committee
"""
import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    def is_configured(self) -> bool:
        return bool(self.bot_token and self.chat_id)

    def send_summary(self, session_report: dict) -> bool:
        """ส่งรายงานมติ CIO เข้า Telegram"""
        if not self.is_configured():
            logger.info("Telegram Bot not configured. Skipping alert.")
            return False

        verdict = session_report["cio_verdict"]
        market = session_report["market_snapshot"]
        risk = session_report["risk_assessment"]

        message = (
            f"🏛 *[AI TRADING FIRM - GOLD XAUUSD]*\n"
            f"📅 วันที่: `{session_report['session_time']}`\n\n"
            f"🎯 *มติการประชุม (CIO Verdict):* `{verdict['action']}`\n"
            f"💰 ราคาทองปัจจุบัน: `${market['current_price']}`\n"
            f"------------------------------------\n"
            f"🔹 *จุดเข้า (Entry):* `${verdict['final_entry']}`\n"
            f"🛑 *Stop Loss (SL):* `${verdict['final_sl']}`\n"
            f"🎯 *Take Profit 1:* `${verdict['final_tp1']}`\n"
            f"🎯 *Take Profit 2:* `${verdict['final_tp2']}`\n"
            f"⚖️ *Risk/Reward:* `{risk['rr_ratio']}`\n"
            f"📦 *แนะนำ Lot Size:* `{verdict['recommended_lot']} Lot`\n"
            f"💵 *ความเสี่ยงเงินจริง:* `${verdict['risk_dollar']}`\n"
            f"------------------------------------\n"
            f"📝 *บทสรุปผู้บริหาร:*\n{verdict['executive_summary']}\n"
        )

        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            resp = requests.post(url, json=payload, timeout=10)
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
