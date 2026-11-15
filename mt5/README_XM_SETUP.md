# 🏅 คู่มือติดตั้งและเชื่อมต่อ MetaTrader 5 (XM) บน Mac กับ AI Holding Company V8

คู่มือฉบับสมบูรณ์สำหรับเปิดใช้งาน **AurumBridgeEA** บนโปรแกรม **MetaTrader 5 (XM)** บนระบบปฏิบัติการ **macOS** เพื่อเชื่อมต่อสัญญาณเทรดอัตโนมัติจาก AI Holding Company V8 เข้าสู่พอร์ตจำลอง (Demo) แบบ Real-Time

---

## 🛡️ กฎความปลอดภัยระดับสูง (Safety Guardrails)
1. **0.05 Lot Hard Cap**: ระบบจำกัดขนาดไม้สูงสุดไม่เกิน `0.05 Lot` เสมอ เพื่อบริหารความเสี่ยงอย่างรัดกุม
2. **3.0% Max Daily Drawdown Guard**: หากผลขาดทุนสะสมในวันแตะ `3.0%` ของเงินต้นวันนั้น ระบบจะตัดขาดทุนปิดทุกออเดอร์ทันที (Emergency Stop) และหยุดเทรดตลอดทั้งวัน
3. **Strict Demo Lock**: ระบบอนุญาตเฉพาะพอร์ต **Demo Account** เท่านั้น หากตรวจพบพอร์ตจริง (Live) โดยไม่ได้รับอนุญาต ระบบจะปฏิเสธคำสั่งและปิดพอร์ตทันที
4. **Instant Kill Switch**: สามารถกดสั่งตัดการทำงานและปิดทุกไม้ได้ใน 1 วินาทีจาก Web UI หรือกดปุ่มบน Dashboard

---

## 📋 ขั้นตอนการติดตั้งทีละสเต็ป (Step-by-Step Guide)

### ขั้นตอนที่ 1: เปิดโปรแกรม MetaTrader 5 บน Mac
- เปิดโปรแกรม **XM MetaTrader 5 for Mac** จากโฟลเดอร์ Applications หรือ Launchpad

### ขั้นตอนที่ 2: ตั้งค่าอนุญาต WebRequest (สำคัญมาก ⚠️)
เพื่อให้บอทสามารถสื่อสารกับ AI Server ภายในเครื่องได้:
1. ไปที่แถบเมนูด้านบน คลิก **Tools** -> **Options** (หรือกดคีย์ลัด `Cmd + ,` บน macOS)
2. สลับไปที่แท็บ **Expert Advisors**
3. ติ๊กเครื่องหมายถูกที่ช่อง:
   - `[✔] Allow algorithmic trading`
   - `[✔] Allow WebRequest for listed URL:`
4. ดับเบิลคลิกที่ช่องสีเขียวใต้แถบ URL แล้วพิมพ์:
   ```text
   http://127.0.0.1:8080
   ```
5. กดปุ่ม **OK** เพื่อบันทึกการตั้งค่า

---

### ขั้นตอนที่ 3: ล็อกอินบัญชี XM Demo Account
1. เข้าสู่ระบบบัญชีทดลอง XM Demo (ประเภทบัญชี Standard หรือ Ultra Low)
2. ตรวจสอบว่ามีสัญลักษณ์ทองคำ **`GOLD`** หรือ **`XAUUSD`** ในหน้าต่าง Market Watch

---

### ขั้นตอนที่ 4: คัดลอกไฟล์ EA เข้าโฟลเดอร์ของ MT5
1. ในโปรแกรม MT5 ไปที่เมนูด้านบน คลิก **File** -> **Open Data Folder** (โฟลเดอร์ Finder บน Mac จะเปิดขึ้นมา)
2. ดับเบิลคลิกเข้าไปที่โฟลเดอร์ **`MQL5`** -> **`Experts`**
3. คัดลอกไฟล์:
   ```text
   mt5/AurumBridgeEA.mq5
   ```
   จากโฟลเดอร์โปรเจกต์ `AI-Holding-Company-V8-Portable` ไปวางไว้ในโฟลเดอร์ `MQL5/Experts/`
4. (หากต้องการคอมไพล์) ดับเบิลคลิกเปิดไฟล์ด้วย MetaEditor แล้วกดปุ่ม **Compile (F7)** จะได้ไฟล์ `AurumBridgeEA.ex5`

---

### ขั้นตอนที่ 5: ติดตั้ง EA ลงบนกราฟราคาทองคำ (GOLD / XAUUSD)
1. ในหน้าต่างโปรแกรม MT5 ดูที่พาเนลซ้ายมือ **Navigator** (หากไม่เห็น ให้กด `Cmd + N` หรือ `View -> Navigator`)
2. คลิกขวาที่หัวข้อ **Expert Advisors** -> กด **Refresh**
3. จะเห็นชื่อ **`AurumBridgeEA`** ปรากฏขึ้นมา
4. เปิดกราฟทองคำ **GOLD** หรือ **XAUUSD** (แนะนำ Timeframe `M5` หรือ `M15`)
5. ลาก `AurumBridgeEA` ไปปล่อยลงบนหน้าต่างกราฟทองคำ

---

### ขั้นตอนที่ 6: ตั้งค่าพารามิเตอร์ของ EA (Inputs)
หน้าต่างตั้งค่าจะแสดงขึ้นมา:
1. แท็บ **Common**: ติ๊กเครื่องหมายถูก `[✔] Allow Algo Trading`
2. แท็บ **Inputs**:
   - `InpBridgeUrl`: ให้เป็น `http://127.0.0.1:8080`
   - `InpBridgeToken`: คัดลอก **Bridge Token** จากหน้า Web Dashboard (หรือดูจาก API `/api/mt5/token`) มาวางในช่องนี้
   - `InpPollIntervalSec`: `2` (ส่งข้อมูลทุกๆ 2 วินาที)
   - `InpMaxLot`: `0.05`
   - `InpMaxDailyLossPct`: `3.0`
   - `InpAutoDetectGold`: `true`
   - `InpAllowLiveAccount`: `false` (ล็อกพอร์ตเดโมเพื่อความปลอดภัย)
3. กดปุ่ม **OK**

---

### ขั้นตอนที่ 7: เปิดใช้งาน Algo Trading
1. กดที่ปุ่ม **`Algo Trading`** บนแถบเครื่องมือด้านบนของ MT5 ให้ไอคอนเปลี่ยนเป็น **สีเขียว** (Active)
2. สังเกตที่มุมขวาบนของกราฟ จะเห็นไอคอนหมวกบัณฑิต หรือสัญลักษณ์ EA แสดงเป็นสีฟ้า/น้ำเงิน
3. ดูที่แท็บ **Experts** ด้านล่างของจอ จะพบข้อความยืนยัน:
   ```text
   AurumBridgeEA: Successfully detected active Gold symbol -> GOLD
   AurumBridgeEA running. Waiting for next timer tick...
   ```

---

## 🎯 การตรวจสอบสถานะการเชื่อมต่อ (Verification)
- บนหน้าต่าง Web Dashboard ของ AI Holding Company V8:
  - สัญลักษณ์สถานะ **MT5 Bridge** จะแสดงสถานะ **ONLINE (CONNECTED) 🟢**
  - แสดงตัวเลข **Balance**, **Equity**, **Free Margin**, และ **Floating P&L** ตรงกับในโปรแกรม MT5 แบบสดๆ
- สามารถทดสอบส่งคำสั่ง หรือกดปุ่ม **Emergency Kill Switch** ได้ทันที ระบบจะตัดวงจรและปิดทุกออเดอร์ใน MT5 อัตโนมัติ!
