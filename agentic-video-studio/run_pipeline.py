#!/usr/bin/env python3
"""
STUDIO PIPELINE RUNNER — Single command to run all 5 phases end-to-end.
Usage:
  python run_pipeline.py <input> --project <name> --brief "<creative brief>"

Optional:
  --model tiny|base|small|medium|large-v2
  --phase 0-5 (run only a specific phase, defaults to all)
"""
import argparse, subprocess, sys
from pathlib import Path

STUDIO_ROOT = Path(__file__).parent
TOOLS = STUDIO_ROOT / "tools"

def run(script: str, *args):
    cmd = [sys.executable, str(TOOLS / script)] + list(args)
    print(f"\n{'='*60}")
    print(f"  >> {script}")
    print(f"{'='*60}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"\n[ERROR] {script} failed with exit code {result.returncode}")
        sys.exit(result.returncode)

def main():
    parser = argparse.ArgumentParser(description="[STUDIO] Agentic Video Studio — Full Pipeline Runner")
    parser.add_argument("input", nargs="?", help="Input: local file path or URL")
    parser.add_argument("--project", "-p", required=True, help="Project name")
    parser.add_argument("--brief",   "-b", default="Create an engaging, polished video for social media.",
                        help="Creative brief describing tone, style, goals")
    parser.add_argument("--model",   "-m", default="base",
                        choices=["tiny", "base", "small", "medium", "large-v2"],
                        help="Whisper model size (default: base)")
    parser.add_argument("--phase",   "-ph", type=int, default=0,
                        help="Start from this phase (0=all, 1=skip input, 2=skip analysis, etc.)")
    parser.add_argument("--no-subtitles", action="store_true", help="Skip subtitle burn-in in Phase 4")
    args = parser.parse_args()

    print(f"""
+==========================================================╗
|        [STUDIO]  AGENTIC VIDEO STUDIO — PIPELINE START         |
+==========================================================╣
|  Project : {args.project:<46} |
|  Brief   : {args.brief[:46]:<46} |
|  Model   : {args.model:<46} |
+==========================================================╝
""")

    start_phase = args.phase

    if start_phase <= 0:
        if not args.input:
            print("[ERROR] --input required for Phase 0")
            sys.exit(1)
        run("phase0_input_handler.py", args.input, "--project", args.project)

    if start_phase <= 1:
        run("phase1_analyser.py", args.project, "--model", args.model)

    if start_phase <= 2:
        run("phase2_director.py", args.project, "--brief", args.brief)

    if start_phase <= 3:
        run("phase3_broll_sourcer.py", args.project)

    if start_phase <= 4:
        extra = ["--skip-subtitles"] if args.no_subtitles else []
        run("phase4_editor.py", args.project, *extra)

    print(f"""
+==========================================================╗
|  [OK]  PIPELINE COMPLETE                                   |
|  Renders : agentic-video-studio/renders/{args.project:<17} |
|  Review  : agentic-video-studio/reviews/{args.project}_review.json |
+==========================================================╝
""")

if __name__ == "__main__":
    main()
