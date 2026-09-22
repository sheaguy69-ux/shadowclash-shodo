#!/usr/bin/env python3
"""Cut the figures off a delivered layout page into loose transparent PNGs.

    python3 tools/sprites/cut_page.py <page.png> <outdir> --expect 5

The owner's pages vary — 2 up, 4 up, 3+2, 3 rows of 5 — so nothing here assumes a
grid. It segments FIGURES instead:

  * white is keyed by flooding from the page border, so enclosed white (between
    braced legs, inside a chain loop) is caught separately below;
  * panel RULES are dropped by shape: long, straight, and almost no fill inside
    their own bounding box;
  * every component over CORE px is a figure core. Everything smaller joins the
    nearest core if it is close enough — that is how detached chain links, FX
    streaks and dust stay with their figure — and is dropped otherwise, which is
    what removes the caption text and the numbered badges;
  * enclosed white slabs at the very bottom of a figure are removed by size AND
    height, because the border flood cannot reach them and they pack as a bright
    plate under her feet.

Figures come out ordered top-to-bottom then left-to-right, i.e. reading order.
"""
import argparse
import pathlib

import numpy as np
from PIL import Image
from scipy import ndimage as nd


def cut(path, expect=None, core_px=2500, join=70, top=0.13, verbose=True):
    A = np.asarray(Image.open(path).convert('RGB')).astype(int)
    H, W, _ = A.shape

    white = A.min(2) > 224

    # ⛔ PANEL RULES COME OFF BEFORE THE FLOOD, and they come off as ROWS AND COLUMNS,
    # not as components. A panel rectangle encloses its own white interior, so the
    # border flood cannot get inside it and the whole page keys as one solid blob;
    # and the rule is usually touching a figure, so it cannot be dropped as a
    # component either.
    #
    # The threshold is 85%, not 40%: her mane is a solid black mass, so a row through
    # her shoulders clears 40% easily and erasing it shatters the page into strips
    # (143 "panels" on the heavy-chain page). A ruled line is drawn edge to edge and
    # nothing else on these pages is.
    ink = ~white
    kill_r = ink.sum(1) > W * 0.85
    kill_c = ink.sum(0) > H * 0.85
    white[kill_r, :] = True
    white[:, kill_c] = True

    seed = np.zeros((H, W), bool)
    seed[0, :] = seed[-1, :] = seed[:, 0] = seed[:, -1] = True
    alpha = ~nd.binary_propagation(seed & white, mask=white)
    alpha[kill_r, :] = False
    alpha[:, kill_c] = False

    lab, n = nd.label(alpha, np.ones((3, 3)))
    objs = nd.find_objects(lab)
    areas = nd.sum(alpha, lab, range(1, n + 1))
    cent = nd.center_of_mass(alpha, lab, range(1, n + 1))

    # ⛔ PANELS ARE THE COMPLEMENT OF THE RULES. Not a grid — the owner's pages run
    # 3-over-2, 4-over-3, 2-up, 4-up — and not distance clustering either, because a
    # thrown chain reaches further across the page than the gap to the next figure,
    # and a chain of links is indistinguishable from a row of letters by size,
    # brightness or spacing (all three were measured and all three fail).
    #
    # Whatever the layout, every panel is a rectangle bounded by ruled lines, so the
    # connected regions of NOT-A-RULE are exactly the panels. Caption strips come out
    # as panels too, and drop out because their biggest component is under core_px.
    # A RECURSIVE X-Y CUT, because a rule only spans its own region: the vertical
    # separators between the top three heavy-chain panels stop at that row, so
    # measuring them against the FULL page height finds nothing. Split on whatever
    # runs edge-to-edge within the current region, then recurse into each piece.
    def split(y0, y1, x0, x1, depth=0):
        r = ink[y0:y1, x0:x1]
        h, w = r.shape
        if h < 20 or w < 20 or depth > 6:
            return [(y0, y1, x0, x1)]
        rr = np.nonzero(r.sum(1) > w * 0.85)[0]
        cc = np.nonzero(r.sum(0) > h * 0.85)[0]
        for cuts, horiz in ((rr, True), (cc, False)):
            runs, s = [], None
            for i, v in enumerate(cuts):
                if s is None or v != cuts[i - 1] + 1:
                    if s is not None:
                        runs.append((cuts[s], cuts[i - 1] + 1))
                    s = i
            if s is not None:
                runs.append((cuts[s], cuts[-1] + 1))
            keep = [(a, b) for a, b in runs if 6 < a and b < (h if horiz else w) - 6]
            if keep:
                out, prev = [], 0
                for a, b in keep + [((h if horiz else w), None)]:
                    if a - prev > 12:
                        out += (split(y0 + prev, y0 + a, x0, x1, depth + 1) if horiz
                                else split(y0, y1, x0 + prev, x0 + a, depth + 1))
                    prev = b if b else prev
                if len(out) > 1:
                    return out
        return [(y0, y1, x0, x1)]

    panels = split(0, H, 0, W)
    if verbose:
        print(f'  {n} ink parts, {len(panels)} panel region(s)')

    groups, order = [], []
    for (y0, y1, x0, x1) in panels:
        if y1 < H * top:
            continue          # the page title
        inside = [k for k in range(n)
                  if y0 <= cent[k][0] < y1 and x0 <= cent[k][1] < x1]
        if not inside or max(areas[k] for k in inside) < core_px:
            continue          # a caption strip or the page title, not a figure panel
        # The caption often shares the panel with the figure rather than getting its
        # own strip. Everything sitting below the figure's own bounding box, in the
        # bottom fifth of the panel, is that caption — the badge and the text.
        core = max(inside, key=lambda k: areas[k])
        foot = objs[core][0].stop
        cut_y = max(foot, y0 + (y1 - y0) * 0.80)
        inside = [k for k in inside if objs[k][0].start < cut_y]
        # A panel can be wider than its drawing — the heavy-chain page runs three
        # over two, so the bottom pair are double-width and the empty half brings a
        # stray with it. Nothing of hers reaches a third of the page from her body.
        cy, cx = objs[core]
        inside = [k for k in inside
                  if max(cy.start - objs[k][0].stop, objs[k][0].start - cy.stop, 0) < W * 0.30
                  and max(cx.start - objs[k][1].stop, objs[k][1].start - cx.stop, 0) < W * 0.30]
        groups.append(inside)
        order.append((y0, x0))
    groups = [g for _, g in sorted(zip(order, groups), key=lambda t: t[0])]

    out = []
    for g, ks in enumerate(groups):
        m = np.isin(lab, [k + 1 for k in ks])
        # The white between her braced legs is enclosed by her own silhouette, so the
        # border flood never reaches it and it packs as a bright plate at her feet.
        # The cut-off is measured off her BODY, not the whole figure: a chain hanging
        # low drags the figure's bbox down and the leg gap ends up in its top 80%.
        # Her white mane streaks are the only other enclosed white and they are all
        # above the body's midpoint, so nothing of hers is lost.
        core = nd.binary_erosion(m, np.ones((13, 13)))
        if core.any():
            cl, cn = nd.label(core, np.ones((3, 3)))
            cs = nd.sum(core, cl, range(1, cn + 1))
            bod = nd.binary_dilation(cl == int(np.argmax(cs)) + 1, np.ones((13, 13))) & m
            by = np.nonzero(bod)[0]
            mid = (by.min() + by.max()) / 2
            nearwhite = m & (A.min(2) > 228)
            wl, wn = nd.label(nearwhite, np.ones((3, 3)))
            for k in range(1, wn + 1):
                b = wl == k
                if b.sum() > 100 and np.nonzero(b)[0].mean() > mid:
                    m &= ~b
        ys, xs = np.nonzero(m)
        sub = A[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        ka = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        out.append(Image.fromarray(np.dstack([sub, np.where(ka, 255, 0)]).astype(np.uint8), 'RGBA'))
        if verbose:
            print(f'  fig {g+1:2d}  {out[-1].size}  {int(m.sum()):6d}px  '
                  f'{len(ks)} part{"" if len(ks)==1 else "s"}')
    if expect and len(out) != expect:
        print(f'  ⚠ expected {expect} figures, segmented {len(out)} — '
              f'tune --core / --join before packing')
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('page')
    ap.add_argument('outdir')
    ap.add_argument('--expect', type=int, default=None)
    ap.add_argument('--core', type=int, default=2500)
    ap.add_argument('--join', type=int, default=70)
    ap.add_argument('--top', type=float, default=0.13,
                    help='ignore panels entirely above this fraction of the page — the title')
    ap.add_argument('--prefix', default='f')
    a = ap.parse_args()
    d = pathlib.Path(a.outdir)
    d.mkdir(parents=True, exist_ok=True)
    print(pathlib.Path(a.page).name)
    for i, im in enumerate(cut(a.page, a.expect, a.core, a.join, a.top)):
        im.save(d / f'{a.prefix}{i+1}.png')


if __name__ == '__main__':
    main()
