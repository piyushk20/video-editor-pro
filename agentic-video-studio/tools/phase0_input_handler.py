#!/usr/bin/env python3
"""
PHASE 0 — Universal Input Handler
Accepts: local video/audio file, YouTube/URL, or image/infographic.
Normalises everything into agentic-video-studio/inputs/.
"""
import os, sys, shutil, subprocess, argparse, json
from pathlib import Path
from datetime import datetime

STUDIO_ROOT = Path(__file__).parent.parent
INPUTS_DIR  = STUDIO_ROOT / "inputs"
INPUTS_DIR.mkdir(parents=True, exist_ok=True)

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".ts"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac", ".opus"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"}

def detect_input_type(path_or_url: str) -> str:
    if path_or_url.startswith(("http://", "https://", "www.")):
        return "url"
    p = Path(path_or_url)
    ext = p.suffix.lower()
    if ext in VIDEO_EXTS: return "video"
    if ext in AUDIO_EXTS: return "audio"
    if ext in IMAGE_EXTS: return "image"
    return "unknown"

def handle_url(url: str, project_name: str) -> dict:
    out_dir = INPUTS_DIR / project_name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_template = str(out_dir / "%(title)s.%(ext)s")
    print(f"[yt-dlp] Downloading best quality from: {url}")
    cmd = [
        "yt-dlp",
        "--format", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "--write-info-json",
        "--write-thumbnail",
        "--output", out_template,
        url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] yt-dlp failed:\n{result.stderr}")
        sys.exit(1)
    # Find downloaded file
    files = list(out_dir.glob("*.mp4"))
    info_files = list(out_dir.glob("*.json"))
    video_path = files[0] if files else None
    title = ""
    if info_files:
        with open(info_files[0]) as f:
            info = json.load(f)
        title = info.get("title", "")
    print(f"[OK] Downloaded: {video_path}")
    return {"type": "url", "path": str(video_path), "title": title, "project": project_name}

def handle_local(local_path: str, project_name: str, input_type: str) -> dict:
    src = Path(local_path)
    if not src.exists():
        print(f"[ERROR] File not found: {local_path}")
        sys.exit(1)
    out_dir = INPUTS_DIR / project_name
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / src.name
    if not dst.exists():
        shutil.copy2(src, dst)
    print(f"[OK] Copied {input_type}: {dst}")
    return {"type": input_type, "path": str(dst), "title": src.stem, "project": project_name}

def main():
    parser = argparse.ArgumentParser(description="Agentic Video Studio — Phase 0: Input Handler")
    parser.add_argument("input", help="Local file path, YouTube URL, or web URL")
    parser.add_argument("--project", "-p", default="", help="Project name (auto-generated if omitted)")
    args = parser.parse_args()

    input_str = args.input
    input_type = detect_input_type(input_str)
    project_name = args.project or f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print(f"\n{'='*60}")
    print(f"  Agentic Video Studio — Phase 0: Input Handler")
    print(f"  Input  : {input_str}")
    print(f"  Type   : {input_type}")
    print(f"  Project: {project_name}")
    print(f"{'='*60}\n")

    if input_type == "url":
        result = handle_url(input_str, project_name)
    elif input_type in ("video", "audio", "image"):
        result = handle_local(input_str, project_name, input_type)
    else:
        print(f"[ERROR] Unrecognised input type for: {input_str}")
        sys.exit(1)

    # Save manifest
    manifest_path = INPUTS_DIR / project_name / "manifest.json"
    result["timestamp"] = datetime.now().isoformat()
    with open(manifest_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"[OK] Manifest saved: {manifest_path}")
    print(f"\n[DONE] Phase 0 complete. Project '{project_name}' ready for Phase 1 analysis.\n")
    return result

if __name__ == "__main__":
    main()
