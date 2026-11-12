@echo off
chcp 65001 >nul
title AI Holding Company V8 — 1-Click GitHub Sync
echo ============================================================================
echo   🚀 ซิงก์ข้อมูลโค้ด + รายงาน + คลังสมอง Obsidian ขึ้น GitHub อัตโนมัติ
echo ============================================================================
cd /d "%~dp0"
git add -A
git commit -m "Auto-sync AI Holding Company V8 state, reports & Obsidian Knowledge Graph"
git push origin main
echo.
echo ✅ อัปเดตข้อมูลขึ้น GitHub เรียบร้อยแล้ว!
pause
