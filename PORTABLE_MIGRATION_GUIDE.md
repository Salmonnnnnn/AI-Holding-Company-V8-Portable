# 📦 คู่มือการย้ายเครื่องคอมพิวเตอร์และสรุปสถาปัตยกรรมทั้งหมด (Portable Migration Guide — V8)

เอกสารฉบับนี้สรุปขั้นตอนการย้ายโปรเจกต์ **AI Holding Company V8** ไปยังคอมพิวเตอร์เครื่องใหม่ รวมถึงวิธีเชื่อมต่อทุกส่วนให้ทำงานต่อได้ทันทีโดยข้อมูลไม่หาย

---

## 🚀 1. วิธีย้ายไปคอมเครื่องใหม่ (เลือกได้ 2 วิธี)

### วิธีที่ A: ดึงจาก GitHub ลงคอมเครื่องใหม่ (แนะนำที่สุด)
เมื่อไปที่คอมเครื่องใหม่ที่มีโปรแกรม `Git` และ `Python 3.10+`:
```powershell
git clone https://github.com/Salmonnnnnn/AI-Holding-Company-V8-Portable.git
cd AI-Holding-Company-V8-Portable
.\setup_and_start.bat
```
- เมื่อแก้ไขหรือเทรน AI เพิ่มบนคอมเครื่องใหม่แล้ว อยากเซฟกลับขึ้น GitHub แค่ดับเบิลคลิกไฟล์ **`push_to_github.bat`**

### วิธีที่ B: ก๊อปปี้โฟลเดอร์ `AI-Holding-Company-V8-Portable` ใส่ Flash Drive / Google Drive / OneDrive
1. ก๊อปปี้ทั้งโฟลเดอร์ `C:\Users\ADMIN\AI-Holding-Company-V8-Portable` ไปวางในคอมเครื่องใหม่
2. ข้อมูลเลเวลของ AI ทั้ง 11 ตัว, งบโทเคน, สกิลที่ค้นพบ และประวัติการเทรดทั้งหมด ถูกเก็บอยู่ในไฟล์ฐานข้อมูลพกพา **`data/company_hq.db`** และโฟลเดอร์ **`obsidian_vault/`** เรียบร้อยแล้ว
3. ดับเบิลคลิก **`setup_and_start.bat`** เพื่อเปิดบริษัทต่อได้ทันที!

---

## 🗂️ 2. แผนผังโครงสร้างไฟล์ทั้งหมดในโฟลเดอร์นี้

```text
AI-Holding-Company-V8-Portable/
├── setup_and_start.bat          # ⚡ คลิกเดียวติดตั้ง + กู้คืนกะตอนปิดคอม + เปิดเว็บ http://localhost:8080
├── start_company.bat            # ▶️ คลิกเดียวเปิดเซิร์ฟเวอร์บริษัท
├── push_to_github.bat           # 🚀 คลิกเดียวอัปเดตข้อมูลทั้งหมดขึ้น GitHub
├── main.py                      # 🖥️ สคริปต์รันระบบผ่าน CLI และสร้างรายงาน
├── server.py                    # 🌐 เซิร์ฟเวอร์เว็บแอปสด (Live Web Server & REST API)
├── config.py                    # ⚙️ ตั้งค่าเริ่มต้นของบริษัทและรายการกลยุทธ์
├── requirements.txt             # 📦 รายชื่อไลบรารี Python ที่ต้องใช้
├── Dockerfile & render.yaml     # ☁️ ไฟล์สำหรับเอาขึ้นรันบน Cloud 24 ชม.
├── .github/workflows/           # 🤖 GitHub Actions รันเทรน AI บนคลาวด์ฟรีทุก 6 ชม. แม้ปิดคอม
│   └── ai_company_24_7.yml
├── data/
│   ├── company_hq.db            # 💾 ฐานข้อมูล SQLite เก็บเลเวล AI, โทเคน, สกิลใหม่, ประวัติกะ
│   ├── database.py              # 🗄️ โมดูลจัดการฐานข้อมูล V1-V8
│   └── market_data.py           # 📊 โมดูลดึงกราฟทองคำจริง (XAUUSD H1/H4/D1 + DXY + US10Y)
├── agents/                      # 🧠 สมองพนักงาน AI เฉพาะทาง
│   ├── technical_agent.py       # นักวิเคราะห์กราฟเทคนิค
│   ├── macro_agent.py           # นักวิเคราะห์เศรษฐกิจมหภาคและข่าว
│   ├── debate_agent.py          # ทีมโต้วาที Bull vs Bear
│   ├── risk_agent.py            # ผู้จัดการความเสี่ยง (Kelly Sizing & Veto)
│   └── cio_agent.py             # ประธานเจ้าหน้าที่การลงทุน (CIO Final Verdict)
├── engine/                      # ⚙️ เครื่องยนต์หลักของบริษัท AI V1-V8
│   ├── committee_room.py        # ห้องประชุมใหญ่เชื่อมทุกแผนกเข้าด้วยกัน
│   ├── virtual_office.py        # จำลองการทำงานของพนักงาน AI ทั้ง 11 ตัว
│   ├── skill_academy.py         # โรงเรียนฝึกสกิล AI อัตโนมัติ
│   ├── skill_harvester.py       # 🎓 ระบบใช้โทเคนออกไปวิจัยและปลดล็อกสกิลใหม่สดๆ
│   ├── token_economy.py         # 🪙 ระบบคลังโทเคนและโหมดสมอง (ECO / BALANCED / OVERCLOCK)
│   ├── llm_router.py            # 🤖 ระบบสลับสมอง AI 12+ รุ่นระดับโลก + เพิ่มโมเดลเองได้
│   ├── historical_replay.py     # 📅 ระบบดึงแท่งเทียนจริงมาสรุปย้อนหลังแยกตามวันและกะเวลา
│   ├── offline_catchup.py       # ⚡ ระบบกู้คืนกะอัตโนมัติเมื่อปิดคอมไปนาน
│   ├── mt5_executor.py          # 📈 ระบบจำลองและยิงคำสั่งเทรด MetaTrader 5 (MT5)
│   ├── strategy_benchmark.py    # 🏆 ระบบทดสอบ 4 กลยุทธ์มาตรฐานระดับโลก
│   ├── obsidian_sync.py         # 🕸️ ระบบสร้างโน้ต + กราฟ .canvas + ประหยัดโทเคน 83%+
│   ├── chat_copilot.py          # 💬 ระบบแชทถาม-ตอบกับ Antigravity & พนักงาน AI
│   └── dashboard_generator.py   # 🎨 ระบบสร้างเว็บแอป 6 หน้า + ตึก Isometric + โหมดมืด/สว่าง
├── obsidian_vault/              # 💎 คลังสมองที่สอง (เปิดด้วยโปรแกรม Obsidian ได้ทันที)
│   ├── 00_AI_Holding_Company_MOC.md
│   ├── 00_Knowledge_Graph_Topology.md
│   ├── AI_Company_Knowledge_Map.canvas
│   ├── 01_Daily_Summaries/
│   ├── 02_AI_Agents/
│   ├── 03_Central_Knowledge_Core/
│   ├── 04_MT5_Trade_Journal/
│   └── 05_Business_Ventures/
└── tests/
    └── test_committee.py        # 🧪 ชุดทดสอบความถูกต้องอัตโนมัติ 7/7 ข้อ
```
