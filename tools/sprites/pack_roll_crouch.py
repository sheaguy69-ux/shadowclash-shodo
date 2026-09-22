#!/usr/bin/env python3
"""Pack the owner's ground-roll + crouch candidates into the eight sheets (SHEET_V 487).

Source: media/roll-crouch-candidates-2026-08-12/frames/<fighter>/<fighter>_{roll,crouch}_N.png
Adds `roll_1..6` (six fighters) and `crouch_1..4` (all eight) — 68 cells, append-only.

⛔ ONE UNIFORM SCALE PER SEQUENCE (the Ember recipe, rule 5). Never per-cell
MATCH_HEIGHT: body height changing across the beats IS the animation, and flattening
each cell to its own target scales the compact ball ~1.2x against the upright rise and
boils the character's size. The one scale is `median(target_h / candidate_h)` over the
set — the targets in docs/HANDOFF-ROLL-CROUCH.md §4 are each fighter's own measured
standing height times the §3 percentages, so the median lands the set on the house
registration while keeping the artist's internal proportions intact.

Ink area was checked as a second opinion and REJECTED as an anchor: it runs +10..+28%
against the height answer on every one of the fourteen sets, and the sign is uniform
because a folded pose simply has less silhouette than a standing one. A cross-pose area
match would inflate every crouch.

Horizontal anchor differs by sequence, because the thing that must not slide differs:
  crouch — foot-band centroid pinned to the IDLE's foot-band centroid. The feet do not
           move when you duck, so the drawing must not either.
  roll   — ink-bbox centre pinned to the idle's ink-bbox centre. The contact point
           travels (feet -> shoulder -> back -> hip -> feet); pinning the contact point
           would shove the body backward the moment the shoulder takes the floor.
"""
import json
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
REPO = '/Users/anthonyguy/SHADOWCLASH-RECOVERED'
CAND = f'{REPO}/media/roll-crouch-candidates-2026-08-12/frames'
SPR = f'{REPO}/web/assets/sprites'

# docs/HANDOFF-ROLL-CROUCH.md §4 — sheet-pixel heights, per beat.
TARGET = {
    'executioner': dict(roll=[144, 118, 111, 122, 133, 170], crouch=[163, 141, 126, 130]),
    'mizu':        dict(roll=[122, 100,  94, 103, 112, 144], crouch=[137, 119, 106, 109]),
    'shin':        dict(roll=[151, 124, 116, 128, 140, 178], crouch=[171, 147, 132, 136]),
    'tsubasa':     dict(roll=[151, 124, 116, 127, 139, 178], crouch=[170, 147, 131, 135]),
    'ember':       dict(roll=[161, 132, 124, 137, 149, 190], crouch=[182, 157, 141, 145]),
    'kael':        dict(roll=[136, 111, 104, 115, 125, 160], crouch=[153, 132, 118, 122]),
    'mokurai':     dict(crouch=[131, 113, 101, 104]),
    'exile':       dict(crouch=[136, 118, 105, 108]),
}
FOOT_BAND = 0.12   # bottom fraction of the ink used as "what is on the floor"


def alpha(img):
    return np.array(img.convert('RGBA'))[..., 3] > 0


def bbox(m):
    ys, xs = np.where(m)
    return xs.min(), ys.min(), xs.max(), ys.max()


def foot_cx(m):
    """Centroid x of the lowest FOOT_BAND of the ink."""
    _, y0, _, y1 = bbox(m)
    cut = y1 - int(round((y1 - y0 + 1) * FOOT_BAND))
    band = m[cut:y1 + 1, :]
    xs = np.where(band.any(axis=0))[0]
    return (xs.min() + xs.max()) / 2


def bbox_cx(m):
    x0, _, x1, _ = bbox(m)
    return (x0 + x1) / 2


def compose(img, s, cw, ch, footy, want_cx, mode):
    """Scale by s, pin the lowest ink row to footy, pin the sequence anchor to want_cx.

    ⛔ PURGE SUB-VISIBLE ALPHA BEFORE MEASURING, and place with numpy rather than
    Image.paste. LANCZOS hangs a two-pixel fringe of alpha 4 under the soles, and
    paste-with-its-own-mask multiplies alpha by itself (4*4/255 -> 0), so the fringe
    measured as body, set the anchor, then evaporated in the composite — every one of
    the 68 cells landed 2-3px ABOVE the floor line. Which is the exact bug this whole
    job exists to kill.
    """
    fs = np.array(img.resize((max(1, int(round(img.width * s))),
                              max(1, int(round(img.height * s)))), Image.LANCZOS))
    fs[fs[..., 3] < 16] = 0
    m = fs[..., 3] > 0
    _, _, _, y1 = bbox(m)
    cx = foot_cx(m) if mode == 'crouch' else bbox_cx(m)
    dx, dy = int(round(want_cx - cx)), footy - y1
    cell = np.zeros((ch, cw, 4), np.uint8)
    sy0, sx0 = max(0, -dy), max(0, -dx)
    sy1, sx1 = min(fs.shape[0], ch - dy), min(fs.shape[1], cw - dx)
    cell[dy + sy0:dy + sy1, dx + sx0:dx + sx1] = fs[sy0:sy1, sx0:sx1]
    return Image.fromarray(cell, 'RGBA')


def main():
    report = []
    for name in sorted(TARGET):
        man = json.load(open(f'{SPR}/{name}.json'))
        cw, ch, footy = man['frameW'], man['frameH'], man['footY']
        base = man['cols']
        sheet = Image.open(f'{SPR}/{name}.png').convert('RGBA')
        assert sheet.size == (base * cw, ch), (name, sheet.size)
        orig = np.array(sheet)

        idle_m = alpha(sheet.crop((man['frames']['idle'] * cw, 0,
                                   (man['frames']['idle'] + 1) * cw, ch)))
        anchor = {'crouch': foot_cx(idle_m), 'roll': bbox_cx(idle_m)}
        stand_h = footy - bbox(idle_m)[1]

        new = []
        for seq in ('roll', 'crouch'):
            tg = TARGET[name].get(seq)
            if not tg:
                continue
            imgs = [Image.open(f'{CAND}/{name}/{name}_{seq}_{i}.png').convert('RGBA')
                    for i in range(1, len(tg) + 1)]
            hs = [bbox(alpha(im))[3] - bbox(alpha(im))[1] + 1 for im in imgs]
            s = float(np.median([t / h for t, h in zip(tg, hs)]))
            for i, im in enumerate(imgs, 1):
                cell = compose(im, s, cw, ch, footy, anchor[seq], seq)
                cm = alpha(cell)
                assert cm.any(), f'{name} {seq}_{i} composed empty'
                x0, y0, x1, y1 = bbox(cm)
                # nothing clipped, nothing floating, nothing through the floor
                assert x0 > 0 and x1 < cw - 1, f'{name} {seq}_{i} clipped horizontally ({x0},{x1})'
                assert y0 > 0, f'{name} {seq}_{i} clipped at the top'
                assert y1 == footy, f'{name} {seq}_{i} bottom {y1} != footY {footy}'
                new.append((f'{seq}_{i}', cell))
                report.append((name, f'{seq}_{i}', y1 - y0 + 1,
                               round((y1 - y0 + 1) / stand_h * 100), round(s, 4)))

        out = Image.new('RGBA', ((base + len(new)) * cw, ch), (0, 0, 0, 0))
        out.paste(sheet, (0, 0))
        for k, (_, cell) in enumerate(new):
            out.paste(cell, ((base + k) * cw, 0))
        # non-negotiable #1: every original cell byte-identical
        assert np.array_equal(np.array(out)[:, :base * cw], orig), f'{name}: originals changed'
        out.save(f'{SPR}/{name}.png')
        assert np.array_equal(np.array(Image.open(f'{SPR}/{name}.png'))[:, :base * cw], orig), \
            f'{name}: post-save mismatch'

        for k, (key, _) in enumerate(new):
            assert key not in man['frames'], f'{name}: {key} already exists'
            man['frames'][key] = base + k
        man['cols'] = base + len(new)
        txt = json.dumps(man, indent=1) + '\n'
        open(f'{SPR}/{name}.json', 'w').write(txt)
        print(f'{name}: +{len(new)} cells -> cols {man["cols"]}, sheet {out.size}')

    print(f'\n{"fighter":<12}{"cell":<10}{"px":>5}{"% standing":>12}{"scale":>9}')
    for r in report:
        print(f'{r[0]:<12}{r[1]:<10}{r[2]:>5}{r[3]:>11}%{r[4]:>9}')
    print(f'\n{len(report)} cells packed')


if __name__ == '__main__':
    main()
