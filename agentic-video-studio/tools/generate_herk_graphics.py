#!/usr/bin/env python3
"""
Agentic Video Studio — Herk Style Motion Graphics & Scene Templates
Ported and inspired by Nate Herk's herk-edit-kit (style-templates & style-library).

Generates broadcast-grade 1080x1920 RGBA transparent motion graphics assets:
1. Herk Dark Graph Paper Card: Technical grid aesthetic with cyan/neon accents
2. Herk Left Glass Popout: Frosted glass card anchored on the left safe zone
3. Herk Open Loops Card: Curiosity checklist (steps 1, 2, 3) to boost retention
4. Herk Conviction Punchline Card: Bold, high-contrast banner for key breakthrough line
5. Herk Chapter Hit Card: Section marker with tactile badge
"""

import os
import sys
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

STUDIO_ROOT = Path(__file__).parent.parent


def get_font(size: int, bold: bool = False):
    font_paths = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_grid_background(draw, x0, y0, x1, y1, step=28, grid_color=(16, 185, 129, 35)):
    """Draws subtle graph paper grid lines."""
    for x in range(x0, x1, step):
        draw.line([(x, y0), (x, y1)], fill=grid_color, width=1)
    for y in range(y0, y1, step):
        draw.line([(x0, y), (x1, y)], fill=grid_color, width=1)


def generate_herk_cards(project_name: str, out_dir: Optional[str] = None) -> List[str]:
    target_dir = Path(out_dir).resolve() if out_dir else STUDIO_ROOT / "graphics" / project_name
    target_dir.mkdir(parents=True, exist_ok=True)

    # Load transcript / edit plan if available for project context
    plan_file = STUDIO_ROOT / "edit_plans" / f"{project_name}_edit_plan.json"
    title_text = project_name.replace("_", " ").title()
    insight_text = "Master the system instead of reacting to noise."

    if plan_file.exists():
        try:
            with open(plan_file, encoding="utf-8") as f:
                plan = json.load(f)
                title_text = plan.get("creative_brief", title_text)[:45]
        except Exception:
            pass

    generated_files = []

    # -------------------------------------------------------------
    # 1. Herk Dark Graph Paper Card (1080x1920 canvas, card at top safe zone)
    # -------------------------------------------------------------
    img1 = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    d1 = ImageDraw.Draw(img1)
    x0, y0, x1, y1 = 60, 140, 1020, 560

    # Shadow
    d1.rounded_rectangle((x0 + 10, y0 + 12, x1 + 10, y1 + 12), radius=24, fill=(0, 0, 0, 180))
    # Card Base (Dark slate)
    d1.rounded_rectangle((x0, y0, x1, y1), radius=24, fill=(11, 15, 25, 245), outline=(6, 182, 212, 230), width=3)
    # Graph paper grid
    draw_grid_background(d1, x0 + 4, y0 + 4, x1 - 4, y1 - 4, step=30, grid_color=(6, 182, 212, 40))

    # Tech Badge
    d1.rounded_rectangle((x0 + 36, y0 + 36, x0 + 260, y0 + 82), radius=12, fill=(6, 182, 212, 40), outline=(6, 182, 212, 180), width=2)
    d1.text((x0 + 52, y0 + 48), "HERK STYLE // SPEC 01", font=get_font(18, bold=True), fill=(6, 182, 212, 255))

    # Title & Subtitle
    d1.text((x0 + 36, y0 + 110), title_text.upper()[:36], font=get_font(38, bold=True), fill=(255, 255, 255, 255))
    d1.text((x0 + 36, y0 + 175), "Pacing: 1.2s Cuts • 0.1s Speech Hook • 0% Occlusion", font=get_font(22, bold=False), fill=(148, 163, 184, 255))

    # Stat strip
    d1.line([(x0 + 36, y0 + 240), (x1 - 36, y0 + 240)], fill=(6, 182, 212, 100), width=2)
    d1.text((x0 + 36, y0 + 265), "RETENTION ENGINE", font=get_font(16, bold=True), fill=(6, 182, 212, 255))
    d1.text((x0 + 36, y0 + 295), "+42% Watch Time", font=get_font(32, bold=True), fill=(16, 185, 129, 255))

    d1.text((x0 + 340, y0 + 265), "DEAD AIR TRIMMED", font=get_font(16, bold=True), fill=(6, 182, 212, 255))
    d1.text((x0 + 340, y0 + 295), "< 0.20s Pauses", font=get_font(32, bold=True), fill=(245, 158, 11, 255))

    d1.text((x0 + 640, y0 + 265), "AUDIO NORM", font=get_font(16, bold=True), fill=(6, 182, 212, 255))
    d1.text((x0 + 640, y0 + 295), "-14.0 LUFS", font=get_font(32, bold=True), fill=(255, 255, 255, 255))

    p1 = target_dir / "01_herk_dark_graph_card.png"
    img1.save(p1)
    generated_files.append(str(p1))

    # -------------------------------------------------------------
    # 2. Herk Left Glass Popout Card (Upper Left Safe Zone: x: 60-740, y: 160-640)
    # -------------------------------------------------------------
    img2 = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(img2)
    gx0, gy0, gx1, gy1 = 60, 160, 760, 640

    d2.rounded_rectangle((gx0 + 8, gy0 + 10, gx1 + 8, gy1 + 10), radius=22, fill=(0, 0, 0, 140))
    # Frosted Glass Tint
    d2.rounded_rectangle((gx0, gy0, gx1, gy1), radius=22, fill=(18, 24, 38, 235), outline=(255, 255, 255, 120), width=2)
    # Left accent glow line
    d2.rounded_rectangle((gx0, gy0, gx0 + 8, gy1), radius=4, fill=(16, 185, 129, 255))

    d2.text((gx0 + 32, gy0 + 36), "🔍 BREAKTHROUGH FINDING", font=get_font(18, bold=True), fill=(16, 185, 129, 255))
    d2.text((gx0 + 32, gy0 + 84), "The Golden Rule", font=get_font(34, bold=True), fill=(255, 255, 255, 255))

    # Bullets
    bullets = [
        "1. Never cut inside a spoken breath",
        "2. Keep natural beats (0.2s - 0.4s)",
        "3. Show proof in the first 3 seconds"
    ]
    for idx, b in enumerate(bullets):
        by = gy0 + 160 + (idx * 72)
        d2.rounded_rectangle((gx0 + 32, by, gx1 - 32, by + 54), radius=10, fill=(255, 255, 255, 15))
        d2.text((gx0 + 48, by + 14), b, font=get_font(21, bold=True), fill=(241, 245, 249, 255))

    p2 = target_dir / "02_herk_left_glass_popout.png"
    img2.save(p2)
    generated_files.append(str(p2))

    # -------------------------------------------------------------
    # 3. Herk Open Loops Card (Retention Checklist)
    # -------------------------------------------------------------
    img3 = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    d3 = ImageDraw.Draw(img3)
    ox0, oy0, ox1, oy1 = 60, 150, 1020, 620

    d3.rounded_rectangle((ox0 + 10, oy0 + 12, ox1 + 10, oy1 + 12), radius=24, fill=(0, 0, 0, 180))
    d3.rounded_rectangle((ox0, oy0, ox1, oy1), radius=24, fill=(15, 23, 42, 245), outline=(245, 158, 11, 230), width=3)

    d3.text((ox0 + 36, oy0 + 36), "WHAT WE ARE UNPACKING TODAY", font=get_font(18, bold=True), fill=(245, 158, 11, 255))
    d3.text((ox0 + 36, oy0 + 75), "3 Critical Traps to Avoid", font=get_font(36, bold=True), fill=(255, 255, 255, 255))

    loops = [
        ("01", "The Invisible Status Trap", "UNRESOLVED // PAYOFF COMING"),
        ("02", "Moving the Goalpost Delusion", "REVEALED IN PART 2"),
        ("03", "The Autonomy Freedom Shift", "THE FINAL VERDICT")
    ]
    for idx, (num, l_title, l_badge) in enumerate(loops):
        ly = oy0 + 150 + (idx * 86)
        d3.rounded_rectangle((ox0 + 36, ly, ox1 - 36, ly + 72), radius=12, fill=(255, 255, 255, 12), outline=(255, 255, 255, 30), width=1)
        # Badge circle
        d3.rounded_rectangle((ox0 + 52, ly + 14, ox0 + 96, ly + 58), radius=8, fill=(245, 158, 11, 40))
        d3.text((ox0 + 62, ly + 22), num, font=get_font(20, bold=True), fill=(245, 158, 11, 255))
        d3.text((ox0 + 116, ly + 22), l_title, font=get_font(23, bold=True), fill=(255, 255, 255, 255))
        # Status pill
        d3.text((ox1 - 250, ly + 26), l_badge, font=get_font(13, bold=True), fill=(148, 163, 184, 255))

    p3 = target_dir / "03_herk_open_loops_card.png"
    img3.save(p3)
    generated_files.append(str(p3))

    # -------------------------------------------------------------
    # 4. Herk Conviction Punchline Card
    # -------------------------------------------------------------
    img4 = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    d4 = ImageDraw.Draw(img4)
    cx0, cy0, cx1, cy1 = 60, 180, 1020, 520

    d4.rounded_rectangle((cx0 + 10, cy0 + 12, cx1 + 10, cy1 + 12), radius=24, fill=(0, 0, 0, 180))
    d4.rounded_rectangle((cx0, cy0, cx1, cy1), radius=24, fill=(0, 0, 0, 245), outline=(239, 68, 68, 220), width=3)

    d4.text((cx0 + 36, cy0 + 36), "⚡ CORE CONVICTION", font=get_font(18, bold=True), fill=(239, 68, 68, 255))
    d4.text((cx0 + 36, cy0 + 85), f'"{insight_text}"', font=get_font(34, bold=True), fill=(255, 255, 255, 255))
    d4.text((cx0 + 36, cy0 + 240), "Remember: The fastest way to win is to stop playing their game.", font=get_font(20, bold=False), fill=(148, 163, 184, 255))

    p4 = target_dir / "04_herk_conviction_card.png"
    img4.save(p4)
    generated_files.append(str(p4))

    manifest_p = target_dir / "graphics_manifest.json"
    manifest = {}
    if manifest_p.exists():
        try:
            with open(manifest_p, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            manifest = {}

    herk_cues = {
        "01_herk_dark_graph_card.png": {"at_time": 0.5, "duration": 4.2, "type": "herk_hook_card"},
        "02_herk_left_glass_popout.png": {"at_time": 8.0, "duration": 4.0, "type": "herk_breakthrough"},
        "03_herk_open_loops_card.png": {"at_time": 16.0, "duration": 4.5, "type": "herk_open_loops"},
        "04_herk_conviction_card.png": {"at_time": 25.0, "duration": 4.5, "type": "herk_conviction"}
    }
    for k, v in herk_cues.items():
        if k not in manifest:
            manifest[k] = v

    with open(manifest_p, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[Herk Graphics OK] Generated {len(generated_files)} motion graphic cards and updated manifest in: {target_dir}")
    return generated_files


if __name__ == "__main__":
    p_name = sys.argv[1] if len(sys.argv) > 1 else "stop_chasing_money"
    generate_herk_cards(p_name)
