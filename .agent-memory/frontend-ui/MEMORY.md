# 🎨 Frontend & UI/UX Specialist Memory

## 🖥️ Presentation Layer Overview
- **Brand Identity**: **Aurum Isle — เกาะ AI ล่าทองคำ** (`BRAND_NAME = "Aurum Isle"`, `BRAND_TAGLINE = "เกาะ AI ล่าทองคำ"`).
- **Renderer**: `engine/dashboard_generator.py` generates a self-contained single-page dynamic HTML/CSS/JS dashboard.
- **Port**: Default `8080` (configurable via `SERVER_PORT` or CLI `--port`).
- **Style**: Cozy Isometric Cutaway AI Agent Town on a Beach Island (combining `@ong_stw` cutaway rooms with `@not_nang` AI Agent Town houses, glowing 3D green cylindrical energy batteries, and a 30-Day $1,000 Challenge banner).
- **Theme Support**: Dual mode toggle (☀️ Light Mode / 🌙 Dark Mode).

## 🏆 30-Day $1,000 AI Agent Town Challenge & Multi-Stream Breakdown (`compute_challenge_state`)
- **Goal**: `$1,000.00` cumulative profit (`CHALLENGE_GOAL_USD = 1000.0`) within `30` days (`CHALLENGE_DAYS = 30`).
- **Profit Formula**: `round(equity - initial_capital, 2)` from `portfolio_state` (fallback `0.0`).
- **Day Formula**: `(now.date() - started.date()).days + 1` derived from `portfolio_state["first_trade_at"]` (`MIN(opened_at)` in `portfolio_trades`), clamped to `1..30` (defaults to `Day 1` when no trades exist).
- **Progress Bar**: `pct = clamp((profit / 1000.0) * 100, 0.0, 100.0)`; displays negative profit cleanly with a coral status pill while keeping bar width at `0%`.
- **Multi-Stream Revenue Breakdown (`#challengeVenturesStrip`)**: Breaks down the revenue across the 4 specialized venture streams (Trading War Room, Online Store, Tech Studio Micro-SaaS/Bots, and Meme Studio Viral Content). Returns `"ventures"` dict in `compute_challenge_state`.

## 🏝️ Multi-Venture AI Agent Town Architecture (`Exmple.mp4`)
- **8 Specialized Studios (`ISO_ROOMS`)**:
  1. `TOWN_HALL`: 🏛️ ทำเนียบผู้บริหาร ("The Boss" Arthur & Sophia) — classical columns, podium, and daily executive directive memo.
  2. `TECH_STUDIO`: 💻 สตูดิโอโค้ดดิ้ง (Dr. Kenji Sato & AutoBot X-1) — cyber server rack, blinking LEDs, and glowing neon `</>` emblem.
  3. `MEME_STUDIO`: 🎬 มีมสตูดิโอ (Maya Lin & Sarah Jenkins) — colorful striped tent roof, camera on tripod with `● REC` light, and floating party balloons.
  4. `ONLINE_STORE`: 🏪 ร้านค้าดิจิทัล (Nova Vance) — cozy striped shop awning, storefront counter, POS cash register, and digital product cards.
  5. `TRADING_LAB`: 📈 วอร์รูมเทรดดิ้ง (Alex Vance & Dr. Marcus Sterling) — multi-monitor candlestick charts & 3D holographic gold trendline.
  6. `CRITIC_STUDIO`: 🛡️ สตูดิโอตรวจงาน (Viktor Kane & Elena Rostova) — security checkpoint desk, metallic shield emblem, and `96/100 PASSED` rubber stamp seal.
  7. `GROWTH_STUDIO`: ⚡ สตูดิโอยิงการตลาด (Sarah Jenkins) — megaphone emblem, broadcast antenna, and viral growth analytics chart.
  8. `COURIER_DISPATCH`: 📦 ศูนย์กระจายงาน (AutoBot X-1) — conveyor belt, delivery crates with labels, and automated drone landing pad.
- **Collaborating Pipelines & Animated Task Envelopes (`STUDIO_COLLAB_PIPELINES`)**: Renders animated glowing curved task light rays and floating white/gold task envelopes (✉️) with red wax seals traveling between collaborating studios.
- **Interactive Deliverables Viewer Modal (`#studioDeliverablesModal`)**: Triggered by clicking any studio building on `#isometricOfficeCanvas` or clicking `📦 ดูผลงานจริงของแต่ละสตูดิโอ (View AI Deliverables)`. Features a smartphone mockup card with viral Reel preview/script, syntax-styled Python micro-tool code with copy button, digital store catalog, live XAUUSD signal card, and QA audit scorecard.

## 🗂️ 6 Concise Navigation Pages & Layout Rules
1. `🏝️ 1. เมือง AI (Aurum Isle)` — Challenge banner, offline auto-catchup bar, isometric AI town canvas, live 8-step workflow & log.
2. `🪙 2. คลังโทเคน & สกิล` — Token economy metrics, Autonomous Skill Harvester, Custom Frontier Model Adder, per-agent token allocator.
3. `📅 3. ย้อนหลังตามกราฟจริง` — True Historical Candle & Shift Replay (`FULL_24H`, `MORNING_ASIA`, `AFTERNOON_LONDON`, `EVENING_NY`, `NIGHT_AUDIT`).
4. `🪪 4. ทำเนียบพนักงาน AI` — 11 AI agent profiles, model switcher, 5D radar chart.
5. `💬 5. แชทกับทีม AI` — Live Copilot chat with Antigravity & 11 agents.
6. `🤖 6. MT5 Demo & Obsidian` — Tick-by-tick MT5 simulation, 4-strategy benchmark table, Obsidian 1-Hop Subgraph canvas & routing table.
- **Typography & Table Rules**: Use `.section-head` flex wrappers (`flex-wrap: wrap`) so card titles and action buttons never collide on 1280px–1440px screens; wrap wide tables in `.table-wrap` (`overflow-x: auto`) and apply `.num` (`white-space: nowrap`) to numeric/badge cells.
