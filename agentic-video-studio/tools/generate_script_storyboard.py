#!/usr/bin/env python3
"""
Professional Director Script & Visual Storyboard Generator.
Synthesizes speech transcripts, semantic hooks, motion graphics, and B-roll cutaways
into a crisp, timecoded, broadcast-grade script with visual snippet cues.
Outputs:
- storyboard.json (structured API data)
- DIRECTOR_SCRIPT.md (human-readable screenplay format)
"""

import os
import sys
import json
import re
from pathlib import Path

STUDIO_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = STUDIO_ROOT.parent / "output"

def format_timecode(seconds: float) -> str:
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def clean_script_dialogue(text: str) -> str:
    """Make raw speech transcript crisp, professional, and readable."""
    cleaned = re.sub(r'\s+', ' ', text).strip()
    # Capitalize first letter
    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]
    # Ensure terminal punctuation
    if cleaned and cleaned[-1] not in ".!?":
        cleaned += "."
    return cleaned

def generate_storyboard(project_name: str) -> dict:
    print(f"[Storyboard] Generating professional script & visual storyboard for: {project_name}")

    trans_file = STUDIO_ROOT / "transcripts" / project_name / "transcript.json"
    plan_file = STUDIO_ROOT / "edit_plans" / f"{project_name}_edit_plan.json"
    analysis_file = STUDIO_ROOT / "analysis" / project_name / "content_analysis.json"
    gfx_dir = STUDIO_ROOT / "graphics" / project_name
    broll_dir = STUDIO_ROOT / "assets" / "broll" / project_name

    transcript = {}
    if trans_file.exists():
        with open(trans_file, encoding="utf-8") as f:
            transcript = json.load(f)

    edit_plan = {}
    if plan_file.exists():
        with open(plan_file, encoding="utf-8") as f:
            edit_plan = json.load(f)

    analysis = {}
    if analysis_file.exists():
        with open(analysis_file, encoding="utf-8") as f:
            analysis = json.load(f)

    duration = transcript.get("duration") or edit_plan.get("source_duration_sec") or 60.0
    segments = transcript.get("segments", [])
    
    # Motion Graphics & B-Rolls
    gfx_cards = sorted([p.name for p in gfx_dir.glob("*.png")]) if gfx_dir.exists() else []
    broll_clips = sorted([p.name for p in broll_dir.glob("*.mp4") if p.stat().st_size > 100000]) if broll_dir.exists() else []
    broll_cues = edit_plan.get("broll_plan", [])

    # Group segments into coherent 6-18 second scenes
    scenes = []
    curr_text = []
    curr_start = 0.0
    curr_end = 0.0
    target_scene_dur = 10.0

    if not segments:
        # Fallback if transcript empty
        segments = [{"start": 0.0, "end": duration, "text": project_name.replace("_", " ")}]

    for seg in segments:
        if not curr_text:
            curr_start = seg["start"]
        curr_text.append(seg.get("text", "").strip())
        curr_end = seg["end"]

        if (curr_end - curr_start) >= target_scene_dur or seg == segments[-1]:
            combined_text = " ".join(curr_text)
            dialogue = clean_script_dialogue(combined_text)
            scene_idx = len(scenes) + 1
            st_time = round(curr_start, 2)
            en_time = round(curr_end, 2)

            # Determine Visual Snippet
            visual = {
                "type": "host_camera",
                "label": "Host Camera (9:16 Centered)",
                "description": "Centered speaker framing with ambient blurred background (gblur=28)",
                "badge": "👤 Host Center",
                "thumbnail_url": None,
                "asset_file": None
            }

            # Check if Motion Graphic card triggers in this time window
            matched_card = None
            if gfx_cards:
                # Distribute cards across early/mid/outro scenes
                card_idx = int((st_time / duration) * len(gfx_cards))
                card_idx = min(card_idx, len(gfx_cards) - 1)
                # First scene gets intro title
                if scene_idx == 1:
                    matched_card = gfx_cards[0]
                elif scene_idx == len(segments):
                    matched_card = gfx_cards[-1]
                elif card_idx < len(gfx_cards) and (scene_idx % 2 == 1):
                    matched_card = gfx_cards[card_idx]

            # Check if B-Roll triggers
            matched_broll = None
            for bc in broll_cues:
                if abs(bc.get("at_time", -10) - st_time) < 4.0:
                    matched_broll = bc
                    break

            if matched_card:
                visual = {
                    "type": "motion_graphic",
                    "label": f"Motion Card: {matched_card}",
                    "description": "Bold high-contrast card in upper safe zone (never on face)",
                    "badge": "🎨 Motion Graphic",
                    "thumbnail_url": f"/graphics/{project_name}/{matched_card}",
                    "asset_file": matched_card
                }
            elif matched_broll and broll_clips:
                b_clip_name = broll_clips[min(scene_idx % len(broll_clips), len(broll_clips) - 1)]
                visual = {
                    "type": "broll_cutaway",
                    "label": f"4K B-Roll: {matched_broll.get('search_query', 'Cinematic Cutaway')}",
                    "description": f"Ken Burns pan & smooth alpha crossfade ({matched_broll.get('context', '')[:40]})",
                    "badge": "🎥 B-Roll Cutaway",
                    "thumbnail_url": None,
                    "asset_file": b_clip_name
                }
            elif scene_idx % 3 == 0 and broll_clips:
                b_clip_name = broll_clips[(scene_idx // 3) % len(broll_clips)]
                visual = {
                    "type": "broll_cutaway",
                    "label": "Cinematic B-Roll Cutaway",
                    "description": "Dynamic context-matched visual cutaway with smooth crossfade",
                    "badge": "🎥 B-Roll Cutaway",
                    "thumbnail_url": None,
                    "asset_file": b_clip_name
                }

            # Pacing / Delivery Tone
            if scene_idx == 1:
                pacing = "High-Energy Opening Hook"
            elif st_time > duration * 0.85:
                pacing = "Climactic Punchline & Call to Action"
            elif visual["type"] == "motion_graphic":
                pacing = "Pillar Concept Emphasis"
            else:
                pacing = "Steady Conversational Delivery"

            scenes.append({
                "scene_number": scene_idx,
                "timecode": f"{format_timecode(st_time)} – {format_timecode(en_time)}",
                "start_sec": st_time,
                "end_sec": en_time,
                "duration_sec": round(en_time - st_time, 2),
                "speaker": "Host" if scene_idx % 2 != 0 else "Guest / Speaker",
                "pacing": pacing,
                "dialogue": dialogue,
                "director_note": f"{pacing}. Subtitles locked to lower safe zone (MarginV=180).",
                "visual": visual
            })

            curr_text = []

    storyboard_data = {
        "project": project_name,
        "title": project_name.replace("_", " ").title(),
        "total_duration_sec": round(duration, 2),
        "total_scenes": len(scenes),
        "broll_count": len([s for s in scenes if s["visual"]["type"] == "broll_cutaway"]),
        "graphics_count": len([s for s in scenes if s["visual"]["type"] == "motion_graphic"]),
        "status": "ready_for_review",
        "scenes": scenes
    }

    # Save JSON
    dest_render = STUDIO_ROOT / "renders" / project_name
    dest_output = OUTPUT_DIR / project_name
    dest_render.mkdir(parents=True, exist_ok=True)
    dest_output.mkdir(parents=True, exist_ok=True)

    json_path_r = dest_render / "storyboard.json"
    json_path_o = dest_output / "storyboard.json"
    with open(json_path_r, "w", encoding="utf-8") as f:
        json.dump(storyboard_data, f, indent=2)
    with open(json_path_o, "w", encoding="utf-8") as f:
        json.dump(storyboard_data, f, indent=2)

    # Save Markdown Screenplay
    md_lines = [
        f"# Director Script & Visual Storyboard — {storyboard_data['title']}",
        f"**Project:** `{project_name}` | **Duration:** {duration:.1f}s | **Format:** 9:16 Vertical Master",
        "",
        "---",
        "",
        "| Scene | Timecode | Pacing | Spoken Dialogue | Visual Snippet & Notes |",
        "|---|---|---|---|---|"
    ]
    for s in scenes:
        vis = s["visual"]
        v_note = f"**{vis['badge']}**<br>_{vis['label']}_<br>{vis['description']}"
        dialogue_escaped = s['dialogue'].replace("|", "\\|")
        md_lines.append(f"| **Scene {s['scene_number']:02d}** | `{s['timecode']}` | {s['pacing']} | {dialogue_escaped} | {v_note} |")

    md_content = "\n".join(md_lines)
    with open(dest_render / "DIRECTOR_SCRIPT.md", "w", encoding="utf-8") as f:
        f.write(md_content)
    with open(dest_output / "DIRECTOR_SCRIPT.md", "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"[OK] Storyboard generated: {len(scenes)} scenes in {json_path_o}")
    return storyboard_data

def main():
    proj = sys.argv[1] if len(sys.argv) > 1 else "socialmedia_algo"
    generate_storyboard(proj)

if __name__ == "__main__":
    main()
