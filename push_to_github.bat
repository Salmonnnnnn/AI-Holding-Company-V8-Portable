@echo off
chcp 65001 >nul
title AI Holding Company V8 — 1-Click GitHub Repo Creator & Sync
echo ============================================================================
echo   🚀 สร้าง Repository อัตโนมัติและซิงก์ AI Holding Company V8 ขึ้น GitHub
echo ============================================================================
cd /d "%~dp0"

echo [1/3] ตรวจสอบสิทธิ์เชื่อมต่อ GitHub (หากโทเคนเดิมหมดอายุ ระบบจะเปิดหน้าเว็บให้กด Authorize 1 คลิก)...
python -c "
import subprocess, urllib.request, json, sys

def get_token():
    p = subprocess.run(['git', 'credential', 'fill'], input='protocol=https\nhost=github.com\n\n', text=True, capture_output=True)
    creds = dict(line.split('=', 1) for line in p.stdout.splitlines() if '=' in line)
    return creds.get('password', ''), creds.get('username', 'Salmonnnnnn')

def check_token(tok):
    if not tok: return False
    req = urllib.request.Request('https://api.github.com/user', headers={'Authorization': f'token {tok}', 'User-Agent': 'AI-Holding-V8'})
    try:
        with urllib.request.urlopen(req) as r: return r.status == 200
    except Exception:
        return False

tok, usr = get_token()
if not check_token(tok):
    print('🔄 โทเคน GitHub เดิมหมดอายุ กำลังเปิดหน้าต่างล็อกอิน GitHub ผ่านเบราว์เซอร์...')
    subprocess.run(['git', 'credential', 'reject'], input='protocol=https\nhost=github.com\n\n', text=True)
    subprocess.run(['git', 'credential-manager', 'github', 'login'])
    tok, usr = get_token()

if check_token(tok):
    req = urllib.request.Request(
        'https://api.github.com/user/repos',
        data=json.dumps({
            'name': 'AI-Holding-Company-V8-Portable',
            'description': 'Autonomous AI Holding Company V8: Cozy Isometric Cutaway Office, 12+ Frontier LLMs, Obsidian Knowledge Graph Token-Saver (83% Savings), MT5 Bot & 24/7 Cloud Runner',
            'private': False
        }).encode('utf-8'),
        headers={'Authorization': f'token {tok}', 'Accept': 'application/vnd.github+json', 'User-Agent': 'AI-Holding-V8'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print('✅ สร้าง GitHub Repository สำเร็จ:', data.get('html_url'))
    except urllib.error.HTTPError as e:
        if e.code == 422:
            print('ℹ️ มี Repository ชื่อ AI-Holding-Company-V8-Portable อยู่บนบัญชีแล้ว พร้อมอัปเดตโค้ด!')
"

echo [2/3] บันทึกการเปลี่ยนแปลงลง Git Commit...
git add -A
git commit -m "Sync AI Holding Company V8 state, reports & Obsidian Knowledge Graph" 2>nul

echo [3/3] กำลังอัปโหลด (Push) ขึ้น https://github.com/Salmonnnnnn/AI-Holding-Company-V8-Portable ...
git branch -M main
git remote remove origin 2>nul
git remote add origin https://github.com/Salmonnnnnn/AI-Holding-Company-V8-Portable.git
git push -u origin main

echo.
echo ✅ เสร็จสมบูรณ์! เปิดดูได้ที่: https://github.com/Salmonnnnnn/AI-Holding-Company-V8-Portable
pause
