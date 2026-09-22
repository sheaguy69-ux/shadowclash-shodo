"""Executioner GYAKU KESA — the rising launcher finally gets its own frames.

Owner picked Option 1 of three (Jul 31 2026): A_20 -> A_16 -> A_13 from the
approved ChatGPT sheets. Waki chamber (blade hidden low behind the hip) ->
the blade driving up through 60 degrees -> jodan, arms high and torso stretched.

That is his own kenjutsu spec word for word — executioner.json gyaku_kesa_rising
reads "Waki-kamae (blade hidden behind right hip), sweeping upward ... Settles
into Jodan high guard" — and until now the move borrowed heavy_i1/i2/i4, which
is why it never read as a RISING cut: those are frames from a horizontal arc.

SCALE: the whole of sheet A packs at ONE number, 1.2734 — the scale the xtsuki
cells were built and approved at. Per-sequence anchoring failed twice for the same
reason, that INK IS NOT BODY: anchoring on the crouch (B_24) gave 1.58x and
inflated everything, and anchoring on A_13 gave 1.03x and shrank the body ~15%
because a third of its ink is the blade held overhead.

NO de-white pass, measured not assumed: near-white is 1 / 78 / 194 px and every
one of them was painted red and looked at — all blade highlight, no trapped
background. Running Kael's fix here would moth-eat the sword.
"""
import json, pathlib
import numpy as np
from PIL import Image

REPO = pathlib.Path('/Users/anthonyguy/SHADOWCLASH-RECOVERED')
NF = pathlib.Path('/private/tmp/claude-501/-Users-anthonyguy-SHADOWCLASH-RECOVERED/'
                  'b474c4d4-46d9-4af5-8aa7-777bd55635a8/scratchpad/newframes')
SRC = ['A_20', 'A_16', 'A_13']          # chamber -> rise -> jodan
KEYS = ['xrise1', 'xrise2', 'xrise3']
# ⛔ ONE SCALE FOR THE WHOLE SHEET, not a per-sequence anchor. Sheet A is drawn at
# one size, so its frames only differ in ink height because of POSE and BLADE ANGLE —
# and anchoring on ink is exactly what went wrong first time: A_13 holds its blade
# overhead, so ~30px of its 172px "height" is sword, and forcing that to 177 shrank
# the BODY about 15%. Measured after: eyes sat 71-78px above the floor where the idle
# and the light cells put them at 107-110, and the heads were visibly smaller side by
# side. 1.2734 is the scale the xtsuki cells were packed at (A_14/A_15/A_09, same
# sheet) and approved on screen, so it is the sheet's known-good number.
SHEET_A_SCALE = 1.2734


def bbox(im):
    ys, xs = np.nonzero(np.array(im.convert('RGBA'))[..., 3] > 16)
    return xs.min(), ys.min(), xs.max(), ys.max()


def main():
    d = json.loads((REPO / 'web/assets/sprites/executioner.json').read_text())
    fw, fh, cols, footY = d['frameW'], d['frameH'], d['cols'], d['footY']
    sheet = Image.open(REPO / 'web/assets/sprites/executioner.png').convert('RGBA')
    assert sheet.width == cols * fw, (sheet.width, cols * fw)

    src = {n: Image.open(NF / f'{n}.png').convert('RGBA') for n in SRC}
    scale = SHEET_A_SCALE
    print(f'  sheet-A scale {scale:.4f} (same as the approved xtsuki cells)')

    new = Image.new('RGBA', ((cols + len(SRC)) * fw, fh), (0, 0, 0, 0))
    new.paste(sheet, (0, 0))
    for i, n in enumerate(SRC):
        im = src[n]
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
        bx0, by0, bx1, by1 = bbox(im)
        new.alpha_composite(im, ((cols + i) * fw + fw // 2 - (bx0 + bx1) // 2, footY - by1))
        print(f'  cell {cols+i} <- {n}  h={by1-by0+1}')

    new.save(REPO / 'web/assets/sprites/executioner.png')
    for i, k in enumerate(KEYS):
        d['frames'][k] = cols + i
    d['cols'] = cols + len(SRC)
    (REPO / 'web/assets/sprites/executioner.json').write_text(json.dumps(d, indent=2) + '\n')
    print(f'  cols {cols} -> {d["cols"]}')


if __name__ == '__main__':
    main()
