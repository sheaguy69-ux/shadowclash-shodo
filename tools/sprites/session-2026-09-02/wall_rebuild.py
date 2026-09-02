"""Wall cells, both laws at once.

The two failed attempts each broke one law: the split build kept the drawn stroke
byte-identical but left the figure 18px off the sheet's foot convention; the whole-cell
build anchored the figure but scaled the stroke with it.

Here the stroke is ISOLATED first — it is the ink both wall cells share, since her pose
differs between them but the painted wall does not — so the figure (including the fingers
that lap onto the stroke) can be scaled and re-anchored on its own, and the stroke pixels
are then restored from the live cell untouched.
"""
import json, sys
import numpy as np
from PIL import Image
sys.path.insert(0, '/private/tmp/claude-501/-Users-anthonyguy-SHADOWCLASH-1-0-2/3fa5f15d-d94b-4fc3-a77b-8dbde6db14fe/scratchpad')
from keyer_emu import keyed_cell
Image.MAX_IMAGE_PIXELS = None
R = '/Users/anthonyguy/SHADOWCLASH.1.0*2/SHODO-EDITION/web/assets/sprites'
OUT = '/private/tmp/claude-501/-Users-anthonyguy-SHADOWCLASH-1-0-2/9551097b-df90-4c80-8abf-d16ed89ab400/scratchpad/wallfix'

def resize_premult(rgba, f):
    a = rgba[..., 3:4].astype(np.float64) / 255.0
    pm = np.concatenate([rgba[..., :3].astype(np.float64) * a, a * 255.0], -1)
    h, w = rgba.shape[:2]
    nw, nh = max(1, round(w * f)), max(1, round(h * f))
    im = Image.fromarray(pm.astype(np.float32).reshape(h, w, 4)[..., 0], 'F')  # placeholder, per-channel below
    chans = [np.array(Image.fromarray(pm[..., c].astype(np.float32), 'F').resize((nw, nh), Image.LANCZOS)) for c in range(4)]
    out = np.stack(chans, -1)
    na = np.clip(out[..., 3:4], 0, 255)
    rgb = np.where(na > 0.5, np.clip(out[..., :3] / np.maximum(na / 255.0, 1e-6), 0, 255), 0)
    return np.concatenate([rgb, na], -1).round().astype(np.uint8)

def build(fighter, cells, band_hi, factor, target_bottom=None, keep_own_bottom=False):
    m = json.load(open(f'{R}/{fighter}.json')); fw, fh, footY = m['frameW'], m['frameH'], m['footY']
    sh = np.array(Image.open(f'{R}/{fighter}.png').convert('RGBA'))
    keyed = {c: keyed_cell(sh[:, c*fw:(c+1)*fw]) for c in cells}
    inks = {c: keyed[c][..., 3] > 40 for c in cells}
    # the painted wall = ink both cells share inside the band (her pose differs, the wall does not)
    stroke = np.ones((fh, fw), bool)
    for c in cells: stroke &= inks[c]
    stroke[:, band_hi:] = False
    print(f'{fighter}: shared stroke {int(stroke.sum())} px, band x<{band_hi}')
    res = {}
    for c in cells:
        cell = keyed[c]; ink = inks[c]
        fig = ink & ~stroke
        ys, xs = np.nonzero(fig)
        y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
        crop = np.where(fig[y0:y1+1, x0:x1+1, None], cell[y0:y1+1, x0:x1+1], 0)
        sc = resize_premult(crop, factor)
        nh, nw = sc.shape[:2]
        sa = sc[..., 3] > 40
        sys_, sxs = np.nonzero(sa)
        # X: the wall-side edge of the figure stays exactly where it was (she keeps her grip)
        nx = x0 - sxs.min()
        # Y: land on the sheet's own foot convention, or keep this cell's own bottom for an air pose
        bot = target_bottom if target_bottom is not None else (y1 if keep_own_bottom else footY - 3)
        ny = bot - sys_.max()
        out = np.zeros_like(cell)
        # KEYER DISARM FIRST. These cells carry a faint pixel out at the cell border (alpha 9 in
        # the bottom-right corner on exile) whose only job is to widen the alpha bbox so the
        # runtime keyer does not read the cell as a card and eat it. Dropping it cost 55% of the
        # cell on the first attempt (keyed ratio 0.458). Border ring only, so the old figure's
        # antialiased fringe is not dragged along with it.
        border = np.zeros((fh, fw), bool)
        border[:3, :] = border[-3:, :] = border[:, :3] = border[:, -3:] = True
        faint = (cell[..., 3] > 0) & (cell[..., 3] <= 40) & border
        out[faint] = cell[faint]
        out[stroke] = cell[stroke]                      # the painted wall, byte-identical
        ys2, xs2 = np.nonzero(sa)
        for yy, xx in zip(ys2, xs2):
            ty, tx = ny + yy, nx + xx
            if 0 <= ty < fh and 0 <= tx < fw: out[ty, tx] = sc[yy, xx]
        res[c] = out
        Image.fromarray(out).save(f'{OUT}/{fighter}_{c}.png')
    return m, keyed, stroke, res

if __name__ == '__main__':
    which = sys.argv[1]
    if which == 'shin':
        build('shin', [212, 213], 48, 0.851)
    else:
        build('exile', [267, 268], 40, 0.837, keep_own_bottom=True)
