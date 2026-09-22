#!/usr/bin/env python3
"""TRAILER B — "HE NEVER LOOKED UP" · Kael vs the Executioner · hard 30s.

Every fighter frame is a SHIPPED sprite cell. Nothing is generated, so nothing can
drift: the horns, the blade count and the palette are correct by construction because
this IS the source art. Background is the game's own warrant stage (his execution
ground). Cost: $0.

ponytail: PIL compositing + one ffmpeg encode. No video model, no compositor.
Ceiling: cuts + push-ins only, no per-limb motion. Upgrade path is HyperFrames if
the trailer ever needs real choreography beyond the sprite cells.

Usage: python3 tools/trailer/build_trailer_b.py [--fast]
"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SPR = ROOT / "web/assets/sprites"
OUT = Path("/private/tmp/claude-501/-Users-anthonyguy-SHADOWCLASH-RECOVERED"
           "/ca56c915-b305-4845-a1ac-6d66942b0b2d/scratchpad/trailerB")
W, H, FPS = 1920, 1080, 24
TOTAL = 30 * FPS                      # 720 frames, hard 30s

# ---------------------------------------------------------------- assets
def load(name):
    d = json.load(open(SPR / f"{name}.json"))
    return Image.open(SPR / f"{name}.png").convert("RGBA"), d["frames"], d["frameW"], d["frameH"]

SHEETS = {n: load(n) for n in ("kael", "executioner")}
BG = Image.open(ROOT / "web/assets/stages/warrant-far.png").convert("RGB")

_cache = {}
def cell(fighter, slot):
    """One sprite cell, alpha-cropped to its ink. Sheets are authored facing LEFT."""
    key = (fighter, slot)
    if key in _cache:
        return _cache[key]
    im, fr, fw, fh = SHEETS[fighter]
    if slot not in fr:
        raise KeyError(f"{fighter}.{slot} does not exist in the sheet")
    i = fr[slot]
    c = im.crop((i * fw, 0, i * fw + fw, fh))
    c = c.crop(c.getbbox())
    _cache[key] = c
    return c

F = "/System/Library/Fonts/Avenir Next Condensed.ttc"
def font(sz, bold=True):
    return ImageFont.truetype(F, sz, index=1 if bold else 0)

# ---------------------------------------------------------------- helpers
def ease(t):                       # smootherstep, for push-ins
    t = max(0.0, min(1.0, t))
    return t * t * t * (t * (t * 6 - 15) + 10)

def backdrop(zoom, cx, cy, dim=0.0):
    """Crop the stage for a push-in. zoom 1.0 = full plate; cx/cy in 0..1."""
    bw, bh = BG.size
    cw, ch = bw / zoom, bh / zoom
    x = (bw - cw) * cx
    y = (bh - ch) * cy
    f = BG.crop((int(x), int(y), int(x + cw), int(y + ch))).resize((W, H), Image.LANCZOS)
    if dim:
        f = Image.blend(f, Image.new("RGB", (W, H), (8, 6, 14)), dim)
    return f.convert("RGBA")

def put(frame, fighter, slot, *, x, y, h, flip=False):
    """Paste a cell scaled to h px tall, anchored at (x, y) = feet centre."""
    c = cell(fighter, slot)
    s = h / c.height
    c = c.resize((max(1, int(c.width * s)), int(h)), Image.LANCZOS)
    if flip:
        c = c.transpose(Image.FLIP_LEFT_RIGHT)
    frame.alpha_composite(c, (int(x - c.width / 2), int(y - c.height)))

def text(frame, s, *, size=44, xy=(90, 908), fill=(238, 232, 222), track=6, anchor="ls"):
    d = ImageDraw.Draw(frame)
    f = font(size)
    x, y = xy
    for ch in s:                                    # manual tracking
        d.text((x, y), ch, font=f, fill=fill, anchor=anchor,
               stroke_width=3, stroke_fill=(0, 0, 0))
        x += d.textlength(ch, font=f) + track

def bars(frame):                                    # 2.39:1 letterbox
    d = ImageDraw.Draw(frame)
    b = int((H - W / 2.39) / 2)
    d.rectangle([0, 0, W, b], fill=(0, 0, 0))
    d.rectangle([0, H - b, W, H], fill=(0, 0, 0))

GROUND = 880                                        # feet line

# ---------------------------------------------------------------- the cut
# Each entry: (start_frame, end_frame, render fn). Hard cuts only — house rule.
def seg_approach(f, t, n):                          # 0:00–0:04  wide, Kael enters
    fr = backdrop(1.0 + 0.05 * ease(t), 0.5, 0.55, dim=0.35)
    walk = ["run_clean1", "run_clean2", "run_clean3", "run_clean4",
            "run_clean5", "run_clean6", "run_clean7", "run_clean8"]
    put(fr, "kael", walk[(n // 4) % 8], x=180 + 620 * t, y=GROUND, h=210, flip=True)
    text(fr, "THE LAST STUDENT OF A SCHOOL", size=34, xy=(90, 852))
    text(fr, "THAT NO LONGER EXISTS", size=34, xy=(90, 908))
    return fr

def seg_challenge(f, t, n):                         # 0:04–0:08  the dual draw
    fr = backdrop(1.55 + 0.10 * ease(t), 0.42, 0.62, dim=0.42)
    draw = ["idle", "kdual1", "kdual2", "kdual3", "kdual4", "kdual5", "kdual6"]
    i = min(len(draw) - 1, int(t * 9))
    put(fr, "kael", draw[i], x=760, y=GROUND, h=560, flip=True)
    text(fr, "HE CAME DOWN CHASING SOMEONE", size=40, xy=(90, 908))
    return fr

def seg_noanswer(f, t, n):                          # 0:08–0:12  he does not react
    fr = backdrop(1.5 + 0.85 * ease(t), 0.58, 0.60, dim=0.5)
    put(fr, "executioner", "idle" if n % 48 < 30 else "idle2",
        x=1120, y=GROUND, h=520 + 380 * ease(t))
    if t > 0.45:
        text(fr, "THE MASK STOPPED COMING OFF", size=36, xy=(90, 852))
        text(fr, "BETWEEN JOBS", size=36, xy=(90, 908))
    return fr

def exchange(kael_slots, exec_slots, word):
    """2s: Kael commits (1s), the Executioner answers (1s). Never initiates."""
    def render(f, t, n):
        fr = backdrop(1.9, 0.5, 0.62, dim=0.45)
        if t < 0.5:                                  # Kael's half
            i = min(len(kael_slots) - 1, int(t * 2 * len(kael_slots)))
            put(fr, "kael", kael_slots[i], x=610, y=GROUND, h=640, flip=True)
            put(fr, "executioner", "idle", x=1360, y=GROUND, h=660)
        else:                                        # the counter
            i = min(len(exec_slots) - 1, int((t - 0.5) * 2 * len(exec_slots)))
            put(fr, "kael", kael_slots[-1], x=610, y=GROUND, h=640, flip=True)
            put(fr, "executioner", exec_slots[i], x=1360, y=GROUND, h=660)
        text(fr, word, size=64, xy=(90, 908))
        return fr
    return render

def seg_fang(f, t, n):                              # 0:20–0:26  the invulnerable one
    fr = backdrop(2.1, 0.5, 0.58, dim=0.5)
    if t < 0.62:                                     # slow-mo rise (the only slomo)
        rise = ["krise1", "krise2", "krise3", "krise4", "krise5", "krise6"]
        i = min(5, int(t / 0.62 * 6))
        put(fr, "kael", rise[i], x=760, y=GROUND - 250 * ease(t / 0.62), h=660, flip=True)
        # he is ALREADY gone — empty air where the counter should be
        if t > 0.30:
            text(fr, "HE IS ALREADY GONE", size=44, xy=(90, 908))
    else:                                            # lands off balance, back open
        u = (t - 0.62) / 0.38
        put(fr, "kael", ["hurt", "kneel", "kneel"][min(2, int(u * 3))],
            x=760, y=GROUND, h=620, flip=True)
    return fr

def seg_execution(f, t, n):                         # 0:26–0:30
    if t > 0.62:                                     # black, then the card
        fr = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        if t > 0.72:
            d = ImageDraw.Draw(fr)
            d.text((W // 2, H // 2 - 30), "SHADOWCLASH", font=font(118),
                   fill=(240, 236, 228), anchor="mm")
            if t > 0.86:
                d.text((W // 2, H // 2 + 70), "NONE OF THOSE MEETINGS WERE FAIR",
                       font=font(30), fill=(150, 146, 156), anchor="mm")
        return fr
    fr = backdrop(2.4, 0.55, 0.55, dim=0.55)
    iai = ["xiai1", "xiai2", "xiai3", "xiai4", "xiai5"]
    i = min(4, int(t / 0.62 * 5))
    put(fr, "executioner", iai[i], x=1150, y=GROUND, h=760)
    if t < 0.18:
        text(fr, "HE LOOKS AT HIM", size=44, xy=(90, 908))
    return fr

CUT = [
    (0,   96,  seg_approach),
    (96,  192, seg_challenge),
    (192, 288, seg_noanswer),
    (288, 336, exchange(["kcyc1", "kcyc2", "kcyc3", "kcyc4", "kcyc5", "kcyc6"],
                        ["block", "block2", "xblkguard"], "HE")),
    (336, 384, exchange(["kscis1", "kscis2", "kscis3", "kscis4", "kscis5", "kscis6"],
                        ["xslip1", "xslip2", "xslip3", "xslip4", "xslip5", "xslip6"], "IS")),
    (384, 432, exchange(["ktrav1", "ktrav2", "ktrav3", "ktrav4", "ktrav5", "ktrav6"],
                        ["xreprisal1", "xreprisal2", "xreprisal3",
                         "xreprisal4", "xreprisal5", "xreprisal6"], "NOT")),
    (432, 480, exchange(["xparry1", "xparry2", "xparry3", "xparry4", "xparry5", "xparry6"],
                        ["idle", "idle", "idle"], "EVEN HERE")),
    (480, 624, seg_fang),
    (624, 720, seg_execution),
]

def main():
    fast = "--fast" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    for p in OUT.glob("*.png"):
        p.unlink()
    step = 4 if fast else 1
    for n in range(0, TOTAL, step):
        for a, b, fn in CUT:
            if a <= n < b:
                fr = fn(n - a, (n - a) / (b - a), n)
                break
        bars(fr)
        fr.convert("RGB").save(OUT / f"f{n:04d}.png")
    # renumber for ffmpeg's sequential reader
    for i, p in enumerate(sorted(OUT.glob("f*.png"))):
        p.rename(OUT / f"s{i:04d}.png")
    mp4 = OUT.parent / "TRAILER-B-Kael-vs-Executioner.mp4"
    subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS // step),
                    "-i", str(OUT / "s%04d.png"), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-crf", "17", str(mp4)], check=True)
    print(f"\n{mp4}  ({TOTAL // step} frames @ {FPS // step}fps)")

if __name__ == "__main__":
    main()
