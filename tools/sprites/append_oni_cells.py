#!/usr/bin/env python3
"""Append new Oni pose boards to his EXISTING sheet without repacking it.

    python3 tools/sprites/append_oni_cells.py --sheets web/assets/sprites \
        --add saya=media/pages/oni-held/bostaff-strike ...

WHY APPEND AND NOT REPACK. pack_oni_new.py rebuilds oni.png from the cut-cell dirs
for EVERY board, and those dirs live under media/, which is gitignored — they are
gone. Re-cutting all 63 boards to reproduce 153 working cells, with no recorded
invocation to reproduce, risks regressing art that already ships. Sheets are
append-only by house rule anyway: the original cells are copied byte-identical
here and only new columns are added on the right, so nothing already on screen
can move.

SCALE IS THE WHOLE PROBLEM, and it is why this reuses pack_oni_new rather than
reimplementing. His boards are NOT drawn at one size — measured mask areas across
them run 363 to 1672, i.e. more than twice as big linearly — so packing a new
board at x1.0 makes him balloon the moment that move plays. The anchor is the
WHITE DEMON MASK: rigid, high-contrast, and the same object in every frame, which
is the house "head-geometry scale only" rule. Here the reference is measured off
the ALREADY-PACKED idle cell, so new cells land in the same space as the old ones
by construction.

The mask can be RESTYLED, though, and then its area is silently absurd rather than
wrong-looking. So source_scale's geometric head-band cross-check comes along too,
and a board whose two measures disagree by more than a quarter is reported rather
than trusted.

Boards are drawn facing RIGHT; the roster is authored facing LEFT and the engine
mirrors by facing. So every cell is flipped ONCE here, uniformly — flipping cells
individually to chase claw handedness is what broke him before.
"""
import argparse
import importlib.util
import json
import pathlib

import numpy as np
from PIL import Image

_spec = importlib.util.spec_from_file_location(
    'pack_oni_new', pathlib.Path(__file__).with_name('pack_oni_new.py'))
_p = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_p)
body_box, mask_area, head_band_width, cells_from = (
    _p.body_box, _p.mask_area, _p.head_band_width, _p.cells_from)


def board_scale(cells, ref_area, ref_headw, name):
    """Scale putting this board's mask at the packed sheet's mask size.

    Mask area goes as scale**2, and ref_area is measured off a cell already IN the
    sheet, so this lands in final sheet space directly — no second multiplication.
    """
    areas = sorted(a for a in (mask_area(im) for im in cells.values()) if a)
    if not areas:
        raise SystemExit(f'{name}: no mask found — cannot scale')
    med = areas[len(areas) // 2]
    k = (ref_area / med) ** 0.5

    # ⛔ THE MASK DECIDES; head geometry only REPORTS. pack_oni_new lets geometry override
    # a restyled mask, and that is right when it is measuring a head — but head_band_width
    # takes the top third of the figure, and on these boards the figure is often INVERTED.
    # Measured here: the cartwheel's mask asked x0.394, in family with the other seven
    # boards (0.28-0.44), while geometry asked x0.887 and blew four cells past the 300px
    # frame box. In a cartwheel the top third is his LEGS. The mask is rigid at any
    # orientation and is the only measure an acrobatic pose cannot fool, so it wins and a
    # disagreement is printed for a human rather than acted on.
    widths = sorted(w for w in (head_band_width(im) for im in cells.values()) if w)
    note = ''
    if widths and ref_headw:
        kg = ref_headw / widths[len(widths) // 2]
        if abs(kg - k) > k * 0.25:
            note = (f'  (head geometry x{kg:.3f} disagrees — figure is probably inverted '
                    f'or something thin sits above the head; mask x{k:.3f} kept)')
    return k, note


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sheets', default='web/assets/sprites')
    ap.add_argument('--add', action='append', default=[],
                    help='KEYPREFIX=dir — cells sorted by name become KEYPREFIX1..N')
    ap.add_argument('--dry', action='store_true')
    # The escape hatch the mask/geometry disagreement print exists FOR. When the two
    # measures split (a board whose head proportions differ from the packed idle's),
    # a human measures an upright frame against the shipped standing height and
    # rules — this passes that ruling in. Applies to every --add in the run.
    ap.add_argument('--scale', type=float, default=None,
                    help='override the mask-anchored scale with a measured one')
    # ⛔ THE FLIP IS NOT UNIVERSAL ANY MORE. It was written for the Aug-9 boards, which
    # were all drawn facing RIGHT. Art delivered against docs/handoff/*/…BRIEF.md is
    # specified "FACING LEFT" — the direction the roster is authored in — so flipping it
    # would play the whole move backwards, and no measurement in this tool would catch
    # that. Pass --no-flip for anything drawn to a brief.
    ap.add_argument('--no-flip', dest='flip', action='store_false',
                    help='source already faces LEFT (brief-delivered art); skip the mirror')
    a = ap.parse_args()

    sd = pathlib.Path(a.sheets)
    man = json.loads((sd / 'oni.json').read_text())
    sheet = Image.open(sd / 'oni.png').convert('RGBA')
    FW, FH, FOOT, cols = man['frameW'], man['frameH'], man['footY'], man['cols']
    assert sheet.width == FW * cols, f'sheet {sheet.width} != {FW}*{cols} — refusing to append'

    # Reference = the cell the `idle` key actually draws, already in sheet space.
    idle_i = man['frames']['idle']
    idle_cell = sheet.crop((FW * idle_i, 0, FW * (idle_i + 1), FH))
    ref_area, ref_headw = mask_area(idle_cell), head_band_width(idle_cell)
    if not ref_area:
        # Without the mask there is no scale anchor, and packing at x1.0 would size
        # every new board off whatever the generator happened to draw.
        raise SystemExit(f'no white mask found in packed cell {idle_i} (key idle) — '
                         'that cell is the scale anchor; cannot append blind')
    print(f'reference: packed cell {idle_i} (key idle) mask area {ref_area:.0f}, '
          f'head band {ref_headw:.0f}' if ref_headw else
          f'reference: packed cell {idle_i} mask area {ref_area:.0f}')

    plan = []
    for spec in a.add:
        prefix, _, d = spec.partition('=')
        cells = cells_from(d)
        if not cells:
            raise SystemExit(f'{prefix}: no cells in {d}')
        k, note = board_scale(cells, ref_area, ref_headw, prefix)
        if a.scale:
            note = f'  (mask asked x{k:.3f}; human override)'
            k = a.scale
        print(f'  {prefix:10s} {len(cells)} cells  x{k:.3f}{note}')
        for i, name in enumerate(sorted(cells), 1):
            plan.append((f'{prefix}{i}', cells[name], k, f'{prefix}/{name}'))

    if not plan:
        raise SystemExit('nothing to add')
    clash = [k for k, *_ in plan if k in man['frames']]
    if clash:
        raise SystemExit(f'keys already exist, refusing to overwrite: {clash}')

    out = Image.new('RGBA', (FW * (cols + len(plan)), FH), (0, 0, 0, 0))
    out.paste(sheet, (0, 0))            # originals copied byte-identical
    frames = dict(man['frames'])
    over = []
    for n, (key, im, k, src) in enumerate(plan):
        r = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
        if a.flip:
            r = r.transpose(Image.FLIP_LEFT_RIGHT)  # legacy boards face RIGHT; roster is authored LEFT
        bb = body_box(r)
        if bb is None:
            raise SystemExit(f'{key}: empty after scaling')
        bx0, by0, bx1, by1 = bb
        col = cols + n
        if (by1 - by0 + 1) > FH or (bx1 - bx0 + 1) > FW:
            over.append(f'{key} ({bx1-bx0+1}x{by1-by0+1})')
        out.alpha_composite(r, (FW * col + FW // 2 - (bx0 + bx1) // 2, max(0, FOOT - by1)))
        frames[key] = col

    man['cols'] = cols + len(plan)
    man['frames'] = frames
    print(f'{cols} -> {man["cols"]} cells, {len(frames)} keys')
    if over:
        # ⛔ A POSE THAT DOES NOT FIT GROWS THE BOX — never shrink the body, never crop.
        raise SystemExit('EXCEEDS FRAME BOX, grow frameW/frameH: ' + ', '.join(over))
    if a.dry:
        print('dry run — nothing written')
        return
    out.save(sd / 'oni.png')
    (sd / 'oni.json').write_text(json.dumps(man, indent=1))
    print(f'wrote {sd}/oni.png {out.width}x{out.height}')


def _selfcheck():
    """Appending must never disturb a byte of the original sheet, and must place
    every new cell inside its own column with its feet on footY."""
    import tempfile
    FW, FH, FOOT = 40, 30, 26
    with tempfile.TemporaryDirectory() as td:
        sd = pathlib.Path(td)
        def figure(body, mask_px):
            """A stand-in Oni: coloured body with a WHITE MASK block, the scale anchor."""
            im = Image.new('RGBA', (10, 12), (0, 0, 0, 0))
            im.paste(Image.new('RGBA', (10, 12), body), (0, 0))
            im.paste(Image.new('RGBA', (mask_px, mask_px), (255, 255, 255, 255)), (2, 1))
            return im

        base = Image.new('RGBA', (FW * 2, FH), (0, 0, 0, 0))
        for i, c in enumerate(((255, 0, 0, 255), (0, 255, 0, 255))):
            base.paste(figure(c, 4), (FW * i + 5, FOOT - 11))
        base.save(sd / 'oni.png')
        (sd / 'oni.json').write_text(json.dumps(
            dict(frameW=FW, frameH=FH, footY=FOOT, cols=2, frames={'idle': 0}, scale=0.5)))
        cd = sd / 'new'; cd.mkdir()
        # Drawn at DOUBLE size — the append must scale it back down by the mask, which is
        # the whole point: boards are not delivered at one size.
        big = figure((0, 0, 255, 255), 4).resize((20, 24), Image.NEAREST)
        big.save(cd / 'c1.png')

        before = np.asarray(Image.open(sd / 'oni.png').convert('RGBA')).copy()
        import sys
        argv = sys.argv
        sys.argv = ['x', '--sheets', str(sd), '--add', f'test={cd}']
        try:
            main()
        finally:
            sys.argv = argv

        after = Image.open(sd / 'oni.png').convert('RGBA')
        m = json.loads((sd / 'oni.json').read_text())
        assert m['cols'] == 3 and m['frames']['test1'] == 2, m
        assert np.array_equal(np.asarray(after)[:, :FW * 2], before), 'ORIGINAL CELLS MOVED'
        a3 = np.asarray(after)[:, FW * 2:]
        ys = np.nonzero(a3[:, :, 3].any(1))[0]
        assert ys.max() == FOOT, f'feet at {ys.max()}, want footY {FOOT}'
        # The double-size source must come back down to the packed figure's height.
        assert abs((ys.max() - ys.min() + 1) - 12) <= 1, \
            f'new cell is {ys.max()-ys.min()+1}px tall, packed figure is 12 — mask scale failed'
        print('selfcheck OK — originals byte-identical, new cell seated on footY, '
              'double-size source scaled back by its mask')


if __name__ == '__main__':
    import sys
    if '--selfcheck' in sys.argv:
        _selfcheck()
    else:
        main()
