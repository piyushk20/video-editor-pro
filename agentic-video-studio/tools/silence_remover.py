#!/usr/bin/env python3
"""
Agentic Video Studio ? Silence & Pause Trimmer
Detects and removes dead air, awkward pauses, and silent gaps from video/audio.
Preserves natural breath padding (80ms) and applies 20ms audio micro-fades to prevent clicks.
"""

import os
import sys
import re
import json
import argparse
import subprocess
from pathlib import Path

try:
    import imageio_ffmpeg
    FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_BIN = "ffmpeg"


def get_media_duration(media_path: str) -> float:
    """Return total media duration in seconds via FFmpeg probe."""
    cmd = [FFMPEG_BIN, "-i", media_path]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", res.stderr)
    if m:
        h, mn, s = float(m.group(1)), float(m.group(2)), float(m.group(3))
        return round(h * 3600 + mn * 60 + s, 3)
    return 0.0


def detect_silences(media_path: str, noise_db: int = -32, min_silence_sec: float = 0.35) -> list[tuple[float, float, float]]:
    """
    Detect pauses longer than min_silence_sec below noise_db threshold.
    Returns list of (start_time, end_time, duration).
    """
    cmd = [
        FFMPEG_BIN, "-i", media_path,
        "-af", f"silencedetect=noise={noise_db}dB:d={min_silence_sec}",
        "-f", "null", "-"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    silences = []
    current_start = None
    for line in res.stderr.splitlines():
        if "silence_start:" in line:
            m = re.search(r"silence_start:\s*([\d\.]+)", line)
            if m:
                current_start = float(m.group(1))
        elif "silence_end:" in line and current_start is not None:
            m = re.search(r"silence_end:\s*([\d\.]+).*silence_duration:\s*([\d\.]+)", line)
            if m:
                silences.append((current_start, float(m.group(1)), float(m.group(2))))
                current_start = None

    return silences


def remove_silences(
    input_path: str,
    output_path: str,
    noise_db: int = -32,
    min_silence_sec: float = 0.35,
    pad_sec: float = 0.08
) -> dict:
    """
    Splices out silent gaps from input_path and renders tightened video to output_path.
    Leaves pad_sec breath cushion on each side of speech.
    """
    input_file = Path(input_path).resolve()
    output_file = Path(output_path).resolve()
    output_file.parent.mkdir(parents=True, exist_ok=True)

    total_duration = get_media_duration(str(input_file))
    if total_duration <= 0:
        raise ValueError(f"Could not determine duration for: {input_path}")

    silences = detect_silences(str(input_file), noise_db=noise_db, min_silence_sec=min_silence_sec)
    
    if not silences:
        print("  [Silence Trimmer] No pauses detected exceeding threshold. Copying original.")
        import shutil
        shutil.copy2(input_file, output_file)
        return {
            "original_duration": total_duration,
            "new_duration": total_duration,
            "silence_removed_sec": 0.0,
            "silence_count": 0,
            "output_path": str(output_file)
        }

    # Build active speech segments (keep list)
    keep_segments = []
    prev_end = 0.0

    for s_start, s_end, s_dur in silences:
        seg_start = prev_end
        seg_end = min(total_duration, s_start + pad_sec)
        if seg_end - seg_start > 0.15:
            keep_segments.append((round(seg_start, 3), round(seg_end, 3)))
        prev_end = max(0.0, s_end - pad_sec)

    if prev_end < total_duration:
        keep_segments.append((round(prev_end, 3), round(total_duration, 3)))

    new_duration = sum(e - s for s, e in keep_segments)
    time_saved = total_duration - new_duration

    print(f"  [Silence Trimmer] Detected {len(silences)} pauses.")
    print(f"  [Silence Trimmer] Original: {total_duration:.2f}s | Tightened: {new_duration:.2f}s (Saved {time_saved:.2f}s)")

    # Build FFmpeg complex filter for splicing
    v_filters = []
    a_filters = []
    concat_inputs = []

    for idx, (s, e) in enumerate(keep_segments):
        v_filters.append(f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{idx}]")
        # Add 20ms audio micro-fade to eliminate clicks/pops at cuts
        a_filters.append(f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={round(e - s - 0.02, 3)}:d=0.02[a{idx}]")
        concat_inputs.append(f"[v{idx}][a{idx}]")

    concat_filter = f"{''.join(concat_inputs)}concat=n={len(keep_segments)}:v=1:a=1[v_out][a_out]"
    full_filter = f"{';'.join(v_filters)};{';'.join(a_filters)};{concat_filter}"

    cmd = [
        FFMPEG_BIN, "-y",
        "-i", str(input_file),
        "-filter_complex", full_filter,
        "-map", "[v_out]",
        "-map", "[a_out]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "19",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_file)
    ]

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg silence splicing failed: {res.stderr[-500:]}")

    actual_duration = get_media_duration(str(output_file))

    result = {
        "original_duration": total_duration,
        "new_duration": actual_duration,
        "silence_removed_sec": round(total_duration - actual_duration, 2),
        "silence_count": len(silences),
        "keep_segments": keep_segments,
        "output_path": str(output_file)
    }

    # Save summary report in same directory
    summary_path = output_file.parent / "silence_report.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result


def main():
    parser = argparse.ArgumentParser(description="Agentic Video Studio ? Silence & Pause Trimmer")
    parser.add_argument("input", help="Path to input video or audio file")
    parser.add_argument("--output", "-o", required=True, help="Path to output tightened file")
    parser.add_argument("--noise-db", "-n", type=int, default=-32, help="Noise threshold in dB (default: -32)")
    parser.add_argument("--min-silence", "-m", type=float, default=0.35, help="Minimum silence duration in seconds (default: 0.35)")
    parser.add_argument("--pad", "-p", type=float, default=0.08, help="Breath cushion padding in seconds (default: 0.08)")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  Agentic Video Studio ? Silence & Pause Trimmer")
    print(f"  Input       : {args.input}")
    print(f"  Output      : {args.output}")
    print(f"  Noise Gate  : {args.noise_db} dB")
    print(f"  Min Silence : {args.min_silence}s")
    print(f"  Breath Pad  : {args.pad}s")
    print(f"{'='*60}\n")

    res = remove_silences(
        args.input,
        args.output,
        noise_db=args.noise_db,
        min_silence_sec=args.min_silence,
        pad_sec=args.pad
    )

    print(f"\n[OK] Spliced output saved: {res['output_path']}")
    print(f"     Duration: {res['original_duration']:.2f}s -> {res['new_duration']:.2f}s (Saved {res['silence_removed_sec']:.2f}s)\n")


if __name__ == "__main__":
    main()
