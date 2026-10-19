#!/usr/bin/env python3
"""
PHASE 2 — Creative Planning (Director)
Reads Phase 1 analysis and produces a structured EditPlan JSON.
Determines: target length, cuts, color grade style, caption style,
motion graphics plan, B-roll plan, chapters, highlight clips.
"""
import json, sys, argparse
from pathlib import Path
from datetime import datetime

STUDIO_ROOT = Path(__file__).parent.parent

def load_analysis(project_name: str) -> dict:
    f = STUDIO_ROOT / "analysis" / project_name / "content_analysis.json"
    if not f.exists():
        print(f"[ERROR] No analysis found for '{project_name}'. Run Phase 1 first.")
        sys.exit(1)
    with open(f) as fp:
        return json.load(fp)

def load_transcript(project_name: str) -> dict:
    f = STUDIO_ROOT / "transcripts" / project_name / "transcript.json"
    if not f.exists():
        return {}
    with open(f) as fp:
        return json.load(fp)

def build_edit_plan(analysis: dict, transcript: dict, creative_brief: str, project_name: str) -> dict:
    duration = analysis.get("duration", 0)
    segments = transcript.get("segments", [])
    fillers = analysis.get("filler_instances", [])
    pauses = analysis.get("long_pauses", [])
    chapters = analysis.get("chapter_points", [])
    highlights = analysis.get("highlight_moments", [])
    broll_ops = analysis.get("broll_opportunities", [])

    # ── Cut list: remove filler words + long pauses ──────────────────────
    cuts_to_remove = []
    for fi in fillers:
        cuts_to_remove.append({
            "type": "filler_removal",
            "start": fi["start"],
            "end": fi["end"],
            "reason": f"Filler word: '{fi['word']}'"
        })
    for p in pauses:
        if p["duration"] > 2.0:
            cuts_to_remove.append({
                "type": "pause_trim",
                "start": p["start"] + 0.3,
                "end": p["end"] - 0.3,
                "reason": f"Dead air {p['duration']}s"
            })

    # ── Highlight clips for Shorts/Reels ──────────────────────────────────
    short_clips = []
    for h in highlights[:5]:
        clip_start = max(0, h["start"] - 1.0)
        clip_end   = min(duration, h["end"] + 1.0)
        short_clips.append({
            "label": f"Highlight_{len(short_clips)+1}",
            "start": clip_start,
            "end": clip_end,
            "duration": round(clip_end - clip_start, 1),
            "hook_text": h["text"][:60]
        })

    # ── Chapter markers ───────────────────────────────────────────────────
    chapter_markers = []
    for i, cp in enumerate(chapters):
        mins = int(cp["start"] // 60); secs = int(cp["start"] % 60)
        chapter_markers.append({
            "index": i,
            "timecode": f"{mins:02d}:{secs:02d}",
            "start_sec": cp["start"],
            "title": f"Chapter {i+1}",
            "preview_text": cp["text"]
        })

    # ── B-Roll plan ───────────────────────────────────────────────────────
    broll_plan = []
    for b in broll_ops[:10]:
        broll_plan.append({
            "at_time": b["start"],
            "duration": min(b["end"] - b["start"], 6.0),
            "search_query": " ".join(b["keywords"][:3]) + " cinematic 4K",
            "context": b["text"][:60],
            "source_priority": ["pexels", "pixabay", "mixkit"]
        })

    # ── Motion graphics plan ───────────────────────────────────────────────
    motion_graphics = [
        {"type": "intro_title", "at_time": 0, "duration": 3.0,
         "content": {"title": project_name.replace("_", " ").title(), "subtitle": creative_brief[:60]}},
        {"type": "lower_third", "at_time": 3.0, "duration": 4.0,
         "content": {"name": "Host", "role": "Speaker"}},
        {"type": "kinetic_captions", "style": "bold_centered", "throughout": True,
         "font": "Inter", "color_scheme": "white_with_shadow"},
        {"type": "chapter_cards", "trigger": "chapter_markers",
         "style": "slide_in_from_right"},
        {"type": "outro", "at_time": max(0, duration - 5), "duration": 5.0,
         "content": {"cta": "Subscribe for more!", "socials": "@channel"}},
    ]

    # ── Final output formats ───────────────────────────────────────────────
    target_duration_min = max(duration * 0.75, duration - (len(fillers) * 0.3) - sum(p["duration"] for p in pauses))
    edit_plan = {
        "project": project_name,
        "creative_brief": creative_brief,
        "created_at": datetime.now().isoformat(),
        "source_duration_sec": round(duration, 1),
        "target_duration_sec": round(target_duration_min, 1),
        "time_saved_sec": round(duration - target_duration_min, 1),
        "output_formats": [
            {"format": "master_vertical_9x16", "resolution": "1080x1920", "fps": 30, "codec": "h264", "audio": "aac_stereo_192k", "is_default": True},
            {"format": "vertical_short", "resolution": "1080x1920", "fps": 30, "codec": "h264", "duration_limit": 60},
            {"format": "horizontal_widescreen_16x9", "resolution": "1920x1080", "fps": 30, "codec": "h264", "audio": "aac_stereo_192k"},
        ],
        "color_grade": {
            "style": "cinematic_warm",
            "lut": None,
            "brightness": "+5%",
            "contrast": "+10%",
            "saturation": "+8%",
            "color_temp": "slightly_warm"
        },
        "audio": {
            "loudness_target_lufs": -14,
            "noise_reduction": True,
            "de_esser": True,
            "fade_ms": 30
        },
        "cuts_to_remove": cuts_to_remove,
        "chapter_markers": chapter_markers,
        "short_highlight_clips": short_clips,
        "motion_graphics": motion_graphics,
        "broll_plan": broll_plan,
        "review_criteria": {
            "pacing_score_target": 8,
            "clarity_score_target": 9,
            "engagement_score_target": 8,
            "watchability_score_target": 8
        }
    }

    # Save
    out_dir = STUDIO_ROOT / "edit_plans"
    out_dir.mkdir(parents=True, exist_ok=True)
    plan_file = out_dir / f"{project_name}_edit_plan.json"
    with open(plan_file, "w") as f:
        json.dump(edit_plan, f, indent=2)
    print(f"[OK] EditPlan saved: {plan_file}")

    # Human summary
    print(f"\n[PLAN] EditPlan Summary")
    print(f"   Source duration  : {duration:.0f}s")
    print(f"   Target duration  : {target_duration_min:.0f}s")
    print(f"   Cuts to remove   : {len(cuts_to_remove)} (fillers + pauses)")
    print(f"   Chapters         : {len(chapter_markers)}")
    print(f"   Highlight clips  : {len(short_clips)}")
    print(f"   B-Roll slots     : {len(broll_plan)}")
    print(f"   Motion graphics  : {len(motion_graphics)} elements")

    return edit_plan

def main():
    parser = argparse.ArgumentParser(description="Agentic Video Studio — Phase 2: Creative Planning")
    parser.add_argument("project", help="Project name")
    parser.add_argument("--brief", "-b", default="Create an engaging, polished video optimised for social media.",
                        help="Creative brief (tone, style, goals)")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  Agentic Video Studio — Phase 2: Creative Planning")
    print(f"  Project : {args.project}")
    print(f"{'='*60}\n")

    analysis = load_analysis(args.project)
    transcript = load_transcript(args.project)
    edit_plan = build_edit_plan(analysis, transcript, args.brief, args.project)

    print(f"\n[OK] Phase 2 complete. EditPlan ready for Phase 3 enrichment.\n")

if __name__ == "__main__":
    main()
