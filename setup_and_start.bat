@echo off
chcp 65001 >nul
title AI Holding Company V8 — Portable 1-Click Setup & Launcher
echo ============================================================================
echo   🏝️ AI HOLDING COMPANY V8 (PORTABLE EDITION)
echo   ระบบติดตั้งอัตโนมัติ + กู้คืนกะที่ตกหล่น + ซิงก์กราฟ Obsidian + เปิดเซิร์ฟเวอร์สด
echo ============================================================================
cd /d "%~dp0"

echo [1/3] กำลังตรวจสอบและติดตั้งไลบรารี Python ที่จำเป็น (requirements.txt)...
python -m pip install -r requirements.txt --quiet

echo [2/3] กำลังรันตรวจสอบระบบ, กู้คืนกะที่ตกหล่นตอนปิดคอม และสร้างกราฟ Obsidian...
set PYTHONIOENCODING=utf-8
python main.py --capital 1000 --risk 1.5

echo [3/3] กำลังเปิดหน้าเว็บ http://localhost:8080 และเดินเครื่องเซิร์ฟเวอร์สด...
start "" "http://localhost:8080"
python server.py --port 8080 --capital 1000 --risk 1.5 --interval 45
pause
