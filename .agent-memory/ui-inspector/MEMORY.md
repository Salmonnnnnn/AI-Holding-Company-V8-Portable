# 🎨 Elite UI/UX Visual Inspector Memory (`ui-inspector`)

## 🎯 Reference Benchmark (`Exmple.mp4` TV Screen Web App)
- **Layout Model**: Full-bleed interactive 3D/Isometric Island Town canvas (`AI Office` / `Aurum Isle`) occupying the entire viewport, with floating game-style HUD overlays (instead of cramped multi-box enterprise cards).
- **Floating HUD Elements from `Exmple.mp4`**:
  1. **Top Bar (Floating Pills)**:
     - Brand title (`🏢 AI Office` / `🏝️ Aurum Isle`)
     - Green status pill (`▶ 6 working`)
     - Orange action pill (`⏸ Pause` / `▶ Resume`)
     - White rounded pills (`👥 View All`, `📊 Stats`, `📬 Inbox` with red badge count, `☰ Menu`)
  2. **Left / Top-Left Currency & Challenge HUD**:
     - Gold coin / Revenue badge (`🪙 $0` / `$1,000 Goal`)
     - Level / Day indicator (`DAY 1 OF 30`)
  3. **Bottom-Right Floating `Messages` Box**:
     - White/translucent card with header `Messages` and minimize button `[-]`
     - Live stream of agent-to-agent handoffs (`Agent A → Agent B: ...` with timestamps like `8:05 PM`)
  4. **Distinct Work Zones on the Circular Green Island**:
     - Central Plaza with blue-roof civic building + 2 giant green battery cylinders (`5-HOUR 99%`, `7-DAY 100%`)
     - Top: Classical `Town Hall` with white columns, green dome, and `The Boss`
     - Fenced peripheral work zones with wooden/colored zone banners:
       * `TECH STUDIO` (blue banner, fenced compound on right with white/teal houses & `</>`)
       * `ONLINE SHIRTS / STORE` (green banner, fenced compound with lighthouse & shop houses)
       * `MEME STUDIO` (orange banner, fenced compound at bottom-left with red/white circus tent & houses)
       * `WHAT IF STUDIO` / Video Lab (purple banner, fenced compound on left)
       * Inner ring specialist houses: `Forge` (`</>`), `Hype` (purple), `Critic` (green), `Courier` (red), `Design` (pink), `Observatory` (dome)
- **Known UI Pitfalls to Guard Against**:
  - Do not use raw unstyled `<select>` dropdowns for atmosphere switching; use sleek segmented HUD pill buttons with active highlight and smooth canvas palette transitions (Sky Blue default like video, Sunset, Night).
  - Ensure floating HUD overlays never obscure clickable studio buildings or collide with each other.
