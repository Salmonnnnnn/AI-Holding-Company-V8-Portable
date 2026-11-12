@echo off
chcp 65001 >nul
title AI Holding Company V8 — 1-Click GitHub Repo Creator & Sync
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
python -m engine.github_pusher
pause
