"""Pack the guard + at-impact block cells for mizu, tsubasa, ember and shin.

Frames from tools/sprites/gen_block_four.py (8 nano-banana-pro still edits, ~$1.20;
shin regenerated once, +$0.30). Wiring is free — the engine already picks between
them: `p.blockPushTimer > 0 ? F.block2 : F.block`.

WHAT THIS REPLACES: all four `block2` cells were the wrong pose AND damaged —
mizu 54, tsubasa 57, shin 63, ember 48 are crouched LUNGES with a hard vertical cut
edge and a dark slab bleeding off the right side (mizu 12 columns of opaque
near-black, tsubasa 68) plus white motion-smear at the feet. The old cells stay on
the sheet, byte-identical and unreferenced, per the append-only rule.

SCALE = seed-cell body height / generated body height, measured head-top -> sole
with the run-width head finder (a thin bo or a raised claw scores below the 30%
width gate, so it does not inflate the measurement the way raw bbox ink does).
This works here — and did NOT work for the executioner and Kael in 326 — because
each frame is an EDIT OF THE PACKED CELL ITSELF, so it is already in the sheet's
own size lineage. Guard and hit measure within 1-3% of each other; the pair packs
at ONE number (the guard's) so the hit keeps its real compression instead of being
flattened back out.

⛔ frameW AND frameH ARE PER-FIGHTER: ember is 340x377/footY 369, tsubasa 301x320,
mizu and shin 300x320. Never assume 300.
"""
import json
import pathlib
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pack_block_326 import bbox, keyed  # noqa: E402  (same key + trim recipe)

REPO = pathlib.Path('/Users/anthonyguy/SHADOWCLASH-RECOVERED')
SRC = REPO / 'media/polished-candidates/block-four-331'
KEYS = ['xblkguard', 'xblkhit']
SCALE = {'mizu': 0.1434, 'tsubasa': 0.1509, 'ember': 0.1685, 'shin': 0.1507}


def main():
    for name, scale in SCALE.items():
        jp = REPO / f'web/assets/sprites/{name}.json'
        d = json.loads(jp.read_text())
        fw, fh, cols, footY = d['frameW'], d['frameH'], d['cols'], d['footY']
        sheet = Image.open(REPO / f'web/assets/sprites/{name}.png').convert('RGBA')
        assert sheet.width == cols * fw, (name, sheet.width, cols * fw)

        figs = [keyed(Image.open(SRC / f'{name}-{t}.png').convert('RGB')) for t in ('guard', 'hit')]
        base = d['frames'].get(KEYS[0], cols)          # re-runnable, same as 326
        grow = max(0, base + len(figs) - cols)
        new = Image.new('RGBA', ((cols + grow) * fw, fh), (0, 0, 0, 0))
        new.paste(sheet, (0, 0))
        for i in range(len(figs)):
            new.paste(Image.new('RGBA', (fw, fh), (0, 0, 0, 0)), ((base + i) * fw, 0))

        for i, im in enumerate(figs):
            im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
            # a cell is a hard box; the fix for an overflow is a bigger frameH, never a
            # smaller body — assert instead of silently clamping (measured: all 8 fit)
            assert im.width <= fw and im.height <= footY, (name, im.size, fw, footY)
            bx0, by0, bx1, by1 = bbox(im)
            new.alpha_composite(im, ((base + i) * fw + fw // 2 - (bx0 + bx1) // 2, footY - by1))
            print(f'  {name} cell {base + i} <- {KEYS[i]}  {im.width}x{im.height}')

        px = np.array(new)                              # purge sub-visible alpha LAST
        for i in range(len(figs)):
            band = px[:, (base + i) * fw:(base + i + 1) * fw]
            band[..., 3][band[..., 3] < 16] = 0
        new = Image.fromarray(px)

        oldA = np.array(sheet)
        newA = np.array(new.crop((0, 0, sheet.width, fh)))
        for c in range(cols):
            if base <= c < base + len(figs):
                continue
            assert np.array_equal(oldA[:, c * fw:(c + 1) * fw], newA[:, c * fw:(c + 1) * fw]), (name, c)
        new.save(REPO / f'web/assets/sprites/{name}.png')

        for i, k in enumerate(KEYS):
            d['frames'][k] = base + i
        d['frames']['block'] = d['frames']['xblkguard']
        d['frames']['block2'] = d['frames']['xblkhit']
        d['cols'] = cols + grow
        jp.write_text(json.dumps(d, indent=2) + '\n')
        print(f'  {name}: cols {cols} -> {d["cols"]}, block={d["frames"]["block"]} '
              f'block2={d["frames"]["block2"]}')


if __name__ == '__main__':
    main()
