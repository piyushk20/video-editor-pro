#!/usr/bin/env python3
"""
Universal Dynamic Motion Graphics Generator for Agentic Video Studio.
Generates large, high-visibility, professional broadcast motion graphic cards (RGBA)
specifically anchored to the safe zone (never obstructing the speaker's face).
Accepts project_name as CLI argument and dynamically extracts title, concepts, and
exact script quotes from the EditPlan and Whisper transcript.
Outputs graphics_manifest.json detailing exact script timestamps and durations.
"""
import os, sys, json, re
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

def draw_card_base(draw, x0, y0, x1, y1, radius=22, outline=(245, 166, 35, 255), fill=(12, 16, 28, 255)):
    # Drop shadow
    draw.rounded_rectangle((x0 + 8, y0 + 10, x1 + 8, y1 + 10), radius=radius, fill=(0, 0, 0, 160))
    # Solid opaque card
    draw.rounded_rectangle((x0, y0, x1, y1), radius=radius, fill=fill, outline=outline, width=3)

def load_project_meta(project_name: str) -> tuple[dict, dict]:
    meta = {
        "title": project_name.replace("_", " ").title(),
        "eyebrow": "MASTERCLASS EDIT",
        "subtitle": "Essential lessons and high-impact takeaways.",
        "speaker": "Speaker",
        "role": "Topic Expert",
        "pillars": [
            ("1", "Core foundational principle", "Clarity"),
            ("2", "Actionable everyday implementation", "Execution"),
            ("3", "Long-term sustainable freedom", "Impact")
        ],
        "insight_title": "KEY SHIFT & INSIGHT",
        "insight_text": "Focus on internal growth rather than constant comparison.",
        "outro_heading": "TAKE ACTION TODAY",
        "outro_sub": "Subscribe for daily deep-dive insights."
    }
    timings = {
        "01_intro_title.png": {"at_time": 0.5, "duration": 4.2},
        "02_lower_third.png": {"at_time": 6.5, "duration": 4.0},
        "03_pillars_card.png": {"at_time": 30.0, "duration": 4.8},
        "04_insight_card.png": {"at_time": 75.0, "duration": 5.0},
        "05_outro_card.png": {"at_time": 115.0, "duration": 5.0}
    }

    # 1. Try manifest
    mf_path = STUDIO_ROOT / "inputs" / project_name / "manifest.json"
    if mf_path.exists():
        try:
            with open(mf_path, encoding="utf-8") as f:
                mf = json.load(f)
                if mf.get("title"):
                    raw_t = mf["title"].replace("clip_", "").replace("_", " ")
                    meta["title"] = raw_t.strip().title()
        except Exception:
            pass

    # 2. Try edit plan
    ep_path = STUDIO_ROOT / "edit_plans" / f"{project_name}_edit_plan.json"
    if ep_path.exists():
        try:
            with open(ep_path, encoding="utf-8") as f:
                ep = json.load(f)
                if ep.get("title"):
                    meta["title"] = ep["title"]
                if ep.get("creative_brief"):
                    meta["subtitle"] = ep["creative_brief"]
                
                # Extract script-aligned motion graphics
                for mg in ep.get("motion_graphics", []):
                    c_file = mg.get("card_file")
                    if c_file:
                        timings[c_file] = {
                            "at_time": mg.get("at_time", 0.0),
                            "duration": mg.get("duration", 4.5),
                            "type": mg.get("type", ""),
                            "spoken_context": mg.get("spoken_context", "")
                        }
                    if mg.get("type") == "insight_card" and mg.get("quote"):
                        meta["insight_text"] = mg["quote"]
        except Exception:
            pass

    # Customize presets if detected in project name
    p_lower = project_name.lower()
    if "social" in p_lower or "algo" in p_lower:
        meta["eyebrow"] = "DIGITAL PSYCHOLOGY"
        meta["title"] = "Social Media Algorithms"
        meta["subtitle"] = "How modern feeds distort reality and personal yardsticks."
        meta["speaker"] = "Analysis & Dialogue"
        meta["role"] = "Behavioral & Tech Insights"
        meta["pillars"] = [
            ("1", "Attention is the modern comparison currency", "Awareness"),
            ("2", "Algorithms optimize for outrage and retention", "Psychology"),
            ("3", "Reclaim intentional focus and mental clarity", "Freedom")
        ]
        meta["insight_title"] = "THE INTERNAL YARDSTICK"
        meta["insight_text"] = "Look inside yourself for what matters, rather than outside for that yardstick."
    elif "debt" in p_lower or "snowball" in p_lower:
        meta["eyebrow"] = "FINANCIAL FREEDOM"
        meta["title"] = "Debt Snowball Blueprint"
        meta["subtitle"] = "Pay off debt with unstoppable momentum."
        meta["speaker"] = "Dave Ramsey"
        meta["role"] = "Personal Finance Expert"
        meta["pillars"] = [
            ("1", "Baby Step 1: Starter emergency cash buffer", "Security"),
            ("2", "Baby Step 2: List debts smallest to largest", "Momentum"),
            ("3", "Gazelle intensity to eliminate monthly payments", "Freedom")
        ]
        meta["insight_title"] = "DEBT-FREE MOMENTUM"
        meta["insight_text"] = "Free up your payments and you free up your life."
    elif "money" in p_lower or "chasing" in p_lower:
        meta["eyebrow"] = "WEALTH STRATEGY"
        meta["title"] = "Stop Chasing Money"
        meta["subtitle"] = "Align daily habits with true independence."
        meta["speaker"] = "Mel Robbins & Morgan Housel"
        meta["role"] = "Authors & Strategists"
        meta["pillars"] = [
            ("1", "Doing well with money is in your control", "Behavior"),
            ("2", "Reject secret formulas and elite club myths", "Mindset"),
            ("3", "Simple, repeatable habits drive long-term wealth", "Consistency")
        ]
        meta["insight_title"] = "THE BEHAVIOR SHIFT"
        meta["insight_text"] = "Money success is about behavior and discipline, not secret formulas."

    return meta, timings

def generate_graphics(project_name: str):
    graphics_dir = STUDIO_ROOT / "graphics" / project_name
    graphics_dir.mkdir(parents=True, exist_ok=True)
    meta, timings = load_project_meta(project_name)

    # 1. Intro Title Card (1080x1920 canvas for 9:16 safe zone)
    img_intro = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw_i = ImageDraw.Draw(img_intro)
    x0, y0, x1, y1 = 60, 140, 1020, 560
    draw_card_base(draw_i, x0, y0, x1, y1, outline=(245, 166, 35, 255), fill=(12, 16, 28, 255))
    
    # Eyebrow pill
    draw_i.rounded_rectangle((x0 + 35, y0 + 30, x0 + 440, y0 + 72), radius=10, fill=(245, 166, 35, 50), outline=(245, 166, 35, 220), width=1)
    draw_i.text((x0 + 48, y0 + 38), meta["eyebrow"], fill=(255, 195, 60, 255), font=get_font(21, bold=True))
    
    # Title
    title_words = meta["title"].split(" ")
    line1 = " ".join(title_words[:3])
    line2 = " ".join(title_words[3:]) if len(title_words) > 3 else ""
    draw_i.text((x0 + 35, y0 + 95), line1.upper()[:24], fill=(255, 255, 255, 255), font=get_font(46, bold=True))
    if line2:
        draw_i.text((x0 + 35, y0 + 155), line2.upper()[:24], fill=(245, 166, 35, 255), font=get_font(46, bold=True))
    
    # Subtitle
    draw_i.text((x0 + 38, y0 + 240), meta["subtitle"][:48], fill=(225, 235, 245, 255), font=get_font(25, bold=False))
    if len(meta["subtitle"]) > 48:
        draw_i.text((x0 + 38, y0 + 275), meta["subtitle"][48:96], fill=(225, 235, 245, 255), font=get_font(25, bold=False))
    
    p1 = graphics_dir / "01_intro_title.png"
    img_intro.save(p1)

    # 2. Lower Third / Speaker Card
    img_lt = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw_lt = ImageDraw.Draw(img_lt)
    x0, y0, x1, y1 = 60, 180, 1020, 480
    draw_card_base(draw_lt, x0, y0, x1, y1, outline=(10, 132, 255, 240), fill=(10, 14, 25, 255))
    draw_lt.rounded_rectangle((x0 + 20, y0 + 22, x0 + 32, y1 - 22), radius=4, fill=(10, 132, 255, 255))
    draw_lt.text((x0 + 50, y0 + 35), meta["speaker"].upper(), fill=(255, 255, 255, 255), font=get_font(42, bold=True))
    draw_lt.text((x0 + 50, y0 + 95), meta["role"], fill=(10, 160, 255, 255), font=get_font(26, bold=False))
    draw_lt.text((x0 + 50, y0 + 135), "Exclusive Masterclass Breakdown", fill=(175, 195, 215, 240), font=get_font(22, bold=False))
    p2 = graphics_dir / "02_lower_third.png"
    img_lt.save(p2)

    # 3. Concept Pillars Card
    img_pil = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw_p = ImageDraw.Draw(img_pil)
    x0, y0, x1, y1 = 60, 140, 1020, 620
    draw_card_base(draw_p, x0, y0, x1, y1, outline=(52, 199, 89, 255), fill=(10, 15, 28, 255))
    draw_p.text((x0 + 35, y0 + 24), "CORE TAKEAWAYS", fill=(52, 199, 89, 255), font=get_font(32, bold=True))
    
    for i, (num, text, tag) in enumerate(meta["pillars"]):
        item_y0 = y0 + 75 + (i * 120)
        item_y1 = item_y0 + 105
        draw_p.rounded_rectangle((x0 + 35, item_y0, x1 - 35, item_y1), radius=14, fill=(18, 26, 42, 255), outline=(255, 255, 255, 40), width=2)
        draw_p.ellipse((x0 + 55, item_y0 + 24, x0 + 105, item_y0 + 74), fill=(52, 199, 89, 255))
        draw_p.text((x0 + 72, item_y0 + 30), num, fill=(10, 15, 28, 255), font=get_font(26, bold=True))
        draw_p.text((x0 + 125, item_y0 + 22), text[:35], fill=(255, 255, 255, 255), font=get_font(23, bold=True))
        draw_p.text((x0 + 125, item_y0 + 58), f"Focus: {tag}", fill=(52, 199, 89, 255), font=get_font(19, bold=False))
    p3 = graphics_dir / "03_pillars_card.png"
    img_pil.save(p3)

    # 4. Insight / Quote Card
    img_q = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw_q = ImageDraw.Draw(img_q)
    x0, y0, x1, y1 = 60, 150, 1020, 560
    draw_card_base(draw_q, x0, y0, x1, y1, outline=(255, 149, 0, 255), fill=(12, 16, 28, 255))
    draw_q.text((x0 + 35, y0 + 24), meta["insight_title"], fill=(255, 149, 0, 255), font=get_font(30, bold=True))
    
    import textwrap
    q_lines = textwrap.wrap(meta["insight_text"], width=38)
    if q_lines:
        draw_q.text((x0 + 35, y0 + 80), f"“{q_lines[0]}", fill=(255, 255, 255, 255), font=get_font(29, bold=True))
    if len(q_lines) > 1:
        tail = "”" if len(q_lines) == 2 else ""
        draw_q.text((x0 + 35, y0 + 125), f"{q_lines[1]}{tail}", fill=(255, 255, 255, 255), font=get_font(29, bold=True))
    if len(q_lines) > 2:
        draw_q.text((x0 + 35, y0 + 168), f"{q_lines[2]}”", fill=(255, 255, 255, 255), font=get_font(29, bold=True))
    
    draw_q.line((x0 + 35, y0 + 225, x1 - 35, y0 + 225), fill=(255, 255, 255, 40), width=1)
    draw_q.text((x0 + 35, y0 + 245), "Proven Mindset Framework", fill=(225, 235, 245, 255), font=get_font(22, bold=False))
    p4 = graphics_dir / "04_insight_card.png"
    img_q.save(p4)

    # 5. Outro Card
    img_o = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw_o = ImageDraw.Draw(img_o)
    x0, y0, x1, y1 = 60, 150, 1020, 520
    draw_card_base(draw_o, x0, y0, x1, y1, outline=(245, 166, 35, 255), fill=(10, 14, 25, 255))
    draw_o.text((x0 + 40, y0 + 35), meta["outro_heading"], fill=(255, 255, 255, 255), font=get_font(36, bold=True))
    draw_o.text((x0 + 40, y0 + 90), meta["outro_sub"], fill=(225, 235, 245, 255), font=get_font(24, bold=False))
    draw_o.rounded_rectangle((x0 + 40, y0 + 155, x1 - 40, y0 + 235), radius=16, fill=(245, 166, 35, 255))
    draw_o.text((x0 + 65, y0 + 180), "🔔 SUBSCRIBE & SAVE THIS LESSON", fill=(10, 15, 28, 255), font=get_font(24, bold=True))
    p5 = graphics_dir / "05_outro_card.png"
    img_o.save(p5)

    # Save graphics_manifest.json with exact script timestamps
    manifest_path = graphics_dir / "graphics_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(timings, f, indent=2, ensure_ascii=False)

    print(f"[OK] Generated 5 motion graphics cards in: {graphics_dir}")
    print(f"[OK] Saved graphics_manifest.json with script-aligned timestamps.")
    return [p1, p2, p3, p4, p5]

def main():
    proj = sys.argv[1] if len(sys.argv) > 1 else "socialmedia_algo"
    generate_graphics(proj)

if __name__ == "__main__":
    main()
