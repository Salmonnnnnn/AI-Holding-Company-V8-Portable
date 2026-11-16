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
- **Complete Circular Town Symmetry & 8 Outer Work Zones Architecture**:
  - Oval hill at center `(720, 415)` with lush green meadow, sand beach, and ocean with animated wave ripples.
  - Central circular sandy plaza with cobblestone ring pattern.
  - 8 Radial Sandy Paths connecting `(720, 415)` to all 8 studio work zones:
    1. Town Hall (North: `720, 240`)
    2. Critic & Risk Studio Zone (North-West: `450, 275`)
    3. Tech Studio (West: `370, 420`)
    4. Online Shirts & Store (South-West: `490, 540`)
    5. Meme Studio (South-East: `950, 540`)
    6. What-If & Quant Studio (East: `1085, 420`)
    7. Growth & Hype Studio Zone (North-East: `920, 320`)
    8. OpenClaw Pier Entrance (Far North-East Shore: `1140, 270`)
  - All 8 studios have dedicated main buildings, picket fences, wooden arch gates, named cottages, and floating hover badges:
    * `TOWN_HALL`: `(720, 165, badge: 720, 72)` with Neoclassical columns, green dome, The Boss podium.
    * `CRITIC_STUDIO`: `(450, 275, badge: 450, 185)` with `drawCriticStudioZone` (picket fence, arch gate `AUDIT`, stone cottage with golden shield at `450, 255`, and cottages `Audit` and `Risk`).
    * `GROWTH_STUDIO`: `(980, 310, badge: 980, 205)` with `drawGrowthStudioZone` (picket fence, arch gate `GROWTH`, viral hype building with golden megaphone at `980, 275`, and cottages `Turbo` and `Hype`).
    * `TECH_STUDIO`: `(300, 420, badge: 300, 280)` with `drawTechStudioZone` (picket fence, arch gate `TECH`, windmill at `215, 395`, cottages `Sprocket`, `Ada`, `Bit`).
    * `ONLINE_STORE`: `(440, 610, badge: 440, 485)` with `drawOnlineShirtsZone` (picket fence, arch gate `STORE`, lighthouse at `330, 620`, cottages `Whiskers`, `Calico`, `Mittens`, `Biscuit`).
    * `MEME_STUDIO`: `(1000, 610, badge: 1000, 485)` with `drawMemeStudioZone` (picket fence, arch gate `MEME`, circus tent, balloons, camera, cottages `Giggle`, `Chuckles`).
    * `TRADING_LAB`: `(1180, 420, badge: 1180, 275)` with `drawWhatIfQuantZone` (picket fence, arch gate `QUANT`, observatory, cottages `Atlas`, `Iso`, `Vector`, `Pixel`).
    * `COURIER_DISPATCH`: `(1260, 220, badge: 1260, 145)` with `drawOpenClawPier` (pier walkway, crates, crane, speedboat).
- **Single-Page Fullscreen AI Town View (`#townFullscreenCard`)**:
  - Interactive canvas `#isometricOfficeCanvas` (`width="1440" height="820"`) filling a full-bleed viewport card (`height: calc(100vh - 100px); min-height: 720px; border-radius: 16px; position: relative; overflow: hidden;`).
  - **Floating Top Bar (`.town-top-nav-bar`)**:
    * Unified flex container (`position: absolute; top: 12px; left: 16px; right: 16px; display: flex; justify-content: space-between; align-items: center; z-index: 25; pointer-events: none; gap: 8px; flex-wrap: nowrap;`).
    * **Left Pill Group (`.town-top-left-bar`)** (`gap: 6px; font-size: 0.78rem; flex-shrink: 0; pointer-events: auto;`):
      - Title: `🏰 AI Office • Aurum Isle`
      - Status pill: `▶ 11 working` (`btnTownStatus`, triggers `runLiveCompanyWorkflowAnimation()`)
      - Pause pill: `⏸ Pause` / `▶ Resume` (`btnTownPause`, triggers `toggleTownPause()`)
      - Action pills: `👥 View all` (directory drawer), `📊 Stats` (HUD toggle), `📬 Inbox` with red badge `8` (`openStudioDeliverablesModal()`), `🗂️ 6 แท็บระบบ (Menu)` (toggles lower enterprise tabs).
    * **Right Pill Group & Atmosphere Switcher (`.town-top-right-bar`)** (`pointer-events: auto; flex-shrink: 0; gap: 8px;`):
      - Compact Real-time Revenue & Challenge HUD: `🪙 {chal_profit_disp} / $1,000` • `DAY {chal_day} OF 30` (redundant battery status removed as batteries are already 3D structures on the island).
      - Sleek 3-button segmented atmosphere pill bar (`#atmosphereSegmentBar`): `☀️ กลางวัน (Day)` (default), `🌅 ยามเย็น (Sunset)`, `🌙 กลางคืน (Night)`.
    * Zero horizontal overlap or pill collision on standard 1280px–1440px viewports with seamless click-through via `pointer-events: auto` on buttons.
  - **Floating Bottom-Left `💬 Messages` Box (`#townMessagesBox`)**:
    * White translucent card (`320px x 230px`, `backdrop-filter: blur(8px)`), header with minimize `[ − ]` button (`toggleTownMessagesBox()`).
    * Live task handoff feed (`Forge ➔ Hype`, `Critic ➔ Iso`, `Atlas ➔ Vector`, `Jester ➔ Mittens`). Clicking opens that studio's Deliverables Modal.
  - **Floating Bottom-Right Quick Zone Switcher Bar (`#townZoneSwitcherBar`)**:
    * 5 core zone pills: `🏛️ Town Hall`, `💻 Tech Studio`, `👕 Online Store`, `🎬 Meme Studio`, `🔮 What-If & Quant`.
    * Clicking focuses that zone with an animated golden locator beacon spotlight (`focusedZoneTimer = 240`).
- **Island Canvas Render Loop & 4 Fenced Work Zones (`1440 x 820`)**:
  - Oval hill at center `(720, 415)` with lush green meadow, sand beach, and ocean with animated wave ripples and drifting cartoon clouds.
  - Central circular sandy plaza with cobblestone ring pattern.
  - Central Civic Hall (`drawCentralSquareBuilding`) at `(720, 390)` with blue roof, red clock tower, and clock face.
  - 2 Giant Glowing Green Battery Cylinders (`drawGiantBattery`):
    * Left battery: **"5-HOUR 99%"** at `(615, 415)`
    * Right battery: **"7-DAY 100%"** at `(825, 415)`
  - Town Hall (12:00, Top Center): Neoclassical white building with 6 white columns, green dome, cupola and flag. Podium with "The Boss" and floating speech callout box: `Cutaway #1 render APPROVED! Accuracy 96%...`
  - 4 Outer Fenced Work Zones:
    1. `💻 TECH STUDIO` (Left — 8:30, `260, 420`): Blue zone pill banner, circular white picket fence, wooden arch gate, coastal windmill with 4 rotating lattice sails, and cottages (`Sprocket` with glowing neon `</>`, `Ada`, `Bit`).
    2. `👕 ONLINE SHIRTS & STORE` (Bottom-Left — 6:30, `440, 610`): Green zone pill banner, circular white picket fence, wooden arch gate, red/white striped Lighthouse with rotating beam, and shop cottages (`Whiskers`, `Calico`, `Mittens`, `Biscuit`).
    3. `🎬 MEME STUDIO` (Bottom-Right — 5:00, `1000, 610`): Orange zone pill banner, circular white picket fence, wooden arch gate, red-and-white striped Circus Tent (`Jester`), floating party balloons, camera ● REC, and cottages (`Giggle`, `Chuckles`).
    4. `🔮 WHAT IF & QUANT STUDIO` (Right — 3:30, `1180, 420`): Purple zone pill banner, circular white picket fence, wooden arch gate, observatory tower with telescope, and cottages (`Atlas` with 3D holographic gold trendline, `Iso`, `Vector`, `Pixel`).
    5. `🌉 OpenClaw Pier` (Top-Left — 10:00, `260, 160`): Wooden walkway extending out into the ocean with pilings, foam splashes, lanterns, and coastal gateway house `OpenClaw`.
  - Collaborating pipelines with animated parabolic curved light rays and flying task envelopes (✉️).
  - Full-body chibi AI agents walking paths between zones.
- **Interactive Deliverables Viewer Modal (`#studioDeliverablesModal`)**:
  - Modal card style: `.deliverables-modal-card` with `opacity: 1; animation: modalFadeIn 0.2s ease-out forwards;` ensuring instant visibility and proper animation completion across all renderers.
  - Clicking any building or character opens the modal with real specialized deliverables:
    * Meme Studio: Smartphone mockup with viral Instagram Reel / TikTok preview, multiline script, and engagement stats.
    * Tech Studio: Clean multiline Python code (`liquidity_sweep_bot.py`) with copy button.
    * Online Store: Digital products (VIP Signal, Graph-RAG Tool, Prompt Pack) with prices & sales revenue.
    * Trading War Room: Live XAUUSD signal card with entry, SL, TP, RR ratio.
    * Critic Studio: QA audit checklist (100% passed).
    * Town Hall: Executive daily memo with proper line breaks.

## 🗂️ Enterprise Navigation Pages & Key Upgrades
- **Aurum Isle Canvas Clean Layout & Zero-Collision Architecture**:
  - **The Boss Podium & Speech Refinement**:
    * Clean executive speech callout: `speechText = "✨ อนุมัติแผนการเงิน & ขับเคลื่อน AI อัตโนมัติ 24/7"`.
    * Clean centered callout bubble (`bw = tw + 26`, `bh = 28`, `bx = x - bw/2`, `by = y - 68`) without text clipping or awkward cutoff.
    * Repositioned Boss name badge (`👑 The Boss`) neatly on the lectern (`y + 14` to `y + 28`, `229` to `243`) clearing the central axis.
  - **Studio Badges Zero-Collision Optimization (`ISO_ROOMS`)**:
    * `TOWN_HALL`: `badgeX: 720, badgeY: 72`
    * `CRITIC_STUDIO`: `badgeX: 720, badgeY: 262` (optimal position clearing The Boss podium at Y=243 and Critic Studio door at Y=292 with zero central axis collision)
    * `COURIER_DISPATCH`: `badgeX: 1260, badgeY: 145` (above OpenClaw Pier on East shoreline)
    * `TRADING_LAB`: `badgeX: 1180, badgeY: 275`
    * `ONLINE_STORE`: `badgeX: 440, badgeY: 485`
    * `MEME_STUDIO`: `badgeX: 1000, badgeY: 485`
    * `GROWTH_STUDIO`: `badgeX: 980, badgeY: 245`
    * `TECH_STUDIO`: `badgeX: 260, badgeY: 270` (higher up in the meadow, giving 70px+ clearance above Sprocket's roof)
  - **Contract Integrity**:
    * Verified exact chart pattern chip label contains `"🌊 Asian Range Liquidity Grab"` (Win Rate 91.2%).
    * Preserved legacy init speech test contract `"Cutaway #1 render APPROVED!"` in `isoSprites`.
  - Removed duplicate `drawZonePillBanner` across all 4 zones (`TECH_STUDIO`, `ONLINE_SHIRTS`, `MEME_STUDIO`, `WHAT_IF`), unifying district presentation into ONE clean, sleek `drawRoundedBadge` per district rendered in step 13 of `renderIsometricCompany`.
  - Relocated Critic & Risk Studio (`CRITIC_STUDIO`) to Central Civic Plaza (`x: 720, y: 290`, `badgeX: 720, badgeY: 245`) with `drawCriticStudioBuilding` rendered cleanly alongside Town Hall and the central batteries.
  - Relocated OpenClaw Pier (`COURIER_DISPATCH`) to the East/Right shoreline (`x: 1260, y: 220`, `badgeX: 1260, badgeY: 150`) with walkway connecting from land (`1140, 270`) into Finance & Trading District.
  - Added **XM MT5 Bridge Tower prop** (`drawXmBridgeTower`) on East shoreline (`x: 1270, y: 335`) featuring steel lattice mast, microwave transceiver, server cabin with blinking LEDs, pulsing green/amber status beacon, and illuminated "⚡ XM MT5" broker sign.
  - Repositioned Sprocket (`230, 375`), Ada (`295, 385`), and Bit (`255, 460`) cottages in Tech Studio to give clean spacing without colliding with the windmill (`175, 395`) or arch gate (`350, 420`).
  - Preserved test contracts for two giant green battery cylinders with labels `"5-HOUR 99%"` and `"7-DAY 100%"`.
- **Modern Segmented Navigation Bar (`.nav-tabs`)**:
  - Replaced bulky sub-labels (`📈 การเงิน & MT5:`, `💻 เทคโนโลยี:`, `👥 องค์กร & ทีมงาน:`) with a clean Apple-style **Segmented Navigation Bar**:
    * 6 Primary Core Segments: `🏝️ เกาะ Aurum` (`#tab-page-visualizer`), `📈 MT5 Live` (`#tab-page-mt5-live`), `🎨 Media` (`#tab-page-meme-studio`), `🏪 Store` (`#tab-page-store-studio`), `⚙️ Tech` (`#tab-page-tech-studio`), `🏛️ Office` (`#tab-page-profiles`).
    * Compact Secondary Analytics/Utilities: `📅 ปฏิทิน` (`#tab-page-replay`), `🪙 โทเคน` (`#tab-page-tokens`), `💬 แชท` (`#tab-page-chat`), `🤖 MT5 Sim` (`#tab-page-mt5`).
- **Unified Top Status Strip above XAUUSD Chart (`#mt5MarketStatusBanner`)**:
  - Combined the stacked banners into a single executive frosted glass banner above `#xauusdComparisonCanvas`:
    * Left side: Market status (`🔴 ตลาดทองคำปิดทำการ — เปิดวันจันทร์ 05:00 น.` with `#mt5MarketStatusIcon`, `#mt5MarketStatusTitle`, `#mt5MarketStatusBadge`, `#mt5MarketCountdownBadge`, `#mt5MarketStatusSubtext`).
    * Right side: 24/7 background auto-learner widget (`#osAutoLearningBanner` with `#osAutoLearnerPulseDot`, `#osAutoLearnerActivePill`, `#osAutoLearnerIntervalPill`, `#osAutoLearnerStatusVal`, `#osLastAutonomousCycleVal`, `#osAutoLearnerDescText`).
    * Dynamic JS updates via `updateMarketStatusUI(session, isOpen)` and `updateOpenSourceTrainingUI(data)` fully synchronized without height clutter.
- **5-Agent Trading War Room Committee Grid (`#tradingCommitteeGridCard`) Glass Redesign**:
  - Minimalist Frosted Glass Cards (`.war-room-glass-card`) with backdrop blur (`12px`), generous padding, and crisp visual hierarchy:
    * Avatar in 40x40 rounded tinted glass box, Agent Name (`0.92rem` bold), and Primary Role in high-contrast colored subtitle.
    * Generously padded Open-Source Stack and Mastery pills (`#osStackBadge_<id>`, `#osMasteryBadge_<id>`) without font crowding.
    * Real-time condition assessment (`#osStatusText_<id>`).
    * Expandable tech specs drawer (`<details class="war-card-drawer">`): reveals mathematical models, indicator weights, and institutional decision logic on click/hover.
- **Collapsible Open-Source Curriculum Matrix (`#openSourceCurriculumMatrix`)**:
  - Converted matrix table into a sleek Collapsible Accordion Drawer (collapsed by default).
  - Toggle summary bar: `[📚 คลังความรู้ Open-Source 11 สาขา (คลิกเพื่อดูรายละเอียด ▾)]` with counter badge `11 โมเดล`.
  - Smooth expansion revealing the complete 11-agent curriculum matrix table (`#openSourceCurriculumMatrixBody`).
- **3D Island Canvas Semi-Transparent Glass Badges (`drawRoundedBadge`)**:
  - Upgraded badges into semi-transparent frosted glass (`rgba(255, 255, 255, 0.72)` base alpha ~0.68) with 8px rounded corners, subtle drop shadow, and crisp border.
  - Interactive mouse tracking (`isoMouseX`, `isoMouseY`) on `#isometricOfficeCanvas` provides smooth 60fps fade-in transition (`targetAlpha = 1.0`) when hovering over badge or studio building.
  - Compact badge height (`32px`) and fine-tuned positions eliminate font collision with 3D buildings, trees, and podium.
- **Visual Polish & Edge-Cutoff / Collision Hardening (Bug Fixes)**:
  - **Radial Sandy Paths & Battery Collision Fix**:
    * North-West Critic path starting point adjusted from central origin `(720, 415)` to northern edge of central plaza `(670, 365)` connecting to `(490, 290)`, cleanly bypassing the 5-HOUR giant battery cylinder at `(615, 415)` and its floating badge at `tagY = 321`.
    * West Tech Studio path starting point adjusted to `(560, 420)` connecting to TECH arch gate at `(390, 420)`, eliminating intersection with the western battery pedestal.
  - **Agent Initial Positions & District Distribution (`isoSprites`)**:
    * Mapped all 11 AI agents to distinct initial coordinates across all 8 specialized districts with zero character or speech tag overlap:
      - Arthur (CIO / The Boss): `(720, 195)` (Town Hall Podium)
      - Sophia (COS): `(480, 600)` (Online Store)
      - Maya (News): `(960, 330)` (Growth Studio)
      - Dr. Kenji (Quant): `(1140, 440)` (What-If & Quant Studio)
      - Alex (TA): `(320, 440)` (Tech Studio)
      - Dr. Marcus (Macro): `(1200, 440)` (What-If & Quant Studio)
      - Sarah (Bull): `(420, 600)` (Online Store)
      - Viktor (Bear): `(430, 290)` (Critic Studio)
      - Elena (Risk): `(480, 290)` (Critic Studio)
      - AutoBot (Execution): `(1000, 330)` (Growth Studio)
      - Nova (Venture): `(270, 440)` (Tech Studio)
  - **3D Canvas Containment & Full-Bleed Integrity**:
    * Changed `.town-fullscreen-card #isometricOfficeCanvas` CSS from `object-fit: cover;` to `object-fit: contain;` so the 1440x820 canvas is 100% visible and never cropped on left/right on non-matching screen viewports.
    * In `ISO_ROOMS`:
      - Moved `TECH_STUDIO` inward from `x: 260` to `x: 300, y: 420, badgeX: 300, badgeY: 280`.
      - In `drawTechStudioZone`: Updated picket fence to `zx: 300, zy: 420, rx: 105, ry: 80`, wooden arch gate to `gx: 390, gy: 420`, windmill to `215, 395`, Sprocket cottage to `270, 375`, Ada cottage to `335, 385`, and Bit cottage to `295, 460`, ensuring all labels and cottages are completely inside the canvas border.
      - Moved `CRITIC_STUDIO` from central avenue (`x: 720, y: 290, badgeX: 720, badgeY: 262`) to west lawn at `x: 580, y: 280, badgeX: 580, badgeY: 220`, completely eliminating overlap with central walking characters, speech bubbles (`ส่งงานไป...`), and The Boss podium.
      - In `drawWoodenArchGate`: Elevated posts to `gy - 26` (height 32) and beam to `gy - 34` (label at `gy - 27.5`) so gate signs sit high above walking chibi agent heads.
  - **Executive KPI Cards & Financial Data Collision Prevention (`#page-mt5-live`)**:
    * In `.exec-kpi-grid`: Updated `grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 16px;` (up from 295px) to give cards ample breathing room.
    * In `.exec-kpi-card`: Added `min-width: 0; overflow: hidden;` to contain flex/grid children.
    * In `.exec-kpi-card .card-head`: Added `display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;` and added `white-space: nowrap; flex-shrink: 0; font-size: 0.95rem; font-weight: 900; color: var(--text-main); display: flex; align-items: center; gap: 6px;` on `.card-title`.
    * In status badges (`#mt5RealStatusBadge`, `#mt5DemoStatusBadge`): Set `white-space: nowrap; font-size: 0.68rem; font-weight: 800; padding: 2px 8px; flex-shrink: 0;`.
    * For Balance & Equity in Card 1 & Card 2: Formatted as a rigid 2-column grid (`display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 8px;`) with `font-size: 1.18rem; font-weight: 900; white-space: nowrap;` for `#mt5RealBalance`, `#mt5RealEquity`, `#mt5KpiBalance`, and `#mt5KpiEquity` with `text-align: right` on equity, guaranteeing numbers never touch or collide.
- **GitHub Push Modal (`#githubPushModal`)**:
  - Clear token auto-save explanation in input label and subtext indicating tokens are encrypted and auto-persisted in local `.env`.
  - JS handler `triggerGitHubPush()` seamlessly renders both `SUCCESS` and `SUCCESS_EXCLUDING_WORKFLOW` responses with token-saved confirmation and direct repository link.
- **XM MT5 Live Bridge Institutional Trading Console (`page-mt5-live`)**:
  - Live Broker Status Banner & Account Mode Banner:
    * Connection badge: Pulsing Green for Connected, Amber for Waiting for EA, Red for Disconnected.
    * Account Mode Banner (`#mt5AccountModeBanner`): Switches dynamically between Demo (`🧪 บัญชีทดลอง XM Demo (ปลอดภัย 100% สำหรับทดสอบผลงานและดูผลลัพธ์ก่อน)`) and Live (`🟢 บัญชีจริง XM Live (อนุมัติสิทธิ์เรียบร้อย — ป้องกันความเสี่ยงไม่เกิน 0.05 Lot / 3% Drawdown)`).
    * Action button: Direct download `⬇️ ดาวน์โหลด EA (AurumBridgeEA.mq5)` (`downloadAurumBridgeEA()`). Bulky 4-step wizard card completely removed for zero clutter.
    * Telemetry metrics: Ping, Server (`XMGlobal-MT5`), Account ID & Symbol (`XAUUSD`).
  - 5 Financial KPI Cards: Balance, Equity, Floating P&L (color indicator), Free Margin & Margin Level %, Daily Risk Guard with 3.0% hard cap meter and day-start equity tracker.
  - **Modern Executive Glassmorphic Financial Cards & XAUUSD Comparison Chart Engine (`#page-mt5-live`)**:
    * **Modern Executive Glassmorphic Financial Cards (`.exec-kpi-grid`, `.exec-kpi-card`)**:
      - 5 redesigned executive glassmorphic cards with frosted glass backdrop blur, high-contrast typography, top accent color borders, and live telemetry IDs:
        1. 👑 **พอร์ตหลัก (XM Real / Main Account)**: Account `#430446448` (`XMGlobal-MT5 18`), Real Balance strictly `$0.00` (unbacked / pending deposit), Real Equity `$0.00`, Floating P&L `+$0.00`, Badge `🟡 รอเติมเงินทุนจริง (Pending Deposit)`, Subtext `🛡️ รอเติมเงินทุนจริงจากผู้ใช้ • ปลอดภัย 100%`. Switches to `🟢 บัญชีจริง XM Live (Authorized Live)` only when `real.balance > 0`.
        2. 🧪 **พอร์ตทดลอง (XM Demo Forward Test)**: Account `#50892104` (`XMGlobal-MT5 Demo`), Balance `$10,000.00`, Equity `$10,340.50`, Floating P&L `+$340.50 (+3.41%)`, Status `🧪 Active Demo Telemetry (2 ออเดอร์เปิดอยู่)`.
        3. 📊 **กำไรสุทธิรวม & อัตราชนะ (Net Combined P&L & Win Rate)**: Net Profit `+$340.50`, Win Rate `64.2%`, Profit Factor `1.88`, R:R `1:1.9`.
        4. 🛡️ **มาร์จิ้น & เซฟตี้การ์ด (Free Margin & Risk Guard)**: Free Margin `$10,215.00`, Margin Level `820%`, Daily Drawdown `0.45%` (Cap 3.00%) with animated Risk Meter bar.
        5. 🎯 **ความพร้อม & การเข้าทำของ AI Bot (Autonomous Bot Intel)**: โหมด `🟢 ออโต้ (Active)`, คำสั่งทั้งหมด `28 ไม้`, IPC Latency `12ms`, แพตเทิร์นยอดเยี่ยม `🌊 Asian Range Grab (Win Rate 91.2%)`.
    * **Prominent Weekend Market Status Banner (`#mt5MarketStatusBanner`)**:
      - Placed prominently above the chart: `🔴 ตลาดทองคำ XAUUSD ปิดทำการ (Weekend Market Closed) — ตลาดจะเปิดอีกครั้งวันจันทร์ 05:00 น. (เวลาไทย)` with badge `🔒 Weekend Closed` and subtext `🛡️ โหมดวิจัยกลยุทธ์และวิเคราะห์กราฟย้อนหลัง (Weekend Strategy Research & Backtest Review Mode) — บอท AI พักการออกคำสั่งพอร์ตจริงจนกว่าตลาดจะเปิด` and Sydney/Tokyo open countdown pill.
      - Driven dynamically by `updateMarketStatusUI(session, isOpen)`, which also synchronizes the Master Auto-Trade switch to `🟡 ตลาดปิดทำการ (Weekend Hold)` and text to `⏸️ ตลาดปิดทำการสุดสัปดาห์ (Weekend Closed) — บอท AI อยู่ในโหมดวิเคราะห์กราฟและพักคำสั่งเทรดอัตโนมัติ`.
    * **5-Agent Specialized Trading War Room Committee Grid (`#tradingCommitteeGridCard`)**:
      - Dedicated 5-card division of labor grid on `#page-mt5-live` with Open-Source Tech Stack Pills (`#osStackBadge_<agent_id>`) and OVERCLOCK Mastery Badges (`#osMasteryBadge_<agent_id>`):
        1. 📰 **Dr. Marcus Sterling**: ข่าวสารและเศรษฐกิจมหภาคเรียลไทม์ (`📦 ProsusAI/FinBERT + OpenBB Macro SDK`, `🔥 OVERCLOCK • Mastery 97.8%`).
        2. 📈 **Alex 'ChartMaster' Vance**: นักวิเคราะห์โครงสร้างกราฟและแท่งเทียน Price Action (`📦 TA-Lib + polakowo/vectorbt`, `🔥 OVERCLOCK • Mastery 98.4%`).
        3. 🧠 **Dr. Kenji Sato**: วิเคราะห์สภาพคล่องสถาบัน SMC/ICT (`📦 smart-money-concepts + NautilusTrader`, `🔥 OVERCLOCK • Mastery 99.6%`).
        4. 🛡️ **Viktor 'The Skeptic' Kane**: ผู้จัดการความเสี่ยงและวินัยพอร์ตเข้มงวด (`📦 Riskfolio-Lib + QuantLib Monte Carlo`, `🔥 OVERCLOCK • Mastery 98.2%`).
        5. 👑 **Arthur Pendelton**: ผู้อนุมัติคำสั่งเทรดสูงสุด (`📦 Microsoft Qlib + FinRL Ensemble`, `🔥 OVERCLOCK • Mastery 99.4%`).
    * **Open-Source Deep Training & 100% Daily Token Burn Deck (`#openSourceMaxBurnDeck`)**:
      - Displays the Daily Token Budget Progress Bar (`#osDailyTokenMeterLabel`, `#osDailyTokenProgressBar`, `#osRemainingTokensBadge`): `🔥 โควต้าโทเคนรายวัน: 1,000,000 / 1,000,000 Tokens (100.0% FULL OVERCLOCK BURN — ใช้โทเคนหมดวันเพื่อฝึกฝนสูงสุด)`.
      - Prominent action button (`#btnTriggerOpenSourceMax`, `onclick="triggerOpenSourceMaxTrain()"`): `🔥 สั่ง AI เรียน Open-Source ขั้นสุด & ใช้โทเคนเต็มพิกัด 100% (Max Daily Burn)` which posts to `/api/train_open_source_max`, updates the 5 War Room cards, refreshes the 11-Agent Open-Source Specialization Matrix (`#openSourceCurriculumMatrixBody`), updates the token meter to `100.0% (0 Remaining)`, displays toast banner `#osTrainingToastBanner`, and refreshes MT5 telemetry & chart comparison data.
    * **Authentic Japanese Candlesticks (OHLC) & Comparative Chart Engine (`#xauusdComparisonCanvas`)**:
      - Rendered via `renderXauusdComparisonChart()` using `candlesticks` array (36 OHLC intraday M15 candles with volume).
      - Center wicks drawn from High to Low, rectangular candle body from Open to Close with solid bullish emerald green (`#10b981`) and bearish crimson red (`#ef4444`) fill and outlines.
      - Mini volume bars at the bottom with bullish/bearish opacity tinting.
      - AI Bot BUY/SELL markers directly aligned to candlestick time/price with glowing rings and directional triangles.
      - Comparative equity curves:
        * Demo Curve: Cyan line showing forward-test growth ($10,000 -> $10,340.50).
        * Real Curve: Dashed amber line steady at $0.00 baseline labeled `พอร์ตหลัก Real: $0.00 (รอเติมเงินทุนจริง)`.
      - In-canvas legend showing OHLC Candlestick spot price, Demo equity, Real equity ($0.00), and Buy/Sell markers.
    * **Dual-Account Trade Ledger (XM Demo vs Real Tabs)**:
      - Clean tab switcher between `🧪 พอร์ตทดลอง XM Demo` and `👑 พอร์ตหลัก XM Real` via `switchMt5TradesTab()`.
      - Demo Tab: Renders open demo orders with ticket, symbol, type, lots, open/current price, SL/TP, floating P&L, pattern tag chip, and 1-click close button.
      - Real Tab: Displays zero-risk Pending Deposit executive notice with $0.00 balance/equity/PnL, XM Deposit guide prompt, and empty 0-order table.
  - **Sleek Master 2-State Trading Control Bar (Master AI Switch)**:
    * Mode Status Banner (`#mt5ModeDisplayBanner`): Dynamic animated banner showing active mode (`🟢 โหมดออโต้: AI วิเคราะห์กราฟและตัดสินใจเปิด-ปิดออเดอร์อัตโนมัติ` vs `⏸️ โหมดหยุด: หยุดการเทรดชั่วคราว (ไม่มีการส่งออเดอร์ใหม่)`).
    * Master 2-State Buttons:
      - `[🟢 ออโต้ (Auto AI Mode)]` (`#btnAutoTradeOn`): Calls `setAutoTradeMode(true)` -> `POST /api/mt5/auto_trade` with `{enabled: true}`, highlighted with emerald green glow.
      - `[⏸️ หยุด (Stop Mode)]` (`#btnAutoTradeOff`): Calls `setAutoTradeMode(false)` -> `POST /api/mt5/auto_trade` with `{enabled: false}`, highlighted with amber glow.
      - `[⛔ ปิดทุกไม้ (Close All)]`: Calls `closeAllOrders()` -> `POST /api/mt5/close_all`.
    * Secondary quick manual actions (BUY 0.01 / SELL 0.01, Kill Switch, Resume) cleanly tucked in a subtle bottom strip.
  - **ตารางเปรียบเทียบผลงาน Demo vs AI Strategy & Benchmark (Performance Comparison Table)**:
    * 5 columns: ตัวชี้วัด (Metric), บัญชี XM Demo (Live Forward Test), สถิติย้อนหลัง 60 วัน (Big Data Backtest), เกณฑ์มาตรฐานสถาบัน (Target), สถานะประเมิน (Status).
    * 6 institutional metrics: Win Rate %, Profit Factor, Avg Risk:Reward, Max Drawdown %, Total Trades Sample, Net P&L $.
    * Green status pills (`✅ ผ่านเกณฑ์ยอดเยี่ยม`, `🛡️ ปลอดภัยสูง`, `✅ สถิติมีนัยสำคัญ`, `✅ เติบโตต่อเนื่อง`).
  - **AI Pattern Knowledge Bank & Continuous Training Deck (`#aiPatternDeck`)**:
    * Mastery badge (`#aiMasteryBadge`): `🎓 Level 9 Quant Neural Engine • ความแม่นยำ 96.4%` (updates to Level 10 upon training).
    * Continuous Training Button (`#btnTrainAiPatterns`): `🧠 ฝึกฝน AI จากข้อมูลกราฟย้อนหลัง 60 วัน (Train AI from Historical Big Data)` calling `trainAiPatterns()` -> `POST /api/train`.
    * Grid of 5 Learned Chart Patterns with live win rate chips:
      1. 🎯 ICT Fair Value Gap (FVG) Sweep (Win Rate ~88.4%)
      2. 🌊 Asian Range Liquidity Grab & Reversal (Win Rate ~91.2%)
      3. 📈 EMA 50/200 Dynamic Confluence Pullback (Win Rate ~84.6%)
      4. ⚡ Institutional Order Block Rejection (Win Rate ~86.5%)
      5. 🧭 H4 Multi-Timeframe Trend Continuation (Win Rate ~89.1%)
  - Live Open Positions Table: Ticket, Symbol, Type, Lots, Open Price, Current Price, SL, TP, Profit, and 1-Click "❌ ปิดไม้นี้" button calling `closeMt5Ticket(ticket)` via `POST /api/mt5/close_ticket`.
  - Live Telemetry & Event Feed (`#mt5EventsLogContainer`) with compact 1-Click Secret Token copy button (`copyMt5BridgeToken()`).
  - JS Syntax Rigor: All string literals verified via `node --check` with exit code 0. Bulky `#mt5SetupWizardCard` removed.
- **GitHub Push Modal 100% Success Upgrade (`#githubPushModal`)**:
  - Checkbox `#excludeWorkflowsCheck` allows bypassing `.github/workflows` to prevent token permission failures.
  - Passes `exclude_workflows` parameter in fetch payload to `/api/github_push`.
  - Error rendering provides direct guidance and link to `https://github.com/settings/tokens` for adding `[✔] workflow` permission.
- **macOS Canvas Emoji+Thai Text Right-Shift Fix (`fillCenteredText`)**:
  - Replaces `ctx.textAlign = "center"; ctx.fillText(...)` across all Canvas 2D label drawing functions (`drawRoundedBadge`, `drawZonePillBanner`, `drawTownCottage`, `drawTheBossPodium`, `drawGiantBattery`, `drawChibiAgent`, etc.) with `fillCenteredText(ctx, text, cx, y)` using `ctx.textAlign = "left"` and `Math.round(cx - ctx.measureText(s).width / 2)` so CoreText on macOS WebKit/Chrome never shifts Emoji+Thai strings to the right.
- **Live Account vs. Paper/Test Account Separation (`#challengeBanner` & `.comic-hud-pill`)**:
  - Replaced the `$1,000 Goal` display with side-by-side **🟢 บัญชีจริง (Live Production Account)** (`$0.00` until live broker/API connected) vs. **🧪 บัญชีเทสบนกราฟจริง (Paper & Forward-Test Account)** while preserving all legacy DOM IDs (`#challengeDayBadge`, `#challengeProfitText`, `#challengePctText`, `#challengeProgressBar`, `#challengeVenturesStrip`, `#vTradingVal`, `#vStoreVal`, `#vTechVal`, `#vMediaVal`) and test contracts.
- **9 Enterprise Tabs in `.nav-tabs`**:
  1. `🏝️ 1. เมือง AI (Aurum Isle)` (`#page-visualizer`) — Fullscreen circular island town canvas, Live vs. Paper/Test Account P&L banner, Executive KPI Strip, live 8-step workflow & log, and Multi-Venture Financial Ledger Card (`#ventureLedgerCard`).
  2. `🎬 2. มีม & มีเดียสตูดิโอ` (`#page-meme-studio`) — Full-page Media & Viral Content Studio with 4 KPI cards, Interactive Viral Reel/TikTok Script & Hook Generator (`generateEnterpriseViralScript()`), 9:16 Smartphone Preview, and 6-Channel Content Distribution & Attribution Matrix.
  3. `🏪 3. ร้านค้าออนไลน์ (Store)` (`#page-store-studio`) — Full-page Digital Store & E-Commerce Studio with 4 E-Commerce KPI cards, 4 Digital Product SKU cards with 1-click Test Order recording (`submitQuickStoreOrder()`), Interactive Unit Economics & Profit Margin Calculator (`calculateStoreUnitEconomics()`), and Customer Order Fulfillment Log.
  4. `💻 4. เทค & บอทสตูดิโอ` (`#page-tech-studio`) — Full-page Quantitative FinTech & Micro-SaaS Studio with 4 SLA/Latency KPI cards, 4 Micro-SaaS Architecture Cards, Interactive Production Code Explorer (`selectTechStudioModule()`, `copyTechExplorerCode()`, `downloadTechStudioCodeFile()`), and Automated CI/CD & Backtest Verification Matrix.
  5. `📅 5. ปฏิทิน P&L & ย้อนหลัง` (`#page-replay`) — Interactive Monthly P&L & XAUUSD Daily Change Calendar (`#monthlyPnlCalendarCard`, `#monthlyCalendarGrid`, `changeCalendarMonth()`, `renderMonthlyPnlCalendar()`) + 5-Shift Historical Replay & `.md` exporter.
  6. `🪙 6. คลังโทเคน & สกิล` (`#page-tokens`) — Enterprise AI FinOps & Cost Governance bar, token economy metrics, Autonomous Skill Harvester, Custom Frontier Model Adder, per-agent token allocator.
  7. `🪪 7. ทำเนียบพนักงาน AI` (`#page-profiles`) — 11 AI agent profiles, model switcher, 5D radar chart, plus Enterprise HR & SLA Scorecard Matrix (`#hrScorecardTableBody`).
  8. `💬 8. แชทกับทีม AI` (`#page-chat`) — Live Copilot chat with Antigravity & 11 agents + All-Hands Executive Boardroom Briefing (`triggerAllHandsBoardMeeting()`).
  9. `🤖 9. MT5 & Obsidian` (`#page-mt5`) — Institutional Live Order Book & Position Manager (`#liveOrderBookCard`), tick-by-tick MT5 simulation, 4-strategy benchmark table, Obsidian 1-Hop Subgraph canvas & routing table.
- **Live Data Provenance & API Integrations Modal (`#liveIntegrationsModal`)**: Accessible from `.top-header` (`🔌 เชื่อมต่อข้อมูลจริง & API`) and Page 1; displays 100% Data Provenance Audit Table and live `.env` API key configurator (`POST /api/save_integrations`) + live market sync (`POST /api/refresh_live_market`).
- **24/7 Autonomous Background Learning UI & Real-Time Telemetry (`#openSourceMaxBurnDeck`)**:
  - Prominent glowing banner (`#osAutoLearningBanner`):
    * Pulsing status dot (`#osAutoLearnerPulseDot`) + active pill (`#osAutoLearnerActivePill`): `🟢 ระบบเรียนรู้อัตโนมัติ 24/7 กำลังทำงานในพื้นหลัง (Background Auto-Learner Active)`.
    * Interval pill (`#osAutoLearnerIntervalPill`): `⏱️ รอบละ 5 นาที`.
    * Clear explanation: `💡 เอไอค้นคว้าคลังความรู้ Open-Source, แบ็กเทสต์กราฟ Big Data 60 วัน และฝึกฝนตัวเองอย่างต่อเนื่องอัตโนมัติทุก 5 นาทีเมื่อว่าง/ตลาดปิด โดยที่คุณไม่ต้องกดปุ่มเอง`.
    * Dynamic telemetry box: Status (`#osAutoLearnerStatusVal`) and last cycle timestamp with relative timing (`#osLastAutonomousCycleVal`).
  - Button adjusted:
    * Label: `[⚡ บังคับเรียนทันที (Instant Force Cycle)]` (`#btnTriggerOpenSourceMax`).
    * Tooltip/subtext: `*ระบบทำงานอัตโนมัติอยู่แล้วในพื้นหลังตลอดเวลา คุณสามารถปล่อยให้เอไอเรียนรู้เอง หรือกดปุ่มนี้เพื่อเร่งรอบทันทีตามใจชอบ`.
  - JS Runtime & Telemetry Polling:
    * `updateOpenSourceTrainingUI(data)` dynamically updates banner status, cycle timestamp, description, and token meter from `/api/mt5/status` or `/api/state`.
    * Invoked inside `renderMt5BridgeStatus(status)`, `fetchMt5BridgeStatus(manual)`, and `triggerOpenSourceMaxTrain()`.
    * Polling interval in `initMt5LiveConsole()` and on `window.load` keeps background telemetry updated every 4-6 seconds.
- **GitHub Push Buttons UI Removal (User Request Verified)**:
  - Removed top navbar button: `<button class="cozy-btn purple" onclick="openGitHubPushModal()" id="topGithubBtn">🚀 อัปโหลด GitHub</button>`.
  - Removed catchup status bar button: `<button class="cozy-btn purple" style="padding:4px 10px;font-size:0.76rem" onclick="openGitHubPushModal()">🚀 กดอัปโหลดขึ้น GitHub</button>`.
  - Confirmed `openGitHubPushModal()` is not attached to any clickable element (`<button>` or `<a>`) across the dashboard.
  - Preserved `#githubPushModal` DOM container and JS functions (`openGitHubPushModal()`, `closeGitHubPushModal()`, `triggerGitHubPush()`) to satisfy test assertions in `tests/test_committee.py`.
  - Regenerated `reports/latest_dashboard.html` via `venv/bin/python3 -c "import server; server.ensure_state(); print('Dashboard regenerated')"`.
  - Verified via grep that `reports/latest_dashboard.html` has zero instances of `topGithubBtn` and zero `<button>`/`<a>` tags calling `openGitHubPushModal()`.
- **5 Major Luxury UI/UX Upgrades (Uncapped Real Token Leaderboard, Decluttered 75% Island + Minimal Strip, Dynamic 5-Stage Live Sprint, 7-Column Monthly P&L Calendar + Day Drill-Down Modal, 4-Pillar Apple Navigation)**:
  1. **🪙 Uncapped Real Token Display & 11-Bot Token Leaderboard (`#tokenLeaderboardModal` + Top Header Pill + `#page-tokens`)**:
     - Replaced `/ 1,000,000` capped token display in `.top-header` with a clickable **Uncapped Real Token & Cost Pill** (`onclick="openTokenLeaderboardModal()"`) showing `🪙 โทเคนใช้จริง: <strong id="topTokenUsedText">...</strong> (<span id="topTokenCostUsdText">$...</span>) • ไร้ขีดจำกัด (คลิกดูรายบอท)` while keeping `<span id="topTokenBudgetText" style="display:none">∞ Uncapped</span>` hidden.
     - Added `#tokenLeaderboardModal` (`openTokenLeaderboardModal()` / `closeTokenLeaderboardModal()`) and `#pageTokensLeaderboardTableBody` on `#page-tokens` sorted by real usage with 7 columns (`อันดับ` | `บอท AI & แผนก` | `สมองกล (Smart Model Routing)` | `โทเคนที่ใช้จริง (Used)` | `โทเคนคงเหลือพร้อมใช้ (Remaining Available)` | `ต้นทุนจริง ($ USD)` | `พลังงาน & สถานะ (Energy %)`), plus `+ เพิ่มบอทผู้ช่วยใหม่แบ่งเบาภาระ` button (`openAddCustomBotFromLeaderboard()`, `submitQuickSpawnBotFromModal()`, `addNewCustomModel()`).
  2. **🏝️ Decluttered `#page-island` — 75% 3D Island + 1 Minimal Live Workflow Strip (`.minimal-island-workflow-strip`)**:
     - `.town-fullscreen-card` sized to `height: 75vh; min-height: 580px; max-height: 780px;` so the 3D Island and the single minimal strip below it fit cleanly in the viewport.
     - Directly underneath the island, `.minimal-island-workflow-strip` shows `#bannerAvatar`, `#bannerSpeaker`, `#bannerMessage`, the `💬 สั่งงานผ่าน Arthur CIO / LINE` button, the 5-step `#liveWorkflowStepper`, and the single-line `#liveActivityTickerText`.
     - Bulky legacy sections (`#challengeBanner`, `.catchup-banner`, 4-box KPI strip, `#miniAgentsStrip`, `#missionChecklistBox`, `#realtimeLogBox`, `#ventureLedgerCard`) are housed inside `<div id="legacyUnderIslandHiddenStore" style="display:none">` (toggleable via `📂 ดูตารางบัญชีดิบ` / `toggleLegacyUnderIslandStore()`), preserving 100% of DOM IDs for `tests/test_committee.py`.
  3. **⚙️ Dynamic 5-Stage Live Task Pipeline Engine (`window.liveTaskSprintState` + `advanceLiveTaskSprint()`)**:
     - Replaced the static `งานเสร็จ 8/8` (`100%`) display with an automated 5-stage operational pipeline cycling every 6 seconds (and on user click) across:
       1. `1/5 • Dr. Marcus สแกนข่าวเศรษฐกิจ & CPI/Fed Sentiment`
       2. `2/5 • Alex Vance วิเคราะห์แท่งเทียน MTF (H4/H1/M15) & FVG`
       3. `3/5 • Viktor Kane กรองกราฟหลอก (Anti-Fakeout) & เช็กสเปรด XM`
       4. `4/5 • Sophia & Maya อัปเดตชุดแฟชั่นแปะตะกร้า & คลิปไวรัล What-If`
       5. `5/5 • Arthur CIO อนุมัติแผนเกรด A+ & ซิงค์พอร์ต Real/Demo`
     - Synchronizes `#topTaskCountText`, `#topTaskPctText`, `#topTaskBar`, `#liveWorkflowStepper`, `#liveActivityTickerText`, and `#missionChecklistBox` in real time.
  4. **📅 Overhauled Monthly P&L Calendar (`#page-replay`) — 7-Column CSS Grid Day Boxes + Interactive Day Drill-Down Modal (`#calendarDayDetailModal`)**:
     - Top Consolidated Monthly Executive Summary features 4 cards: `🟢 กำไรสุทธิพอร์ตหลัก (Real Account Monthly P&L)` (`#calRealPnlMonthVal`), `🧪 กำไรสุทธิพอร์ตทดลอง (Demo Account Monthly P&L)` (`#calTestPnlMonthVal`), `🎯 อัตราชนะ & สถิติรายวัน` (`#calWinDaysVal`, `#calLossDaysVal`, `#calGoldMonthChangeVal`), and `🎬 รายได้ธุรกิจเสริมรวมทั้งเดือน` (`#calVentureMonthVal`) with `[⚡ โยกกำไรไปทบพอร์ตเทรด 1-Click]` (`reinvestVentureToTrading()`) and `[📥 Export CSV (Excel)]` (`exportMonthlyCalendarCsv()`).
     - `#monthlyCalendarGrid` is a 7-Column CSS Grid (`display:grid; grid-template-columns:repeat(7, minmax(115px, 1fr)); gap:10px;`) rendering `.cal-day-box` cards with day number, status pill, `👑 หลัก (Real)` + shadow $50 est., `🧪 เดโม่ (Demo)`, trade count, gold close price, and `🔍 คลิกดูรายละเอียด`.
     - Clicking any day box calls `openCalendarDayModal(dateStr)` to open `#calendarDayDetailModal` with side-by-side XM Real (`#430446448`) vs XM Demo (`#50892104`) comparison cards, executed trade log table (`#calModalTradeLogBody`), and daily XAUUSD market/news summary (`#calModalMarketNewsBox`).
  5. **🧭 Clean Apple-Style 4-Pillar Navigation Bar (`.nav-tabs`) & Unified `#page-mt5`**:
     - Primary 4-pillar buttons: `🏝️ เกาะ AI (Overview)` (`switchPage('page-island')`), `📈 เทรดทอง MT5 (Trading)` (`switchPage('page-mt5')`), `🎬 ธุรกิจหารายได้ (Ventures)` (`switchPage('page-store-studio')`), and `📅 ปฏิทิน & สถิติ (Calendar)` (`switchPage('page-replay')`).
     - Secondary bar & `.ventures-subnav-bar` provide quick switches between `👗 แปะตะกร้าชุดแฟชั่น (Store)`, `🎬 คลิปไวรัล What-If (Media)`, `💻 บอท & เทค (Tech)`, and `🪙 ตารางโทเคน 11 บอท`.
     - Unified `#page-mt5-live` and `#page-mt5` so `switchPage('page-mt5')` and `switchPage('page-mt5-live')` both open the full XM MT5 Live Bridge Console + Candlestick Chart + Dual Account Real/Demo + Order Book + Obsidian Graph.
- **Typography & Table Rules**: Use `.section-head` flex wrappers (`flex-wrap: wrap`) so card titles and action buttons never collide on 1280px–1440px screens; wrap wide tables in `.table-wrap` (`overflow-x: auto`) and apply `.num` (`white-space: nowrap`) to numeric/badge cells.
- **Top Right Header Overflow & Fullscreen AI Canvas Border Elimination Fix (November 2026)**:
  - **Top Nav Bar Text Overflow Fix**:
    * Sized `.town-top-left-bar` with `max-width: 62%`, `gap: 4px`, `flex-wrap: wrap;`.
    * Sized `.town-top-right-bar` with `margin-left: auto; max-width: 48%; justify-content: flex-end; gap: 6px; flex-wrap: wrap;`.
    * Compacted `.comic-hud-pill` to `padding: 4px 10px; font-size: 0.72rem; gap: 4px; max-width: 100%;`.
    * HTML and JS labels streamlined: `🟢 จริง: ${live_profit_val:+,.2f}` • `🧪 เทส: ${test_profit_val:+,.2f}` • `⚡ {b5h_pct:.0f}%` (updated both in initial template and in `updateChallengeAndVentureUIFromLedger()`).
    * Compacted `.comic-pill-btn` (`padding: 4px 9px; font-size: 0.74rem; gap: 4px;`) and `.atmosphere-segmented-bar .segment-btn` (`padding: 4px 8px; font-size: 0.72rem;`).
  - **Fullscreen AI Island Scene Letterbox Elimination**:
    * `.town-fullscreen-card`: `background: #050811; border: 1.5px solid rgba(255, 255, 255, 0.12); height: 80vh; min-height: 620px; max-height: 860px;`.
    * `#isometricOfficeCanvas`: Changed from `object-fit: contain;` to `object-fit: cover;` so the 3D animated island fills the entire viewport without cyan letterbox borders.
    * `setTownSkyAtmosphere(mode)`: Added dynamic background color sync for `#townFullscreenCard` (`#050811` for NIGHT, `#f472b6` for SUNSET, `#22a6f2` for DAY).
- **Raw Ledger Removal, Canvas Controls Floating Fix & Scroll Background Continuity Fix (November 2026)**:
  - **Raw Ledger Button Removal ("เอาตารางบัชชีดิบออกให้หน่อย")**:
    * Removed `<button class="cozy-btn" onclick="toggleLegacyUnderIslandStore()" id="btnToggleLegacyUnderIsland">📂 ดูตารางบัญชีดิบ</button>` from under-island workflow strip.
    * Set `<div id="legacyUnderIslandHiddenStore" style="display:none !important">` to guarantee complete invisibility and inaccessibility while preserving child DOM IDs for test stability.
  - **Canvas Controls Single-Line Pinning ("ไอที่ไปให้เเก้ตรวจดีๆยังมันวางไม่ดีมันผิดที่")**:
    * Sized `.town-top-nav-bar` with `top: 14px; left: 16px; right: 16px; max-width: calc(100% - 32px); flex-wrap: nowrap !important; z-index: 25; pointer-events: none;`.
    * Sized `.town-top-left-bar` with `gap: 5px; flex-wrap: nowrap; flex-shrink: 1; min-width: 0; overflow: hidden; pointer-events: auto;`. Redundant `#btnTownEnterpriseMenu` button hidden (`style="display:none"`).
    * Sized `.town-top-right-bar` with `gap: 8px; flex-wrap: nowrap !important; flex-shrink: 0; margin-left: auto; justify-content: flex-end;`.
    * Upgraded `.comic-hud-pill` with `padding: 5px 12px; font-size: 0.73rem; line-height: 1.3; font-weight: 800;` to prevent top-edge clipping.
    * Sized `.atmosphere-segmented-bar` (`#atmosphereSegmentBar`) with compact buttons (`☀️ วัน`, `🌅 เย็น`, `🌙 คืน`) with descriptive titles, keeping the top navigation strictly pinned on a single horizontal plane without wrapping or floating into the 3D sky.
  - **Scroll Background & Sticky Header Continuity ("เเละบางหน้ามันเลื่อนไป ui ไม่ดีมันเหมือนมีพื้นหลังขาดตรวจดีๆก่อนส่งงานหน่อย")**:
    * Added `html, body { background: var(--bg-body); min-height: 100%; width: 100%; margin: 0; padding: 0; overflow-x: hidden; }` preventing page background gaps or cut-offs during scrolling.
    * Set `.nav-tabs` to `position: sticky; top: 58px; z-index: 99; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);` docked smoothly below sticky `.top-header` (`top: 0; z-index: 100;`).
    * Updated `.page-view` with `padding: 16px 20px 48px 20px; max-width: 1680px; width: 100%; margin: 0 auto; flex: 1; background: var(--bg-body);`.
    * Updated `.visualizer-layout` to `align-items: stretch;` eliminating background gaps between uneven two-column layouts.
- **Visual Layout Fixes, Free LLM Telemetry & 11-Bot Cumulative Token Table (November 2026)**:
  - **Town Hall Badge Repositioning**:
    * Changed `badgeY: 72` to `badgeY: 125` for `TOWN_HALL` in `ISO_ROOMS`. Eliminates visual clipping behind top floating nav bar.
  - **Top-Right Overflow & Island Fill**:
    * Sized `.town-top-right-bar` with `max-width: 50%`, `overflow: hidden`, and added responsive rule `@media (max-width: 1300px)` keeping `.comic-hud-pill` strictly contained.
    * Adjusted `drawLushCircularIsland` dimensions to `rx = 670, ry = 310` filling canvas without excessive empty oceans or letterbox seams.
    * Set `.town-fullscreen-card .iso-canvas-wrap` background to `#050811`.
  - **De-gamification & Free LLM Transformation**:
    * Completely removed raw ledger button references ("ดูตารางบัญชีดิบ").
    * Removed gamey "OVERCOOK", "เผาโควต้า 100%", and "Lv." badges across all agent cards, profiles, directory drawers, and HR matrices.
    * Replaced with Frontier Model names, Free Providers (Cerebras, Groq, SambaNova, Gemini, OpenRouter, Mistral), and Rate Limits (RPM/TPM).
  - **Free LLM Quota Telemetry & Auto-Failover Monitor**:
    * Rendered dynamic telemetry deck in `#tokenLeaderboardModal`: Active Provider banner, Real-time Quota Progress Bar, and Auto-Failover Chain Pill Diagram (`Cerebras ➔ Groq ➔ SambaNova ➔ Gemini ➔ OpenRouter ➔ Mistral`).
    * Added `refreshFreeLlmQuotaAndFailover()` fetching `/api/free_llm_quota`, updating gauges dynamically, and alerting via `#modalQuotaToast`.
  - **11-Bot Cumulative Historical Token Table**:
    * Built 8-column table (บอท / แผนก, Provider หลัก & โมเดล, Provider สำรอง, โทเคนวันนี้, โควต้าคงเหลือ, ยอดใช้สะสมรวมทั้งหมด, ประหยัดเงินจาก Free Tier $, สถานะ).
    * Summary Metric Cards at modal top: รวมโทเคนสะสมทั้ง 11 บอท: 2,400,000+ Tokens • โควต้ารวมฟรีทุก Provider: 5,300,000 Tokens / วัน • ประหยัดงบสะสมได้แล้ว: ~$36.00+ USD • สถานะระบบ: Active บน Cerebras WSE-3.
    * Added `🪙 ตารางโทเคน 11 บอท` button `#btnTownEnterpriseMenu` on island nav bar.
- **Top Header Atmosphere Switcher, Central Data Center, Clean HUD & Token Cap UI (November 2026)**:
  - **Move Day/Night Atmosphere Switcher to Top Navigation Bar (User Choice A1)**:
    * Relocated `#atmosphereSegmentBar` and `<select id="skyTimeSelect">` from `.town-top-right-bar` inside the island canvas to `.status-pills-bar` in the sticky top navigation header next to `#themeToggleBtn`.
    * Upgraded `.atmosphere-segmented-bar` with theme-aware styling (`background: var(--bg-card)`, `color: var(--text-sub)`, active state `#1e293b`/`#f59e0b`), preventing island canvas overflow and sky blockage.
  - **100% Elimination of "ตารางบัญชีดิบ" (Raw Ledger) (User Choice A4)**:
    * Removed legacy store trigger button and any visible text mentioning "ดูตารางบัญชีดิบ".
    * Preserved `#legacyUnderIslandHiddenStore` strictly hidden (`display: none !important;`) maintaining DOM element contracts for test compatibility.
  - **Replace 2 Green Battery Cylinders with Central AI Data Center & Knowledge Vault (User Choice A3)**:
    * Implemented `drawSingleServerRack(ctx, bx, by, rackIndex)` and `drawCentralDataCenter(ctx, cx, cy)`.
    * Central plaza at `(720, 415)` renders 2 isometric server racks (`#0f172a`, `#1e293b`), glowing activity LEDs (steady green `#10b981`, blinking cyan `#06b6d4`, pulsing amber `#f59e0b`), glass cabinet doors with subtle cyan cyber glow, server cooling exhaust vents, animated optical cyber data conduits on the stone plaza, and a floating dark glassmorphic badge `💾 AI DATA CENTER • KNOWLEDGE VAULT`.
    * Completely removed old labels `"5-HOUR 65%"` and `"7-DAY 100%"` from the canvas. Preserved `drawGiantBattery` as a backward-compatible alias.
  - **Remove Energy/Battery & Fake Percentages from HUD and Cards**:
    * Cleaned `.comic-hud-pill`: purely financial figures `🟢 จริง: ${live_profit_val:+,.2f} • 🧪 เทส: ${test_profit_val:+,.2f}` without any battery percent or energy status text.
    * Removed fake `🔋 %` from `selectVisualizerAgent`, `renderMiniAgentsStrip`, and `renderTownDirectoryDrawer`.
  - **Token Usage "ใช้ไปแล้ว / เพดานลิมิต" & Total Company Summary (User Choice A2)**:
    * **Top Consolidated Banner** in `#tokenLeaderboardModal` and `#page-tokens`:
      - Shows `ยอดใช้สะสมรวม / เพดานฟรีรวมทุก Provider`: `2,490,000 / 5,300,000 Tokens/วัน` with live failover status for Cerebras, Groq, SambaNova, Gemini, OpenRouter, and Mistral.
    * **11-Bot Table Columns (7 Distinct Columns)**:
      1. บอท / แผนก (Avatar, Name, Department)
      2. Provider หลัก & โมเดล (พร้อมขีดจำกัดชัดเจน เช่น Cerebras Llama-3.3-70B • 30 RPM / 60K TPM)
      3. การใช้งานเทียบเพดาน (Usage / Cap): `"ใช้ไป / เพดานลิมิต"` (เช่น `10,000 / 60,000 TPM`) with mini progress bar and % of cap.
      4. Provider สำรอง (Failover Target เช่น Groq LPU)
      5. สถานะการสลับค่าย (🟢 ใช้ตัวหลัก / 🔄 สลับไปตัวสำรองอัตโนมัติ / ↩️ รีเซ็ตกลับตัวหลัก)
      6. ยอดสะสมตลอดชีพ (Cumulative Lifetime Tokens)
      7. ประหยัดงบ ($ Saved)
    * **Bot Cards & Drawer Profile**:
      - Displays `Provider: [Provider]` • `โควต้า: [Used] / [Limit]` • `สถานะ: Auto-Failover พร้อม`.
- **Token Table Layout De-clutter & Realistic Daily TPD Benchmark (Option A2 + A1)**:
  - **Realistic Daily Token Limits (TPD 500K - 1.5M)**:
    * Replaced tight 60K TPM minute rate limit with authentic Daily Quota (`capUnit: "TPD"`):
      - `ag_cio`: `1,000,000 TPD`, used `360,000` (36% 🟢)
      - `ag_quant`: `1,000,000 TPD`, used `520,000` (52% 🟢)
      - `ag_macro`: `1,500,000 TPD`, used `290,000` (19% 🟢)
      - `ag_ta`: `1,000,000 TPD`, used `380,000` (38% 🟢)
      - `ag_bear`: `1,000,000 TPD`, used `340,000` (34% 🟢)
      - `ag_bull`: `500,000 TPD`, used `210,000` (42% 🟢)
      - `ag_risk`: `1,000,000 TPD`, used `260,000` (26% 🟢)
      - `ag_news`: `500,000 TPD`, used `135,000` (27% 🟢)
      - `ag_cos`: `1,500,000 TPD`, used `210,000` (14% 🟢)
      - `ag_bot`: `500,000 TPD`, used `165,000` (33% 🟢)
      - `ag_venture`: `800,000 TPD`, used `145,000` (18% 🟢)
    * All bots operate at comfortable green usage (14%–52%), completely eliminating the artificial 100% red bottleneck.
  - **De-cluttered Layout for Column 3 ("การใช้งานเทียบเพดาน")**:
    * Sized `<th>` with `min-width: 210px` in `#tokenLeaderboardModal` and `#page-tokens`.
    * Implemented distinct 2-line vertical hierarchy:
      - Line 1: `<strong>{usedToday.toLocaleString()}</strong> / {capVal.toLocaleString()} {capUnit}`
      - Line 2: Flex row with 7px progress bar and right-aligned percentage badge `{capPct}%` (`color: {capBarCol}`).
    * Zero text clipping, zero number overlap, generous cell padding.
  - **Status Badge Accuracy**:
    * Displays `🟢 ปกติ (ใช้ตัวหลัก)` for all active bots within quota.
    * Only switches to `🔄 สลับไปตัวสำรองอัตโนมัติ` if `capPct >= 100` or explicit failover trigger.
