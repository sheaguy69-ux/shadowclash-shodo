"""Is every row of a move spreadsheet drawn at the SAME size?

The Aug 2 aerial sheets came back with Kael's second row drawn ~15% smaller than his
first. Packed as-is the player watches him shrink for pressing back instead of forward.
Nothing else in the batch showed it, and nothing already here catches it —
`detect_floaters.py` finds loose limbs, not scale.

⛔ THE RULER IS INK AREA, NOT BOUNDING-BOX HEIGHT. A tuck genuinely has less bbox height
than an extension, so a height ruler flags every curled pose and, worse, invites the
per-cell height flattening that CAUSES size boil. Area rotates with the pose instead of
fighting it, and it is compared on the row MEDIAN so one odd pose cannot move the verdict.
A 2x scale error shows up as 4x area, so the square root below is the linear scale.

Weapons are deliberately NOT masked out: measured across the five Aug 2 sheets, masking
steel moved the verdict by at most 0.009 (kael 0.872 vs 0.870), because both rows of one
fighter carry the same weapon. Not worth per-fighter colour rules.

Fix a flagged sheet by scaling the SMALL row UP to the large one — never shrink the good
row, that throws away pixels you cannot get back.

Usage: python3 check_row_scale.py <sheet.png> [more.png ...]
       python3 check_row_scale.py selftest
"""
import pathlib
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cut_sheet_grid import PAGE, grid

TOL = 0.95        # linear scale ratio between rows; kael's real defect measured 0.872


def row_scales(img):
    """Median ink area per row, as a linear scale relative to the largest row."""
    a = np.array(img.convert('RGB')).astype(int)
    rows, cols = grid(img)
    if len(cols) < 3 or len(rows) < 2:
        return None, rows, cols
    ink = a.sum(2) < PAGE
    med = []
    for r in range(len(rows) - 1):
        cells = [int(ink[rows[r] + 4:rows[r + 1] - 4, cols[c] + 4:cols[c + 1] - 4].sum())
                 for c in range(1, len(cols) - 1)]
        med.append(float(np.median(cells)))
    top = max(med)
    return [float(np.sqrt(m / top)) for m in med], rows, cols


def selftest():
    """One row drawn at 85% must be caught; identical rows must not be."""
    def sheet(scales):
        a = np.full((520 * len(scales) + 20, 1420, 3), 255, np.uint8)
        for x in range(0, 1420, 200):
            a[:, max(0, x - 1):x + 2] = 212
        for i, s in enumerate(scales):
            a[i * 520:i * 520 + 2, :] = 129
            for c in range(6):
                w, h = int(120 * s), int(300 * s)
                x0, y0 = 210 + c * 200 + (120 - w) // 2, i * 520 + 100
                a[y0:y0 + h, x0:x0 + w] = 40
        a[-2:, :] = 129
        return Image.fromarray(a)

    same = row_scales(sheet([1.0, 1.0]))[0]
    assert same and min(same) > 0.99, f'identical rows flagged: {same}'
    off = row_scales(sheet([1.0, 0.85]))[0]
    assert off and min(off) < TOL, f'a row drawn at 85% was not caught: {off}'
    assert abs(min(off) - 0.85) < 0.03, f'ratio wrong: {off}'
    print(f'check_row_scale selftest OK — identical {min(same):.3f}, 85% row {min(off):.3f}')


def main():
    if len(sys.argv) == 2 and sys.argv[1] == 'selftest':
        return selftest()
    bad = 0
    for p in sys.argv[1:]:
        sc, rows, cols = row_scales(Image.open(p))
        if sc is None:
            print(f'{pathlib.Path(p).name[:44]:46s} grid not found ({len(rows)} rows, {len(cols)} cols)')
            continue
        worst = min(sc)
        flag = 'PASS' if worst >= TOL else f'⛔ row {sc.index(worst) + 1} is {100 * (1 - worst):.0f}% small'
        bad += worst < TOL
        print(f'{pathlib.Path(p).name[:44]:46s} {[round(s, 3) for s in sc]}  {flag}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main() or 0)
