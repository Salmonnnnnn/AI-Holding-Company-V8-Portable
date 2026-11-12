"""
AI Holding Company V5 - 4D Spatial AI HQ, Obsidian Second-Brain Sync, Multi-LLM Router & Live Copilot Chat
Main CLI & 24/7 Daemon Runner
"""
import os
import sys
import time

# Ensure UTF-8 output on Windows console
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import argparse
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv

from engine.committee_room import TradingCommitteeRoom
from engine.dashboard_generator import generate_html_dashboard
from notifier.telegram_bot import TelegramNotifier

load_dotenv()
console = Console(force_terminal=True, highlight=False)


def save_markdown_report(report: dict, filepath: str):
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
    obs_sync = report.get("obsidian_status", {})

    roster_lines = []
    for ag in office.get("agents_roster", []):
        roster_lines.append(
            f"| {ag.get('avatar')} **{ag.get('name')}** (`Lv.{ag.get('level', 10)}`) | `{ag.get('llm_model', 'gemini-2.5-flash')}` | `{ag.get('mastery_pct', 90)}%` (+{ag.get('accuracy_bonus_pct', 7)}% Acc) | `{ag.get('primary_skill')}` | {ag.get('current_task')} |"
        )
    roster_md = "\n".join(roster_lines)

    core_lines = []
    for ck in skill_rep.get("central_knowledge_core", [])[:6]:
        core_lines.append(
            f"- **🧠 [{ck.get('contributor_agent')}] {ck.get('insight_title')}** -> `{ck.get('learned_parameters')}` *(+{ck.get('confidence_boost')}% Edge)*"
        )
    core_md = "\n".join(core_lines)

    mt5_lines = []
    for st in mt5_demo.get("steps_telemetry", []):
        mt5_lines.append(
            f"{st.get('step')}. **{st.get('phase')}** (`{st.get('status')}`)\n   - โค้ดคำสั่ง: `{st.get('code')}`\n   - รายละเอียด: {st.get('detail')}"
        )
    mt5_md = "\n".join(mt5_lines)

    strat_lines = []
    for s in bench.get("all_strategies", []):
        strat_lines.append(
            f"| **{s.get('strategy_name')}** | `{s.get('best_regime')}` | {s.get('published_win_rate')}% (PF {s.get('published_pf')}) | **{s.get('live_win_rate')}%** ({s.get('live_trades')} ไม้) | **{s.get('live_pf')}** | `{s.get('live_net_r'):+}R` | `{s.get('live_signal_now')}` |"
        )
    strat_md = "\n".join(strat_lines)

    md_content = f"""# 🌌 รายงานบริษัท AI เสมือนจริง V5: 4D Spatial HQ, Obsidian Vault Sync & Multi-LLM Brains
**วันเวลาที่ประมวลผล:** {report['session_time']}  
**เลเวลรวมของทีม AI:** `Lv.{skill_rep.get('team_total_level', 123)}` | **ค่าความชำนาญเฉลี่ย (Avg Mastery):** `{skill_rep.get('average_mastery_pct', 90.6)}%`  
**Obsidian Second-Brain Vault:** `{obs_sync.get('vault_path', 'obsidian_vault')}` (ซิงก์แล้ว `{obs_sync.get('files_synced_count', 0)}` ไฟล์ Markdown พร้อม `[[Wikilinks]]`)  
**มติชี้ขาด (CIO Verdict):** `{cio['action']}` (ความเชื่อมั่น {cio.get('conviction_pct', 70)}% | คะแนนรวม {cio.get('weighted_score', 0):+.1f})

---

## 1. แผนผังพนักงาน AI, สมอง Multi-LLM และสกิลเฉพาะทาง (24/7 AI Roster & Multi-LLM Brains)

| พนักงาน AI (Level) | สมอง LLM ที่เชื่อมต่อ (LLM Brain) | ความชำนาญ (Mastery) | สกิลหลัก (Primary Skill) | ภารกิจล่าสุด |
|---|---|---|---|---|
{roster_md}

### 🧠 ข้อมูลที่ AI วิ่งนำมาส่งเข้าแกนกลางบริษัท (Central Knowledge Nexus Core):
{core_md}

---

## 2. การเชื่อมต่อ MetaTrader 5 (MT5) & ผลจำลองยิงออเดอร์ Demo สดๆ 8 ขั้นตอน
- **Ticket จำลอง:** `#{mt5_demo.get('ticket_id')}` | **คำสั่ง:** `{mt5_demo.get('direction')} {mt5_demo.get('lot_size')} Lot` @ `${mt5_demo.get('entry_price'):,.2f}`
- **Stop Loss เริ่มต้น:** `${mt5_demo.get('sl_price'):,.2f}` -> **ขยับบังทุนอัตโนมัติ (Break-Even)** เมื่อแตะ TP1 (`${mt5_demo.get('tp1_price'):,.2f}`)
- **เป้าหมาย TP2:** `${mt5_demo.get('tp2_price'):,.2f}` | **กำไรสุทธิจากการทดสอบ Demo:** **`+${mt5_demo.get('demo_profit_dollar', 0):,.2f}`**

### ⚡ ลำดับการทำงานของบอทกับ MT5 ทีละขั้นตอน (8-Step Execution Telemetry):
{mt5_md}

---

## 3. ผลทดสอบเปรียบเทียบ 4 กลยุทธ์วิจัยระดับโลก (Proven Quant Strategy Benchmark Lab)
{bench.get('auditor_summary', '')}

| ชื่อกลยุทธ์มาตรฐาน (Proven Strategy) | สภาวะตลาดที่ถนัด | สถิติงานวิจัย (Benchmark) | ความแม่นยำทดสอบจริง (Live Win Rate) | Profit Factor จริง | ผลตอบแทนสุทธิ (Net R) | สัญญาณปัจจุบัน |
|---|---|---|---|---|---|---|
{strat_md}

---

## 4. บทสรุปห้องดีเบต & มติชี้ขาดขั้นสุดท้าย (The Debate & CIO Final Verdict)
- **ศึกดีเบต Bull Advocate ({deb.get('bull_power')}%) vs. Bear & Red Team ({deb.get('bear_power')}%):**  
{deb['debate_critique']}

### 👑 มติชี้ขาดโดย CIO ({cio['cio_name']}):
> **🎯 คำสั่ง: {cio['action']}**  
> **Entry:** `${cio['final_entry']:,.2f}` | **Stop Loss:** `${cio['final_sl']:,.2f}` | **TP1:** `${cio['final_tp1']:,.2f}` | **TP2:** `${cio['final_tp2']:,.2f}` | **Lot Size:** `{cio['recommended_lot']} Lot`

{cio['executive_summary']}
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)


def run_once(args):
    console.print(Panel.fit(
        "[bold gold1]🌌  AI HOLDING COMPANY V5: 4D SPATIAL HQ, OBSIDIAN VAULT SYNC & MULTI-LLM ROUTER[/bold gold1]\n"
        "[italic cyan]Three.js 4D Building • Claude/Gemini/DeepSeek/Groq Brains • Obsidian Second-Brain • Cute Time-Machine & Live Copilot Chat[/italic cyan]",
        border_style="yellow"
    ))

    with console.status("[bold green]กำลังเดินเครื่องสำนักงาน AI 4D V5, เชื่อมสมอง Multi-LLM, ซิงก์ Obsidian Vault และจำลองยิงออเดอร์ MT5 Demo...", spinner="dots"):
        room = TradingCommitteeRoom()
        if args.add_division:
            div_id, div_name, div_desc = args.add_division
            room.db.add_business_division(div_id, div_name, "Nova Vance (Venture Architect)", "ACTIVE (NEW VENTURE)", div_desc, "Custom KPI")
        report = room.run_session(capital=args.capital, risk_pct=args.risk)

    cio = report["cio_verdict"]
    office = report["office_digest"]
    skill_rep = report["skill_training_report"]
    mt5_demo = report["mt5_demo_telemetry"]
    obs_sync = report.get("obsidian_status", {})

    # 1. ตารางพนักงาน AI + สมอง LLM + เลเวล + สกิล
    office_table = Table(title=f"🧠 1. พนักงาน AI ทั้ง 11 ตัว & สมอง Multi-LLM ที่เชื่อมต่อ (Team Total Lv.{skill_rep.get('team_total_level')} | Avg Mastery {skill_rep.get('average_mastery_pct')}%)", border_style="cyan")
    office_table.add_column("พนักงาน AI", style="bold white")
    office_table.add_column("สมอง LLM (Brain Model)", style="bold magenta")
    office_table.add_column("Level & EXP", style="bold gold1", justify="center")
    office_table.add_column("Mastery (+Acc)", style="bold green", justify="right")
    office_table.add_column("สกิลหลักที่ติดตั้ง", style="cyan")

    for ag in office.get("agents_roster", []):
        office_table.add_row(
            f"{ag.get('avatar')} {ag.get('name')}",
            str(ag.get("llm_model", "gemini-2.5-flash")),
            f"Lv.{ag.get('level')} ({ag.get('exp')}/{ag.get('max_exp')})",
            f"{ag.get('mastery_pct')}% (+{ag.get('accuracy_bonus_pct')}%)",
            str(ag.get("primary_skill"))
        )
    console.print(office_table)
    console.print("\n")

    # 2. Obsidian Second-Brain Sync Status
    console.print(Panel(
        f"📂 [bold cyan]Obsidian Vault Directory:[/bold cyan] {obs_sync.get('vault_path')}\n"
        f"📝 [bold green]จำนวนไฟล์ Markdown ที่ซิงก์สำเร็จ:[/bold green] {obs_sync.get('files_synced_count')} ไฟล์ (พร้อม YAML Frontmatter + [[Wikilinks]])\n"
        f"🔗 [bold yellow]เปิดดูในแอป Obsidian ทันที:[/bold yellow] {obs_sync.get('obsidian_uri')}",
        title="[bold magenta]💎 2. ระบบเชื่อมต่อสมองที่สอง Obsidian Second-Brain Vault Sync[/bold magenta]",
        border_style="magenta"
    ))

    # 3. มติ CIO
    decision_color = "green" if "BUY" in cio['action'] and "WAIT" not in cio['action'] else (
        "red" if "SELL" in cio['action'] and "WAIT" not in cio['action'] else "yellow"
    )
    console.print(Panel(
        f"[bold {decision_color}]🎯 มติคำสั่งขั้นสุดท้าย: {cio['action']}[/bold {decision_color}]\n"
        f"📍 [bold]Entry:[/bold] ${cio['final_entry']:,.2f} | 🛑 [bold]SL (1.5x ATR):[/bold] ${cio['final_sl']:,.2f} | 🎯 [bold]TP1:[/bold] ${cio['final_tp1']:,.2f} | 🚀 [bold]TP2:[/bold] ${cio['final_tp2']:,.2f} | 📦 [bold]Lot:[/bold] {cio['recommended_lot']} Lot\n"
        f"--------------------------------------------------\n"
        f"{cio['executive_summary']}",
        title="[bold gold1]👑 3. มติชี้ขาดคณะกรรมการ (CIO Final Verdict)[/bold gold1]",
        border_style="gold1"
    ))

    os.makedirs("reports", exist_ok=True)
    ts_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"reports/session_{ts_str}.md"
    latest_md = "reports/latest_report.md"
    dashboard_file = "reports/latest_dashboard.html"

    save_markdown_report(report, report_filename)
    save_markdown_report(report, latest_md)
    generate_html_dashboard(report, dashboard_file)

    console.print(f"[bold green]✓ บันทึกรายงานสำนักงาน V5 ไว้ที่:[/bold green] {report_filename} และ {latest_md}")
    console.print(f"[bold cyan]✓ สร้างเว็บแอป 6 หน้า (4D Spatial HQ + AI Profile Studio + Cute Time-Machine + Live Chat + MT5 Demo + Obsidian Graph) ไว้ที่:[/bold cyan] {dashboard_file}")

    if args.notify_telegram:
        notifier = TelegramNotifier()
        if notifier.is_configured():
            notifier.send_summary(report)


def main():
    parser = argparse.ArgumentParser(description="AI Holding Company V5 — 4D Spatial HQ, Obsidian Sync, Multi-LLM Router & Live Chat")
    parser.add_argument("--capital", type=float, default=float(os.getenv("ACCOUNT_CAPITAL", 1000.0)), help="เงินทุนในพอร์ต ($)")
    parser.add_argument("--risk", type=float, default=float(os.getenv("RISK_PERCENT", 1.5)), help="ความเสี่ยงต่อไม้ (%)")
    parser.add_argument("--notify-telegram", action="store_true", help="ส่งสรุปเข้า Telegram ทันที")
    parser.add_argument("--daemon", action="store_true", help="รันสำนักงาน AI ต่อเนื่องตลอด 24 ชม.")
    parser.add_argument("--interval", type=int, default=300, help="รอบเวลาอัปเดตในโหมด 24 ชม. (วินาที)")
    parser.add_argument("--add-division", nargs=3, metavar=("ID", "NAME", "DESC"), help="เพิ่มแผนกธุรกิจใหม่เข้าบริษัท AI")
    args = parser.parse_args()

    if args.daemon:
        console.print(f"[bold green]🚀 เริ่มเดินเครื่องสำนักงาน AI V5 โหมด 24/7 Continuous Daemon (อัปเดตทุก {args.interval} วินาที)...[/bold green]")
        while True:
            run_once(args)
            time.sleep(args.interval)
    else:
        run_once(args)


if __name__ == "__main__":
    main()
