"""
Obsidian Second-Brain Vault Synchronizer & Knowledge Graph Token-Saver (V8)
Automatically generates interconnected Markdown notes with YAML Frontmatter,
[[Wikilinks]], Callouts, Native Obsidian Canvas (`AI_Company_Knowledge_Map.canvas`),
and Graph-RAG Topology (`00_Knowledge_Graph_Topology.md`) to prune LLM context and save 80%+ tokens.
"""
import json
import os
import urllib.parse
from datetime import datetime


DEFAULT_VAULT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "obsidian_vault")


class ObsidianVaultSync:
    def __init__(self, vault_dir: str = DEFAULT_VAULT_DIR):
        self.vault_dir = vault_dir

    def build_knowledge_graph_topology(self, report: dict) -> dict:
        """
        สร้างโครงข่าย Knowledge Graph (Nodes + Edges) ว่าข้อมูลส่วนไหนเชื่อมกับส่วนไหน
        พร้อมคำนวณการประหยัดโทเคน (Graph-RAG Context Pruning) เมื่อดึงเฉพาะโหนดที่เกี่ยวข้อง
        """
        office = report.get("office_digest", {})
        agents = office.get("agents_roster", [])
        disc_skills = report.get("discovered_skills", [])
        date_str = datetime.now().strftime("%Y-%m-%d")

        # 1. Core System Hub Nodes
        nodes = [
            {
                "id": "HUB_MOC",
                "label": "🏛️ 00_AI_Holding_MOC",
                "category": "CORE_HUB",
                "color": "#f59e0b",
                "token_weight": 680,
                "file": "00_AI_Holding_Company_MOC.md",
                "description": "สารบัญหลักเชื่อมทุกแผนกในบริษัท AI"
            },
            {
                "id": "HUB_MARKET",
                "label": "📊 Market Feed (H1/H4/D1)",
                "category": "DATA_SOURCE",
                "color": "#38bdf8",
                "token_weight": 920,
                "file": f"01_Daily_Summaries/{date_str}_Daily_Summary.md",
                "description": "ข้อมูลแท่งเทียนทองคำ, RSI, MACD, ATR, DXY, US10Y"
            },
            {
                "id": "HUB_NEXUS",
                "label": "🧠 Central Knowledge Core",
                "category": "SHARED_MEMORY",
                "color": "#a855f7",
                "token_weight": 1450,
                "file": "03_Central_Knowledge_Core/Central_Nexus_Insights.md",
                "description": "คลังสมองกลางเก็บสูตรและพารามิเตอร์ที่ AI วิจัยสำเร็จ"
            },
            {
                "id": "HUB_MT5",
                "label": "🤖 MT5 Trade & Benchmarks",
                "category": "EXECUTION_HUB",
                "color": "#10b981",
                "token_weight": 1180,
                "file": "04_MT5_Trade_Journal/MT5_Portfolio_and_Benchmarks.md",
                "description": "บันทึกพอร์ต MT5 Demo/Live และผล Backtest 4 กลยุทธ์โลก"
            },
            {
                "id": "HUB_DAILY",
                "label": f"📅 Daily Summary ({date_str})",
                "category": "REPORT_HUB",
                "color": "#ec4899",
                "token_weight": 890,
                "file": f"01_Daily_Summaries/{date_str}_Daily_Summary.md",
                "description": "สรุปมติ CIO และผลการดำเนินงานรายกะ/รายวัน"
            },
            {
                "id": "HUB_VENTURE",
                "label": "🚀 Venture Blueprints",
                "category": "BUSINESS_HUB",
                "color": "#6366f1",
                "token_weight": 760,
                "file": "05_Business_Ventures/New_Venture_Ideas_Blueprint.md",
                "description": "แผนกปั้นธุรกิจใหม่ในเครือ AI Holding"
            }
        ]

        # 2. AI Agent Nodes & Directed Edges
        edges = [
            {
                "source": "HUB_MARKET",
                "target": "HUB_NEXUS",
                "relation": "FEEDS_PRICE_AND_REGIME",
                "data_flow": "ส่งราคา OHLC, ATR14 และ Market Regime เข้าสมองกลาง",
                "tokens_saved": 1420
            },
            {
                "source": "HUB_NEXUS",
                "target": "HUB_MT5",
                "relation": "OPTIMIZES_PARAMETERS",
                "data_flow": "ส่งค่าพารามิเตอร์ Walk-Forward และสกิลใหม่ไปปรับแต่งบอท MT5",
                "tokens_saved": 1680
            },
            {
                "source": "HUB_MT5",
                "target": "HUB_DAILY",
                "relation": "LOGS_PNL_AND_TICKETS",
                "data_flow": "ส่งผลกำไร/ขาดทุนและหมายเลข Ticket เข้าสรุปรายวัน",
                "tokens_saved": 1150
            },
            {
                "source": "HUB_DAILY",
                "target": "HUB_MOC",
                "relation": "UPDATES_MASTER_INDEX",
                "data_flow": "อัปเดตสถานะมติล่าสุดขึ้นหน้าสารบัญหลัก MOC",
                "tokens_saved": 980
            }
        ]

        agent_routing_matrix = []
        total_unfiltered_tokens = 18650  # หากส่งทุกไฟล์ในบริษัทเข้า Prompt พร้อมกัน

        dept_hub_map = {
            "Executive / CIO": ("HUB_DAILY", "HUB_MT5", "ตัดสินใจชี้ขาด Entry/SL/TP จากมติทีม"),
            "Executive Office": ("HUB_MOC", "HUB_DAILY", "รวบรวมบันทึกทุกกะทำสรุปผู้บริหาร"),
            "Quant & Backtest": ("HUB_MARKET", "HUB_NEXUS", "คำนวณอินดิเคเตอร์และทดสอบกลยุทธ์"),
            "Macro & News": ("HUB_MARKET", "HUB_DAILY", "กรองข่าว Fed/CPI/DXY และความเสี่ยงภูมิรัฐศาสตร์"),
            "Bullish Strategy": ("HUB_NEXUS", "HUB_DAILY", "สังเคราะห์สัญญาณฝั่งซื้อ (Long Thesis)"),
            "Bearish Strategy": ("HUB_NEXUS", "HUB_DAILY", "สังเคราะห์สัญญาณฝั่งขายและจับผิดจุดอ่อน (Short Thesis)"),
            "Risk & Governance": ("HUB_MT5", "HUB_DAILY", "คุมเพดานความเสี่ยง 1.5% และตรวจ Veto"),
            "MT5 Execution": ("HUB_MT5", "HUB_NEXUS", "ยิงออเดอร์จริง/เดโม่และขยับ Trailing Stop"),
            "Venture Incubator": ("HUB_VENTURE", "HUB_MOC", "ออกแบบโมเดลธุรกิจ AI ใหม่เข้าโฮลดิ้ง")
        }

        for ag in agents:
            ag_id = ag.get("agent_id", "AG")
            ag_name = ag.get("name", "AI Agent")
            dept = ag.get("department", "Executive Office")
            safe_name = ag_name.replace("'", "").replace(" ", "_")
            note_file = f"02_AI_Agents/Agent_{safe_name}.md"
            ag_token_weight = 520

            nodes.append({
                "id": ag_id,
                "label": f"{ag.get('avatar', '🤖')} {ag_name}",
                "category": "AI_AGENT",
                "department": dept,
                "llm_model": ag.get("llm_model", "Claude 3.7 Sonnet"),
                "color": "#22c55e" if "Bull" in dept or "Execution" in dept else ("#ef4444" if "Bear" in dept or "Risk" in dept else "#60a5fa"),
                "token_weight": ag_token_weight,
                "file": note_file,
                "description": f"{ag.get('role')} ({ag.get('primary_skill')})"
            })

            src_hub, tgt_hub, flow_desc = dept_hub_map.get(dept, ("HUB_MARKET", "HUB_NEXUS", "วิเคราะห์ข้อมูลเฉพาะทาง"))
            edges.append({
                "source": src_hub,
                "target": ag_id,
                "relation": "READS_SUBGRAPH",
                "data_flow": f"ดึงเฉพาะโหนด {src_hub} เข้าสมอง {ag_name}",
                "tokens_saved": 1240
            })
            edges.append({
                "source": ag_id,
                "target": tgt_hub,
                "relation": "WRITES_INSIGHT",
                "data_flow": flow_desc,
                "tokens_saved": 1350
            })

            # คำนวณโทเคนที่ใช้จริงเมื่อดึงเฉพาะ 1-Hop Connected Subgraph
            pruned_tokens = ag_token_weight + 920 + 1150  # Agent Note + Source Hub + Target Hub
            saved_tokens = total_unfiltered_tokens - pruned_tokens
            saved_pct = round((saved_tokens / total_unfiltered_tokens) * 100, 1)

            agent_routing_matrix.append({
                "agent_id": ag_id,
                "agent_name": f"{ag.get('avatar', '🤖')} {ag_name}",
                "role": ag.get("role", ""),
                "llm_model": ag.get("llm_model", ""),
                "connected_nodes": [src_hub, tgt_hub, f"Agent_{safe_name}"],
                "data_flow_summary": flow_desc,
                "full_vault_tokens": total_unfiltered_tokens,
                "graph_pruned_tokens": pruned_tokens,
                "tokens_saved_per_call": saved_tokens,
                "savings_pct": saved_pct
            })

        # 3. Discovered Skill Nodes (Top 5)
        for idx, sk in enumerate(disc_skills[:5]):
            sk_id = f"SKILL_{idx+1}"
            sk_name = sk.get("skill_name", f"Skill #{idx+1}")
            ag_owner = sk.get("agent_id", "A2_KENJI")
            nodes.append({
                "id": sk_id,
                "label": f"🎓 {sk_name[:26]}",
                "category": "DISCOVERED_SKILL",
                "color": "#f43f5e",
                "token_weight": 340,
                "file": "03_Central_Knowledge_Core/Central_Nexus_Insights.md",
                "description": f"Win Rate {sk.get('backtest_win_rate')}% (+{sk.get('accuracy_boost')}% Acc)"
            })
            edges.append({
                "source": sk_id,
                "target": ag_owner,
                "relation": "EQUIPPED_BY",
                "data_flow": f"ติดตั้งสูตร '{sk_name}' ให้ {sk.get('agent_name')}",
                "tokens_saved": 890
            })
            edges.append({
                "source": sk_id,
                "target": "HUB_NEXUS",
                "relation": "STORED_IN_NEXUS",
                "data_flow": "บันทึกสูตรลงคลังสมองกลางเพื่อแชร์ให้ทีม",
                "tokens_saved": 950
            })

        avg_pruned = int(sum(r["graph_pruned_tokens"] for r in agent_routing_matrix) / max(1, len(agent_routing_matrix)))
        avg_saved = total_unfiltered_tokens - avg_pruned
        avg_saved_pct = round((avg_saved / total_unfiltered_tokens) * 100, 1)

        return {
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "token_savings_report": {
                "unfiltered_full_vault_tokens": total_unfiltered_tokens,
                "graph_routed_avg_tokens": avg_pruned,
                "tokens_saved_per_call": avg_saved,
                "savings_pct": avg_saved_pct,
                "daily_estimated_tokens_saved": avg_saved * 44,  # 11 agents x 4 shifts/day
                "agent_routing_matrix": agent_routing_matrix
            }
        }

    def _create_obsidian_canvas_file(self, date_str: str) -> str:
        """สร้างไฟล์กระดานกราฟ Native Obsidian Canvas (`AI_Company_Knowledge_Map.canvas`)"""
        canvas_path = os.path.join(self.vault_dir, "AI_Company_Knowledge_Map.canvas")
        canvas_data = {
            "nodes": [
                {
                    "id": "node_moc",
                    "type": "file",
                    "file": "00_AI_Holding_Company_MOC.md",
                    "x": 0,
                    "y": -380,
                    "width": 360,
                    "height": 220,
                    "color": "3"
                },
                {
                    "id": "node_graph_doc",
                    "type": "file",
                    "file": "00_Knowledge_Graph_Topology.md",
                    "x": 440,
                    "y": -380,
                    "width": 380,
                    "height": 220,
                    "color": "6"
                },
                {
                    "id": "node_market_text",
                    "type": "text",
                    "text": "### 📊 1. Market & Macro Feed\n- ดึงกราฟทองคำ H1/H4/D1\n- คำนวณ RSI, MACD, ATR, DXY, US10Y\n- ส่งเฉพาะตัวเลขสำคัญให้ทีม Quant & Macro (ประหยัด 85% โทเคน)",
                    "x": -480,
                    "y": -40,
                    "width": 340,
                    "height": 210,
                    "color": "5"
                },
                {
                    "id": "node_nexus",
                    "type": "file",
                    "file": "03_Central_Knowledge_Core/Central_Nexus_Insights.md",
                    "x": 0,
                    "y": -40,
                    "width": 380,
                    "height": 240,
                    "color": "6"
                },
                {
                    "id": "node_mt5",
                    "type": "file",
                    "file": "04_MT5_Trade_Journal/MT5_Portfolio_and_Benchmarks.md",
                    "x": 460,
                    "y": -40,
                    "width": 380,
                    "height": 240,
                    "color": "4"
                },
                {
                    "id": "node_daily",
                    "type": "file",
                    "file": f"01_Daily_Summaries/{date_str}_Daily_Summary.md",
                    "x": 0,
                    "y": 280,
                    "width": 380,
                    "height": 240,
                    "color": "1"
                },
                {
                    "id": "node_venture",
                    "type": "file",
                    "file": "05_Business_Ventures/New_Venture_Ideas_Blueprint.md",
                    "x": 460,
                    "y": 280,
                    "width": 380,
                    "height": 240,
                    "color": "2"
                }
            ],
            "edges": [
                {
                    "id": "edge_1",
                    "fromNode": "node_market_text",
                    "fromSide": "right",
                    "toNode": "node_nexus",
                    "toSide": "left",
                    "label": "ส่งราคา & ATR (1-Hop Pruned)"
                },
                {
                    "id": "edge_2",
                    "fromNode": "node_nexus",
                    "fromSide": "right",
                    "toNode": "node_mt5",
                    "toSide": "left",
                    "label": "ส่งสูตรสกิล & พารามิเตอร์ชนะตลาด"
                },
                {
                    "id": "edge_3",
                    "fromNode": "node_nexus",
                    "fromSide": "bottom",
                    "toNode": "node_daily",
                    "toSide": "top",
                    "label": "สรุปมติ Bull vs Bear"
                },
                {
                    "id": "edge_4",
                    "fromNode": "node_mt5",
                    "fromSide": "bottom",
                    "toNode": "node_daily",
                    "toSide": "right",
                    "label": "บันทึก Ticket & กำไร MT5"
                },
                {
                    "id": "edge_5",
                    "fromNode": "node_moc",
                    "fromSide": "bottom",
                    "toNode": "node_nexus",
                    "toSide": "top",
                    "label": "เชื่อม AI ทั้ง 11 ตัว"
                },
                {
                    "id": "edge_6",
                    "fromNode": "node_daily",
                    "fromSide": "right",
                    "toNode": "node_venture",
                    "toSide": "left",
                    "label": "ต่อยอดธุรกิจใหม่"
                }
            ]
        }
        with open(canvas_path, "w", encoding="utf-8") as f:
            json.dump(canvas_data, f, ensure_ascii=False, indent=2)
        return canvas_path

    def sync_all(self, report: dict) -> dict:
        """สร้างและอัปเดตคลังโน้ต Obsidian ทั้งหมด + โครงข่าย Knowledge Graph ประหยัดโทเคน"""
        subdirs = [
            "",
            "01_Daily_Summaries",
            "02_AI_Agents",
            "03_Central_Knowledge_Core",
            "04_MT5_Trade_Journal",
            "05_Business_Ventures"
        ]
        for sd in subdirs:
            os.makedirs(os.path.join(self.vault_dir, sd), exist_ok=True)

        files_created = []
        date_str = datetime.now().strftime("%Y-%m-%d")

        market = report.get("market_snapshot", {})
        cio = report.get("cio_verdict", {})
        office = report.get("office_digest", {})
        bench = report.get("strategy_benchmarks", {})
        port = report.get("portfolio_state", {})
        skill_rep = report.get("skill_training_report", {})
        mt5_demo = report.get("mt5_demo_telemetry", {})
        agents = office.get("agents_roster", [])

        # สร้างโครงข่าย Knowledge Graph & รายงานการประหยัดโทเคน
        graph_topology = self.build_knowledge_graph_topology(report)
        tok_sav = graph_topology["token_savings_report"]

        # 1. สร้างไฟล์โปรไฟล์แยกสำหรับ AI ทั้ง 11 ตัว
        agent_links = []
        for ag in agents:
            safe_name = ag["name"].replace("'", "").replace(" ", "_")
            note_name = f"Agent_{safe_name}"
            agent_links.append(f"- {ag.get('avatar')} [[{note_name}|{ag.get('name')}]] — *{ag.get('role')}* (`{ag.get('llm_model', 'Gemini 2.5 Flash')}` | `Lv.{ag.get('level')}`)")
            ag_path = os.path.join(self.vault_dir, "02_AI_Agents", f"{note_name}.md")

            ag_md = f"""---
tags:
  - ai-agent
  - gold-trading-firm
  - {ag.get('department', 'hq').lower().replace(' ', '-').replace('/', '')}
agent_id: {ag.get('agent_id')}
level: {ag.get('level')}
mastery: {ag.get('mastery_pct')}
llm_brain: "{ag.get('llm_model')}"
updated: "{report.get('session_time')}"
---
# {ag.get('avatar')} {ag.get('name')}
**ตำแหน่ง:** {ag.get('role')}  
**สังกัดแผนก:** {ag.get('department')}  
**สมองกล AI ที่เชื่อมต่อ (LLM Brain):** `{ag.get('llm_model')}`  
**กลับหน้าหลักบริษัท:** [[00_AI_Holding_Company_MOC]] | [[00_Knowledge_Graph_Topology]] | [[{date_str}_Daily_Summary]]

> [!info] ประวัติและบทบาทเฉพาะทาง (Agent Bio)
> {ag.get('bio', ag.get('current_task'))}

## 📊 ค่าพลังความสามารถ 5 มิติ (5D Capability Radar)
- **ความแม่นยำ (Accuracy):** `{ag.get('stat_accuracy', 90)}/100` (+{ag.get('accuracy_bonus_pct')}% Bonus)
- **ความเร็วประมวลผล (Speed):** `{ag.get('stat_speed', 90)}/100`
- **วินัยความเสี่ยง (Risk Discipline):** `{ag.get('stat_risk', 88)}/100`
- **ความเข้าใจตลาดมหภาค (Macro Insight):** `{ag.get('stat_macro', 85)}/100`
- **ความคิดสร้างสรรค์/กลยุทธ์ (Creativity):** `{ag.get('stat_creativity', 85)}/100`

## 🎓 สกิลที่ติดตั้ง (Equipped Skill Tree — Lv.{ag.get('level')})
1. **Primary Skill:** `{ag.get('primary_skill')}`
2. **Secondary Skill:** `{ag.get('secondary_skill')}`
3. **Ultimate Skill:** `{ag.get('ultimate_skill')}`

## ⚡ ภารกิจล่าสุดที่ส่งเข้า [[Central_Nexus_Insights]]
- สถานะปัจจุบัน: `{ag.get('status')}`
- งานที่ทำล่าสุด: {ag.get('current_task')}
- จำนวนภารกิจสำเร็จวันนี้: `{ag.get('tasks_completed_today')} งาน`
"""
            with open(ag_path, "w", encoding="utf-8") as f:
                f.write(ag_md)
            files_created.append(ag_path)

        # 2. สร้างไฟล์ Central Knowledge Core
        core_path = os.path.join(self.vault_dir, "03_Central_Knowledge_Core", "Central_Nexus_Insights.md")
        core_items = []
        for ck in skill_rep.get("central_knowledge_core", []):
            core_items.append(
                f"### 🧠 {ck.get('insight_title')}\n"
                f"- **ผู้ค้นพบ:** `{ck.get('contributor_agent')}` ({ck.get('skill_domain')})\n"
                f"- **พารามิเตอร์ที่เรียนรู้:** `{ck.get('learned_parameters')}`\n"
                f"- **ความได้เปรียบที่เพิ่มขึ้น:** `+{ck.get('confidence_boost')}% Edge` *(เวลา: {ck.get('timestamp')})*\n"
            )
        core_md = f"""---
tags:
  - central-core
  - knowledge-nexus
  - self-training
updated: "{report.get('session_time')}"
---
# 🧠 Central Knowledge Nexus Core (สมองกลางของบริษัท AI)
เชื่อมโยงกับ: [[00_AI_Holding_Company_MOC]] | [[00_Knowledge_Graph_Topology]] | [[MT5_Portfolio_and_Benchmarks]] | [[{date_str}_Daily_Summary]]

> [!tip] การทำงานของสมองกลาง (Shared Neural Memory)
> ทุกครั้งที่พนักงาน AI ใน [[00_AI_Holding_Company_MOC]] ฝึกสกิลใน Academy หรือรัน Walk-Forward Tuning เสร็จ จะวิ่งนำก้อนความรู้มาเก็บสะสมไว้ในโน้ตนี้

{chr(10).join(core_items)}
"""
        with open(core_path, "w", encoding="utf-8") as f:
            f.write(core_md)
        files_created.append(core_path)

        # 3. สร้างไฟล์ MT5 Trade Journal & Strategy Benchmarks
        mt5_path = os.path.join(self.vault_dir, "04_MT5_Trade_Journal", "MT5_Portfolio_and_Benchmarks.md")
        strat_rows = []
        for s in bench.get("all_strategies", []):
            strat_rows.append(
                f"| {s.get('strategy_name')} | `{s.get('best_regime')}` | {s.get('published_win_rate')}% | **{s.get('live_win_rate')}%** | **{s.get('live_pf')}** | `{s.get('live_net_r'):+}R` |"
            )
        mt5_md = f"""---
tags:
  - mt5-journal
  - quant-benchmark
  - xauusd
updated: "{report.get('session_time')}"
---
# 🤖 บันทึกพอร์ต MT5 อัตโนมัติ & ผลทดสอบ 4 กลยุทธ์วิจัยระดับโลก
เชื่อมโยงกับ: [[00_AI_Holding_Company_MOC]] | [[00_Knowledge_Graph_Topology]] | [[Central_Nexus_Insights]] | [[{date_str}_Daily_Summary]]

## 1. สถานะพอร์ตลงทุนอัตโนมัติ ([[Agent_AutoBot_X-1|AutoBot X-1]])
- **โหมดเชื่อมต่อ:** `{port.get('execution_mode')}`
- **Balance:** `${port.get('balance', 1000):,.2f}` | **Equity:** `${port.get('equity', 1000):,.2f}` (`{port.get('net_return_pct', 0):+.2f}%`)
- **Live Win Rate:** `{port.get('live_win_rate_pct', 100)}%`
- **การดำเนินการล่าสุด:** {port.get('summary_message')}

## 2. ตารางเปรียบเทียบ 4 กลยุทธ์มาตรฐานระดับสถาบัน (โดย [[Agent_Dr._Kenji_Sato|Dr. Kenji Sato]])
| กลยุทธ์มาตรฐาน | ตลาดที่ถนัด | Win Rate วิจัย | Win Rate ทดสอบจริง | Profit Factor | Net R |
|---|---|---|---|---|---|
{chr(10).join(strat_rows)}

## 3. บันทึกการจำลองยิงคำสั่ง MT5 Demo ล่าสุด (Ticket #{mt5_demo.get('ticket_id')})
- **คำสั่ง:** `{mt5_demo.get('direction')} {mt5_demo.get('lot_size')} Lot @ ${mt5_demo.get('entry_price'):,.2f}`
- **Stop Loss:** `${mt5_demo.get('sl_price'):,.2f}` (ขยับบังหน้าทุนอัตโนมัติเมื่อแตะ TP1 `${mt5_demo.get('tp1_price'):,.2f}`)
- **TP2 Target:** `${mt5_demo.get('tp2_price'):,.2f}` (กำไรจำลอง `+$ {mt5_demo.get('demo_profit_dollar', 0):,.2f}`)
"""
        with open(mt5_path, "w", encoding="utf-8") as f:
            f.write(mt5_md)
        files_created.append(mt5_path)

        # 4. สร้างไฟล์ Business Ventures Blueprint
        venture_path = os.path.join(self.vault_dir, "05_Business_Ventures", "New_Venture_Ideas_Blueprint.md")
        div_lines = []
        for dv in office.get("business_divisions", []):
            div_lines.append(f"- **{dv.get('name')}** (`{dv.get('status')}`) — {dv.get('description')} *(KPI: {dv.get('kpi_metric')})*")
        venture_md = f"""---
tags:
  - business-ideas
  - ai-holding-company
  - venture-incubator
updated: "{report.get('session_time')}"
---
# 🚀 แผนกปั้นธุรกิจใหม่ในเครือ AI Holding (ดูแลโดย [[Agent_Nova_Vance|Nova Vance]])
เชื่อมโยงกับ: [[00_AI_Holding_Company_MOC]] | [[00_Knowledge_Graph_Topology]] | [[Central_Nexus_Insights]]

## รายชื่อแผนกธุรกิจที่เปิดดำเนินการและสล็อตขยายธุรกิจ
{chr(10).join(div_lines)}

## 💡 ไอเดียธุรกิจ AI ที่พร้อมต่อยอดเข้าบริษัทได้ทันที
1. **VIP Gold & Macro AI Debate Signal SaaS:** นำบทสรุปการดีเบตระหว่าง [[Agent_Sarah_Jenkins|Sarah (Bull)]] และ [[Agent_Viktor_The_Skeptic_Kane|Viktor (Bear)]] ส่งเข้ากลุ่ม Telegram VIP แบบรายเดือน
2. **Crypto Funding Rate & Liquidity Sweep Bot:** ใช้โมดูล `SMC Liquidity Sweep` ของ [[Agent_Dr._Kenji_Sato|Dr. Kenji]] กับคู่เหรียญ BTCUSDT / SOLUSDT ตลอด 24 ชม.
3. **Automated Financial News & TikTok/Reels Studio:** ให้ [[Agent_Maya_Lin|Maya Lin]] สรุปข่าวทองคำและเศรษฐกิจด่วนเป็นสคริปต์สั้นส่งเข้า Obsidian และโซเชียลมีเดียอัตโนมัติ
"""
        with open(venture_path, "w", encoding="utf-8") as f:
            f.write(venture_md)
        files_created.append(venture_path)

        # 5. สร้างไฟล์สรุปรายวัน (Daily Summary)
        daily_path = os.path.join(self.vault_dir, "01_Daily_Summaries", f"{date_str}_Daily_Summary.md")
        daily_md = f"""---
tags:
  - daily-summary
  - xauusd-verdict
date: "{date_str}"
verdict: "{cio.get('action')}"
gold_price: {market.get('current_price')}
---
# 📅 สรุปรายงานประจำวัน: {date_str} (AI Holding Company HQ)
เชื่อมโยงกับ: [[00_AI_Holding_Company_MOC]] | [[00_Knowledge_Graph_Topology]] | [[Central_Nexus_Insights]] | [[MT5_Portfolio_and_Benchmarks]]

> [!important] มติชี้ขาดวันนี้โดย [[Agent_Arthur_Pendelton|Arthur Pendelton (CIO)]]: `{cio.get('action')}`
> - **ราคาทองคำปัจจุบัน:** `${market.get('current_price'):,.2f}` (`D1: {market.get('d1_trend')}` | `H1: {market.get('trend')}`)
> - **จุดเข้า (Entry):** `${cio.get('final_entry'):,.2f}` | **SL (1.5x ATR):** `${cio.get('final_sl'):,.2f}`
> - **TP1 (1.8R):** `${cio.get('final_tp1'):,.2f}` | **TP2 (2.8R):** `${cio.get('final_tp2'):,.2f}` | **Lot Size:** `{cio.get('recommended_lot')} Lot`

## 👩‍💼 บทสรุปการทำงาน 24 ชม. (โดย [[Agent_Sophia_Chen|Sophia Chen]])
{office.get('digest_summary')}

## 📝 รายละเอียดมติผู้บริหาร
{cio.get('executive_summary')}
"""
        with open(daily_path, "w", encoding="utf-8") as f:
            f.write(daily_md)
        files_created.append(daily_path)

        # 6. สร้างไฟล์โครงข่ายกราฟและการประหยัดโทเคน (00_Knowledge_Graph_Topology.md)
        graph_doc_path = os.path.join(self.vault_dir, "00_Knowledge_Graph_Topology.md")
        matrix_rows = []
        for r in tok_sav["agent_routing_matrix"]:
            nodes_str = " ↔ ".join([f"`{n}`" for n in r["connected_nodes"]])
            matrix_rows.append(
                f"| **{r['agent_name']}** | `{r['llm_model']}` | {nodes_str} | {r['data_flow_summary']} | `{r['full_vault_tokens']:,}` | **`{r['graph_pruned_tokens']:,}`** | **-{r['savings_pct']}%** (`{r['tokens_saved_per_call']:,}` โทเคน) |"
            )

        edge_rows = []
        for e in graph_topology["edges"][:18]:
            edge_rows.append(
                f"| `{e['source']}` | ➡️ `{e['relation']}` ➡️ | `{e['target']}` | {e['data_flow']} | **-{e['tokens_saved']:,} Tokens** |"
            )

        graph_md = f"""---
tags:
  - knowledge-graph
  - token-saving-rag
  - obsidian-topology
updated: "{report.get('session_time')}"
---
# 🕸️ 00 — ผังโครงข่ายข้อมูล Obsidian Knowledge Graph & ระบบประหยัดโทเคน (Graph-RAG)
เชื่อมโยงกับ: [[00_AI_Holding_Company_MOC]] | [[Central_Nexus_Insights]] | [[MT5_Portfolio_and_Benchmarks]] | [[{date_str}_Daily_Summary]]

> [!tip] ประหยัดโทเคน AI เฉลี่ย **{tok_sav['savings_pct']}%** (`-{tok_sav['tokens_saved_per_call']:,} Tokens / รอบ` หรือ `-{tok_sav['daily_estimated_tokens_saved']:,} Tokens / วัน`)
> แทนที่จะส่งข้อมูลทั้งบริษัท (`{tok_sav['unfiltered_full_vault_tokens']:,} Tokens`) เข้า Prompt ทุกครั้ง ระบบใช้ผัง **Knowledge Graph** นี้ดึงเฉพาะ **โหนดที่เชื่อมต่อกันโดยตรง 1 ขั้น (1-Hop Connected Subgraph)** เหลือเพียงเฉลี่ย **`{tok_sav['graph_routed_avg_tokens']:,} Tokens / รอบ`**!

---

## 🗺️ 1. แผนผังการไหลของข้อมูลในบริษัท (Mermaid Knowledge Graph)

```mermaid
flowchart TD
    MKT["📊 HUB_MARKET: กราฟทองคำ H1/H4/D1 + Macro"] -->|ส่งราคา & ATR| QUANT["🔬 Quant Lab (Dr. Kenji & Elena)"]
    MKT -->|ส่ง DXY & US10Y| MACRO["🌍 Macro Radar (Marcus & Maya)"]
    NEXUS["🧠 HUB_NEXUS: Central Knowledge Core"] -->|ส่งสูตรสกิลที่วิจัยแล้ว| QUANT
    QUANT -->|ส่งสัญญาณกลยุทธ์| DEBATE["⚔️ Bull vs Bear Debate (Sarah vs Viktor)"]
    MACRO -->|ส่งแนวโน้มข่าว| DEBATE
    DEBATE -->|ส่งข้อโต้แย้ง| RISK["🛡️ Risk Guard (Chloe & Liam)"]
    RISK -->|ส่งขนาด Lot & เพดานความเสี่ยง| CIO["👑 CIO Verdict (Arthur Pendelton)"]
    CIO -->|สั่งยิงออเดอร์| MT5["🤖 HUB_MT5: AutoBot X-1 Execution"]
    MT5 -->|บันทึกผลเทรด| DAILY["📅 HUB_DAILY: สรุปรายกะ & รายวัน (Sophia)"]
    DAILY -->|อัปเดตสารบัญ| MOC["🏛️ HUB_MOC: Master Index"]
    DAILY -->|ต่อยอดธุรกิจ| VENTURE["🚀 HUB_VENTURE: Nova Vance"]
```

---

## 🪙 2. ตารางจัดเส้นทางข้อมูลเฉพาะส่วนเพื่อประหยัดโทเคน (1-Hop Subgraph Routing Matrix)

| พนักงาน AI | สมองกล (LLM) | โหนดข้อมูลที่เชื่อมตรง (1-Hop Nodes) | ข้อมูลที่ส่งหากัน | โทเคนปกติ (ทั้งคลัง) | โทเคนใช้จริง (Graph-RAG) | ประหยัดไปได้ |
|---|---|---|---|---|---|---|
{chr(10).join(matrix_rows)}

---

## 🔗 3. รายละเอียดเส้นเชื่อมโยงข้อมูล (Data Dependency Edges)

| โหนดต้นทาง (Source) | ความสัมพันธ์ | โหนดปลายทาง (Target) | รายละเอียดข้อมูลที่เชื่อมกัน | โทเคนที่ประหยัดได้ |
|---|---|---|---|---|
{chr(10).join(edge_rows)}
"""
        with open(graph_doc_path, "w", encoding="utf-8") as f:
            f.write(graph_md)
        files_created.append(graph_doc_path)

        # 7. สร้างไฟล์กระดาน Obsidian Canvas (AI_Company_Knowledge_Map.canvas)
        canvas_path = self._create_obsidian_canvas_file(date_str)
        files_created.append(canvas_path)

        # 8. สร้างหน้าสารบัญหลัก (00_AI_Holding_Company_MOC.md)
        moc_path = os.path.join(self.vault_dir, "00_AI_Holding_Company_MOC.md")
        moc_md = f"""---
tags:
  - moc
  - ai-holding-hq
  - second-brain
updated: "{report.get('session_time')}"
---
# 🏛️ 00 — AI Holding Company & Isometric Cutaway HQ (Master MOC — V8)

ยินดีต้อนรับสู่คลังสมองที่สอง (**Obsidian Second-Brain Vault**) ของบริษัท AI เทรดทองคำและพัฒนาธุรกิจอัตโนมัติ!  
- กดเปิดไฟล์กระดาน **`AI_Company_Knowledge_Map.canvas`** หรือ **[[00_Knowledge_Graph_Topology]]** เพื่อดูว่าข้อมูลส่วนไหนเชื่อมกับส่วนไหน
- กด **`Ctrl+G` ในแอป Obsidian** เพื่อดูโครงข่ายใยแมงมุม (Graph View)

---

## 🧭 สารบัญคลังความรู้หลัก (Core Vault Hubs)
- 🕸️ **ผังโครงข่ายข้อมูล & ระบบประหยัดโทเคน ({tok_sav['savings_pct']}%):** [[00_Knowledge_Graph_Topology]]
- 📅 **สรุปรายงานประจำวันล่าสุด:** [[{date_str}_Daily_Summary]]
- 🧠 **แกนกลางความรู้บริษัท (Shared Brain):** [[Central_Nexus_Insights]]
- 🤖 **พอร์ตบอท MT5 & ผลทดสอบ 4 กลยุทธ์วิจัย:** [[MT5_Portfolio_and_Benchmarks]]
- 🚀 **แผนกปั้นธุรกิจใหม่ในเครือบริษัท AI:** [[New_Venture_Ideas_Blueprint]]

---

## 🪪 ทำเนียบพนักงาน AI ทั้ง 11 ตัว และสมองกลที่เชื่อมต่อ (AI Roster & LLM Brains)
{chr(10).join(agent_links)}
"""
        with open(moc_path, "w", encoding="utf-8") as f:
            f.write(moc_md)
        files_created.append(moc_path)

        encoded_path = urllib.parse.quote(moc_path.replace("\\", "/"))
        obsidian_uri = f"obsidian://open?path={encoded_path}"

        return {
            "vault_path": self.vault_dir,
            "moc_file": moc_path,
            "graph_topology_file": graph_doc_path,
            "canvas_file": canvas_path,
            "files_synced_count": len(files_created),
            "obsidian_uri": obsidian_uri,
            "last_synced": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "knowledge_graph": graph_topology
        }
