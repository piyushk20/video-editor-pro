#!/usr/bin/env python3
"""
Generates large, high-visibility, professional 9:16 vertical motion graphic cards (1080x1920 RGBA)
for the debt_snowball project.
Cards are anchored in the upper zone (y: 130-620) so they NEVER touch or obstruct Dave Ramsey's face/body (which sits centered at y: 650-1260).
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

STUDIO_ROOT = Path(__file__).parent.parent
GRAPHICS_DIR = STUDIO_ROOT / "graphics" / "debt_snowball"
GRAPHICS_DIR.mkdir(parents=True, exist_ok=True)

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

def draw_card_base(draw, x0, y0, x1, y1, radius=24, outline=(0, 185, 255, 255), fill=(10, 18, 32, 255)):
    # Drop shadow
    draw.rounded_rectangle((x0 + 8, y0 + 10, x1 + 8, y1 + 10), radius=radius, fill=(0, 0, 0, 180))
    # Main card
    draw.rounded_rectangle((x0, y0, x1, y1), radius=radius, fill=fill, outline=outline, width=3)

def make_intro_title():
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Upper safe zone: x from 60 to 1020 (width 960), y from 140 to 580
    x0, y0, x1, y1 = 60, 140, 1020, 580
    draw_card_base(draw, x0, y0, x1, y1, outline=(0, 195, 255, 255), fill=(10, 20, 36, 255))
    
    # Ramsey tag pill
    draw.rounded_rectangle((x0 + 40, y0 + 35, x0 + 480, y0 + 78), radius=12, fill=(0, 195, 255, 45), outline=(0, 195, 255, 220), width=1)
    draw.text((x0 + 55, y0 + 43), "THE RAMSEY SHOW • FINANCIAL PEACE", fill=(0, 220, 255, 255), font=get_font(21, bold=True))
    
    # Headlines
    draw.text((x0 + 40, y0 + 100), "DEBT FREE IN 24 MONTHS", fill=(255, 255, 255, 255), font=get_font(52, bold=True))
    draw.text((x0 + 40, y0 + 165), "THE DEBT SNOWBALL METHOD", fill=(255, 195, 60, 255), font=get_font(42, bold=True))
    
    # Subtitle
    draw.text((x0 + 42, y0 + 245), "How thousands of families eliminate all debt", fill=(225, 235, 245, 255), font=get_font(28, bold=False))
    draw.text((x0 + 42, y0 + 285), "with relentless gazelle intensity.", fill=(225, 235, 245, 255), font=get_font(28, bold=False))
    
    # Speaker tag
    draw.text((x0 + 42, y0 + 360), "🎙️ DAVE RAMSEY ADVICE", fill=(0, 195, 255, 255), font=get_font(24, bold=True))
    
    out_path = GRAPHICS_DIR / "01_intro_title.png"
    img.save(out_path)
    print(f"Generated 9:16 intro: {out_path}")
    return out_path

def make_lower_third():
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Upper safe zone: x from 60 to 1020, y from 180 to 470
    x0, y0, x1, y1 = 60, 180, 1020, 480
    draw_card_base(draw, x0, y0, x1, y1, outline=(255, 195, 60, 255), fill=(12, 18, 30, 255))
    
    # Vertical gold accent bar
    draw.rounded_rectangle((x0 + 25, y0 + 25, x0 + 38, y1 - 25), radius=5, fill=(255, 195, 60, 255))
    
    draw.text((x0 + 60, y0 + 35), "DAVE RAMSEY", fill=(255, 255, 255, 255), font=get_font(52, bold=True))
    draw.text((x0 + 60, y0 + 105), "Host of The Ramsey Show | 8x Best-Selling Author", fill=(255, 195, 60, 255), font=get_font(30, bold=False))
    draw.text((x0 + 60, y0 + 155), "Creator of The 7 Baby Steps & Financial Peace University", fill=(185, 205, 225, 240), font=get_font(24, bold=False))
    draw.text((x0 + 60, y0 + 210), "Over 20 Million Listeners Weekly", fill=(0, 215, 255, 255), font=get_font(22, bold=True))
    
    out_path = GRAPHICS_DIR / "02_lower_third.png"
    img.save(out_path)
    print(f"Generated 9:16 speaker card: {out_path}")
    return out_path

def make_baby_steps_card():
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Upper safe zone: x: 60 to 1020, y: 120 to 640 (Height: 520)
    x0, y0, x1, y1 = 60, 120, 1020, 640
    draw_card_base(draw, x0, y0, x1, y1, outline=(52, 199, 89, 255), fill=(10, 22, 34, 255))
    
    draw.text((x0 + 40, y0 + 25), "THE 3 PROVEN BABY STEPS", fill=(52, 220, 100, 255), font=get_font(34, bold=True))
    draw.text((x0 + 40, y0 + 68), "Follow this exact sequence to win with money:", fill=(200, 215, 230, 240), font=get_font(22, bold=False))
    
    steps = [
        ("BABY STEP 1", "$1,000 Starter Emergency Fund Quick", "Stop new debt immediately"),
        ("BABY STEP 2", "Pay Off All Debt Except The House", "Sell the boat, take an extra job"),
        ("BABY STEP 3", "3 to 6 Months Fully Funded Safety Cushion", "The permanent buffer: You are the bank")
    ]
    
    for i, (tag, title, sub) in enumerate(steps):
        sy0 = y0 + 110 + (i * 125)
        sy1 = sy0 + 105
        draw.rounded_rectangle((x0 + 35, sy0, x1 - 35, sy1), radius=14, fill=(16, 32, 50, 255), outline=(255, 255, 255, 35), width=2)
        
        # Check badge with crisp vector checkmark
        cx, cy = x0 + 80, sy0 + 49
        draw.ellipse((cx - 24, cy - 24, cx + 24, cy + 24), fill=(52, 199, 89, 255))
        draw.line([(cx - 10, cy), (cx - 2, cy + 9), (cx + 12, cy - 9)], fill=(255, 255, 255, 255), width=4)
        
        draw.text((x0 + 125, sy0 + 18), f"{tag}: {title}", fill=(255, 255, 255, 255), font=get_font(24, bold=True))
        draw.text((x0 + 125, sy0 + 56), sub, fill=(255, 195, 60, 255), font=get_font(20, bold=False))
        
    out_path = GRAPHICS_DIR / "03_baby_steps.png"
    img.save(out_path)
    print(f"Generated 9:16 baby steps card: {out_path}")
    return out_path

def make_rainy_day_card():
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Upper safe zone: x: 60 to 1020, y: 140 to 600
    x0, y0, x1, y1 = 60, 140, 1020, 600
    draw_card_base(draw, x0, y0, x1, y1, outline=(255, 69, 58, 255), fill=(16, 18, 30, 255))
    
    draw.text((x0 + 40, y0 + 30), "WHY GRANDMA'S RAINY DAY FUND?", fill=(255, 195, 60, 255), font=get_font(32, bold=True))
    
    # Giant quote
    draw.text((x0 + 40, y0 + 85), "“IT'S GONNA RAIN!”", fill=(255, 69, 58, 255), font=get_font(60, bold=True))
    
    draw.line((x0 + 40, y0 + 180, x1 - 40, y0 + 180), fill=(255, 255, 255, 40), width=1)
    
    draw.text((x0 + 40, y0 + 205), "Be positive? Dave: 'I am positive — it's gonna rain.'", fill=(240, 245, 255, 255), font=get_font(26, bold=True))
    draw.text((x0 + 40, y0 + 250), "When you have $20,000 cash in the bank buffer,", fill=(220, 230, 245, 255), font=get_font(26, bold=False))
    draw.text((x0 + 40, y0 + 290), "a medical emergency or job layoff is an inconvenience,", fill=(220, 230, 245, 255), font=get_font(26, bold=False))
    draw.text((x0 + 40, y0 + 330), "NOT a family financial catastrophe.", fill=(52, 199, 89, 255), font=get_font(26, bold=True))
    draw.text((x0 + 40, y0 + 390), "— Dave Ramsey", fill=(175, 195, 215, 230), font=get_font(22, bold=True))
    
    out_path = GRAPHICS_DIR / "04_rainy_day.png"
    img.save(out_path)
    print(f"Generated 9:16 rainy day card: {out_path}")
    return out_path

def make_outro_card():
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Upper safe zone: x: 60 to 1020, y: 150 to 580
    x0, y0, x1, y1 = 60, 150, 1020, 580
    draw_card_base(draw, x0, y0, x1, y1, outline=(255, 195, 60, 255), fill=(10, 18, 32, 255))
    
    draw.text((x0 + 45, y0 + 40), "TAKE CONTROL OF YOUR MONEY", fill=(255, 255, 255, 255), font=get_font(44, bold=True))
    draw.text((x0 + 45, y0 + 105), "“Live like no one else,", fill=(255, 195, 60, 255), font=get_font(34, bold=True))
    draw.text((x0 + 45, y0 + 155), "so later you can live like no one else.”", fill=(255, 195, 60, 255), font=get_font(34, bold=True))
    draw.text((x0 + 45, y0 + 220), "Start your debt snowball today and breathe easy.", fill=(225, 235, 245, 255), font=get_font(26, bold=False))
    
    # CTA button
    draw.rounded_rectangle((x0 + 45, y0 + 290, x0 + 720, y0 + 365), radius=16, fill=(255, 195, 60, 255))
    draw.text((x0 + 75, y0 + 310), "🔔 SUBSCRIBE FOR DAILY FINANCIAL FREEDOM", fill=(10, 18, 32, 255), font=get_font(25, bold=True))
    
    out_path = GRAPHICS_DIR / "05_outro_card.png"
    img.save(out_path)
    print(f"Generated 9:16 outro card: {out_path}")
    return out_path

def main():
    print("Generating dedicated 9:16 vertical motion graphic cards for debt_snowball...")
    make_intro_title()
    make_lower_third()
    make_baby_steps_card()
    make_rainy_day_card()
    make_outro_card()
    print("All 5 cards generated in:", GRAPHICS_DIR)

if __name__ == "__main__":
    main()
