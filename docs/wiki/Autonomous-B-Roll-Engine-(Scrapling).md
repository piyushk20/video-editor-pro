# Autonomous B-Roll Engine (Scrapling)

Video Editor Pro features an autonomous B-roll sourcing subsystem powered by Karim Shoair's [Scrapling](https://github.com/D4Vinci/Scrapling.git) framework. It eliminates the need for expensive stock media subscriptions or external API keys (`PEXELS_API_KEY`, `PIXABAY_API_KEY`) by scraping direct video stream endpoints directly.

---

## 🌟 How It Works

1. **Anti-Bot & Cloudflare Bypass**:
   - Uses Scrapling's high-speed `Fetcher` and headless `StealthyFetcher` (backed by `camoufox` and `patchright`) to fetch search result pages without triggering CAPTCHAs or Cloudflare blocks.
2. **Direct CDN Video Link Extraction**:
   - Parses video articles and download endpoints (`https://www.pexels.com/download/video/<id>/`).
   - Automatically follows redirects to extract direct high-bitrate MP4 CDN streams (`videos.pexels.com/video-files/<id>/...mp4`).
3. **Aspect Ratio Enforcement**:
   - Queries with `?orientation=portrait` to retrieve native 9:16 vertical videos (e.g., `1080x1920` or `2160x3840`), or `?orientation=landscape` for 16:9 widescreen.
4. **Visual Diversity & Deduplication (`exclude_ids`)**:
   - Tracks IDs of already-sourced clips within a project.
   - If two scenes request related keywords (e.g. `"ai cinematic 4k"`), the engine automatically skips previous IDs and selects fresh footage.
5. **Stream Downloading & Probe Validation**:
   - Streams chunks with download progress logging.
   - Probes files via `ffmpeg` to verify valid codecs, frame sizes, and duration.
   - Saves to `assets/broll/<project_name>/`.
6. **Licensing Provenance**:
   - Logs clip ID, query, direct URL, page URL, and license (100% Free for commercial use, no attribution required) to `assets/broll_sources.md`.

---

## 💻 CLI Usage

You can test and run the B-roll provider standalone:

```bash
# Sourcing 9:16 vertical B-roll for mobile shorts
python agentic-video-studio/tools/scrapling_broll_provider.py \
  --query "credit card debt" \
  --orientation portrait \
  --limit 2 \
  --dest "assets/broll/test_downloads"

# Sourcing 16:9 landscape B-roll
python agentic-video-studio/tools/scrapling_broll_provider.py \
  --query "money cash" \
  --orientation landscape \
  --limit 1
```

---

## 🐍 Programmatic API

```python
from tools.scrapling_broll_provider import search_and_download_broll
from pathlib import Path

# Sourcing unique vertical clips
clips = search_and_download_broll(
    query="rain storm window",
    dest_dir=Path("assets/broll/my_project"),
    orientation="portrait",
    limit=1,
    prefix="slot01",
    exclude_ids={"7230794"}  # optional exclusions
)

for clip in clips:
    print(f"Downloaded: {clip.local_path}")
    print(f"Resolution: {clip.resolution}")
    print(f"Duration: {clip.duration}s")
    print(f"License: {clip.license}")
```

---

## 📋 License Compliance Table

| Source | License | Attribution Required? | Commercial Use? |
| :--- | :--- | :--- | :--- |
| **Pexels** | Pexels License | ❌ No | ✅ Yes |
| **Coverr** | Coverr Free License | ❌ No | ✅ Yes |
| **Pixabay** | Pixabay License | ❌ No | ✅ Yes |
