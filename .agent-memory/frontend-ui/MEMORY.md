# 🎨 Frontend & UI/UX Specialist Memory

## 🖥️ Presentation Layer Overview
- **Renderer**: `engine/dashboard_generator.py` generates self-contained single-page dynamic HTML/CSS/JS.
- **Port**: Default `8080` (configurable via `SERVER_PORT` or CLI `--port`).
- **Style**: Cozy Isometric Cutaway Office 3D (inspired by `@ong_stw` TikTok office concept).
- **Theme Support**: Dual mode toggle (☀️ Light Mode / 🌙 Dark Mode).

## 🗂️ Dashboard Modules & Tabs
1. **🏢 Isometric Cutaway 3D Office**: Real-time room status, animated agents, shift indicators.
2. **📊 Trading War Room & MT5 Demo**: Order execution pipeline, real-time charts, Kelly sizing panel.
3. **💎 Obsidian Knowledge Graph**: Interactive Canvas Graph-RAG node viewer (1-Hop Subgraph token saver).
4. **🪙 Token Treasury**: Token consumption breakdown, cost savings counter, speed dials.
5. **🎓 Skill Academy & Harvester**: AI level progression, discovered skills matrix.
6. **💬 Copilot Chat & Committee Log**: Live prompt exchange with agent council.

## 🎨 Design Rules
- Keep JavaScript modular and vanilla (zero external heavy npm build steps required).
- Responsive grid ensuring readability on both desktop monitors and laptops.
- Ensure isometric SVG/Canvas elements re-render cleanly on theme switches.
