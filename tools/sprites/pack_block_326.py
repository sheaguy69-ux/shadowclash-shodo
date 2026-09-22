"""Executioner + Kael get REAL blocking cells (owner art, Jul 31 2026).

Owner: "two frames on both characters represent before impact and at impact of
someone['s] attack" — which is exactly the engine's BLOCKING branch:
`p.blockPushTimer > 0 ? F.block2 : F.block` (web/index.html:6528). So the calm
guard packs to `block` and the sparking catch packs to `block2`.

What was there before: BOTH fighters' `block` was a cell of them holding the
sword HIGH AND WIDE — a windup, not a guard — and `block2` was another swing
pose. Nothing about either read as "I am being hit right now".

⛔ THE SCALE IS PICKED BY EYE AND THIS TOOL SAYS SO — same honesty 324 and 325
were written with. Six metrics were run against the idle and they do not agree:

  metric                    executioner   kael     why it lies
  bbox ink height            0.72         0.46     every pose holds a blade ABOVE
                                                   the head, so ~30% of the ink is sword
  head-top -> sole           0.594        0.441    the head-top scan (widest contiguous
                                                   run >= 30% of max) keeps the ref's
                                                   horns and drops the idle's
  helmet width               0.94/0.34    0.34     catches the scarf, and light1's blade
  eye-pair span              0.556        0.32     clean on the executioner (25/24/24/27
                                                   across four sheet cells), contaminated
                                                   on Kael — his blade sits beside the face
  eye-line -> sole           0.659        0.467    pose: both refs stand wider than the idle
  heads cropped to one zoom  ~0.50        ~0.44    <- the one you can actually see

Picked: executioner 0.55, kael 0.34 — both settled by EYE-PAIR SPAN measured on the
cells the game actually draws today, then confirmed by eye.

⛔ AND THE ANCHOR CELL MATTERS MORE THAN THE METRIC. Kael was first packed at 0.44
because the head crop was compared against CELL 0, and cell 0 is the old, larger
lineage — `frames.idle` moved to cell 67 while this was being packed. Against the
live cells (idle 67, light1, hurt, kneel: eye-span 23-28) the 0.44 pack measured 32,
i.e. 28% too big — the exact bug 6648a36 had just fixed on his cross parry. Measure
the anchor on the cells the JSON points at RIGHT NOW, not on cell 0.
The executioner sheet is one size (24-27 across idle 70 / light1 / hurt / kneel), so
0.55 lands his pair at 24 and stands.

Sheets stay append-only: cells 0..101 are copied byte-identical, the four new
poses go on the end, and `block`/`block2` are repointed. The old block cells
stay on the sheet, just unreferenced.
"""
import json
import pathlib
import subprocess
import tempfile

import numpy as np
from PIL import Image

REPO = pathlib.Path('/Users/anthonyguy/SHADOWCLASH-RECOVERED')
DL = pathlib.Path.home() / 'Downloads'

# (fighter, source png, [(x0, x1) of the two figures: guard, impact], scale)
JOBS = [
    ('executioner', DL / 'The executioner blocking frame.png', [(790, 1095), (1133, 1449)], 0.55),
    ('kael',        DL / 'kael blocking frame.png',            [(373, 693), (804, 1104)], 0.34),
]
KEYS = ['xblkguard', 'xblkhit']


def keyed(img):
    """white/near-white field -> transparent, house recipe: fuzz 42% corner floodfill."""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as t:
        src = t.name
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as t:
        dst = t.name
    img.save(src)
    subprocess.run(['magick', src, '-alpha', 'set',
                    '-bordercolor', 'white', '-border', '1',
                    '-fuzz', '42%', '-fill', 'none', '-floodfill', '+0+0', 'white',
                    '-shave', '1x1', '-trim', '+repage', dst], check=True)
    return Image.open(dst).convert('RGBA')


def body_height(im):
    """sole -> top of the HELMET, ignoring a blade held above the head.

    Row metric is the widest CONTIGUOUS ink run, so a wide helmet scores high and
    a thin blade scores low no matter how much of the row it crosses.
    """
    a = np.array(im)[..., 3] > 16
    runs = np.array([max((len(list(g)) for g in _groups(row)), default=0) for row in a])
    ys = np.nonzero(runs)[0]
    head = ys[runs[ys] >= 0.30 * runs.max()][0]
    return int(ys.max() - head + 1), int(head), int(ys.max())


def _groups(row):
    out, cur = [], 0
    for v in row:
        if v:
            cur += 1
        elif cur:
            out.append([0] * cur)
            cur = 0
    if cur:
        out.append([0] * cur)
    return out


def bbox(im):
    ys, xs = np.nonzero(np.array(im)[..., 3] > 16)
    return xs.min(), ys.min(), xs.max(), ys.max()


def main():
    for name, src_png, spans, scale in JOBS:
        jp = REPO / f'web/assets/sprites/{name}.json'
        d = json.loads(jp.read_text())
        fw, fh, cols, footY = d['frameW'], d['frameH'], d['cols'], d['footY']
        sheet = Image.open(REPO / f'web/assets/sprites/{name}.png').convert('RGBA')
        assert sheet.width == cols * fw, (sheet.width, cols * fw)

        idle = sheet.crop((d['frames']['idle'] * fw, 0, (d['frames']['idle'] + 1) * fw, fh))
        idle_h, _, _ = body_height(idle)

        raw = Image.open(src_png).convert('RGB')
        figs = [keyed(raw.crop((x0 - 4, 0, x1 + 4, raw.height))) for x0, x1 in spans]
        # ONE scale for the pair — the two poses come off the same drawn sheet, so
        # per-cell matching would flatten the (real) crouch the impact frame has.
        print(f'{name}: scale {scale} (picked by eye; idle body {idle_h}px)')

        # re-runnable: once the cells exist they are rewritten in place, so tuning the
        # scale does not stack a new pair on the end every time.
        base = d['frames'].get(KEYS[0], cols)
        grow = max(0, base + len(figs) - cols)
        new = Image.new('RGBA', ((cols + grow) * fw, fh), (0, 0, 0, 0))
        new.paste(sheet, (0, 0))
        for i in range(len(figs)):
            new.paste(Image.new('RGBA', (fw, fh), (0, 0, 0, 0)), ((base + i) * fw, 0))
        for i, im in enumerate(figs):
            im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
            bx0, by0, bx1, by1 = bbox(im)
            assert im.height <= footY and im.width <= fw, (name, im.size)
            new.alpha_composite(im, ((base + i) * fw + fw // 2 - (bx0 + bx1) // 2, footY - by1))
            bh = body_height(im)[0]
            print(f'  cell {base + i} <- {KEYS[i]}  body={bh}px (idle {idle_h})  ink h={by1 - by0 + 1}')

        # purge sub-visible alpha LAST (house recipe) — LANCZOS leaves a 1px veil of
        # a<16 around every edge, which is a faint halo once the engine tints a hit.
        # NOT a de-white pass: measured, every near-white pixel here is blade
        # highlight (93/12/98/224 px, all on the swords), and 323 already recorded
        # that running Kael's white-knee on this art moth-eats the blades.
        px = np.array(new)
        for i in range(len(figs)):
            band = px[:, (base + i) * fw:(base + i + 1) * fw]
            band[..., 3][band[..., 3] < 16] = 0
        new = Image.fromarray(px)

        # every cell that is not one of ours stays byte-identical
        oldA, newA = np.array(sheet), np.array(new.crop((0, 0, sheet.width, fh)))
        for c in range(cols):
            if base <= c < base + len(figs):
                continue
            assert np.array_equal(oldA[:, c * fw:(c + 1) * fw], newA[:, c * fw:(c + 1) * fw]), c
        new.save(REPO / f'web/assets/sprites/{name}.png')

        for i, k in enumerate(KEYS):
            d['frames'][k] = base + i
        d['frames']['block'] = d['frames']['xblkguard']
        d['frames']['block2'] = d['frames']['xblkhit']
        d['cols'] = cols + grow
        jp.write_text(json.dumps(d, indent=2) + '\n')
        print(f'  cols {cols} -> {d["cols"]}, block={d["frames"]["block"]} block2={d["frames"]["block2"]}')


if __name__ == '__main__':
    main()
