# 🏝️ Aurum Isle — เกาะ AI ล่าทองคำ (AI Holding Company V8 Portable)
### เมือง AI อัตโนมัติ 24 ชม. • ชาเลนจ์ 30 วัน ปั้นกำไร $1,000 • เกาะ Isometric 3D • 12+ Frontier LLMs • Obsidian Knowledge Graph (ประหยัดโทเคน 83%+) • บอทเทรดทองคำ MT5

โปรเจกต์นี้คือระบบจำลองและปฏิบัติการจริงของ **Aurum Isle — เกาะ AI ล่าทองคำ (Autonomous AI Holding Company & Quantitative Gold Trading Town)** ที่รวมพนักงาน AI เฉพาะทาง 11 ตัว ทำงานร่วมกันบนเกาะเมือง AI สไตล์ **Cozy Isometric Island Town** (พร้อมบ้านประจำแผนก หลอดพลังงานแบตเตอรี่เรืองแสง `%` และแบนเนอร์ภารกิจ **Day X of 30 — ปั้นกำไร $1,000**) เชื่อมต่อ **MetaTrader 5 (MT5)**, **คลังสมองที่สอง Obsidian Knowledge Graph ที่ช่วยประหยัดโทเคน AI สูงสุด 83%+**, และ **ระบบกู้คืนกะอัตโนมัติแม้ปิดคอม (Offline Shift Auto-Catchup & 24/7 GitHub Cloud Runner)**

---

## ⚡ วิธีเปิดใช้งานในคลิกเดียว (เมื่อย้ายคอมหรือเพิ่งโคลนโปรเจกต์มาใหม่)

### วิธีที่ 1: ดับเบิลคลิกไฟล์เดียว (สำหรับ Windows)
ดับเบิลคลิกไฟล์ **`setup_and_start.bat`** ในโฟลเดอร์นี้ ระบบจะทำการ:
1. ติดตั้งไลบรารี Python ใน `requirements.txt` อัตโนมัติ
2. รันกู้คืนกะตลาดที่ตกหล่นระหว่างปิดคอม (Offline Auto-Catchup)
3. ซิงก์คลังโน้ตและกราฟความเชื่อมโยงลงโฟลเดอร์ `obsidian_vault/`
4. เปิดหน้าเว็บแอปที่ **`http://localhost:8080`** ทันที!

### วิธีที่ 2: รันผ่าน Terminal / PowerShell
```powershell
pip install -r requirements.txt
python main.py --capital 1000 --risk 1.5
python server.py --port 8080 --capital 1000 --risk 1.5 --interval 45
```

---

## 🌟 สรุปวิวัฒนาการและฟีเจอร์ทั้งหมดที่สร้างมา (V1 – V8 Complete Summary)

| เวอร์ชัน | ระบบที่พัฒนา | รายละเอียดและไฟล์หลัก |
|---|---|---|
| **V1** | **Multi-Agent Gold Trading Committee** | พนักงาน AI วิเคราะห์กราฟเทคนิค (`agents/technical_agent.py`), ข่าวมหภาค (`agents/macro_agent.py`), โต้แย้ง Bull vs Bear (`agents/debate_agent.py`), คุมความเสี่ยง (`agents/risk_agent.py`), และ CIO ชี้ขาด (`agents/cio_agent.py`) |
| **V2** | **Multi-Timeframe (D1/H4/H1), Kelly Sizing & Walk-Forward** | ดึงกราฟทองคำจริง + DXY + US10Y (`data/market_data.py`), คำนวณ Fractional Kelly Criterion และปรับพารามิเตอร์ตามสภาวะตลาด (`TRENDING`, `RANGING`, `VOLATILE_NEWS`) |
| **V3** | **24/7 AI Enterprise Office & 4 Global Benchmarks** | ระบบสำนักงาน 11 พนักงาน AI (`engine/virtual_office.py`) และระบบเทียบความแม่นยำกับ 4 กลยุทธ์วิจัยระดับโลก (`engine/strategy_benchmark.py`) |
| **V4** | **Academy Self-Training, Central Knowledge Core & Live MT5 Demo** | โรงเรียนฝึกสกิล AI อัพเลเวล (`engine/skill_academy.py`) และระบบจำลองยิงออเดอร์ MT5 Demo สดๆ 8 ขั้นตอน (`engine/mt5_executor.py`) |
| **V5** | **4D Spatial WebGL HQ, Multi-LLM Router, Obsidian Sync & Copilot Chat** | เชื่อมต่อโมเดล LLM หลากหลายค่าย (`engine/llm_router.py`), ซิงก์โน้ตเข้า Obsidian (`engine/obsidian_sync.py`), และห้องแชทถาม-ตอบกับ Antigravity & พนักงาน AI (`engine/chat_copilot.py`) |
| **V6** | **Cozy Isometric Cutaway Office, Historical Replay, Token Treasury & Skill Harvester** | หน้าจอตึกบริษัท Isometric 6 ห้องสไตล์คลิป TikTok `@ong_stw`, ระบบดูสรุปย้อนหลังตามแท่งเทียนจริง (`engine/historical_replay.py`), ระบบจัดสรรงบโทเคน (`engine/token_economy.py`), และระบบสั่ง AI ออกไปวิจัยสกิลใหม่สดๆ (`engine/skill_harvester.py`) |
| **V7** | **Light/Dark Theme, 12+ Frontier Models + Custom Model Adder & Offline Auto-Catchup** | ปุ่มสลับโหมดสว่าง/มืด (`☀️/🌙`), โมเดลระดับท็อป 12 รุ่น (`Claude 3.7 Sonnet`, `OpenAI o1-Pro`, `GPT-4.5`, `DeepSeek-R1 671B`, `Grok-3` ฯลฯ) + ปุ่มเพิ่มโมเดลใหม่เองได้ และระบบกู้คืนกะตอนปิดคอม (`engine/offline_catchup.py`) + GitHub Actions 24/7 (`.github/workflows/ai_company_24_7.yml`) |
| **V8** | **Obsidian Knowledge Graph Token-Saver (Graph-RAG) & Portable GitHub Release** | สร้างกระดานกราฟ `AI_Company_Knowledge_Map.canvas` + `00_Knowledge_Graph_Topology.md` + Interactive Graph บนเว็บ เพื่อดึงเฉพาะโหนดที่เชื่อมกัน 1 ขั้น (1-Hop Subgraph) **ช่วยประหยัดโทเคน AI เฉลี่ย 83.5%+ ต่อรอบ** |
| **Aurum Isle** | **30-Day $1,000 AI Agent Town Challenge & Orchestration Protocol** | รีแบรนด์เป็น **Aurum Isle — เกาะ AI ล่าทองคำ**, เพิ่มแบนเนอร์ภารกิจ 30 วัน ปั้นกำไร $1,000 (`compute_challenge_state`), อัปเกรดเกาะ Isometric เป็นเมือง AI พร้อมหลังคาบ้านและหลอดแบตเตอรี่พลังงานเรืองแสงรายตัว (`drawAgentTownHouseAndBattery`), จัดระเบียบหัวข้อและตารางทั้ง 6 หน้า และใช้ระเบียบ Multi-Agent Orchestration (`docs/ORCHESTRATION_PROTOCOL.md`) |

---

## 🕸️ ระบบกราฟความเชื่อมโยงข้อมูลใน Obsidian (ทำไมถึงช่วยประหยัดโทเคน 83%+?)

แทนที่จะส่งข้อมูลทั้งบริษัท (`~18,650 Tokens`) เข้าไปใน Prompt ทุกครั้งที่ AI คุยกัน ระบบใน `engine/obsidian_sync.py` ได้สร้าง **Knowledge Graph Topology** เพื่อระบุว่าข้อมูลส่วนไหนเชื่อมกับส่วนไหน:
- **เปิดดูในแอป Obsidian:** เปิดโฟลเดอร์ `obsidian_vault/` เป็น Vault ในโปรแกรม Obsidian แล้วคลิกไฟล์ **`AI_Company_Knowledge_Map.canvas`** หรือ **`00_Knowledge_Graph_Topology.md`** (หรือกด `Ctrl+G` เพื่อดู Graph View)
- **เปิดดูบนหน้าเว็บ:** ไปที่แท็บ **`🤖 6. MT5 Demo & Obsidian`** ด้านล่างจะมีกราฟ Interactive ที่คลิกดูแต่ละโหนดได้ทันทีว่าเชื่อมกับใครและประหยัดโทเคนไปกี่ Tokens

---

## 🧪 การรันทดสอบระบบอัตโนมัติ (8/8 Automated Pytest Suite)
```bash
./run_tests.sh
# หรือบน Windows: python -m pytest tests\test_committee.py -v
```
