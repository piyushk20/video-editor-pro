# Video Editor Pro Wiki 🎬🤖

Welcome to the **Video Editor Pro** documentation wiki. 

Video Editor Pro is an autonomous, agentic video and podcast production studio built inside Google Antigravity. It transforms raw input footage, audio podcasts, web URLs, or infographics into broadcast-ready, highly engaging videos formatted for mobile-first social media and widescreen distribution.

---

## 📚 Wiki Directory

| Guide | Description |
| :--- | :--- |
| **[Architecture & Pipeline](Architecture-&-Phases)** | Complete walkthrough of Phases 0 through 4 and the dedicated project folder standard. |
| **[Autonomous B-Roll Engine (Scrapling)](Autonomous-B-Roll-Engine-(Scrapling))** | Zero-API copyright-free B-roll scraping using Scrapling (`D4Vinci/Scrapling`), anti-bot bypass, and aspect ratio filtering. |
| **[Motion Graphics & Safe Zones](Motion-Graphics-&-Safe-Zones)** | 9:16 vertical composition, speaker face obstruction prevention, and typography standards. |
| **[Quickstart & CLI Reference](Quickstart-&-CLI-Reference)** | Installation, command-line arguments, phase execution, and troubleshooting. |

---

## 🌟 Core System Tenets

1. **📱 9:16 Vertical Master First (1080×1920)**  
   Engineered for modern mobile consumption (TikTok, Instagram Reels, YouTube Shorts). Source footage is automatically styled with an ambient blurred background (`gblur=sigma=28`) and sharp center framing, accompanied by a 16:9 widescreen companion.

2. **🤖 Zero-API Autonomous B-Roll (Powered by Scrapling)**  
   Utilizes Karim Shoair's [Scrapling](https://github.com/D4Vinci/Scrapling.git) framework with stealth anti-bot bypass to source commercial-free, high-definition stock footage (Pexels, Coverr) without requiring API keys or subscriptions.

3. **🛡️ Face Obstruction Prevention**  
   Motion graphics (title cards, lower thirds, key lists, quote callouts) are locked strictly to the upper safe zone (`y: 120–600`), and kinetic captions sit in the lower third margin (`y: 1740`), ensuring the speaker's face is never covered.

4. **📁 Dedicated Project Folder Standard**  
   Every processed video generates a self-contained project directory in `agentic-video-studio/renders/<project_name>/` containing 100% of the project's deliverables (masters, companion, shorts, SRT, transcripts, edit plan, graphics assets, and delivery report).

5. **🔊 Broadcast-Grade Audio**  
   Mastered to **-14 LUFS** standard with studio noise gating and speech clarity enhancement.

---

## 🏗️ Pipeline Overview

```
[Input: Video / Podcast / URL / Infographic]
                    │
                    ▼
        Phase 0: Input Handler
   (Metadata probe, normalise aspect ratio)
                    │
                    ▼
     Phase 1: Transcription & Analysis
       (Faster-Whisper word-level SRT)
                    │
                    ▼
         Phase 2: Creative Director
      (Edit plan, b-roll cues, pacing)
                    │
                    ▼
         Phase 3: Visual Sourcing
   (Scrapling Zero-API B-roll + Motion Cards)
                    │
                    ▼
         Phase 4: Master Assembly
     (Multi-layer FFmpeg + -14 LUFS Audio)
                    │
                    ▼
   [Dedicated Deliverables Folder]
   ├── full_episode_9x16_vertical.mp4
   ├── full_episode_16x9_horizontal.mp4
   ├── shorts/
   ├── transcript.srt
   └── DELIVERY_REPORT.md
```
