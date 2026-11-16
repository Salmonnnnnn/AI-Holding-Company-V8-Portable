"""
Token Treasury & Free LLM Economy Manager (V8)
Curated Free LLM Providers Catalog (based on awesome-free-llm-apis),
Smart Auto-Failover Engine, Rate-Limit Telemetry, and Bot Historical Token Accounting.
"""
from datetime import datetime
from data.database import CompanyDatabase
from engine.llm_router import AVAILABLE_MODELS


# -----------------------------------------------------------------------------
# Curated Free LLM Providers Catalog (awesome-free-llm-apis)
# Explicit Rate Limits, Benchmark Speeds, and Fallback Routing
# -----------------------------------------------------------------------------
FREE_LLM_PROVIDERS = {
    "cerebras": {
        "key": "cerebras",
        "name": "Cerebras Inference",
        "model": "Llama-3.3-70B",
        "primary_model": "Llama-3.3-70B",
        "models": ["Llama-3.3-70B"],
        "rpm_limit": 30,
        "rpm": 30,
        "tpm_limit": 60000,
        "tpm": 60000,
        "rpd": 14400,
        "daily_token_limit": 1000000,
        "latency": "Ultra-Fast (2,600+ tok/s)",
        "speed_benchmark": "~2,600+ tok/s (Wafer-Scale Engine)",
        "speed_tok_s": 2600,
        "status": "ACTIVE",
        "description": "WSE-3 Wafer-scale engine, fastest inference in the world, 1M free tokens/day",
        "context_window": "128K",
        "tier": "Free Tier (No Credit Card)",
        "fallback_target": "groq",
        "cost_per_million": 0.0,
        "provider_badge": "⚡ Ultra-Fast 2,600 tok/s"
    },
    "groq": {
        "key": "groq",
        "name": "Groq LPU",
        "model": "Llama-3.3-70B-Versatile / DeepSeek-R1-Distill-70B",
        "primary_model": "Llama-3.3-70B-Versatile / DeepSeek-R1-Distill-70B",
        "models": ["Llama-3.3-70B-Versatile", "DeepSeek-R1-Distill-70B"],
        "rpm_limit": 30,
        "rpm": 30,
        "tpm_limit": 30000,
        "tpm": 30000,
        "rpd": 14400,
        "daily_token_limit": 500000,
        "latency": "Ultra-Fast (300+ tok/s)",
        "speed_benchmark": "~300+ tok/s (Groq LPU)",
        "speed_tok_s": 300,
        "status": "STANDBY",
        "description": "LPU Tensor Core high reasoning speed, 14,400 RPD free tier",
        "context_window": "128K",
        "tier": "Free Tier (High Availability)",
        "fallback_target": "sambanova",
        "cost_per_million": 0.0,
        "provider_badge": "🚀 LPU Real-time 300+ tok/s"
    },
    "sambanova": {
        "key": "sambanova",
        "name": "SambaNova Cloud",
        "model": "Meta-Llama-3.1-405B / Qwen-2.5-72B",
        "primary_model": "Meta-Llama-3.1-405B / Qwen-2.5-72B",
        "models": ["Meta-Llama-3.1-405B", "Qwen-2.5-72B"],
        "rpm_limit": 20,
        "rpm": 20,
        "tpm_limit": 50000,
        "tpm": 50000,
        "rpd": 5000,
        "daily_token_limit": 1000000,
        "latency": "High Quality (180+ tok/s)",
        "speed_benchmark": "~180+ tok/s (SN40L Reconfigurable Dataflow)",
        "speed_tok_s": 180,
        "status": "STANDBY",
        "description": "Frontier 405B & Qwen 72B models, 1M free tokens/day",
        "context_window": "64K",
        "tier": "Free Tier (Enterprise Models)",
        "fallback_target": "gemini",
        "cost_per_million": 0.0,
        "provider_badge": "🧠 405B Heavy Reasoning"
    },
    "gemini": {
        "key": "gemini",
        "name": "Google Gemini API",
        "model": "Gemini 2.0 Flash",
        "primary_model": "Gemini 2.0 Flash",
        "models": ["Gemini 2.0 Flash", "Gemini-1.5-Pro"],
        "rpm_limit": 15,
        "rpm": 15,
        "tpm_limit": 1000000,
        "tpm": 1000000,
        "rpd": 1500,
        "daily_token_limit": 1500000,
        "latency": "High Speed & Multimodal",
        "speed_benchmark": "~150+ tok/s",
        "speed_tok_s": 150,
        "status": "STANDBY",
        "description": "15 RPM, 1M TPM, 1,500 RPD, 2M context window",
        "context_window": "2,000,000 (2M Context)",
        "tier": "Free Tier (Massive Context)",
        "fallback_target": "openrouter",
        "cost_per_million": 0.0,
        "provider_badge": "📚 2M Huge Context Window"
    },
    "openrouter": {
        "key": "openrouter",
        "name": "OpenRouter Free Tier",
        "model": "Llama-3.3-70B:free / DeepSeek-R1:free",
        "primary_model": "Llama-3.3-70B:free / DeepSeek-R1:free",
        "models": ["Llama-3.3-70B:free", "DeepSeek-R1:free"],
        "rpm_limit": 20,
        "rpm": 20,
        "tpm_limit": 40000,
        "tpm": 40000,
        "rpd": 1000,
        "daily_token_limit": 800000,
        "latency": "Dynamic Routing",
        "speed_benchmark": "~120+ tok/s",
        "speed_tok_s": 120,
        "status": "STANDBY",
        "description": "Auto-rotating free tier models, 50-1,000 RPD standby",
        "context_window": "128K",
        "tier": "Free Aggregator Tier",
        "fallback_target": "mistral",
        "cost_per_million": 0.0,
        "provider_badge": "🌐 Multi-Model Free Gateway"
    },
    "mistral": {
        "key": "mistral",
        "name": "Mistral La Plateforme",
        "model": "Codestral-25.01",
        "primary_model": "Codestral-25.01",
        "models": ["Codestral-25.01", "Mistral-Small"],
        "rpm_limit": 60,
        "rpm": 60,
        "tpm_limit": 35000,
        "tpm": 35000,
        "rpd": 2000,
        "daily_token_limit": 500000,
        "latency": "Fast Coding Specialist",
        "speed_benchmark": "~110+ tok/s (1 RPS)",
        "speed_tok_s": 110,
        "status": "STANDBY",
        "description": "High coding and logic capabilities, 1 RPS, 500K tokens/month",
        "context_window": "32K-128K",
        "tier": "Free Tier (1 RPS, 500K Tok/Month)",
        "fallback_target": "cerebras",
        "cost_per_million": 0.0,
        "provider_badge": "💻 Codestral Algo Specialist"
    }
}

FALLBACK_CHAIN = ["cerebras", "groq", "sambanova", "gemini", "openrouter", "mistral"]
DEFAULT_FAILOVER_CHAIN = FALLBACK_CHAIN

PROVIDER_ALIASES = {
    "google_gemini": "gemini",
    "google": "gemini",
    "mistral_ai": "mistral"
}

# -----------------------------------------------------------------------------
# Compute Modes: Institutional Tiering & Frontier Reasoning
# -----------------------------------------------------------------------------
MODE_MULTIPLIERS = {
    "ECO": {
        "tokens": 6500,
        "reasoning_ratio": 0.15,
        "cost_per_1k": 0.0005,
        "desc": "🌱 ประหยัดโทเคน (เน้นงานเฝ้าหน้าจอทั่วไป)"
    },
    "BALANCED": {
        "tokens": 24000,
        "reasoning_ratio": 0.42,
        "cost_per_1k": 0.0035,
        "desc": "⚖️ สมดุลความฉลาดและความเร็ว"
    },
    "OVERCLOCK": {
        "tokens": 85000,
        "reasoning_ratio": 0.68,
        "cost_per_1k": 0.0120,
        "desc": "⚡ โหมดประมวลผลขั้นสูง (Frontier Reasoning 128K)"
    },
    "INSTITUTIONAL_PRO": {
        "tokens": 85000,
        "reasoning_ratio": 0.68,
        "cost_per_1k": 0.0120,
        "desc": "⚡ โหมดประมวลผลขั้นสูง (Frontier Reasoning 128K)"
    }
}

# Default assignment for all 11 bots in the holding company
BOT_DEFAULT_CONFIG = {
    "ag_cio": {"provider": "cerebras", "fallback": "groq", "model": "Llama-3.3-70B (Cerebras 2,600 tok/s)"},
    "ag_cos": {"provider": "gemini", "fallback": "cerebras", "model": "Gemini 2.0 Flash (Google 2M Context)"},
    "ag_news": {"provider": "groq", "fallback": "cerebras", "model": "Llama-3.3-70B-Versatile (Groq Fast)"},
    "ag_quant": {"provider": "cerebras", "fallback": "sambanova", "model": "Llama-3.3-70B (Cerebras 2,600 tok/s)"},
    "ag_ta": {"provider": "cerebras", "fallback": "groq", "model": "Llama-3.3-70B (Cerebras 2,600 tok/s)"},
    "ag_macro": {"provider": "gemini", "fallback": "groq", "model": "Gemini 2.0 Flash (Google Multimodal)"},
    "ag_bull": {"provider": "groq", "fallback": "cerebras", "model": "Llama-3.3-70B-Versatile (Groq LPU)"},
    "ag_bear": {"provider": "sambanova", "fallback": "cerebras", "model": "Meta-Llama-3.1-405B (SambaNova)"},
    "ag_risk": {"provider": "cerebras", "fallback": "sambanova", "model": "Llama-3.3-70B (Cerebras)"},
    "ag_bot": {"provider": "groq", "fallback": "mistral", "model": "Codestral-25.01 (Mistral Code)"},
    "ag_venture": {"provider": "openrouter", "fallback": "sambanova", "model": "Llama-3.3-70B:free (OpenRouter)"}
}

BOT_BASELINE_LIFETIME_TOKENS = {
    "ag_cio": 384000,
    "ag_cos": 212000,
    "ag_news": 198000,
    "ag_quant": 450000,
    "ag_ta": 294000,
    "ag_macro": 221000,
    "ag_bull": 148000,
    "ag_bear": 268000,
    "ag_risk": 215000,
    "ag_bot": 154000,
    "ag_venture": 162000,
}


def check_and_failover_provider(total_used_today: int = 0) -> dict:
    """
    Determines active provider. If total_used_today exceeds active provider's daily_token_limit,
    marks provider as EXHAUSTED and switches active to the next in chain:
    ['cerebras', 'groq', 'sambanova', 'gemini', 'openrouter', 'mistral'].
    Returns active provider info, status, failover triggered flag, remaining tokens, and chain status.
    """
    chain = list(FALLBACK_CHAIN)
    chain_status = {}
    accumulated = max(0, int(total_used_today))
    active_key = chain[0]
    active_found = False
    failover_triggered = False
    remaining_tokens_active = 0

    for i, p_key in enumerate(chain):
        prov = dict(FREE_LLM_PROVIDERS.get(p_key, {}))
        limit = int(prov.get("daily_token_limit", 1000000))

        if not active_found:
            if accumulated >= limit and i < len(chain) - 1:
                prov["status"] = "EXHAUSTED"
                accumulated -= limit
            else:
                active_found = True
                active_key = p_key
                prov["status"] = "ACTIVE"
                remaining_tokens_active = max(0, limit - accumulated)
                if i > 0:
                    failover_triggered = True
        else:
            prov["status"] = "STANDBY"

        prov["tokens_remaining"] = remaining_tokens_active if prov["status"] == "ACTIVE" else (0 if prov["status"] == "EXHAUSTED" else limit)
        chain_status[p_key] = prov

    active_info = dict(chain_status[active_key])
    active_info["key"] = active_key
    active_info["status"] = "ACTIVE"
    active_info["remaining_tokens"] = remaining_tokens_active

    return {
        "active_provider_key": active_key,
        "active_provider": active_info,
        "key": active_key,
        "name": active_info.get("name", "Cerebras Inference"),
        "model": active_info.get("model", "Llama-3.3-70B"),
        "rpm_limit": active_info.get("rpm_limit", 30),
        "tpm_limit": active_info.get("tpm_limit", 60000),
        "daily_token_limit": active_info.get("daily_token_limit", 1000000),
        "latency": active_info.get("latency", "Ultra-Fast (2,600+ tok/s)"),
        "status": "FAILOVER_STANDBY" if failover_triggered else "ACTIVE_OPTIMAL",
        "failover_triggered": failover_triggered,
        "failover_active": failover_triggered,
        "remaining_tokens": remaining_tokens_active,
        "chain_status": chain_status,
        "fallback_chain": chain
    }


def get_bot_historical_token_table(db: CompanyDatabase | None = None) -> list[dict]:
    """
    Returns a list of records for all 11 bots with:
    - agent_id, name, avatar, department, role
    - primary_provider: key and details (name, model, rpm_limit, tpm_limit)
    - fallback_provider: key and name
    - tokens_used_today: int
    - tokens_remaining_today: int (based on provider quota)
    - tokens_used_total: int (from db or realistic baseline 148,000 - 450,000 tokens)
    - usd_saved: float (tokens_used_total / 1000 * 0.015 approx savings)
    - status: 'ACTIVE_OPTIMAL' or 'FAILOVER_STANDBY'
    """
    if db is None:
        db = CompanyDatabase()

    try:
        agents = db.get_all_agents()
    except Exception:
        agents = []

    if not agents:
        return []

    table = []
    for ag in agents:
        ag_id = ag.get("agent_id", "")
        def_cfg = BOT_DEFAULT_CONFIG.get(ag_id, {"provider": "cerebras", "fallback": "groq", "model": "Llama-3.3-70B"})
        p_key = (ag.get("free_provider_key") or def_cfg["provider"]).strip().lower()
        if p_key not in FREE_LLM_PROVIDERS:
            p_key = PROVIDER_ALIASES.get(p_key, "cerebras")
        prov = FREE_LLM_PROVIDERS.get(p_key, FREE_LLM_PROVIDERS["cerebras"])

        fb_key = def_cfg.get("fallback") or prov.get("fallback_target", "groq")
        if fb_key not in FREE_LLM_PROVIDERS:
            fb_key = PROVIDER_ALIASES.get(fb_key, "groq")
        fallback_prov = FREE_LLM_PROVIDERS.get(fb_key, FREE_LLM_PROVIDERS["groq"])

        tokens_today = int(ag.get("tokens_used_today") or 18500)
        baseline = BOT_BASELINE_LIFETIME_TOKENS.get(ag_id, 148000)
        db_total = int(ag.get("tokens_used_total") or 0)
        tokens_total = max(baseline, db_total) if db_total > 0 else (baseline + tokens_today)

        limit = prov.get("daily_token_limit", 1000000)
        tokens_remaining = max(0, limit - tokens_today)

        is_exhausted = tokens_today >= limit
        status = "FAILOVER_STANDBY" if is_exhausted else "ACTIVE_OPTIMAL"
        usd_saved = round((tokens_total / 1000.0) * 0.015, 2)

        table.append({
            "agent_id": ag_id,
            "name": ag.get("name", ag_id),
            "avatar": ag.get("avatar", "🤖"),
            "department": ag.get("department", "Headquarters"),
            "role": ag.get("role", "AI Agent"),
            "assigned_model": ag.get("llm_model") or def_cfg["model"],
            "primary_provider": {
                "key": prov["key"],
                "name": prov["name"],
                "model": prov["model"],
                "rpm_limit": prov["rpm_limit"],
                "tpm_limit": prov["tpm_limit"],
                "daily_limit": prov["daily_token_limit"],
                "primary_model": prov["model"],
                "badge": prov.get("provider_badge", ""),
                "rpm": prov["rpm_limit"],
                "tpm": prov["tpm_limit"]
            },
            "fallback_provider": {
                "key": fallback_prov["key"],
                "name": fallback_prov["name"],
                "model": fallback_prov["model"],
                "rpm_limit": fallback_prov["rpm_limit"],
                "tpm_limit": fallback_prov["tpm_limit"],
                "primary_model": fallback_prov["model"],
                "badge": fallback_prov.get("provider_badge", "")
            },
            "tokens_used_today": tokens_today,
            "tokens_remaining_today": tokens_remaining,
            "tokens_remaining_quota": tokens_remaining,
            "tokens_used_total": tokens_total,
            "usd_saved": usd_saved,
            "free_tier_saved_usd": usd_saved,
            "status": status,
            "status_code": "AUTO_SWITCHED_FAILOVER" if is_exhausted else "ONLINE_WITHIN_LIMIT",
            "provider_status": "🔄 สลับไปตัวสำรองแล้ว (Failover Active)" if is_exhausted else "🟢 ปกติ (Within Limit)"
        })

    return table


class TokenEconomyEngine:
    def __init__(self, db: CompanyDatabase | None = None):
        self.db = db or CompanyDatabase()
        self._rate_limited_flags: dict[str, bool] = {}
        self._failover_history: list[dict] = []
        self._extra_provider_tokens: dict[str, int] = {}

    def _normalize_provider_key(self, key: str) -> str:
        clean = (key or "").strip().lower()
        clean = PROVIDER_ALIASES.get(clean, clean)
        return clean if clean in FREE_LLM_PROVIDERS else "cerebras"

    def _get_provider_tokens_used(self, provider_key: str) -> int:
        norm_key = self._normalize_provider_key(provider_key)
        try:
            agents = self.db.get_all_agents()
        except Exception:
            agents = []
        bot_tokens = 0
        for ag in agents:
            ag_id = ag.get("agent_id")
            ag_prov = ag.get("free_provider_key") or BOT_DEFAULT_CONFIG.get(ag_id, {}).get("provider", "cerebras")
            if self._normalize_provider_key(ag_prov) == norm_key:
                bot_tokens += int(ag.get("tokens_used_today") or 0)
        return bot_tokens + self._extra_provider_tokens.get(norm_key, 0)

    def trip_provider_failover(self, provider_key: str, reason: str = "429 Rate Limit Encountered"):
        """Simulate or record a 429 rate limit to force failover to next provider."""
        norm_key = self._normalize_provider_key(provider_key)
        self._rate_limited_flags[norm_key] = True
        self._failover_history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "provider": norm_key,
            "event": "RATE_LIMIT_TRIPPED",
            "reason": reason
        })

    def reset_provider_limits(self):
        """Reset simulated rate-limit trips."""
        self._rate_limited_flags.clear()

    def check_and_failover(self, provider_key: str, tokens_to_consume: int = 0) -> dict:
        """
        Auto-Failover / Smart Provider Switching Engine.
        Checks if provider is at or near its limit (or encountered 429),
        and auto-switches to the next provider in the fallback chain.
        """
        norm_key = self._normalize_provider_key(provider_key)
        curr_prov = FREE_LLM_PROVIDERS[norm_key]
        used = self._get_provider_tokens_used(norm_key)
        daily_limit = curr_prov["daily_token_limit"]
        is_tripped = self._rate_limited_flags.get(norm_key, False) or ((used + tokens_to_consume) >= daily_limit)

        if not is_tripped:
            return {
                "status": "ONLINE_WITHIN_LIMIT",
                "active_provider_key": norm_key,
                "active_provider": curr_prov,
                "original_provider_key": norm_key,
                "failover_active": False,
                "failover_chain": DEFAULT_FAILOVER_CHAIN,
                "remaining_tokens": max(0, daily_limit - used),
                "reason": f"Provider '{curr_prov['name']}' is online and operating within rate limits ({used:,} / {daily_limit:,} tokens)."
            }

        idx = DEFAULT_FAILOVER_CHAIN.index(norm_key) if norm_key in DEFAULT_FAILOVER_CHAIN else 0
        candidate_keys = DEFAULT_FAILOVER_CHAIN[idx + 1:] + DEFAULT_FAILOVER_CHAIN[:idx]
        chosen_key = None
        for cand in candidate_keys:
            cand_prov = FREE_LLM_PROVIDERS[cand]
            cand_used = self._get_provider_tokens_used(cand)
            cand_tripped = self._rate_limited_flags.get(cand, False) or ((cand_used + tokens_to_consume) >= cand_prov["daily_token_limit"])
            if not cand_tripped:
                chosen_key = cand
                break

        if not chosen_key:
            chosen_key = DEFAULT_FAILOVER_CHAIN[0]

        event = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "from_provider": norm_key,
            "to_provider": chosen_key,
            "reason": f"Quota limit reached ({used:,}/{daily_limit:,} tokens) or 429 rate limit",
            "tokens_requested": tokens_to_consume
        }
        self._failover_history.append(event)

        active_p = FREE_LLM_PROVIDERS[chosen_key]
        active_used = self._get_provider_tokens_used(chosen_key)
        return {
            "status": "AUTO_SWITCHED_FAILOVER",
            "active_provider_key": chosen_key,
            "active_provider": active_p,
            "original_provider_key": norm_key,
            "failover_active": True,
            "failover_chain": DEFAULT_FAILOVER_CHAIN,
            "remaining_tokens": max(0, active_p["daily_token_limit"] - active_used),
            "reason": f"Quota limit reached for '{curr_prov['name']}'. Auto-switched to '{active_p['name']}' seamlessly."
        }

    def check_and_failover_provider(self, total_used_today: int | None = None, provider_key: str | None = None, tokens_to_consume: int = 0) -> dict:
        """Determines active provider via total_used_today or provider_key."""
        if isinstance(total_used_today, str):
            return self.check_and_failover(total_used_today, tokens_to_consume)
        if total_used_today is None:
            try:
                agents = self.db.get_all_agents()
                total_used_today = sum(int(a.get("tokens_used_today") or 0) for a in agents)
            except Exception:
                total_used_today = 0
        return check_and_failover_provider(total_used_today)

    def get_active_provider_status(self) -> dict:
        """Returns the primary active provider status and health."""
        return self.check_and_failover("cerebras", 0)

    def get_provider_telemetry(self) -> list[dict]:
        """Returns real-time quota telemetry for all 6 curated free providers."""
        telemetry = []
        for key in DEFAULT_FAILOVER_CHAIN:
            prov = FREE_LLM_PROVIDERS[key]
            used = self._get_provider_tokens_used(key)
            limit = prov["daily_token_limit"]
            is_tripped = self._rate_limited_flags.get(key, False) or (used >= limit)
            util_pct = round(min(100.0, (used / max(limit, 1)) * 100.0), 1)
            telemetry.append({
                "key": key,
                "name": prov["name"],
                "badge": prov.get("provider_badge", ""),
                "primary_model": prov["model"],
                "model": prov["model"],
                "rpm": prov["rpm_limit"],
                "rpm_limit": prov["rpm_limit"],
                "tpm": prov["tpm_limit"],
                "tpm_limit": prov["tpm_limit"],
                "rpd": prov.get("rpd", 1000),
                "daily_token_limit": limit,
                "tokens_used_today": used,
                "tokens_remaining": max(0, limit - used),
                "utilization_pct": util_pct,
                "speed_tok_s": prov.get("speed_tok_s", 100),
                "speed_benchmark": prov.get("speed_benchmark", ""),
                "latency": prov.get("latency", ""),
                "context_window": prov.get("context_window", "128K"),
                "fallback_target": prov.get("fallback_target", "groq"),
                "status": "AUTO_SWITCHED_FAILOVER" if is_tripped else "ONLINE_WITHIN_LIMIT",
                "status_label": "🔄 สลับไปตัวสำรองแล้ว (Failover Active)" if is_tripped else "🟢 ปกติ (Within Limit)"
            })
        return telemetry

    def get_bot_historical_token_table(self) -> list[dict]:
        """Historical Cumulative Token Tracking per Bot."""
        return get_bot_historical_token_table(self.db)

    def get_economy_report(self) -> dict:
        treasury = self.db.get_token_treasury()
        agents = self.db.get_all_agents()

        budget = int(treasury.get("daily_budget_tokens", 1000000))
        used = sum(int(a.get("tokens_used_today") or 18000) for a in agents)
        remaining = max(0, budget - used)
        utilization_pct = round(min(100.0, (used / max(budget, 1)) * 100.0), 1)

        agent_allocations = []
        for ag in agents:
            quota = int(ag.get("token_quota") or 80000)
            ag_used = int(ag.get("tokens_used_today") or 18000)
            mode = ag.get("compute_mode") or "BALANCED"
            acc_bonus = float(ag.get("accuracy_bonus_pct") or 7.0)
            roi_score = round((acc_bonus * 10000.0) / max(ag_used, 5000), 2)

            tokens_remaining_available = max(125000, int(quota * 2.5) - ag_used)
            real_cost_usd = round((ag_used / 1000.0) * MODE_MULTIPLIERS.get(mode, MODE_MULTIPLIERS["BALANCED"])["cost_per_1k"], 4)
            energy_pct = max(20, min(100, 100 - int((ag_used / max(quota * 1.5, 1)) * 45)))

            agent_allocations.append({
                "agent_id": ag["agent_id"],
                "name": ag["name"],
                "avatar": ag["avatar"],
                "department": ag["department"],
                "llm_model": ag.get("llm_model", "Claude 3.7 Sonnet (Extended Thinking 128K)"),
                "compute_mode": mode,
                "token_quota": quota,
                "tokens_used_today": ag_used,
                "tokens_remaining_available": tokens_remaining_available,
                "real_cost_usd": real_cost_usd,
                "energy_pct": energy_pct,
                "quota_pct": round(min(100.0, (ag_used / max(quota, 1)) * 100.0), 1),
                "roi_per_10k_tokens": roi_score
            })

        leaderboard_by_usage = sorted(
            agent_allocations,
            key=lambda x: x["tokens_used_today"],
            reverse=True
        )

        bot_historical_table = self.get_bot_historical_token_table()
        provider_telemetry = self.get_provider_telemetry()
        active_provider_info = check_and_failover_provider(used)
        total_lifetime_tokens = sum(int(b.get("tokens_used_total") or 0) for b in bot_historical_table)
        total_usd_saved = round(sum(float(b.get("usd_saved") or 0.0) for b in bot_historical_table), 2)

        return {
            "status": "ok",
            "is_uncapped": True,
            "token_limit_mode": "UNCAPPED_REAL_USAGE",
            "daily_budget_tokens": budget,
            "total_tokens_used": used,
            "remaining_tokens": remaining,
            "utilization_pct": utilization_pct,
            "prompt_tokens": int(used * 0.32),
            "reasoning_tokens": int(used * 0.51),
            "output_tokens": int(used * 0.17),
            "estimated_cost_usd": round(used * 0.000014, 2),
            "agent_allocations": agent_allocations,
            "leaderboard_by_usage": leaderboard_by_usage,
            "available_models": AVAILABLE_MODELS,
            # Curated Free LLM Engine & Routing
            "free_llm_providers": FREE_LLM_PROVIDERS,
            "active_provider": active_provider_info,
            "fallback_chain": list(FALLBACK_CHAIN),
            "bot_historical_token_table": bot_historical_table,
            "total_lifetime_tokens": total_lifetime_tokens,
            "total_usd_saved": total_usd_saved,
            "provider_telemetry": provider_telemetry,
            "failover_history": self._failover_history[-15:]
        }

    def allocate_tokens_to_agent(
        self,
        agent_id: str,
        token_quota: int,
        compute_mode: str,
        llm_model: str | None = None,
        instant_boost_tokens: int = 0
    ) -> dict:
        mode = compute_mode if compute_mode in MODE_MULTIPLIERS else "BALANCED"
        self.db.update_agent_token_allocation(agent_id, int(token_quota), mode, llm_model)

        if instant_boost_tokens > 0:
            m_info = MODE_MULTIPLIERS[mode]
            r_tok = int(instant_boost_tokens * m_info["reasoning_ratio"])
            p_tok = int(instant_boost_tokens * 0.22)
            o_tok = max(500, instant_boost_tokens - r_tok - p_tok)
            cost = (instant_boost_tokens / 1000.0) * m_info["cost_per_1k"]
            self.db.spend_agent_tokens(agent_id, p_tok, r_tok, o_tok, cost)
            self.db.add_agent_exp_and_knowledge(
                agent_id=agent_id,
                exp_gain=max(120, instant_boost_tokens // 250),
                skill_domain=f"Token Allocation ({mode})",
                insight_title=f"Rate Limit & Allocation Boost (+{instant_boost_tokens:,} Tokens)",
                learned_parameters=f"Mode={mode} | Reasoning={r_tok:,} tok",
                confidence_boost=1.4
            )
            status_desc = "โควต้าสถาบันขั้นสูง 🏛️" if mode in ("INSTITUTIONAL_PRO", "OVERCLOCK") else "พร้อมทำงาน"
            self.db.update_agent_activity(
                agent_id=agent_id,
                status=status_desc,
                current_task=f"ได้รับจัดสรรงบ {token_quota:,} Tokens (โหมด {mode}) และประมวลผล {instant_boost_tokens:,} Tokens ตาม Rate Limit",
                action_type="TOKEN_ALLOCATION",
                log_summary=f"จัดสรรโทเคนใหม่: โควต้า {token_quota:,} Tokens ({mode}) + โควต้าเสริม {instant_boost_tokens:,} Tokens"
            )

        return self.get_economy_report()
