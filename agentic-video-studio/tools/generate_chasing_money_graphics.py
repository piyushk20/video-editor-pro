#!/usr/bin/env python3
"""
Generate bold, high-contrast, large 9:16 motion graphic cards for:
'Stop Chasing Money: How to Align Your Daily Habits' (Mel Robbins & Morgan Housel)
All cards sit strictly in the upper safe zone (y: 130–550), never covering speaker faces.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = Path("agentic-video-studio/graphics/stop_chasing_money")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Standard full HD vertical canvas
CANVAS_W = 1080
CANVAS_H = 1920

# Card dimensions
CARD_W = 960
CARD_H = 400
CARD_X = 60
CARD_Y = 130  # strictly above y: 656 speaker box

# Colors
BG_COLOR = (14, 18, 30, 245)  # deep solid navy
GOLD_ACCENT = (245, 185, 66)
CYAN_ACCENT = (56, 189, 248)
EMERALD_ACCENT = (52, 211, 153)
WHITE = (255, 255, 255)
MUTED_TEXT = (203, 213, 225)
BORDER_COLOR = (245, 185, 66, 220)


def get_fonts():
    font_paths = [
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\calibrib.ttf",
    ]
    for p in font_paths:
        if Path(p).exists():
            return {
                "tag": ImageFont.truetype(p, 26),
                "title": ImageFont.truetype(p, 48),
                "sub": ImageFont.truetype(p, 30),
                "body": ImageFont.truetype(p, 28),
                "badge": ImageFont.truetype(p, 22),
            }
    f = ImageFont.load_default()
    return {"tag": f, "title": f, "sub": f, "body": f, "badge": f}


def draw_rounded_card(draw: ImageDraw.ImageDraw, x, y, w, h, border_color, fill_color, radius=24, border_w=4):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill_color, outline=border_color, width=border_w)


def create_card_1_intro():
    fonts = get_fonts()
    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Base card
    draw_rounded_card(draw, CARD_X, CARD_Y, CARD_W, CARD_H, GOLD_ACCENT, BG_COLOR)

    # Top category pill badge
    pill_w = 340
    pill_h = 44
    draw.rounded_rectangle([CARD_X + 40, CARD_Y + 36, CARD_X + 40 + pill_w, CARD_Y + 36 + pill_h], radius=12, fill=(245, 185, 66, 50), outline=GOLD_ACCENT, width=2)
    draw.text((CARD_X + 55, CARD_Y + 44), "THE PSYCHOLOGY OF MONEY", font=fonts["tag"], fill=GOLD_ACCENT)

    # Main Headline
    draw.text((CARD_X + 40, CARD_Y + 105), "STOP CHASING MONEY", font=fonts["title"], fill=WHITE)

    # Sub-punchline
    draw.text((CARD_X + 40, CARD_Y + 175), "Why Daily Habits Beat 'Secret Formulas'", font=fonts["sub"], fill=CYAN_ACCENT)

    # Divider bar
    draw.line([(CARD_X + 40, CARD_Y + 230), (CARD_X + CARD_W - 40, CARD_Y + 230)], fill=(71, 85, 105, 180), width=2)

    # Key takeaway footnote
    draw.text((CARD_X + 40, CARD_Y + 255), "Doing well with money is 100% in your control.", font=fonts["body"], fill=MUTED_TEXT)
    draw.text((CARD_X + 40, CARD_Y + 300), "Featuring Morgan Housel & Mel Robbins", font=fonts["tag"], fill=GOLD_ACCENT)

    out = OUTPUT_DIR / "01_intro_title.png"
    img.save(out, "PNG")
    print(f"[OK] Card 1 saved: {out}")


def create_card_2_speakers():
    fonts = get_fonts()
    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw_rounded_card(draw, CARD_X, CARD_Y, CARD_W, CARD_H, CYAN_ACCENT, BG_COLOR)

    # Pill badge
    draw.rounded_rectangle([CARD_X + 40, CARD_Y + 36, CARD_X + 380, CARD_Y + 80], radius=12, fill=(56, 189, 248, 40), outline=CYAN_ACCENT, width=2)
    draw.text((CARD_X + 55, CARD_Y + 44), "THE MEL ROBBINS PODCAST", font=fonts["tag"], fill=CYAN_ACCENT)

    # Host row
    draw.text((CARD_X + 40, CARD_Y + 105), "HOST: MEL ROBBINS", font=fonts["title"], fill=WHITE)
    draw.text((CARD_X + 40, CARD_Y + 170), "Author of 'The 5 Second Rule' & 'The Let Them Theory'", font=fonts["sub"], fill=MUTED_TEXT)

    draw.line([(CARD_X + 40, CARD_Y + 225), (CARD_X + CARD_W - 40, CARD_Y + 225)], fill=(71, 85, 105, 180), width=2)

    # Guest row
    draw.text((CARD_X + 40, CARD_Y + 245), "GUEST: MORGAN HOUSEL", font=fonts["sub"], fill=GOLD_ACCENT)
    draw.text((CARD_X + 40, CARD_Y + 295), "Partner at Collaborative Fund  Author of 'The Psychology of Money'", font=fonts["body"], fill=WHITE)

    out = OUTPUT_DIR / "02_speakers_banner.png"
    img.save(out, "PNG")
    print(f"[OK] Card 2 saved: {out}")


def create_card_3_myth():
    fonts = get_fonts()
    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw_rounded_card(draw, CARD_X, CARD_Y, CARD_W, CARD_H, (239, 68, 68), BG_COLOR)

    # Pill badge
    draw.rounded_rectangle([CARD_X + 40, CARD_Y + 36, CARD_X + 370, CARD_Y + 80], radius=12, fill=(239, 68, 68, 50), outline=(239, 68, 68), width=2)
    draw.text((CARD_X + 55, CARD_Y + 44), "THE BIGGEST WEALTH ILLUSION", font=fonts["tag"], fill=(248, 113, 113))

    # The Myth
    draw.text((CARD_X + 40, CARD_Y + 105), "MYTH: There's A Secret Club", font=fonts["title"], fill=WHITE)
    draw.text((CARD_X + 40, CARD_Y + 170), "\"Who you know, where you went to school, private formulas...\"", font=fonts["body"], fill=(248, 113, 113))

    draw.line([(CARD_X + 40, CARD_Y + 225), (CARD_X + CARD_W - 40, CARD_Y + 225)], fill=(71, 85, 105, 180), width=2)

    # The Truth
    draw.text((CARD_X + 40, CARD_Y + 250), "TRUTH: \"You're Focusing On The Wrong Stuff!\"", font=fonts["sub"], fill=EMERALD_ACCENT)
    draw.text((CARD_X + 40, CARD_Y + 300), "Wealth is built through learnable daily behaviors, not secrets.", font=fonts["body"], fill=MUTED_TEXT)

    out = OUTPUT_DIR / "03_wealth_myth.png"
    img.save(out, "PNG")
    print(f"[OK] Card 3 saved: {out}")


def create_card_4_behaviors():
    fonts = get_fonts()
    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw_rounded_card(draw, CARD_X, CARD_Y, CARD_W, CARD_H, EMERALD_ACCENT, BG_COLOR)

    # Pill badge
    draw.rounded_rectangle([CARD_X + 40, CARD_Y + 30, CARD_X + 430, CARD_Y + 74], radius=12, fill=(52, 211, 153, 40), outline=EMERALD_ACCENT, width=2)
    draw.text((CARD_X + 55, CARD_Y + 38), "THE 3 BEHAVIORS YOU CONTROL", font=fonts["tag"], fill=EMERALD_ACCENT)

    # 3 Bullet Items with checkmarks
    items = [
        ("1. Stop Comparing Yourself", "Focus internally on your own goals, not others' status"),
        ("2. Live Below Your Means", "Save a little bit of every single paycheck"),
        ("3. Consistently Invest The Rest", "Let compound interest do the heavy lifting over decades")
    ]

    y_pos = CARD_Y + 95
    for title, desc in items:
        # Checkmark vector box
        draw.rounded_rectangle([CARD_X + 40, y_pos + 4, CARD_X + 66, y_pos + 30], radius=6, fill=EMERALD_ACCENT)
        # Vector checkmark
        draw.line([(CARD_X + 45, y_pos + 17), (CARD_X + 51, y_pos + 23)], fill=(14, 18, 30), width=3)
        draw.line([(CARD_X + 51, y_pos + 23), (CARD_X + 61, y_pos + 11)], fill=(14, 18, 30), width=3)

        draw.text((CARD_X + 80, y_pos), title, font=fonts["sub"], fill=WHITE)
        draw.text((CARD_X + 80, y_pos + 38), desc, font=fonts["tag"], fill=MUTED_TEXT)
        y_pos += 85

    out = OUTPUT_DIR / "04_daily_behaviors.png"
    img.save(out, "PNG")
    print(f"[OK] Card 4 saved: {out}")


def create_card_5_outro():
    fonts = get_fonts()
    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw_rounded_card(draw, CARD_X, CARD_Y, CARD_W, CARD_H, GOLD_ACCENT, BG_COLOR)

    # Pill badge
    draw.rounded_rectangle([CARD_X + 40, CARD_Y + 36, CARD_X + 320, CARD_Y + 80], radius=12, fill=(245, 185, 66, 40), outline=GOLD_ACCENT, width=2)
    draw.text((CARD_X + 55, CARD_Y + 44), "THE KEY TAKEAWAY", font=fonts["tag"], fill=GOLD_ACCENT)

    # Punchline quote
    draw.text((CARD_X + 40, CARD_Y + 105), "\"IT'S SIMPLE, NOT EASY.\"", font=fonts["title"], fill=WHITE)
    draw.text((CARD_X + 40, CARD_Y + 175), "Align your daily habits to win with money.", font=fonts["sub"], fill=CYAN_ACCENT)

    draw.line([(CARD_X + 40, CARD_Y + 230), (CARD_X + CARD_W - 40, CARD_Y + 230)], fill=(71, 85, 105, 180), width=2)

    # Subscribe badge
    draw.rounded_rectangle([CARD_X + 40, CARD_Y + 260, CARD_X + CARD_W - 40, CARD_Y + 330], radius=16, fill=(245, 185, 66), outline=WHITE, width=2)
    draw.text((CARD_X + 130, CARD_Y + 278), "FOLLOW & SUBSCRIBE FOR MORE WEALTH INSIGHTS", font=fonts["sub"], fill=(14, 18, 30))

    out = OUTPUT_DIR / "05_outro_cta.png"
    img.save(out, "PNG")
    print(f"[OK] Card 5 saved: {out}")


def main():
    print("Generating 9:16 motion graphic cards for Stop Chasing Money...")
    create_card_1_intro()
    create_card_2_speakers()
    create_card_3_myth()
    create_card_4_behaviors()
    create_card_5_outro()
    print("All 5 motion graphic cards generated successfully in safe zone!")


if __name__ == "__main__":
    main()
