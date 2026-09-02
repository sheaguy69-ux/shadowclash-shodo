#!/usr/bin/env python3
"""Cut a one-row delivery board (N poses left-to-right) into loose keyed PNGs.

    python3 tools/sprites/cut_strip.py <board.png> <outdir> --n 6

WHY THIS AND NOT cut_page.py: cut_page segments FIGURES by connected components.
That is right for a page whose figures stand apart, and wrong for these boards —
Oni's red claw arc and his smoke column BRIDGE two neighbours, so every component
chains into one blob and the page segments as a single figure no matter how far
--join is wound down (verified 70/40/25/15/8, all gave 1).

A one-row board does not need components. The poses are laid out on a pitch, so
the cut is a 1-D problem: score every column by ink, then put N-1 cuts near the
expected pitch, each nudged to the emptiest column in its window. FX that spans a
boundary is split at its thinnest point, which is where a human would cut it too.

The white key is a border flood (not a global threshold) so enclosed white — the
mask, the wrappings — survives; see key_edge.py, same rule.
"""
import argparse
import json
import pathlib

import numpy as np
from PIL import Image
from scipy import ndimage as nd

WHITE = 224          # >= this on every channel is page white
TITLE = 0.13         # top fraction holding the caption, never a pose


def enclosed_page_white(rgb, page):
    """Yield masks of page-white pockets sealed inside the drawing by his own outline.

    These cannot be keyed by brightness: his MASK is white too, and the two overlap.
    Measured off the Aug-9 boards, a background pocket reads core 244.9 with a channel
    spread of 0.04 while a piece of mask right beside it reads 243.5 / 0.67 — nearly the
    same brightness, very different NEUTRALITY, because the mask carries a warm tint and
    printed page white does not. So take a pocket as background when it is either bright
    and near-neutral, or merely light and DEAD neutral. Erode 2px first: the anti-aliased
    rim is common to both and drags the mean.
    """
    white = rgb.min(2) >= WHITE
    lab, n = nd.label(white & ~page)
    for i in range(1, n + 1):
        m = lab == i
        core = nd.binary_erosion(m, np.ones((3, 3)), iterations=2)
        if core.sum() < 12:
            core = m                      # too thin to erode; judge it whole
        mean = rgb[core].mean(0)
        v, spread = mean.mean(), mean.max() - mean.min()
        if (v >= 246 and spread < 1.0) or (v >= 240 and spread < 0.30):
            yield m


def cut(path, n=6, title=TITLE, pad=6, verbose=True, forced=None, keep_enclosed=False,
        drop_pockets=()):
    im = Image.open(path).convert('RGBA')
    A = np.asarray(im).astype(int)
    H, W = A.shape[:2]
    rgb = A[:, :, :3]

    ink = rgb.min(2) <= WHITE
    ink[:int(H * title)] = False          # drop the caption band

    col = ink.sum(0).astype(float)
    body = np.where(col > 0)[0]
    if body.size == 0:
        raise SystemExit('no ink below the title band')
    x0, x1 = body[0], body[-1]
    pitch = (x1 - x0 + 1) / n

    # N-1 cuts, each snapped to the emptiest column within +/- 35% of the pitch.
    #
    # ⛔ FX IS NOT SPLITTABLE. A claw arc or a speed streak reads as one object; slicing
    # it leaves a hard vertical edge in BOTH neighbours (the cartwheel's arc did exactly
    # that at x=983). Saturated red is therefore scored as if it were solid ink, so a
    # cut is pushed off the FX rather than through it. If the whole window is FX the
    # board needs --cuts; nothing here guesses which figure the FX belongs to.
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    fx = (r > 120) & (r - g > 60) & (r - b > 60)
    fx[:int(H * title)] = False
    score = col + fx.sum(0) * 50.0

    if forced:
        cuts = sorted(int(c) for c in forced)
        if len(cuts) != n - 1:
            raise SystemExit(f'--cuts needs {n-1} values for --n {n}, got {len(cuts)}')
    else:
        cuts = []
        for i in range(1, n):
            guess = int(x0 + pitch * i)
            w = max(8, int(pitch * 0.35))
            lo, hi = max(x0 + 1, guess - w), min(x1 - 1, guess + w)
            cuts.append(lo + int(np.argmin(score[lo:hi + 1])))
    bounds = [x0] + cuts + [x1 + 1]
    if verbose:
        bad = [c for c in cuts if fx[:, c].any()]
        if bad:
            print(f'  ⚠ cut(s) still crossing FX at x={bad} — pass --cuts')

    # border flood: page white that touches the frame edge becomes transparent,
    # white sealed inside the drawing (mask, wraps) stays opaque.
    white = rgb.min(2) >= WHITE
    lab, _ = nd.label(white)
    edge = set(lab[0, :]) | set(lab[-1, :]) | set(lab[:, 0]) | set(lab[:, -1])
    edge.discard(0)
    page = np.isin(lab, list(edge))

    out = A.copy()
    out[:, :, 3] = np.where(page, 0, 255)

    # ⛔ ENCLOSED PAGE WHITE. The flood only reaches white joined to the frame, so a
    # pocket sealed by his own outline — between arm and torso, inside the crook of a
    # knee — stays opaque and ships as a white blob on the sprite. It cannot be keyed
    # by brightness alone: his MASK is white too, and both clear 224.
    #
    # They separate on TINT, measured off these four boards, not guessed. Page white
    # is neutral and bright (core mean 247-250, channel spread 0.04-0.52); the mask is
    # dimmer and warm (core mean 234-244, spread 1.85-3.52). Erode 2px first so the
    # anti-aliased rim, which is common to both, cannot drag the mean.
    # ⛔ OPT OUT WHEN THE ART'S OWN WHITE IS NEUTRAL. The tint test above separates page
    # white from a WARM mask (Aug-9 Oni boards: page 244.9/spread 0.04 vs mask 243.5/0.67).
    # It cannot separate page white from a PURE-NEUTRAL white, and the Sep-2 shodo trio
    # draws Mizu's and Tsubasa's eyes exactly that way — measured core mean 249.8-251.4,
    # spread 0.03-0.30, i.e. dead-on the page-white signature. Left on, it silently keys
    # BOTH EYES OUT OF EVERY BEAT (verified: Mizu's 684px eye fell to a 27px remnant).
    # On those boards no sealed page-white pocket exists inside the figure at all — every
    # pocket >=150px in the figure band is an eye — so the rule has nothing to do there.
    #
    # keep_enclosed does NOT mean "keep every pocket" — that is just as wrong the other
    # way. Tsubasa has BOTH on one board: white eyes high in the mask, and real page
    # showing through the gap between his arm and his hip. Measured, they are the same
    # colour (eye cores 249.0-251.1, hip cores 244.1-248.9, page 251.4) and the same
    # neutrality, so no threshold on the pocket itself can tell them apart. Ring
    # brightness nearly works and then fails on Mizu's CATCH, where her own hanbō crosses
    # her face and lights the ring to p75 201.
    #
    # What does separate them is WHERE THEY SIT. Interior white that belongs to the art
    # is head-and-shoulder detail — the eyes, Shin's pale shoulder plate. Page showing
    # through is a gap between limbs, and that is lower down the body. So keep pockets in
    # the top keep_frac of the figure and drop the rest. Verified on all three boards:
    # every eye and Shin's shoulder plate sit at 32-40% of figure height, every hip gap
    # and every caption counter sits below 45%.
    # ⛔ WHEN IN DOUBT, KEEP THE ART. A position rule was tried here (keep pockets in the
    # figure's top fraction, drop the rest) and it is WRONG: an 18-cell adversarial pass
    # caught it deleting Mizu's specular robe highlights, Shin's white brush glyphs, and
    # THE STEEL INSIDE TSUBASA'S KUNAI BLADES — 14 beats of drawn art, one graded a
    # blocker. Every separator that was measured fails on this art: colour (eye cores
    # 249.0-251.1 vs hip cores 244.1-248.9 vs page 251.4), neutrality, flatness, ring
    # brightness (dies on Mizu's CATCH, her hanbō lights the ring to p75 201), and
    # re-flooding at a looser threshold (all pockets stay sealed down to >=140).
    #
    # The two errors are not symmetric. Keeping a page pocket leaves a white patch the
    # owner can SEE and rule on; deleting a highlight destroys his art invisibly. So keep
    # every pocket and PRINT them, so a leftover is always reported and never silent.
    # --drop-pocket names a pocket that a HUMAN looked at and called page. That is the
    # only reliable input here, and it is auditable: the list below prints, the operator
    # checks the crops, and the coordinates go back in. Nothing is guessed.
    kept, dropped = [], []
    for m in enclosed_page_white(rgb, page):
        if keep_enclosed:
            ys, xs = np.nonzero(m)
            cx, cy = int(xs.mean()), int(ys.mean())
            hit = any(abs(cx - dx) <= 25 and abs(cy - dy) <= 25 for dx, dy in drop_pockets)
            if not hit:
                kept.append((int(m.sum()), cx, cy))
                continue
            dropped.append((int(m.sum()), cx, cy))
        out[m, 3] = 0
    if verbose and keep_enclosed:
        kept.sort(reverse=True)
        big = [k for k in kept if k[0] >= 120]
        print(f'  kept {len(kept)} enclosed-white pockets ({len(big)} >=120px) — '
              f'eyes and highlights. CHECK each for page left at a limb gap:')
        for sz, cx, cy in big[:14]:
            print(f'      {sz:>5}px at x{cx} y{cy}')
        if dropped:
            print(f'  dropped {len(dropped)} pocket(s) named on the command line: '
                  + ', '.join(f'{sz}px@{cx},{cy}' for sz, cx, cy in dropped))

    cells = []
    for i in range(n):
        a, b = bounds[i], bounds[i + 1]
        sub = out[:, a:b].copy()

        # ⛔ DROP CAPTION TEXT BY COMPONENT SIZE, NOT BY CROPPING ROWS. Narrowing the
        # band to its dense rows looks reasonable and quietly DECAPITATES him: his horns
        # and hood are narrower than his torso, so those rows carry less ink and fall
        # under any density threshold — measured 20-38px lost off the top of every row
        # on the labelled mobility sheet. A row title and a frame number are instead
        # small, SEPARATE blobs; his body is one big one. So keep components that are a
        # real fraction of the largest, plus anything sitting close to it (detached FX
        # streaks, dust, a claw tip), and drop the rest.
        m = sub[:, :, 3] > 0
        clab, ncomp = nd.label(m)          # NOT `n` — that is the cell count
        if ncomp > 1:
            sizes = nd.sum(m, clab, range(1, ncomp + 1))
            big = int(np.argmax(sizes)) + 1
            ys, xs = np.where(clab == big)
            y0b, y1b, x0b, x1b = ys.min(), ys.max(), xs.min(), xs.max()
            # ⛔ MEASURE "ABOVE"/"BELOW" AGAINST HIS BODY, NOT AGAINST HIS FX. A spark
            # spray or a blade arc is part of the main component and drags y0b up into
            # the numeral band, so a frame number stops reading as "above him" and ships
            # as a floating glyph (URONAME 1 beat 5, a "5" welded over the burst). The
            # body is the WIDE part of the component and FX is thin, so take the band
            # where the component is at least a quarter of its own widest row.
            wid = (clab == big).sum(1)
            thick = np.where(wid >= wid.max() * 0.25)[0]
            if thick.size:
                y0b, y1b = int(thick[0]), int(thick[-1])
            for j in range(1, ncomp + 1):
                if j == big:
                    continue
                cy, cx = np.where(clab == j)
                # ⛔ A DETACHED BLOB TOUCHING THE CUT COLUMN IS THE NEIGHBOUR'S, NOT HIS.
                # When FX genuinely spans two poses the cut has to land somewhere, and the
                # slice leaves a stub at x=0 (or the far edge) of the cell downstream. It is
                # never part of this pose: on the wire-shot page cell 4 inherited an 865px
                # bar of cell 3's taut wire and cell 6 a 333px stub of cell 5's coil, both
                # floating in empty air well clear of him. His OWN detached FX — speed lines
                # off the claw, dust, a thrown wire tip — grows out of the figure and dies
                # before the boundary, so it never touches the edge and survives this.
                #
                # Checked BEFORE the 5%-of-main keep below: a sliced stub is not made his by
                # being big, and the taut-wire bar is the largest fragment on the page.
                if cx.min() == 0 or cx.max() == sub.shape[1] - 1:
                    sub[clab == j, 3] = 0
                    continue
                # A row TITLE sits wholly above the figure and a frame NUMBER wholly
                # below it, so vertical separation is what identifies them — proximity
                # is not enough, since both are only a few px clear of the body. FX
                # streaks, dust and a detached claw tip all OVERLAP his vertical span,
                # so they survive this and the text does not.
                above = cy.max() < y0b
                below = cy.min() > y1b
                near_x = cx.max() >= x0b - 20 and cx.min() <= x1b + 20
                if above or below or not near_x:
                    sub[clab == j, 3] = 0
                    continue
                if sizes[j - 1] < sizes[big - 1] * 0.05 and not near_x:
                    sub[clab == j, 3] = 0

        solid = sub[:, :, 3] > 0
        solid[:int(H * title)] = False
        ys, xs = np.where(solid)
        if ys.size == 0:
            cells.append(None)
            if verbose:
                print(f'  cell {i+1}: EMPTY  x {a}-{b}')
            continue
        t, bm = ys.min(), ys.max()
        l, r = xs.min(), xs.max()
        crop = sub[max(0, t - pad):bm + 1 + pad, max(0, l - pad):r + 1 + pad]
        cells.append((crop, a + l, t, r - l + 1, bm - t + 1))
        if verbose:
            print(f'  cell {i+1}: {crop.shape[1]:>4}x{crop.shape[0]:<4} '
                  f'page-x {a+l:>4}  ink={int(col[a:b].sum()):>7}')
    return cells, bounds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('board')
    ap.add_argument('outdir')
    ap.add_argument('--n', type=int, default=6)
    ap.add_argument('--prefix', default='c')
    ap.add_argument('--title', type=float, default=TITLE,
                    help='top fraction to ignore; 0 when the board has no caption')
    ap.add_argument('--cuts', type=int, nargs='*', default=None,
                    help='explicit cut columns (n-1 of them) when FX spans a boundary')
    ap.add_argument('--keep-enclosed-white', action='store_true',
                    help="keep enclosed white in the figure's top fraction — use when the "
                         "art's own white is pure neutral (eyes), which the tint test "
                         'cannot tell from page white')
    ap.add_argument('--drop-pocket', action='append', default=[], metavar='X,Y',
                    help='with --keep-enclosed-white, drop the enclosed pocket centred near '
                         'X,Y — for page you have LOOKED at and confirmed. Repeatable.')
    a = ap.parse_args()

    print(pathlib.Path(a.board).name)
    cells, bounds = cut(a.board, a.n, title=a.title, forced=a.cuts,
                        keep_enclosed=a.keep_enclosed_white,
                        drop_pockets=[tuple(int(v) for v in t.split(',')) for t in a.drop_pocket])
    d = pathlib.Path(a.outdir)
    d.mkdir(parents=True, exist_ok=True)
    kept = 0
    # ⛔ EMIT THE REGISTRATION. Each cell is cropped to its own bbox, so the shared origin
    # the six poses were drawn against does not survive into the files — and nothing
    # downstream can re-derive it, because every cell now starts at its own ink. footY and
    # a common baseline are exactly what the packer needs, so record them here while the
    # board is still in hand.
    reg = {'board': pathlib.Path(a.board).name, 'n': a.n, 'cuts': [int(b) for b in bounds[1:-1]],
           'cells': {}}
    for i, c in enumerate(cells, 1):
        if c is None:
            continue
        Image.fromarray(c[0].astype(np.uint8)).save(d / f'{a.prefix}{i}.png')
        _, bx, by, bw, bh = c
        reg['cells'][f'{a.prefix}{i}'] = {
            'board_x': int(bx), 'board_y': int(by), 'w': int(bw), 'h': int(bh),
            'board_foot_y': int(by + bh - 1),
        }
        kept += 1
    feet = [v['board_foot_y'] for v in reg['cells'].values()]
    if feet:
        reg['board_foot_y_min'] = min(feet)
        reg['board_foot_y_max'] = max(feet)
        reg['foot_spread_px'] = max(feet) - min(feet)
    (d / 'registration.json').write_text(json.dumps(reg, indent=2))
    print(f'  wrote {kept}/{a.n} -> {d}')
    print(f'  cuts at x: {bounds[1:-1]}')
    if feet:
        print(f'  board foot line {min(feet)}-{max(feet)} (spread {max(feet)-min(feet)}px) '
              f'-> registration.json')


if __name__ == '__main__':
    main()
