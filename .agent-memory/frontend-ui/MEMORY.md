# 🎨 Frontend & UI/UX Specialist Memory

## 🖥️ Presentation Layer Overview
- **Brand Identity**: **Aurum Isle — เกาะ AI ล่าทองคำ** (`BRAND_NAME = "Aurum Isle"`, `BRAND_TAGLINE = "เกาะ AI ล่าทองคำ"`).
- **Renderer**: `engine/dashboard_generator.py` generates a self-contained single-page dynamic HTML/CSS/JS dashboard.
- **Port**: Default `8080` (configurable via `SERVER_PORT` or CLI `--port`).
- **Style**: Cozy Isometric Cutaway AI Agent Town on a Beach Island (combining `@ong_stw` cutaway rooms with `@not_nang` AI Agent Town houses, glowing 3D green cylindrical energy batteries, and a 30-Day $1,000 Challenge banner).
- **Theme Support**: Dual mode toggle (☀️ Light Mode / 🌙 Dark Mode).

## 🏆 30-Day $1,000 AI Agent Town Challenge (`compute_challenge_state`)
- **Goal**: `$1,000.00` cumulative profit (`CHALLENGE_GOAL_USD = 1000.0`) within `30` days (`CHALLENGE_DAYS = 30`).
- **Profit Formula**: `round(equity - initial_capital, 2)` from `portfolio_state` (fallback `0.0`).
- **Day Formula**: `(now.date() - started.date()).days + 1` derived from `portfolio_state["first_trade_at"]` (`MIN(opened_at)` in `portfolio_trades`), clamped to `1..30` (defaults to `Day 1` when no trades exist).
- **Progress Bar**: `pct = clamp((profit / 1000.0) * 100, 0.0, 100.0)`; displays negative profit cleanly with a coral status pill while keeping bar width at `0%`.

## 🏝️ Isometric AI Agent Town & Battery Visuals
- **Town Houses & Cutaway Rooms**: 8 connected isometric zones (`ISO_ROOMS`) rendered via `drawIsoWallWithDoor`, `drawRoomFurniture3D`, `drawChibiAgent`, `drawRoundedBadge`, `drawPalmTree`, and `drawAgentTownHouseAndBattery`.
- **Agent Energy / Battery Pillar (`computeAgentEnergyPct`)**: Each plot renders a pitched roof gable on its back apex plus a 3D glowing green cylindrical battery pillar with a floating `%` badge (`68%–100%` derived from `tokens_used_today / token_quota`, or `100%` in `OVERCLOCK` mode).

## 🗂️ 6 Concise Navigation Pages & Layout Rules
1. `🏝️ 1. เมือง AI (Aurum Isle)` — Challenge banner, offline auto-catchup bar, isometric AI town canvas, live 8-step workflow & log.
2. `🪙 2. คลังโทเคน & สกิล` — Token economy metrics, Autonomous Skill Harvester, Custom Frontier Model Adder, per-agent token allocator.
3. `📅 3. ย้อนหลังตามกราฟจริง` — True Historical Candle & Shift Replay (`FULL_24H`, `MORNING_ASIA`, `AFTERNOON_LONDON`, `EVENING_NY`, `NIGHT_AUDIT`).
4. `🪪 4. ทำเนียบพนักงาน AI` — 11 AI agent profiles, model switcher, 5D radar chart.
5. `💬 5. แชทกับทีม AI` — Live Copilot chat with Antigravity & 11 agents.
6. `🤖 6. MT5 Demo & Obsidian` — Tick-by-tick MT5 simulation, 4-strategy benchmark table, Obsidian 1-Hop Subgraph canvas & routing table.
- **Typography & Table Rules**: Use `.section-head` flex wrappers (`flex-wrap: wrap`) so card titles and action buttons never collide on 1280px–1440px screens; wrap wide tables in `.table-wrap` (`overflow-x: auto`) and apply `.num` (`white-space: nowrap`) to numeric/badge cells.
