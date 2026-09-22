"""Shrink Kael's cross-parry cells (90-95) to the size of the rest of his sheet.

Owner-ordered in-place replacement (precedent: 287/298/302/318/321).

WHY ONLY THESE SIX. I first reported that his whole sheet was ~60% inconsistent
and he authorised a full 96-cell rescale — that report was WRONG and the job was
mostly unnecessary. The 60% came from measuring EYES ABOVE FEET, which moves with
the pose, not the size: light1 is a lunge with the head thrown high, xparry1 is a
crouch. The cells that actually get drawn in game already agree. The cross parry
is the one real outlier, and it is visible the moment you stand the cells on the
same floor line.

WHY THE FACTOR IS EYEBALLED AND NOT COMPUTED. Four automatic metrics were tried
on this sheet and returned 1.61 / 1.38 / 1.12 / 0.97 for the same question —
bbox ink (a raised blade inflates it), eye-pair AREA (his gold trim reads as
eye), eyes-above-feet (pose), head width at eye level (the crossed blades sit
exactly there, and the new art draws a rounder hood). Each is contaminated by
something different. So the factor was picked by cropping the HEADS to a common
zoom and looking: 1.00 is plainly bigger than the idle, 0.85 still a touch big,
0.78 matches. When every metric disagrees, say so and use your eyes — do not
pick whichever number is most convenient and call it measured.
"""
import json, pathlib
import numpy as np
from PIL import Image

REPO = pathlib.Path('/Users/anthonyguy/SHADOWCLASH-RECOVERED')
CELLS = range(90, 96)
SCALE = 0.78


def main():
    d = json.loads((REPO / 'web/assets/sprites/kael.json').read_text())
    fw, fh, footY = d['frameW'], d['frameH'], d['footY']
    sheet = Image.open(REPO / 'web/assets/sprites/kael.png').convert('RGBA')

    for c in CELLS:
        cell = sheet.crop((c * fw, 0, c * fw + fw, fh))
        a = np.array(cell)[..., 3]
        ys, xs = np.nonzero(a > 16)
        art = cell.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
        art = art.resize((max(1, round(art.width * SCALE)), max(1, round(art.height * SCALE))),
                         Image.LANCZOS)
        ys2, xs2 = np.nonzero(np.array(art)[..., 3] > 16)
        blank = Image.new('RGBA', (fw, fh), (0, 0, 0, 0))
        # soles stay ON the floor line, body stays centred in its cell
        blank.alpha_composite(art, (fw // 2 - (xs2.min() + xs2.max()) // 2, footY - ys2.max()))
        sheet.paste(blank, (c * fw, 0))          # paste, not composite: replaces the old cell
        print(f'  cell {c}: {xs.max()-xs.min()+1}x{ys.max()-ys.min()+1} -> {art.width}x{art.height}')

    sheet.save(REPO / 'web/assets/sprites/kael.png')
    print(f'  rescaled {len(list(CELLS))} cells by {SCALE}')


if __name__ == '__main__':
    main()
