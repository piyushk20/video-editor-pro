#!/usr/bin/env python3
"""
Generates large, high-visibility, professional broadcast motion graphic cards (1920x1080 RGBA)
specifically anchored to the LEFT safe zone (x: 60-880) so they NEVER touch or obstruct the speaker's face (which is on the right x: 960-1800).
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

STUDIO_ROOT = Path(__file__).parent.parent
GRAPHICS_DIR = STUDIO_ROOT / "graphics" / "trap_of_comparison"
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

def draw_card_base(draw, x0, y0, x1, y1, radius=22, outline=(245, 166, 35, 255), fill=(12, 16, 28, 255)):
    # Draw drop shadow
    draw.rounded_rectangle((x0 + 8, y0 + 10, x1 + 8, y1 + 10), radius=radius, fill=(0, 0, 0, 160))
    # Draw solid opaque card
    draw.rounded_rectangle((x0, y0, x1, y1), radius=radius, fill=fill, outline=outline, width=3)

def make_intro_title():
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Left safe zone: x from 60 to 880, y from 130 to 530
    x0, y0, x1, y1 = 60, 130, 880, 530
    draw_card_base(draw, x0, y0, x1, y1, outline=(245, 166, 35, 255), fill=(12, 16, 28, 255))
    
    # Eyebrow pill
    draw.rounded_rectangle((x0 + 35, y0 + 30, x0 + 440, y0 + 72), radius=10, fill=(245, 166, 35, 50), outline=(245, 166, 35, 220), width=1)
    draw.text((x0 + 48, y0 + 38), "FINANCIAL MINDSET MASTERCLASS", fill=(255, 195, 60, 255), font=get_font(21, bold=True))
    
    # Headlines
    draw.text((x0 + 35, y0 + 90), "THE TRAP OF", fill=(255, 255, 255, 255), font=get_font(52, bold=True))
    draw.text((x0 + 35, y0 + 155), "COMPARISON", fill=(245, 166, 35, 255), font=get_font(68, bold=True))
    
    # Subtitle
    draw.text((x0 + 38, y0 + 255), "Why measuring success against others", fill=(225, 235, 245, 255), font=get_font(27, bold=False))
    draw.text((x0 + 38, y0 + 295), "destroys true wealth and peace of mind.", fill=(225, 235, 245, 255), font=get_font(27, bold=False))
    
    out_path = GRAPHICS_DIR / "01_intro_title.png"
    img.save(out_path)
    print(f"Generated large left-anchored intro: {out_path}")
    return out_path

def make_lower_third():
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Left anchored at bottom: x: 60 to 860, y: 670 to 865
    x0, y0, x1, y1 = 60, 670, 860, 865
    draw_card_base(draw, x0, y0, x1, y1, outline=(245, 166, 35, 240), fill=(10, 14, 25, 255))
    
    # Vertical gold accent bar
    draw.rounded_rectangle((x0 + 20, y0 + 22, x0 + 32, y1 - 22), radius=4, fill=(245, 166, 35, 255))
    
    # Speaker details
    draw.text((x0 + 50, y0 + 28), "MORGAN HOUSEL", fill=(255, 255, 255, 255), font=get_font(44, bold=True))
    draw.text((x0 + 50, y0 + 88), "Author of 'The Psychology of Money'", fill=(245, 185, 75, 255), font=get_font(27, bold=False))
    draw.text((x0 + 50, y0 + 130), "Former Wall Street Journal Financial Columnist", fill=(175, 195, 215, 240), font=get_font(22, bold=False))
    
    out_path = GRAPHICS_DIR / "02_lower_third.png"
    img.save(out_path)
    print(f"Generated large lower-third: {out_path}")
    return out_path

def make_core_pillars_card():
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Left safe zone: x: 60 to 880, y: 120 to 665
    x0, y0, x1, y1 = 60, 120, 880, 665
    draw_card_base(draw, x0, y0, x1, y1, outline=(10, 132, 255, 255), fill=(10, 15, 28, 255))
    
    draw.text((x0 + 35, y0 + 28), "WHAT PEOPLE ACTUALLY WANT", fill=(10, 160, 255, 255), font=get_font(33, bold=True))
    draw.text((x0 + 35, y0 + 74), "The 3 Non-Negotiable Pillars of True Wealth:", fill=(200, 215, 230, 240), font=get_font(23, bold=False))
    
    pillars = [
        ("1", "Stable housing for myself and my family", "Security"),
        ("2", "A financial cushion to fall back on in emergencies", "Resilience"),
        ("3", "Freedom to spend meaningful time with children", "Independence")
    ]
    
    for i, (num, text, tag) in enumerate(pillars):
        item_y0 = y0 + 120 + (i * 118)
        item_y1 = item_y0 + 98
        draw.rounded_rectangle((x0 + 35, item_y0, x1 - 35, item_y1), radius=14, fill=(18, 26, 42, 255), outline=(255, 255, 255, 40), width=2)
        
        # Check badge
        draw.ellipse((x0 + 55, item_y0 + 24, x0 + 102, item_y0 + 72), fill=(52, 199, 89, 255))
        draw.text((x0 + 68, item_y0 + 30), "✓", fill=(255, 255, 255, 255), font=get_font(28, bold=True))
        
        # Text
        draw.text((x0 + 120, item_y0 + 20), text, fill=(255, 255, 255, 255), font=get_font(24, bold=True))
        draw.text((x0 + 120, item_y0 + 56), f"Core Value: {tag}", fill=(52, 199, 89, 255), font=get_font(20, bold=False))
        
    out_path = GRAPHICS_DIR / "03_pillars_card.png"
    img.save(out_path)
    print(f"Generated large pillars card: {out_path}")
    return out_path

def make_comparison_card():
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Left safe zone: x: 60 to 880, y: 110 to 690 (Never touches speaker face on right)
    x0, y0, x1, y1 = 60, 110, 880, 690
    draw_card_base(draw, x0, y0, x1, y1, outline=(245, 166, 35, 255), fill=(10, 14, 25, 255))
    
    draw.text((x0 + 35, y0 + 28), "THE MONEY MINDSET SHIFT", fill=(255, 215, 90, 255), font=get_font(33, bold=True))
    draw.text((x0 + 35, y0 + 72), "Two fundamentally different ways people relate to money:", fill=(200, 210, 225, 240), font=get_font(21, bold=False))
    
    # Box 1: AS A TOOL (Green)
    bx_y0 = y0 + 115
    bx_y1 = bx_y0 + 190
    draw.rounded_rectangle((x0 + 35, bx_y0, x1 - 35, bx_y1), radius=15, fill=(16, 42, 28, 255), outline=(52, 199, 89, 255), width=2)
    draw.text((x0 + 55, bx_y0 + 20), "1. MONEY AS A TOOL (Freedom)", fill=(52, 199, 89, 255), font=get_font(28, bold=True))
    draw.text((x0 + 55, bx_y0 + 66), "• Used to live a better, calmer, fulfilling life", fill=(240, 255, 245, 255), font=get_font(23, bold=False))
    draw.text((x0 + 55, bx_y0 + 104), "• Control over your daily calendar and peace", fill=(240, 255, 245, 255), font=get_font(23, bold=False))
    draw.text((x0 + 55, bx_y0 + 144), "• Outcome: Permanent autonomy and security", fill=(160, 240, 180, 255), font=get_font(21, bold=True))
    
    # Box 2: AS A YARDSTICK (Red)
    rx_y0 = bx_y1 + 24
    rx_y1 = rx_y0 + 190
    draw.rounded_rectangle((x0 + 35, rx_y0, x1 - 35, rx_y1), radius=15, fill=(45, 18, 24, 255), outline=(255, 69, 58, 255), width=2)
    draw.text((x0 + 55, rx_y0 + 20), "2. MONEY AS A YARDSTICK (The Trap)", fill=(255, 69, 58, 255), font=get_font(28, bold=True))
    draw.text((x0 + 55, rx_y0 + 66), "• Measuring yourself against other people", fill=(255, 235, 235, 255), font=get_font(23, bold=False))
    draw.text((x0 + 55, rx_y0 + 104), "• Always moving the goalpost; comparison has no end", fill=(255, 235, 235, 255), font=get_font(23, bold=False))
    draw.text((x0 + 55, rx_y0 + 144), "• Outcome: Perpetual anxiety and insecurity", fill=(255, 160, 160, 255), font=get_font(21, bold=True))
    
    out_path = GRAPHICS_DIR / "04_comparison_card.png"
    img.save(out_path)
    print(f"Generated large comparison card: {out_path}")
    return out_path

def make_quote_card():
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Left safe zone: x: 60 to 880, y: 150 to 620
    x0, y0, x1, y1 = 60, 150, 880, 620
    draw_card_base(draw, x0, y0, x1, y1, outline=(245, 166, 35, 255), fill=(12, 16, 28, 255))
    
    # Big quotation mark
    draw.text((x0 + 35, y0 + 15), "“", fill=(245, 166, 35, 220), font=get_font(88, bold=True))
    
    # Quote text
    draw.text((x0 + 110, y0 + 50), "Not 'how big is my house'...", fill=(255, 255, 255, 255), font=get_font(38, bold=True))
    draw.text((x0 + 110, y0 + 110), "but 'how big relative to that guy?'", fill=(255, 195, 75, 255), font=get_font(40, bold=True))
    
    draw.line((x0 + 45, y0 + 205, x1 - 45, y0 + 205), fill=(255, 255, 255, 40), width=1)
    
    draw.text((x0 + 45, y0 + 230), "THE SOCIAL COMPARISON PARADOX", fill=(245, 166, 35, 255), font=get_font(23, bold=True))
    draw.text((x0 + 45, y0 + 275), "Status is a relative game with no winner.", fill=(220, 230, 245, 255), font=get_font(25, bold=False))
    draw.text((x0 + 45, y0 + 315), "True wealth is playing your own game.", fill=(220, 230, 245, 255), font=get_font(25, bold=False))
    draw.text((x0 + 45, y0 + 375), "— Morgan Housel", fill=(160, 180, 205, 230), font=get_font(23, bold=True))
    
    out_path = GRAPHICS_DIR / "05_quote_card.png"
    img.save(out_path)
    print(f"Generated large quote card: {out_path}")
    return out_path

def make_outro_card():
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Left safe zone: x: 60 to 880, y: 150 to 590
    x0, y0, x1, y1 = 60, 150, 880, 590
    draw_card_base(draw, x0, y0, x1, y1, outline=(245, 166, 35, 255), fill=(10, 14, 25, 255))
    
    draw.text((x0 + 40, y0 + 40), "DEFINE SUCCESS ON YOUR TERMS", fill=(255, 255, 255, 255), font=get_font(40, bold=True))
    draw.text((x0 + 40, y0 + 110), "Stop running someone else's race.", fill=(225, 235, 245, 255), font=get_font(27, bold=False))
    draw.text((x0 + 40, y0 + 150), "Build freedom, independence, and peace of mind.", fill=(225, 235, 245, 255), font=get_font(27, bold=False))
    
    # Big CTA Button
    draw.rounded_rectangle((x0 + 40, y0 + 240, x0 + 620, y0 + 315), radius=16, fill=(245, 166, 35, 255))
    draw.text((x0 + 70, y0 + 260), "🔔 SUBSCRIBE FOR DAILY WEALTH WISDOM", fill=(10, 15, 28, 255), font=get_font(25, bold=True))
    
    out_path = GRAPHICS_DIR / "06_outro_card.png"
    img.save(out_path)
    print(f"Generated large outro card: {out_path}")
    return out_path

def main():
    print("Generating redesigned large, left-anchored motion graphic cards...")
    make_intro_title()
    make_lower_third()
    make_core_pillars_card()
    make_comparison_card()
    make_quote_card()
    make_outro_card()
    print("All 6 cards regenerated and placed safely on left side (x: 60-880) completely away from speaker's face!")

if __name__ == "__main__":
    main()
