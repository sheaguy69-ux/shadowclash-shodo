#!/usr/bin/env python3
"""Key and pack a blade-lock strip into a fighter's sheet as lock1..lockN.

Input is what the generator returns: ONE horizontal strip PNG, N figures side by side on
flat white. Output is the fighter's sheet with N cells appended and `frames.lockN` written.

    python3 tools/sprites/pack_lock_cells.py kael strip-kael.png --dry-run
    python3 tools/sprites/pack_lock_cells.py kael strip-kael.png

⛔ HOUSE RULES THIS OBEYS — all of them are load-bearing:

1. APPEND-ONLY, and it PROVES it. Existing cells are copied byte-for-byte and the result is
   compared against the original before anything is written. If one pixel of old art moved,
   it aborts. Rule 1 is the one that cannot be walked back once a sheet ships.

2. ONE UNIFORM SCALE for the whole set — never per-cell MATCH_HEIGHT. Lock poses legitimately
   differ in height (upright catch vs deep strain), so per-cell flattening would scale the
   compact frames up against the extended ones and cause size boil. Same reasoning as
   pack_attack5.py. The scale is anchored by mapping cell 1's body height onto the fighter's
   own idle body height, so the bind arrives the same size as the fighter already is.

3. NEVER SHRINK THE BODY TO FIT. If a scaled pose overflows its cell box the whole set
   shrinks uniformly and the percentage is PRINTED — registration survives, and you get told.
   Beyond 6% it refuses, because at that point frameH is too small for the poses and the
   answer is a bigger frame, not a smaller fighter.

4. KEYING is a corner flood-fill at the house 42% fuzz, then keep the largest connected
   component, then purge sub-visible alpha LAST. magick is not always available, so this is
   the PIL equivalent: 42% of the 0-255 channel range is a distance of ~107.

5. SHEET_V must be bumped in the SAME commit as any web/assets/sprites change. This script
   does not touch index.html — it PRINTS the line to add, because the version string is one
   enormous hand-curated line and a script has no business editing it.

The engine reads however many lockN cells exist (catch / strain loop / win / lose, where win
and lose are always the last two), so a 6-cell or a 9-cell strip both work with no code change.
"""
import argparse
import json
import os
import shutil
import sys
from collections import deque
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHEETS = os.path.join(REPO, "web", "assets", "sprites")

FUZZ = 107          # 42% of 255 — the house fuzz, as a per-channel distance
ALPHA_FLOOR = 8     # below this an "edge" pixel is invisible but still counts in a bbox
MAX_SHRINK = 0.06   # refuse past 6%: the frame is too small, not the fighter too big


def flood_key(im):
    """Corner flood-fill to transparent, then largest component, then purge faint alpha."""
    im = im.convert("RGBA")
    w, h = im.width, im.height
    px = im.load()
    seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    base = [px[s][:3] for s in seeds]

    def near(c, ref):
        return all(abs(c[i] - ref[i]) <= FUZZ for i in range(3))

    seen = bytearray(w * h)
    q = deque()
    for s, ref in zip(seeds, base):
        if not seen[s[1] * w + s[0]]:
            seen[s[1] * w + s[0]] = 1
            q.append((s[0], s[1], ref))
    while q:
        x, y, ref = q.popleft()
        px[x, y] = (px[x, y][0], px[x, y][1], px[x, y][2], 0)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not seen[ny * w + nx]:
                if near(px[nx, ny][:3], ref):
                    seen[ny * w + nx] = 1
                    q.append((nx, ny, ref))

    # largest connected component of remaining ink — drops stray specks the fill missed
    solid = [[px[x, y][3] > ALPHA_FLOOR for y in range(h)] for x in range(w)]
    best, cur_id = None, 0
    comp = [[0] * h for _ in range(w)]
    for sx in range(w):
        for sy in range(h):
            if solid[sx][sy] and not comp[sx][sy]:
                cur_id += 1
                cells, dq = [], deque([(sx, sy)])
                comp[sx][sy] = cur_id
                while dq:
                    x, y = dq.popleft()
                    cells.append((x, y))
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < w and 0 <= ny < h and solid[nx][ny] and not comp[nx][ny]:
                            comp[nx][ny] = cur_id
                            dq.append((nx, ny))
                if best is None or len(cells) > len(best):
                    best = cells
    # ⛔ DETACHED FX ARE STRIPPED HERE, and that is a feature worth naming rather than a
    # side effect. The generator keeps drawing floating debris, spark specks and strain ticks
    # beside the body; every one of those is a SEPARATE connected component, so keeping only
    # the largest removes them and leaves the fighter. It cannot remove FX that TOUCHES the
    # art — ember's glow bleeding off the claws stays, because it is fused to the claws — so
    # the count is reported and a big number means look at the cell.
    stripped = 0
    if best:
        keep = set(best)
        for x in range(w):
            for y in range(h):
                if solid[x][y] and (x, y) not in keep:
                    px[x, y] = (px[x, y][0], px[x, y][1], px[x, y][2], 0)
                    stripped += 1
    im.info["stripped_px"] = stripped

    # purge sub-visible alpha LAST, so it cannot inflate the bbox
    for x in range(w):
        for y in range(h):
            if 0 < px[x, y][3] <= ALPHA_FLOOR:
                px[x, y] = (px[x, y][0], px[x, y][1], px[x, y][2], 0)
    return im


def split_strip(im):
    """Cut the strip on WHITE columns, BEFORE keying.

    ⛔ Order matters and getting it wrong is silent. Keying the whole strip first destroys it:
    the largest-connected-component step then sees six separate figures, keeps the biggest one
    and erases the other five. Found by running this on a 6-cell strip and getting 1 cell back.
    So the split happens on raw whiteness, and each cell is keyed on its own afterwards, where
    "largest component" correctly means "this figure, minus specks".
    """
    im = im.convert("RGBA")
    px = im.load()
    filled = [any(sum(px[x, y][:3]) < 720 for y in range(im.height)) for x in range(im.width)]
    out, run = [], None
    for x, f in enumerate(filled):
        if f and run is None:
            run = x
        elif not f and run is not None:
            if x - run > 8:
                out.append(im.crop((run, 0, x, im.height)))
            run = None
    if run is not None:
        out.append(im.crop((run, 0, im.width, im.height)))
    return out


def body_height(cell):
    bb = cell.getbbox()
    return bb[3] - bb[1]


def torso_span(cell):
    """The BODY's x-range, excluding the weapon.

    Needed because the fighter must be placed in its cell by its BODY centre, not its bbox
    centre. A blade thrown far forward drags the bbox with it, so centring the bbox shoves
    the body backwards — and every other cell on the sheet is body-centred, so the bind
    would sit visibly off-axis from the fighter's own idle. The torso is the widest part of
    the figure, so the widest rows are the body.
    """
    px = cell.load()
    rows = []
    for y in range(cell.height):
        xs = [x for x in range(cell.width) if px[x, y][3] > ALPHA_FLOOR]
        if xs:
            rows.append((len(xs), min(xs), max(xs)))
    if not rows:
        return 0, cell.width
    rows.sort(reverse=True)
    top = rows[: max(1, len(rows) // 3)]      # widest third = torso and legs
    return min(r[1] for r in top), max(r[2] for r in top)


def contact_point(cell):
    """Where the weapon reaches furthest FORWARD (left), and at what height above the feet.

    This is the point that has to meet the opponent's. Measured off the drawing rather than
    assumed, so the ART decides the bind geometry instead of having to match a constant.
    """
    px = cell.load()
    best = None
    bot = 0
    for y in range(cell.height):
        xs = [x for x in range(cell.width) if px[x, y][3] > ALPHA_FLOOR]
        if xs:
            bot = y
            if best is None or min(xs) < best[0]:
                best = (min(xs), y)
    return best[0], best[1], bot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fighter")
    ap.add_argument("strip")
    ap.add_argument("--dry-run", action="store_true", help="measure and report, write nothing")
    ap.add_argument("--pick", default="",
                    help="SALVAGE: which strip cells to use, in order, 1-based. e.g. "
                         "--pick 1,2,3,5,6,7,9,10 drops cells 4 and 8. The engine reads whatever "
                         "count is packed, so a set with two bad frames becomes an 8-cell set "
                         "rather than a redraw. Order matters: the LAST TWO picked become "
                         "win/lose, the first becomes the catch, the rest are the strain loop.")
    ap.add_argument("--first-cell-anchors", action="store_true", default=True,
                    help="anchor the uniform scale on cell 1 (the catch), which is the most "
                         "upright pose and therefore the closest thing to the idle")
    args = ap.parse_args()

    jpath = os.path.join(SHEETS, args.fighter + ".json")
    ppath = os.path.join(SHEETS, args.fighter + ".png")
    for p in (jpath, ppath, args.strip):
        if not os.path.exists(p):
            sys.exit(f"not found: {p}")

    man = json.load(open(jpath))
    sheet = Image.open(ppath).convert("RGBA")
    fw, fh, footY = man["frameW"], man["frameH"], man["footY"]
    cols = sheet.width // fw
    if sheet.width % fw:
        sys.exit(f"sheet width {sheet.width} is not a multiple of frameW {fw}")

    idle_i = man["frames"]["idle"]
    idle = sheet.crop((idle_i * fw, 0, idle_i * fw + fw, fh))
    idle_h = body_height(idle)

    print(f"\n  {args.fighter}: sheet {cols} cells of {fw}x{fh}, footY {footY}, "
          f"idle body {idle_h}px")

    cells = [flood_key(c) for c in split_strip(Image.open(args.strip))]
    cells = [c.crop(c.getbbox()) for c in cells if c.getbbox()]
    found = len(cells)

    # ⛔ SALVAGE BEFORE DISPOSAL. A delivered set is rarely all-good or all-bad: two frames may
    # carry a wrong grip while the other eight are usable. Since the engine reads whatever count
    # is packed, dropping the bad frames turns a redraw into a shorter set — which is strictly
    # better than throwing away eight good drawings to fix two.
    if args.pick:
        want = [int(n) for n in args.pick.replace(" ", "").split(",") if n]
        bad = [n for n in want if not 1 <= n <= found]
        if bad:
            sys.exit(f"  ⛔ --pick names cell(s) {bad}, but the strip has {found}")
        if len(want) < 3:
            sys.exit(f"  ⛔ --pick needs at least 3 cells (catch + win + lose); got {len(want)}")
        dropped = [n for n in range(1, found + 1) if n not in want]
        cells = [cells[n - 1] for n in want]
        print(f"  PICKED {want} of {found}"
              + (f" — dropping {dropped}" if dropped else "")
              + f" -> a {len(cells)}-cell set")
    if len(cells) < 3:
        sys.exit(f"only found {len(cells)} cells in the strip — expected at least 3")
    print(f"  strip: {len(cells)} cells, body heights "
          f"{[body_height(c) for c in cells]}")
    fx = [c.info.get("stripped_px", 0) for c in cells]
    if any(fx):
        print(f"  detached FX stripped per cell: {fx}")
        loud = [i + 1 for i, n in enumerate(fx) if n > 400]
        if loud:
            print(f"  ⚠ cells {loud} lost over 400px of detached ink. That is usually floating "
                  f"debris or spark specks and is correct to remove — but check them, because a "
                  f"weapon drawn DETACHED from the hand would be stripped the same way.")

    # ⛔ SIZE BOIL CHECK on the SOURCE, before scaling. If the generator's own cells disagree
    # in height, no uniform scale can fix it — that is a redraw, and it must be said now
    # rather than discovered on screen.
    hs = [body_height(c) for c in cells]
    spread_pct = (max(hs) - min(hs)) / (sum(hs) / len(hs)) * 100
    print(f"  source body-height spread: {max(hs) - min(hs)}px ({spread_pct:.1f}%)")
    if spread_pct > 6:
        print(f"  ⛔ SIZE BOIL IN THE SOURCE ART ({spread_pct:.1f}% > 6%). A uniform scale "
              f"cannot fix this — the cells were drawn at different sizes. Redraw, do not pack.")
        if not args.dry_run:
            sys.exit(1)

    # ONE uniform scale, anchored on cell 1 vs the fighter's own idle
    scale = idle_h / hs[0]
    print(f"  uniform scale {scale:.4f} (cell 1 {hs[0]}px -> idle {idle_h}px)")

    def render(c, s):
        w = max(1, round(c.width * s))
        h = max(1, round(c.height * s))
        return c.resize((w, h), Image.LANCZOS)

    # NEVER shrink the body to fit: if a pose overflows, shrink the WHOLE set and say so
    shrink = 1.0
    for _ in range(40):
        scaled = [render(c, scale * shrink) for c in cells]
        over_w = max(s.width for s in scaled) - fw
        over_h = max(s.height for s in scaled) - fh
        if over_w <= 0 and over_h <= 0:
            break
        shrink *= 0.99
    if shrink < 1.0:
        pct = (1 - shrink) * 100
        print(f"  ⚠ the set overflowed its {fw}x{fh} cell box — whole set shrunk {pct:.1f}% "
              f"uniformly (registration preserved)")
        if 1 - shrink > MAX_SHRINK:
            sys.exit(f"  ⛔ refusing: {pct:.1f}% shrink exceeds {MAX_SHRINK*100:.0f}%. frameH is "
                     f"too small for these poses — GROW frameH/footY, do not shrink the fighter.")
    scaled = [render(c, scale * shrink) for c in cells]

    names = [f"lock{i}" for i in range(1, len(cells) + 1)]
    clash = [n for n in names if n in man["frames"]]
    if clash:
        sys.exit(f"  ⛔ {args.fighter}.json already has {clash} — this would overwrite packed "
                 f"cells. Sheets are append-only; pick a fresh run or remove them deliberately.")

    print(f"  will append {len(cells)} cells at index {cols}..{cols + len(cells) - 1} as "
          f"{names[0]}..{names[-1]}")
    print(f"  final body heights on sheet: {[body_height(s) for s in scaled]}")

    if args.dry_run:
        print("\n  dry run — nothing written\n")
        return

    out = Image.new("RGBA", (sheet.width + len(scaled) * fw, fh), (0, 0, 0, 0))
    out.paste(sheet, (0, 0))
    reach_px, contact_fr = [], []
    for n, s in enumerate(scaled):
        # ⛔ CENTRE ON THE BODY, NOT THE BBOX. A blade thrown forward drags the bbox with it,
        # so bbox-centring pushes the body backwards and the bind sits off-axis from the
        # fighter's own idle. Align the torso centre to the cell centre, as every other cell
        # on the sheet is.
        t_lo, t_hi = torso_span(s)
        body_cx = (t_lo + t_hi) / 2
        x = sheet.width + n * fw + round(fw / 2 - body_cx)
        # measure this cell's drawn contact point while it is in hand
        cxp, cyp, botp = contact_point(s)
        reach_px.append((body_cx - cxp) * man["scale"])
        contact_fr.append((botp - cyp) / max(1, s.height))
        y = footY - s.height
        if y < 0:
            sys.exit(f"  ⛔ cell {n+1} is taller than footY ({s.height} > {footY}) — the pose "
                     f"does not fit above the foot line. GROW frameH/footY.")
        out.alpha_composite(s, (x, y))

    # ⛔ PROVE APPEND-ONLY before writing: the original region must be byte-identical
    if out.crop((0, 0, sheet.width, fh)).tobytes() != sheet.tobytes():
        sys.exit("  ⛔ ABORT: the existing cells changed. Sheets are append-only and this would "
                 "have rewritten shipped art.")
    print("  ✓ append-only verified — every original pixel is unchanged")

    shutil.copy2(ppath, ppath + ".bak")
    shutil.copy2(jpath, jpath + ".bak")
    out.save(ppath)
    for n, nm in enumerate(names):
        man["frames"][nm] = cols + n
    if "cols" in man:
        man["cols"] = cols + len(scaled)

    # ⛔ THE ART DECIDES THE BIND GEOMETRY. Written from the cells just packed, in on-screen
    # px from the body centre to the weapon's furthest forward point, averaged over the STRAIN
    # cells (the held ones — the catch and the win/lose reach differently and would skew it).
    # enterBladeLock reads this instead of the shared LOCK_SEP/2, so a fighter drawn with a
    # short close bind is stood closer and still MEETS the opponent.
    strain = reach_px[1:-2] if len(reach_px) > 3 else reach_px
    man["lockReach"] = round(sum(strain) / len(strain), 2)
    frs = contact_fr[1:-2] if len(contact_fr) > 3 else contact_fr
    man["lockContactFrac"] = round(sum(frs) / len(frs), 3)

    print(f"  lockReach {man['lockReach']}px on screen from body centre "
          f"(LOCK_SEP/2 would have been 34.0)")
    print(f"  contact height {man['lockContactFrac'] * 100:.1f}% of body — the spec asks ~48%")
    if abs(man["lockContactFrac"] - 0.48) > 0.12:
        print(f"  ⚠ that is {abs(man['lockContactFrac'] - 0.48) * 100:.0f} points off the spec. "
              f"Spacing is corrected automatically; HEIGHT IS NOT — a fighter binding here will "
              f"pass above or below an opponent drawn at 48%. Compare against the other sets "
              f"before accepting.")
    json.dump(man, open(jpath, "w"), indent=2)

    print(f"  wrote {os.path.relpath(ppath, REPO)} ({cols} -> {cols + len(scaled)} cells)")
    print(f"  wrote {os.path.relpath(jpath, REPO)} (+{len(names)} frame names)")
    print(f"  backups at *.bak — delete once you have eyeballed the sheet\n")
    print("  ⛔ NOW BUMP SHEET_V in web/index.html IN THIS SAME COMMIT. Suggested entry:\n")
    print(f"     BLADE LOCK CELLS — {args.fighter} {names[0]}..{names[-1]} packed from the "
          f"owner's generator strip, ONE uniform scale {scale * shrink:.4f} anchored on cell 1 "
          f"vs his idle body height ({idle_h}px), source spread {spread_pct:.1f}%. Appended at "
          f"{cols}..{cols + len(scaled) - 1}; original cells verified byte-identical.\n")


if __name__ == "__main__":
    main()
