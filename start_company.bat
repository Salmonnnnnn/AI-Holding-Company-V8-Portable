@echo off
chcp 65001 >nul
title AI Holding Company V7 — 1-Click Startup & Offline Catch-up Launcher
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo ===============================================================================
echo 🏝️ กำลังเปิดบริษัท AI Holding Company V7 + เก็บตกงานช่วงที่ปิดคอม (Auto-Catchup)...
echo ===============================================================================
python main.py --capital 1000 --risk 1.5
start "" "http://localhost:8080"
python server.py
