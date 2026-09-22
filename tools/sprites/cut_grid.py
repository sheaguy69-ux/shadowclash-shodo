"""Cut a PANELLED grid board (rounded boxes, number in the corner) into keyed cells.

cut_strip cannot read this one: a panel rectangle encloses its own white interior, so the
border flood never gets inside and the whole page keys as one blob. The panel rules are
regular, so find them as rows/cols that are inked nearly edge to edge, crop INSIDE each
box, then key and drop the corner numeral by component.
"""
import sys, pathlib, numpy as np
from PIL import Image
from scipy import ndimage as nd


def cut_grid(path, rows, cols, inset=6):
    A = np.asarray(Image.open(path).convert('RGBA')).astype(int)
    H, W = A.shape[:2]
    rgb = A[:, :, :3]
    ink = rgb.min(2) <= 200
    rr = np.where(ink.sum(1) > W * 0.60)[0]
    def group(a):
        out, s, p = [], a[0], a[0]
        for v in a[1:]:
            if v > p + 3: out.append((s, p)); s = v
            p = v
        out.append((s, p)); return out
    # ⛔ A SECTION TITLE IS ALSO INKED EDGE TO EDGE. "3. BODY RUSH TAIJUTSU" spans the
    # page and reads as a rule at any density threshold. A rule is a LINE — a few px tall;
    # a title is 11-24. Filter on thickness, not on density.
    hr = [g for g in group(rr) if g[1] - g[0] <= 6]
    assert len(hr) == rows * 2, f'expected {rows*2} panel rules, got {len(hr)}'
    ybands = [(hr[2*i][1], hr[2*i+1][0]) for i in range(rows)]
    # ⛔ VERTICALS MUST BE MEASURED INSIDE A BAND. Across the whole page the panel
    # borders ink every column, so a page-wide column profile groups the six panels into
    # one run. Inside a band a panel wall is the column inked from floor to ceiling and a
    # figure never is.
    y0, y1 = ybands[0]
    band = ink[y0 + 4:y1 - 4]
    wall = np.where(band.sum(0) >= band.shape[0] * 0.90)[0]
    wg = group(wall) if len(wall) else []
    assert len(wg) == cols + 1, f'expected {cols+1} panel walls, got {len(wg)}'
    xb = [ (g[0] + g[1]) // 2 for g in wg ]
    out = []
    for r, (y0, y1) in enumerate(ybands):
        for c in range(cols):
            sub = A[y0+inset:y1-inset, xb[c]+inset:xb[c+1]-inset].copy()
            s = sub[:, :, :3]
            white = s.min(2) >= 224
            lab, _ = nd.label(white)
            edge = set(lab[0, :]) | set(lab[-1, :]) | set(lab[:, 0]) | set(lab[:, -1]); edge.discard(0)
            sub[:, :, 3] = np.where(np.isin(lab, list(edge)), 0, 255)
            m = sub[:, :, 3] > 0
            cl, n = nd.label(m)
            if n > 1:
                sz = nd.sum(m, cl, range(1, n + 1)); big = int(np.argmax(sz)) + 1
                ys, xs = np.where(cl == big)
                for j in range(1, n + 1):
                    if j == big: continue
                    cy, cx = np.where(cl == j)
                    # the beat NUMBER lives in the corner, clear of him; his own dust does not
                    if cy.max() < ys.min() or cy.min() > ys.max() or cx.max() < xs.min() - 12 \
                       or cx.min() > xs.max() + 12 or sz[j-1] < sz[big-1] * 0.02:
                        sub[cl == j, 3] = 0
            ys, xs = np.where(sub[:, :, 3] > 0)
            # ⛔ gap is measured INSIDE the crop. `y1` is a PAGE row and ys are crop rows;
            # mixing them adds each panel's own y0 to its gap, so rows register hundreds
            # of px apart and land outside the cell entirely.
            out.append((sub[ys.min():ys.max()+1, xs.min():xs.max()+1],
                        int(sub.shape[0] - 1 - ys.max()), r, c))   # px above the panel floor
    return out


if __name__ == '__main__':
    src, dst, rows, cols = sys.argv[1], pathlib.Path(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    dst.mkdir(parents=True, exist_ok=True)
    import json
    meta = {}
    for crop, gap, r, c in cut_grid(src, rows, cols):
        Image.fromarray(crop.astype('uint8'), 'RGBA').save(dst / f'r{r+1}c{c+1}.png')
        meta[f'r{r+1}c{c+1}'] = dict(gap=gap, h=int(crop.shape[0]), w=int(crop.shape[1]))
    (dst / 'meta.json').write_text(json.dumps(meta))
    print(f'{len(meta)} cells -> {dst}')
