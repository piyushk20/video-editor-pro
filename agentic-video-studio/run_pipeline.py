#!/usr/bin/env python3
"""
STUDIO PIPELINE RUNNER — Single command to run all phases end-to-end.
Incorporates features from Nate Herk's herk-edit-kit:
- Phase 0: Input Handler & Silence Trimmer
- Phase 1: Whisper Word-Level Transcription & Semantic Analysis
- Phase 1.5: Transcript-Driven Mistake, Stutter & Retake Cutter + Visual EDL Generator
- Phase 2: Creative Director + Nate Herk House Reel Pacing & Motion Graphics
- Phase 3: B-Roll Sourcing & Visual Assembly
- Phase 3.5: Preflight & Safe-Zone Occlusion Verification Guard
- Phase 4: Master 9:16 Compositing, -14 LUFS Audio Normalization & Multi-Format Render

Usage:
  python run_pipeline.py <input> --project <name> --brief "<creative brief>"
"""
import argparse
import subprocess
import sys
import shutil
import json
from pathlib import Path

STUDIO_ROOT = Path(__file__).parent
TOOLS = STUDIO_ROOT / "tools"


def run(script: str, *args):
    cmd = [sys.executable, str(TOOLS / script)] + list(args)
    print(f"\n{'='*60}")
    print(f"  >> {script} {' '.join(str(a) for a in args)}")
    print(f"{'='*60}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"\n[ERROR] {script} failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(description="[STUDIO] Agentic Video Studio — Full Pipeline Runner")
    parser.add_argument("input", nargs="?", help="Input: local file path or URL")
    parser.add_argument("--project", "-p", required=True, help="Project name")
    parser.add_argument("--brief", "-b", default="Create an engaging, polished video for social media.",
                        help="Creative brief describing tone, style, goals")
    parser.add_argument("--model", "-m", default="base",
                        choices=["tiny", "base", "small", "medium", "large-v2"],
                        help="Whisper model size (default: base)")
    parser.add_argument("--phase", "-ph", type=int, default=0,
                        help="Start from this phase (0=all, 1=skip input, 2=skip analysis, etc.)")
    parser.add_argument("--no-subtitles", action="store_true", help="Skip subtitle burn-in in Phase 4")
    parser.add_argument("--no-cut-mistakes", dest="cut_mistakes", action="store_false", default=True,
                        help="Disable transcript-driven mistake and stutter cutting")
    parser.add_argument("--no-house-style", dest="house_style", action="store_false", default=True,
                        help="Disable Nate Herk house reel pacing and templates")
    args = parser.parse_args()

    print(f"""
+==========================================================╗
|        [STUDIO]  AGENTIC VIDEO STUDIO — PIPELINE START         |
+==========================================================╣
|  Project       : {args.project:<40} |
|  Brief         : {args.brief[:40]:<40} |
|  Model         : {args.model:<40} |
|  Cut Mistakes  : {str(args.cut_mistakes):<40} |
|  House Pacing  : {str(args.house_style):<40} |
+==========================================================╝
""")

    start_phase = args.phase

    # Phase 0: Ingestion & Initial Pause Trimming
    if start_phase <= 0:
        if not args.input:
            print("[ERROR] --input required for Phase 0")
            sys.exit(1)
        run("phase0_input_handler.py", args.input, "--project", args.project)

    # Phase 1: Whisper Word-Level Transcription
    if start_phase <= 1:
        run("phase1_analyser.py", args.project, "--model", args.model)

    # Phase 1.5: Transcript-Driven Mistake & Retake Cutter (Herk Edit Kit)
    if args.cut_mistakes and start_phase <= 2:
        transcript_file = STUDIO_ROOT / "transcripts" / args.project / "transcript.json"
        if transcript_file.exists():
            print("\n[Phase 1.5: Herk Edit Kit — Mistake, Stutter & Retake Cutter]")
            # 1. Scan candidate cuts
            run("cut_mistakes.py", str(transcript_file), "--auto-apply")

            # 2. Build Interactive Visual EDL Review
            edl_file = STUDIO_ROOT / "transcripts" / args.project / "transcript_mistakes_edl.json"
            if edl_file.exists():
                edl_out = STUDIO_ROOT / "renders" / args.project / "edl_review.html"
                run("build_edl_review.py", str(edl_file), "--output", str(edl_out))
                # Also copy to output/ directory
                workspace_out = STUDIO_ROOT.parent / "output" / args.project
                workspace_out.mkdir(parents=True, exist_ok=True)
                if edl_out.exists():
                    shutil.copy2(edl_out, workspace_out / "edl_review.html")

    # Phase 2: Creative Director & Herk Motion Graphics
    if start_phase <= 2:
        run("phase2_director.py", args.project, "--brief", args.brief)
        if args.house_style:
            transcript_file = STUDIO_ROOT / "transcripts" / args.project / "transcript.json"
            if transcript_file.exists():
                run("house_reel_engine.py", str(transcript_file))
            run("generate_herk_graphics.py", args.project)

    # Phase 3: Visual Sourcing
    if start_phase <= 3:
        run("phase3_broll_sourcer.py", args.project)

    # Phase 3.5: Preflight Safe-Zone & Occlusion Guard
    if start_phase <= 4:
        run("preflight_guard.py", args.project)

    # Phase 4: Assembly & Broadcast Compositing
    if start_phase <= 4:
        extra = ["--skip-subtitles"] if args.no_subtitles else []
        run("phase4_editor.py", args.project, *extra)

    # Ensure all deliverables (EDL review, reports, transcripts) are synced to output/
    render_proj = STUDIO_ROOT / "renders" / args.project
    output_proj = STUDIO_ROOT.parent / "output" / args.project
    if render_proj.exists() and output_proj.exists():
        for f in render_proj.glob("*.html"):
            shutil.copy2(f, output_proj / f.name)
        for f in render_proj.glob("*.json"):
            shutil.copy2(f, output_proj / f.name)

    print(f"""
+==========================================================╗
|  [OK]  PIPELINE COMPLETE                                   |
|  Renders : agentic-video-studio/renders/{args.project:<17} |
|  Review  : agentic-video-studio/reviews/{args.project}_review.json |
|  EDL     : output/{args.project}/edl_review.html        |
+==========================================================╝
""")


if __name__ == "__main__":
    main()
