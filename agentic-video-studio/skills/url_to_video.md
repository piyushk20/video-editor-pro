# 🎯 Skill: url_to_video
# Download any YouTube/web video and run the full production pipeline.

## When to use
- Input is a YouTube URL, Vimeo, Twitter video, or any yt-dlp-supported URL
- Goal is a polished, edited re-export with B-roll, captions, highlights

## Command
```bash
cd agentic-video-studio
python run_pipeline.py "https://www.youtube.com/watch?v=XXXX" \
  --project my_youtube_project \
  --brief "Reformat this tutorial into clean, punchy vertical Shorts with subtitles." \
  --model base
```

## Notes
- yt-dlp downloads best quality automatically (4K if available)
- Use `--model tiny` for quick test runs, `--model small` for production
- Review edit_plan before Phase 4 to approve cuts

## Output
- renders/<project>/full_episode.mp4
- renders/<project>/shorts/
