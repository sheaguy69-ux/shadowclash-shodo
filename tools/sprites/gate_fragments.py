"""Catch cells that are FRAGMENTS OF A FIGURE rather than a figure.

WHY THIS EXISTS (owner, Jul 31 2026): "the frame of the special attack, like his
head disappeared... why isn't your catching it?" He was right that nothing was.
Executioner cell 54 shipped a torso and two arms with no head and no legs,
floating 81px above the floor, and the neutral special held it for three of its
five exposures.

Every gate we had checked the WRAPPER and none checked the FIGURE:
  components == 1   -> a headless torso is exactly one component
  edge alpha == 0   -> it floats in the middle, so it never touches an edge
  bottom on footY   -> only ever asserted on cells we had just packed
A missing head passes all three. So measure the figure itself:

  bodyH   how tall the ink is, against the fighter's own median cell
  footGap how far the lowest pixel sits above footY

A crouch is short but PLANTED. An air frame is off the floor but FULL HEIGHT.
Only a fragment is usually both short AND floating, which is why the two numbers
are reported together and judged together.

It SHORTLISTS, it does not judge — a tucked jump is honestly short and honestly
floating, so a handful of good cells come up with the bad ones and a human looks
at the montage. Two cleverer discriminators were tried and both failed on real
data: silhouette-boundary darkness (the fragment is 95% outlined, same as a good
tuck — it was drawn deliberately, not sliced) and blade-excluded body height
(the blade is level in a thrust, so it never changes the bbox). Nine fighters
shortlist four cells. That is a small enough pile to just look at.

  python3 tools/sprites/gate_fragments.py [fighter ...]     # default: all
  python3 tools/sprites/gate_fragments.py --strict …        # exit 1 on any flag
"""
import json, pathlib, sys
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None   # executioner's strip passed PIL's 179M-pixel bomb cap at 601 cols (SHEET_V 863)

SPR = pathlib.Path(__file__).resolve().parents[2] / 'web/assets/sprites'
SHORT = 0.72      # of the fighter's median cell height
FLOAT = 40        # px above footY


def check(name):
    d = json.loads((SPR / f'{name}.json').read_text())
    fw, fh, cols, footY = d['frameW'], d['frameH'], d['cols'], d['footY']
    a = np.array(Image.open(SPR / f'{name}.png').convert('RGBA'))[..., 3] > 16
    used = {}                                   # cell -> the keys that draw it
    for k, v in d.get('frames', {}).items():
        if isinstance(v, int) and 0 <= v < cols:
            used.setdefault(v, []).append(k)

    rows = []
    for c in range(cols):
        ys, _ = np.nonzero(a[:, c * fw:(c + 1) * fw])
        if not len(ys):
            rows.append((c, 0, fh)); continue
        rows.append((c, ys.max() - ys.min() + 1, footY - ys.max()))
    med = float(np.median([h for _, h, _ in rows if h]))

    # h == 0 is an UNPACKED cell (mokurai's sheet is mostly blank), not a fragment.
    bad = [(c, h, g) for c, h, g in rows if 0 < h < med * SHORT and g > FLOAT]
    blank = sum(1 for _, h, _ in rows if h == 0)
    print(f'{name}: {cols} cells, median body {med:.0f}px'
          f'{f", {blank} blank" if blank else ""}'
          f'{"  — CLEAN" if not bad else ""}')
    for c, h, g in bad:
        who = ','.join(used.get(c, ['(unreferenced)']))
        print(f'  LOOK AT cell {c:3d}  bodyH={h:3d} ({h/med:.0%} of median)  '
              f'floats {g}px above footY   <- {who}')
    return not bad


if __name__ == '__main__':
    argv = [a for a in sys.argv[1:] if not a.startswith('--')]
    strict = '--strict' in sys.argv
    names = argv or sorted(p.stem for p in SPR.glob('*.json'))
    ok = all([check(n) for n in names])
    sys.exit(1 if strict and not ok else 0)
