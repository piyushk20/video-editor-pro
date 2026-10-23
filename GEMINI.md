# Video Editor Pro — AI Agent Rules & Standards

## 📱 Mandatory Default Output Format: 9:16 Vertical

**CRITICAL USER RULE:**
Unless the user explicitly specifies a different aspect ratio (e.g. "make it 16:9" or "widescreen"), **ALL final video outputs, master episodes, and clips MUST default to 9:16 vertical format (1080×1920)**.

### Layout & Composition Rules for 9:16:
1. **Vertical Canvas (1080×1920):**
   - For widescreen source footage: Use professional blurred ambient background (`gblur=sigma=28`) with sharp centered foreground video, or smart crop/reframe.
2. **Motion Graphics Safe Zone:**
   - Motion graphics must be **large, bold, and high contrast** (solid opaque backgrounds with colored borders).
   - Graphics **must NEVER cover or obstruct the speaker's face**. Always anchor cards on the left safe zone (`x: 60px – 880px`) or open areas.
3. **Kinetic Captions:**
   - Synced word-level subtitles burned with high-contrast outlines and drop shadows (e.g., Segoe UI Bold / Inter).
4. **Cinematic B-Roll:**
   - Dynamic cutaways with smooth Ken Burns zoom/pan camera moves and alpha crossfades.
5. **Broadcast Audio:**
   - Audio normalized to **-14 LUFS** with studio noise reduction.

## 📁 Dedicated Project Folder Standard (MANDATORY)

**CRITICAL USER RULE:**
For ANY given video processed, create a dedicated self-contained project directory:
`agentic-video-studio/renders/<project_name>/`

**ALL outputs for that video MUST reside in that single directory:**
- `full_episode_9x16_vertical.mp4` (Primary 9:16 vertical master)
- `full_episode_16x9_horizontal.mp4` (16:9 widescreen companion)
- `shorts/` (All 9:16 and 16:9 highlight reels)
- `subtitles.srt` (Timestamped captions)
- `transcript.txt` / `transcript.json` (Full transcripts)
- `edit_plan.json` (Director plan)
- `review_score.json` (Quality audit)
- `graphics/` (Motion graphic assets used)
- `DELIVERY_REPORT.md` (Project summary & timestamps)

The user should be able to open that **one folder** in File Explorer and have 100% of the project's deliverables.

## 🚀 Stable State Configuration

- **App Name**: Video Editor Pro
- **Workspace Path**: `c:\Users\HP\video-editorpro`
- **Port**: 8090 (unified FastAPI backend & modern web UI)
- **Launch Command**: `python studio_server.py` from `c:\Users\HP\video-editorpro\agentic-video-studio`
- **Health Check Endpoint**: `http://127.0.0.1:8090/health` (HTTP 200 `{"status": "ok", "app": "Video Editor Pro"}`)
- **Frontend URL**: `http://localhost:8090/`

