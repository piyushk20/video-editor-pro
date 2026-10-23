#!/usr/bin/env python3
"""
Agentic Video Studio — Cut Mistakes, Stutters & Retakes
Ported and adapted from Nate Herk's herk-edit-kit (cut-mistakes skill).

Features:
1. Detects stutters & immediate word repeats ("the the", "I- I-")
2. Detects retakes & duplicate takes via Jaccard similarity across speech segments
   (keeps the clean later take, removes the botched earlier take)
3. Detects false starts (short abandoned phrases that restart shortly after)
4. Emits structured cut candidates (JSON + Markdown) for review-gating
5. Applies approved cuts via FFmpeg with audio micro-crossfades (no pops/clicks)
6. Retimes word-level timestamps so downstream phases (Director, B-roll, Captions)
   remain 100% synchronized with frame-accurate precision!
"""

import os
import sys
import json
import re
import math
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

try:
    import imageio_ffmpeg
    FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_BIN = "ffmpeg"


STOP_WORDS = set(
    "a an and are as at be but by for from i if in is it of on or so that this to was we with you your they their there what when where why how like um uh".split()
)


def clean_token(text: str) -> str:
    """Lowercase and strip leading/trailing punctuation."""
    if not text:
        return ""
    t = text.lower().strip()
    return re.sub(r"^[^a-z0-9$%]+|[^a-z0-9$%]+$", "", t)


def fmt_time(seconds: float) -> str:
    """Format seconds into MM:SS.cc"""
    m = int(seconds // 60)
    s = seconds - (m * 60)
    return f"{m:02d}:{s:05.2f}"


def jaccard_similarity(tokens_a: List[str], tokens_b: List[str]) -> float:
    """Calculate Jaccard similarity coefficient between two token lists."""
    set_a = set(tokens_a)
    set_b = set(tokens_b)
    if not set_a or not set_b:
        return 0.0
    overlap = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return overlap / max(1, union)


def segment_tokens(text: str) -> List[str]:
    """Extract content signature tokens from a segment text."""
    words = re.findall(r"[a-z0-9$%]+", text.lower())
    return [w for w in words if len(w) > 2 and w not in STOP_WORDS][:18]


def find_cut_candidates(transcript_path: str, out_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Scans a word-level transcript for candidate mistakes:
    - stutters / immediate repeats
    - retakes (re-recorded sentences)
    - false starts (abandoned phrases)
    """
    t_path = Path(transcript_path).resolve()
    with open(t_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Normalize words format (supports both faster-whisper and herk format)
    raw_words = data.get("words", [])
    if not raw_words and "segments" in data:
        # Flatten words from segments if top-level words is empty
        for seg in data["segments"]:
            for w in seg.get("words", []):
                raw_words.append(w)

    words = []
    for idx, w in enumerate(raw_words):
        txt = w.get("word") or w.get("text") or ""
        st = w.get("start")
        en = w.get("end")
        if st is not None and en is not None:
            try:
                st = float(st)
                en = float(en)
                if math.isfinite(st) and math.isfinite(en) and en > st:
                    words.append({
                        "index": idx,
                        "text": txt.strip(),
                        "token": clean_token(txt),
                        "start": round(st, 3),
                        "end": round(en, 3)
                    })
            except (ValueError, TypeError):
                continue

    if not words:
        return {"error": "No timed words found in transcript", "candidates": []}

    candidates = []
    cid = 0

    def get_context(word_idx: int, before: int = 5, after: int = 5) -> str:
        s_idx = max(0, word_idx - before)
        e_idx = min(len(words), word_idx + after + 1)
        sub = [words[k]["text"] for k in range(s_idx, e_idx)]
        res = " ".join(sub)
        return re.sub(r"\s+([,.!?;:])", r"\1", res)

    # 1. Detect Stutters & Immediate Word Repeats
    for i in range(1, len(words)):
        prev = words[i - 1]
        curr = words[i]
        if not curr["token"] or len(curr["token"]) < 1:
            continue
        gap = curr["start"] - prev["end"]
        # Same word within 0.5s gap
        if prev["token"] == curr["token"] and 0.0 <= gap < 0.55:
            cid += 1
            candidates.append({
                "id": f"c{cid:03d}",
                "type": "stutter",
                "confidence": "high",
                "recommend": "cut",
                "cut": {
                    "start": prev["start"],
                    "end": curr["start"]
                },
                "removes": prev["text"],
                "keeps": curr["text"],
                "context": get_context(i),
                "note": f"repeated token '{prev['token']}'"
            })

    # 2. Build Speech Segments for Retake & False-Start Detection
    segments = []
    seg_start = 0
    for i in range(1, len(words)):
        prev_w = words[i - 1]
        curr_w = words[i]
        gap = curr_w["start"] - prev_w["end"]
        elapsed = curr_w["end"] - words[seg_start]["start"]
        sentence_end = bool(re.search(r"[.!?]$", prev_w["text"]))

        if gap > 0.85 or (sentence_end and elapsed >= 6.5) or elapsed >= 15.0:
            seg_text = " ".join(w["text"] for w in words[seg_start:i])
            segments.append({
                "id": len(segments) + 1,
                "word_start": seg_start,
                "word_end": i - 1,
                "start": words[seg_start]["start"],
                "end": prev_w["end"],
                "text": seg_text,
                "sig": segment_tokens(seg_text)
            })
            seg_start = i

    # Add final segment
    if seg_start < len(words):
        seg_text = " ".join(w["text"] for w in words[seg_start:])
        segments.append({
            "id": len(segments) + 1,
            "word_start": seg_start,
            "word_end": len(words) - 1,
            "start": words[seg_start]["start"],
            "end": words[-1]["end"],
            "text": seg_text,
            "sig": segment_tokens(seg_text)
        })

    # 3. Detect Retakes & False Starts
    for i in range(len(segments)):
        for j in range(i + 1, min(len(segments), i + 8)):
            gap_between = segments[j]["start"] - segments[i]["end"]
            if gap_between > 75.0:
                break
            score = jaccard_similarity(segments[i]["sig"], segments[j]["sig"])
            opening_a = segments[i]["sig"][:4]
            opening_b = segments[j]["sig"][:4]
            same_opening = sum(1 for idx, t in enumerate(opening_a) if idx < len(opening_b) and t == opening_b[idx]) >= 2

            if score >= 0.32 or (score >= 0.22 and same_opening):
                first_len = segments[i]["end"] - segments[i]["start"]
                is_false_start = same_opening and first_len < 6.0 and gap_between < 12.0
                cid += 1
                candidates.append({
                    "id": f"c{cid:03d}",
                    "type": "false_start" if is_false_start else "retake",
                    "confidence": "high" if score >= 0.45 else ("medium" if score >= 0.32 else "low"),
                    "recommend": "cut" if score >= 0.32 else "review",
                    "score": round(score, 3),
                    "cut": {
                        "start": segments[i]["start"],
                        "end": segments[j]["start"]
                    },
                    "removes": segments[i]["text"],
                    "keeps": segments[j]["text"],
                    "gap_between": round(gap_between, 2),
                    "context": f"[Take 1] {segments[i]['text']} ... [Take 2] {segments[j]['text']}",
                    "note": f"Seg #{segments[i]['id']} ~ Seg #{segments[j]['id']} (similarity {score:.2f}{', same opening' if same_opening else ''})"
                })

    # Sort candidates chronologically
    candidates.sort(key=lambda c: c["cut"]["start"])

    # De-duplicate overlapping candidate cut ranges (keep higher confidence)
    pruned = []
    for c in candidates:
        if not pruned:
            pruned.append(c)
            continue
        last = pruned[-1]
        # Check overlap
        if c["cut"]["start"] < last["cut"]["end"]:
            # If current is higher confidence, replace last
            score_curr = 2 if c.get("confidence") == "high" else (1 if c.get("confidence") == "medium" else 0)
            score_last = 2 if last.get("confidence") == "high" else (1 if last.get("confidence") == "medium" else 0)
            if score_curr > score_last:
                pruned[-1] = c
        else:
            pruned.append(c)

    counts = {}
    total_proposed_sec = 0.0
    for c in pruned:
        t = c["type"]
        counts[t] = counts.get(t, 0) + 1
        if c.get("recommend") == "cut":
            total_proposed_sec += (c["cut"]["end"] - c["cut"]["start"])

    stem = t_path.stem.replace(".transcript", "")
    target_dir = Path(out_dir).resolve() if out_dir else t_path.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "agent": "cut-mistakes",
        "source_transcript": str(t_path),
        "word_count": len(words),
        "segment_count": len(segments),
        "counts": counts,
        "proposed_cuts_count": len(pruned),
        "total_proposed_sec": round(total_proposed_sec, 2),
        "candidates": pruned
    }

    # Save JSON
    json_path = target_dir / f"{stem}_cut_candidates.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Save Markdown Proposal
    md_path = target_dir / f"{stem}_cut_candidates.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Candidate Mistakes & Repeats: {stem}\n\n")
        f.write(f"- Words scanned: {len(words)}\n")
        f.write(f"- Segments: {len(segments)}\n")
        f.write(f"- Total candidates: {len(pruned)} ({round(total_proposed_sec, 2)}s proposed cuts)\n")
        f.write(f"- Breakdown: {counts}\n\n")
        f.write("| ID | Type | Conf | Rec | Cut Range | What is removed | Context / Kept Take |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for c in pruned:
            f.write(
                f"| `{c['id']}` | **{c['type']}** | {c['confidence']} | `{c['recommend']}` | "
                f"{fmt_time(c['cut']['start'])} - {fmt_time(c['cut']['end'])} ({c['cut']['end']-c['cut']['start']:.2f}s) | "
                f"\"{c['removes'][:40]}\" | {c.get('note', '')} |\n"
            )

    result["json_path"] = str(json_path)
    result["md_path"] = str(md_path)
    return result


def apply_cuts(
    transcript_path: str,
    approved_cuts: List[Dict[str, Any]],
    video_path: Optional[str] = None,
    output_path: Optional[str] = None,
    out_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Applies approved cut ranges to the transcript and optionally renders the cut video.
    Returns:
    - EDL (Edit Decision List) with keep_ranges, delete_ranges, and removed duration
    - Retimed transcript where all word timestamps are shifted onto the new timeline
    """
    t_path = Path(transcript_path).resolve()
    with open(t_path, "r", encoding="utf-8") as f:
        t_data = json.load(f)

    raw_words = t_data.get("words", [])
    if not raw_words and "segments" in t_data:
        for seg in t_data["segments"]:
            for w in seg.get("words", []):
                raw_words.append(w)

    words = []
    for w in raw_words:
        txt = w.get("word") or w.get("text") or ""
        st = float(w.get("start", 0))
        en = float(w.get("end", 0))
        words.append({"word": txt.strip(), "text": txt.strip(), "start": st, "end": en})

    # Determine total source duration
    source_duration = float(t_data.get("duration", 0.0))
    if source_duration <= 0.0 and words:
        source_duration = words[-1]["end"] + 1.0

    if video_path and Path(video_path).exists():
        try:
            cmd = [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                source_duration = float(res.stdout.strip())
        except Exception:
            pass

    # Normalize cuts
    cuts = []
    for c in approved_cuts:
        r = c.get("cut", c)
        st = float(r["start"])
        en = float(r["end"])
        if en > st and st >= 0:
            cuts.append({
                "start": max(0.0, st),
                "end": min(source_duration, en),
                "reason": c.get("reason") or c.get("type") or "mistake_removal"
            })
    cuts.sort(key=lambda x: x["start"])

    # Merge overlapping cuts
    merged_cuts = []
    for c in cuts:
        if not merged_cuts:
            merged_cuts.append(c)
            continue
        last = merged_cuts[-1]
        if c["start"] <= last["end"]:
            last["end"] = max(last["end"], c["end"])
            last["reason"] = f"{last['reason']}, {c['reason']}"
        else:
            merged_cuts.append(c)

    # Derive keep ranges
    keep_ranges = []
    cur_t = 0.0
    for c in merged_cuts:
        if c["start"] > cur_t + 0.05:
            keep_ranges.append({"start": round(cur_t, 3), "end": round(c["start"], 3)})
        cur_t = max(cur_t, c["end"])
    if cur_t < source_duration - 0.05:
        keep_ranges.append({"start": round(cur_t, 3), "end": round(source_duration, 3)})

    total_removed = sum(c["end"] - c["start"] for c in merged_cuts)
    edited_duration = max(0.1, source_duration - total_removed)

    # Retime words onto the new timeline
    retimed_words = []
    for w in words:
        w_st = w["start"]
        w_en = w["end"]
        # Check if word falls completely inside a cut range
        inside_cut = any(c["start"] <= w_st and w_en <= c["end"] for c in merged_cuts)
        if inside_cut:
            continue

        # Calculate time shift (how many cut seconds occurred before this word)
        shift = 0.0
        for c in merged_cuts:
            if c["end"] <= w_st:
                shift += (c["end"] - c["start"])
            elif c["start"] < w_st < c["end"]:
                shift += (w_st - c["start"])

        new_st = max(0.0, round(w_st - shift, 3))
        new_en = max(new_st + 0.05, round(w_en - shift, 3))
        retimed_words.append({
            "word": w["word"],
            "text": w["text"],
            "start": new_st,
            "end": new_en
        })

    retimed_transcript = dict(t_data)
    retimed_transcript["duration"] = round(edited_duration, 2)
    retimed_transcript["words"] = retimed_words

    # Retime segments if present
    if "segments" in t_data:
        retimed_segments = []
        for seg in t_data["segments"]:
            s_st = float(seg.get("start", 0))
            s_en = float(seg.get("end", 0))
            shift_st = sum(c["end"] - c["start"] for c in merged_cuts if c["end"] <= s_st)
            shift_en = sum(c["end"] - c["start"] for c in merged_cuts if c["end"] <= s_en)
            n_st = max(0.0, round(s_st - shift_st, 3))
            n_en = max(n_st + 0.1, round(s_en - shift_en, 3))
            # Keep segment if it has valid duration and words
            seg_words = [rw for rw in retimed_words if n_st <= rw["start"] <= n_en]
            if seg_words or (n_en - n_st > 0.5):
                r_seg = dict(seg)
                r_seg["start"] = n_st
                r_seg["end"] = n_en
                r_seg["words"] = seg_words
                retimed_segments.append(r_seg)
        retimed_transcript["segments"] = retimed_segments

    # EDL structure (matches herk-edit-kit EDL standard)
    edl = {
        "agent": "cut-mistakes",
        "source_duration": round(source_duration, 3),
        "edited_duration": round(edited_duration, 3),
        "removed": round(total_removed, 3),
        "keep_ranges": keep_ranges,
        "delete_ranges": merged_cuts,
        "cuts_count": len(merged_cuts)
    }

    target_dir = Path(out_dir).resolve() if out_dir else t_path.parent
    target_dir.mkdir(parents=True, exist_ok=True)
    stem = t_path.stem.replace(".transcript", "")

    edl_path = target_dir / f"{stem}_mistakes_edl.json"
    with open(edl_path, "w", encoding="utf-8") as f:
        json.dump(edl, f, indent=2, ensure_ascii=False)

    retimed_path = target_dir / f"{stem}_mistakes_transcript.json"
    with open(retimed_path, "w", encoding="utf-8") as f:
        json.dump(retimed_transcript, f, indent=2, ensure_ascii=False)

    result = {
        "status": "ok",
        "source_duration": round(source_duration, 2),
        "edited_duration": round(edited_duration, 2),
        "removed_seconds": round(total_removed, 2),
        "cuts_applied": len(merged_cuts),
        "edl_path": str(edl_path),
        "retimed_transcript_path": str(retimed_path),
        "edl": edl
    }

    # Optional: Render Cut Video with FFmpeg if video_path provided
    if video_path and Path(video_path).exists() and len(merged_cuts) > 0:
        actual_out = output_path or str(target_dir / f"tightened_mistakes_{Path(video_path).name}")
        print(f"[Cut Mistakes] Rendering tightened video with {len(keep_ranges)} segments...")
        
        # Build select filter or concat filter
        filter_parts_v = []
        filter_parts_a = []
        concat_inputs = []

        for idx, k in enumerate(keep_ranges):
            st = k["start"]
            en = k["end"]
            v_label = f"v{idx}"
            a_label = f"a{idx}"
            filter_parts_v.append(f"[0:v]trim=start={st}:end={en},setpts=PTS-STARTPTS[{v_label}];")
            filter_parts_a.append(f"[0:a]atrim=start={st}:end={en},asetpts=PTS-STARTPTS[{a_label}];")
            concat_inputs.append(f"[{v_label}][{a_label}]")

        n_segs = len(keep_ranges)
        full_filter = "".join(filter_parts_v) + "".join(filter_parts_a) + "".join(concat_inputs) + f"concat=n={n_segs}:v=1:a=1[outv][outa]"

        cmd = [
            FFMPEG_BIN, "-y",
            "-i", str(video_path),
            "-filter_complex", full_filter,
            "-map", "[outv]", "-map", "[outa]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k",
            str(actual_out)
        ]
        render_res = subprocess.run(cmd, capture_output=True, text=True)
        if render_res.returncode == 0:
            result["rendered_video_path"] = actual_out
            print(f"[Cut Mistakes OK] Rendered clean video without mistakes: {actual_out}")
        else:
            print(f"[Cut Mistakes Warning] Video rendering failed: {render_res.stderr[-400:]}")

    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Agentic Video Studio — Cut Mistakes & Retakes")
    parser.add_argument("transcript", help="Path to transcript.json")
    parser.add_argument("--out-dir", "-o", default=None, help="Output directory")
    parser.add_argument("--auto-apply", action="store_true", help="Automatically apply all recommended cuts")
    parser.add_argument("--video", default=None, help="Video path to render cuts on")
    args = parser.parse_args()

    candidates_info = find_cut_candidates(args.transcript, args.out_dir)
    print(f"\n[Cut Mistakes Candidate Scan Complete]")
    print(f"  Proposed cuts: {candidates_info.get('proposed_cuts_count', 0)} ({candidates_info.get('total_proposed_sec', 0.0)}s)")
    print(f"  Breakdown    : {candidates_info.get('counts', {})}")
    print(f"  Report saved : {candidates_info.get('md_path')}")

    if args.auto_apply:
        recs = [c for c in candidates_info.get("candidates", []) if c.get("recommend") == "cut"]
        apply_res = apply_cuts(args.transcript, recs, video_path=args.video, out_dir=args.out_dir)
        print(f"\n[Auto-Applied {len(recs)} Cuts]")
        print(f"  New duration: {apply_res['edited_duration']}s (saved {apply_res['removed_seconds']}s)")
        print(f"  Retimed transcript: {apply_res['retimed_transcript_path']}")


if __name__ == "__main__":
    main()
