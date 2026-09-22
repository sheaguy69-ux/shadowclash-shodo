#!/usr/bin/env python3
"""Pack Oni's owner-drawn ground dodge roll — six beats — into oni.png as roll_1..6.

Source: RECOVERY/oni-founder/dodge-roll-aug13/beat1..6.png, cut from the owner's
2172x724 board. Delivered on WHITE, not transparent, so this keys as well as packs.

Scale: ONE UNIFORM FACTOR, median(target / candidate) over the set, where the targets
are his measured standing height (153px) times the handoff §3 percentages. Anchoring on
beat 6 instead was tested and rejected: it puts the BALL at 74% of standing (spec 60%)
and the duck-in at 95%, i.e. a "duck" as tall as standing. The median holds the ball at
61% against the engine's ROLL_TUCK of 0.62, and a feet-aligned render against his
shipped idle shows no head boil (RECOVERY/oni-founder/dodge-roll-aug13/SCALE-CHECK.png).

His beats 5-6 come out lower than the six originals' (62% / 75% against their 91-100%)
because the art finishes in a low claw-planted crouch rather than rising to stance. That
is the drawing, not the scale — see the note in the commit.

⛔ ONI IS STILL BENCHED. This packs and wires the art; it does not unbench him.
"""
import json

import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
REPO = '/Users/anthonyguy/SHADOWCLASH-RECOVERED'
SRC = f'{REPO}/RECOVERY/oni-founder/dodge-roll-aug13'
SPR = f'{REPO}/web/assets/sprites'
PCT = [0.78, 0.64, 0.60, 0.66, 0.72, 0.92]      # handoff §3, the six roll beats
WHITE_TOL = 30                                   # how close to pure white counts as page


def key_white(path):
    """Flood the white page from the corners, keep the largest body, purge soft alpha.

    ⛔ FLOOD FROM THE CORNERS — never 'delete every white pixel'. His mask IS white, and
    a global white-key would punch his face out. The mask is sealed inside a black
    outline, so a corner flood cannot reach it; that is the whole reason this works.
    """
    a = np.array(Image.open(path).convert('RGBA'))
    rgb = a[..., :3].astype(int)
    near_white = (rgb.min(2) >= 255 - WHITE_TOL) & (np.ptp(rgb, axis=2) <= WHITE_TOL)
    lab, n = ndimage.label(near_white)
    page = np.zeros(near_white.shape, bool)
    h, w = near_white.shape
    for cy, cx in ((0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)):
        if lab[cy, cx]:
            page |= lab == lab[cy, cx]
    a[page] = 0
    # keep the largest connected body — drops stray specks the board carried
    solid = a[..., 3] > 0
    lab2, n2 = ndimage.label(solid, np.ones((3, 3)))
    if n2 > 1:
        keep = 1 + int(np.argmax(ndimage.sum(solid, lab2, range(1, n2 + 1))))
        a[(lab2 != keep) & solid] = 0
    return a


def bbox(m):
    ys, xs = np.where(m)
    return xs.min(), ys.min(), xs.max(), ys.max()


def main():
    man = json.load(open(f'{SPR}/oni.json'))
    cw, ch, footy, F = man['frameW'], man['frameH'], man['footY'], man['frames']
    base = man['cols']
    sheet = Image.open(f'{SPR}/oni.png').convert('RGBA')
    assert sheet.size == (base * cw, ch), sheet.size
    orig = np.array(sheet)

    idle = np.array(sheet.crop((F['idle'] * cw, 0, (F['idle'] + 1) * cw, ch)))[..., 3] > 0
    ix0, iy0, ix1, _ = bbox(idle)
    stand = footy - iy0
    want_cx = (ix0 + ix1) / 2
    target = [round(stand * p) for p in PCT]

    keyed, faces = [], []
    for i in range(1, 7):
        a = key_white(f'{SRC}/beat{i}.png')
        m = a[..., 3] > 0
        # the white skull must survive the key — it is the one white thing we keep
        rgb = a[..., :3].astype(int)
        faces.append(int((m & (rgb.min(2) > 150) & (np.ptp(rgb, axis=2) < 40)).sum()))
        keyed.append(a)
        Image.fromarray(a, 'RGBA').save(f'{SRC}/keyed{i}.png')
    assert all(f > 100 for f in faces), f'skull mask lost in the key: {faces}'
    print('white mask pixels surviving the key, per beat:', faces)

    hs = [bbox(a[..., 3] > 0)[3] - bbox(a[..., 3] > 0)[1] + 1 for a in keyed]
    s = float(np.median([t / h for t, h in zip(target, hs)]))
    print(f'standing {stand}px  targets {target}  candidates {hs}  -> ONE scale {s:.4f}')

    new = []
    for i, a in enumerate(keyed, 1):
        im = Image.fromarray(a, 'RGBA')
        fs = np.array(im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))),
                                Image.LANCZOS))
        fs[fs[..., 3] < 16] = 0          # the LANCZOS fringe, purged before it is measured
        m = fs[..., 3] > 0
        x0, _, x1, y1 = bbox(m)
        dx, dy = int(round(want_cx - (x0 + x1) / 2)), footy - y1
        cell = np.zeros((ch, cw, 4), np.uint8)
        sy0, sx0 = max(0, -dy), max(0, -dx)
        sy1, sx1 = min(fs.shape[0], ch - dy), min(fs.shape[1], cw - dx)
        cell[dy + sy0:dy + sy1, dx + sx0:dx + sx1] = fs[sy0:sy1, sx0:sx1]
        cm = cell[..., 3] > 0
        bx0, by0, bx1, by1 = bbox(cm)
        assert by1 == footy, f'beat{i} bottom {by1} != footY {footy}'
        assert bx0 > 0 and bx1 < cw - 1 and by0 > 0, f'beat{i} clipped ({bx0}..{bx1}, {by0})'
        new.append((f'roll_{i}', Image.fromarray(cell, 'RGBA')))
        print(f'  roll_{i}: {by1 - by0 + 1}px = {round((by1 - by0 + 1) / stand * 100)}% of standing')

    out = Image.new('RGBA', ((base + len(new)) * cw, ch), (0, 0, 0, 0))
    out.paste(sheet, (0, 0))
    for k, (_, c) in enumerate(new):
        out.paste(c, ((base + k) * cw, 0))
    assert np.array_equal(np.array(out)[:, :base * cw], orig), 'original cells changed'
    out.save(f'{SPR}/oni.png')
    assert np.array_equal(np.array(Image.open(f'{SPR}/oni.png'))[:, :base * cw], orig), \
        'post-save mismatch'

    for k, (name, _) in enumerate(new):
        assert name not in man['frames'], name
        man['frames'][name] = base + k
    man['cols'] = base + len(new)
    open(f'{SPR}/oni.json', 'w').write(json.dumps(man, indent=1) + '\n')
    print(f'packed {len(new)} cells -> cols {man["cols"]}, sheet {out.size}')


if __name__ == '__main__':
    main()
