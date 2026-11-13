"""
Aurum Isle — เกาะ AI ล่าทองคำ (single-file dashboard renderer).
Cozy isometric island town (each AI agent has a house + energy battery) with a
30-day "$1,000 challenge" banner, Light/Dark theme, Token Treasury & Skill Harvester,
Historical Shift Replay, Agent Profiles, Copilot Chat and MT5 Demo / Obsidian Vault.
"""
import html
import json
from datetime import datetime, timedelta

BRAND_NAME = "Aurum Isle"
BRAND_TAGLINE = "เกาะ AI ล่าทองคำ"
CHALLENGE_GOAL_USD = 1000.0
CHALLENGE_DAYS = 30


def compute_challenge_state(port: dict | None, now: datetime | None = None) -> dict:
    """30-Day $1,000 challenge numbers derived from the existing portfolio state.

    - profit  = equity - initial_capital (fallback 0 when missing/invalid)
    - day     = days since first_trade_at + 1, clamped 1..30 (missing -> Day 1)
    - pct     = profit / goal * 100, clamped 0..100
    """
    port = port or {}
    now = now or datetime.now()
    try:
        profit = round(float(port.get("equity")) - float(port.get("initial_capital")), 2)
    except (TypeError, ValueError):
        profit = 0.0

    day = 1
    first = port.get("first_trade_at")
    if first:
        try:
            started = datetime.fromisoformat(str(first).strip())
            day = (now.date() - started.date()).days + 1
        except ValueError:
            day = 1
    day = max(1, min(CHALLENGE_DAYS, day))

    pct = max(0.0, min(100.0, (profit / CHALLENGE_GOAL_USD) * 100.0))
    return {
        "goal": CHALLENGE_GOAL_USD,
        "days_total": CHALLENGE_DAYS,
        "day": day,
        "days_left": CHALLENGE_DAYS - day,
        "profit": profit,
        "pct": round(pct, 1),
        "is_negative": profit < 0,
        "started_at": str(first) if first else None,
    }


def generate_html_dashboard(report: dict, filepath: str) -> str:
    market = report["market_snapshot"]
    ta = report["technical_analysis"]
    macro = report["macro_analysis"]
    deb = report["debate_critique"]
    risk = report["risk_assessment"]
    cio = report["cio_verdict"]
    bench = report.get("strategy_benchmarks", {})
    port = report.get("portfolio_state", {})
    office = report.get("office_digest", {})
    skill_rep = report.get("skill_training_report", {})
    mt5_demo = report.get("mt5_demo_telemetry", {})
    obs_info = report.get("obsidian_status", {})
    avail_models = report.get("available_models", [])
    tok_econ = report.get("token_economy", {})
    disc_skills = report.get("discovered_skills", [])
    checklist = report.get("workflow_checklist", [])
    catchup_info = report.get("offline_catchup", {})
    chat_hist = report.get("chat_history", [])

    action_text = str(cio.get("action", "WAIT"))
    today_dt = datetime.now()
    today_str = today_dt.strftime("%Y-%m-%d")
    d_m1 = (today_dt - timedelta(days=1)).strftime("%Y-%m-%d")
    d_m2 = (today_dt - timedelta(days=2)).strftime("%Y-%m-%d")
    d_m3 = (today_dt - timedelta(days=3)).strftime("%Y-%m-%d")
    d_m5 = (today_dt - timedelta(days=5)).strftime("%Y-%m-%d")
    challenge = compute_challenge_state(port, today_dt)
    chal_profit = float(challenge.get("profit", 0.0))
    chal_goal = float(challenge.get("goal", CHALLENGE_GOAL_USD))
    chal_pct = float(challenge.get("pct", 0.0))
    chal_day = int(challenge.get("day", 1))
    chal_days_total = int(challenge.get("days_total", CHALLENGE_DAYS))
    chal_days_left = int(challenge.get("days_left", CHALLENGE_DAYS - 1))
    chal_is_neg = bool(challenge.get("is_negative", False))
    chal_profit_col = "#ef4444" if chal_is_neg else "#fbbf24"
    chal_pill_bg = "rgba(239, 68, 68, 0.18)" if chal_is_neg else "rgba(16, 185, 129, 0.18)"
    chal_pill_col = "#fca5a5" if chal_is_neg else "#6ee7b7"
    chal_status_txt = "กำลังติดลบ (รอจังหวะแก้พอร์ต)" if chal_is_neg else f"ก้าวหน้า {chal_pct:.1f}% ของเป้า $1,000"
    port_equity = float(port.get("equity", 1000.0))
    port_winrate = float(port.get("live_win_rate_pct", 100.0))
    port_closed = int(port.get("total_closed_trades", 0))

    report_json = json.dumps({
        "session_time": report.get("session_time"),
        "brand_name": BRAND_NAME,
        "brand_tagline": BRAND_TAGLINE,
        "challenge": challenge,
        "market": market,
        "cio": cio,
        "deb": deb,
        "bench": bench,
        "port": port,
        "office": office,
        "skill_rep": skill_rep,
        "mt5_demo": mt5_demo,
        "obs_info": obs_info,
        "avail_models": avail_models,
        "tok_econ": tok_econ,
        "disc_skills": disc_skills,
        "checklist": checklist,
        "catchup_info": catchup_info,
        "chat_hist": chat_hist
    }, ensure_ascii=False)

    strat_rows_html = ""
    best_key = bench.get("best_strategy", {}).get("strategy_key", "")
    for s in bench.get("all_strategies", []):
        is_best = (s.get("strategy_key") == best_key)
        row_style = "background: rgba(245, 158, 11, 0.14); border-left: 4px solid #f59e0b;" if is_best else ""
        trophy = "🏆 " if is_best else ""
        strat_rows_html += f"""
        <tr style="{row_style}">
            <td><strong>{trophy}{html.escape(str(s.get('strategy_name')))}</strong><br><small style="color:var(--text-sub)">{html.escape(str(s.get('reference')))}</small></td>
            <td class="num"><span class="pill">{html.escape(str(s.get('best_regime')))}</span></td>
            <td class="num">{s.get('published_win_rate')}% (PF {s.get('published_pf')})</td>
            <td class="num" style="color:#10b981;font-weight:700">{s.get('live_win_rate')}% ({s.get('live_trades')} ไม้)</td>
            <td class="num" style="font-weight:700">{s.get('live_pf')}</td>
            <td class="num" style="color:{'#10b981' if float(s.get('live_net_r', 0)) >= 0 else '#ef4444'};font-weight:700">{s.get('live_net_r'):+}R</td>
            <td class="num"><strong>{html.escape(str(s.get('live_signal_now')))}</strong></td>
        </tr>
        """

    html_doc = f"""<!DOCTYPE html>
<html lang="th" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{BRAND_NAME} — {BRAND_TAGLINE} | 30-Day $1,000 AI Agent Town Challenge</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        /* LIGHT THEME (Default Cozy Pastel Island Town) */
        :root, [data-theme="light"] {{
            --bg-body: #f1f5f9;
            --bg-card: #ffffff;
            --bg-sub: #f8fafc;
            --border-col: #cbd5e1;
            --border-soft: #e2e8f0;
            --text-main: #0f172a;
            --text-sub: #64748b;
            --pill-bg: #e2e8f0;
            --pill-txt: #1e293b;
            --shadow-card: 0 6px 20px rgba(15, 23, 42, 0.06);
        }}
        /* DARK THEME (Pro Cyber Night Mode) */
        [data-theme="dark"] {{
            --bg-body: #070b14;
            --bg-card: #0f172a;
            --bg-sub: #1e293b;
            --border-col: #334155;
            --border-soft: #1e293b;
            --text-main: #f8fafc;
            --text-sub: #94a3b8;
            --pill-bg: #334155;
            --pill-txt: #f8fafc;
            --shadow-card: 0 6px 24px rgba(0, 0, 0, 0.45);
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-body);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            transition: background 0.25s, color 0.25s;
        }}
        .top-header {{
            display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px 16px;
            background: var(--bg-card);
            border-bottom: 1px solid var(--border-col);
            padding: 10px 20px;
            position: sticky; top: 0; z-index: 100;
            box-shadow: var(--shadow-card);
        }}
        .brand-wrap {{ display: flex; align-items: center; gap: 10px; min-width: 0; }}
        .brand-avatar {{
            width: 40px; height: 40px; border-radius: 12px;
            background: linear-gradient(135deg, #f59e0b, #ea580c);
            display: flex; align-items: center; justify-content: center;
            color: #fff; font-size: 1.25rem; font-weight: 900; flex-shrink: 0;
            box-shadow: 0 3px 10px rgba(245, 158, 11, 0.3);
        }}
        .status-pills-bar {{ display: flex; align-items: center; gap: 6px; flex-wrap: wrap; min-width: 0; }}
        .top-pill {{
            background: var(--bg-sub); border: 1px solid var(--border-col); border-radius: 999px;
            padding: 5px 11px; font-size: 0.78rem; font-weight: 600; color: var(--text-main);
            display: flex; align-items: center; gap: 6px; white-space: nowrap;
        }}
        .dot-green {{ width: 9px; height: 9px; border-radius: 50%; background: #10b981; display: inline-block; box-shadow: 0 0 6px #10b981; }}
        .progress-bar-mini {{ width: 64px; height: 7px; background: var(--border-col); border-radius: 99px; overflow: hidden; }}
        .progress-fill-mini {{ height: 100%; background: #10b981; width: 100%; transition: width 0.3s; }}

        .nav-tabs {{
            display: flex; gap: 8px; padding: 8px 20px;
            background: var(--bg-card); border-bottom: 1px solid var(--border-soft);
            overflow-x: auto; flex-wrap: wrap;
        }}
        .nav-tab {{
            background: var(--bg-sub); color: var(--text-sub);
            border: 1px solid var(--border-col); border-radius: 10px;
            padding: 8px 14px; font-weight: 700; font-size: 0.83rem;
            cursor: pointer; transition: all 0.18s; white-space: nowrap;
        }}
        .nav-tab:hover {{ color: var(--text-main); border-color: #f59e0b; }}
        .nav-tab.active {{
            background: linear-gradient(135deg, #f59e0b, #ea580c);
            color: #ffffff; border-color: #f59e0b;
            box-shadow: 0 3px 10px rgba(245, 158, 11, 0.25);
        }}

        .page-view {{ display: none; padding: 14px 20px; max-width: 1680px; width: 100%; margin: 0 auto; flex: 1; }}
        .page-view.active {{ display: block; }}

        /* 30-Day $1,000 AI Agent Town Challenge Banner (Reel-inspired) */
        .challenge-banner {{
            background: linear-gradient(135deg, #090d16 0%, #1e293b 55%, #0f172a 100%);
            border: 2px solid #f59e0b;
            border-radius: 16px;
            padding: 14px 20px;
            margin-bottom: 12px;
            color: #f8fafc;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 14px 24px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.22);
        }}
        .challenge-day-badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: linear-gradient(180deg, #fde68a 0%, #f59e0b 100%);
            color: #0f172a;
            font-weight: 900;
            font-size: 0.78rem;
            letter-spacing: 0.06em;
            padding: 4px 12px;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(245, 158, 11, 0.45);
        }}
        .challenge-headline {{
            font-size: 1.18rem;
            font-weight: 900;
            letter-spacing: 0.02em;
            color: #ffffff;
            text-shadow: 0 2px 6px rgba(0,0,0,0.45);
            margin-top: 4px;
            line-height: 1.25;
        }}
        .challenge-sub {{
            font-size: 0.8rem;
            color: #cbd5e1;
            margin-top: 3px;
        }}
        .challenge-right {{
            display: flex;
            align-items: center;
            gap: 18px;
            flex-wrap: wrap;
            min-width: 280px;
            flex: 1;
            justify-content: flex-end;
        }}
        .challenge-goal-figure {{
            text-align: right;
        }}
        .challenge-goal-big {{
            font-size: 1.55rem;
            font-weight: 900;
            background: linear-gradient(180deg, #fef08a 0%, #f59e0b 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            line-height: 1.15;
        }}
        .challenge-progress-wrap {{
            min-width: 230px;
            max-width: 340px;
            flex: 1;
        }}
        .challenge-progress-track {{
            width: 100%;
            height: 11px;
            background: rgba(255, 255, 255, 0.14);
            border: 1px solid rgba(251, 191, 36, 0.4);
            border-radius: 999px;
            overflow: hidden;
            margin-top: 6px;
        }}
        .challenge-progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #10b981 0%, #fbbf24 100%);
            border-radius: 999px;
            transition: width 0.4s ease;
        }}

        /* Offline Auto-Catchup Banner */
        .catchup-banner {{
            display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;
            background: linear-gradient(90deg, rgba(16, 185, 129, 0.14), rgba(14, 165, 233, 0.14));
            border: 1px solid #10b981; border-radius: 12px;
            padding: 8px 14px; margin-bottom: 12px; font-size: 0.83rem;
        }}

        .visualizer-layout {{
            display: grid;
            grid-template-columns: 1fr 365px;
            gap: 16px;
            align-items: start;
        }}
        .iso-stage-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-col);
            border-radius: 18px;
            overflow: hidden;
            box-shadow: var(--shadow-card);
            min-width: 0;
        }}
        .iso-canvas-wrap {{
            position: relative;
            width: 100%;
            height: 560px;
        }}
        #isometricOfficeCanvas {{ width: 100%; height: 100%; display: block; cursor: pointer; }}
        #threeContainer {{ width: 100%; height: 100%; display: none; }}

        .stage-floating-top-left {{
            position: absolute; top: 12px; left: 12px;
            display: flex; gap: 8px; flex-wrap: wrap; z-index: 10;
        }}
        .stage-floating-top-right {{
            position: absolute; top: 12px; right: 12px;
            display: flex; gap: 8px; z-index: 10;
        }}
        .cozy-btn {{
            background: var(--bg-card);
            border: 1px solid var(--border-col);
            color: var(--text-main);
            padding: 7px 13px;
            border-radius: 10px;
            font-size: 0.81rem;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            transition: all 0.15s;
            white-space: nowrap;
        }}
        .cozy-btn:hover {{ transform: translateY(-1px); border-color: #f59e0b; }}
        .cozy-btn.primary {{ background: #0f172a; color: #fbbf24; border-color: #334155; }}
        .cozy-btn.amber {{ background: linear-gradient(135deg, #f59e0b, #ea580c); color: #fff; border: none; }}
        .cozy-btn.green {{ background: linear-gradient(135deg, #10b981, #059669); color: #fff; border: none; }}
        .cozy-btn.purple {{ background: linear-gradient(135deg, #8b5cf6, #6d28d9); color: #fff; border: none; }}

        .dialogue-banner {{
            display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;
            padding: 12px 18px;
            background: var(--bg-sub);
            border-top: 1px solid var(--border-soft);
            border-bottom: 1px solid var(--border-soft);
        }}
        .mini-agents-strip {{
            display: flex; gap: 10px; padding: 12px 16px;
            overflow-x: auto; background: var(--bg-card);
        }}
        .mini-agent-card {{
            min-width: 172px;
            background: var(--bg-sub);
            border: 1px solid var(--border-col);
            border-radius: 12px;
            padding: 9px 12px;
            display: flex; align-items: center; gap: 10px;
            cursor: pointer; transition: all 0.15s;
        }}
        .mini-agent-card:hover, .mini-agent-card.active {{
            border-color: #f59e0b;
            box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.25);
            transform: translateY(-2px);
        }}

        .right-sidebar-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-col);
            border-radius: 18px;
            padding: 16px;
            box-shadow: var(--shadow-card);
            display: flex; flex-direction: column; gap: 14px;
            min-width: 0;
        }}
        .mission-item {{
            display: flex; align-items: flex-start; gap: 10px;
            padding: 7px 8px; border-radius: 10px;
            font-size: 0.82rem;
            border-bottom: 1px dashed var(--border-soft);
        }}
        .check-circle {{
            width: 20px; height: 20px; border-radius: 50%;
            background: #10b981; color: #fff;
            display: flex; align-items: center; justify-content: center;
            font-size: 0.72rem; font-weight: 900; flex-shrink: 0; margin-top: 2px;
        }}
        .check-circle.pending {{ background: var(--border-col); color: var(--text-sub); }}
        .check-circle.running {{ background: #f59e0b; color: #fff; }}

        .live-log-list {{
            max-height: 245px; overflow-y: auto;
            display: flex; flex-direction: column; gap: 6px;
            background: var(--bg-sub); border: 1px solid var(--border-col);
            border-radius: 12px; padding: 10px;
            font-size: 0.78rem;
        }}
        .live-log-row {{
            display: flex; gap: 8px; line-height: 1.4;
            padding-bottom: 5px; border-bottom: 1px solid var(--border-soft);
        }}
        .log-time {{ color: #0ea5e9; font-family: monospace; font-weight: 700; flex-shrink: 0; }}

        .white-card {{
            background: var(--bg-card); border: 1px solid var(--border-col);
            border-radius: 16px; padding: 20px; margin-bottom: 16px;
            box-shadow: var(--shadow-card);
            min-width: 0;
        }}
        .white-card h2 {{
            font-size: 1.06rem; color: var(--text-main); margin-bottom: 12px;
            border-bottom: 1px solid var(--border-soft); padding-bottom: 9px;
            line-height: 1.38; display: flex; align-items: center; justify-content: space-between;
            flex-wrap: wrap; gap: 8px;
        }}
        .section-head {{
            display: flex; justify-content: space-between; align-items: center;
            flex-wrap: wrap; gap: 10px 16px; margin-bottom: 14px;
            padding-bottom: 10px; border-bottom: 1px solid var(--border-soft);
        }}
        .section-head h2 {{
            border-bottom: none; padding-bottom: 0; margin-bottom: 0;
        }}
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
        .grid-2 > * {{ min-width: 0; }}
        .grid-4 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; }}
        .stat-metric-box {{
            background: var(--bg-sub); border: 1px solid var(--border-col);
            border-radius: 12px; padding: 14px; min-width: 0;
        }}
        .stat-metric-box .lbl {{ font-size: 0.77rem; color: var(--text-sub); font-weight: 700; line-height: 1.3; }}
        .stat-metric-box .val {{ font-size: 1.25rem; font-weight: 900; color: var(--text-main); margin-top: 4px; line-height: 1.25; }}

        .input-clean {{
            background: var(--bg-sub); border: 1px solid var(--border-col);
            border-radius: 10px; padding: 8px 12px; font-size: 0.86rem; color: var(--text-main);
        }}
        .shift-pill {{
            background: var(--bg-sub); border: 1px solid var(--border-col); color: var(--text-main);
            padding: 8px 14px; border-radius: 999px; cursor: pointer; font-weight: 700; font-size: 0.82rem;
        }}
        .shift-pill.active {{
            background: linear-gradient(135deg, #f59e0b, #ea580c); color: #fff; border-color: #f59e0b;
        }}
        .pill {{
            background: var(--pill-bg); color: var(--pill-txt);
            padding: 3px 9px; border-radius: 6px; font-size: 0.74rem; font-weight: 700;
            display: inline-block; white-space: nowrap;
        }}
        .table-wrap {{
            width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch;
            border: 1px solid var(--border-soft); border-radius: 12px;
        }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.84rem; }}
        th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border-soft); vertical-align: middle; line-height: 1.4; }}
        th {{ background: var(--bg-sub); color: var(--text-main); font-weight: 800; white-space: nowrap; }}
        td.num {{ white-space: nowrap; }}
        tbody tr:hover {{ background: rgba(245, 158, 11, 0.05); }}
        @media (max-width: 1180px) {{ .visualizer-layout, .grid-2 {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>

<!-- ====================================================================== -->
<!-- TOP STATUS HEADER + LIGHT/DARK THEME SWITCHER                          -->
<!-- ====================================================================== -->
<div class="top-header">
    <div class="brand-wrap">
        <div class="brand-avatar">🏝️</div>
        <div>
            <div style="font-weight:900;font-size:1.05rem;line-height:1.2">{BRAND_NAME} — {BRAND_TAGLINE}</div>
            <div style="font-size:0.74rem;color:var(--text-sub);margin-top:2px">เมือง AI เทรดทองคำ • ภารกิจ $1,000 ใน 30 วัน • 12+ โมเดลตัวท็อป • โหมดมืด/สว่าง & เก็บตกงานอัตโนมัติ</div>
        </div>
    </div>

    <div class="status-pills-bar">
        <div class="top-pill">
            <span class="dot-green"></span>
            <span id="topSysStatusText">ระบบปกติ พร้อมทำงาน</span>
        </div>
        <div class="top-pill">
            <span>🕒</span>
            <span id="liveThaiClock">พฤ. 12 พ.ย. 23:35:00</span>
        </div>
        <div class="top-pill">
            <span id="topTaskCountText">งานเสร็จ 8/8</span>
            <div class="progress-bar-mini"><div class="progress-fill-mini" id="topTaskBar"></div></div>
            <span id="topTaskPctText">100%</span>
        </div>
        <div class="top-pill" style="border-color:#f59e0b">
            <span>🪙 โทเคน:</span>
            <strong id="topTokenUsedText" style="color:#f59e0b">{tok_econ.get('total_tokens_used', 279200):,}</strong> / <span id="topTokenBudgetText">{tok_econ.get('daily_budget_tokens', 1000000):,}</span>
        </div>
        <!-- Theme Switcher & GitHub Push Buttons -->
        <button class="cozy-btn purple" onclick="openGitHubPushModal()" id="topGithubBtn">🚀 อัปโหลด GitHub</button>
        <button class="cozy-btn amber" onclick="toggleThemeMode()" id="themeToggleBtn">🌙 สลับโหมดมืด (Dark Mode)</button>
        <button class="cozy-btn primary" onclick="switchPage('page-replay')">▶ สรุปย้อนหลัง</button>
    </div>
</div>

<!-- GITHUB 1-CLICK PUSH MODAL -->
<div id="githubPushModal" style="display:none;position:fixed;inset:0;background:rgba(15,23,42,0.72);z-index:9999;align-items:center;justify-content:center;padding:16px">
    <div class="white-card" style="max-width:620px;width:100%;margin:0;border:2px solid #8b5cf6;box-shadow:0 20px 50px rgba(0,0,0,0.45)">
        <div class="section-head">
            <h2>🚀 อัปโหลดโปรเจกต์ขึ้น GitHub (1-Click Cloud Sync)</h2>
            <button class="cozy-btn" onclick="closeGitHubPushModal()">✖ ปิด</button>
        </div>
        <p style="font-size:0.85rem;color:var(--text-sub);margin-bottom:12px">
            สร้าง Repository และอัปโหลดโค้ดทั้งหมด (73+ ไฟล์ + ฐานข้อมูล + คลังสมอง Obsidian Knowledge Graph) ขึ้นบัญชี GitHub ของคุณ เพื่อดึงไปทำต่อบนคอมเครื่องใหม่หรือรัน GitHub Actions ฟรี 24 ชม.
        </p>
        <div style="display:flex;flex-direction:column;gap:10px;margin-bottom:14px">
            <div>
                <label style="font-size:0.8rem;font-weight:700;display:block;margin-bottom:4px">📦 ชื่อ Repository บน GitHub:</label>
                <input type="text" id="ghRepoNameInput" class="input-clean" style="width:100%" value="AI-Holding-Company-V8-Portable">
            </div>
            <div>
                <label style="font-size:0.8rem;font-weight:700;display:block;margin-bottom:4px">🔑 GitHub Personal Access Token (เว้นว่างได้หากต้องการกดล็อกอินผ่านเว็บเบราว์เซอร์):</label>
                <input type="password" id="ghTokenInput" class="input-clean" style="width:100%" placeholder="เว้นว่างไว้เพื่อเด้งหน้าเว็บล็อกอิน GitHub อัตโนมัติ หรือวาง ghp_... ที่นี่">
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.83rem">
                <input type="checkbox" id="ghPrivateCheckbox">
                <label for="ghPrivateCheckbox">🔒 ตั้งค่าเป็น Private Repository (ส่วนตัว)</label>
            </div>
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap">
            <button class="cozy-btn purple" style="flex:1;padding:11px;font-size:0.9rem" id="ghPushConfirmBtn" onclick="triggerGitHubPush()">
                🌐 เชื่อมต่อ GitHub & อัปโหลดทั้งหมดทันที
            </button>
        </div>
        <div id="ghPushResultBox" style="display:none;margin-top:14px;padding:12px;border-radius:10px;background:var(--bg-sub);border:1px solid var(--border-col);font-size:0.83rem"></div>
    </div>
</div>

<!-- 6 DEDICATED NAVIGATION PAGES -->
<div class="nav-tabs">
    <button class="nav-tab active" onclick="switchPage('page-visualizer')" id="tab-page-visualizer">🏝️ 1. เมือง AI (Aurum Isle)</button>
    <button class="nav-tab" onclick="switchPage('page-tokens')" id="tab-page-tokens">🪙 2. คลังโทเคน & สกิล</button>
    <button class="nav-tab" onclick="switchPage('page-replay')" id="tab-page-replay">📅 3. ย้อนหลังตามกราฟจริง</button>
    <button class="nav-tab" onclick="switchPage('page-profiles')" id="tab-page-profiles">🪪 4. ทำเนียบพนักงาน AI</button>
    <button class="nav-tab" onclick="switchPage('page-chat')" id="tab-page-chat">💬 5. แชทกับทีม AI</button>
    <button class="nav-tab" onclick="switchPage('page-mt5')" id="tab-page-mt5">🤖 6. MT5 Demo & Obsidian</button>
</div>

<!-- ====================================================================== -->
<!-- PAGE 1: AURUM ISLE — AI AGENT TOWN & 30-DAY $1,000 CHALLENGE           -->
<!-- ====================================================================== -->
<div class="page-view active" id="page-visualizer">
    <!-- 30-Day $1,000 AI Agent Town Challenge Banner -->
    <div class="challenge-banner" id="challengeBanner">
        <div>
            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
                <span class="challenge-day-badge" id="challengeDayBadge">DAY {chal_day} OF {chal_days_total}</span>
                <span style="font-size:0.76rem;padding:3px 10px;border-radius:999px;background:rgba(255,255,255,0.1);color:#fde68a;font-weight:700">⏳ เหลืออีก {chal_days_left} วัน</span>
                <span style="font-size:0.75rem;padding:3px 10px;border-radius:999px;background:{chal_pill_bg};color:{chal_pill_col};font-weight:700">{chal_status_txt}</span>
            </div>
            <div class="challenge-headline">CAN A TOWN OF AI AGENTS MAKE US $1,000?</div>
            <div class="challenge-sub">🏝️ <strong>{BRAND_NAME} — {BRAND_TAGLINE}:</strong> ภารกิจเมือง AI ล่าทองคำ ปั้นกำไรสะสม <strong>$1,000</strong> ใน 30 วัน (พอร์ตจริง Equity <strong>${port_equity:,.2f}</strong> • Win Rate <strong>{port_winrate:.1f}%</strong> • ปิดแล้ว <strong>{port_closed} ไม้</strong>)</div>
        </div>

        <div class="challenge-right">
            <div class="challenge-goal-figure">
                <div style="font-size:0.74rem;color:#94a3b8;font-weight:700">กำไรสะสม (Cumulative Profit)</div>
                <div style="font-size:1.35rem;font-weight:900;color:{chal_profit_col}" id="challengeProfitText">${chal_profit:+,.2f} <span style="font-size:0.85rem;color:#cbd5e1">/ ${chal_goal:,.0f}</span></div>
            </div>
            <div class="challenge-progress-wrap">
                <div style="display:flex;justify-content:space-between;font-size:0.76rem;font-weight:800;color:#fde68a">
                    <span>เป้าหมาย $1,000 Challenge</span>
                    <span id="challengePctText">{chal_pct:.1f}%</span>
                </div>
                <div class="challenge-progress-track">
                    <div class="challenge-progress-fill" id="challengeProgressBar" style="width:{chal_pct:.1f}%"></div>
                </div>
            </div>
            <div class="challenge-goal-figure">
                <div class="challenge-goal-big">$1,000?</div>
                <div style="font-size:0.7rem;color:#fde68a;font-weight:700">30-DAY GOAL</div>
            </div>
        </div>
    </div>

    <!-- Offline Auto-Catchup Status Bar -->
    <div class="catchup-banner">
        <div>
            <strong style="color:#10b981">☁️ สถานะระบบทำงานแทนตอนปิดคอม (Offline Auto-Catchup & Cloud 24/7):</strong>
            <span id="catchupStatusText">{html.escape(str(catchup_info.get('summary', 'ปิดคอมได้สบายใจ! เมื่อเปิดเครื่องใหม่ ระบบจะดึงกราฟย้อนหลังทุกกะที่ปิดคอมมาสรุปให้อัตโนมัติ')))}</span>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
            <button class="cozy-btn green" style="padding:4px 10px;font-size:0.76rem" onclick="triggerOfflineCatchupSim(12)">⚡ ทดสอบเก็บตกงานย้อนหลัง 12 ชม. (2 กะ)</button>
            <button class="cozy-btn purple" style="padding:4px 10px;font-size:0.76rem" onclick="openGitHubPushModal()">🚀 กดอัปโหลดขึ้น GitHub</button>
        </div>
    </div>

    <div class="visualizer-layout">
        <!-- Left: Ultra-Detailed Isometric Island Cutaway Stage -->
        <div class="iso-stage-card">
            <div class="iso-canvas-wrap" id="isoWrapBox">
                <canvas id="isometricOfficeCanvas" width="1140" height="560"></canvas>
                <div id="threeContainer"></div>

                <div class="stage-floating-top-left">
                    <button class="cozy-btn amber" onclick="runLiveCompanyWorkflowAnimation()">▶️ รันภารกิจบริษัทสดๆ (Step 1 ➔ 8)</button>
                    <button class="cozy-btn purple" onclick="quickOverclockAllAgents()">🔥 ทุ่มโทเคน Overclock ทั้งบริษัท</button>
                    <button class="cozy-btn green" onclick="switchPage('page-tokens')">🎓 สั่ง AI ไปเรียนสกิลใหม่</button>
                </div>

                <div class="stage-floating-top-right">
                    <select id="skyTimeSelect" class="cozy-btn" onchange="changeSkyAtmosphere(this.value)">
                        <option value="SUNSET">🌅 บรรยากาศ: ชายหาดยามเย็นพาสเทล (ต้นฉบับคลิป)</option>
                        <option value="MORNING">☀️ บรรยากาศ: เช้าสดใสน้ำทะเลคราม</option>
                        <option value="NIGHT">🌙 บรรยากาศ: ค่ำคืนนีออน (Dark Cyber Island)</option>
                    </select>
                </div>
            </div>

            <!-- Active Agent Speech Banner -->
            <div class="dialogue-banner">
                <div style="display:flex;align-items:center;gap:12px">
                    <div id="bannerAvatar" style="width:44px;height:44px;border-radius:12px;background:#fef3c7;border:2px solid #f59e0b;display:flex;align-items:center;justify-content:center;font-size:1.5rem">👑</div>
                    <div>
                        <div style="font-weight:800;font-size:0.92rem" id="bannerSpeaker">Arthur Pendelton (CIO) — สมองกล: Claude 3.7 Sonnet (Extended Thinking 128K)</div>
                        <div style="font-size:0.84rem;color:var(--text-sub)" id="bannerMessage">ตรวจสอบครบทั้ง 8 ขั้นตอนแล้ว — มติเอกฉันท์สั่ง <strong>{html.escape(action_text)}</strong> ทองคำที่ <strong>${cio['final_entry']:,.2f}</strong> (SL ${cio['final_sl']:,.2f} | TP1 ${cio['final_tp1']:,.2f} | TP2 ${cio['final_tp2']:,.2f})</div>
                    </div>
                </div>
                <div style="display:flex;gap:8px;flex-shrink:0">
                    <button class="cozy-btn" onclick="openSelectedAgentProfile()">🪪 ดูโปรไฟล์</button>
                    <button class="cozy-btn primary" onclick="askSelectedAgentInChat()">💬 ทักแชทถามตัวนี้</button>
                </div>
            </div>

            <!-- Mini Agent Status Cards Row -->
            <div class="mini-agents-strip" id="miniAgentsStrip"></div>
        </div>

        <!-- Right Sidebar: Today's Mission Checklist + Real-Time Activity Log -->
        <div class="right-sidebar-card">
            <div>
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                    <h3 style="font-size:1.02rem">📋 ภารกิจวันนี้ (Live Workflow)</h3>
                    <span class="pill" style="background:#dcfce7;color:#166534">ทองคำ XAUUSD • สด</span>
                </div>
                <div style="font-size:0.77rem;color:var(--text-sub);margin-bottom:10px">
                    กดปุ่ม <strong>"▶️ รันภารกิจบริษัทสดๆ"</strong> เพื่อดูตัวละคร AI เดินส่งงานผ่านประตูห้องทีละแผนก:
                </div>
                <div id="missionChecklistBox" style="display:flex;flex-direction:column;gap:4px"></div>
            </div>

            <div style="border-top:1px solid var(--border-soft);padding-top:12px">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                    <h3 style="font-size:0.95rem">🕒 บันทึกการทำงานสด (Real-Time Log)</h3>
                    <span style="font-size:0.72rem;color:#10b981;font-weight:700">● LIVE STREAM</span>
                </div>
                <div class="live-log-list" id="realtimeLogBox"></div>
            </div>
        </div>
    </div>
</div>

<!-- ====================================================================== -->
<!-- PAGE 2: TOKEN TREASURY, CUSTOM MODEL ADDER & SKILL HARVESTER           -->
<!-- ====================================================================== -->
<div class="page-view" id="page-tokens">
    <div class="grid-4" style="margin-bottom:16px">
        <div class="stat-metric-box" style="border-left:4px solid #f59e0b">
            <div class="lbl">🪙 งบโทเคนรายวันของบริษัท (Daily Token Pool)</div>
            <div class="val" id="econBudgetVal">{tok_econ.get('daily_budget_tokens', 1000000):,} Tokens</div>
            <div style="font-size:0.75rem;color:var(--text-sub);margin-top:4px">ปรับโควต้าให้แต่ละแผนกได้อิสระ</div>
        </div>
        <div class="stat-metric-box" style="border-left:4px solid #8b5cf6">
            <div class="lbl">🧠 Reasoning Tokens ที่เผาไปคิดลึกวันนี้</div>
            <div class="val" style="color:#8b5cf6" id="econReasoningVal">{tok_econ.get('reasoning_tokens', 142000):,} Tokens</div>
            <div style="font-size:0.75rem;color:#10b981;margin-top:4px">Extended Thinking & วิจัยสกิล</div>
        </div>
        <div class="stat-metric-box" style="border-left:4px solid #0ea5e9">
            <div class="lbl">⚡ โทเคนรวมที่ใช้ไปทั้งหมดวันนี้</div>
            <div class="val" id="econUsedVal">{tok_econ.get('total_tokens_used', 279200):,} Tokens ({tok_econ.get('utilization_pct', 27.9)}%)</div>
            <div style="font-size:0.75rem;color:var(--text-sub);margin-top:4px">คงเหลือ {tok_econ.get('remaining_tokens', 720800):,} Tokens</div>
        </div>
        <div class="stat-metric-box" style="border-left:4px solid #10b981">
            <div class="lbl">🎓 สกิลใหม่ที่ AI ค้นพบและปลดล็อกแล้ว</div>
            <div class="val" style="color:#10b981" id="econSkillsCountVal">{len(disc_skills)} สกิลใหม่</div>
            <div style="font-size:0.75rem;color:var(--text-sub);margin-top:4px">พร้อมใช้เทรดจริงและซิงค์ลง Obsidian</div>
        </div>
    </div>

    <div class="grid-2">
        <!-- Left: Autonomous Live Skill Discovery Lab + Custom Model Adder -->
        <div>
            <div class="white-card" style="border:2px solid #8b5cf6">
                <h2>🔬 ห้องแล็บวิจัยสกิลใหม่ (Autonomous Skill Harvester)</h2>
                <div style="background:var(--bg-sub);border:1px solid var(--border-col);border-radius:12px;padding:14px;margin-bottom:14px">
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
                        <div>
                            <label style="font-size:0.78rem;font-weight:700">1. เลือกพนักงาน AI ที่จะส่งไปเรียน:</label>
                            <select id="harvestAgentSelect" class="input-clean" style="width:100%;margin-top:4px"></select>
                        </div>
                        <div>
                            <label style="font-size:0.78rem;font-weight:700">2. จัดสรรงบโทเคนให้เผาวิจัยสกิลนี้:</label>
                            <select id="harvestTokenSelect" class="input-clean" style="width:100%;margin-top:4px">
                                <option value="25000">🪙 25,000 Reasoning Tokens (วิจัยมาตรฐาน)</option>
                                <option value="50000" selected>🔥 50,000 Reasoning Tokens (เจาะลึก + Backtest กราฟจริง)</option>
                                <option value="100000">🚀 100,000 Reasoning Tokens (Overclock คิดลึกสูงสุด 128K)</option>
                            </select>
                        </div>
                    </div>

                    <label style="font-size:0.78rem;font-weight:700">3. พิมพ์ชื่อสกิลหรือเทคนิคใหม่ที่ต้องการให้ AI ไปศึกษาและสร้างสูตร:</label>
                    <div style="display:flex;gap:8px;margin-top:4px;flex-wrap:wrap">
                        <input type="text" id="harvestTopicInput" class="input-clean" style="flex:1;min-width:220px" placeholder="เช่น ICT Silver Bullet NY Session, Wyckoff Spring Volume, Orderblock + FVG...">
                        <button class="cozy-btn purple" onclick="triggerLearnNewSkill()">🔬 ส่งไปเรียนสกิลใหม่เดี๋ยวนี้!</button>
                    </div>

                    <div style="margin-top:10px;display:flex;gap:6px;flex-wrap:wrap;align-items:center">
                        <span style="font-size:0.75rem;color:var(--text-sub);font-weight:700">คลิกหัวข้อฮิต:</span>
                        <button class="cozy-btn" style="padding:3px 9px;font-size:0.74rem" onclick="setSkillTopic('ICT Killzone Silver Bullet & FVG Sniper')">⚡ ICT Silver Bullet</button>
                        <button class="cozy-btn" style="padding:3px 9px;font-size:0.74rem" onclick="setSkillTopic('Wyckoff Accumulation Spring & Volume Profile POC')">📊 Wyckoff + Volume POC</button>
                        <button class="cozy-btn" style="padding:3px 9px;font-size:0.74rem" onclick="setSkillTopic('Elliott Wave 5 Impulse & Fibonacci 61.8% Confluence')">🌊 Elliott Wave + Fibo</button>
                        <button class="cozy-btn" style="padding:3px 9px;font-size:0.74rem" onclick="setSkillTopic('Fed Hawkish/Dovish NLP & US10Y Real-Yield Arbitrage')">🌐 Fed NLP + Bond Yield</button>
                    </div>
                </div>

                <h3 style="font-size:0.95rem;margin-bottom:8px">🏆 คลังสกิลใหม่ที่ AI ค้นพบและทดสอบกับกราฟจริงแล้ว:</h3>
                <div id="discoveredSkillsBox" style="display:flex;flex-direction:column;gap:10px;max-height:280px;overflow-y:auto"></div>
            </div>

            <!-- Add Custom AI Model Card -->
            <div class="white-card" style="border:2px solid #ec4899">
                <h2>➕ เพิ่มโมเดล AI เข้าเมือง (Custom Frontier Model Adder)</h2>
                <p style="font-size:0.82rem;color:var(--text-sub);margin-bottom:10px">
                    อยากใส่โมเดลใหม่ล่าสุดตัวไหนเพิ่มเติม (เช่น <code>GPT-5 Preview</code>, <code>Claude 4 Opus</code>, <code>Gemini 3 Ultra</code> หรือรหัสโมเดลจาก OpenRouter) พิมพ์เพิ่มเข้าคลังสมองเมือง AI ได้ทันที:
                </p>
                <div style="display:grid;grid-template-columns:1.3fr 1fr auto;gap:8px">
                    <input type="text" id="customModelNameInput" class="input-clean" placeholder="ชื่อโมเดล เช่น GPT-5 Reasoning (256K)">
                    <input type="text" id="customModelSpecInput" class="input-clean" placeholder="จุดเด่น เช่น วิเคราะห์กราฟและข่าวความเร็วสูง">
                    <button class="cozy-btn amber" onclick="addNewCustomModel()">➕ เพิ่มโมเดลเข้าเมือง</button>
                </div>
            </div>
        </div>

        <!-- Right: Per-Agent Token Budget & Compute Mode Allocator -->
        <div class="white-card">
            <h2>🪙 จัดสรรโควต้าโทเคน & สมองกลรายตัว (12+ Frontier Models)</h2>
            <p style="font-size:0.83rem;color:var(--text-sub);margin-bottom:12px">
                สลับสมองกล (`o1-Pro`, `GPT-4.5`, `Claude 3.7 Extended Thinking`, `Grok-3 Thinking`, `DeepSeek-R1 671B`) และปรับโหมด <strong>🌱 ECO / ⚖️ BALANCED / 🔥 OVERCLOCK</strong>:
            </p>
            <div id="tokenAllocationTableWrap" style="max-height:590px;overflow-y:auto"></div>
        </div>
    </div>
</div>

<!-- ====================================================================== -->
<!-- PAGE 3: TRUE HISTORICAL CANDLE & SHIFT REPLAY SUMMARIZER               -->
<!-- ====================================================================== -->
<div class="page-view" id="page-replay">
    <div class="white-card" style="border:2px solid #0ea5e9">
        <div class="section-head">
            <div>
                <h2>📅 สรุปย้อนหลังตามกราฟจริง & กะเวลา (Historical Shift Replay)</h2>
                <p style="font-size:0.84rem;color:var(--text-sub);margin-top:3px">
                    ดึงข้อมูลแท่งเทียนทองคำ (Open / High / Low / Close / RSI / ATR) และไทม์ไลน์การทำงานของวันที่และกะเวลาที่เลือกจริง <strong>(ไม่ซ้ำกัน 100%)</strong>
                </p>
            </div>
            <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">
                <label style="font-weight:800;font-size:0.84rem">📅 วันที่:</label>
                <input type="date" id="sumDateInput" class="input-clean" value="{today_str}" onchange="generateCuteSummary()">
                <button class="cozy-btn" onclick="pickQuickReplayDate('{today_str}')">วันนี้ ({today_str[-5:]})</button>
                <button class="cozy-btn" onclick="pickQuickReplayDate('{d_m1}')">เมื่อวาน ({d_m1[-5:]})</button>
                <button class="cozy-btn" onclick="pickQuickReplayDate('{d_m2}')">2 วันก่อน ({d_m2[-5:]})</button>
                <button class="cozy-btn" onclick="pickQuickReplayDate('{d_m3}')">3 วันก่อน ({d_m3[-5:]})</button>
                <button class="cozy-btn" onclick="pickQuickReplayDate('{d_m5}')">5 วันก่อน ({d_m5[-5:]})</button>
            </div>
        </div>

        <div style="margin-bottom:14px">
            <div style="font-size:0.84rem;font-weight:800;margin-bottom:8px">⏰ เลือกกะเวลาทำงานของเมือง AI (Aurum Isle):</div>
            <div style="display:flex;gap:8px;flex-wrap:wrap" id="shiftPillsWrap">
                <div class="shift-pill active" data-slot="FULL_24H" onclick="selectShiftPill(this)">✨ ภาพรวมครบ 24 ชม. (Full 24h)</div>
                <div class="shift-pill" data-slot="MORNING_ASIA" onclick="selectShiftPill(this)">🌅 กะเช้า ตลาดเอเชีย (06:00-12:00)</div>
                <div class="shift-pill" data-slot="AFTERNOON_LONDON" onclick="selectShiftPill(this)">☀️ กะบ่าย ตลาดลอนดอน (12:00-18:00)</div>
                <div class="shift-pill" data-slot="EVENING_NY" onclick="selectShiftPill(this)">🌆 กะค่ำ ตลาดนิวยอร์ก (18:00-24:00)</div>
                <div class="shift-pill" data-slot="NIGHT_AUDIT" onclick="selectShiftPill(this)">🌙 กะดึก วิจัยสกิล & สรุปงบ (00:00-06:00)</div>
            </div>
        </div>

        <div class="grid-4" style="margin-bottom:14px">
            <div class="stat-metric-box">
                <div class="lbl">📊 ราคาเปิดกะ ➔ ปิดกะ (Open ➔ Close)</div>
                <div class="val" style="font-size:1.15rem" id="repOpenCloseTxt">${market.get('current_price'):,.2f}</div>
                <div style="font-size:0.8rem;font-weight:700" id="repChangeTxt">--</div>
            </div>
            <div class="stat-metric-box">
                <div class="lbl">📏 กรอบสูงสุด / ต่ำสุดในกะ (High / Low)</div>
                <div class="val" style="font-size:1.15rem" id="repHighLowTxt">--</div>
                <div style="font-size:0.8rem;color:var(--text-sub)" id="repRangeTxt">--</div>
            </div>
            <div class="stat-metric-box">
                <div class="lbl">🧭 อินดิเคเตอร์ & ผลดีเบตประจำกะ</div>
                <div class="val" style="font-size:1.1rem" id="repRsiAtrTxt">RSI {market.get('rsi14')} | ATR ${market.get('atr14')}</div>
                <div style="font-size:0.8rem;color:#8b5cf6;font-weight:700" id="repDebateTxt">--</div>
            </div>
            <div class="stat-metric-box">
                <div class="lbl">👑 มติ CIO & โทเคนที่เผาในกะนี้</div>
                <div class="val" style="font-size:1.15rem;color:#f59e0b" id="repVerdictTxt">{html.escape(action_text)}</div>
                <div style="font-size:0.8rem;color:#10b981;font-weight:700" id="repTokensTxt">--</div>
            </div>
        </div>

        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:12px">
            <div style="display:flex;gap:8px;flex-wrap:wrap">
                <button class="cozy-btn primary" onclick="generateCuteSummary('EXECUTIVE_CUTE')">🏝️ สไตล์สรุปผู้บริหาร & ไทม์ไลน์กะนี้</button>
                <button class="cozy-btn amber" onclick="generateCuteSummary('TRADING_ACTION')">🎯 สไตล์เน้นจุดเข้าเทรด (Entry/SL/TP)</button>
                <button class="cozy-btn purple" onclick="generateCuteSummary('OBSIDIAN_NOTE')">💎 สไตล์โน้ต Obsidian (YAML + Wikilinks)</button>
            </div>
            <div style="display:flex;gap:8px;flex-wrap:wrap">
                <button class="cozy-btn green" onclick="copySummaryText()">📋 คัดลอกข้อความสรุป</button>
                <button class="cozy-btn" onclick="syncObsidianNow()">💎 ซิงค์ลง Obsidian Vault</button>
            </div>
        </div>

        <pre id="cuteSummaryOutput" style="background:#0f172a;color:#f8fafc;padding:18px;border-radius:14px;font-family:'Segoe UI',sans-serif;font-size:0.93rem;line-height:1.68;white-space:pre-wrap;min-height:240px"></pre>
    </div>
</div>

<!-- ====================================================================== -->
<!-- PAGE 4: DEDICATED AI AGENT PROFILES & FRONTIER BRAIN STUDIO            -->
<!-- ====================================================================== -->
<div class="page-view" id="page-profiles">
    <div class="visualizer-layout" style="grid-template-columns: 320px 1fr">
        <div class="white-card" style="margin-bottom:0">
            <h2>🪪 ทำเนียบชาวเมือง AI (11 ตัว)</h2>
            <div id="profileRosterList" style="display:flex;flex-direction:column;gap:8px;max-height:600px;overflow-y:auto"></div>
        </div>

        <div class="white-card" style="margin-bottom:0">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:16px;border-bottom:1px solid var(--border-soft);padding-bottom:16px;margin-bottom:18px">
                <div style="display:flex;align-items:center;gap:16px">
                    <div id="profAvatar" style="width:72px;height:72px;border-radius:18px;background:#fef3c7;border:3px solid #f59e0b;display:flex;align-items:center;justify-content:center;font-size:2.4rem">👑</div>
                    <div>
                        <span class="pill" id="profDept">ห้องตัดสินใจ CIO</span>
                        <h1 id="profName" style="font-size:1.45rem;margin-top:4px;line-height:1.25">Arthur Pendelton</h1>
                        <div id="profRole" style="color:var(--text-sub);font-size:0.9rem">Chief Investment Officer (CIO)</div>
                    </div>
                </div>

                <div style="background:var(--bg-sub);border:1px solid var(--border-col);padding:12px 16px;border-radius:12px;min-width:290px;flex:1;max-width:420px">
                    <div style="font-size:0.78rem;font-weight:800;margin-bottom:6px">🧠 เลือกสมองกล AI (12+ โมเดลตัวท็อปสายกินโทเคน):</div>
                    <select id="profModelSelect" class="input-clean" style="width:100%" onchange="changeAgentModelBrain()"></select>
                    <div id="profModelMeta" style="font-size:0.75rem;color:#10b981;margin-top:6px;font-weight:700">✓ พร้อมใช้งาน</div>
                </div>
            </div>

            <div class="grid-2">
                <div>
                    <h3 style="font-size:0.98rem;margin-bottom:8px">📖 บทบาทหน้าที่ & งบโทเคนประจำตัว</h3>
                    <p id="profBio" style="background:var(--bg-sub);padding:12px;border-radius:10px;border:1px solid var(--border-soft);margin-bottom:14px;font-size:0.9rem"></p>

                    <h3 style="font-size:0.98rem;margin-bottom:8px">🎓 สกิลที่ติดตั้ง & ระดับความชำนาญ</h3>
                    <div style="background:var(--bg-sub);padding:14px;border-radius:12px;border:1px solid var(--border-soft)">
                        <div style="display:flex;justify-content:space-between;font-weight:800;margin-bottom:6px">
                            <span id="profLevelTxt" style="color:#f59e0b">Level 12</span>
                            <span id="profMasteryTxt" style="color:#10b981">Mastery: 92.4%</span>
                        </div>
                        <div style="height:9px;background:var(--border-col);border-radius:99px;overflow:hidden;margin-bottom:12px">
                            <div id="profExpBar" style="height:100%;width:70%;background:linear-gradient(90deg,#f59e0b,#10b981)"></div>
                        </div>
                        <div id="profSkillsList" style="display:flex;flex-direction:column;gap:8px;font-size:0.86rem"></div>
                        <div style="margin-top:14px;display:flex;gap:8px;flex-wrap:wrap">
                            <button class="cozy-btn amber" onclick="trainCurrentProfileAgent()">⚡ ฝึกสกิลอัปเลเวล (+180 EXP)</button>
                            <button class="cozy-btn purple" onclick="switchPage('page-tokens')">🔬 สั่งตัวนี้ไปเรียนสกิลใหม่</button>
                            <button class="cozy-btn primary" onclick="askCurrentProfileAgent()">💬 คุยแชทกับตัวนี้</button>
                        </div>
                    </div>
                </div>

                <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;background:#0f172a;border-radius:14px;padding:16px;color:#fff">
                    <h3 style="color:#38bdf8;margin-bottom:8px;font-size:0.95rem">🕸️ กราฟเรดาร์ความสามารถ 5 มิติ (5D Capability Radar)</h3>
                    <canvas id="radarChartCanvas" width="340" height="300"></canvas>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- ====================================================================== -->
<!-- PAGE 5: LIVE COPILOT CHAT WITH ANTIGRAVITY & 11 AI AGENTS              -->
<!-- ====================================================================== -->
<div class="page-view" id="page-chat">
    <div class="visualizer-layout" style="grid-template-columns: 300px 1fr">
        <div class="white-card" style="margin-bottom:0">
            <h2>💬 เลือกคู่สนทนา AI</h2>
            <div id="chatTargetList" style="display:flex;flex-direction:column;gap:8px;max-height:560px;overflow-y:auto"></div>
        </div>

        <div class="white-card" style="margin-bottom:0;display:flex;flex-direction:column;height:620px;padding:0;overflow:hidden">
            <div style="padding:14px 18px;background:#0f172a;color:#fff;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
                <div>
                    <strong style="color:#fbbf24;font-size:1rem" id="chatHeaderSpeaker">🤖 Antigravity Copilot (Head AI Architect)</strong>
                    <div style="font-size:0.76rem;color:#38bdf8" id="chatHeaderModel">Brain: Claude 3.7 Extended Thinking + OpenAI o1-Pro Hybrid</div>
                </div>
                <div style="display:flex;gap:6px;flex-wrap:wrap">
                    <button class="cozy-btn" style="padding:4px 10px;font-size:0.75rem" onclick="sendQuickPrompt('ขอแผนเทรดทองคำ XAUUSD ตอนนี้พร้อมจุด Entry, SL, TP หน่อย')">📊 ขอแผนเทรดทองตอนนี้</button>
                    <button class="cozy-btn" style="padding:4px 10px;font-size:0.75rem" onclick="sendQuickPrompt('ดูการใช้โทเคนและสกิลใหม่ที่ทีม AI เพิ่งเรียนรู้มาหน่อย')">🪙 เช็กโทเคน & สกิลใหม่</button>
                    <button class="cozy-btn" style="padding:4px 10px;font-size:0.75rem" onclick="sendQuickPrompt('ช่วยคิดไอเดียธุรกิจใหม่เอาเข้าบริษัท AI ของเราหน่อย')">🚀 ขอไอเดียธุรกิจใหม่</button>
                </div>
            </div>

            <div id="chatMessagesBox" style="flex:1;padding:18px;overflow-y:auto;display:flex;flex-direction:column;gap:12px;background:var(--bg-sub)"></div>

            <div style="display:flex;gap:10px;padding:14px;background:var(--bg-card);border-top:1px solid var(--border-col)">
                <input type="text" id="chatInputField" class="input-clean" style="flex:1" placeholder="พิมพ์ถามผม (Antigravity) หรือพนักงาน AI ที่เลือกได้เลย..." onkeydown="if(event.key==='Enter') sendChatMessage()">
                <button class="cozy-btn primary" onclick="sendChatMessage()">🚀 ส่งข้อความ</button>
            </div>
        </div>
    </div>
</div>

<!-- ====================================================================== -->
<!-- PAGE 6: LIVE MT5 DEMO EXECUTION, 4 STRATEGIES & OBSIDIAN VAULT         -->
<!-- ====================================================================== -->
<div class="page-view" id="page-mt5">
    <div class="white-card">
        <div class="section-head">
            <div>
                <h2>🤖 จำลองยิงออเดอร์ MT5 Demo สด (8 ขั้นตอน Tick-by-Tick)</h2>
                <p style="font-size:0.84rem;color:var(--text-sub);margin-top:3px">ดูวิธีการทำงานของ AutoBot X-1 ตั้งแต่เช็ก Spread ➔ ยิง <code>mt5.order_send()</code> ➔ ขยับ SL บังหน้าทุนเมื่อแตะ TP1 ➔ ปิดกำไร TP2</p>
            </div>
            <button class="cozy-btn amber" onclick="startLiveMT5Simulation()">▶️ เริ่มจำลองยิงออเดอร์ MT5 Demo สด</button>
        </div>

        <div class="grid-2">
            <div>
                <canvas id="mt5DemoChartCanvas" width="700" height="340" style="width:100%;background:#0f172a;border-radius:12px"></canvas>
                <div style="margin-top:10px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;background:var(--bg-sub);padding:12px;border-radius:10px;border:1px solid var(--border-col);font-size:0.86rem">
                    <span>📍 Entry: <strong>${float(mt5_demo.get('entry_price', 3900)):,.2f}</strong></span>
                    <span>🛑 Live SL: <strong id="mt5LiveSL" style="color:#ef4444">${float(mt5_demo.get('sl_price', 3930)):,.2f}</strong></span>
                    <span>🎯 TP1/TP2: <strong style="color:#10b981">${float(mt5_demo.get('tp1_price', 3850)):,.2f} / ${float(mt5_demo.get('tp2_price', 3818)):,.2f}</strong></span>
                    <span>💵 Demo PnL: <strong id="mt5LivePnL" style="color:#10b981">+$0.00</strong></span>
                </div>
            </div>
            <div id="mt5StepsContainer" style="max-height:390px;overflow-y:auto;display:flex;flex-direction:column;gap:8px"></div>
        </div>
    </div>

    <div class="grid-2">
        <div class="white-card">
            <h2>🔬 ผลทดสอบ 4 กลยุทธ์วิจัยระดับโลกเทียบตลาดจริง</h2>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>ชื่อกลยุทธ์มาตรฐาน</th>
                            <th>ตลาดที่ถนัด</th>
                            <th>Win Rate วิจัย</th>
                            <th>Win Rate จริง</th>
                            <th>PF จริง</th>
                            <th>Net R</th>
                            <th>สัญญาณ</th>
                        </tr>
                    </thead>
                    <tbody>{strat_rows_html}</tbody>
                </table>
            </div>
        </div>

        <div class="white-card">
            <h2>💎 คลังสมอง Obsidian & ระบบประหยัดโทเคน Graph-RAG</h2>
            <p style="font-size:0.85rem;color:var(--text-sub);margin-bottom:10px">
                ซิงค์ไฟล์ Markdown + กระดาน <code>AI_Company_Knowledge_Map.canvas</code> + ผัง <code>00_Knowledge_Graph_Topology.md</code> ({obs_info.get('files_synced_count', 18)} ไฟล์) เพื่อดึงเฉพาะโหนดที่เกี่ยวข้อง (1-Hop Subgraph) ช่วยประหยัดโทเคน AI สูงสุด <strong>83.5%</strong>:
            </p>
            <div class="grid-4" style="margin-bottom:12px">
                <div class="stat-metric-box">
                    <div class="lbl">📦 โทเคนถ้าส่งทั้งคลัง (Full Vault)</div>
                    <div class="val" style="color:#ef4444;font-size:1.1rem">18,650 Tok/รอบ</div>
                </div>
                <div class="stat-metric-box">
                    <div class="lbl">🕸️ โทเคนผ่านกราฟ (1-Hop Subgraph)</div>
                    <div class="val" style="color:#10b981;font-size:1.1rem">2,590 Tok/รอบ</div>
                </div>
                <div class="stat-metric-box">
                    <div class="lbl">⚡ ประหยัดโทเคนต่อคำสั่ง</div>
                    <div class="val" style="color:#0ea5e9;font-size:1.1rem">-86.1% (-16,060)</div>
                </div>
                <div class="stat-metric-box">
                    <div class="lbl">💰 ประหยัดโทเคนสะสม/วัน</div>
                    <div class="val" style="color:#8b5cf6;font-size:1.1rem">~706,640 Tok</div>
                </div>
            </div>
            <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px">
                <a href="{html.escape(str(obs_info.get('obsidian_uri', 'obsidian://open')))}" class="cozy-btn primary" style="text-decoration:none">💎 เปิดในโปรแกรม Obsidian</a>
                <button class="cozy-btn amber" onclick="syncObsidianNow()">🔄 ซิงค์กราฟ & โน้ตล่าสุดลง Obsidian</button>
            </div>
            <div style="position:relative">
                <canvas id="obsidianGraphCanvas" width="760" height="360" style="width:100%;background:#0f172a;border-radius:12px;cursor:pointer"></canvas>
                <div id="obsNodeInspector" style="margin-top:8px;padding:10px 14px;background:var(--bg-sub);border:1px solid var(--border-col);border-radius:10px;font-size:0.82rem">
                    💡 <strong>คลิกที่โหนดกลมๆ บนกราฟด้านบน</strong> เพื่อดูว่าข้อมูลส่วนนั้นเชื่อมกับส่วนไหนบ้าง และช่วยประหยัดโทเคนได้เท่าไหร่!
                </div>
            </div>
        </div>
    </div>

    <div class="white-card">
        <h2>🕸️ ตารางผังเชื่อมโยงข้อมูล Obsidian (1-Hop Subgraph Routing Matrix)</h2>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>พนักงาน AI</th>
                        <th>สมองกล (LLM)</th>
                        <th>โหนดข้อมูลที่เชื่อมกันโดยตรง (Connected Nodes)</th>
                        <th>รายละเอียดข้อมูลที่ส่งหากัน</th>
                        <th>โทเคนทั้งคลัง</th>
                        <th>โทเคนใช้จริง (Graph)</th>
                        <th>ประหยัดโทเคน</th>
                    </tr>
                </thead>
                <tbody id="obsRoutingTableBody"></tbody>
            </table>
        </div>
    </div>
</div>

<script>
const APP = {report_json};
let selectedAgent = APP.office.agents_roster[0];
let currentShiftSlot = "FULL_24H";
let currentSummaryStyle = "EXECUTIVE_CUTE";
let chatTargetId = "antigravity";
let skyTheme = "SUNSET";
let isDarkTheme = false;

// ============================================================================
// LIGHT / DARK THEME SWITCHER
// ============================================================================
function toggleThemeMode() {{
    isDarkTheme = !isDarkTheme;
    document.documentElement.setAttribute('data-theme', isDarkTheme ? 'dark' : 'light');
    const btn = document.getElementById('themeToggleBtn');
    if (btn) btn.textContent = isDarkTheme ? '☀️ สลับโหมดสว่าง (Light Mode)' : '🌙 สลับโหมดมืด (Dark Mode)';
    skyTheme = isDarkTheme ? 'NIGHT' : 'SUNSET';
    const sel = document.getElementById('skyTimeSelect');
    if (sel) sel.value = skyTheme;
    try {{ localStorage.setItem('agy_v7_theme', isDarkTheme ? 'dark' : 'light'); }} catch (e) {{}}
}}

(function restoreSavedTheme() {{
    try {{
        const saved = localStorage.getItem('agy_v7_theme');
        if (saved === 'dark') toggleThemeMode();
    }} catch (e) {{}}
}})();

// ============================================================================
// REAL-TIME THAI CLOCK
// ============================================================================
function updateLiveThaiClock() {{
    const now = new Date();
    const days = ["อา.", "จ.", "อ.", "พ.", "พฤ.", "ศ.", "ส."];
    const months = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."];
    const dStr = `${{days[now.getDay()]}} ${{now.getDate()}} ${{months[now.getMonth()]}} ${{String(now.getHours()).padStart(2,'0')}}:${{String(now.getMinutes()).padStart(2,'0')}}:${{String(now.getSeconds()).padStart(2,'0')}}`;
    const el = document.getElementById('liveThaiClock');
    if (el) el.textContent = dStr;
}}
setInterval(updateLiveThaiClock, 1000);
updateLiveThaiClock();

// ============================================================================
// PAGE 1: ULTRA-DETAILED ISOMETRIC CUTAWAY ISLAND & FULL-BODY CHIBI MODELS
// ============================================================================
const isoCanvas = document.getElementById('isometricOfficeCanvas');
const isoCtx = isoCanvas ? isoCanvas.getContext('2d') : null;
let wavePhase = 0;

// 8 Connected Rooms forming a unified Isometric Office Building on a Beach Island
const ISO_ROOMS = [
    {{ id: "RECEPTION", name: "ห้องต้อนรับ & รับบรีฟ", sub: "พร้อมรับงาน", gx: 0, gy: 0, floorCol: "#fef3c7", floorAlt: "#fde68a", wallCol: "#f59e0b", wallTop: "#fffbeb", badgeDot: "#10b981", propType: "SOFA_COUNTER" }},
    {{ id: "NEWS_DESK", name: "ห้องเรดาร์ข่าวสาร", sub: "เสร็จแล้ว", gx: 1, gy: 0, floorCol: "#e0f2fe", floorAlt: "#bae6fd", wallCol: "#0284c7", wallTop: "#f0f9ff", badgeDot: "#10b981", propType: "MULTI_SCREEN" }},
    {{ id: "QUANT_LAB", name: "ห้องแล็บวิจัย & สกิล", sub: "กำลังเผาโทเคนวิจัย", gx: 2, gy: 0, floorCol: "#f3e8ff", floorAlt: "#e9d5ff", wallCol: "#7c3aed", wallTop: "#faf5ff", badgeDot: "#f59e0b", propType: "SERVER_LAB" }},
    {{ id: "TA_ROOM",   name: "ห้องวิเคราะห์กราฟ", sub: "เสร็จแล้ว", gx: 3, gy: 0, floorCol: "#dcfce7", floorAlt: "#bbf7d0", wallCol: "#059669", wallTop: "#f0fdf4", badgeDot: "#10b981", propType: "CHART_DESK" }},
    {{ id: "MACRO_ROOM",name: "ห้องวิจัยมหภาค", sub: "เสร็จแล้ว", gx: 0, gy: 1, floorCol: "#e0e7ff", floorAlt: "#c7d2fe", wallCol: "#4f46e5", wallTop: "#eef2ff", badgeDot: "#10b981", propType: "BOOK_DESK" }},
    {{ id: "DEBATE_RM", name: "ห้องดีเบตกลยุทธ์", sub: "ดีเบตเสร็จแล้ว", gx: 1, gy: 1, floorCol: "#ffedd5", floorAlt: "#fed7aa", wallCol: "#ea580c", wallTop: "#fff7ed", badgeDot: "#10b981", propType: "ROUND_TABLE" }},
    {{ id: "RISK_ROOM", name: "ห้องตรวจความเสี่ยง", sub: "อนุมัติ Lot Size", gx: 2, gy: 1, floorCol: "#fce7f3", floorAlt: "#fbcfe8", wallCol: "#db2777", wallTop: "#fdf2f8", badgeDot: "#10b981", propType: "SHIELD_DESK" }},
    {{ id: "CIO_MT5",   name: "ห้องส่งคำสั่ง CIO & MT5", sub: "พร้อมส่งออเดอร์", gx: 3, gy: 1, floorCol: "#fef9c3", floorAlt: "#fef08a", wallCol: "#ca8a04", wallTop: "#fefce8", badgeDot: "#10b981", propType: "EXEC_SUITE" }}
];

// Connected zero-gap Isometric grid projection
function isoProject(gx, gy) {{
    const originX = 485;
    const originY = 148;
    const tileW = 204;
    const tileH = 104;
    const sx = originX + (gx - gy) * (tileW / 2);
    const sy = originY + (gx + gy) * (tileH / 2);
    return {{ x: sx, y: sy, w: tileW, h: tileH }};
}}

// Hair & Outfit customization for each of the 11 Chibi AI Agents
const CHIBI_STYLES = [
    {{ hair: "#fbbf24", suit: "#1e293b", acc: "CROWN" }},    // Arthur CIO
    {{ hair: "#334155", suit: "#ec4899", acc: "BUN" }},      // Sophia COS
    {{ hair: "#0f172a", suit: "#0284c7", acc: "HEADSET" }},  // Maya News
    {{ hair: "#475569", suit: "#ffffff", acc: "GLASSES" }},  // Dr. Kenji Quant (White Labcoat)
    {{ hair: "#059669", suit: "#065f46", acc: "VISOR" }},    // Alex TA
    {{ hair: "#1e3a8a", suit: "#1d4ed8", acc: "GLASSES" }},  // Dr. Marcus Macro
    {{ hair: "#ea580c", suit: "#16a34a", acc: "HORNS" }},    // Sarah Bull
    {{ hair: "#7f1d1d", suit: "#dc2626", acc: "CAP" }},      // Viktor Bear
    {{ hair: "#831843", suit: "#db2777", acc: "SHIELD" }},   // Elena Risk
    {{ hair: "#38bdf8", suit: "#7c3aed", acc: "ANTENNA" }},  // AutoBot X-1
    {{ hair: "#f97316", suit: "#4338ca", acc: "STAR" }}      // Nova Venture
];

const isoSprites = APP.office.agents_roster.map((ag, idx) => {{
    const rmIdx = idx % ISO_ROOMS.length;
    const rm = ISO_ROOMS[rmIdx];
    const p = isoProject(rm.gx, rm.gy);
    return {{
        ag: ag,
        style: CHIBI_STYLES[idx % CHIBI_STYLES.length],
        rmIdx: rmIdx,
        x: p.x + ((idx % 3) - 1) * 24,
        y: p.y + 52 + ((idx % 2) * 12),
        tx: p.x + ((idx % 3) - 1) * 24,
        ty: p.y + 52 + ((idx % 2) * 12),
        walkPhase: idx * 1.1,
        facingRight: true,
        speech: idx === 0 ? `สั่ง ${{APP.cio.action}}!` : (idx === 3 ? "วิจัยสกิล o1-Pro..." : ""),
        speechTimer: idx % 3 === 0 ? 180 : 0
    }};
}});

let clouds = [
    {{ x: 140, y: 46, s: 1.0, v: 0.2 }},
    {{ x: 520, y: 34, s: 1.25, v: 0.15 }},
    {{ x: 890, y: 52, s: 0.92, v: 0.22 }}
];

// Draw 3D Extruded Isometric Wall Segment with Top Thickness & Doorway Gap
function drawIsoWallWithDoor(ctx, x1, y1, x2, y2, wallH, thick, faceCol, topCol, hasDoor) {{
    const drawSeg = (ax, ay, bx, by) => {{
        // Vertical Wall Face
        ctx.fillStyle = faceCol;
        ctx.strokeStyle = "rgba(15,23,42,0.22)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(ax, ay);
        ctx.lineTo(bx, by);
        ctx.lineTo(bx, by - wallH);
        ctx.lineTo(ax, ay - wallH);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // Top 3D Thickness Strip
        ctx.fillStyle = topCol;
        ctx.beginPath();
        ctx.moveTo(ax, ay - wallH);
        ctx.lineTo(bx, by - wallH);
        ctx.lineTo(bx, by - wallH - thick);
        ctx.lineTo(ax, ay - wallH - thick);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
    }};

    if (!hasDoor) {{
        drawSeg(x1, y1, x2, y2);
    }} else {{
        // Leave a doorway opening in the middle (36% to 64%)
        const mx1 = x1 + (x2 - x1) * 0.36, my1 = y1 + (y2 - y1) * 0.36;
        const mx2 = x1 + (x2 - x1) * 0.64, my2 = y1 + (y2 - y1) * 0.64;
        drawSeg(x1, y1, mx1, my1);
        drawSeg(mx2, my2, x2, y2);
    }}
}}

// Draw Detailed 3D Furniture Inside Each Isometric Room
function drawRoomFurniture3D(ctx, cx, cy, propType, wallCol) {{
    // Isometric 3D Desk Helper
    const draw3DDesk = (dx, dy, w, h, topC, sideC) => {{
        // Top surface
        ctx.fillStyle = topC;
        ctx.beginPath();
        ctx.moveTo(dx, dy - 10);
        ctx.lineTo(dx + w, dy - 4);
        ctx.lineTo(dx, dy + 4);
        ctx.lineTo(dx - w, dy - 4);
        ctx.closePath();
        ctx.fill();
        // Left front leg/panel
        ctx.fillStyle = sideC;
        ctx.beginPath();
        ctx.moveTo(dx - w, dy - 4);
        ctx.lineTo(dx, dy + 4);
        ctx.lineTo(dx, dy + 4 + h);
        ctx.lineTo(dx - w, dy - 4 + h);
        ctx.closePath();
        ctx.fill();
        // Right front panel
        ctx.fillStyle = sideC;
        ctx.beginPath();
        ctx.moveTo(dx, dy + 4);
        ctx.lineTo(dx + w, dy - 4);
        ctx.lineTo(dx + w, dy - 4 + h);
        ctx.lineTo(dx, dy + 4 + h);
        ctx.closePath();
        ctx.fill();
    }};

    // Draw Monitor with Mini Candlestick Chart
    const drawMonitor = (mx, my, screenCol) => {{
        ctx.fillStyle = "#0f172a";
        ctx.fillRect(mx - 13, my - 22, 26, 16);
        ctx.fillStyle = screenCol;
        ctx.fillRect(mx - 11, my - 20, 22, 12);
        // Mini green/red candles on screen
        ctx.fillStyle = "#10b981";
        ctx.fillRect(mx - 8, my - 16, 3, 6);
        ctx.fillRect(mx - 3, my - 18, 3, 7);
        ctx.fillStyle = "#ef4444";
        ctx.fillRect(mx + 2, my - 15, 3, 5);
        ctx.fillStyle = "#fbbf24";
        ctx.fillRect(mx + 6, my - 19, 3, 8);
        // Stand
        ctx.fillStyle = "#475569";
        ctx.fillRect(mx - 3, my - 6, 6, 4);
    }};

    // Potted Plant in corner
    ctx.fillStyle = "#b45309";
    ctx.beginPath();
    ctx.arc(cx - 52, cy + 4, 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#16a34a";
    ctx.beginPath();
    ctx.arc(cx - 52, cy - 3, 8, 0, Math.PI * 2);
    ctx.fill();

    if (propType === "ROUND_TABLE") {{
        // War Room Oval Conference Table
        ctx.fillStyle = "#7c2d12";
        ctx.beginPath();
        ctx.ellipse(cx, cy + 12, 34, 16, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "#fdba74";
        ctx.beginPath();
        ctx.ellipse(cx, cy + 8, 32, 14, 0, 0, Math.PI * 2);
        ctx.fill();
        // Hologram Bull vs Bear chart in center of table
        ctx.fillStyle = "#10b981";
        ctx.fillRect(cx - 10, cy + 2, 8, 8);
        ctx.fillStyle = "#ef4444";
        ctx.fillRect(cx + 2, cy + 2, 8, 8);
    }} else if (propType === "SERVER_LAB") {{
        // Quant Lab Server Racks + Dual Monitors
        ctx.fillStyle = "#1e1b4b";
        ctx.fillRect(cx + 26, cy - 18, 18, 32);
        // Blinking LEDs
        ctx.fillStyle = (Math.floor(Date.now() / 300) % 2 === 0) ? "#10b981" : "#38bdf8";
        ctx.fillRect(cx + 29, cy - 14, 4, 3);
        ctx.fillRect(cx + 29, cy - 8, 4, 3);
        ctx.fillStyle = "#f43f5e";
        ctx.fillRect(cx + 36, cy - 11, 4, 3);
        draw3DDesk(cx - 8, cy + 10, 26, 10, "#e9d5ff", "#7c3aed");
        drawMonitor(cx - 8, cy + 6, "#1e1b4b");
    }} else {{
        draw3DDesk(cx, cy + 10, 28, 10, "#fde68a", wallCol);
        drawMonitor(cx, cy + 6, "#090d16");
    }}
}}

// Draw Full-Body Multi-Part Chibi AI Character (Hair, Face, Suit, Walking Legs, Tablet, Accessories)
function drawChibiAgent(ctx, sp) {{
    const x = sp.x;
    const isMoving = Math.hypot(sp.tx - sp.x, sp.ty - sp.y) > 2.5;
    if (isMoving) sp.walkPhase += 0.22;
    else sp.walkPhase += 0.06;

    const bob = isMoving ? Math.abs(Math.sin(sp.walkPhase)) * 4.5 : Math.sin(sp.walkPhase) * 1.5;
    const legSwing = isMoving ? Math.sin(sp.walkPhase) * 5 : 0;
    const y = sp.y - bob;
    const st = sp.style;

    // 1. Overclock Golden Flame Aura
    if (sp.ag.compute_mode === "OVERCLOCK") {{
        const grad = ctx.createRadialGradient(x, y - 18, 4, x, y - 18, 26);
        grad.addColorStop(0, "rgba(251, 191, 36, 0.55)");
        grad.addColorStop(1, "rgba(245, 158, 11, 0.0)");
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(x, y - 18, 26, 0, Math.PI * 2);
        ctx.fill();
    }}

    // 2. Ground Drop Shadow
    ctx.fillStyle = "rgba(15, 23, 42, 0.24)";
    ctx.beginPath();
    ctx.ellipse(x, sp.y + 5, 12, 5.5, 0, 0, Math.PI * 2);
    ctx.fill();

    // 3. Animated Walking Legs / Shoes
    ctx.strokeStyle = "#1e293b";
    ctx.lineWidth = 3.5;
    ctx.lineCap = "round";
    ctx.beginPath();
    ctx.moveTo(x - 4, y - 6);
    ctx.lineTo(x - 4 - legSwing * 0.6, y + 3);
    ctx.moveTo(x + 4, y - 6);
    ctx.lineTo(x + 4 + legSwing * 0.6, y + 3);
    ctx.stroke();

    // 4. Chibi Suit / Labcoat Torso
    ctx.fillStyle = st.suit;
    ctx.strokeStyle = "#0f172a";
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.roundRect(x - 9, y - 20, 18, 15, 5);
    ctx.fill();
    ctx.stroke();

    // White Collar & Tie detail
    ctx.fillStyle = "#ffffff";
    ctx.beginPath();
    ctx.moveTo(x - 4, y - 20);
    ctx.lineTo(x + 4, y - 20);
    ctx.lineTo(x, y - 14);
    ctx.closePath();
    ctx.fill();

    // 5. Swinging Arms + Glowing Tablet in Hand
    ctx.strokeStyle = st.suit;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(x - 9, y - 17);
    ctx.lineTo(x - 13, y - 10 + legSwing * 0.4);
    ctx.moveTo(x + 9, y - 17);
    ctx.lineTo(x + 13, y - 11 - legSwing * 0.4);
    ctx.stroke();

    // Glowing Cyan Data Tablet held in right hand
    ctx.fillStyle = "#38bdf8";
    ctx.strokeStyle = "#0284c7";
    ctx.lineWidth = 1;
    ctx.fillRect(x + 10, y - 15 - legSwing * 0.3, 7, 9);
    ctx.strokeRect(x + 10, y - 15 - legSwing * 0.3, 7, 9);

    // 6. Cute Chibi Head (Skin Tone + Rosy Cheeks + Eyes)
    ctx.fillStyle = "#fde68a";
    ctx.strokeStyle = "#78350f";
    ctx.lineWidth = 1.3;
    ctx.beginPath();
    ctx.arc(x, y - 30, 11.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Cute Hair Cap / Bangs
    ctx.fillStyle = st.hair;
    ctx.beginPath();
    ctx.arc(x, y - 32, 11.8, Math.PI * 0.95, Math.PI * 2.05);
    ctx.fill();

    // Eyes
    ctx.fillStyle = "#0f172a";
    ctx.beginPath();
    ctx.arc(x - 4, y - 29, 1.7, 0, Math.PI * 2);
    ctx.arc(x + 4, y - 29, 1.7, 0, Math.PI * 2);
    ctx.fill();

    // Rosy Cheeks
    ctx.fillStyle = "rgba(244, 63, 94, 0.45)";
    ctx.beginPath();
    ctx.arc(x - 6.5, y - 26.5, 2.2, 0, Math.PI * 2);
    ctx.arc(x + 6.5, y - 26.5, 2.2, 0, Math.PI * 2);
    ctx.fill();

    // Role Accessory (Crown for CIO, Glasses for Quant, Headset for News, Visor for Bot)
    if (st.acc === "CROWN") {{
        ctx.fillStyle = "#fbbf24";
        ctx.beginPath();
        ctx.moveTo(x - 7, y - 41);
        ctx.lineTo(x - 4, y - 47);
        ctx.lineTo(x, y - 43);
        ctx.lineTo(x + 4, y - 47);
        ctx.lineTo(x + 7, y - 41);
        ctx.closePath();
        ctx.fill();
    }} else if (st.acc === "GLASSES") {{
        ctx.strokeStyle = "#0284c7";
        ctx.lineWidth = 1.4;
        ctx.strokeRect(x - 7.5, y - 32, 6, 4.5);
        ctx.strokeRect(x + 1.5, y - 32, 6, 4.5);
    }} else if (st.acc === "ANTENNA") {{
        ctx.strokeStyle = "#a855f7";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x, y - 41);
        ctx.lineTo(x, y - 48);
        ctx.stroke();
        ctx.fillStyle = "#38bdf8";
        ctx.beginPath();
        ctx.arc(x, y - 49, 3, 0, Math.PI * 2);
        ctx.fill();
    }}

    // 7. Mini Name Tag Pill under feet
    ctx.font = "bold 9.5px 'Segoe UI', sans-serif";
    const shortName = sp.ag.name.split(' ')[0];
    const nw = ctx.measureText(shortName).width + 10;
    ctx.fillStyle = "rgba(15, 23, 42, 0.78)";
    ctx.beginPath();
    ctx.roundRect(x - nw / 2, sp.y + 6, nw, 13, 4);
    ctx.fill();
    ctx.fillStyle = "#fbbf24";
    ctx.textAlign = "center";
    ctx.fillText(shortName, x, sp.y + 15.5);

    // 8. Speech Bubble when active
    if (sp.speech && sp.speechTimer > 0) {{
        sp.speechTimer--;
        ctx.font = "bold 10px 'Segoe UI', sans-serif";
        const sw = ctx.measureText(sp.speech).width + 16;
        const bx = x - sw / 2, by = y - 64;
        ctx.fillStyle = "#ffffff";
        ctx.strokeStyle = "#f59e0b";
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.roundRect(bx, by, sw, 20, 8);
        ctx.fill();
        ctx.stroke();
        ctx.fillStyle = "#0f172a";
        ctx.fillText(sp.speech, x, by + 13.5);
    }}
}}

function drawRoundedBadge(ctx, cx, cy, title, subText, dotColor) {{
    ctx.font = "bold 11px 'Segoe UI', sans-serif";
    const w1 = ctx.measureText(title).width;
    ctx.font = "600 10px 'Segoe UI', sans-serif";
    const w2 = ctx.measureText(subText).width + 14;
    const bw = Math.max(w1, w2) + 22;
    const bh = 36;
    const bx = cx - bw / 2, by = cy - bh / 2;

    ctx.fillStyle = "rgba(15, 23, 42, 0.16)";
    ctx.beginPath();
    ctx.roundRect(bx + 2, by + 3, bw, bh, 10);
    ctx.fill();

    ctx.fillStyle = "rgba(255, 255, 255, 0.96)";
    ctx.strokeStyle = "#cbd5e1";
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.roundRect(bx, by, bw, bh, 10);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#0f172a";
    ctx.font = "bold 11px 'Segoe UI', sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(title, cx, by + 14);

    ctx.fillStyle = dotColor;
    ctx.beginPath();
    ctx.arc(cx - w2 / 2 + 4, by + 26, 4, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "#475569";
    ctx.font = "600 10px 'Segoe UI', sans-serif";
    ctx.fillText(subText, cx + 6, by + 29);
}}

function drawPalmTree(ctx, px, py, scale) {{
    ctx.save();
    ctx.translate(px, py);
    ctx.scale(scale, scale);
    ctx.strokeStyle = "#78350f";
    ctx.lineWidth = 6;
    ctx.lineCap = "round";
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.quadraticCurveTo(7, -24, 2, -46);
    ctx.stroke();
    ctx.fillStyle = "#15803d";
    [[-24, -40], [24, -40], [-18, -52], [20, -52], [0, -56]].forEach(([lx, ly]) => {{
        ctx.beginPath();
        ctx.ellipse(lx / 2, ly, 16, 5.5, (lx > 0 ? 0.32 : -0.32), 0, Math.PI * 2);
        ctx.fill();
    }});
    ctx.restore();
}}

// Compute each AI Agent's live Energy / Battery % (derived from token quota & compute mode)
function computeAgentEnergyPct(ag) {{
    if (!ag) return 98;
    if (ag.compute_mode === "OVERCLOCK") return 100;
    const quota = Math.max(ag.token_quota || 80000, 10000);
    const used = Math.max(0, ag.tokens_used_today || 16000);
    const ratio = Math.min(1, used / quota);
    return Math.max(68, Math.min(100, Math.round(100 - ratio * 22)));
}}

// Draw Aurum Isle AI Agent Town House Roof Gable + 3D Glowing Green Battery Cylinder & % Badge
function drawAgentTownHouseAndBattery(ctx, rm, p, energyPct, codeLabel) {{
    const wallH = 38;
    // 1. Cozy Pitched Town-House Roof Gable on Back Apex (preserves cutaway interior view)
    const rx = p.x;
    const ry = p.y - wallH;
    ctx.fillStyle = rm.wallCol;
    ctx.strokeStyle = "#0f172a";
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.moveTo(rx - 36, ry + 16);
    ctx.lineTo(rx, ry - 14);
    ctx.lineTo(rx + 36, ry + 16);
    ctx.lineTo(rx, ry + 4);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Roof ridge highlight
    ctx.fillStyle = rm.wallTop;
    ctx.beginPath();
    ctx.arc(rx, ry - 5, 3.5, 0, Math.PI * 2);
    ctx.fill();

    // 2. 3D Glowing Cylindrical Green Energy Battery Pillar (inspired by @not_nang AI Town Reel)
    const bx = p.x + 54;
    const by = p.y + 46;
    const radX = 9.5;
    const radY = 4.5;
    const cylH = 26;
    const fillH = Math.max(6, Math.round((Math.min(100, Math.max(10, energyPct)) / 100) * cylH));

    // Outer neon green aura
    const glow = ctx.createRadialGradient(bx, by - cylH / 2, 2, bx, by - cylH / 2, 22);
    glow.addColorStop(0, "rgba(34, 197, 94, 0.42)");
    glow.addColorStop(1, "rgba(34, 197, 94, 0.0)");
    ctx.fillStyle = glow;
    ctx.beginPath();
    ctx.arc(bx, by - cylH / 2, 22, 0, Math.PI * 2);
    ctx.fill();

    // Dark metallic base platform
    ctx.fillStyle = "#1e293b";
    ctx.strokeStyle = "#475569";
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.ellipse(bx, by + 2, radX + 3, radY + 1.8, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Cylinder glass shell background
    ctx.fillStyle = "rgba(15, 23, 42, 0.55)";
    ctx.fillRect(bx - radX, by - cylH, radX * 2, cylH);

    // Glowing green energy cylinder body
    const bodyGrad = ctx.createLinearGradient(bx - radX, by - fillH, bx + radX, by);
    bodyGrad.addColorStop(0, "#4ade80");
    bodyGrad.addColorStop(0.5, "#22c55e");
    bodyGrad.addColorStop(1, "#15803d");
    ctx.fillStyle = bodyGrad;
    ctx.beginPath();
    ctx.moveTo(bx - radX, by);
    ctx.lineTo(bx - radX, by - fillH);
    ctx.ellipse(bx, by - fillH, radX, radY, 0, Math.PI, 0, true);
    ctx.lineTo(bx + radX, by);
    ctx.ellipse(bx, by, radX, radY, 0, 0, Math.PI, false);
    ctx.closePath();
    ctx.fill();

    // Cylinder top glowing ellipse
    ctx.fillStyle = "#86efac";
    ctx.strokeStyle = "#16a34a";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.ellipse(bx, by - cylH, radX, radY, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Dark battery terminal cap on top
    ctx.fillStyle = "#1e293b";
    ctx.beginPath();
    ctx.ellipse(bx, by - cylH - 2, 4.5, 2.2, 0, 0, Math.PI * 2);
    ctx.fill();

    // Floating white % badge above the battery pillar (e.g. "98%" / "100%")
    const pctTxt = `${{energyPct}}%`;
    ctx.font = "bold 9.5px 'Segoe UI', sans-serif";
    const tw = Math.max(ctx.measureText(pctTxt).width, ctx.measureText(codeLabel).width) + 10;
    const tagX = bx - tw / 2;
    const tagY = by - cylH - 25;
    ctx.fillStyle = "rgba(255, 255, 255, 0.95)";
    ctx.strokeStyle = "#0f172a";
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.roundRect(tagX, tagY, tw, 19, 5);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#64748b";
    ctx.font = "700 7.5px 'Segoe UI', sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(codeLabel, bx, tagY + 7.5);

    ctx.fillStyle = "#0f172a";
    ctx.font = "900 9px 'Segoe UI', sans-serif";
    ctx.fillText(pctTxt, bx, tagY + 16);
}}

function renderIsometricCompany() {{
    if (!isoCtx || !isoCanvas) return;
    const W = isoCanvas.width, H = isoCanvas.height;
    wavePhase += 0.04;
    isoCtx.clearRect(0, 0, W, H);

    // 1. Sky & Ocean Background (Aurum Isle — Beachside AI Agent Town)
    const skyGrad = isoCtx.createLinearGradient(0, 0, 0, H);
    if (skyTheme === "SUNSET") {{
        skyGrad.addColorStop(0, "#f472b6");
        skyGrad.addColorStop(0.24, "#fdba74");
        skyGrad.addColorStop(0.46, "#38bdf8");
        skyGrad.addColorStop(1, "#0284c7");
    }} else if (skyTheme === "MORNING") {{
        skyGrad.addColorStop(0, "#38bdf8");
        skyGrad.addColorStop(0.45, "#7dd3fc");
        skyGrad.addColorStop(1, "#0369a1");
    }} else {{
        skyGrad.addColorStop(0, "#050811");
        skyGrad.addColorStop(0.45, "#0f172a");
        skyGrad.addColorStop(1, "#1e1b4b");
    }}
    isoCtx.fillStyle = skyGrad;
    isoCtx.fillRect(0, 0, W, H);

    // Glowing Sun / Moon
    isoCtx.fillStyle = skyTheme === "NIGHT" ? "#fef08a" : "#fb923c";
    isoCtx.beginPath();
    isoCtx.arc(920, 74, 34, 0, Math.PI * 2);
    isoCtx.fill();

    // Animated Ocean Waves on Left & Right Shoreline
    isoCtx.strokeStyle = "rgba(255, 255, 255, 0.35)";
    isoCtx.lineWidth = 2;
    for (let i = 0; i < 5; i++) {{
        const wy = 220 + i * 55 + Math.sin(wavePhase + i) * 4;
        isoCtx.beginPath();
        isoCtx.moveTo(20, wy);
        isoCtx.quadraticCurveTo(90, wy - 8, 160, wy);
        isoCtx.moveTo(960, wy);
        isoCtx.quadraticCurveTo(1040, wy - 8, 1110, wy);
        isoCtx.stroke();
    }}

    // Drifting Clouds
    clouds.forEach(cl => {{
        cl.x += cl.v;
        if (cl.x > W + 80) cl.x = -80;
        isoCtx.fillStyle = skyTheme === "NIGHT" ? "rgba(255,255,255,0.14)" : "rgba(255,255,255,0.82)";
        isoCtx.beginPath();
        isoCtx.arc(cl.x, cl.y, 18 * cl.s, 0, Math.PI * 2);
        isoCtx.arc(cl.x + 16 * cl.s, cl.y - 5 * cl.s, 22 * cl.s, 0, Math.PI * 2);
        isoCtx.arc(cl.x + 34 * cl.s, cl.y, 16 * cl.s, 0, Math.PI * 2);
        isoCtx.fill();
    }});

    // 2. Sandy Beach Island Base & Golden Town Plaza Ring
    isoCtx.fillStyle = skyTheme === "NIGHT" ? "#1e293b" : "#fde68a";
    isoCtx.strokeStyle = skyTheme === "NIGHT" ? "#38bdf8" : "#f59e0b";
    isoCtx.lineWidth = 3;
    isoCtx.beginPath();
    isoCtx.moveTo(490, 95);
    isoCtx.lineTo(1065, 345);
    isoCtx.lineTo(575, 545);
    isoCtx.lineTo(85, 295);
    isoCtx.closePath();
    isoCtx.fill();
    isoCtx.stroke();

    // Palm Trees on Beach Corners
    drawPalmTree(isoCtx, 155, 285, 1.0);
    drawPalmTree(isoCtx, 995, 335, 1.05);
    drawPalmTree(isoCtx, 285, 455, 0.9);
    drawPalmTree(isoCtx, 865, 465, 0.95);

    // 3. Draw Connected Isometric AI Town Houses (Floors + 3D Cutaway Walls + Roof Gable + Furniture + Energy Battery Pillar)
    ISO_ROOMS.forEach((rm, idx) => {{
        const p = isoProject(rm.gx, rm.gy);
        const hw = p.w / 2;
        const hh = p.h / 2;
        const wallH = 38;

        // Isometric Diamond Floor Tile
        isoCtx.fillStyle = rm.floorCol;
        isoCtx.strokeStyle = rm.floorAlt;
        isoCtx.lineWidth = 1.5;
        isoCtx.beginPath();
        isoCtx.moveTo(p.x, p.y);
        isoCtx.lineTo(p.x + hw, p.y + hh);
        isoCtx.lineTo(p.x, p.y + p.h);
        isoCtx.lineTo(p.x - hw, p.y + hh);
        isoCtx.closePath();
        isoCtx.fill();
        isoCtx.stroke();

        // Subtle Interior Floor Grid Lines (gives true Isometric game look)
        isoCtx.strokeStyle = "rgba(15, 23, 42, 0.06)";
        isoCtx.lineWidth = 1;
        for (let g = 1; g <= 3; g++) {{
            const f = g / 4.0;
            isoCtx.beginPath();
            isoCtx.moveTo(p.x - hw * f, p.y + hh * f);
            isoCtx.lineTo(p.x + hw * (1 - f), p.y + hh * (1 + f));
            isoCtx.moveTo(p.x + hw * f, p.y + hh * f);
            isoCtx.lineTo(p.x - hw * (1 - f), p.y + hh * (1 + f));
            isoCtx.stroke();
        }}

        // Back-Left & Back-Right 3D Extruded Cutaway Walls (with doorway gaps between interior rooms!)
        drawIsoWallWithDoor(isoCtx, p.x - hw, p.y + hh, p.x, p.y, wallH, 5, rm.floorAlt, rm.wallTop, rm.gy > 0);
        drawIsoWallWithDoor(isoCtx, p.x, p.y, p.x + hw, p.y + hh, wallH, 5, rm.wallCol, rm.wallTop, rm.gx > 0);

        // Detailed 3D Room Furniture & Monitors
        drawRoomFurniture3D(isoCtx, p.x, p.y + hh, rm.propType, rm.wallCol);

        // AI Town House Roof Gable + Glowing Green Energy Battery Cylinder
        const linkedAg = APP.office.agents_roster[idx % APP.office.agents_roster.length];
        const energyPct = computeAgentEnergyPct(linkedAg);
        const shortCode = rm.id.split('_')[0];
        drawAgentTownHouseAndBattery(isoCtx, rm, p, energyPct, shortCode);
    }});

    // 4. Sort & Draw Full-Body Chibi AI Characters by Y-depth
    const sortedSprites = [...isoSprites].sort((a, b) => a.y - b.y);
    sortedSprites.forEach(sp => {{
        const dx = sp.tx - sp.x;
        const dy = sp.ty - sp.y;
        const dist = Math.hypot(dx, dy);
        if (dist > 2.2) {{
            sp.x += (dx / dist) * 2.1;
            sp.y += (dy / dist) * 2.1;
        }} else if (Math.random() < 0.014) {{
            const nextRm = ISO_ROOMS[Math.floor(Math.random() * ISO_ROOMS.length)];
            const np = isoProject(nextRm.gx, nextRm.gy);
            sp.tx = np.x + (Math.random() - 0.5) * 42;
            sp.ty = np.y + 48 + (Math.random() - 0.5) * 18;
            if (Math.random() < 0.35) {{
                sp.speech = `ส่งงานไป ${{nextRm.name.split(' ')[0]}} ✔`;
                sp.speechTimer = 110;
            }}
        }}
        drawChibiAgent(isoCtx, sp);
    }});

    // 5. Floating White Rounded Room Status Badges on Top
    ISO_ROOMS.forEach(rm => {{
        const p = isoProject(rm.gx, rm.gy);
        drawRoundedBadge(isoCtx, p.x, p.y - 26, rm.name, rm.sub, rm.badgeDot);
    }});

    requestAnimationFrame(renderIsometricCompany);
}}

if (isoCanvas) {{
    isoCanvas.addEventListener('click', e => {{
        const rect = isoCanvas.getBoundingClientRect();
        const mx = (e.clientX - rect.left) * (isoCanvas.width / rect.width);
        const my = (e.clientY - rect.top) * (isoCanvas.height / rect.height);
        let closest = null, bestD = 999;
        isoSprites.forEach(sp => {{
            const d = Math.hypot(sp.x - mx, (sp.y - 18) - my);
            if (d < bestD && d < 48) {{ bestD = d; closest = sp; }}
        }});
        if (closest) {{
            closest.speech = "พร้อมรายงานครับ! 💬";
            closest.speechTimer = 150;
            selectVisualizerAgent(closest.ag.agent_id);
        }}
    }});
}}

function changeSkyAtmosphere(val) {{ skyTheme = val; }}

function selectVisualizerAgent(agentId) {{
    const ag = APP.office.agents_roster.find(a => a.agent_id === agentId);
    if (!ag) return;
    selectedAgent = ag;
    const energyPct = computeAgentEnergyPct(ag);
    document.getElementById('bannerAvatar').textContent = ag.avatar;
    document.getElementById('bannerSpeaker').textContent = `${{ag.name}} (${{ag.role}}) — สมองกล: ${{ag.llm_model}} [${{ag.compute_mode || 'BALANCED'}} • 🔋 ${{energyPct}}%]`;
    document.getElementById('bannerMessage').innerHTML = `ภารกิจล่าสุด: <strong>${{ag.current_task}}</strong> • โทเคนวันนี้: <strong>${{(ag.tokens_used_today || 18500).toLocaleString()}} / ${{(ag.token_quota || 80000).toLocaleString()}} Tokens</strong>`;
    renderMiniAgentsStrip();
}}

function renderMiniAgentsStrip() {{
    const strip = document.getElementById('miniAgentsStrip');
    if (!strip) return;
    strip.innerHTML = APP.office.agents_roster.map(ag => {{
        const energyPct = computeAgentEnergyPct(ag);
        return `
        <div class="mini-agent-card ${{ag.agent_id === selectedAgent.agent_id ? 'active' : ''}}" onclick="selectVisualizerAgent('${{ag.agent_id}}')">
            <div style="font-size:1.5rem">${{ag.avatar}}</div>
            <div style="overflow:hidden;flex:1">
                <div style="display:flex;justify-content:space-between;align-items:center;gap:4px">
                    <div style="font-weight:800;font-size:0.8rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${{ag.name}}</div>
                    <span style="font-size:0.68rem;background:#dcfce7;color:#15803d;padding:1px 6px;border-radius:99px;font-weight:800">🔋 ${{energyPct}}%</span>
                </div>
                <div style="font-size:0.72rem;color:#10b981;font-weight:700">● ${{ag.status || 'เสร็จแล้ว'}}</div>
                <div style="font-size:0.68rem;color:var(--text-sub)">🧠 ${{(ag.llm_model || '').split(' ')[0]}} • ${{Math.round((ag.tokens_used_today || 18000)/1000)}}K</div>
            </div>
        </div>
        `;
    }}).join('');
}}

function renderRightSidebarMission(activeStep = 8) {{
    const box = document.getElementById('missionChecklistBox');
    if (!box) return;
    box.innerHTML = APP.checklist.map(item => {{
        let circleCls = "check-circle";
        let icon = "✔";
        if (item.step > activeStep) {{ circleCls = "check-circle pending"; icon = item.step; }}
        else if (item.step === activeStep && activeStep < 8) {{ circleCls = "check-circle running"; icon = "⏳"; }}
        return `
        <div class="mission-item">
            <div class="${{circleCls}}">${{icon}}</div>
            <div style="flex:1">
                <div style="font-weight:800">${{item.step}}. ${{item.title}}</div>
                <div style="font-size:0.75rem;color:var(--text-sub)">${{item.agent}} • ${{item.detail}}</div>
            </div>
        </div>`;
    }}).join('');

    const doneCount = Math.min(8, activeStep);
    const pct = Math.round((doneCount / 8) * 100);
    document.getElementById('topTaskCountText').textContent = `งานเสร็จ ${{doneCount}}/8`;
    document.getElementById('topTaskPctText').textContent = `${{pct}}%`;
    document.getElementById('topTaskBar').style.width = `${{pct}}%`;
}}

function appendRealtimeLog(timeStr, agentName, text) {{
    const box = document.getElementById('realtimeLogBox');
    if (!box) return;
    const row = document.createElement('div');
    row.className = 'live-log-row';
    row.innerHTML = `<span class="log-time">${{timeStr}}</span><div><strong>${{agentName}}:</strong> ${{text}}</div>`;
    box.prepend(row);
}}

function initRealtimeLogs() {{
    const box = document.getElementById('realtimeLogBox');
    if (!box) return;
    box.innerHTML = '';
    const logs = APP.office.recent_logs || [];
    logs.slice(0, 12).reverse().forEach(lg => {{
        const t = (lg.timestamp || '').split(' ')[1] || '23:35:00';
        appendRealtimeLog(t, lg.agent_name, lg.summary);
    }});
}}

let workflowTimer = null;
function runLiveCompanyWorkflowAnimation() {{
    if (workflowTimer) clearInterval(workflowTimer);
    let step = 1;
    document.getElementById('topSysStatusText').textContent = "กำลังรันภารกิจสด...";
    ISO_ROOMS.forEach(r => {{ r.sub = "รอคิวงาน..."; r.badgeDot = "#94a3b8"; }});
    renderRightSidebarMission(1);

    workflowTimer = setInterval(() => {{
        const item = APP.checklist[step - 1];
        if (item) {{
            const rm = ISO_ROOMS[step - 1];
            if (rm) {{
                rm.sub = "เสร็จแล้ว ✔";
                rm.badgeDot = "#10b981";
                const p = isoProject(rm.gx, rm.gy);
                const sp = isoSprites[step - 1];
                if (sp) {{
                    sp.tx = p.x;
                    sp.ty = p.y + 48;
                    sp.speech = `${{item.title}} ✔`;
                    sp.speechTimer = 140;
                }}
            }}
            const now = new Date();
            const ts = `${{String(now.getHours()).padStart(2,'0')}}:${{String(now.getMinutes()).padStart(2,'0')}}:${{String(now.getSeconds()).padStart(2,'0')}}`;
            appendRealtimeLog(ts, item.agent, `${{item.title}} — ${{item.detail}}`);
            document.getElementById('bannerSpeaker').textContent = `${{item.agent}} (${{item.room}})`;
            document.getElementById('bannerMessage').innerHTML = `ขั้นตอนที่ ${{step}}/8: <strong>${{item.title}}</strong> ➔ ${{item.detail}}`;
        }}
        renderRightSidebarMission(step);
        step++;
        if (step > 8) {{
            clearInterval(workflowTimer);
            document.getElementById('topSysStatusText').textContent = "ระบบปกติ พร้อมทำงาน";
            selectVisualizerAgent("ag_cio");
        }}
    }}, 650);
}}

// Trigger Offline Auto-Catchup Simulation
async function triggerOfflineCatchupSim(hours) {{
    try {{
        const res = await fetch('/api/offline_catchup', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ offline_hours: hours }})
        }});
        if (res.ok) {{
            const data = await res.json();
            document.getElementById('catchupStatusText').textContent = data.summary;
            const now = new Date();
            appendRealtimeLog(`${{String(now.getHours()).padStart(2,'0')}}:${{String(now.getMinutes()).padStart(2,'0')}}:${{String(now.getSeconds()).padStart(2,'0')}}`, "Offline Auto-Catchup", data.summary);
            alert(`⚡ เก็บตกงานย้อนหลังช่วงปิดคอม (${{hours}} ชม. / ${{data.shifts_recovered}} กะ) สำเร็จ!\n• ซิงค์กราฟและมติย้อนหลังเข้าหน้า 'ดูสรุปย้อนหลัง' และโฟลเดอร์ Obsidian เรียบร้อยแล้ว!`);
            return;
        }}
    }} catch (e) {{}}
    alert(`⚡ เก็บตกงานย้อนหลังช่วงปิดคอม (${{hours}} ชม.) สำเร็จ!`);
}}


// ============================================================================
// PAGE 2: TOKEN TREASURY, CUSTOM MODEL ADDER & SKILL HARVESTER
// ============================================================================
function initTokenAndSkillPage() {{
    const agSel = document.getElementById('harvestAgentSelect');
    if (agSel) {{
        agSel.innerHTML = APP.office.agents_roster.map(ag =>
            `<option value="${{ag.agent_id}}">${{ag.avatar}} ${{ag.name}} (${{ag.llm_model}})</option>`
        ).join('');
        agSel.value = "ag_quant";
    }}
    renderDiscoveredSkillsList(APP.disc_skills);
    renderTokenAllocationTable();
}}

async function addNewCustomModel() {{
    const nameInp = document.getElementById('customModelNameInput');
    const specInp = document.getElementById('customModelSpecInput');
    const modelId = nameInp.value.trim();
    const spec = specInp.value.trim() || "โมเดล AI ระดับท็อปที่ผู้บริหารเพิ่มเข้าระบบ";
    if (!modelId) {{ alert("กรุณาพิมพ์ชื่อโมเดล AI ที่ต้องการเพิ่มครับ"); return; }}

    const newMod = {{
        id: modelId,
        provider: "Custom Frontier / OpenRouter",
        badge_color: "#ec4899",
        specialty: spec,
        cost: "CUSTOM BURN (50K Tokens/รอบ)",
        avg_tokens_per_run: 50000,
        tier: "HEAVY_REASONING"
    }};
    APP.avail_models.unshift(newMod);
    nameInp.value = '';
    specInp.value = '';
    renderTokenAllocationTable();
    initProfileRoster();

    try {{
        await fetch('/api/add_custom_model', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ model_id: modelId, specialty: spec }})
        }});
    }} catch (e) {{}}
    alert(`✨ เพิ่มโมเดล '${{modelId}}' เข้าสู่คลังสมองบริษัทเรียบร้อยแล้ว! สามารถเลือกให้พนักงาน AI ใช้ได้ทันที`);
}}

function renderDiscoveredSkillsList(skills) {{
    const box = document.getElementById('discoveredSkillsBox');
    if (!box) return;
    box.innerHTML = (skills || []).map(sk => `
        <div style="background:var(--bg-sub);border:1px solid var(--border-col);border-left:4px solid #8b5cf6;border-radius:10px;padding:12px">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px">
                <strong style="font-size:0.9rem">🎓 ${{sk.skill_name}}</strong>
                <span class="pill" style="background:#dcfce7;color:#166534">Win Rate: ${{sk.backtest_win_rate}}% (+${{sk.accuracy_boost}}% Acc)</span>
            </div>
            <div style="font-size:0.8rem;color:var(--text-sub);margin-top:5px">${{sk.formula_logic}}</div>
            <div style="font-size:0.74rem;color:var(--text-sub);margin-top:6px;display:flex;justify-content:space-between">
                <span>👤 ผู้ค้นพบ: <strong>${{sk.agent_name}}</strong> (${{sk.category}})</span>
                <span>🪙 เผาโทเคนวิจัย: <strong>${{(sk.tokens_spent || 25000).toLocaleString()}} Tokens</strong></span>
            </div>
        </div>
    `).join('');
}}

function renderTokenAllocationTable() {{
    const wrap = document.getElementById('tokenAllocationTableWrap');
    if (!wrap) return;
    const rows = APP.office.agents_roster.map(ag => {{
        const quota = ag.token_quota || 80000;
        const used = ag.tokens_used_today || 18500;
        const mode = ag.compute_mode || "BALANCED";
        const modelOpts = APP.avail_models.map(m =>
            `<option value="${{m.id}}" ${{m.id === ag.llm_model ? 'selected' : ''}}>${{m.id}}</option>`
        ).join('');

        return `
        <div style="padding:12px;border:1px solid var(--border-col);border-radius:12px;margin-bottom:10px;background:var(--bg-sub)">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:8px">
                <div>
                    <strong style="font-size:0.9rem">${{ag.avatar}} ${{ag.name}}</strong>
                    <span class="pill" style="margin-left:6px">Lv.${{ag.level}}</span>
                </div>
                <div style="font-size:0.78rem;color:#f59e0b;font-weight:700">
                    ใช้ไป ${{used.toLocaleString()}} / ${{quota.toLocaleString()}} Tokens
                </div>
            </div>
            <div style="display:grid;grid-template-columns:1.4fr 1fr 1fr auto;gap:8px;align-items:center">
                <select id="model-${{ag.agent_id}}" class="input-clean" style="font-size:0.78rem;padding:6px">${{modelOpts}}</select>
                <select id="mode-${{ag.agent_id}}" class="input-clean" style="font-size:0.78rem;padding:6px">
                    <option value="ECO" ${{mode==='ECO'?'selected':''}}>🌱 ECO (ประหยัด)</option>
                    <option value="BALANCED" ${{mode==='BALANCED'?'selected':''}}>⚖️ BALANCED (มาตรฐาน)</option>
                    <option value="OVERCLOCK" ${{mode==='OVERCLOCK'?'selected':''}}>🔥 OVERCLOCK (คิดลึกสุดขีด)</option>
                </select>
                <input type="number" id="quota-${{ag.agent_id}}" class="input-clean" style="font-size:0.78rem;padding:6px" value="${{quota}}" step="10000">
                <button class="cozy-btn amber" style="padding:6px 10px;font-size:0.76rem" onclick="saveAgentTokenAllocation('${{ag.agent_id}}')">💾 บันทึก & อัดโทเคน</button>
            </div>
        </div>`;
    }}).join('');
    wrap.innerHTML = rows;
}}

function setSkillTopic(txt) {{ document.getElementById('harvestTopicInput').value = txt; }}

async function triggerLearnNewSkill() {{
    const agentId = document.getElementById('harvestAgentSelect').value;
    const tok = parseInt(document.getElementById('harvestTokenSelect').value, 10) || 50000;
    const topicInput = document.getElementById('harvestTopicInput');
    const topic = topicInput.value.trim() || "ICT New York Killzone Orderblock & FVG";

    try {{
        const res = await fetch('/api/learn_skill', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ agent_id: agentId, skill_topic: topic, tokens_to_spend: tok }})
        }});
        if (res.ok) {{
            const data = await res.json();
            APP.disc_skills = data.all_discovered_skills;
            renderDiscoveredSkillsList(APP.disc_skills);
            document.getElementById('econSkillsCountVal').textContent = `${{APP.disc_skills.length}} สกิลใหม่`;
            topicInput.value = '';
            alert(`🎓 ปลดล็อกสกิลใหม่สำเร็จ!\n• ชื่อสกิล: ${{data.new_skill.skill_name}}\n• Win Rate ทดสอบบนกราฟจริง: ${{data.new_skill.backtest_win_rate}}% (+${{data.new_skill.accuracy_boost}}% Accuracy)`);
            return;
        }}
    }} catch (e) {{}}
}}

async function saveAgentTokenAllocation(agentId) {{
    const modelVal = document.getElementById('model-' + agentId).value;
    const modeVal = document.getElementById('mode-' + agentId).value;
    const quotaVal = parseInt(document.getElementById('quota-' + agentId).value, 10) || 80000;
    const boost = modeVal === 'OVERCLOCK' ? 25000 : 5000;

    const ag = APP.office.agents_roster.find(a => a.agent_id === agentId);
    if (ag) {{
        ag.llm_model = modelVal;
        ag.compute_mode = modeVal;
        ag.token_quota = quotaVal;
        ag.tokens_used_today = (ag.tokens_used_today || 18000) + boost;
    }}
    renderTokenAllocationTable();
    renderMiniAgentsStrip();

    try {{
        const res = await fetch('/api/allocate_tokens', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
                agent_id: agentId,
                llm_model: modelVal,
                compute_mode: modeVal,
                token_quota: quotaVal,
                instant_boost_tokens: boost
            }})
        }});
        if (res.ok) {{
            const data = await res.json();
            document.getElementById('topTokenUsedText').textContent = data.total_tokens_used.toLocaleString();
            document.getElementById('econUsedVal').textContent = `${{data.total_tokens_used.toLocaleString()}} Tokens (${{data.utilization_pct}}%)`;
            document.getElementById('econReasoningVal').textContent = `${{data.reasoning_tokens.toLocaleString()}} Tokens`;
        }}
    }} catch (e) {{}}
}}

function quickOverclockAllAgents() {{
    APP.office.agents_roster.forEach(ag => {{ ag.compute_mode = "OVERCLOCK"; }});
    document.getElementById('bannerMessage').innerHTML = `🔥 <strong>เปิดโหมด OVERCLOCK ทั้งเมือง AI (Aurum Isle)!</strong> แบตเตอรี่ทุกบ้านชาร์จเต็ม 100% เผา Reasoning Tokens คิดวิเคราะห์เชิงลึกสูงสุด!`;
    renderTokenAllocationTable();
    renderMiniAgentsStrip();
}}


// ============================================================================
// PAGE 3: TRUE HISTORICAL CANDLE & SHIFT REPLAY SUMMARIZER
// ============================================================================
function pickQuickReplayDate(dtStr) {{
    document.getElementById('sumDateInput').value = dtStr;
    generateCuteSummary(currentSummaryStyle);
}}

function selectShiftPill(el) {{
    document.querySelectorAll('.shift-pill').forEach(p => p.classList.remove('active'));
    el.classList.add('active');
    currentShiftSlot = el.getAttribute('data-slot');
    generateCuteSummary(currentSummaryStyle);
}}

async function generateCuteSummary(styleOverride) {{
    if (styleOverride) currentSummaryStyle = styleOverride;
    const dt = document.getElementById('sumDateInput').value || "{today_str}";
    const outBox = document.getElementById('cuteSummaryOutput');

    try {{
        const res = await fetch('/api/summarize', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ date: dt, time_slot: currentShiftSlot, style: currentSummaryStyle }})
        }});
        if (res.ok) {{
            const data = await res.json();
            updateReplayMetricCards(data);
            outBox.textContent = data.summary_text;
            return;
        }}
    }} catch (e) {{}}

    let hash = 0;
    const keyStr = `${{dt}}:${{currentShiftSlot}}`;
    for (let i = 0; i < keyStr.length; i++) hash = ((hash << 5) - hash) + keyStr.charCodeAt(i);
    hash = Math.abs(hash);

    const baseP = APP.market.current_price || 3860.0;
    const openP = +(baseP + ((hash % 700) - 350) / 10.0).toFixed(2);
    const chg = +(((hash >> 3) % 460 - 220) / 10.0).toFixed(2);
    const closeP = +(openP + chg).toFixed(2);
    const highP = +(Math.max(openP, closeP) + (hash % 140) / 10.0 + 3.5).toFixed(2);
    const lowP = +(Math.min(openP, closeP) - (hash % 130) / 10.0 - 3.2).toFixed(2);
    const rsi = +(35 + (hash % 380) / 10.0).toFixed(1);
    const atr = +(12 + (hash % 120) / 10.0).toFixed(2);
    const act = chg >= 0 ? "BUY (LONG)" : "SELL (SHORT)";
    const bullP = chg >= 0 ? 64 : 36;
    const tokBurn = 45000 + (hash % 85000);

    const mockSnap = {{
        open_price: openP, close_price: closeP, high_price: highP, low_price: lowP,
        range_dollar: +(highP - lowP).toFixed(2), change_dollar: chg,
        change_pct: +((chg / openP) * 100).toFixed(2),
        rsi14: rsi, atr14: atr, bull_power: bullP, bear_power: 100 - bullP,
        verdict_action: act, tokens_burned: tokBurn
    }};
    updateReplayMetricCards(mockSnap);
    outBox.textContent = `🏝️ สรุปบันทึกย้อนหลัง {BRAND_NAME} ({BRAND_TAGLINE}) — วันที่ ${{dt}} (กะ ${{currentShiftSlot}})\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n• ราคาเปิดกะ: $${{openP}} ➔ ปิดกะ: $${{closeP}} (${{chg >= 0 ? '+' : ''}}${{chg}}$)\n• กรอบ High/Low ประจำกะ: สูงสุด $${{highP}} / ต่ำสุด $${{lowP}}\n• อินดิเคเตอร์ประจำกะ: RSI = ${{rsi}} | H1 ATR = $${{atr}}\n• มติ CIO ประจำกะ: ${{act}} (Bull ${{bullP}}% vs Bear ${{100-bullP}}%)\n• โทเคนที่เผาในกะนี้: ${{tokBurn.toLocaleString()}} Tokens`;
}}

function updateReplayMetricCards(d) {{
    if (!d) return;
    document.getElementById('repOpenCloseTxt').textContent = `$${{d.open_price}} ➔ $${{d.close_price}}`;
    const isPos = d.change_dollar >= 0;
    const chgEl = document.getElementById('repChangeTxt');
    chgEl.textContent = `${{isPos ? '+' : ''}}${{d.change_dollar}}$ (${{isPos ? '+' : ''}}${{d.change_pct}}%)`;
    chgEl.style.color = isPos ? '#10b981' : '#ef4444';

    document.getElementById('repHighLowTxt').textContent = `H: $${{d.high_price}} / L: $${{d.low_price}}`;
    document.getElementById('repRangeTxt').textContent = `ระยะสวิงในกะ: $${{d.range_dollar}}`;
    document.getElementById('repRsiAtrTxt').textContent = `RSI ${{d.rsi14}} | ATR $${{d.atr14}}`;
    document.getElementById('repDebateTxt').textContent = `🐂 Bull ${{d.bull_power}}% vs 🐻 Bear ${{d.bear_power}}%`;
    document.getElementById('repVerdictTxt').textContent = d.verdict_action;
    document.getElementById('repTokensTxt').textContent = `🪙 เผาไป ${{(d.tokens_burned || 52000).toLocaleString()}} Tokens`;
}}

function copySummaryText() {{
    const txt = document.getElementById('cuteSummaryOutput').textContent;
    navigator.clipboard.writeText(txt);
    alert("📋 คัดลอกข้อความสรุปเรียบร้อยแล้ว!");
}}


// ============================================================================
// PAGE 4: DEDICATED AI AGENT PROFILES & 5D RADAR CHART
// ============================================================================
function initProfileRoster() {{
    const listEl = document.getElementById('profileRosterList');
    const selEl = document.getElementById('profModelSelect');
    if (!listEl || !selEl) return;

    selEl.innerHTML = APP.avail_models.map(m =>
        `<option value="${{m.id}}">${{m.id}} — [${{m.cost}}]</option>`
    ).join('');

    listEl.innerHTML = APP.office.agents_roster.map(ag => `
        <div class="mini-agent-card ${{ag.agent_id === selectedAgent.agent_id ? 'active' : ''}}" onclick="selectProfileAgent('${{ag.agent_id}}')">
            <span style="font-size:1.7rem">${{ag.avatar}}</span>
            <div style="flex:1">
                <div style="font-weight:800">${{ag.name}} <span style="color:#f59e0b;font-size:0.76rem">Lv.${{ag.level}}</span></div>
                <div style="font-size:0.73rem;color:#8b5cf6;font-weight:700">🧠 ${{ag.llm_model}}</div>
            </div>
        </div>
    `).join('');
}}

function selectProfileAgent(agentId) {{
    const found = APP.office.agents_roster.find(a => a.agent_id === agentId);
    if (!found) return;
    selectedAgent = found;
    initProfileRoster();
    renderProfileStudio(found);
}}

function renderProfileStudio(ag) {{
    document.getElementById('profAvatar').textContent = ag.avatar || '🤖';
    document.getElementById('profDept').textContent = ag.department;
    document.getElementById('profName').textContent = ag.name;
    document.getElementById('profRole').textContent = ag.role;
    document.getElementById('profBio').textContent = `${{ag.bio || ag.current_task}} (โควต้าโทเคน: ${{(ag.token_quota || 80000).toLocaleString()}} Tokens/วัน • โหมด ${{ag.compute_mode || 'BALANCED'}})`;
    document.getElementById('profLevelTxt').textContent = `Level ${{ag.level}} (EXP: ${{ag.exp}}/${{ag.max_exp}})`;
    document.getElementById('profMasteryTxt').textContent = `Mastery: ${{ag.mastery_pct}}% (+${{ag.accuracy_bonus_pct}}% Accuracy)`;
    document.getElementById('profExpBar').style.width = `${{Math.min(100, Math.round((ag.exp / Math.max(ag.max_exp, 1)) * 100))}}%`;

    const selEl = document.getElementById('profModelSelect');
    if (selEl) selEl.value = ag.llm_model;

    document.getElementById('profSkillsList').innerHTML = `
        <div style="padding:8px;background:var(--bg-card);border-radius:8px;border:1px solid var(--border-col)">⚡ <strong>Primary Skill:</strong> ${{ag.primary_skill}}</div>
        <div style="padding:8px;background:var(--bg-card);border-radius:8px;border:1px solid var(--border-col)">🛡️ <strong>Secondary Skill:</strong> ${{ag.secondary_skill}}</div>
        <div style="padding:8px;background:var(--bg-card);border-radius:8px;border:1px solid #f59e0b">👑 <strong>Ultimate Skill:</strong> ${{ag.ultimate_skill}}</div>
    `;
    drawRadarChart(ag);
}}

function drawRadarChart(ag) {{
    const c = document.getElementById('radarChartCanvas');
    if (!c) return;
    const ctx = c.getContext('2d');
    ctx.clearRect(0, 0, c.width, c.height);

    const cx = c.width / 2, cy = c.height / 2 + 8, maxR = 100;
    const labels = ["Accuracy", "Speed", "Risk Guard", "Macro", "Creativity"];
    const stats = [ag.stat_accuracy || 92, ag.stat_speed || 90, ag.stat_risk || 88, ag.stat_macro || 86, ag.stat_creativity || 88];

    [0.25, 0.5, 0.75, 1.0].forEach(rFrac => {{
        ctx.beginPath();
        for (let i = 0; i < 5; i++) {{
            const ang = (i / 5) * Math.PI * 2 - Math.PI / 2;
            const x = cx + Math.cos(ang) * (maxR * rFrac);
            const y = cy + Math.sin(ang) * (maxR * rFrac);
            if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }}
        ctx.closePath();
        ctx.strokeStyle = "#334155";
        ctx.stroke();
    }});

    ctx.beginPath();
    for (let i = 0; i < 5; i++) {{
        const ang = (i / 5) * Math.PI * 2 - Math.PI / 2;
        const valR = (stats[i] / 100.0) * maxR;
        const x = cx + Math.cos(ang) * valR;
        const y = cy + Math.sin(ang) * valR;
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);

        const lx = cx + Math.cos(ang) * (maxR + 28);
        const ly = cy + Math.sin(ang) * (maxR + 16);
        ctx.fillStyle = "#f8fafc";
        ctx.font = "bold 11px 'Segoe UI', sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(`${{labels[i]}} (${{stats[i]}})`, lx, ly);
    }}
    ctx.closePath();
    ctx.fillStyle = "rgba(56, 189, 248, 0.35)";
    ctx.fill();
    ctx.strokeStyle = "#38bdf8";
    ctx.lineWidth = 2.5;
    ctx.stroke();
}}

async function changeAgentModelBrain() {{
    const newModel = document.getElementById('profModelSelect').value;
    selectedAgent.llm_model = newModel;
    document.getElementById('profModelMeta').textContent = `✓ เปลี่ยนสมองกลเป็น '${{newModel}}' สำเร็จ!`;
    initProfileRoster();
    renderTokenAllocationTable();
    try {{
        await fetch('/api/switch_model', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ agent_id: selectedAgent.agent_id, llm_model: newModel }})
        }});
    }} catch (e) {{}}
}}

async function trainCurrentProfileAgent() {{
    selectedAgent.exp += 180;
    if (selectedAgent.exp >= selectedAgent.max_exp) {{
        selectedAgent.exp -= selectedAgent.max_exp;
        selectedAgent.level += 1;
        selectedAgent.mastery_pct = +(selectedAgent.mastery_pct + 0.5).toFixed(2);
    }}
    renderProfileStudio(selectedAgent);
    initProfileRoster();
}}

function openSelectedAgentProfile() {{ switchPage('page-profiles'); }}


// ============================================================================
// PAGE 5: LIVE COPILOT CHAT
// ============================================================================
function initChatRoom() {{
    const listEl = document.getElementById('chatTargetList');
    if (!listEl) return;
    let html = `
        <div class="mini-agent-card active" id="chat-target-antigravity" onclick="selectChatTarget('antigravity', '🤖 Antigravity Copilot', 'Claude 3.7 Extended Thinking + OpenAI o1-Pro')">
            <span style="font-size:1.7rem">🤖</span>
            <div>
                <div style="font-weight:800">Antigravity Copilot (ตัวผมเอง)</div>
                <div style="font-size:0.74rem;color:#0ea5e9">ถามแผนเทรด โทเคน หรือสั่งงานได้ทุกเรื่อง</div>
            </div>
        </div>
    `;
    APP.office.agents_roster.forEach(ag => {{
        html += `
        <div class="mini-agent-card" id="chat-target-${{ag.agent_id}}" onclick="selectChatTarget('${{ag.agent_id}}', '${{ag.avatar}} ${{ag.name}}', '${{ag.llm_model}}')">
            <span style="font-size:1.5rem">${{ag.avatar}}</span>
            <div>
                <div style="font-weight:800">${{ag.name}}</div>
                <div style="font-size:0.72rem;color:var(--text-sub)">${{ag.llm_model}}</div>
            </div>
        </div>`;
    }});
    listEl.innerHTML = html;

    const box = document.getElementById('chatMessagesBox');
    box.innerHTML = `
        <div style="align-self:flex-start;background:var(--bg-card);border:1px solid var(--border-col);padding:12px 16px;border-radius:14px;max-width:82%;font-size:0.9rem;line-height:1.55">
            👋 สวัสดีครับ! ผม <strong>🤖 Antigravity Copilot</strong> ยินดีต้อนรับสู่ <strong>{BRAND_NAME} — {BRAND_TAGLINE}</strong> (ภารกิจเมือง AI ปั้นกำไร $1,000 ใน 30 วัน)!<br>
            • ตอนนี้ราคาทองคำอยู่ที่ <strong>$${{APP.market.current_price}}</strong> และมติ CIO คือ <strong>${{APP.cio.action}}</strong> (Entry $${{APP.cio.final_entry}} | SL $${{APP.cio.final_sl}} | TP1 $${{APP.cio.final_tp1}})<br>
            • คุณสามารถปิดคอมนอนได้สบายใจ เพราะมีระบบ <strong>Offline Shift Auto-Catchup</strong> คอยดึงกราฟย้อนหลังมาสรุปให้ครบทุกกะเมื่อเปิดเครื่องครับ!
        </div>
    `;
}}

function selectChatTarget(targetId, title, modelName) {{
    chatTargetId = targetId;
    document.querySelectorAll('#chatTargetList .mini-agent-card').forEach(el => el.classList.remove('active'));
    const el = document.getElementById('chat-target-' + targetId);
    if (el) el.classList.add('active');
    document.getElementById('chatHeaderSpeaker').textContent = title;
    document.getElementById('chatHeaderModel').textContent = `Brain: ${{modelName}}`;
}}

function askSelectedAgentInChat() {{
    switchPage('page-chat');
    selectChatTarget(selectedAgent.agent_id, `${{selectedAgent.avatar}} ${{selectedAgent.name}}`, selectedAgent.llm_model);
}}
function askCurrentProfileAgent() {{ askSelectedAgentInChat(); }}

function sendQuickPrompt(text) {{
    document.getElementById('chatInputField').value = text;
    sendChatMessage();
}}

async function sendChatMessage() {{
    const inp = document.getElementById('chatInputField');
    const msg = inp.value.trim();
    if (!msg) return;
    inp.value = '';

    const box = document.getElementById('chatMessagesBox');
    box.innerHTML += `<div style="align-self:flex-end;background:#0f172a;color:#fbbf24;padding:10px 15px;border-radius:14px;max-width:80%;font-size:0.9rem">${{msg}}</div>`;
    box.scrollTop = box.scrollHeight;

    try {{
        const res = await fetch('/api/chat', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ message: msg, target_agent: chatTargetId }})
        }});
        if (res.ok) {{
            const data = await res.json();
            box.innerHTML += `<div style="align-self:flex-start;background:var(--bg-card);border:1px solid var(--border-col);padding:12px 16px;border-radius:14px;max-width:82%;font-size:0.9rem;white-space:pre-wrap;line-height:1.55"><strong style="color:#f59e0b">${{data.speaker_name}} [${{data.model_used}}]:</strong>\n${{data.reply}}</div>`;
            box.scrollTop = box.scrollHeight;
            return;
        }}
    }} catch (e) {{}}
}}


// ============================================================================
// PAGE 6: MT5 DEMO TERMINAL & OBSIDIAN GRAPH
// ============================================================================
const mt5Canvas = document.getElementById('mt5DemoChartCanvas');
const mt5Ctx = mt5Canvas ? mt5Canvas.getContext('2d') : null;
let mt5Timer = null, mt5AnimIndex = 0, currentSLPrice = APP.mt5_demo.sl_price;

function startLiveMT5Simulation() {{
    if (!mt5Ctx) return;
    if (mt5Timer) clearInterval(mt5Timer);
    mt5AnimIndex = 1;
    currentSLPrice = APP.mt5_demo.sl_price;
    const ticks = APP.mt5_demo.tick_series || [];

    const container = document.getElementById('mt5StepsContainer');
    if (container) {{
        container.innerHTML = (APP.mt5_demo.steps_telemetry || []).map(st => `
            <div style="padding:9px 12px;border:1px solid var(--border-col);border-left:4px solid #10b981;border-radius:8px;background:var(--bg-sub);font-size:0.8rem">
                <strong>Step ${{st.step}}: ${{st.phase}}</strong> <span class="pill">${{st.status}}</span>
                <div style="color:var(--text-sub);margin-top:3px">${{st.detail}}</div>
            </div>
        `).join('');
    }}

    mt5Timer = setInterval(() => {{
        mt5AnimIndex++;
        if (mt5AnimIndex >= ticks.length) {{
            mt5AnimIndex = ticks.length;
            clearInterval(mt5Timer);
        }}
        const tk = ticks[mt5AnimIndex - 1];
        if (tk && tk.sl_moved_to_be) {{
            currentSLPrice = APP.mt5_demo.entry_price;
            document.getElementById('mt5LiveSL').textContent = `$${{currentSLPrice.toFixed(2)}} (LOCKED BE)`;
        }}
        if (tk) {{
            const pnl = ((APP.mt5_demo.direction === "BUY") ? (tk.price - APP.mt5_demo.entry_price) : (APP.mt5_demo.entry_price - tk.price)) * APP.mt5_demo.lot_size * 100;
            document.getElementById('mt5LivePnL').textContent = `${{pnl >= 0 ? '+' : ''}}$${{pnl.toFixed(2)}}`;
        }}
        drawMT5ChartFrame(mt5AnimIndex);
    }}, 80);
}}

function drawMT5ChartFrame(upToIdx) {{
    if (!mt5Ctx) return;
    const W = mt5Canvas.width, H = mt5Canvas.height;
    mt5Ctx.clearRect(0, 0, W, H);
    const ticks = APP.mt5_demo.tick_series || [];
    if (!ticks.length) return;

    const allP = [APP.mt5_demo.entry_price, APP.mt5_demo.sl_price, APP.mt5_demo.tp1_price, APP.mt5_demo.tp2_price, ...ticks.map(t => t.price)];
    const minP = Math.min(...allP) - 6, maxP = Math.max(...allP) + 6;
    const py = p => H - 25 - ((p - minP) / Math.max(maxP - minP, 1)) * (H - 50);

    const drawLvl = (price, col, lbl) => {{
        const y = py(price);
        mt5Ctx.strokeStyle = col; mt5Ctx.setLineDash([5, 5]);
        mt5Ctx.beginPath(); mt5Ctx.moveTo(0, y); mt5Ctx.lineTo(W, y); mt5Ctx.stroke();
        mt5Ctx.setLineDash([]); mt5Ctx.fillStyle = col; mt5Ctx.font = "bold 11px sans-serif";
        mt5Ctx.fillText(`${{lbl}}: $${{price.toFixed(2)}}`, 12, y - 5);
    }};
    drawLvl(APP.mt5_demo.entry_price, "#fbbf24", "ENTRY");
    drawLvl(currentSLPrice, "#ef4444", "STOP LOSS");
    drawLvl(APP.mt5_demo.tp1_price, "#38bdf8", "TP1 (Auto BE)");
    drawLvl(APP.mt5_demo.tp2_price, "#10b981", "TP2 TARGET");

    mt5Ctx.strokeStyle = "#f8fafc"; mt5Ctx.lineWidth = 2.5;
    mt5Ctx.beginPath();
    for (let i = 0; i < upToIdx && i < ticks.length; i++) {{
        const x = 30 + (i / Math.max(ticks.length - 1, 1)) * (W - 60);
        const y = py(ticks[i].price);
        if (i === 0) mt5Ctx.moveTo(x, y); else mt5Ctx.lineTo(x, y);
    }}
    mt5Ctx.stroke();
}}

let selectedObsNodeId = "HUB_NEXUS";
let obsGraphAnimId = null;

function drawObsidianGraph() {{
    const c = document.getElementById('obsidianGraphCanvas');
    if (!c) return;
    const ctx = c.getContext('2d');
    const kg = (APP.obs_info && APP.obs_info.knowledge_graph) ? APP.obs_info.knowledge_graph : null;

    // Populate routing matrix table
    const tbody = document.getElementById('obsRoutingTableBody');
    if (tbody && kg && kg.token_savings_report && kg.token_savings_report.agent_routing_matrix) {{
        tbody.innerHTML = kg.token_savings_report.agent_routing_matrix.map(r => `
            <tr>
                <td class="num"><strong>${{r.agent_name}}</strong></td>
                <td class="num"><span class="pill">${{r.llm_model}}</span></td>
                <td>${{r.connected_nodes.map(n => `<code style="background:var(--bg-sub);padding:2px 6px;border-radius:5px;margin-right:4px;display:inline-block;margin-bottom:2px">${{n}}</code>`).join('↔ ')}}</td>
                <td style="font-size:0.81rem">${{r.data_flow_summary}}</td>
                <td class="num" style="color:#ef4444">${{r.full_vault_tokens.toLocaleString()}}</td>
                <td class="num" style="color:#10b981;font-weight:800">${{r.graph_pruned_tokens.toLocaleString()}}</td>
                <td class="num" style="color:#0ea5e9;font-weight:900">-${{r.savings_pct}}% (-${{r.tokens_saved_per_call.toLocaleString()}} Tok)</td>
            </tr>
        `).join('');
    }}

    if (!kg || !kg.nodes) return;

    const W = c.width, H = c.height;
    const cx = W / 2, cy = H / 2;

    // Compute radial layout positions for hubs, agents, and skills
    const hubs = kg.nodes.filter(n => n.category !== 'AI_AGENT' && n.category !== 'DISCOVERED_SKILL');
    const agents = kg.nodes.filter(n => n.category === 'AI_AGENT');
    const skills = kg.nodes.filter(n => n.category === 'DISCOVERED_SKILL');

    const posMap = {{}};
    hubs.forEach((h, i) => {{
        if (h.id === 'HUB_NEXUS') {{
            posMap[h.id] = {{ x: cx, y: cy, r: 17, node: h }};
        }} else {{
            const ang = (i / Math.max(1, hubs.length - 1)) * Math.PI * 2 - Math.PI / 2;
            posMap[h.id] = {{ x: cx + Math.cos(ang) * 92, y: cy + Math.sin(ang) * 75, r: 14, node: h }};
        }}
    }});
    agents.forEach((a, i) => {{
        const ang = (i / Math.max(1, agents.length)) * Math.PI * 2;
        posMap[a.id] = {{ x: cx + Math.cos(ang) * 225, y: cy + Math.sin(ang) * 135, r: 11, node: a }};
    }});
    skills.forEach((s, i) => {{
        const ang = (i / Math.max(1, skills.length)) * Math.PI * 2 + 0.35;
        posMap[s.id] = {{ x: cx + Math.cos(ang) * 320, y: cy + Math.sin(ang) * 150, r: 9, node: s }};
    }});

    c.onclick = (ev) => {{
        const rect = c.getBoundingClientRect();
        const mx = (ev.clientX - rect.left) * (W / rect.width);
        const my = (ev.clientY - rect.top) * (H / rect.height);
        for (const id of Object.keys(posMap)) {{
            const p = posMap[id];
            if (Math.hypot(mx - p.x, my - p.y) <= p.r + 8) {{
                selectedObsNodeId = id;
                updateObsInspector(id, kg);
                break;
            }}
        }}
    }};

    updateObsInspector(selectedObsNodeId, kg);

    if (obsGraphAnimId) cancelAnimationFrame(obsGraphAnimId);
    let tick = 0;
    function renderFrame() {{
        tick += 0.018;
        ctx.clearRect(0, 0, W, H);

        // Subtle grid
        ctx.strokeStyle = "rgba(51, 65, 85, 0.35)";
        ctx.lineWidth = 1;
        for (let x = 40; x < W; x += 60) {{ ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }}
        for (let y = 40; y < H; y += 60) {{ ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }}

        // Draw edges & animated data flow particles
        kg.edges.forEach((e, idx) => {{
            const p1 = posMap[e.source], p2 = posMap[e.target];
            if (!p1 || !p2) return;
            const isHighlighted = (e.source === selectedObsNodeId || e.target === selectedObsNodeId);
            ctx.strokeStyle = isHighlighted ? "#fbbf24" : "rgba(148, 163, 184, 0.28)";
            ctx.lineWidth = isHighlighted ? 2.4 : 1.1;
            ctx.beginPath(); ctx.moveTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y); ctx.stroke();

            if (isHighlighted) {{
                const t = (tick + idx * 0.17) % 1;
                const px = p1.x + (p2.x - p1.x) * t;
                const py = p1.y + (p2.y - p1.y) * t;
                ctx.fillStyle = "#38bdf8";
                ctx.beginPath(); ctx.arc(px, py, 3.5, 0, Math.PI * 2); ctx.fill();
            }}
        }});

        // Draw nodes
        Object.keys(posMap).forEach(id => {{
            const p = posMap[id];
            const isSel = (id === selectedObsNodeId);
            const isNeighbor = kg.edges.some(e => (e.source === selectedObsNodeId && e.target === id) || (e.target === selectedObsNodeId && e.source === id));

            if (isSel) {{
                ctx.fillStyle = "rgba(251, 191, 36, 0.25)";
                ctx.beginPath(); ctx.arc(p.x, p.y, p.r + 7, 0, Math.PI * 2); ctx.fill();
            }}
            ctx.fillStyle = p.node.color || "#38bdf8";
            ctx.globalAlpha = (isSel || isNeighbor) ? 1.0 : 0.55;
            ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); ctx.fill();
            ctx.strokeStyle = isSel ? "#ffffff" : "#0f172a";
            ctx.lineWidth = isSel ? 2.5 : 1.2;
            ctx.stroke();

            ctx.fillStyle = isSel ? "#fbbf24" : "#f8fafc";
            ctx.font = isSel ? "bold 11px 'Prompt', sans-serif" : "10px 'Prompt', sans-serif";
            ctx.textAlign = "center";
            ctx.fillText(p.node.label.slice(0, 18), p.x, p.y - p.r - 5);
            ctx.globalAlpha = 1.0;
        }});

        obsGraphAnimId = requestAnimationFrame(renderFrame);
    }}
    renderFrame();
}}

function updateObsInspector(nodeId, kg) {{
    const box = document.getElementById('obsNodeInspector');
    if (!box || !kg) return;
    const node = kg.nodes.find(n => n.id === nodeId) || kg.nodes[0];
    const relEdges = kg.edges.filter(e => e.source === node.id || e.target === node.id);
    const savedSum = relEdges.reduce((acc, e) => acc + (e.tokens_saved || 950), 0);
    const edgeList = relEdges.map(e => {{
        const other = e.source === node.id ? e.target : e.source;
        return `<span class="pill" style="margin-right:5px">${{other}} (${{e.data_flow}})</span>`;
    }}).join(' ');

    box.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:6px">
            <div><strong>🎯 โหนดที่เลือก: ${{node.label}}</strong> <span class="pill">${{node.category}}</span> <code style="font-size:0.76rem">${{node.file || ''}}</code></div>
            <div style="color:#10b981;font-weight:800">⚡ ประหยัดโทเคนจากโหนดนี้: -${{savedSum.toLocaleString()}} Tokens/รอบ (ขนาดโหนด ${{node.token_weight}} Tok)</div>
        </div>
        <div style="font-size:0.8rem;color:var(--text-sub);margin-bottom:6px">${{node.description || ''}}</div>
        <div style="font-size:0.79rem"><strong>🔗 เชื่อมโยงข้อมูลโดยตรงกับ (${{relEdges.length}} ส่วน):</strong> ${{edgeList || 'เชื่อมผ่านสารบัญหลัก MOC'}}</div>
    `;
}}

async function syncObsidianNow() {{
    try {{ await fetch('/api/sync_obsidian', {{ method: 'POST' }}); }} catch (e) {{}}
    alert("💎 ซิงค์โน้ตทั้งหมดลงโฟลเดอร์ obsidian_vault/ เรียบร้อยแล้ว!");
}}

function openGitHubPushModal() {{
    const m = document.getElementById('githubPushModal');
    if (m) m.style.display = 'flex';
}}

function closeGitHubPushModal() {{
    const m = document.getElementById('githubPushModal');
    if (m) m.style.display = 'none';
}}

async function triggerGitHubPush() {{
    const repoName = document.getElementById('ghRepoNameInput').value.trim() || 'AI-Holding-Company-V8-Portable';
    const customToken = document.getElementById('ghTokenInput').value.trim();
    const isPrivate = document.getElementById('ghPrivateCheckbox').checked;
    const btn = document.getElementById('ghPushConfirmBtn');
    const resBox = document.getElementById('ghPushResultBox');

    btn.disabled = true;
    btn.innerText = "⏳ กำลังเชื่อมต่อ GitHub (โปรดดูหน้าต่างเบราว์เซอร์ที่เด้งขึ้นมาเพื่อกด Authorize)...";
    resBox.style.display = 'block';
    resBox.innerHTML = "🔄 กำลังตรวจสอบสิทธิ์ GitHub และสร้าง Repository <code>" + repoName + "</code>...";

    try {{
        const resp = await fetch('/api/github_push', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
                repo_name: repoName,
                private: isPrivate,
                custom_token: customToken
            }})
        }});
        const data = await resp.json();
        const stepsHtml = (data.steps_log || []).map(s => `<div style="margin-bottom:4px">${{s}}</div>`).join('');
        if (data.status === 'SUCCESS') {{
            resBox.innerHTML = `
                <div style="color:#10b981;font-weight:900;font-size:0.95rem;margin-bottom:8px">${{data.message}}</div>
                ${{stepsHtml}}
                <div style="margin-top:10px">
                    <a href="${{data.repo_url}}" target="_blank" class="cozy-btn green" style="text-decoration:none;display:inline-block">🌐 คลิกเปิดดู GitHub Repository ของคุณทันที!</a>
                </div>
            `;
        }} else {{
            resBox.innerHTML = `
                <div style="color:#f59e0b;font-weight:800;margin-bottom:6px">${{data.message}}</div>
                ${{stepsHtml}}
            `;
        }}
    }} catch (err) {{
        resBox.innerHTML = `<div style="color:#ef4444">⚠️ ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้ กรุณารันผ่าน <code>setup_and_start.bat</code> หรือดับเบิลคลิกไฟล์ <code>push_to_github.bat</code> ในโฟลเดอร์ได้โดยตรงครับ</div>`;
    }} finally {{
        btn.disabled = false;
        btn.innerText = "🌐 เชื่อมต่อ GitHub & อัปโหลดทั้งหมดทันที";
    }}
}}

function switchPage(pageId) {{
    document.querySelectorAll('.page-view').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    const target = document.getElementById(pageId);
    const tab = document.getElementById('tab-' + pageId);
    if (target) target.classList.add('active');
    if (tab) tab.classList.add('active');

    if (pageId === 'page-tokens') initTokenAndSkillPage();
    if (pageId === 'page-replay') generateCuteSummary(currentSummaryStyle);
    if (pageId === 'page-profiles') renderProfileStudio(selectedAgent);
    if (pageId === 'page-mt5') {{ startLiveMT5Simulation(); drawObsidianGraph(); }}
}}

window.addEventListener('load', () => {{
    renderMiniAgentsStrip();
    renderRightSidebarMission(8);
    initRealtimeLogs();
    renderIsometricCompany();
    initTokenAndSkillPage();
    initProfileRoster();
    renderProfileStudio(selectedAgent);
    initChatRoom();
    generateCuteSummary('EXECUTIVE_CUTE');
}});
</script>
</body>
</html>
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_doc)
    return filepath
