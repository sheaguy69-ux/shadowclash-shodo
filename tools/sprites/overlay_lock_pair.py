#!/usr/bin/env python3
"""COMPOSITE two fighters' lock cells and SEE whether they form a bind.

Owner's point, and it corrects a mistake in how batch 1 was graded: the generator drew
each fighter from that fighter's own point of view, alone. Judging one strip against a
spec number says nothing about whether TWO of them meet — and meeting each other is the
only thing that actually matters. Put two together and look.

This matters more than the spec number it replaces. `check_lock_pairs.py` pre-flights the
ANCHOR geometry using stand-in guard cells, which is the right check before art exists.
Once the real cells exist, the anchor is no longer the authority — the ART is. If every
fighter binds at the same height as every other fighter, the bind works, and the engine's
number should be moved to match the drawings rather than the drawings redrawn to match the
number. Moving one constant is free; redrawing 36 cells is not.

So this script does two things:

  MEASURE   for each cell, where the weapon actually crosses — found as the outermost
            forward reach of non-body pixels at each height, which is the blade/staff
            sticking out ahead of the fighter. Reported as a percentage of body height so
            fighters of different sizes are comparable.
  COMPOSITE frame N of fighter A against frame N of fighter B, B mirrored, positioned so
            each fighter's own measured contact point lands on one shared line. If the
            weapons meet, it looks like a bind. If they do not, that is visible instantly.

Input is one horizontal strip PNG per fighter (the format the generator returns): N cells
side by side on a flat white background. Cells are cut by finding the vertical gaps.

    python3 tools/sprites/overlay_lock_pair.py strip-*.png          # the whole batch
    python3 tools/sprites/overlay_lock_pair.py a.png b.png --cell 3  # one cell
    python3 tools/sprites/overlay_lock_pair.py *.png --measure-only  # numbers, no images
    python3 tools/sprites/overlay_lock_pair.py *.png --pair a.png b.png

Hand it every strip at once. With six fighters there are fifteen pairings and ninety
overlays, which is not a report anyone reads — but the pairings are not independent. What
decides whether any two fighters meet is whether each binds at the same FRACTION of its own
body height, so the batch gets one number per fighter, a median as the actual convention,
and a name for whoever departs from it. Then it composites only the worst-case pair (highest
bind height against lowest), because if that one meets, every other pairing does.

Writes overlays to docs/handoff/blade-lock/pair-overlays/.
"""
import argparse
import os
import sys
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "docs", "handoff", "blade-lock", "pair-overlays")

# A generator returns strips on flat white, not with alpha. Anything darker than this on
# all three channels is ink; the rest is background.
WHITE_CUT = 238


def font(size, bold=True):
    n = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    p = f"/usr/share/fonts/truetype/dejavu/{n}"
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()


def to_alpha(im):
    """White background -> transparent, so cells can be composited over each other."""
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if r > WHITE_CUT and g > WHITE_CUT and b > WHITE_CUT:
                px[x, y] = (r, g, b, 0)
    return im


def split_cells(im, min_gap=8):
    """Cut a horizontal strip into cells on the empty columns between figures."""
    px = im.load()
    filled = []
    for x in range(im.width):
        col = any(px[x, y][3] > 40 for y in range(im.height))
        filled.append(col)
    cells, run = [], None
    for x, f in enumerate(filled):
        if f and run is None:
            run = x
        elif not f and run is not None:
            if x - run > min_gap:
                cells.append((run, x))
            run = None
    if run is not None:
        cells.append((run, im.width))
    return [im.crop((a, 0, b, im.height)) for a, b in cells]


def measure(cell):
    """Body box, and the height at which the weapon reaches furthest FORWARD (left).

    The weapon is whatever sticks out ahead of the torso. Scanning row by row for the
    leftmost ink and taking the row that reaches furthest finds the blade, the staff or
    the claw tips without needing to know which fighter this is.
    """
    px = cell.load()
    rows = {}
    for y in range(cell.height):
        xs = [x for x in range(cell.width) if px[x, y][3] > 40]
        if xs:
            rows[y] = (min(xs), max(xs))
    if not rows:
        return None
    top, bot = min(rows), max(rows)
    h = bot - top + 1

    # torso x-range: the widest 40% band of the figure, which is the body, never the weapon
    mid = sorted(rows.items(), key=lambda kv: kv[1][1] - kv[1][0], reverse=True)
    body_left = min(v[0] for _, v in mid[: max(1, len(mid) // 3)])

    # the weapon reaches furthest left of the body; find the row where it goes furthest
    reach_y, reach_x = min(rows.items(), key=lambda kv: kv[1][0])[0], min(v[0] for v in rows.values())
    return {
        "top": top, "bottom": bot, "bodyH": h,
        "bodyLeft": body_left,
        "contactY": reach_y,
        "contactX": reach_x,
        # height of the contact above the FEET, as a fraction of body height — the number
        # that has to agree between fighters
        "contactFrac": round((bot - reach_y) / h, 3),
    }


def load_strip(path):
    im = to_alpha(Image.open(path))
    cells = split_cells(im)
    return cells, [measure(c) for c in cells]


def report(paths):
    print(f"\n  {'file':28} {'cell':>4} {'bodyH':>6} {'contact % of body':>18}")
    print("  " + "-" * 62)
    data = {}
    for p in paths:
        cells, ms = load_strip(p)
        name = os.path.basename(p)
        data[p] = (cells, ms)
        for i, m in enumerate(ms, 1):
            if not m:
                continue
            print(f"  {name[:28]:28} {i:>4} {m['bodyH']:>6} {m['contactFrac'] * 100:>17.1f}%")
        # the boil check that cannot be done by eye
        hs = [m["bodyH"] for m in ms if m]
        if len(hs) > 1:
            spread = max(hs) - min(hs)
            pct = spread / (sum(hs) / len(hs)) * 100
            flag = "OK" if pct < 2 else "SIZE BOIL"
            print(f"  {'':28} {'':>4} body height spread {spread}px ({pct:.1f}%)  -> {flag}")
    return data


def overlay(pa, pb, cell_i, data):
    (ca, ma), (cb, mb) = data[pa], data[pb]
    i = cell_i - 1
    if i >= len(ca) or i >= len(cb):
        print(f"  cell {cell_i}: one strip does not have that many cells")
        return
    a, b = ca[i], cb[i]
    da, db = ma[i], mb[i]
    if not (da and db):
        return

    # B is mirrored — it is the fighter facing RIGHT (raw art faces left, see
    # check_lock_pairs.py). Its contact point mirrors with it.
    bm = b.transpose(Image.FLIP_LEFT_RIGHT)
    b_contact_x = bm.width - db["contactX"]

    # Scale B so both bodies are the same height on screen: these are reference drawings at
    # whatever size the generator returned, not packed cells, so raw pixels are not
    # comparable. Equal body height is what the game will produce after per-fighter scale.
    k = da["bodyH"] / db["bodyH"]
    bm = bm.resize((max(1, round(bm.width * k)), max(1, round(bm.height * k))), Image.LANCZOS)
    b_contact_x = round(b_contact_x * k)
    b_contact_y = round(db["contactY"] * k)
    b_bottom = round(db["bottom"] * k)

    pad = 90
    # floor the width on the CAPTION, not just the art: two small cells produced a canvas
    # narrower than the header and the legend line ran off the right edge
    W = max(a.width + bm.width + pad * 3, 760)
    H = max(a.height, bm.height) + 190
    img = Image.new("RGBA", (W, H), (24, 24, 28, 255))
    dr = ImageDraw.Draw(img)

    ground = H - 70
    # both feet on the ground line, both contact points on one vertical line
    contact_x = W // 2
    ax = contact_x - da["contactX"]
    ay = ground - da["bottom"]
    bx = contact_x - b_contact_x
    by = ground - b_bottom
    img.alpha_composite(a, (ax, ay))
    img.alpha_composite(bm, (bx, by))

    # each fighter's own contact height, on screen
    a_cy = ay + da["contactY"]
    b_cy = by + b_contact_y
    dy = abs(a_cy - b_cy)

    dr.line([(0, ground), (W, ground)], fill=(74, 222, 128, 255), width=2)
    dr.line([(0, a_cy), (W, a_cy)], fill=(251, 191, 36, 160), width=2)
    if dy > 2:
        dr.line([(0, b_cy), (W, b_cy)], fill=(96, 165, 250, 160), width=2)
    dr.ellipse([contact_x - 9, min(a_cy, b_cy) - 9, contact_x + 9, max(a_cy, b_cy) + 9],
               outline=(248, 113, 113, 255), width=3)

    na = os.path.splitext(os.path.basename(pa))[0]
    nb = os.path.splitext(os.path.basename(pb))[0]
    verdict = ("THEY MEET" if dy <= max(6, da["bodyH"] * 0.035) else
               f"WEAPONS MISS by {dy}px")
    col = (74, 222, 128, 255) if verdict == "THEY MEET" else (248, 113, 113, 255)
    dr.text((22, 16), f"{na}  vs  {nb}   ·   cell {cell_i}", font=font(21),
            fill=(255, 255, 255, 255))
    dr.text((22, 46), verdict, font=font(16), fill=col)
    dr.text((22, 70), f"contact height: {na} {da['contactFrac']*100:.1f}% of body   ·   "
                      f"{nb} {db['contactFrac']*100:.1f}%", font=font(13, False),
            fill=(148, 163, 184, 255))
    dr.text((22, 90), "amber = fighter A's contact line, blue = fighter B's. One line means "
                      "they agree.", font=font(13, False), fill=(148, 163, 184, 255))

    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, f"{na}--{nb}--cell{cell_i}.png")
    img.convert("RGB").save(out)
    print(f"  cell {cell_i}: {verdict:22} -> {os.path.relpath(out, REPO)}")


def consensus(paths, data):
    """Do the fighters AGREE on a bind height, and who is the outlier?

    With six strips there are fifteen pairings and ninety overlays — unusable as a report.
    But the pairs are not independent: what decides whether any two fighters meet is
    whether each one binds at the same fraction of its own body height. So measure the
    fraction per fighter, take the median as the batch's actual convention, and name whoever
    departs from it. One number per fighter beats fifteen pairings, and it points straight at
    the cell that needs redrawing instead of at a pair.
    """
    rows = []
    for p in paths:
        cells, ms = data[p]
        # cells 1-4 are the held bind; 5 and 6 extend by design and are excluded
        held = [m["contactFrac"] for m in ms[:4] if m]
        if not held:
            continue
        rows.append((os.path.basename(p), sum(held) / len(held),
                     max(held) - min(held), len(held)))
    if not rows:
        return None
    fracs = sorted(r[1] for r in rows)
    mid = fracs[len(fracs) // 2] if len(fracs) % 2 else \
        (fracs[len(fracs) // 2 - 1] + fracs[len(fracs) // 2]) / 2

    print(f"\n  BIND-HEIGHT CONSENSUS across cells 1-4 (5 and 6 extend by design)")
    print(f"  batch median: {mid * 100:.1f}% of body height\n")
    print(f"  {'fighter':28} {'mean':>7} {'drift 1-4':>10} {'vs median':>10}")
    print("  " + "-" * 60)
    worst = None
    for name, mean, drift, n in sorted(rows, key=lambda r: -abs(r[1] - mid)):
        off = (mean - mid) * 100
        flag = "" if abs(off) < 4 else "  <-- OUTLIER"
        if worst is None and abs(off) >= 4:
            worst = name
        dflag = "" if drift < 0.04 else "  DRIFTS"
        print(f"  {name[:28]:28} {mean*100:>6.1f}% {drift*100:>9.1f}%{dflag} "
              f"{off:>+9.1f}%{flag}")
    print()
    if worst:
        print(f"  -> {worst} disagrees with the rest of the batch. Redraw that one, not the "
              f"others.")
    else:
        print("  -> all fighters agree within 4%. THE ART IS SELF-CONSISTENT: move "
              "LOCK_Y_ONSCREEN")
        print(f"     in tools/sprites/make_lock_handoff.py to match {mid*100:.1f}% of body "
              f"height rather than")
        print("     redrawing anything. Re-run check_lock_pairs.py after.")
    return mid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("strips", nargs="+", help="one horizontal strip PNG per fighter")
    ap.add_argument("--cell", type=int, default=0, help="only this cell (1-based); 0 = all")
    ap.add_argument("--measure-only", action="store_true")
    ap.add_argument("--pair", nargs=2, metavar=("A", "B"),
                    help="composite this specific pair instead of the auto-chosen one")
    args = ap.parse_args()

    missing = [p for p in args.strips if not os.path.exists(p)]
    if missing:
        sys.exit(f"not found: {', '.join(missing)}")

    data = report(args.strips)
    consensus(args.strips, data)
    if args.measure_only:
        return
    if len(args.strips) < 2 and not args.pair:
        print("\n  give two or more strips to composite a pair")
        return

    # Composite the pair that stresses the batch hardest — the two fighters furthest apart
    # in bind height — because that is the pairing that fails first. Everything else meets
    # if that one does.
    if args.pair:
        pa, pb = args.pair
    else:
        by_frac = []
        for p in args.strips:
            held = [m["contactFrac"] for m in data[p][1][:4] if m]
            if held:
                by_frac.append((sum(held) / len(held), p))
        by_frac.sort()
        pa, pb = by_frac[-1][1], by_frac[0][1]
        print(f"\n  compositing the WORST-CASE pair: {os.path.basename(pa)} (highest bind) "
              f"vs {os.path.basename(pb)} (lowest)")
    cells = range(1, min(len(data[pa][0]), len(data[pb][0])) + 1) if not args.cell \
        else [args.cell]
    for c in cells:
        overlay(pa, pb, c, data)


if __name__ == "__main__":
    main()
