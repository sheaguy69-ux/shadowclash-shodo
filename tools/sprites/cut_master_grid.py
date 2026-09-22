#!/usr/bin/env python3
"""Cut the owner's two Aug-9 master sheets (4 rows x 8 states) into named cells.

    python3 tools/sprites/cut_master_grid.py states  /tmp/oni/states
    python3 tools/sprites/cut_master_grid.py moveset /tmp/oni/moveset

The sheets are a labelled grid, not a bare strip: a text block on the LEFT names the
row, a caption sits above every cell, and the attacks sheet carries a footer note.
None of that is art. Columns are found by longest vertical INK RUN, which separates a
body from a line of header text, and one set of bounds is shared by every row so a
wider header cannot shift a row by one cell. That is why this does not just call
cut_strip: cut_strip assumes everything below its title band is a pose, which the row
header would break.

Names come from the owner's own captions, so a cell's filename is its state.
"""
import argparse
import pathlib
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as nd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from cut_strip import enclosed_page_white          # noqa: E402  one shared rule

WHITE = 224

SHEETS = {
    'states': dict(
        file='MASTER-STATES-4x8.png',
        bands=[(30, 266), (268, 515), (518, 756), (759, 1020)],
        names=[
            ['idle', 'run_start', 'run_loop1', 'run_accel',
             'run_loop2', 'dash_start', 'dash_burst', 'dash_end'],
            ['wall_cling', 'wall_cling_still', 'wall_jump_leap', 'roll_start',
             'roll_mid', 'roll_end', 'roll_recover', 'stand'],
            ['jump_takeoff', 'jump_rise', 'jump_peak', 'jump_fall',
             'backflip', 'backflip_land', 'cartwheel_fwd', 'land_recover'],
            ['hurt_light', 'air_tumble1', 'air_tumble2', 'ground_slide',
             'slide_end', 'getup_start', 'getup', 'getup_stand'],
        ]),
    'moveset': dict(
        file='MASTER-MOVESET-MATRIX-v2.png',
        bands=[(34, 261), (294, 502), (523, 726), (737, 978)],
        clean=True,
        names=[
            # ROW 1 — crouching, sliding & rising kicks
            ['crouch_stance', 'ground_brace', 'sweep_stretch1', 'sweep_stretch2',
             'prone_recover', 'low_guard', 'axe_kick', 'rising_crescent'],
            # ROW 2 — low sweeps, dashes & rising punches
            ['deep_crouch', 'hands_down', 'slide_sweep1', 'slide_sweep2',
             'knee_guard', 'fists_cocked', 'leap_punch', 'rising_upper'],
            # ROW 3 — claw gauntlet strikes & ground impacts
            ['claws_out1', 'claws_out2', 'claw_thrust1', 'claw_thrust2',
             'ground_slam', 'rising_slash1', 'rising_slash2', 'rising_arc'],
            # ROW 4 — aerial kicks, lunges & dive slams
            ['air_kick1', 'air_kick2', 'air_lunge1', 'air_lunge2',
             'dive_prep1', 'dive_prep2', 'dive_bomb', 'dive_impact'],
        ]),
}

# The CLEAN sheets carry the same states with no caption, header or footer, so they
# are what gets packed and the labelled ones stay the naming reference. Nothing has
# to be dodged here — which means the caption strip must NOT be trimmed, or it eats
# the top of every pose.
SHEETS['moveset-v3'] = dict(
    file='MASTER-MOVESET-MATRIX-v3.png',
    bands=[(26, 249), (270, 480), (499, 725), (740, 974)],
    names=SHEETS['moveset']['names'], clean=True)
SHEETS['moveset-v1'] = dict(
    file='MASTER-MOVESET-MATRIX-v1.png',
    bands=[(30, 265), (300, 505), (530, 730), (745, 985)],
    names=SHEETS['moveset']['names'], clean=True)
SHEETS['states-clean'] = dict(
    file='MASTER-STATES-CLEAN.png',
    bands=[(21, 317), (349, 606), (651, 886), (915, 1002)],
    names=SHEETS['states']['names'], clean=True)


# ---- the Aug-10 DIRECTIONAL masters: 4 rows x 6 beats, one family per row ----------
# These are the six-beat coverage docs/ONI-FRAMES-NEEDED.md §2 said was missing, and the
# row order is the owner's own: forward, back, up/neutral, down. Six beats is exactly
# what dirCells() wants (`<key>1`..`<key>6`), so a row maps to a family with no padding
# and no borrowed beats. Bands were measured off each board, not assumed — the four
# boards share a page size but not a row rhythm.
def _dir(file, bands, keys):
    return dict(file=file, bands=bands, cols=6, clean=True,
                names=[[f'{k}{i}' for i in range(1, 7)] for k in keys])


SHEETS['heavy-dir'] = _dir(
    'MASTER-HEAVY-DIR-4x6.png',
    [(49, 254), (298, 495), (512, 757), (803, 993)],
    ['hfwd', 'hback', 'hup', 'hdown'])
SHEETS['aerial-dir'] = _dir(
    'MASTER-AERIAL-DIR-4x6.png',
    [(42, 248), (296, 497), (528, 742), (769, 1013)],
    ['afwd', 'aback', 'aneu', 'adown'])
SHEETS['special-dir'] = _dir(
    'MASTER-SPECIAL-DIR-4x6.png',
    [(21, 236), (271, 482), (515, 748), (762, 1031)],
    ['sfwd', 'sback', 'sup', 'sdown'])
SHEETS['light-dir'] = _dir(
    'MASTER-LIGHT-DIR-4x6.png',
    [(40, 254), (306, 517), (579, 753), (804, 1032)],
    ['glneu', 'glfwd', 'gldown', 'glup'])
SHEETS['group3'] = dict(**_dir(
    'MASTER-GROUP3-4x6.png',
    [(77, 304), (313, 540), (549, 771), (780, 1003)],
    ['g3wknife', 'g3wslice', 'g3bflip', 'g3roll']), numbered=True)
SHEETS['wire-grabs'] = _dir(
    'MASTER-WIRE-GRABS-v2-4x6.png',
    [(75, 269), (307, 501), (544, 736), (777, 965)],
    ['wkatana', 'wclaw', 'wknife', 'wslice'])


def key(rgb):
    """Border-flood page white, then purge the pockets it cannot reach.

    The enclosed-white rule lives in cut_strip so there is ONE definition of what
    counts as page white on these boards — it was tuned against measurements and
    two copies would drift apart the first time it is retuned."""
    white = rgb.min(2) >= WHITE
    lab, _ = nd.label(white)
    edge = set(lab[0, :]) | set(lab[-1, :]) | set(lab[:, 0]) | set(lab[:, -1])
    edge.discard(0)
    page = np.isin(lab, list(edge))
    alpha = np.where(page, 0, 255)
    for m in enclosed_page_white(rgb, page):
        alpha[m] = 0
    return alpha


def columns(mask, n, W):
    """The 8 cells as (x0, x1).

    Clustering alone does not survive these sheets: the row-header text block sits
    in the same rows as the figures (so it clusters as a 9th "figure"), and row 3's
    claw arcs bridge every figure into ONE blob. So find the header GUTTER first —
    the wide empty column band that separates the text from the grid — then split
    the remainder on the cell pitch, nudging each cut to the emptiest column. The
    grid is regular, so pitch is reliable once the header is out of the way.
    """
    col = mask.sum(0).astype(float)

    # ⛔ TELL THE HEADER FROM A FIGURE BY RUN LENGTH, NOT BY GAPS. A gutter scan
    # fails when the header sits tight against column 1 (no 22px of clear air), and
    # then the text becomes "cell 1" and the row's LAST state is pushed off the
    # sheet. But a body is one TALL unbroken column of ink, while a text line is a
    # short run — so the first column whose longest vertical run clears a quarter of
    # the band is where the art starts, whatever the header does.
    H = mask.shape[0]
    longest = np.zeros(W)
    for x in range(W):
        c = mask[:, x]
        if not c.any():
            continue
        best = run = 0
        for v in c:
            run = run + 1 if v else 0
            if run > best:
                best = run
        longest[x] = best
    # ⛔ ...AND BY WIDTH, OR A RULED LINE BECOMES COLUMN 1. Run length alone cannot tell
    # a body from a border: the vertical rule dividing the label from the grid, and the
    # rounded box around a label on the specials sheet, are both full-height, so both
    # clear the run test — and neither can be caught by ink MASS either, since a
    # full-height 1px line is a full column of ink. Measured on those two boards they set
    # the grid origin 30-140px left of the real first pose and dragged every cut with it
    # (one specials row resolved a 96px "cell"). What separates them is WIDTH: a pose is
    # tens of columns of tall ink side by side, a border is one to three. So keep only
    # runs of tall columns that are themselves wide.
    tall = (longest >= H * 0.25)
    art = np.where(tall)[0]
    if art.size:
        keep = np.zeros_like(tall)
        s = None
        for x in range(W + 1):
            if x < W and tall[x]:
                if s is None:
                    s = x
            elif s is not None:
                if x - s >= 8:
                    keep[s:x] = True
                s = None
        if keep.any():
            art = np.where(keep)[0]
    if art.size == 0:
        return []
    x0, x1 = int(art[0]), int(art[-1])
    pitch = (x1 - x0 + 1) / n

    cuts = []
    for i in range(1, n):
        guess = int(x0 + pitch * i)
        w = max(6, int(pitch * 0.30))
        lo, hi = max(x0 + 1, guess - w), min(x1 - 1, guess + w)
        cuts.append(lo + int(np.argmin(col[lo:hi + 1])))
    bounds = [x0] + cuts + [x1]
    return [(bounds[i], bounds[i + 1]) for i in range(n)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('sheet', choices=sorted(SHEETS))
    ap.add_argument('outdir')
    ap.add_argument('--root', default='RECOVERY/oni-founder/boards-aug9')
    ap.add_argument('--pad', type=int, default=4)
    a = ap.parse_args()

    spec = SHEETS[a.sheet]
    src = pathlib.Path(a.root) / spec['file']
    A = np.asarray(Image.open(src).convert('RGB')).astype(int)
    H, W, _ = A.shape
    alpha = key(A)
    out = np.dstack([A, alpha]).astype(np.uint8)

    d = pathlib.Path(a.outdir)
    d.mkdir(parents=True, exist_ok=True)
    print(src.name)

    # ⛔ ONE SET OF BOUNDS FOR THE WHOLE SHEET. The grid is aligned, but the row
    # HEADER is not: row 3's text block runs ~150px wider than row 1's, so a
    # per-row gutter scan puts row 3's first cut inside the header and every cell
    # in that row shifts one to the right (the last state falls off the sheet).
    # Solve the columns on the row whose header is NARROWEST — its gutter is the
    # only one guaranteed to sit left of column 1 — then reuse them everywhere.
    clean = spec.get('clean', False)
    NC = spec.get('cols', 8)
    per_row = []
    for (y0, y1) in spec['bands']:
        band = alpha[y0:y1] > 0
        zone = band if clean else band[int(band.shape[0] * 0.35):]
        per_row.append(columns(zone, NC, W))
    good = [c for c in per_row if len(c) == NC]
    if not good:
        sys.exit(f'no row resolved {NC} columns')
    shared = min(good, key=lambda c: c[0][0])
    print(f'  grid from x={shared[0][0]} to {shared[-1][1]}, '
          f'pitch~{(shared[-1][1]-shared[0][0])/NC:.0f}px')

    total = 0
    for r, ((y0, y1), names) in enumerate(zip(spec['bands'], spec['names']), 1):
        # ⛔ PER-ROW COLUMNS ONCE THE HEADER IS EXCLUDED BY WIDTH. Sharing one bounds set
        # was the right answer while a wide row header could shift a row by a whole cell,
        # but the width filter in columns() now drops headers, rules and label boxes
        # outright — and sharing then does its own damage, because it forces every row
        # onto the leftmost row's origin. Measured on these four boards, shared bounds put
        # ink across nearly every interior boundary (heavy row 1 alone split four cells);
        # per-row bounds cut that to 156/26/36/88px total, all of it thin FX.
        runs = per_row[r - 1] if len(per_row[r - 1]) == NC else shared
        for c, ((x0, x1), nm) in enumerate(zip(runs, names), 1):
            sub = out[y0:y1, x0:x1 + 1].copy()
            # ⛔ AND WHAT STILL CROSSES BELONGS TO THE NEIGHBOUR. Same rule as cut_strip:
            # when a slash arc or a taut wire genuinely spans two poses the cut has to
            # land somewhere, and the stub it leaves floats in empty air beside the wrong
            # fighter. His own FX grows out of the body and dies before the boundary.
            sm = sub[:, :, 3] > 0
            slab, sn = nd.label(sm)
            if sn > 1:
                ssz = nd.sum(sm, slab, range(1, sn + 1))
                sizes = ssz
                sbig = int(np.argmax(ssz)) + 1
                for j in range(1, sn + 1):
                    if j == sbig:
                        continue
                    jy, jx = np.where(slab == j)
                    if jx.min() == 0 or jx.max() == sub.shape[1] - 1:
                        sub[slab == j, 3] = 0
                        continue
                    # ...and a hairline that runs most of the cell wide is the printed
                    # ROW SEPARATOR, which the band can clip into on a short row (it
                    # shipped across the top of hup2). No pose or FX is 4px tall and
                    # half a cell wide.
                    if (jy.max() - jy.min() <= 4
                            and jx.max() - jx.min() >= sub.shape[1] * 0.40):
                        sub[slab == j, 3] = 0
                        continue
                    # ...and a small blob wholly ABOVE or BELOW the figure is a CAPTION, the
                    # same rule cut_strip uses. The Aug-10 GROUP 3 board numbers every cell
                    # in red and boxes each one, and both survived every rule here: the
                    # numbers sit clear above his head and the box edges are thin verticals
                    # that never reach the cut column. Vertical separation is what identifies
                    # them — his own FX and a detached claw tip always OVERLAP his span.
                    # ⛔ ...AND ONLY IF IT IS COMPACT, BECAUSE FX FLOATS ABOVE HIM TOO. Being
                    # clear of his body is NOT enough to call something a caption: the rising
                    # spiral's topmost arc sits wholly above his head and a bare
                    # above/below test deleted it (sup5, 237px of FX gone). A numeral is
                    # compact — roughly as tall as it is wide — while an FX stroke is long
                    # and thin: measured, that arc is 79x10, aspect 7.9, fill 0.30. So the
                    # caption rule only fires on text-shaped blobs and leaves strokes alone.
                    bys, bxs = np.where(slab == sbig)
                    jh = jy.max() - jy.min() + 1
                    jw = jx.max() - jx.min() + 1
                    compact = 0.3 <= jw / jh <= 2.5
                    if compact and (jy.max() < bys.min() or jy.min() > bys.max()):
                        sub[slab == j, 3] = 0
                        continue
                    # a thin tall line that is not part of him is a PANEL BORDER
                    if (jx.max() - jx.min() <= 4
                            and jy.max() - jy.min() >= sub.shape[0] * 0.25):
                        sub[slab == j, 3] = 0
                        continue
                    # ⛔ AND THE CELL NUMBER LIVES IN THE TOP-LEFT CORNER, WELDED TO ITS BOX.
                    # On the GROUP 3 board every cell is numbered in red AND boxed, and the
                    # numeral touches the box rule — so the two label as ONE blob that is
                    # neither compact nor clear of his body, and both survived the rules
                    # above. What is reliable here is POSITION: this layout always puts the
                    # number in the top-left corner, where none of his art or FX begins.
                    # Bounded to the corner and to blobs far smaller than him, so a stroke
                    # that merely passes through the corner is not at risk.
                    # OPT-IN PER SHEET (`numbered=True`). Tried globally first and it cost two
                    # cells on already-shipped boards — the corner is not universally empty.
                    # Only a board that actually prints cell numbers gets this.
                    if (spec.get('numbered') and
                            jy.min() < sub.shape[0] * 0.16 and jx.min() < sub.shape[1] * 0.16
                            and jy.max() < sub.shape[0] * 0.55
                            and sizes[j - 1] < sizes[sbig - 1] * 0.06):
                        sub[slab == j, 3] = 0
            solid = sub[:, :, 3] > 0
            if not clean:
                solid[:int(solid.shape[0] * 0.30)] = False   # drop the caption line
            ys, xs = np.where(solid)
            if ys.size == 0:
                print(f'  row{r} {nm}: EMPTY')
                continue
            t, b = ys.min(), ys.max()
            l, rr = xs.min(), xs.max()
            p = a.pad
            crop = sub[max(0, t - p):b + 1 + p, max(0, l - p):rr + 1 + p]
            Image.fromarray(crop).save(d / f'r{r}_{c}_{nm}.png')
            total += 1
        print(f'  row{r}: {NC} cells  ({names[0]} .. {names[-1]})')
    print(f'  wrote {total} -> {d}')


if __name__ == '__main__':
    main()
