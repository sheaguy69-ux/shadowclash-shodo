#!/usr/bin/env python3
"""SHODO UI FURNITURE — the select screen's strokes, cut by the same brush that
painted the boards.

⛔ NO SPEND. Everything here comes out of shodo.py's brush, so the panel and the
stage behind it are the same hand and the same ink.

  python3 tools/stages/shodo_ui.py            # writes web/assets/ui/shodo/

ponytail: the engine's canvas is a fixed 2048x1536, so each piece is drawn
somewhere on that sheet and CROPPED out rather than parameterising W/H through
every primitive. Wasteful in pixels, free in code, and it runs in seconds.
"""
import sys
import pathlib

import numpy as np
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from shodo import (Board, W, H, blur, arcring, seal, SUMI, SEAL, VERM)  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[2] / "web/assets/ui/shodo"
INK = (0.078, 0.075, 0.102)


def cut(b, layer, rgb, box, size=None, bleed=0.25):
    """One ink layer as a transparent PNG: density becomes alpha, so a dry tail
    fades instead of ending in a hard edge."""
    d = b.layers[layer]
    a = np.clip(d + blur(d, 7) * bleed, 0, 1)
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2] = [int(c * 255 + 0.5) for c in rgb]
    arr[..., 3] = (a * 255 + 0.5).astype(np.uint8)
    im = Image.fromarray(arr, "RGBA").crop(box)
    if size:
        im = im.resize(size, Image.LANCZOS)
    return im


def save(im, name):
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / name
    im.save(p, optimize=True)
    print(f"  {name:20s} {im.size[0]}x{im.size[1]}  {p.stat().st_size // 1024} KB")


def washi():
    """The sheet the whole panel is written on. Pitched a step ABOVE the boards:
    the panel is the sheet in your hands and the stage is the realm behind it,
    and small ink text needs the contrast that step buys."""
    import shodo
    was, shodo.TONE = shodo.TONE, shodo.TONE * 1.30
    b = Board(9001, (0.937, 0.910, 0.843), 1.0)
    shodo.TONE = was
    arr = (b.paper() * 255 + 0.5).astype(np.uint8)
    im = Image.fromarray(arr).resize((1400, 1050), Image.LANCZOS)
    save(im.quantize(colors=255, dither=Image.Dither.FLOYDSTEINBERG), "washi.png")


def stroke_heavy():
    """The bar a heading sits on. One pass, loaded at the belly, dry at the tail."""
    b = Board(9002)
    b.stroke(SUMI, [(150, 770), (700, 742), (1300, 766), (1900, 736)], 118, 1.0,
             prof=(0.10, 1, 0.05), dry=0.45, wobble=0.9, n=280)
    save(cut(b, SUMI, INK, (120, 620, 1930, 900)), "stroke.png")


def rule():
    """A divider. Nearly out of ink, so it reads as a rule and not a bar."""
    b = Board(9003)
    b.stroke(SUMI, [(150, 764), (900, 754), (1900, 762)], 20, 0.9,
             prof=(0.05, 1, 0.03), dry=0.88, wobble=1.1, n=260)
    save(cut(b, SUMI, INK, (120, 700, 1930, 830)), "rule.png")


def plate():
    """A block of ink for a live button. Ragged ends, so it is stamped, not drawn."""
    b = Board(9004)
    b.stroke(SUMI, [(430, 762), (1024, 754), (1620, 764)], 296, 1.0,
             prof=(0.94, 1, 0.92), dry=0.26, wobble=0.55, n=220)
    save(cut(b, SUMI, INK, (360, 580, 1690, 946)), "plate.png")


def frame():
    """A hand-brushed box. The corners OVERSHOOT — a closed rectangle reads as a
    border-radius, an overshot one reads as four strokes. Sliced by border-image,
    so corners keep their shape at any button size."""
    b = Board(9005)
    x0, x1, y0, y1 = 600, 1450, 340, 1190
    b.stroke(SUMI, [(x0 - 34, y0 + 8), (1024, y0 - 10), (x1 + 30, y0 + 6)], 26, 0.96,
             prof=(0.35, 1, 0.28), dry=0.5, wobble=1.0, n=200)
    b.stroke(SUMI, [(x0 - 30, y1 - 6), (1024, y1 + 12), (x1 + 34, y1 - 4)], 26, 0.96,
             prof=(0.30, 1, 0.34), dry=0.5, wobble=1.0, n=200)
    b.stroke(SUMI, [(x0 + 6, y0 - 30), (x0 - 10, 765), (x0 + 4, y1 + 32)], 24, 0.96,
             prof=(0.32, 1, 0.30), dry=0.5, wobble=1.0, n=200)
    b.stroke(SUMI, [(x1 - 4, y0 - 34), (x1 + 12, 765), (x1 - 6, y1 + 28)], 24, 0.96,
             prof=(0.28, 1, 0.32), dry=0.5, wobble=1.0, n=200)
    # cropped TIGHT to the strokes: border-image slices from the edge, so a
    # frame floating in the middle of its own PNG loses its corners.
    save(cut(b, SUMI, INK, (548, 288, 1480, 1240), (512, 512)), "frame.png")


def enso():
    """The watermark. Swept once, and the gap where the brush left the paper is
    the whole point — a closed circle is a ring, an open one is an enso."""
    b = Board(9006)
    arcring(b, 1024, 766, 560, 548, 0.55, 6.45, 76, 1.0, SUMI, 0.55)
    save(cut(b, SUMI, INK, (400, 142, 1648, 1390), (620, 620)), "enso.png")


def hanko(ch, name, size=300):
    b = Board(9007 + len(name))
    seal(b, 1024, 768, size, ch, grit=0.34)
    r = size // 2 + 8
    save(cut(b, SEAL, VERM, (1024 - r, 768 - r, 1024 + r, 768 + r), (168, 168), bleed=0.06),
         name)


if __name__ == "__main__":
    washi(); stroke_heavy(); rule(); plate(); frame(); enso()
    hanko("選", "seal-pick.png")        # stamped on the fighter you chose
    hanko("闘", "seal-fight.png")       # the button that starts it
    hanko("場", "seal-stage.png")       # stamped on the board you pinned
