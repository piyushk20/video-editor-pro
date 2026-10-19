# Architecture & Production Pipeline

Video Editor Pro processes media through a deterministic, modular 5-phase pipeline. Each phase is self-contained and outputs structured JSON or media files.

---

## Phase 0: Ingestion & Input Normalization
**Script:** `tools/phase0_input_handler.py`

### Capabilities:
- Ingests local media (`.mp4`, `.mov`, `.wav`, `.mp3`), audio podcasts, web URLs (YouTube / direct stream), or infographics.
- Probes media stream properties via `ffmpeg` / `ffprobe`:
  - Width, height, aspect ratio
  - Frame rate (FPS) and video codec
  - Audio channels and sample rate
- Sets up standard project folders and outputs a normalized `manifest.json`.

---

## Phase 1: Whisper Transcription & Semantic Analysis
**Script:** `tools/phase1_analyser.py`

### Capabilities:
- Extracts audio to high-quality WAV.
- Transcribes speech using **Faster-Whisper** with word-level precision timestamps.
- Generates:
  - Timestamped subtitle file (`transcript.srt`)
  - Full transcript metadata (`transcript.json`)
  - Hook detection (first 5 seconds scoring)
  - Key thematic takeaways, quotable moments, and chapter markers
  - Semantic content analysis (`content_analysis.json`)

---

## Phase 2: Creative Director & Pacing
**Script:** `tools/phase2_director.py`

### Capabilities:
- Formulates pacing, b-roll triggers, kinetic caption timing, and graphic placements.
- Enforces user rules (e.g. 9:16 vertical layout, upper safe-zone graphics).
- Outputs `edit_plans/<project_name>_edit_plan.json` containing:
  - Cut points and segment timings
  - B-Roll cue timestamps and contextual search queries
  - Motion graphics cue timestamps, text, and layout coordinates
  - Highlight reel short cut lists

---

## Phase 3: Visual Sourcing & Motion Graphics
**Scripts:** `tools/phase3_broll_sourcer.py`, `tools/scrapling_broll_provider.py`, `tools/generate_motion_graphics.py`

### Capabilities:
1. **Autonomous B-Roll Sourcing via Scrapling**:
   - Scrapes copyright-free 4K/1080p stock footage from Pexels without API keys.
   - Respects orientation filters (`portrait` for 9:16, `landscape` for 16:9).
   - Enforces unique clips per scene (`exclude_ids`).
   - Logs full provenance and licensing in `broll_sources.md`.
2. **Motion Graphics Card Suite**:
   - Generates high-contrast RGBA motion cards (Pillow) with rounded borders and drop shadows.
   - Locked to the upper safe zone (`y: 120–600`), never covering the speaker's face.

---

## Phase 4: Master Assembly & Mastering
**Scripts:** `tools/phase4_editor.py`, `tools/render_vertical_master.py`

### Capabilities:
- **Vertical Canvas (1080×1920)**: Builds dual-layer video with ambient blurred background (`gblur=sigma=28`) and centered foreground video (`scale=1080:608`).
- **B-Roll Cutaways**: Injects smooth Ken Burns pan/zoom camera moves with alpha transitions.
- **Graphic Overlays**: Overlays RGBA graphic cards via FFmpeg `overlay` filter with fade-in/fade-out expressions.
- **Kinetic Subtitles**: Burns high-contrast captions in the lower third margin (`y: 1740`).
- **Broadcast Audio**: Normalizes speech loudness to **-14 LUFS** standard.
- **Companion 16:9 Master**: Simultaneously renders a 1920×1080 widescreen companion video.
- **Highlight Shorts**: Extracts 15s–45s standalone shorts into `shorts/`.

---

## 📁 Dedicated Project Folder Standard

Every processed video resides in a self-contained directory:
`agentic-video-studio/renders/<project_name>/`

```
agentic-video-studio/renders/<project_name>/
├── full_episode_9x16_vertical.mp4      # Primary 9:16 master (1080×1920)
├── full_episode_16x9_horizontal.mp4    # 16:9 widescreen companion
├── shorts/                             # Highlight reels
│   ├── Highlight_1_9x16.mp4
│   └── Highlight_2_9x16.mp4
├── transcript.srt                      # Word-level timestamped captions
├── transcript.json                     # Full transcript payload
├── edit_plan.json                      # Director edit plan
├── review_score.json                   # Quality score
├── graphics/                           # Rendered motion cards
└── DELIVERY_REPORT.md                  # Comprehensive delivery report
```
