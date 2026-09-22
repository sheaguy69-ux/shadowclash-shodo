#!/usr/bin/env python3
"""Render cells exactly as drawSprite anchors them, against the floor line.

Reproduces the engine's anchor: the cell's footY row lands on GROUND_Y, the
sprite is drawn at man.scale, and the contact shadow is nailed to GROUND_Y+2
(it does NOT follow the sprite's bob — which is the whole point of the proof).

Usage: floor_proof.py <fighter> <out.png> <frame-name> [frame-name ...]
       floor_proof.py <fighter> <out.png> --idx 12 13 14
"""
import json
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
SPR = os.path.join(ROOT, 'web', 'assets', 'sprites')
PAD, GROUND = 14, 0.80        # panel padding, floor line as a fraction of panel height


def main():
    name, out = sys.argv[1], sys.argv[2]
    rest = sys.argv[3:]
    man = json.load(open(os.path.join(SPR, f'{name}.json')))
    sheet = Image.open(os.path.join(SPR, f'{name}.png')).convert('RGBA')
    fw, fh, footY, scale = man['frameW'], man['frameH'], man['footY'], man['scale']

    if rest and rest[0] == '--idx':
        cells = [(str(i), int(i)) for i in rest[1:]]
    else:
        F = man['frames']
        cells = [(n, F[n]) for n in rest if n in F]

    dw, dh = round(fw * scale), round(fh * scale)
    panelW, panelH = dw + PAD * 2, dh + 90
    gy = int(panelH * GROUND)
    strip = Image.new('RGBA', (panelW * len(cells), panelH), (24, 26, 34, 255))
    d = ImageDraw.Draw(strip)

    for col, (label, idx) in enumerate(cells):
        ox = col * panelW
        # the floor line + the engine's contact shadow, both FIXED to the ground
        d.line([(ox, gy), (ox + panelW, gy)], fill=(230, 70, 60, 255), width=1)
        d.ellipse([ox + panelW / 2 - 15 * scale / 0.4, gy + 2 - 4.2 * scale / 0.4,
                   ox + panelW / 2 + 15 * scale / 0.4, gy + 2 + 4.2 * scale / 0.4],
                  fill=(0, 0, 0, 90))
        cell = sheet.crop((idx * fw, 0, (idx + 1) * fw, fh)).resize((dw, dh), Image.LANCZOS)
        # honour the manifest's per-cell render corrections, so this shows what the
        # ENGINE draws rather than the raw packing
        if man.get('mirror', {}).get(str(idx)):
            cell = cell.transpose(Image.FLIP_LEFT_RIGHT)
        adj = man.get('footAdj', {}).get(str(idx), 0)
        # footY row lands ON the floor line — exactly drawImage(-(footY-adj)*S)
        strip.alpha_composite(cell, (ox + PAD, gy - round((footY - adj) * scale)))
        tag = (' adj%+d' % adj if adj else '') + (' MIR' if man.get('mirror', {}).get(str(idx)) else '')
        d.text((ox + 4, panelH - 16), f'{label} [{idx}]{tag}', fill=(200, 205, 215, 255))
        d.line([(ox, 0), (ox, panelH)], fill=(60, 64, 76, 255))

    strip.convert('RGB').save(out)
    print(out, strip.size)


if __name__ == '__main__':
    main()
