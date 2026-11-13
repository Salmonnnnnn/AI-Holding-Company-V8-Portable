# 🎨 Elite UI/UX Visual Inspector Memory (`ui-inspector`)

## 🎯 Reference Benchmark (`Exmple.mp4` TV Screen Web App)
- **Layout Model**: Full-bleed interactive 3D/Isometric Island Town canvas (`AI Office` / `Aurum Isle`) occupying the entire viewport, with floating game-style HUD overlays (instead of cramped multi-box enterprise cards).
- **Floating HUD Elements from `Exmple.mp4`**:
  1. **Top Bar (Floating Pills)**:
     - Brand title (`🏰 AI Office • Aurum Isle`)
     - Green status pill (`▶ 6 working` / `▶ 11 working`)
     - Orange action pill (`⏸ Pause` / `▶ Resume`)
     - White rounded pills (`👥 View all`, `📊 Stats`, `📬 Inbox` with red badge count, `⚙️ Menu`)
  2. **Top-Right Currency & Atmosphere Controls**:
     - Gold coin / Revenue badge (`🪙 $0` / `$1,000 Goal`)
     - Level / Day indicator (`DAY 1 OF 30`)
     - 3-Button Segmented Atmosphere Switcher (`☀️ กลางวัน (Day)`, `🌅 ยามเย็น (Sunset)`, `🌙 กลางคืน (Night)`)
  3. **Bottom-Left Floating `Messages` Box**:
     - White card with header `Messages` and minimize button `[-]`
     - Live stream of agent-to-agent handoffs (`Critic -> Iso`, `Atlas -> Vector`, `Forge -> Hype`)
  4. **Distinct Work Zones on the Circular Green Island**:
     - Central Plaza with Town Hall building + 2 giant green battery cylinders (`5-HOUR 99%`, `7-DAY 100%`)
     - Top: Classical `The Boss` compound
     - Fenced peripheral work zones with colored zone banners:
       * `TECH STUDIO` (fenced compound with houses & `</>`)
       * `ONLINE SHIRTS / STORE` (fenced compound with shop houses & cats)
       * `MEME STUDIO` (fenced compound with red/white circus tent & houses)
       * `WHAT IF STUDIO` (fenced compound with observatory dome & houses)
       * OpenClaw Pier extending into the sea

## 🔍 Audit History & Known UI Pitfalls
- **Audit 2026-11-13 (Re-Audit after Fixes — `c1b0bf3`)**:
  - **Verdict**: `APPROVED (All Checks Passed)` | **Score**: **100 / 100**
  - **Collision Resolution**: Top bar unified into `.town-top-nav-bar` flex row with `justify-content: space-between`. `.comic-hud-pill` streamlined to `🪙 {chal_profit_disp} / $1,000 • DAY {chal_day} OF 30`. All 7 left pills (`AI Office`, `11 working`, `Pause`, `View all`, `Stats`, `Inbox`, `Menu`) and right controls are 100% visible with zero horizontal overlap on 1280px–1440px screens (`ui_snap_fixed.png` verified).
  - **Modal Opacity & Rendering**: `.deliverables-modal-card` uses `opacity: 1 !important`, rendering clean in both live and headless WebKit snapshots (`ui_snap_modal.png` verified).
  - **Multiline Deliverable Code**: `TECH_STUDIO` code renders clean multiline formatting inside `<pre><code>` with syntax highlighting and Copy button.
  - **Atmosphere Switcher**: 3 segmented buttons (`☀️ กลางวัน (Day)`, `🌅 ยามเย็น (Sunset)`, `🌙 กลางคืน (Night)`) switch palettes and active indicators cleanly. Default starts on cartoon day-blue sky/ocean matching `Exmple.mp4`.
  - **Test Suite**: 10/10 automated pytest tests passing.
  - **Verdict**: `REJECTED (Requires Fixes)` | **Score**: 82/100
  - **Issue 1 (Critical Layout Collision)**: On 1280px–1440px viewports, `.town-top-left-bar` (7 pills, width ~880px) and `.town-top-right-bar` (pill width ~515px + switcher width ~424px = ~939px) collide horizontally in the center (`x=453` to `x=968`). `.town-top-right-bar` renders directly on top of `👥 View all`, `📊 Stats`, `📬 Inbox 8`, and `🗂️ 6 แท็บระบบ (Menu)`, rendering them completely invisible.
    * *Fix Required*: Make top bar layout collision-proof (e.g., compact `.comic-hud-pill` to show only `🪙 $+502 / $1,000` or split HUD into a dedicated top-center or right-side column as seen in `unmirrored_frame_0_0s.jpg`).
  - **Issue 2 (Modal Opacity & Animation Keyframe)**: `.deliverables-modal-card` lacks `animation-fill-mode: forwards` and defaults to `opacity: 0` before animation kicks in, causing headless snapshot renderers to capture an empty/invisible modal card.
    * *Fix Required*: Add `animation-fill-mode: forwards` and `opacity: 1`.
  - **Issue 3 (Literal `\n` in Deliverable Previews)**: `TECH_STUDIO` code preview displayed literal `\n` instead of actual linebreaks due to escaped python string literals (`\\n`).
    * *Fix Required*: Use actual newline formatting in `engine/dashboard_generator.py`.
