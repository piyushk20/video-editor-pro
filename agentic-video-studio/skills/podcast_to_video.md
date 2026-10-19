# 🎯 Skill: podcast_to_video
# Reusable pipeline for turning a podcast (audio or video) into a
# fully edited, published-ready video with chapters, highlights, B-roll, and Shorts.

## When to use
- Input is an audio podcast (.mp3, .m4a, .wav, .opus)
- Input is a video podcast (talking heads, interview, panel)
- Goal is a polished full episode + short social clips

## Command
```bash
cd agentic-video-studio
python run_pipeline.py "<podcast_file_or_url>" \
  --project my_podcast_ep1 \
  --brief "Energetic podcast interview on [TOPIC]. Clean, modern, professional. Chapters + Shorts." \
  --model small
```

## Phase-by-phase notes

### Phase 0 — Input
- Accepts: .mp3 / .m4a / .wav / .opus / video URL / local video file
- yt-dlp handles YouTube, Spotify web, SoundCloud URLs automatically

### Phase 1 — Transcription
- Use `--model small` for best accuracy/speed balance
- For multi-speaker podcasts: review `transcripts/<project>/transcript.json`
  and manually add `speaker` labels to segments if needed.
- Filler words detected: um, uh, like, you know, basically, literally, right

### Phase 2 — Edit Plan
- Review `edit_plans/<project>_edit_plan.json` before Phase 4
- Adjust `chapter_markers[].title` manually for better chapter titles

### Phase 3 — B-Roll
- Set PEXELS_API_KEY in .env for automated downloads
- Manual fallback: download from pexels.com and place in assets/broll/<project>/

### Phase 4 — Assembly
- Full episode: renders/<project>/full_episode.mp4
- Short clips: renders/<project>/shorts/ (horizontal + vertical)

## Tips
- For long podcasts (>1 hr): use `--model medium` for better accuracy
- For interview/panel: add speaker names in the brief for lower-thirds
- Run `--phase 2` to re-plan without re-transcribing

## Output Checklist
- [ ] full_episode.mp4 (cleaned, graded, subtitled)
- [ ] shorts/*_vertical.mp4 (9:16 for TikTok/Reels/Shorts)
- [ ] shorts/*_horizontal.mp4 (16:9)
- [ ] assets/broll_sources.md (license log)
- [ ] reviews/<project>_review.json (quality scores)
