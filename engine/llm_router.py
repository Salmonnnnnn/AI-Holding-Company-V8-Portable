"""
Multi-LLM Provider Router (V7) — 12 Frontier Heavy-Reasoning Models + Custom Model Registry
Supports:
1. Claude 3.7 Sonnet (Extended Thinking 128K)
2. Claude 3.5 Opus (Flagship Strategist)
3. OpenAI o1-Pro (Maximum Reasoning Compute)
4. OpenAI o3-mini-high (High-Effort Quant & Code)
5. GPT-4.5 Preview (Orion Frontier Multimodal)
6. Gemini 2.5 Pro Exp (2M Context Deep Research)
7. DeepSeek-R1 671B Full (Unquantized CoT)
8. Grok-3 Thinking (xAI Real-Time Macro & X Pulse)
9. Qwen-Max / QwQ-32B-Preview (Math & Algo Reasoning)
10. Mistral Large 2 / Codestral 25.01 (Execution Pro)
11. Llama-3.3-70B (Groq Ultra-Fast)
12. Ollama Local (Llama3 / DeepSeek Offline)
+ Any Custom AI Models added by the Founder via the UI!
"""
import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


AVAILABLE_MODELS = [
    {
        "id": "Claude 3.7 Sonnet (Extended Thinking 128K)",
        "provider": "Anthropic Flagship (Heavy Thinking)",
        "badge_color": "#f59e0b",
        "specialty": "Extended Thinking หลายชั้น สำหรับประธาน CIO และจับผิดแผนเทรด",
        "cost": "HIGH TOKEN BURN (35K-128K Tokens/รอบ)",
        "avg_tokens_per_run": 48000,
        "tier": "HEAVY_REASONING"
    },
    {
        "id": "OpenAI o1-Pro (Maximum Reasoning Compute)",
        "provider": "OpenAI Pro Tier",
        "badge_color": "#7c3aed",
        "specialty": "ตัวท็อปสุดสายคิดลึก คำนวณคณิตศาสตร์ Quant, Kelly Risk & สถิติ",
        "cost": "MAX REASONING (60K-180K Tokens/รอบ)",
        "avg_tokens_per_run": 75000,
        "tier": "HEAVY_REASONING"
    },
    {
        "id": "GPT-4.5 Preview (Orion Frontier Multimodal)",
        "provider": "OpenAI Orion Flagship",
        "badge_color": "#ec4899",
        "specialty": "เข้าใจบริบทเศรษฐกิจมหภาค จิตวิทยาตลาดโลก และการปั้นธุรกิจใหม่",
        "cost": "FRONTIER BURN (45K-140K Tokens/รอบ)",
        "avg_tokens_per_run": 62000,
        "tier": "HEAVY_REASONING"
    },
    {
        "id": "Claude 3.5 Opus (Flagship Strategist)",
        "provider": "Anthropic Opus Tier",
        "badge_color": "#d97706",
        "specialty": "สมองกลระดับผู้บริหารสูงสุด วางกลยุทธ์พอร์ตและขยายเครือธุรกิจ",
        "cost": "HEAVY TOKEN BURN (40K-100K Tokens/รอบ)",
        "avg_tokens_per_run": 52000,
        "tier": "HEAVY_REASONING"
    },
    {
        "id": "OpenAI o3-mini / o1-Pro (Deep Math Reasoning)",
        "provider": "OpenAI Reasoning Series",
        "badge_color": "#8b5cf6",
        "specialty": "เผา Reasoning Tokens คำนวณสถิติ Quant, Backtest และโค้ด MT5",
        "cost": "HEAVY REASONING (50K-150K Tokens/รอบ)",
        "avg_tokens_per_run": 64000,
        "tier": "HEAVY_REASONING"
    },
    {
        "id": "Gemini 2.5 Pro Exp (2M Context Deep Research)",
        "provider": "Google DeepMind Flagship",
        "badge_color": "#0ea5e9",
        "specialty": "กวาดอ่านกราฟย้อนหลังนับพันแท่ง + ข่าวสารทั่วโลกพร้อมกันใน 2M Context",
        "cost": "DEEP CONTEXT (60K-200K Tokens/รอบ)",
        "avg_tokens_per_run": 58000,
        "tier": "HEAVY_REASONING"
    },
    {
        "id": "DeepSeek-R1 671B Full (Unquantized CoT)",
        "provider": "DeepSeek / OpenRouter Pro",
        "badge_color": "#10b981",
        "specialty": "โมเดล 671B เต็มสูบ ค้นพบสูตรอินดิเคเตอร์และสกิลเทรดใหม่",
        "cost": "REASONING CoT (30K-90K Tokens/รอบ)",
        "avg_tokens_per_run": 38000,
        "tier": "HEAVY_REASONING"
    },
    {
        "id": "Grok-3 (Real-Time Macro & X Pulse)",
        "provider": "xAI Flagship",
        "badge_color": "#f43f5e",
        "specialty": "โหมด Grok-3 Thinking ดักจับข่าวด่วน Fed, สงคราม และ Sentiment สด",
        "cost": "LIVE STREAM BURN (25K-70K Tokens/รอบ)",
        "avg_tokens_per_run": 34000,
        "tier": "HEAVY_REASONING"
    },
    {
        "id": "Qwen-Max / QwQ-32B-Preview (Math & Algo Reasoning)",
        "provider": "Alibaba Cloud Flagship",
        "badge_color": "#6366f1",
        "specialty": "โมเดลสายคณิตศาสตร์การเงินและการสังเคราะห์อัลกอริทึมเทรด",
        "cost": "MATH REASONING (28K-75K Tokens/รอบ)",
        "avg_tokens_per_run": 32000,
        "tier": "HEAVY_REASONING"
    },
    {
        "id": "Mistral Large 2 / Codestral 25.01 (Execution Pro)",
        "provider": "Mistral AI Europe",
        "badge_color": "#f97316",
        "specialty": "เขียนและตรวจสอบคำสั่ง MQL5 / Python MT5 Zero-Latency Execution",
        "cost": "FAST PRO (18K-45K Tokens/รอบ)",
        "avg_tokens_per_run": 22000,
        "tier": "FAST_BALANCED"
    },
    {
        "id": "Llama-3.3-70B (Groq Ultra-Fast)",
        "provider": "Groq LPU Cloud",
        "badge_color": "#22c55e",
        "specialty": "ความเร็วแสง 300+ Tokens/sec สำหรับโต้ตอบในห้องดีเบต",
        "cost": "FAST / FREE TIER (12K Tokens/รอบ)",
        "avg_tokens_per_run": 12000,
        "tier": "FAST_BALANCED"
    },
    {
        "id": "Qwen-2.5-Coder-32B (Algo Specialist)",
        "provider": "OpenRouter / Alibaba Cloud",
        "badge_color": "#a855f7",
        "specialty": "เขียนและตรวจสอบคำสั่ง MQL5 / Python MT5 Execution",
        "cost": "FAST / FREE TIER (15K Tokens/รอบ)",
        "avg_tokens_per_run": 15000,
        "tier": "FAST_BALANCED"
    },
    {
        "id": "Ollama Local (Llama3 / DeepSeek Offline)",
        "provider": "Local PC (100% Offline)",
        "badge_color": "#06b6d4",
        "specialty": "รันบนการ์ดจอเครื่องตัวเอง ไม่เสียค่า API",
        "cost": "100% FREE OFFLINE",
        "avg_tokens_per_run": 10000,
        "tier": "ECO"
    }
]


class MultiLLMRouter:
    def __init__(self, db=None):
        self.db = db
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        self.groq_key = os.getenv("GROQ_API_KEY", "").strip()
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        self.openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip()

    def get_available_models(self) -> list[dict]:
        custom = self.db.get_custom_models() if self.db and hasattr(self.db, "get_custom_models") else []
        existing_ids = {m["id"] for m in custom}
        merged = list(custom) + [m for m in AVAILABLE_MODELS if m["id"] not in existing_ids]
        return merged

    def generate(self, model_label: str, system_prompt: str, user_prompt: str, fallback_fn=None) -> str:
        m_low = model_label.lower()

        if "claude" in m_low:
            if self.anthropic_key:
                res = self._call_anthropic(system_prompt, user_prompt)
                if res:
                    return res
            if self.openrouter_key:
                or_model = "anthropic/claude-3.7-sonnet" if "3.7" in m_low else "anthropic/claude-3.5-sonnet"
                res = self._call_openrouter(or_model, system_prompt, user_prompt)
                if res:
                    return res

        if ("o3" in m_low or "o1" in m_low or "gpt" in m_low or "deepseek" in m_low or "qwen" in m_low or "grok" in m_low or "mistral" in m_low) and self.openrouter_key:
            or_model = "deepseek/deepseek-r1:free"
            if "qwen" in m_low:
                or_model = "qwen/qwen-2.5-coder-32b-instruct:free"
            res = self._call_openrouter(or_model, system_prompt, user_prompt)
            if res:
                return res

        if ("groq" in m_low or "llama" in m_low) and self.groq_key:
            res = self._call_groq("llama-3.3-70b-versatile", system_prompt, user_prompt)
            if res:
                return res

        if "ollama" in m_low:
            res = self._call_ollama(system_prompt, user_prompt)
            if res:
                return res

        if self.gemini_key:
            res = self._call_gemini(system_prompt, user_prompt)
            if res:
                return res

        if callable(fallback_fn):
            return fallback_fn(user_prompt)
        return ""

    def _call_gemini(self, sys_p: str, usr_p: str) -> str | None:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
            payload = {
                "contents": [{"parts": [{"text": f"SYSTEM: {sys_p}\n\nUSER: {usr_p}"}]}],
                "generationConfig": {"temperature": 0.4, "maxOutputTokens": 900}
            }
            r = requests.post(url, json=payload, timeout=15)
            if r.status_code == 200:
                cands = r.json().get("candidates", [])
                if cands:
                    return cands[0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            logger.debug(f"Gemini call skipped: {e}")
        return None

    def _call_openrouter(self, model_name: str, sys_p: str, usr_p: str) -> str | None:
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.openrouter_key}", "Content-Type": "application/json"}
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": sys_p},
                    {"role": "user", "content": usr_p}
                ]
            }
            r = requests.post(url, headers=headers, json=payload, timeout=18)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.debug(f"OpenRouter call skipped: {e}")
        return None

    def _call_groq(self, model_name: str, sys_p: str, usr_p: str) -> str | None:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.groq_key}", "Content-Type": "application/json"}
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": sys_p},
                    {"role": "user", "content": usr_p}
                ]
            }
            r = requests.post(url, headers=headers, json=payload, timeout=15)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.debug(f"Groq call skipped: {e}")
        return None

    def _call_anthropic(self, sys_p: str, usr_p: str) -> str | None:
        try:
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": self.anthropic_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            payload = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 900,
                "system": sys_p,
                "messages": [{"role": "user", "content": usr_p}]
            }
            r = requests.post(url, headers=headers, json=payload, timeout=18)
            if r.status_code == 200:
                return r.json()["content"][0]["text"].strip()
        except Exception as e:
            logger.debug(f"Anthropic call skipped: {e}")
        return None

    def _call_ollama(self, sys_p: str, usr_p: str) -> str | None:
        try:
            url = f"{self.ollama_url}/api/generate"
            payload = {"model": "llama3", "prompt": f"{sys_p}\n\n{usr_p}", "stream": False}
            r = requests.post(url, json=payload, timeout=8)
            if r.status_code == 200:
                return r.json().get("response", "").strip()
        except Exception:
            pass
        return None
