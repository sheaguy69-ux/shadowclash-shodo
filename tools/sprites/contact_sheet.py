#!/usr/bin/env python3
"""Labelled contact sheet for a fighter — every cell, its index, and every slot name
that points at it.

    python3 tools/sprites/contact_sheet.py exile
    python3 tools/sprites/contact_sheet.py exile --cols 8 --zoom 0.75

Writes docs/frame-handoff/<fighter>-sheet-contact.png. Cells nothing references are
flagged ORPHAN, because an unreferenced cell is art already paid for that the engine
can never draw.
"""
import argparse
import json
import pathlib
from collections import defaultdict

from PIL import Image, ImageDraw, ImageFont

REPO = pathlib.Path(__file__).resolve().parents[2]
FONT_PATH = '/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD_PATH = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('fighter')
    ap.add_argument('--cols', type=int, default=8)
    ap.add_argument('--zoom', type=float, default=1.0, help='multiplier on the cell size')
    ap.add_argument('--out', default=None)
    a = ap.parse_args()

    man = json.loads((REPO / f'web/assets/sprites/{a.fighter}.json').read_text())
    sheet = Image.open(REPO / f'web/assets/sprites/{a.fighter}.png').convert('RGBA')
    W, H, N = man['frameW'], man['frameH'], man['cols']
    assert sheet.size == (W * N, H), f'{sheet.size} != {(W * N, H)}'

    names = defaultdict(list)
    for slot, idx in man['frames'].items():
        names[idx].append(slot)

    tw, th = round(W * a.zoom), round(H * a.zoom)
    pad, band = 6, 40
    cw, ch = tw + pad * 2, th + band
    rows = (N + a.cols - 1) // a.cols
    head = 54

    out = Image.new('RGB', (cw * a.cols, head + ch * rows), (26, 26, 30))
    d = ImageDraw.Draw(out)
    f_idx = ImageFont.truetype(BOLD_PATH, 15)
    f_nm = ImageFont.truetype(FONT_PATH, 11)
    f_hd = ImageFont.truetype(BOLD_PATH, 24)

    d.text((14, 12), f'{a.fighter.upper()} — {N} cells · {W}x{H} · footY {man["footY"]} '
                     f'· scale {man["scale"]} · {len(man["frames"])} slot names',
           font=f_hd, fill=(238, 238, 244))

    ground = round(man['footY'] * a.zoom)
    for i in range(N):
        col, row = i % a.cols, i // a.cols
        x, y = col * cw, head + row * ch
        d.rectangle([x, y, x + cw - 1, y + ch - 1], fill=(34, 34, 40))
        cell = sheet.crop((i * W, 0, (i + 1) * W, H)).resize((tw, th), Image.LANCZOS)
        out.paste(cell, (x + pad, y), cell)
        d.line([(x + pad, y + ground), (x + pad + tw, y + ground)], fill=(70, 62, 92))

        slots = sorted(names.get(i, []))
        d.text((x + pad, y + th + 2), f'{i}', font=f_idx,
               fill=(255, 214, 120) if slots else (255, 120, 120))
        if not slots:
            d.text((x + pad + 26, y + th + 4), 'ORPHAN — nothing draws this',
                   font=f_nm, fill=(255, 120, 120))
            continue
        line, lines = '', []
        for s in slots:
            trial = f'{line} {s}'.strip()
            if d.textlength(trial, font=f_nm) > tw - 30:
                lines.append(line); line = s
            else:
                line = trial
        lines.append(line)
        for k, ln in enumerate(lines[:3]):
            tail = ' …' if k == 2 and len(lines) > 3 else ''
            d.text((x + pad + 26, y + th + 4 + k * 12), ln + tail, font=f_nm,
                   fill=(200, 200, 214))

    dst = pathlib.Path(a.out) if a.out else REPO / f'docs/frame-handoff/{a.fighter}-sheet-contact.png'
    dst.parent.mkdir(parents=True, exist_ok=True)
    out.save(dst)
    orphans = [i for i in range(N) if i not in names]
    print(f'{dst}  {out.size}  {N} cells, {len(orphans)} orphan{"" if len(orphans)==1 else "s"}'
          + (f': {orphans}' if orphans else ''))


if __name__ == '__main__':
    main()
