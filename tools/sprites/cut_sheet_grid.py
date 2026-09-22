"""Cut an owner-supplied move spreadsheet into individual frames.

Layout (same as Kael's two sheets, see pack_kael_spreadsheet.py): one table, a
left-hand MOVE-NAME column, then 6 frame columns, one move per row.

⛔ THE GRID IS FOUND, NOT ASSUMED, and a rule is the thing that spans the WHOLE axis:

  * A real rule measures ~1.00 of the width or height. Content never does — a raised
    weapon reaches ~0.6-0.7 of a column, and six hilts lining up at one height reach
    ~0.65 of a row. 0.85 sits in that gap on both axes. Mizu's bo put a phantom at
    x=1340 and Tsubasa's raised tanto produced SEVEN; a row of Kael's katana hilts put
    one at y=259, which would have cut row 1 through the characters.
  * 0.85 also drops the occasional genuine rule a body sits across (Mizu lost the one
    at ~x=575). A gap of roughly twice the median frame width is that dropped rule, and
    gets one boundary inserted back at its midpoint.

Rows ran at 0.60 until Aug 2 2026. That was safe only while the darkness cutoff below was
tight enough to ignore most costume ink; widening it to the page boundary made 0.60 start
promoting hilts and sashes to rules on 8 of the 14 spreadsheets on hand.

⛔ A RULE IS ANYTHING OFF THE WHITE PAGE, and THE PAGE IS MEASURED PER SHEET. A hardcoded
darkness cutoff read `sum(RGB) < 500`, then `< 690`, and each raise was really a bet that
the next sheet's white would be exactly 765. Two sheets have already collected that bet:
the Aug 2 aerial sheets drew their rules in light grey (sum 526-639 against the 386-445 of
the earlier ones) and 500 saw four of Kael's six as blank page; Shin's Aug 2 move sheet came
back JPEG-compressed, page 762 and rules 700-729, and 690 found two of its seven columns.
Taking the MODAL sum as the page ends the chase — on a sheet that is mostly white it is the
page by definition, and a rule is whatever sits below it. The SPAN fraction above is what
rejects weapons and hilts; the darkness cutoff was never meant to.

Eyeballed offsets are what put the move-name column into frame 1's slot the first
time this was attempted, silently dropping frame 6 of every row.

Usage: python3 cut_sheet_grid.py "<sheet.png>" <out_dir> <rowname1> <rowname2> ...
"""
import pathlib
import sys

import numpy as np
from PIL import Image

PAGE = 690        # sum(RGB) above this is the flat white page; at or below it is ink or a rule
SPAN = 0.85       # a rule spans this much of its axis; content tops out around 0.7


def _group(vals, gap=3):
    out, cur = [], []
    for x in vals:
        if cur and x - cur[-1] > gap:
            out.append(sum(cur) // len(cur))
            cur = []
        cur.append(x)
    if cur:
        out.append(sum(cur) // len(cur))
    return _merge_close(out)


def _merge_close(b):
    """Two boundaries a few px apart are ONE thick rule, split by its own soft middle.

    The fixed 3px tolerance above is a pixel count on a page whose size is not fixed. Shin's
    Aug 2 redraw came in at 2151px wide with heavy black borders, and the two edges of each
    border rule read as separate boundaries 9px apart — the finder returned 10 columns for a
    6-frame sheet and the caller's assert fired. A real gap between rules is a whole frame
    wide, so anything under a small fraction of the median gap is the same rule twice.
    """
    if len(b) < 3:
        return b
    med = sorted(b[i + 1] - b[i] for i in range(len(b) - 1))[(len(b) - 1) // 2]
    out = [b[0]]
    for x in b[1:]:
        if x - out[-1] < 0.15 * med:
            out[-1] = (out[-1] + x) // 2
        else:
            out.append(x)
    return out


def grid(img):
    a = np.array(img.convert('RGB')).astype(int)
    h, w, _ = a.shape
    # The page white is MEASURED, not assumed. A hardcoded cutoff has now been raised
    # twice chasing ever-lighter rules (500 -> 690 -> ...), and each raise is a guess that
    # the next sheet's white is 765. Shin's Aug 2 sheet is compressed: its page reads 762
    # and its rules 700-729, so a 690 cutoff found TWO of its seven columns. The modal sum
    # over the whole image IS the page — it is by far the most common value on a sheet
    # that is mostly white — and anything below it is a rule or ink. SPAN is what rejects
    # weapons and hilts; the darkness cutoff was never meant to.
    s = a.sum(2)
    page = min(int(np.bincount(s.ravel(), minlength=766).argmax()), 765)
    dark = s < page - 20
    rows = _group([y for y in range(h) if dark[y, :].mean() > SPAN])
    if not rows:
        return [], []     # not a ruled sheet at all — the caller's assert says so, not an IndexError
    # Columns are measured INSIDE the table only. A sheet with anything below the table
    # (the counter sheet's IMPLEMENTATION NOTES box) leaves every vertical rule short of
    # the full page, so a whole-height scan finds the two page edges and nothing else.
    # The table's own bottom rule is not always the last one on the page, so try each
    # horizontal rule as the bottom, deepest first, and keep the first band that shows
    # real vertical rules.
    cols = []
    for bot in reversed(rows[1:] or [h]):
        band = dark[rows[0]:bot]
        cols = _group([x for x in range(w) if band[:, x].mean() > SPAN])
        if len(cols) > 2:
            rows = [r for r in rows if r <= bot]
            # Trim bands that are not move rows: the column header at the top
            # ("MOVE | FRAME 1 | ...") and any notes box below, both a fraction of a
            # real row's height.
            def _bands():
                return [rows[i + 1] - rows[i] for i in range(len(rows) - 1)]
            while len(rows) > 2:
                b = _bands()
                small = 0.5 * sorted(b)[len(b) // 2]
                if b[0] < small:
                    rows = rows[1:]
                elif b[-1] < small:
                    rows = rows[:-1]
                else:
                    break
            # A sliver band BETWEEN move rows is the gap under the table: the table ends
            # there and whatever follows (a notes box) is not a move row.
            b = _bands()
            med = sorted(b)[len(b) // 2] if b else 0
            for i, width in enumerate(b[1:], 1):
                if width < 0.3 * med:
                    rows = rows[:i + 1]
                    break
            break
    if len(cols) > 2:                      # repair a rule a body was sitting across
        sp = sorted(cols[i + 1] - cols[i] for i in range(len(cols) - 1))
        med = sp[len(sp) // 2]
        fixed = [cols[0]]
        for i in range(1, len(cols)):
            if cols[i] - fixed[-1] > 1.6 * med:
                fixed.append((fixed[-1] + cols[i]) // 2)
            fixed.append(cols[i])
        cols = fixed
    return rows, cols


def selftest():
    """The one thing that fails if the page-white measurement regresses.

    Two pages, because both failures are real. The first is a clean 255 page with rules in
    LIGHT GREY (212 -> sum 636, the shade that made four of Kael's rules invisible). The
    second is COMPRESSED — page 254 (sum 762) with rules at 239 (sum 717), which is Shin's
    Aug 2 sheet and which a fixed 690 cutoff read as blank paper. Both carry a dark vertical
    weapon and a band of six hilts, and neither may be promoted to a rule.
    """
    for page, rule in ((255, 212), (254, 239)):
        a = np.full((1000, 1400, 3), page, np.uint8)
        for x in (0, 200, 400, 600, 800, 1000, 1200, 1399):
            a[:, max(0, x - 1):x + 2] = rule
        for y in (0, 500, 999):
            a[max(0, y - 1):y + 2, :] = 129
        a[40:480, 300:307] = 40                              # a raised weapon, one row tall
        for x in range(60, 1340, 200):                       # six hilts at one height
            a[300:308, x:x + 130] = (114, 73, 41)
        rows, cols = grid(Image.fromarray(a))
        assert len(cols) == 8, f'page {page}/rule {rule}: rules not found: {cols}'
        assert len(rows) == 3, f'page {page}/rule {rule}: row rules not found: {rows}'
        assert all(abs(c - 303) > 20 for c in cols), f'weapon promoted to a rule: {cols}'
        assert all(abs(r - 304) > 20 for r in rows), f'hilt band promoted to a rule: {rows}'
    print('cut_sheet_grid selftest OK — clean and compressed pages read, weapons rejected')


def main():
    if len(sys.argv) == 2 and sys.argv[1] == 'selftest':
        return selftest()
    src, outdir, names = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3:]
    outdir.mkdir(parents=True, exist_ok=True)
    img = Image.open(src).convert('RGB')
    rows, cols = grid(img)
    assert len(cols) == 8, f'expected 7 columns (name + 6 frames), got {len(cols) - 1}: {cols}'
    assert len(rows) - 1 == len(names), f'{len(rows) - 1} rows on the sheet, {len(names)} names given'
    for r, name in enumerate(names):
        for c in range(6):
            box = (cols[c + 1] + 3, rows[r] + 3, cols[c + 2] - 3, rows[r + 1] - 3)
            img.crop(box).save(outdir / f'{name}_{c + 1}.png')
        print(f'  {name}: 6 frames  y {rows[r]}-{rows[r + 1]}')


if __name__ == '__main__':
    main()
