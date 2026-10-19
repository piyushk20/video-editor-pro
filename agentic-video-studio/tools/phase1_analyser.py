#!/usr/bin/env python3
"""
PHASE 1 — Deep Content Analysis
Performs word-level transcription (faster-whisper), speaker diarization heuristics,
semantic analysis, and opportunity mapping. Saves all outputs to analysis/ + transcripts/.
"""
import os, sys, json, time, argparse
from pathlib import Path
from datetime import datetime

STUDIO_ROOT = Path(__file__).parent.parent

def load_manifest(project_name: str) -> dict:
    manifest = STUDIO_ROOT / "inputs" / project_name / "manifest.json"
    if not manifest.exists():
        print(f"[ERROR] No manifest found for project '{project_name}'. Run Phase 0 first.")
        sys.exit(1)
    with open(manifest) as f:
        return json.load(f)

import imageio_ffmpeg

def extract_audio(video_path: str, project_name: str) -> str:
    """Extract audio from video for transcription."""
    import subprocess
    audio_out = STUDIO_ROOT / "analysis" / project_name / "audio_extract.wav"
    audio_out.parent.mkdir(parents=True, exist_ok=True)
    if audio_out.exists():
        print(f"[SKIP] Audio already extracted: {audio_out}")
        return str(audio_out)
    print(f"[FFmpeg] Extracting audio from: {video_path}")
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_bin, "-y", "-i", video_path,
        "-ac", "1", "-ar", "16000", "-vn",
        str(audio_out)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] FFmpeg audio extraction failed:\n{result.stderr}")
        sys.exit(1)
    print(f"[OK] Audio extracted: {audio_out}")
    return str(audio_out)

def transcribe(audio_path: str, project_name: str, model_size: str = "base") -> dict:
    """Word-level transcription with faster-whisper."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("[ERROR] faster-whisper not installed. Run: pip install faster-whisper")
        sys.exit(1)

    transcript_dir = STUDIO_ROOT / "transcripts" / project_name
    transcript_dir.mkdir(parents=True, exist_ok=True)
    transcript_file = transcript_dir / "transcript.json"

    if transcript_file.exists():
        print(f"[SKIP] Transcript already exists: {transcript_file}")
        with open(transcript_file) as f:
            return json.load(f)

    print(f"[Whisper] Loading model: {model_size} ...")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    print(f"[Whisper] Transcribing: {audio_path}")
    t0 = time.time()

    # PyAV 19.x broke faster-whisper's decode_audio (metadata_errors kwarg removed).
    # Workaround: load WAV directly as numpy float32 array and pass to transcribe().
    try:
        import soundfile as sf
        import numpy as np
        audio_data, sample_rate = sf.read(audio_path, dtype="float32", always_2d=False)
        if audio_data.ndim > 1:
            audio_data = audio_data.mean(axis=1)  # stereo -> mono
        if sample_rate != 16000:
            # Resample with numpy (simple linear interp fallback)
            target_len = int(len(audio_data) * 16000 / sample_rate)
            audio_data = np.interp(
                np.linspace(0, len(audio_data) - 1, target_len),
                np.arange(len(audio_data)),
                audio_data
            ).astype(np.float32)
        print(f"[Whisper] Audio loaded via soundfile: {len(audio_data)/16000:.1f}s @ 16kHz")
        audio_input = audio_data
    except Exception as e:
        print(f"[WARN] soundfile load failed ({e}), falling back to file path.")
        audio_input = audio_path

    segments, info = model.transcribe(audio_input, word_timestamps=True, vad_filter=True)

    all_segments = []
    all_words = []
    full_text_parts = []

    for seg in segments:
        words = []
        if seg.words:
            for w in seg.words:
                word_obj = {"word": w.word, "start": round(w.start, 3), "end": round(w.end, 3), "prob": round(w.probability, 3)}
                words.append(word_obj)
                all_words.append(word_obj)
        seg_obj = {
            "id": seg.id,
            "start": round(seg.start, 3),
            "end": round(seg.end, 3),
            "text": seg.text.strip(),
            "words": words
        }
        all_segments.append(seg_obj)
        full_text_parts.append(seg.text.strip())

    elapsed = round(time.time() - t0, 1)
    transcript = {
        "project": project_name,
        "audio_path": audio_path,
        "language": info.language,
        "language_probability": round(info.language_probability, 3),
        "duration": round(info.duration, 2),
        "transcription_time_sec": elapsed,
        "model": model_size,
        "segments": all_segments,
        "words": all_words,
        "full_text": " ".join(full_text_parts),
        "timestamp": datetime.now().isoformat()
    }

    with open(transcript_file, "w", encoding="utf-8") as f:
        json.dump(transcript, f, indent=2, ensure_ascii=False)

    # Also save readable SRT
    srt_file = transcript_dir / "transcript.srt"
    with open(srt_file, "w", encoding="utf-8") as f:
        for i, seg in enumerate(all_segments, 1):
            def fmt(t):
                h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60); ms = int((t % 1) * 1000)
                return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
            f.write(f"{i}\n{fmt(seg['start'])} --> {fmt(seg['end'])}\n{seg['text']}\n\n")

    print(f"[OK] Transcript saved ({len(all_segments)} segments, {len(all_words)} words, {elapsed}s)")
    return transcript

def analyse_content(transcript: dict, project_name: str) -> dict:
    """Semantic analysis: filler words, key moments, chapter points, highlights."""
    FILLERS = {"um", "uh", "like", "you know", "i mean", "basically", "literally", "sort of", "kind of", "right"}
    words = transcript.get("words", [])
    segments = transcript.get("segments", [])
    full_text = transcript.get("full_text", "")
    duration = transcript.get("duration", 0)

    # Filler detection
    filler_instances = []
    for w in words:
        if w["word"].strip().lower() in FILLERS:
            filler_instances.append({"word": w["word"], "start": w["start"], "end": w["end"]})

    # Long pauses detection (gap between consecutive words > 1.5s)
    pauses = []
    for i in range(1, len(words)):
        gap = words[i]["start"] - words[i-1]["end"]
        if gap > 1.5:
            pauses.append({"start": words[i-1]["end"], "end": words[i]["start"], "duration": round(gap, 2)})

    # Chapter detection: heuristic — segments with long pauses before them
    chapter_points = []
    for i, seg in enumerate(segments):
        if i == 0:
            chapter_points.append({"index": i, "start": seg["start"], "text": seg["text"][:80]})
            continue
        gap = seg["start"] - segments[i-1]["end"]
        if gap > 3.0 and seg["start"] > 30:
            chapter_points.append({"index": i, "start": seg["start"], "text": seg["text"][:80]})

    # Highlight detection: high-energy moments (short gap, lots of words)
    highlights = []
    for seg in segments:
        wcount = len(seg.get("words", []))
        seg_dur = seg["end"] - seg["start"]
        if seg_dur > 0:
            wpm = (wcount / seg_dur) * 60
            if wpm > 150 and seg_dur >= 5:  # fast speech = energetic
                highlights.append({"start": seg["start"], "end": seg["end"], "text": seg["text"][:100], "wpm": round(wpm)})

    # B-roll opportunity map: comprehensive visual triggers across tech, lifestyle, finance, behavior
    visual_triggers = [
        "office", "computer", "city", "nature", "team", "product", "graph", "data",
        "phone", "meeting", "presentation", "screen", "technology", "ai", "startup",
        "money", "growth", "chart", "interview", "stage", "audience", "algorithm",
        "social", "media", "scroll", "feed", "mobile", "app", "digital", "network",
        "wealth", "rich", "poor", "budget", "finance", "invest", "crypto", "bank",
        "card", "debt", "luxury", "success", "lifestyle", "house", "car", "travel",
        "work", "stress", "anxiety", "focus", "habit", "routine", "mind", "brain",
        "think", "people", "friend", "family", "crowd", "street", "coffee", "laptop",
        "time", "clock", "future", "world", "book", "writing", "read", "camera"
    ]
    broll_moments = []
    for seg in segments:
        text = seg["text"].lower()
        matched = [kw for kw in visual_triggers if kw in text]
        if matched:
            broll_moments.append({"start": seg["start"], "end": seg["end"], "text": seg["text"][:100], "keywords": matched})

    # If few broll opportunities detected (e.g. abstract discourse), generate rhythmic slots
    if len(broll_moments) < 4 and duration > 15:
        target_slots = max(3, min(8, int(duration // 20)))
        step = duration / (target_slots + 1)
        for idx in range(1, target_slots + 1):
            slot_t = round(idx * step, 2)
            # Find closest segment
            closest_seg = min(segments, key=lambda s: abs(s["start"] - slot_t)) if segments else None
            seg_text = closest_seg["text"] if closest_seg else project_name
            broll_moments.append({
                "start": slot_t,
                "end": min(duration, slot_t + 4.5),
                "text": seg_text[:100],
                "keywords": [project_name.replace("_", " "), "cinematic", "lifestyle"]
            })
        # Sort by start time
        broll_moments.sort(key=lambda x: x["start"])

    analysis = {
        "project": project_name,
        "duration": duration,
        "filler_count": len(filler_instances),
        "filler_instances": filler_instances[:50],  # cap for readability
        "pause_count": len(pauses),
        "long_pauses": pauses,
        "chapter_points": chapter_points,
        "highlight_moments": highlights,
        "broll_opportunities": broll_moments,
        "summary_stats": {
            "total_segments": len(segments),
            "total_words": len(words),
            "fillers_per_minute": round(len(filler_instances) / (duration / 60), 2) if duration else 0,
        },
        "timestamp": datetime.now().isoformat()
    }

    out_dir = STUDIO_ROOT / "analysis" / project_name
    out_dir.mkdir(parents=True, exist_ok=True)
    analysis_file = out_dir / "content_analysis.json"
    with open(analysis_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    # Human-readable report
    report_file = out_dir / "analysis_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# Content Analysis Report — {project_name}\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"## Stats\n")
        f.write(f"- Duration: {duration:.1f}s ({duration/60:.1f} min)\n")
        f.write(f"- Segments: {len(segments)} | Words: {len(words)}\n")
        f.write(f"- Filler words: {len(filler_instances)} ({analysis['summary_stats']['fillers_per_minute']}/min)\n")
        f.write(f"- Long pauses (>1.5s): {len(pauses)}\n\n")
        f.write(f"## Chapter Points\n")
        for cp in chapter_points:
            mins = int(cp['start']//60); secs = int(cp['start']%60)
            f.write(f"- [{mins:02d}:{secs:02d}] {cp['text']}\n")
        f.write(f"\n## Highlight Moments\n")
        for h in highlights:
            f.write(f"- [{h['start']:.1f}s–{h['end']:.1f}s] {h['text']} ({h['wpm']} wpm)\n")
        f.write(f"\n## B-Roll Opportunities\n")
        for b in broll_moments:
            f.write(f"- [{b['start']:.1f}s] keywords={b['keywords']} → \"{b['text'][:60]}...\"\n")

    print(f"[OK] Analysis saved: {analysis_file}")
    print(f"[OK] Report saved: {report_file}")
    return analysis

def main():
    parser = argparse.ArgumentParser(description="Agentic Video Studio — Phase 1: Content Analysis")
    parser.add_argument("project", help="Project name (must match Phase 0 project)")
    parser.add_argument("--model", default="base", choices=["tiny", "base", "small", "medium", "large-v2"],
                        help="Whisper model size (default: base)")
    args = parser.parse_args()
    project_name = args.project

    print(f"\n{'='*60}")
    print(f"  Agentic Video Studio — Phase 1: Content Analysis")
    print(f"  Project : {project_name}")
    print(f"  Model   : {args.model}")
    print(f"{'='*60}\n")

    manifest = load_manifest(project_name)
    input_path = manifest["path"]
    input_type = manifest["type"]

    # Extract audio if needed
    if input_type in ("url", "video"):
        audio_path = extract_audio(input_path, project_name)
    elif input_type == "audio":
        audio_path = input_path
    elif input_type == "image":
        print("[NOTE] Image input detected — skipping transcription. Generating visual analysis plan only.")
        audio_path = None
    else:
        audio_path = None

    if audio_path:
        transcript = transcribe(audio_path, project_name, model_size=args.model)
        analysis = analyse_content(transcript, project_name)
    else:
        print("[SKIP] No audio — generating placeholder analysis for image workflow.")
        analysis = {"project": project_name, "type": "image", "timestamp": datetime.now().isoformat()}

    print(f"\n[OK] Phase 1 complete. Analysis ready for Phase 2 planning.\n")

if __name__ == "__main__":
    main()
