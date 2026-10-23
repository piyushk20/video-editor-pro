---
name: short-form-edit
description: "Turns talking-head footage into high-retention 9:16 vertical reels and shorts using Nate Herk's measured house style: 0.1s speech start, 1.2s shot cuts, split layout, punch-ins, open loops, and mouth occlusion guard."
---

# Short Form Edit (House Reel Style)

Engineered based on Nate Herk's measured analysis of top short-form reels.

## House Reel Specifications

### Pacing Numbers
- **Opening Speech Hook**: Starts within `<= 0.10s`. Trims any opening hesitation.
- **Ending Guard**: Master file ends immediately after final spoken word (no dead air tail).
- **Average Shot Duration**: `1.1s to 1.4s`, max `2.8s`.
- **First Visual Cut**: Lands at `0.6s to 1.0s` on the first charged noun or hook word.
- **Phrase-Level Trimming**: Dead air between phrases kept `< 0.20s`. Natural beats after commas and list items preserved at `0.2s to 0.4s`.

### Dynamic 9:16 Layouts
- **Split Layout (30% to 42%)**: B-roll / motion graphic in top safe zone (`y: 0 to 880`), speaker video framed in lower zone (`y: 880 to 1920`). First frame opens in split layout.
- **Full B-Roll (50% to 55%)**: 1080×1920 cinematic footage with subtle Ken Burns push-in.
- **Punch-In Zoom (5% to 15%)**: 1.20x scale crop on speaker for conviction statements, pivots, and the final CTA.
- **Speaker Presence**: Speaker visible ~45% of total runtime, and never absent for `> 3.5s`.

### Safe-Zone & Occlusion Guard
- **First 2.5s Check**: Strictly prohibits any title cards, banners, or subtitles from touching the speaker's mouth region (`y: 750 to 1150`).
- **Contrast Box**: Subtitles rendered with high-contrast translucent dark box (`rgba(0,0,0,0.75)`) ensuring 100% legibility on white websites or dark clips.

## CLI Usage

```bash
python agentic-video-studio/tools/house_reel_engine.py transcripts/<project>/transcript.json <duration>
python agentic-video-studio/tools/preflight_guard.py <project>
```
