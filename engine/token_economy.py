"""
Token Treasury & Compute Allocation Manager (V6)
Manages the AI Holding Company's Daily Token Budget, Per-Agent Token Quotas,
Compute Modes (ECO / BALANCED / OVERCLOCK), Reasoning Token Burn Rate, and Token ROI.
"""
from data.database import CompanyDatabase
from engine.llm_router import AVAILABLE_MODELS


MODE_MULTIPLIERS = {
    "ECO": {"tokens": 6500, "reasoning_ratio": 0.15, "cost_per_1k": 0.0005, "desc": "🌱 ประหยัดโทเคน (เน้นงานเฝ้าหน้าจอทั่วไป)"},
    "BALANCED": {"tokens": 24000, "reasoning_ratio": 0.42, "cost_per_1k": 0.0035, "desc": "⚖️ สมดุลความฉลาดและความเร็ว"},
    "OVERCLOCK": {"tokens": 85000, "reasoning_ratio": 0.68, "cost_per_1k": 0.0120, "desc": "🔥 ทุ่มโทเคนคิดลึกสุดขีด (Extended Thinking 128K + วิจัยสกิลใหม่)"}
}


class TokenEconomyEngine:
    def __init__(self, db: CompanyDatabase | None = None):
        self.db = db or CompanyDatabase()

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

        return {
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
            "available_models": AVAILABLE_MODELS
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
                skill_domain=f"Token Overclock ({mode})",
                insight_title=f"Deep Reasoning Boost (+{instant_boost_tokens:,} Tokens)",
                learned_parameters=f"Mode={mode} | Reasoning={r_tok:,} tok",
                confidence_boost=1.4
            )
            self.db.update_agent_activity(
                agent_id=agent_id,
                status="กำลังใช้โทเคนคิดลึก 🔥" if mode == "OVERCLOCK" else "พร้อมทำงาน",
                current_task=f"ได้รับจัดสรรงบ {token_quota:,} Tokens (โหมด {mode}) และเผา {instant_boost_tokens:,} Tokens คิดเชิงลึก",
                action_type="TOKEN_ALLOCATION",
                log_summary=f"จัดสรรโทเคนใหม่: โควต้า {token_quota:,} Tokens ({mode}) + อัดฉีด {instant_boost_tokens:,} Tokens"
            )

        return self.get_economy_report()
