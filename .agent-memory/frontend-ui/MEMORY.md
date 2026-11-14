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

## 🗂️ 9 Enterprise Navigation Pages & Key Upgrades
- **macOS Canvas Emoji+Thai Text Right-Shift Fix (`fillCenteredText`)**:
  - Replaces `ctx.textAlign = "center"; ctx.fillText(...)` across all Canvas 2D label drawing functions (`drawRoundedBadge`, `drawZonePillBanner`, `drawTownCottage`, `drawTheBossPodium`, `drawGiantBattery`, `drawChibiAgent`, etc.) with `fillCenteredText(ctx, text, cx, y)` using `ctx.textAlign = "left"` and `Math.round(cx - ctx.measureText(s).width / 2)` so CoreText on macOS WebKit/Chrome never shifts Emoji+Thai strings to the right.
  - Added dedicated `badgeX` and `badgeY` coordinates to every room in `ISO_ROOMS`, removed the duplicate small `"🌉 OpenClaw"` badge in `drawOpenClawPier`, and cleared `idx === 1` initial speech bubble so Town Hall and zone banners have zero overlapping labels.
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
- **Typography & Table Rules**: Use `.section-head` flex wrappers (`flex-wrap: wrap`) so card titles and action buttons never collide on 1280px–1440px screens; wrap wide tables in `.table-wrap` (`overflow-x: auto`) and apply `.num` (`white-space: nowrap`) to numeric/badge cells.
