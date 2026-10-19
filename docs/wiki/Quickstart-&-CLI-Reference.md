# Quickstart & CLI Reference

Get up and running with Video Editor Pro in minutes.

---

## 🛠️ Prerequisites

- **Python**: 3.10 or higher
- **FFmpeg**: System FFmpeg or Python `imageio-ffmpeg` package
- **System OS**: Windows, macOS, or Linux

Install Python dependencies:
```bash
pip install scrapling[all] faster-whisper pillow imageio imageio-ffmpeg requests
scrapling install
```

---

## 🚀 Running the Full Autonomous Pipeline

Run end-to-end processing on any local video or podcast:

```bash
python agentic-video-studio/run_pipeline.py \
  --input "C:/path/to/my_video.mp4" \
  --project-name "my_project"
```

The pipeline will:
1. Probe input and generate `manifest.json`.
2. Extract audio and transcribe word-level timestamps (`transcript.srt`).
3. Generate a director edit plan (`edit_plan.json`).
4. Autonomously scrape copyright-free B-roll clips via Scrapling.
5. Generate safe-zone motion graphics cards.
6. Assemble the 9:16 vertical master, 16:9 companion, and highlight shorts in `agentic-video-studio/renders/my_project/`.

---

## ⚙️ Running Individual Phases

### 1. Ingestion (Phase 0)
```bash
python agentic-video-studio/tools/phase0_input_handler.py --input "path/to/media.mp4" --project-name "my_project"
```

### 2. Transcription & Analysis (Phase 1)
```bash
python agentic-video-studio/tools/phase1_analyser.py my_project
```

### 3. Director Planning (Phase 2)
```bash
python agentic-video-studio/tools/phase2_director.py my_project
```

### 4. B-Roll Sourcing via Scrapling (Phase 3)
```bash
python agentic-video-studio/tools/phase3_broll_sourcer.py my_project
```

### 5. Final Compositing & Assembly (Phase 4)
```bash
python agentic-video-studio/tools/phase4_editor.py my_project
```

---

## 🔍 Standalone B-Roll Scraper CLI

```bash
# Query vertical clips
python agentic-video-studio/tools/scrapling_broll_provider.py \
  --query "financial freedom" \
  --orientation portrait \
  --limit 3 \
  --dest "assets/broll/my_project"
```
