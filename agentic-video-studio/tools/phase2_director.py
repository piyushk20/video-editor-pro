#!/usr/bin/env python3
"""
PHASE 2 — Creative Planning (Director) with Semantic Script Alignment.
Reads Phase 1 analysis and produces a structured EditPlan JSON.
Synchronizes Motion Graphics and B-Roll cutaways directly to the spoken
words in the script, preventing visual collisions and ensuring 100% alignment.
"""
import json, sys, argparse, re
from pathlib import Path
from datetime import datetime

STUDIO_ROOT = Path(__file__).parent.parent

VISUAL_KEYWORDS = {
    # Automotive / Transportation
    "pickup truck": "pickup truck driving highway cinematic 4K",
    "truck": "pickup truck driving road cinematic 4K",
    "car": "modern luxury car driving cinematic 4K",
    "pickup": "pickup truck driving road cinematic 4K",
    "private jet": "private jet airplane luxury tarmac cinematic 4K",
    "jet": "private jet airplane flying runway cinematic 4K",
    "private island": "tropical private island luxury aerial cinematic 4K",
    "island": "tropical island ocean luxury aerial cinematic 4K",
    "airplane": "airplane jet flying sky clouds cinematic 4K",
    "boat": "luxury speedboat lake ocean cinematic 4K",
    "yacht": "luxury yacht sailing ocean cinematic 4K",
    # Money / Finance
    "money": "counting cash dollar bills wealth cinematic 4K",
    "dollar": "dollar bills cash currency close up cinematic 4K",
    "cash": "counting cash money bills financial cinematic 4K",
    "wealth": "luxury lifestyle wealth success cinematic 4K",
    "rich": "luxury mansion wealth success aesthetic cinematic 4K",
    "debt": "stressful bills credit card financial debt cinematic 4K",
    "credit card": "credit card payment shopping financial cinematic 4K",
    "bills": "stack of financial bills calculator cinematic 4K",
    "investing": "stock market chart financial growth investment cinematic 4K",
    "stocks": "financial market stock exchange tickers screens cinematic 4K",
    "chart": "business analytics financial growth chart graphs cinematic 4K",
    "bank": "modern commercial bank architecture financial cinematic 4K",
    # Tech / Social Media
    "instagram": "smartphone scrolling instagram social media feed cinematic 4K",
    "tiktok": "person browsing tiktok smartphone videos cinematic 4K",
    "algorithm": "digital data flow algorithm artificial intelligence cyberspace cinematic 4K",
    "phone": "person looking at smartphone screen glowing cinematic 4K",
    "smartphone": "using smartphone touching glass screen cinematic 4K",
    "social media": "smartphone app notifications scrolling feed cinematic 4K",
    "scroll": "finger scrolling smartphone social media feed cinematic 4K",
    "laptop": "typing on laptop computer keyboard desk office cinematic 4K",
    "computer": "person working computer monitors office cinematic 4K",
    # People / Lifestyle
    "kids": "children playing outdoors smiling family cinematic 4K",
    "son": "young boy smiling outdoors lifestyle cinematic 4K",
    "family": "happy family together home living room cinematic 4K",
    "house": "beautiful modern suburban home exterior architecture cinematic 4K",
    "neighbor": "suburban neighborhood street homes daylight cinematic 4K",
    "coworker": "modern corporate office colleagues talking cinematic 4K",
    "coworkers": "modern corporate office colleagues talking cinematic 4K",
    "office": "modern minimalist creative office workspace cinematic 4K",
    "work": "focused professional working busy desk coffee cinematic 4K",
    "stress": "person holding head stressed overwhelmed workspace cinematic 4K",
    "falling behind": "person looking thoughtful window contemplating future cinematic 4K",
    "clock": "ticking analog clock timelapse passage of time cinematic 4K",
    "time": "hourglass sand flowing time concept cinematic 4K",
}

def load_analysis(project_name: str) -> dict:
    f = STUDIO_ROOT / "analysis" / project_name / "content_analysis.json"
    if not f.exists():
        print(f"[ERROR] No analysis found for '{project_name}'. Run Phase 1 first.")
        sys.exit(1)
    with open(f, encoding="utf-8") as fp:
        return json.load(fp)

def load_transcript(project_name: str) -> dict:
    f = STUDIO_ROOT / "transcripts" / project_name / "transcript.json"
    if not f.exists():
        return {}
    with open(f, encoding="utf-8") as fp:
        return json.load(fp)

def plan_script_aligned_visuals(transcript: dict, duration: float, project_name: str, creative_brief: str) -> tuple[list, list]:
    segments = transcript.get("segments", [])
    if not segments:
        # Fallback if transcript empty
        motion_graphics = [
            {"type": "intro_title", "card_file": "01_intro_title.png", "at_time": 0.5, "duration": 4.0, "title": project_name.replace("_", " ").title(), "subtitle": creative_brief[:60]},
            {"type": "lower_third", "card_file": "02_lower_third.png", "at_time": 6.0, "duration": 4.0, "name": "Host", "role": "Topic Expert"},
            {"type": "outro", "card_file": "05_outro_card.png", "at_time": max(0, duration - 5.0), "duration": 5.0, "cta": "Subscribe for more insights"}
        ]
        return motion_graphics, []

    # 1. Anchor Motion Graphics
    motion_graphics = []
    
    # Card 1: Intro Hook & Title
    intro_seg = segments[0]
    motion_graphics.append({
        "type": "intro_title",
        "card_file": "01_intro_title.png",
        "at_time": 0.5,
        "duration": 4.2,
        "title": project_name.replace("_", " ").title(),
        "subtitle": creative_brief[:60],
        "spoken_context": intro_seg.get("text", "")[:80]
    })

    # Card 2: Lower Third / Host & Topic Setup (around 6s–12s)
    lt_time = 7.0
    lt_seg = None
    for seg in segments:
        if 5.0 <= seg["start"] <= 14.0:
            lt_seg = seg
            lt_time = round(seg["start"], 2)
            break
    motion_graphics.append({
        "type": "lower_third",
        "card_file": "02_lower_third.png",
        "at_time": lt_time,
        "duration": 4.0,
        "name": "Featured Speaker",
        "role": "Masterclass Insights",
        "spoken_context": lt_seg.get("text", "")[:80] if lt_seg else ""
    })

    # Card 3: Concept Pillars Card (between 25% and 55% of video)
    pillar_cand = None
    mid_start = duration * 0.25
    mid_end = duration * 0.55
    best_pillar_score = -1

    for seg in segments:
        if mid_start <= seg["start"] <= mid_end:
            text_l = seg.get("text", "").lower()
            score = sum(1 for kw in ["idea", "topic", "important", "principle", "rule", "step", "definition", "expectations", "because", "different", "always", "normal", "behavior"] if kw in text_l)
            if score > best_pillar_score:
                best_pillar_score = score
                pillar_cand = seg

    pillar_time = round(pillar_cand["start"], 2) if pillar_cand else round(duration * 0.35, 2)
    pillar_text = pillar_cand.get("text", "") if pillar_cand else ""
    motion_graphics.append({
        "type": "pillars_card",
        "card_file": "03_pillars_card.png",
        "at_time": pillar_time,
        "duration": 4.8,
        "title": "CORE TAKEAWAYS",
        "spoken_context": pillar_text[:90]
    })

    # Card 4: Insight / Breakthrough Quote (between 55% and 85% of video)
    insight_cand = None
    ins_start = duration * 0.55
    ins_end = duration * 0.85
    best_ins_score = -1

    for seg in segments:
        if ins_start <= seg["start"] <= ins_end:
            text_l = seg.get("text", "").lower()
            score = sum(1 for kw in ["looking inside", "matters", "yardstick", "hardest", "takeaways", "skill set", "secret", "definition", "realize", "truth", "money", "freedom"] if kw in text_l)
            if score > best_ins_score:
                best_ins_score = score
                insight_cand = seg

    insight_time = round(insight_cand["start"], 2) if insight_cand else round(duration * 0.70, 2)
    raw_quote = insight_cand.get("text", "") if insight_cand else "Focus on internal growth rather than constant comparison."
    # Clean quote for card
    clean_q = re.sub(r'^(of|and|but|so|because)\s+', '', raw_quote.strip(), flags=re.I)
    if clean_q:
        clean_q = clean_q[0].upper() + clean_q[1:]
    motion_graphics.append({
        "type": "insight_card",
        "card_file": "04_insight_card.png",
        "at_time": insight_time,
        "duration": 5.0,
        "title": "KEY SHIFT & INSIGHT",
        "quote": clean_q[:85],
        "spoken_context": raw_quote[:90]
    })

    # Card 5: Outro / Call to Action (last 10–12s)
    outro_time = round(max(0, duration - 6.0), 2)
    motion_graphics.append({
        "type": "outro",
        "card_file": "05_outro_card.png",
        "at_time": outro_time,
        "duration": 5.0,
        "title": "TAKE ACTION TODAY",
        "cta": "Subscribe for daily deep-dive insights.",
        "spoken_context": segments[-1].get("text", "")[:80] if segments else ""
    })

    # 2. Build Collision Intervals for Motion Graphics (enforce 0.6s buffer)
    card_windows = [(c["at_time"] - 0.6, c["at_time"] + c["duration"] + 0.6) for c in motion_graphics]

    def collides_with_cards(st: float, dur: float) -> bool:
        en = st + dur
        for c_st, c_en in card_windows:
            if not (en < c_st or st > c_en):
                return True
        return False

    # 3. Detect Concrete Visual B-Roll Moments from Transcript Words
    candidate_cues = []
    seen_keywords = set()

    # Search word-by-word for exact timestamp sync
    for seg in segments:
        words = seg.get("words", [])
        seg_text = seg.get("text", "")
        for w in words:
            w_text = re.sub(r'[^\w]', '', w.get("word", "").lower())
            # Check 2-word combinations
            w_start = w.get("start", seg["start"])
            for kw, query in VISUAL_KEYWORDS.items():
                if kw in seg_text.lower():
                    # Check if this word is the start of the keyword
                    kw_first = kw.split()[0]
                    if w_text == kw_first:
                        if kw not in seen_keywords:
                            seen_keywords.add(kw)
                            candidate_cues.append({
                                "at_time": round(w_start, 2),
                                "keyword": kw,
                                "search_query": query,
                                "spoken_context": seg_text.strip(),
                                "duration": 4.0
                            })
                            break

    # If word-level didn't catch enough, fall back to segment-level search
    if len(candidate_cues) < 4:
        for seg in segments:
            seg_l = seg.get("text", "").lower()
            for kw, query in VISUAL_KEYWORDS.items():
                if kw in seg_l and kw not in seen_keywords:
                    seen_keywords.add(kw)
                    candidate_cues.append({
                        "at_time": round(seg.get("start", 0), 2),
                        "keyword": kw,
                        "search_query": query,
                        "spoken_context": seg.get("text", "").strip(),
                        "duration": 4.0
                    })
                    if len(candidate_cues) >= 6:
                        break

    # Filter candidates for collision with motion cards and minimum spacing between B-rolls
    candidate_cues.sort(key=lambda x: x["at_time"])
    broll_plan = []
    last_broll_end = -10.0

    for cue in candidate_cues:
        st = cue["at_time"]
        dur = cue["duration"]
        # Must not collide with motion cards
        if collides_with_cards(st, dur):
            # Try shifting 0.8s after the colliding card if room permits
            for c_st, c_en in card_windows:
                if c_st <= st <= c_en:
                    st = round(c_en + 0.5, 2)
                    break
        if st + dur > duration - 6.0:
            continue
        if collides_with_cards(st, dur):
            continue
        # Enforce at least 5s gap between b-rolls
        if st >= last_broll_end + 4.0:
            cue["at_time"] = st
            broll_plan.append(cue)
            last_broll_end = st + dur
            if len(broll_plan) >= 5:
                break

    # Ensure at least 3-4 B-rolls if duration permits
    if len(broll_plan) < 3 and duration > 30:
        step = duration / 4.0
        for i in range(1, 4):
            tentative_t = round(step * i, 2)
            if not collides_with_cards(tentative_t, 3.8) and tentative_t < duration - 7.0:
                # Find closest segment
                closest = min(segments, key=lambda s: abs(s["start"] - tentative_t))
                broll_plan.append({
                    "at_time": tentative_t,
                    "keyword": "cinematic storytelling",
                    "search_query": f"{project_name.replace('_', ' ')} cinematic 4K",
                    "spoken_context": closest.get("text", ""),
                    "duration": 3.8
                })

    broll_plan.sort(key=lambda x: x["at_time"])
    for idx, b in enumerate(broll_plan):
        b["slot"] = f"slot{idx+1:02d}"

    return motion_graphics, broll_plan

def build_edit_plan(analysis: dict, transcript: dict, creative_brief: str, project_name: str) -> dict:
    duration = analysis.get("duration", 0)
    segments = transcript.get("segments", [])
    fillers = analysis.get("filler_instances", [])
    pauses = analysis.get("long_pauses", [])
    chapters = analysis.get("chapter_points", [])
    highlights = analysis.get("highlight_moments", [])

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
        if (clip_end - clip_start) >= 5.0:
            short_clips.append({
                "label": f"Highlight_{len(short_clips)+1}",
                "start": clip_start,
                "end": clip_end,
                "duration": round(clip_end - clip_start, 1),
                "hook_text": h["text"][:60]
            })

    if not short_clips and duration > 10:
        c1_end = min(duration, 35.0)
        short_clips.append({
            "label": "Highlight_1_Hook",
            "start": 0.0,
            "end": c1_end,
            "duration": round(c1_end, 1),
            "hook_text": "Top takeaway & opening hook"
        })
        if duration > 50:
            mid_st = round(duration * 0.4, 1)
            mid_en = min(duration, mid_st + 30.0)
            short_clips.append({
                "label": "Highlight_2_Core_Insight",
                "start": mid_st,
                "end": mid_en,
                "duration": round(mid_en - mid_st, 1),
                "hook_text": "Core concept & punchline"
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

    # ── Semantic Script-Aligned Motion Graphics & B-Roll ───────────────────
    motion_graphics, broll_plan = plan_script_aligned_visuals(transcript, duration, project_name, creative_brief)

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
            "pacing_score_target": 9,
            "clarity_score_target": 9,
            "engagement_score_target": 9,
            "watchability_score_target": 9
        }
    }

    # Save
    out_dir = STUDIO_ROOT / "edit_plans"
    out_dir.mkdir(parents=True, exist_ok=True)
    plan_file = out_dir / f"{project_name}_edit_plan.json"
    with open(plan_file, "w", encoding="utf-8") as f:
        json.dump(edit_plan, f, indent=2, ensure_ascii=False)
    print(f"[OK] Script-aligned EditPlan saved: {plan_file}")

    # Human summary
    print(f"\n[PLAN] Script-Aligned EditPlan Summary")
    print(f"   Source duration  : {duration:.0f}s")
    print(f"   Target duration  : {target_duration_min:.0f}s")
    print(f"   Cuts to remove   : {len(cuts_to_remove)} (fillers + pauses)")
    print(f"   Chapters         : {len(chapter_markers)}")
    print(f"   Highlight clips  : {len(short_clips)}")
    print(f"   B-Roll slots     : {len(broll_plan)} (script-anchored & non-overlapping)")
    print(f"   Motion graphics  : {len(motion_graphics)} cards (semantic dialogue sync)")

    return edit_plan

def main():
    parser = argparse.ArgumentParser(description="Agentic Video Studio — Phase 2: Creative Planning (Script Aligned)")
    parser.add_argument("project", help="Project name")
    parser.add_argument("--brief", "-b", default="Create an engaging, polished video optimised for social media.",
                        help="Creative brief (tone, style, goals)")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  Agentic Video Studio — Phase 2: Creative Planning (Script Aligned)")
    print(f"  Project : {args.project}")
    print(f"{'='*60}\n")

    analysis = load_analysis(args.project)
    transcript = load_transcript(args.project)
    build_edit_plan(analysis, transcript, args.brief, args.project)

    print(f"\n[OK] Phase 2 complete. EditPlan ready with exact script alignment.\n")

if __name__ == "__main__":
    main()
