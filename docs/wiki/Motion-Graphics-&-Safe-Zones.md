# Motion Graphics & Safe Zones

In 9:16 vertical video production (1080×1920), motion graphics must be prominent and easily readable on mobile devices without ever obstructing the speaker's face.

---

## 📐 9:16 Canvas Safe Zone Architecture

In a standard 1080×1920 vertical canvas with a 16:9 widescreen host, the layout is mathematically budgeted as follows:

```
┌───────────────────────────────────────────┐ y: 0
│                                           │
│  [TOP SAFE ZONE]                          │
│  y: 120 – 600                             │
│  • Intro Title Cards                      │
│  • Speaker Identity Banners               │
│  • Key 3-Step Lists                       │
│  • Quote Cards & Highlight Banners        │
│                                           │
├───────────────────────────────────────────┤ y: 656
│                                           │
│  [SPEAKER BOX (1080 x 608)]               │
│  Host Video Frame (e.g. Dave Ramsey)      │
│  y: 656 – 1264                            │
│  ⚠️ STRICT PROHIBITION ZONE               │
│  (No graphics or text may overlap)        │
│                                           │
├───────────────────────────────────────────┤ y: 1264
│                                           │
│  [LOWER SAFE ZONE]                        │
│  y: 1300 – 1920                           │
│  • Kinetic Word-Level Subtitles (y: 1740) │
│  • Call To Action & Subscribe Outro       │
│                                           │
└───────────────────────────────────────────┘ y: 1920
```

---

## 🎨 Motion Graphics Suite

1. **Episode Title Card (`01_intro_title.png`)**:
   - Time: `0.5s – 4.0s`
   - Position: `x: 60, y: 140`
   - Content: High-contrast title and topic tag with cyan/gold border.
2. **Speaker Identification Banner (`02_lower_third.png`)**:
   - Time: `4.5s – 8.2s`
   - Position: `x: 60, y: 150`
   - Content: Speaker name, show title, and credentials.
3. **Key Checklist / Bullets Card (`03_baby_steps.png`)**:
   - Time: `13.5s – 17.8s`
   - Position: `x: 60, y: 130`
   - Content: 3-point structured summary with vector checkmarks and step numbers.
4. **Impact Quote Callout (`04_rainy_day.png`)**:
   - Time: `48.5s – 53.3s`
   - Position: `x: 60, y: 160`
   - Content: Key philosophical punchline with bold quotes.
5. **Outro Call To Action (`05_outro_card.png`)**:
   - Time: `54.0s – 59.0s`
   - Position: `x: 60, y: 140`
   - Content: Channel branding, subscribe badge, and follow CTA.

---

## 🔤 Kinetic Subtitle Specification

- **Font**: Segoe UI Bold / Inter / Arial Bold
- **Resolution Base**: `PlayResX=1080, PlayResY=1920`
- **Font Size**: `44pt`
- **MarginV**: `180px` (positions text at `y: 1740`, well clear of platform UI overlays)
- **Styling**: Pure White text (`&H00FFFFFF`) with solid dark outline (`&H00101010`), BorderStyle=1, Outline=3, and soft drop shadow.
