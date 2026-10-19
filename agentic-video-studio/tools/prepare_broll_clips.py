#!/usr/bin/env python3
"""
Prepares cinematic 1080p B-roll MP4 clips with smooth Ken Burns motion camera moves,
vignette, and subtle filmic tone for the project.
"""
import os, subprocess, shutil
from pathlib import Path
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
STUDIO_ROOT = Path(__file__).parent.parent
BROLL_DIR = STUDIO_ROOT / "assets" / "broll" / "trap_of_comparison"
BROLL_DIR.mkdir(parents=True, exist_ok=True)

BRAIN_DIR = Path(r"C:\Users\HP\.gemini\antigravity-ide\brain\f4309d60-af72-40c4-97e7-1ff8433da88d")

BROLL_SPECS = [
    {
        "filename": "slot01_wealth_comparison.mp4",
        "img_pattern": "broll_wealth_comparison",
        "duration": 5.0,
        # Gentle slow zoom in towards center-left
        "vf": "zoompan=z='min(zoom+0.0007,1.14)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=150:s=1920x1080:fps=30"
    },
    {
        "filename": "slot02_family_security.mp4",
        "img_pattern": "broll_family_security",
        "duration": 5.0,
        # Gentle slow push in towards warm interior window
        "vf": "zoompan=z='min(zoom+0.0008,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=150:s=1920x1080:fps=30"
    },
    {
        "filename": "slot03_financial_growth.mp4",
        "img_pattern": "broll_financial_tools",
        "duration": 6.0,
        # Gentle slow drift
        "vf": "zoompan=z='min(zoom+0.0006,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=180:s=1920x1080:fps=30"
    },
    {
        "filename": "slot04_measuring_yardstick.mp4",
        "img_pattern": "broll_measuring_yardstick",
        "duration": 6.0,
        # Slow pan across contrasting executives
        "vf": "zoompan=z='min(zoom+0.0006,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=180:s=1920x1080:fps=30"
    },
    {
        "filename": "slot05_social_comparison.mp4",
        "img_pattern": "broll_social_comparison",
        "duration": 5.0,
        # Subtle slow push towards glowing phone
        "vf": "zoompan=z='min(zoom+0.0007,1.14)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=150:s=1920x1080:fps=30"
    }
]

def find_image(pattern: str) -> Path | None:
    for f in BRAIN_DIR.glob(f"{pattern}*.jpg"):
        return f
    for f in BRAIN_DIR.glob(f"{pattern}*.png"):
        return f
    return None

def main():
    print(f"Preparing B-Roll Video Clips in: {BROLL_DIR}")
    rendered = []
    
    for spec in BROLL_SPECS:
        img_path = find_image(spec["img_pattern"])
        if not img_path:
            print(f"  [MISSING] Image matching pattern: {spec['img_pattern']}")
            continue
            
        out_path = BROLL_DIR / spec["filename"]
        print(f"Rendering B-Roll: {spec['filename']} from {img_path.name} (dur={spec['duration']}s)...")
        
        # Add subtle vignette & cinematic color to B-roll
        filter_str = f"{spec['vf']},eq=contrast=1.05:saturation=1.08:brightness=0.01"
        
        cmd = [
            FFMPEG, "-y",
            "-loop", "1",
            "-i", str(img_path),
            "-vf", filter_str,
            "-t", str(spec["duration"]),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            str(out_path)
        ]
        
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            size_mb = out_path.stat().st_size / (1024 * 1024)
            print(f"  [OK] {spec['filename']} ({size_mb:.2f} MB)")
            rendered.append(out_path)
        else:
            print(f"  [ERROR] {res.stderr[-400:]}")
            
    print(f"\nAll {len(rendered)} B-Roll clips prepared and ready for compositing!")

if __name__ == "__main__":
    main()
