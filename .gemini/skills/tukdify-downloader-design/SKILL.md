---
name: tukdify-downloader-design
description: Comprehensive design system and UX guidance for the Tukdify Video Downloader desktop application. Use when designing, styling, reviewing, or implementing CustomTkinter desktop UI/UX for Tukdify Downloader. Enforces intentional visual identity, Obsidian Studio design tokens, responsive constraints, accessibility, and high-performance offline media ingestion workflows.
---

# Tukdify Video Downloader Desktop Design Skill

This skill guides the design, layout, styling, and user experience of **Tukdify Video Downloader** — a free, offline, telemetry-free desktop application built with Python and CustomTkinter that provides universal 4K/1080p video and 320kbps MP3 audio media ingestion for creators, editors, and archivists.

---

## 1. Product Identity & Brand Architecture

- **Desktop Application:** `Tukdify Video Downloader` (window title, taskbar, executable branding).
- **Umbrella Brand:** `Tukdify` (domain: `tukdify.com`, publisher name, creator ecosystem).
- **Brand Mark:** Approved Metal Silver Falcon with signature blue eye.
- **Audience:** Video creators, podcasters, video editors, archivists, and freelancers requiring fast, local, watermark-free media ingestion.
- **Product Personality:**
  - **Ultra-Fast & Offline-First:** Instant start, clean offline processing, zero cloud lock-in.
  - **Creator-Centric:** One-click format selection, metadata extraction, live progress metrics.
  - **Sleek & Calming:** Obsidian dark studio aesthetic, uncluttered layout, progressive disclosure.

---

## 2. Core Visual Design Principles (Claude & Lovable Standards)

### A. Ground in the Subject (Media Ingestion Studio)
- Avoid noisy, multi-colored clashing web dashboards with arbitrary widgets.
- The interface must reflect the exact flow of an editor: **URL Input -> Stream Analysis -> Format Selection -> High-Speed Ingestion & Verification**.

### B. Top Global Header Navigation
- Use a persistent top header bar (`56px` height) rather than a heavy, space-consuming left sidebar:
  - **Left:** Metal Silver Falcon mark (`22x22`), bold app title, subtle dot separator, and brand lockup.
  - **Center:** Unified segmented navigation pill container (`Downloads`, `History`, `Settings`, `About`).
  - **Right:** Accessible utility buttons (`🌐 Follow`, `❤️ Support`).

### C. Semantic Design Tokens (`ui/theme.py`)

```python
# Semantic Obsidian Studio Palette
APP_BG            = "#0e1017"  # Deep Obsidian studio canvas
SIDEBAR_BG        = "#12141d"  # Top header & container frames
CARD_BG           = "#171923"  # Primary cards & section panels
CARD_HOVER        = "#252838"  # Hovered cards & elevated popovers
INPUT_BG          = "#1f212d"  # Recessed input wells, segmented bars
BORDER            = "#2b2f42"  # Subtle structural 1px borders
BORDER_HOVER      = "#3b415a"  # Active / hovered borders
BORDER_FOCUS      = "#6366f1"  # High-visibility accessible focus ring

TEXT_PRIMARY      = "#f0f2f8"  # High-contrast primary text
TEXT_MUTED        = "#8b92a7"  # Secondary labels & parameters
TEXT_FAINT        = "#52576d"  # Tertiary hints & timestamps

BRAND_ACCENT      = "#6366f1"  # Vivid Indigo primary CTA & selection
BRAND_ACCENT_HOV  = "#7a7dff"  # Primary CTA hover
BRAND_ACCENT_ACT  = "#4f52d6"  # Primary CTA pressed
BRAND_ACCENT_SOFT = "#1e1b4b"  # Selected badge / soft pill background

STATUS_SUCCESS    = "#10b981"  # Completed downloads & verified states
STATUS_WARNING    = "#f59e0b"  # Notices, stream merging with FFmpeg
STATUS_ERROR      = "#ef4444"  # Network failures & stream errors
```

### D. Typography Hierarchy
- **Window Title / Header:** 14px Bold (`Segoe UI`, `SF Pro Display`, sans-serif)
- **Page Titles:** 18px–20px Bold (`#f0f2f8`)
- **Card Section Titles:** 11px Bold (`#8b92a7`, uppercase, tracking +0.5px)
- **Primary Control Labels:** 13px–14px Bold (`#f0f2f8`)
- **Secondary / Helper Text:** 12px Regular (`#8b92a7`)
- **Metrics / Speeds / Timers:** 11px–12px Monospace (`Consolas`, `Roboto Mono`)

---

## 3. Desktop Ergonomics & Layout Rules

1. **Responsive Window Constraints:**
   - Baseline target: **1366 x 768** (standard laptop screen).
   - Default launch dimensions: **1120 x 760** px.
   - Minimum floor: **960 x 640** px.
2. **Content Column Centering:**
   - Center main action columns with an optimal reading width of **740px–760px** (`center_column` helper).
3. **Corner Radii Hierarchy:**
   - `6px–8px`: Buttons, segmented pills, input boxes, badges.
   - `12px–14px`: Hero cards, metadata preview cards, dialog containers.

---

## 4. Downloader Engine Integration Rules

- Always offload information extraction (`extract_info`) and downloads (`Downloader.run`) to daemon worker threads.
- Maintain high-resilience extraction with modern player clients (`ios`, `android`, `mweb`, `web`) to prevent HTTP 403 errors.
- Ensure all GUI callbacks updating Tkinter widgets use `self.after(0, ...)` to guarantee thread safety.
