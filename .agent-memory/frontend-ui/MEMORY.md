# 🎨 Frontend & UI/UX Specialist Memory

## 🖥️ Presentation Layer Overview
- **Brand Identity**: **Aurum Isle — เกาะ AI ล่าทองคำ** (`BRAND_NAME = "Aurum Isle"`, `BRAND_TAGLINE = "เกาะ AI ล่าทองคำ"`).
- **Renderer**: `engine/dashboard_generator.py` generates a self-contained single-page dynamic HTML/CSS/JS dashboard.
- **Port**: Default `8080` (configurable via `SERVER_PORT` or CLI `--port`).
- **Style**: Exmple.mp4 Circular 3D Island Town with lush circular green meadow hill in bright azure/turquoise ocean, central sandy plaza with cobblestone ring, 8 radial sandy paths, 2 giant glowing green battery cylinders ("2-HOUR 99%" & "7-DAY 100%"), 8 specialized studio buildings, pine trees, mushrooms, picket fences, flying task envelopes, and full-body chibi agents.
- **Theme Support**: Dual mode toggle (☀️ Light Mode / 🌙 Dark Mode / 🌅 Sunset Mode).

## 🏆 30-Day $1,000 AI Agent Town Challenge & Multi-Stream Breakdown (`compute_challenge_state`)
- **Goal**: `$1,000.00` cumulative profit (`CHALLENGE_GOAL_USD = 1000.0`) within `30` days (`CHALLENGE_DAYS = 30`).
- **Profit Formula**: `round(equity - initial_capital, 2)` from `portfolio_state` (fallback `0.0`).
- **Day Formula**: `(now.date() - started.date()).days + 1` derived from `portfolio_state["first_trade_at"]` (`MIN(opened_at)` in `portfolio_trades`), clamped to `1..30` (defaults to `Day 1` when no trades exist).
- **Progress Bar**: `pct = clamp((profit / 1000.0) * 100, 0.0, 100.0)`; displays negative profit cleanly with a coral status pill while keeping bar width at `0%`.
- **Multi-Stream Revenue Breakdown (`#challengeVenturesStrip`)**: Breaks down the revenue across the 4 specialized venture streams (Trading War Room, Online Store, Tech Studio Micro-SaaS/Bots, and Meme Studio Viral Content). Returns `"ventures"` dict in `compute_challenge_state`.

## 🏝️ Multi-Venture AI Agent Town Architecture (`Exmple.mp4`)
- **Lush Circular Green Meadow Island (`drawLushCircularIsland`)**:
  - Oval hill at center `(570, 290)` with 3D extruded shaded rim/cliff in bright turquoise/azure ocean with animated wave ripples and foam lines.
  - Central circular sandy plaza with warm cobblestone ring and 8 radial sandy paths radiating outward like spokes on a wheel.
  - Layered forest pine trees (`drawPineTree`), red-and-white spotted mushrooms (`drawMushroom`), white picket fences (`drawPicketFence`), and flower blossoms.
- **2 Giant Upright Glowing Green Battery Cylinders (`drawGiantBattery`)**:
  - Positioned in the central plaza flanking the central civic building:
    * Left battery: Labeled with white badge **"2-HOUR 99%"**
    * Right battery: Labeled with white badge **"7-DAY 100%"**
  - Metallic pedestals, translucent glass chambers, glowing green plasma energy (`#4ade80` → `#15803d`), animated electric sparks, and pulsating green auras.
- **Central Civic Hall Building (`drawCentralSquareBuilding`)**:
  - Located in the center plaza at `(570, 275)` between the 2 giant batteries, featuring blue slate pitched roof, red brick belltower steeple with gold cross, and working clock face.
- **8 Specialized Studio Buildings (`ISO_ROOMS`)**:
  1. `TOWN_HALL` (12:00, Top Center): 🏛️ ทำเนียบผู้บริหาร — Neoclassical white building with 6 marble columns, triangular pediment, entrance stairs, emerald green dome with cupola and fluttering flag. Podium with "The Boss" (Arthur Pendelton).
  2. `TECH_STUDIO` (9:00, Left): 💻 สตูดิโอโค้ดดิ้ง — Cyber dark cube with glowing bright cyan neon trim, roof antenna with blinking red beacon, and large glowing neon `</>` emblem (Dr. Kenji Sato & AutoBot X-1).
  3. `MEME_STUDIO` (6:00, Bottom Center): 🎬 มีมสตูดิโอ — Straight path leading through wooden arch labeled "MEME STUDIO" into fenced green yard with red-and-white striped circus tent / big top, floating colorful party balloons, camera on tripod with `● REC`, studio cottage (Maya Lin & Sarah Jenkins).
  4. `ONLINE_STORE` (4:30, Bottom Right): 🏪 ร้านค้าดิจิทัล — Storefront with striped red/white awning, display window with merchandise, "AI STORE" sign (Nova Vance).
  5. `TRADING_LAB` (3:00, Right): 📈 วอร์รูมเทรดดิ้ง — Red brick cottage, multi-monitor terminals, satellite dish, floating 3D holographic gold candlestick chart with `$3,900` ticker (Alex Vance & Dr. Marcus Sterling).
  6. `COURIER_DISPATCH` (1:30, Upper Right): 🔬 ควอนต์ & หอดูดาว — White cylindrical stone observatory tower with revolving dome, brass telescope pointing to stars, cargo parcel depot.
  7. `CRITIC_STUDIO` (10:30, Upper Left): 🛡️ สตูดิโอตรวจงาน — Stone cottage with picket fence, golden audit shield, and magnifying glass (Viktor Kane & Elena Rostova).
  8. `GROWTH_STUDIO` (7:30, Bottom Left): ⚡ สตูดิโอยิงการตลาด — Purple cottage with golden megaphone / horn on roof, broadcast antennas, viral hype banner.
- **Collaborating Pipelines & Animated Task Envelopes (`STUDIO_COLLAB_PIPELINES`)**:
  - Curved light arcs flowing from Town Hall dome to studios with flying white-and-gold envelopes with red wax seals.
- **Interactive Deliverables Viewer Modal (`#studioDeliverablesModal`)**:
  - Clicking any building or character opens the modal with real specialized deliverables:
    * Meme Studio: Smartphone mockup with viral Instagram Reel / TikTok preview, script, and engagement stats.
    * Tech Studio: Syntax-styled Python code (`liquidity_sweep_bot.py`) with copy button.
    * Online Store: Digital products (VIP Signal, Graph-RAG Tool, Prompt Pack) with prices & sales revenue.
    * Trading War Room: Live XAUUSD signal card with entry, SL, TP, RR ratio.
    * Critic Studio: QA audit checklist (100% passed).
    * Town Hall: Executive daily memo.

## 🗂️ 6 Concise Navigation Pages & Layout Rules
1. `🏝️ 1. เมือง AI (Aurum Isle)` — Challenge banner, offline auto-catchup bar, circular island town canvas, live 8-step workflow & log.
2. `🪙 2. คลังโทเคน & สกิล` — Token economy metrics, Autonomous Skill Harvester, Custom Frontier Model Adder, per-agent token allocator.
3. `📅 3. ย้อนหลังตามกราฟจริง` — True Historical Candle & Shift Replay (`FULL_24H`, `MORNING_ASIA`, `AFTERNOON_LONDON`, `EVENING_NY`, `NIGHT_AUDIT`).
4. `🪪 4. ทำเนียบพนักงาน AI` — 11 AI agent profiles, model switcher, 5D radar chart.
5. `💬 5. แชทกับทีม AI` — Live Copilot chat with Antigravity & 11 agents.
6. `🤖 6. MT5 Demo & Obsidian` — Tick-by-tick MT5 simulation, 4-strategy benchmark table, Obsidian 1-Hop Subgraph canvas & routing table.
- **Typography & Table Rules**: Use `.section-head` flex wrappers (`flex-wrap: wrap`) so card titles and action buttons never collide on 1280px–1440px screens; wrap wide tables in `.table-wrap` (`overflow-x: auto`) and apply `.num` (`white-space: nowrap`) to numeric/badge cells.
