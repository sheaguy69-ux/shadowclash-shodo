#!/usr/bin/env python3
"""Re-cut oni dash1/dash2/dash3 from the owner's board, IN PLACE, keeping their indices.

    python3 tools/sprites/recut_oni_dash.py            # rewrite the three cells
    python3 tools/sprites/recut_oni_dash.py --check    # measure only, touch nothing

WHAT WAS WRONG. The three cells carried the source board's CAPTION TEXT as art —
'5. FORWARD DASH MID', '6. BACKSTEP PREP', '7. SHADOW REPOSITION', '8. RECOVERY' —
plus a 2px panel rule and a neighbouring panel's figure bleeding in at the edge. The
tell is geometric and needs no eye: art width in a cell's TOPMOST row against its
widest row. A head or a horn tip is narrow, so a real cell reads 25-70%; these three
read 95-97%, because their top row is a caption banner. Flagged at SHEET_V 463.

⛔ THE SOURCE BOARD IS MASTER-STATES-CLEAN.png, AND ITS NAME IS A LIE. It is not
clean and it is not the states sheet: it is the labelled SPECIALS board, ROW 1
'NEUTRAL / FORWARD / BACK SPECIALS', with a white-on-black caption pill above every
panel. cut_master_grid.py's SHEETS['states'] points at MASTER-STATES-4x8.png, whose
row 1 is a different set of poses under red numerals, so the cell filenames these
were packed under (r1_6_dash_start / r1_7_dash_burst / r1_8_dash_end) name panels
that are NOT what the pixels hold. Identified three ways that agree: the pill text
reads back literally once un-mirrored, the silhouettes match panels 6 and 8 at IoU
0.91 / 0.78, and the white mask measures the same 0.78-0.80 ratio in all three.

⛔ SO THE SLOTS ARE 5 / 6 / 8, NOT A DASH. dash1 is FORWARD DASH MID, but dash2 is
BACKSTEP PREP — he steps the other way — and dash3 is RECOVERY, a standstill. This
pass DOES NOT change which panels sit in which slot: the cells are decontaminated
and nothing else, because the pose choice is the owner's call and these three are
not drawn by anything yet (see below). Re-slotting them is a separate ask.

⛔ AND NOTHING RENDERS THEM TODAY. 'dash1' does not appear anywhere in web/index.html
outside the SHEET_V note. The engine reaches cells two ways only — 634 literal F.<key>
reads and dirCells' 18 directional stems (glfwd/ghup/sdown/...) — and 'dash' is in
neither list. Confirmed live as well: six real shunshin dashes drew cells 0-8, 40, 41,
42 and 67, never 10/11/12. The SHEET_V 463 note's claim that they 'render mirrored on
screen' is wrong and is corrected in the same commit that this ships in.

SCALE IS MEASURED, NOT RE-DERIVED. The head-match chain in pack_oni_new.py would give
an answer, but the sheet already carries these figures and the job is to land on the
size it already has, so the transform is read straight off the packed cells. Two rigid
rulers, independently: the caption pill is 30px tall on the board and 24px in the cell
(0.800 exactly), and his white mask measures 0.78-0.80 across all three. So 0.80.
"""
import argparse
import json
import pathlib
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as nd

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from cut_strip import cut                                              # noqa: E402

BOARD = ROOT / "RECOVERY/oni-founder/boards-aug9/MASTER-STATES-CLEAN.png"
SHEET = ROOT / "web/assets/sprites/oni.png"
MANIFEST = ROOT / "web/assets/sprites/oni.json"

# Row 1 of the board, cropped BELOW the caption pills (they end at y51, y54 is the
# first blank row) and from the first panel's left edge, clear of the row's text block.
STRIP_X, STRIP_Y = (241, 1510), (54, 300)
PANELS = 8
PANEL = {"dash1": 5, "dash2": 6, "dash3": 8}       # engine key -> board panel number

# ⛔ THE PANEL RULES ARE REPAIRED AT SOURCE, NOT CUT AROUND. Seven 1-2px dividers run
# down row 1, and cut_strip cannot drop them: its text filter throws away a blob sitting
# wholly above or below him, and a rule spans the full band, so it overlaps his vertical
# span and reads like a claw tip. Nor can they be dodged by moving a cut — the divider
# between panels 4 and 5 sits at board x 878-879, INSIDE panel 5's ink, with his red
# speed streak passing on both sides of it. Cutting right of it decapitates the streak;
# cutting left of it keeps the bar. So the rules are erased from the strip first, by
# interpolating each rule column from its two clean neighbours: in the six gaps that is
# white-to-white and changes nothing, and across the streak it closes a 2px slit that
# would otherwise show.
#
# They are identified, not assumed: a column of the band that is >=80% inked, colour
# NEUTRAL down its length, and part of a run at most 4px wide. His art never qualifies —
# the medium is heavy black outlines over a warm palette, so every column of him carries
# either a dark rim or a hue. The count is asserted below; 7 rules for 8 panels.
RULE_MAX_W = 4
RULE_MIN_FILL = 0.80
RULE_NEUTRAL = 12
SCALE = 0.80

FLAT_TOP = 90.0        # topmost-row width as a % of the widest row; a banner, not a head


def figure_only(arr):
    """Keep his largest connected component and drop everything else.

    ⛔ THE PANEL RULE SURVIVES cut_strip's TEXT FILTER. That filter drops a blob that
    sits wholly above or below him, which is what a caption or a frame number does; a
    2px divider rule spans the full height, so it OVERLAPS his vertical span and is
    kept as if it were a claw tip. Panel 8 carries exactly one, 2x223 at its left edge.
    Largest-component is safe for these three specifically because their FX is attached
    to the body — measured, the runners-up are 227px (that rule) and then 17px of
    keying speckle, against 8920-13931px of him.
    """
    m = arr[:, :, 3] > 0
    lab, n = nd.label(m)
    sizes = nd.sum(m, lab, range(1, n + 1))
    keep = lab == int(np.argmax(sizes)) + 1
    out = arr.copy()
    out[~keep, 3] = 0
    return out, sorted(sizes.astype(int), reverse=True)


def flat_top(alpha):
    """(topmost row width, widest row width, % ) — the detector that found this."""
    px = alpha > 8
    widths = []
    for row in px:
        xs = np.where(row)[0]
        widths.append(xs.max() - xs.min() + 1 if xs.size else 0)
    occ = [i for i, w in enumerate(widths) if w]
    if not occ:
        return 0, 0, 0.0
    top, widest = widths[occ[0]], max(widths)
    return top, widest, 100.0 * top / widest


def runs_of(flags):
    """[(start, end)] for each maximal True run."""
    out, cur = [], None
    for i, v in enumerate(flags):
        if v and cur is None:
            cur = i
        elif not v and cur is not None:
            out.append((cur, i - 1)); cur = None
    if cur is not None:
        out.append((cur, len(flags) - 1))
    return out


def derule(strip):
    """Erase the panel dividers by interpolating each rule column from its neighbours."""
    a = np.asarray(strip).astype(int)
    rgb, H = a[:, :, :3], a.shape[0]
    ink = rgb.min(2) <= 224
    neutral = (rgb.max(2) - rgb.min(2)) <= RULE_NEUTRAL
    hit = np.zeros(a.shape[1], bool)
    for x in range(a.shape[1]):
        col = ink[:, x]
        if col.sum() >= RULE_MIN_FILL * H and col.any() and neutral[col, x].mean() > 0.9:
            hit[x] = True
    rules = [r for r in runs_of(hit) if r[1] - r[0] + 1 <= RULE_MAX_W]
    for x0, x1 in rules:
        lo, hi = max(0, x0 - 1), min(a.shape[1] - 1, x1 + 1)
        n = hi - lo
        for i, x in enumerate(range(x0, x1 + 1), start=1):
            t = i / n
            a[:, x, :3] = np.round((1 - t) * a[:, lo, :3] + t * a[:, hi, :3])
    return Image.fromarray(a.astype(np.uint8)), rules


def gap_cuts(strip):
    """Cut columns = centre of each blank gap between the eight panels."""
    ink = np.asarray(strip).astype(int)[:, :, :3].min(2) <= 224
    col = ink.sum(0)
    solid = runs_of(col > 0)
    solid = [r for r in solid if r[1] - r[0] + 1 >= 3]      # ignore keying speckle
    if len(solid) != PANELS:
        raise SystemExit(f"strip segmented into {len(solid)} panels, expected {PANELS}")
    return [(solid[i][1] + solid[i + 1][0]) // 2 for i in range(PANELS - 1)], solid


def build():
    """Cut, scale, mirror. Returns {key: RGBA cell image at frame size}."""
    man = json.load(open(MANIFEST))
    fw, fh, foot = man["frameW"], man["frameH"], man["footY"]

    board = Image.open(BOARD).convert("RGBA")
    strip = board.crop((STRIP_X[0], STRIP_Y[0], STRIP_X[1], STRIP_Y[1]))
    strip, rules = derule(strip)
    if len(rules) != PANELS - 1:
        raise SystemExit(f"found {len(rules)} panel rules, expected {PANELS - 1}: {rules}")
    cuts, solid = gap_cuts(strip)
    print(f"  de-ruled {len(rules)} dividers at strip x {[r[0] for r in rules]}")
    print(f"  {PANELS} panels, cuts at {cuts}")

    tmp = pathlib.Path("/tmp/oni-row1-strip.png")
    strip.save(tmp)
    cells, _ = cut(str(tmp), n=PANELS, title=0.0, forced=cuts, verbose=False)
    tmp.unlink(missing_ok=True)

    out = {}
    for key, panel in PANEL.items():
        raw = cells[panel - 1]
        if raw is None:
            raise SystemExit(f"panel {panel} cut empty — the board or the cuts moved")
        arr, sizes = figure_only(raw[0])
        im = Image.fromarray(arr.astype(np.uint8))
        im = im.resize((max(1, round(im.width * SCALE)), max(1, round(im.height * SCALE))),
                       Image.LANCZOS)
        # ⛔ AUTHORED FACING LEFT, like every other cell on this sheet and every other
        # fighter — the engine draws through ctx.scale(-facing, 1). The board faces RIGHT.
        im = im.transpose(Image.FLIP_LEFT_RIGHT)

        a = np.asarray(im)[:, :, 3] > 0
        ys, xs = np.where(a)
        cell = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
        # Same seating as pack_oni_new: bbox centred on the frame, lowest pixel on footY.
        cell.alpha_composite(im, (fw // 2 - (xs.min() + xs.max()) // 2, foot - ys.max()))
        out[key] = cell
        print(f"  panel {panel} -> {key}: components {sizes[:3]} "
              f"-> {im.width}x{im.height} placed")
    return man, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="measure only, write nothing")
    a = ap.parse_args()

    man, fresh = build()
    fw, fh, cols, foot = man["frameW"], man["frameH"], man["cols"], man["footY"]
    sheet = Image.open(SHEET).convert("RGBA")
    before = np.asarray(sheet).copy()

    print(f"\n{'cell':8} {'':>4}  {'BEFORE flat-top':>22}   {'AFTER flat-top':>22}")
    new = sheet.copy()
    for key, cell in fresh.items():
        idx = man["frames"][key]
        cx, cy = (idx % cols) * fw, (idx // cols) * fh
        old = np.asarray(sheet.crop((cx, cy, cx + fw, cy + fh)))[:, :, 3]
        ot, ow, op = flat_top(old)
        nt, nw, npc = flat_top(np.asarray(cell)[:, :, 3])
        print(f"{key:8} {idx:4d}  {ot:5d}/{ow:<5d} {op:6.1f}%   {nt:5d}/{nw:<5d} {npc:6.1f}%")
        if npc >= FLAT_TOP:
            raise SystemExit(f"{key} still reads flat-topped ({npc:.1f}%) — do not ship")
        new.paste(cell, (cx, cy))          # paste, not composite: the cell is REPLACED

    after = np.asarray(new)
    # ⛔ APPEND-ONLY: every cell that is not one of the three must be byte-identical.
    touched = {man["frames"][k] for k in fresh}
    for i in range(cols):
        if i in touched:
            continue
        x = i * fw
        if not np.array_equal(before[:, x:x + fw], after[:, x:x + fw]):
            raise SystemExit(f"cell {i} changed and must not have")
    print(f"\n  {cols - len(touched)}/{cols} untouched cells verified byte-identical")

    for key, cell in fresh.items():
        arr = np.asarray(cell)[:, :, 3] > 0
        ys, xs = np.where(arr)
        assert ys.max() == foot, f"{key} feet at {ys.max()}, footY is {foot}"
        assert abs((xs.min() + xs.max()) / 2 - fw / 2) <= 1, f"{key} is not centred"
    print(f"  all three seated on footY {foot} and centred on {fw // 2}")

    if a.check:
        print("\n--check: nothing written")
        return
    new.save(SHEET)
    print(f"\nwrote {SHEET.relative_to(ROOT)}  (frames{{}} untouched — indices are stable)")


if __name__ == "__main__":
    main()
