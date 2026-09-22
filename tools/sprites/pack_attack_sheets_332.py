"""Pack the owner's four attack spreadsheets — 19 moves, 114 cells.

Sheets came in Jul 31 2026 and were cut by tools/sprites/cut_sheet_grid.py.
Ember's 24 frames go through fix_ember_claws_332.py first: his sheet drew FOUR
blades per gauntlet and his lock says three (second time the roster has drifted
there — SHEET_V 315 fixed the same defect), so the fourth blade is edited off
every frame before anything is packed.

⛔ ONE SCALE PER FIGHTER, AND IT IS PICKED ON THE HEAD. Body height (head-top ->
sole) says 0.858 / 1.407 / 1.353 / 0.118 for mizu / shin / tsubasa / ember and it
is wrong for all four, for the reason 326 wrote down and 331 confirmed from the
other side: matching total height is only safe when the new art is an EDIT of a
packed cell. This art was drawn independently and uses a SMALLER head-to-body
ratio than the shipped sheets, so height-matching inflates every head. Scales
below were chosen by standing a probe frame next to the fighter's own idle and
light1 and matching HEAD SIZE, which is what the eye actually checks on a chibi.

One number per fighter, never per cell: these frames are a drawn sequence, so the
crouches and the airborne stretches differ in height ON PURPOSE. Per-cell height
matching would flatten exactly the poses that carry the move.

APPEND-ONLY: every pre-existing cell is asserted byte-identical, one cell at a
time. Ember's upatk1..6 are REPOINTED at his new launcher — the old cells stay on
the sheet as upatk*_old.
"""
import json
import pathlib
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pack_block_326 import bbox, keyed  # noqa: E402

REPO = pathlib.Path('/Users/anthonyguy/SHADOWCLASH-RECOVERED')
CUT = REPO / 'media/handoff/attack-sheets-2026-07-31/cut'

# fighter -> (frame dir, scale, [(row file prefix, cell key prefix)])
JOBS = {
    'ember': ('ember-3blade', 0.130, [
        ('elaunch', 'elaunch'), ('clawrend', 'clawrend'),
        ('lowrake', 'lowrake'), ('retreatswipe', 'eretreat')]),
    'mizu': ('mizu', 1.00, [
        ('bothrust', 'bothrust'), ('bolowsweep', 'bolow'),
        ('risingstaff', 'ristaff'), ('staffspin', 'staffspin')]),
    'shin': ('shin', 1.20, [
        ('taijutsu', 'taijutsu'), ('risingaa', 'srisaa'), ('lowsweep', 'slowsweep'),
        ('kunaidash', 'kunaidash'), ('cjknee', 'cjknee')]),
    'tsubasa': ('tsubasa', 1.30, [
        ('divecut', 'divecut'), ('evasiveflick', 'eflick'), ('rgrush', 'rgrush'),
        ('lowtanto', 'lowtanto'), ('risingtwin', 'ristwin'), ('airthrow', 'airthrow')]),
}


def main():
    for name, (subdir, scale, rows) in JOBS.items():
        jp = REPO / f'web/assets/sprites/{name}.json'
        d = json.loads(jp.read_text())
        fw, fh, cols, footY = d['frameW'], d['frameH'], d['cols'], d['footY']
        sheet = Image.open(REPO / f'web/assets/sprites/{name}.png').convert('RGBA')
        assert sheet.width == cols * fw, (name, sheet.width, cols * fw)

        keys, imgs = [], []
        for src, dst in rows:
            for i in range(1, 7):
                keys.append(f'{dst}{i}')
                imgs.append(keyed(Image.open(CUT / subdir / f'{src}_{i}.png').convert('RGB')))

        base = d['frames'].get(keys[0], cols)              # re-runnable
        grow = max(0, base + len(imgs) - cols)
        new = Image.new('RGBA', ((cols + grow) * fw, fh), (0, 0, 0, 0))
        new.paste(sheet, (0, 0))
        for i in range(len(imgs)):
            new.paste(Image.new('RGBA', (fw, fh), (0, 0, 0, 0)), ((base + i) * fw, 0))

        clamped = []
        for i, im in enumerate(imgs):
            im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))),
                           Image.LANCZOS)
            # a cell is a hard box. Report anything that had to be clamped instead of
            # letting a wide lunge silently shrink — that is size boil you find later.
            if im.width > fw - 2 or im.height > footY - 2:
                s = min((fw - 2) / im.width, (footY - 2) / im.height)
                im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))),
                               Image.LANCZOS)
                clamped.append(f'{keys[i]}({s:.3f})')
            bx0, by0, bx1, by1 = bbox(im)
            new.alpha_composite(im, ((base + i) * fw + fw // 2 - (bx0 + bx1) // 2, footY - by1))

        px = np.array(new)                                 # purge sub-visible alpha LAST
        for i in range(len(imgs)):
            band = px[:, (base + i) * fw:(base + i + 1) * fw]
            band[..., 3][band[..., 3] < 16] = 0
        new = Image.fromarray(px)

        oldA = np.array(sheet)
        newA = np.array(new.crop((0, 0, sheet.width, fh)))
        for c in range(cols):
            if base <= c < base + len(imgs):
                continue
            assert np.array_equal(oldA[:, c * fw:(c + 1) * fw], newA[:, c * fw:(c + 1) * fw]), (name, c)
        new.save(REPO / f'web/assets/sprites/{name}.png')

        for i, k in enumerate(keys):
            d['frames'][k] = base + i
        if name == 'ember':                                # the launcher IS the replacement
            for i in range(1, 7):
                d['frames'].setdefault(f'upatk{i}_old', d['frames'][f'upatk{i}'])
                d['frames'][f'upatk{i}'] = d['frames'][f'elaunch{i}']
        d['cols'] = cols + grow
        jp.write_text(json.dumps(d, indent=2) + '\n')
        print(f'{name}: +{len(imgs)} cells at {base}..{base + len(imgs) - 1}, '
              f'cols {cols} -> {d["cols"]}, scale {scale}'
              + (f'  CLAMPED: {clamped}' if clamped else ''))


if __name__ == '__main__':
    main()
