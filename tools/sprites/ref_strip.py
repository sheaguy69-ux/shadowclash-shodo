#!/usr/bin/env python3
"""Build a ref|frames side-by-side strip for the mandatory LOOK gate.

Left column: the fighter's true-ref (canon 18:10). Right: the generated
cells in reading order with labels. Output: <dir>/ref-strip.png (or --out).

Usage:
    python3 tools/sprites/ref_strip.py <char> <dir> [--cells a,b,c] [--out path]
"""
import argparse, pathlib
from PIL import Image, ImageDraw, ImageFont

CELL_W, CELL_H, LABEL_H = 200, 240, 22


def load(path, w=CELL_W, h=CELL_H):
    im = Image.open(path).convert("RGB")
    im.thumbnail((w, h - LABEL_H))
    canvas = Image.new("RGB", (w, h - LABEL_H), (255, 255, 255))
    canvas.paste(im, ((w - im.width) // 2, (h - LABEL_H - im.height) // 2))
    return canvas


def main():
    p = argparse.ArgumentParser()
    p.add_argument("character")
    p.add_argument("dir", help="dir of generated cells")
    p.add_argument("--cells", default=None, help="comma list; default = all pngs sorted")
    p.add_argument("--out", default=None)
    args = p.parse_args()

    d = pathlib.Path(args.dir)
    cells = args.cells.split(",") if args.cells else sorted(x.stem for x in d.glob("*.png") if x.stem != "manifest")
    ref = pathlib.Path(f"media/polished-candidates/true-refs/{args.character}-true-ref.png")

    cols = len(cells) + 1
    img = Image.new("RGB", (cols * CELL_W, CELL_H + LABEL_H), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 13)
    except Exception:
        font = ImageFont.load_default()

    img.paste(load(ref), (0, LABEL_H))
    draw.text((6, 4), f"TRUE-REF: {args.character}", fill=(200, 0, 0), font=font)
    for i, c in enumerate(cells):
        img.paste(load(d / f"{c}.png"), ((i + 1) * CELL_W, LABEL_H))
        draw.text(((i + 1) * CELL_W + 6, 4), c, fill=(0, 0, 0), font=font)

    out = args.out or str(d.parent / f"{args.character}-ref-strip.png")
    img.save(out)
    print(f"strip -> {out} ({cols} panels)")


if __name__ == "__main__":
    main()
