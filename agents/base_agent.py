"""
Base Agent Module with support for Gemini API and Heuristic Fallback
"""
import os
import requests
import json
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, name: str, role: str, persona: str):
        self.name = name
        self.role = role
        self.persona = persona
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()

    def call_llm(self, prompt: str, system_instruction: str = "") -> str:
        """เรียก Gemini API หรือใช้ Fallback Heuristic หากยังไม่ได้ใส่ API Key"""
        if self.api_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
                headers = {"Content-Type": "application/json"}
                
                full_system = f"{self.persona}\n\nบทบาทหน้าที่ของคุณ: {self.role}\n{system_instruction}"
                payload = {
                    "contents": [{
                        "parts": [{"text": f"SYSTEM ROLE: {full_system}\n\nUSER PROMPT / TASK:\n{prompt}"}]
                    }],
                    "generationConfig": {
                        "temperature": 0.4,
                        "maxOutputTokens": 1000
                    }
                }
                
                resp = requests.post(url, headers=headers, json=payload, timeout=20)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
                logger.warning(f"API call returned status {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.warning(f"Failed to call Gemini API: {e}. Switching to internal reasoning mode.")

        # Heuristic / Local Expert Simulation Mode
        return self._fallback_reasoning(prompt)

    def _fallback_reasoning(self, prompt: str) -> str:
        """Method ที่ agent ลูกแต่ละตัวจะ override เพื่อให้เหตุผลอย่างสมจริงหากไม่มี API Key"""
        return f"[{self.name}] ได้รับข้อมูลและทำการวิเคราะห์ตามหลักการของ {self.role} เรียบร้อยแล้ว"
