---
name: cut-mistakes
description: "Finds and removes spoken mistakes — stutters, repeated words, false starts, and retakes (re-recorded lines) — from talking-head recordings. Use after silence trimming to clean up flubs, remove repetitions, and keep the best take. Generates candidate EDL and retimes transcripts for frame-perfect sync."
---

# Cut Mistakes & Repeats

Autonomous mistake cutter based on word-level transcripts.
Ported from Nate Herk's herk-edit-kit.

## Capabilities

1. **Stutters & Immediate Repeats**:
   - Detects repeated identical tokens with < 0.55s gap ("the the", "I- I-").
   - Drops the botched first attempt and keeps the clean follow-up.

2. **Retakes (Re-recorded Lines)**:
   - Partitions speech into breath segments.
   - Computes Jaccard vocabulary similarity across adjacent segments.
   - When similarity >= 0.32 or identical opening phrase is detected, identifies an abandoned take.
   - Drops the botched take and preserves the final clean take.

3. **False Starts**:
   - Short segments (< 6s) with identical opening to the restart within 12s.

4. **Transcript Retiming**:
   - Shifts all subsequent word timestamps so downstream captions and visual triggers remain 100% in sync.

5. **Visual EDL Review Dashboard**:
   - Generates interactive timeline scrubber (`edl_review.html`) with green (kept) vs red (cut) segments and audio preview.

## CLI Usage

```bash
# Scan candidates
python agentic-video-studio/tools/cut_mistakes.py transcripts/<project>/transcript.json

# Auto-apply approved cuts and retime transcript
python agentic-video-studio/tools/cut_mistakes.py transcripts/<project>/transcript.json --auto-apply --video inputs/<project>/input.mp4

# Build interactive EDL review page
python agentic-video-studio/tools/build_edl_review.py transcripts/<project>/transcript_mistakes_edl.json
```
