"""Executioner SUSO-GIRI — the kneeling low cut. His last empty input.

Down+Heavy was byte-identical to his neutral heavy (verified live: both drew
heavy_i1..i5), so the slowest body in the roster had no armed low at all. His
only low was the unarmed sweep on Down+Light, which means a guard held high beat
his entire kit. This is the answer: sink to a knee, cut across the floor.

FRAMES, from the owner's own two sheets (already cut in a prior session):
  xlow1  B_20  compact, blade tucked low        (sink)
  xlow2  B_10  crouch, blade drawn back         (chamber)
  xlow3  B_19  THE CUT — deep crouch, blade skimming the ankle line  (held, contact)
  xlow4  A_23  carried through, blade low-forward   (follow)
  xlow5  B_28  up to the guard, blade still low     (recover)

⛔ EVERY FRAME MUST FACE THE SAME WAY AND HOLD THE SWORD. The first pick was
B_27 / B_23 / B_29 and it was wrong on both counts: those three draw him with no
blade visible at all — the Executioner without his odachi — and the sheets mix
facings, so B_16 and B_26 are lunges to the RIGHT while everything above cuts
LEFT. A five-cell string that flips facing mid-swing reads as a teleport. Checked
by rendering the candidates large, not by trusting the thumbnail grid.

⛔ NOT A FLOOR STAB. A_21 is the best-looking frame on either sheet (a driving
downward cut with a ground-impact spark) and it is deliberately NOT used here:
Down+Special is already GRAVEWAVE, "sword into the floor, shockwave crawls the
ground". Two moves on adjacent buttons that both plant the blade in the dirt is
one move drawn twice. This one sweeps horizontally along the floor instead.

⛔ SHEET A AND SHEET B ARE THE SAME SCALE — checked, not assumed, because two
metrics disagreed and one of them was mine. Standing-guard BBOX HEIGHTS say A is
taller (140 vs 124) which reads as "B is smaller, scale it up"; a head crop taken
in a fixed 70px window says the opposite. Both are artefacts: bbox height moves
with the pose and the blade angle, and a fixed crop window taken AFTER scaling
makes any upscale look bigger by construction. Standing both sheets' frames on
the same floor line at 1.2734 against the shipped xrise3 settles it — the heads
match. So the sheet-wide 1.2734 covers A and B alike, and mixing frames from the
two sheets in one sequence is safe.
"""
import json, pathlib
import numpy as np
from PIL import Image

REPO = pathlib.Path('/Users/anthonyguy/SHADOWCLASH-RECOVERED')
NF = pathlib.Path('/private/tmp/claude-501/-Users-anthonyguy-SHADOWCLASH-RECOVERED/'
                  'b474c4d4-46d9-4af5-8aa7-777bd55635a8/scratchpad/newframes')
OUT = pathlib.Path('/private/tmp/claude-501/-Users-anthonyguy-SHADOWCLASH-RECOVERED/'
                   '092847ce-5b36-4748-bf48-cc27f4a37237/scratchpad')

SRC = ['B_20', 'B_10', 'B_19', 'A_23', 'B_28']
KEYS = ['xlow1', 'xlow2', 'xlow3', 'xlow4', 'xlow5']
SCALE = 1.2734          # the sheet scale xtsuki and xrise were packed and approved at


def cells():
    d = json.loads((REPO / 'web/assets/sprites/executioner.json').read_text())
    fw, fh, footY = d['frameW'], d['frameH'], d['footY']
    out = []
    for n in SRC:
        im = Image.open(NF / f'{n}.png').convert('RGBA')
        im = im.resize((round(im.width * SCALE), round(im.height * SCALE)), Image.LANCZOS)
        ys, xs = np.nonzero(np.array(im)[..., 3] > 16)
        c = Image.new('RGBA', (fw, fh), (0, 0, 0, 0))
        c.alpha_composite(im, (fw // 2 - (xs.min() + xs.max()) // 2, footY - ys.max()))
        out.append(c)
        print(f'  {n}: body {ys.max()-ys.min()+1}px')
    return d, out


def main():
    import sys
    d, cs = cells()
    fw, fh, cols = d['frameW'], d['frameH'], d['cols']

    strip = Image.new('RGBA', (fw * len(cs), fh), (38, 40, 54, 255))
    for i, c in enumerate(cs):
        strip.alpha_composite(c, (i * fw, 0))
    strip.convert('RGB').save(OUT / 'xlow_preview.png')
    print(f'  preview -> {OUT / "xlow_preview.png"}')
    if '--dry' in sys.argv:
        return

    sheet = Image.open(REPO / 'web/assets/sprites/executioner.png').convert('RGBA')
    assert sheet.width == cols * fw, (sheet.width, cols * fw)
    new = Image.new('RGBA', ((cols + len(cs)) * fw, fh), (0, 0, 0, 0))
    new.paste(sheet, (0, 0))
    for i, c in enumerate(cs):
        new.alpha_composite(c, ((cols + i) * fw, 0))
        d['frames'][KEYS[i]] = cols + i
    new.save(REPO / 'web/assets/sprites/executioner.png')
    d['cols'] = cols + len(cs)
    (REPO / 'web/assets/sprites/executioner.json').write_text(json.dumps(d, indent=2) + '\n')
    print(f'  packed {KEYS[0]}..{KEYS[-1]} at cells {cols}-{cols+len(cs)-1}; cols -> {d["cols"]}')


if __name__ == '__main__':
    main()
