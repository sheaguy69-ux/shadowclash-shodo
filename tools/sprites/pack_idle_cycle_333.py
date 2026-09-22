"""Pack the owner's 6-frame IDLE cycles for mizu / tsubasa / ember / shin.

Sheet: "t,m,s,E idle position.png", cut by cut_sheet_grid.py (its header row is
cut as a throwaway row and deleted), then run through erase_ground_shadows.py —
the drawing bakes a soft grey ellipse under the feet and the engine draws its own
contact shadow, so a baked one doubles up. 7,179 px removed across the 24 frames.

⛔ SCALE IS HEIGHT-MATCHED, AND THE REASON MATTERS. Standing the new art beside the
old idle, the heads looked smaller, and head size is the canon anchor — so the
first instinct was to scale UP until the heads matched, which would have stood
every fighter 4-18% taller than their own walk, jump and hurt cells. Measuring
instead of eyeballing killed that: head-top -> NECK over head-top -> sole is

    mizu   0.299 old / 0.315 new     ember  0.220 old / 0.229 new
    shin   0.223 old / 0.221 new     tsubasa 0.459 old / 0.534 new

i.e. the proportions already agree within ~5% on three of the four, and the head
needs no growing at all. Tsubasa is the only outlier and it is his HAIR, not his
skull — spiky hair drawn taller reads as a bigger head to the eye. So height-match
is both correct and free: nothing on the sheet shifts size, and the heads land
right anyway. The eye was wrong; the measurement was right.

Frames pack as xidle1..6. The old cells stay, byte-identical, as idle_old/idle2_old.
"""
import json
import pathlib
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pack_block_326 import bbox, body_height, keyed  # noqa: E402

REPO = pathlib.Path('/Users/anthonyguy/SHADOWCLASH-RECOVERED')
SRC = REPO / 'media/handoff/attack-sheets-2026-07-31/cut/idle-clean'
FIGHTERS = ['mizu', 'tsubasa', 'ember', 'shin']


def main():
    for name in FIGHTERS:
        jp = REPO / f'web/assets/sprites/{name}.json'
        d = json.loads(jp.read_text())
        fw, fh, cols, footY = d['frameW'], d['frameH'], d['cols'], d['footY']
        sheet = Image.open(REPO / f'web/assets/sprites/{name}.png').convert('RGBA')
        assert sheet.width == cols * fw, (name, sheet.width, cols * fw)

        cur = sheet.crop((d['frames']['idle'] * fw, 0, (d['frames']['idle'] + 1) * fw, fh))
        imgs = [keyed(Image.open(SRC / f'{name}_{i}.png').convert('RGB')) for i in range(1, 7)]
        # ONE scale for the cycle, taken from frame 1: a breathing loop that rescales
        # per cell is the classic size boil, and it is most visible on an idle because
        # the idle is the cell you stare at.
        scale = body_height(cur)[0] / body_height(imgs[0])[0]

        keys = [f'xidle{i}' for i in range(1, 7)]
        base = d['frames'].get(keys[0], cols)
        grow = max(0, base + len(imgs) - cols)
        new = Image.new('RGBA', ((cols + grow) * fw, fh), (0, 0, 0, 0))
        new.paste(sheet, (0, 0))
        for i in range(len(imgs)):
            new.paste(Image.new('RGBA', (fw, fh), (0, 0, 0, 0)), ((base + i) * fw, 0))

        for i, im in enumerate(imgs):
            im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))),
                           Image.LANCZOS)
            assert im.width <= fw and im.height <= footY, (name, im.size)
            bx0, by0, bx1, by1 = bbox(im)
            new.alpha_composite(im, ((base + i) * fw + fw // 2 - (bx0 + bx1) // 2, footY - by1))

        px = np.array(new)
        for i in range(len(imgs)):
            band = px[:, (base + i) * fw:(base + i + 1) * fw]
            band[..., 3][band[..., 3] < 16] = 0
        new = Image.fromarray(px)

        oldA, newA = np.array(sheet), np.array(new.crop((0, 0, sheet.width, fh)))
        for c in range(cols):
            if base <= c < base + len(imgs):
                continue
            assert np.array_equal(oldA[:, c * fw:(c + 1) * fw], newA[:, c * fw:(c + 1) * fw]), (name, c)
        new.save(REPO / f'web/assets/sprites/{name}.png')

        for i, k in enumerate(keys):
            d['frames'][k] = base + i
        d['frames'].setdefault('idle_old', d['frames']['idle'])
        d['frames'].setdefault('idle2_old', d['frames']['idle2'])
        d['frames']['idle'] = d['frames']['xidle1']
        d['frames']['idle2'] = d['frames']['xidle4']
        d['cols'] = cols + grow
        jp.write_text(json.dumps(d, indent=2) + '\n')

        bodies = [body_height(new.crop(((base + i) * fw, 0, (base + i + 1) * fw, fh)))[0]
                  for i in range(len(imgs))]
        print(f'{name}: cells {base}..{base + 5}, scale {scale:.3f}, '
              f'bodies {bodies} (was {body_height(cur)[0]}), cols {cols} -> {d["cols"]}')


if __name__ == '__main__':
    main()
