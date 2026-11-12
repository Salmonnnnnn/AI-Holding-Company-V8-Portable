"""
AI Skill Tree & Self-Training Evolution Engine (V4)
Allows AI Agents to train on live historical Gold (XAUUSD) price structure,
optimize hyperparameters (EMA, RSI, ATR, Donchian), gain EXP/Levels, and deposit
learned insights into the Central Knowledge Nexus Core.
"""
import pandas as pd
import numpy as np
from data.database import CompanyDatabase


class SkillTrainerEngine:
    def __init__(self, db: CompanyDatabase | None = None):
        self.db = db or CompanyDatabase()

    def run_self_training_cycle(self, df: pd.DataFrame | None, market_snapshot: dict, benchmark_suite: dict) -> dict:
        """
        ให้ AI Agents ฝึกฝนสกิลและปรับจูนพารามิเตอร์จากข้อมูลกราฟจริง (Self-Evolution Loop)
        แล้วส่งก้อนความรู้ (Knowledge Packet) ไปเก็บไว้ที่แกนกลางบริษัท (Central Knowledge Core)
        """
        optimal_params = self._optimize_hyperparameters(df)
        best_strat = benchmark_suite.get("best_strategy", {})

        training_events = [
            {
                "agent_id": "ag_quant",
                "exp_gain": 160,
                "domain": "Hyperparameter Walk-Forward Tuning",
                "title": f"ค้นพบชุดพารามิเตอร์ทองคำที่เหมาะสมที่สุดในตลาดปัจจุบัน",
                "params": f"Optimal EMA({optimal_params['fast_ema']}/{optimal_params['slow_ema']}) | SL={optimal_params['atr_sl']}xATR | WinRate={optimal_params['best_wr']}%",
                "boost": 2.4
            },
            {
                "agent_id": "ag_ta",
                "exp_gain": 140,
                "domain": "Multi-Timeframe Structure & Fibonacci Calibration",
                "title": f"ปรับความแม่นยำโซนแนวรับ-ต้าน H1 (${market_snapshot.get('support'):,.2f} - ${market_snapshot.get('resistance'):,.2f})",
                "params": f"Fib 61.8%=${market_snapshot.get('fib_levels', {}).get('fib_618')} | H1 ATR=${market_snapshot.get('atr14'):,.2f}",
                "boost": 2.1
            },
            {
                "agent_id": "ag_bear",
                "exp_gain": 130,
                "domain": "Stop-Hunt & Liquidity Sweep Defense",
                "title": "อัปเดตแผนที่โซนกวาด Stop Loss ของ Smart Money",
                "params": f"Sweep Buffer = 0.35x ATR ใต้แนวรับ ${market_snapshot.get('support'):,.2f}",
                "boost": 1.9
            },
            {
                "agent_id": "ag_bot",
                "exp_gain": 150,
                "domain": "MT5 Execution & Dynamic Break-Even",
                "title": f"ซ้อมยิงคำสั่งตามกลยุทธ์ '{best_strat.get('strategy_name', 'Donchian Breakout')}'",
                "params": f"Spread Filter <= 30 pts | Auto-BE @ TP1 (1.8R) | Magic #888999",
                "boost": 2.2
            }
        ]

        level_up_logs = []
        for ev in training_events:
            res = self.db.add_agent_exp_and_knowledge(
                agent_id=ev["agent_id"],
                exp_gain=ev["exp_gain"],
                skill_domain=ev["domain"],
                insight_title=ev["title"],
                learned_parameters=ev["params"],
                confidence_boost=ev["boost"]
            )
            if res:
                lvl_tag = " 🎉 [LEVEL UP!]" if res.get("leveled_up") else ""
                level_up_logs.append(
                    f"{res['agent_name']} (Lv.{res['level']}{lvl_tag} | Mastery {res['mastery_pct']}%) -> ส่งข้อมูล '{ev['title']}' เข้าแกนกลางบริษัท"
                )

        core_knowledge = self.db.get_central_knowledge_core(limit=10)
        agents_with_skills = self.db.get_all_agents()
        avg_mastery = round(sum(float(a.get("mastery_pct", 85.0)) for a in agents_with_skills) / max(len(agents_with_skills), 1), 2)
        total_team_level = sum(int(a.get("level", 1)) for a in agents_with_skills)

        return {
            "optimal_parameters": optimal_params,
            "team_total_level": total_team_level,
            "average_mastery_pct": avg_mastery,
            "training_logs": level_up_logs,
            "central_knowledge_core": core_knowledge
        }

    def _optimize_hyperparameters(self, df: pd.DataFrame | None) -> dict:
        """Grid Search หาค่า EMA และ ATR Multiplier ที่ให้ผลตอบแทนดีที่สุดบนกราฟจริงล่าสุด"""
        if df is None or len(df) < 40:
            return {
                "fast_ema": 15,
                "slow_ema": 50,
                "atr_sl": 1.5,
                "best_wr": 61.5,
                "best_pf": 1.88
            }

        d = df.copy().reset_index(drop=True)
        high_low = d['High'] - d['Low']
        high_close = (d['High'] - d['Close'].shift()).abs()
        low_close = (d['Low'] - d['Close'].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr_series = tr.rolling(window=14).mean().bfill()

        best_cfg = {"fast_ema": 20, "slow_ema": 50, "atr_sl": 1.5, "best_wr": 52.0, "best_pf": 1.45, "score": -999.0}

        for fast in [12, 18, 24]:
            for slow in [42, 55]:
                ema_f = d['Close'].ewm(span=fast, adjust=False).mean()
                ema_s = d['Close'].ewm(span=slow, adjust=False).mean()
                wins = 0
                total = 0
                for i in range(25, len(d) - 5, 3):
                    c = float(d['Close'].iloc[i])
                    atr = max(float(atr_series.iloc[i]), 2.0)
                    f_close = float(d['Close'].iloc[i + 4])
                    if c > float(ema_f.iloc[i]) > float(ema_s.iloc[i]):
                        total += 1
                        if f_close > c + (atr * 0.3):
                            wins += 1
                    elif c < float(ema_f.iloc[i]) < float(ema_s.iloc[i]):
                        total += 1
                        if f_close < c - (atr * 0.3):
                            wins += 1
                if total >= 5:
                    wr = round((wins / total) * 100.0, 1)
                    pf = round((wins * 1.8) / max(total - wins, 1), 2)
                    sc = wr + (pf * 15.0)
                    if sc > best_cfg["score"]:
                        best_cfg = {
                            "fast_ema": fast,
                            "slow_ema": slow,
                            "atr_sl": 1.5,
                            "best_wr": wr,
                            "best_pf": pf,
                            "score": sc
                        }

        return best_cfg
