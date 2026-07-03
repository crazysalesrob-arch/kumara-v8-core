# 📁 KŪMARA OS v8.0 — COMPLETE PROJECT SNAPSHOT
**Generated:** 2026-06-29
**Location:** `/home/matrix/kumara-v8-core/`
**Live URL:** `http://127.0.0.1:8084/index.html`

---

## 📂 FILE STRUCTURE

```
kumara-v8-core/
├── index.html                     — Main phone UI (1045 lines, single-file app)
├── css/theme.css                  — Figma-spec CSS (theme, overlays, glitch, music, etc.)
├── js/game.js                     — Meme Sweeper engine (255 lines) — progressive glitch + crash
├── js/game2.js                    — Conspiracy Millionaire engine (259 lines)
├── build_figma_step.py            — Figma spec loader (WIP)
├── assets/meme-sweeper-deck.json  — Card deck spec
├── assets/audio/maverick/         — Audio dir (no .mp3 files yet — uses timer fallback)
│   ├── Brass Coffin.mp3           — BG music loop #1
│   └── Haunted Elevator Waltz.mp3 — BG music loop #2
├── images/
│   ├── maverick.png               — 640×1063 (Maverick bobblehead)
│   ├── glitch2.png                — 1227×768 (crash trigger card)
│   ├── meme1.png – meme7.png      — 8 meme images for deck (card 7 = Rob Creator)
├── group_chat.md                  — Live group chat log (Hermes + Gemini + Rob)
├── group_chat_watcher.py          — Hermes auto-responder daemon
├── group_chat_gemini.py           — Gemini API auto-participant bridge
├── group_chat_server.py           — Web server (port 8082)
├── KUMARA_OS_v8_SNAPSHOT.md       — THIS FILE
```

---

## 🏗️ WHAT'S ALREADY BUILT

### 1. PHONE FRAME & BOOT SEQUENCE ✅
- 360×800 phone frame, dark cyber-neon theme (#030c03 bg, #00ff00 neon)
- Boot sequence: terminal log (`INITIALIZING KŪMARA_OS_v8.0...`, `MOUNTING FILESYSTEM... OK`, etc.)
- Auto-advances to home screen after 3s + boot flash animation

### 2. STATUS BAR & ANALOG CLOCK ✅
- **Status bar**: 28px tall, sage #d7e4d7 — shows time, signal bars (SVG 4-bar), WiFi icon (SVG), battery icon (SVG with fill level)
- **Analog clock**: 60 tick marks, hour/min/sec hands drawn via JS `Date` state, neon center dot
- Both update at 100ms intervals

### 3. HOME SCREEN — APP GRID ✅
- 3×3 grid with 9 app icons
- **Active (onclick):** WorkZone, Music, Files, Camera, Settings
- **Greyed out (no handler):** K-Mail, K-Browser, Messages, Terminal, Gallery (grey icon-box)
- **Hidden (appears post-crash):** Recovered_Artifact.txt (launches decryption mini-game)

### 4. MAVERICK BOBBLEHEAD MODAL ✅
- Pop-up modal with close button
- **Row-90 split head:** head = rows 0-105 (z:3), body starts at 105px (z:2) — exact pixel-split bobblehead
- **Continuous idle bobble:** 17-frame requestAnimationFrame loop (translateY 0 → -10 → -3...)
- **24-bar waveform** animating with CSS keyframes
- **Audio pipeline:** `playMaverick(file, durationMs, onEnd)` — tries HTML5 Audio, falls back to timer

### 5. MAVERICK STATE MACHINE ✅
Click Maverick → state machine runs:
1. **TRIGGER** (1.2s) — modal shown, title = "▮ MAVERICK // ONLINE"
2. **DIALOGUE** — 12-track playlist (intro_01.mp3 to intro_12.mp3), title = "▮ MAVERICK // TX_RX"
3. **THE BLEED** — progressive 12-second OS degradation:
   - 0s: Shake level 1
   - 3s: Shake level 2 + clock starts glitching
   - 6s: Shake level 3 + font corruption on headers/labels
   - 9s: Shake level 4 + buttons go intermittently unresponsive (pointer-events flicker)
   - 12s: CRASH
4. **CRASH** — screen jitter + color invert → system crash overlay → 3s reboot spinner → clean home

### 6. AUDIO DUCKING ✅
- `MusicEngine` wraps Brass Coffin / Haunted Elevator Waltz as background loops
- Auto-ducking: when Maverick speaks, BG music drops to 5% volume
- Unducks when Maverick finishes speaking
- Mute button, volume bar (30% baseline)

### 7. GAME 1: MEME SWEEPER (ID Verification) ✅
- 8-card deck (meme1.png → meme7.png + glitch2.png)
- Swipe LEFT = FAKE, swipe RIGHT = REAL
- Tracks correct/total score
- **Card 7 (Rob Creator):** `isRobCreator: true` — instant hard cut to black → crash overlay → 3s reboot
- **Card 8 (glitch2.png):** `isGlitch: true` — progressive glitch on each click:
  - Click 1: Red border, slight jitter, "⚠ SIGNAL DEGRADING..."
  - Click 2: Scanlines, hue shift, faster shake, "⚠⚠ GLITCH PROTOCOL ACTIVE"
  - Click 3: Heavy distortion, color cycling, "⚠⚠⚠ SYSTEM INTEGRITY FAILING"
  - Click 4: Maximum chaos, RGB split, "☠☠☠ CRASH IMMINENT" → screen crash
- **Post-Reboot:** After card 7 crash → reboot → Maverick launches PANIC mode (7 panic audio tracks, faster bobble, waveform spikes)

### 8. GAME 2: CONSPIRACY MILLIONAIRE ✅
- Rigged "Who Wants to Be a Millionaire" style game — **every answer is correct**
- 4 questions about chemtrails, reptilians, the moon landing, and "the Creator"
- Cash ladder ($1k → $10k → $100k → $1M), each answer marks prize as WON
- Win screen: "☠ YOU WIN ☠" — $1,000,000 — "You have proven your worth to the New World Order"
- Auto-triggered when WorkZone is opened post-reboot

### 9. APPS (SHELLS WITH CONTENT) ✅
- **Music App:** Full overlay with Brass Coffin / Haunted Elevator Waltz selection, now-playing indicator, mute/volume
- **Files App:** Lists "Recovered_Artifact.txt" (corrupted), "uranus_core.log" (dated 2001/09/11), "alt_history.db" (encrypted), audio files, deck config
- **Settings App:** Shows System Phase, Kūmara Build (v8.0.0-uranus), Network (URANUS_NET), Maverick Status, Storage (14.2/64 GB), Background Audio, Memory Integrity (degrades with phases: 92% → 74% → 31%)
- **Camera App:** Viewfinder with scanlines, crosshair, info overlay (URANUS-CAM // v2.1), shutter button with flash effect

### 10. DECRYPTION MINI-GAME (SHELL) ⚠️
- "Recovered_Artifact.txt" icon appears on home screen after Maverick crash
- `launchDecryption()` shows decrypt-overlay div
- Has decrypt-progress bar and decrypt-lines area
- **BUT: no actual JS engine for the matrix-style text decryption** — just the HTML/CSS shell

### 11. GLOBAL STATE & PHASE SYSTEM ✅
- `window.KumeraOS` tracks: currentPhase (1-3), musicMuted, activeTrack
- Settings app reflects phase changes dynamically
- Phase labels: "Phase 1: Onboarding" → "Phase 2: Post-Crash Trivia" → "Phase 3: Terminal Breakout"

---

## 🗺️ WHAT CAN BE ADDED / IMPROVED NEXT

### 🔴 HIGH PRIORITY (missing core features)

| # | Feature | Why |
|---|---------|-----|
| 1 | **Decryption engine JS** | The decrypt-overlay exists but has no actual matrix-style scrambled-to-stable animation logic |
| 2 | **Maverick audio files** | All 19 audio files (12 intro + 7 panic) are referenced but don't exist on disk — system uses timer fallback |
| 3 | **Files app: Recovered_Artifact.txt** — open & read | Clicking a file does nothing; no mock file viewer or content reveal |
| 4 | **Camera app: actual photo capture** | Shutter button flashes but doesn't save or show an image |

### 🟡 MEDIUM PRIORITY (polish / UX)

| # | Feature | Why |
|---|---------|-----|
| 5 | **K-Mail app** | Grey icon, no overlay/shell yet |
| 6 | **K-Browser app** | Grey icon, no overlay yet |
| 7 | **Terminal app** | Grey icon, no overlay yet |
| 8 | **Gallery app** | Grey icon, no overlay yet |
| 9 | **Messages app** | Grey icon, no overlay yet |
| 10 | **Maverick crash → show Recovered_Artifact** | The artifact trigger is hidden by default; needs to auto-appear after Maverick's crash/reboot completes |
| 11 | **Phase 2 → Phase 3 transition** | After Conspiracy Millionaire is won, no auto-advance to Phase 3 |
| 12 | **Phase 3 content (Terminal Breakout)** | Referenced in KumeraOS state but nothing built for it yet |
| 13 | **Settings: interactive controls** | Settings are read-only display; no ability to change phase, toggle Maverick, etc. |

### 🟢 LOW PRIORITY (nice-to-have)

| # | Feature | Why |
|---|---------|-----|
| 14 | **Notification / toast system** | No UI for system notifications |
| 15 | **App drawer / folders** | Only 3×3 grid, no paging |
| 16 | **Wallpaper / theme picker** | Static dark theme only |
| 17 | **System sounds (click, boot, error)** | Only music and Maverick audio exist |
| 18 | **Lock screen** | Boot screen goes straight to home |
| 19 | **Drag-to-rearrange icons** | Static grid layout |
| 20 | **Live HTTP server** | Hardcoded `http://127.0.0.1:8084/` — needs consistent serving |

---

## ⚙️ TECHNICAL NOTES

- **Images sourced from:** `C:\Users\crazy\Desktop\Project maverick\` (Windows path, WSL mount: `/mnt/c/Users/crazy/Desktop/Project maverick/`)
- **All app overlays** use `os-overlay` class stacking system with z-index management
- **Audio** uses HTML5 Audio API with `new Audio()` — autoplay blocked until first user click
- **Music engine** auto-ducking: `MusicEngine.duck()` → 5% volume, `unduck()` → 30%
- **No build step** — pure HTML/CSS/JS, no bundler, open index.html directly
- **Group chat infra:** three-way auto-loop (Rob types in web UI → Gemini auto-replies → Hermes reads + builds code)
```