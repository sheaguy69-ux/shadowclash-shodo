"""Prepare review-only FX cutouts and a comparison sheet; never touches runtime assets."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
RAW = ROOT / "raw"
NAMES = [
    ("blade-tail-white", "01  LONG WHITE TRAIL"),
    ("blade-tail-yellow", "02  LONG YELLOW TRAIL"),
    ("twin-blade-trails", "03  TWIN-BLADE TRAILS"),
    ("brush-slice", "04  SHODO SLICE HIT"),
    ("blade-clash", "05  BLADE CLASH"),
    ("claw-rake", "06  THREE-CLAW RAKE"),
    ("punch-light", "07  LIGHT PUNCH HIT"),
    ("punch-heavy", "08  HEAVY PUNCH HIT"),
    ("staff-impact", "09  STAFF IMPACT"),
]

for stem, _ in NAMES + [("kama-hook-trail", "10  KAMA HOOK TRAIL")]:
    im = Image.open(RAW / f"{stem}.png").convert("RGBA")
    # Clean faint generated halos for a more solid candidate, preserving the raw.
    a = im.getchannel("A").point(lambda v: 0 if v < 32 else min(255, round((v - 32) * 255 / 150)))
    im.putalpha(a)
    bbox = a.point(lambda v: 255 if v > 12 else 0).getbbox()
    if not bbox:
        raise ValueError(f"Empty alpha: {stem}")
    pad = 25
    im.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad),
             min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad))).save(ROOT / f"{stem}.png")

font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
title_font = ImageFont.truetype(font_path, 29)
small_font = ImageFont.truetype(font_path, 19)
W, H = 1560, 1665
sheet = Image.new("RGB", (W, H), "#151916")
d = ImageDraw.Draw(sheet)
d.text((42, 28), "SHADOW CLASH  /  COMBAT FX CONCEPTS", font=title_font, fill="#f5f0df")
d.text((42, 68), "White • yellow • shodo brush     /     review only — no game installation", font=small_font, fill="#a8b3a5")
tile_w, tile_h, gap = 475, 485, 26
for i, (stem, label) in enumerate(NAMES):
    col, row = i % 3, i // 3
    x, y = 42 + col * (tile_w + gap), 125 + row * (tile_h + gap)
    d.rounded_rectangle((x, y, x + tile_w, y + tile_h), radius=15, fill="#242a25", outline="#5b665a", width=2)
    d.text((x + 18, y + 16), label, font=small_font, fill="#f2e6cc")
    im = Image.open(ROOT / f"{stem}.png").convert("RGBA")
    im.thumbnail((tile_w - 35, tile_h - 95), Image.Resampling.LANCZOS)
    sheet.paste(im, (x + (tile_w - im.width) // 2, y + 60 + (tile_h - 95 - im.height) // 2), im)

sheet.save(ROOT / "contact-sheet.jpg", quality=94)

before = Image.open(RAW / "kael-source-frame.png").convert("RGB").crop((12, 150, 238, 590))
after = Image.open(RAW / "kael-recolor-white.png").convert("RGB").crop((45, 470, 680, 1580))
pair = Image.new("RGB", (1000, 680), "#151916")
pd = ImageDraw.Draw(pair)
pd.text((32, 22), "BAKED FX RECOLOR STUDY  /  original and white concept", font=title_font, fill="#f5f0df")
for n, (label, src) in enumerate((("ORIGINAL", before), ("WHITE CONCEPT", after))):
    x = 32 + n * 490
    pd.rounded_rectangle((x, 85, x + 455, 660), radius=12, fill="#242a25", outline="#5b665a", width=2)
    pd.text((x + 15, 100), label, font=small_font, fill="#f2e6cc")
    src.thumbnail((440, 515), Image.Resampling.LANCZOS)
    pair.paste(src, (x + (455 - src.width) // 2, 137 + (515 - src.height) // 2))
pair.save(ROOT / "kael-before-after.jpg", quality=94)

# A direction diagram makes the tail rule explicit; it is not an in-game animation.
guide = Image.new("RGB", (1560, 520), "#151916")
g = ImageDraw.Draw(guide)
g.text((42, 22), "BLADE-DIRECTION STUDY  /  tail sits behind the traveling tip", font=title_font, fill="#f5f0df")
g.text((42, 65), "The finished trail is fitted to measured blade-root and blade-tip positions for each move.", font=small_font, fill="#a8b3a5")
import math
for i, deg in enumerate((160, 120, 80, 40)):
    x = 42 + i * 380
    y = 125
    g.rounded_rectangle((x, y, x + 350, y + 350), radius=15, fill="#242a25", outline="#5b665a", width=2)
    cx, cy = x + 175, y + 300
    path = [(cx + round(160 * math.cos(math.radians(a))),
             cy - round(160 * math.sin(math.radians(a)))) for a in range(160, 39, -2)]
    g.line(path, fill="#7d8a7e", width=4, joint="curve")
    if i:
        tail = [(cx + round(160 * math.cos(math.radians(a))),
                 cy - round(160 * math.sin(math.radians(a)))) for a in range(160, deg - 1, -2)]
        g.line(tail, fill="#f7c957", width=22 + 4 * i, joint="curve")
    r = math.radians(deg)
    tip = (cx + int(160 * math.cos(r)), cy - int(160 * math.sin(r)))
    g.line((cx, cy, *tip), fill="#f8f4e9", width=8)
    g.ellipse((tip[0]-10, tip[1]-10, tip[0]+10, tip[1]+10), fill="#f7c957")
    g.text((x + 20, y + 18), f"Frame {i+1}: tip travels forward", font=small_font, fill="#f2e6cc")
guide.save(ROOT / "direction-study.png")
