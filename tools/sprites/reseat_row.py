#!/usr/bin/env python3
"""Put a floating row back on the floor, append-only.

    python3 tools/sprites/reseat_row.py exile xidle1..6,idle,idle2 [--gap 3] [--dry]

A packed cell is supposed to stop 1-4px above `footY` — that is the contact point the
engine draws every fighter against. A row whose ink stops higher than that is a fighter
standing in the air, and if the beats disagree with each other he also BOBS while standing
still. Measured across the roster, every idle row has a foot-gap spread of 0-1px except
Ember's feral prowl (4, and his claws legitimately hang below the soles) and Exile's, which
sits 11px up and swings 8px beat to beat.

WHAT THIS DOES, AND WHAT IT REFUSES TO DO.
  * Measures the ink bottom THROUGH THE RUNTIME KEYER, because that is what is actually
    drawn — file alpha lies (see tools/sprites/keyer_emu.py).
  * Translates the RAW cell down by whole pixels. An integer shift is lossless: no resample,
    no filtering, no colour touched. The ink is identical, it is just lower in the cell.
  * APPENDS the result as new cells and repoints the keys. Nothing already on the sheet
    moves, old cells stay exactly where they are for whatever else points at them.
  * ⛔ REFUSES to shift a cell UP past the floor, and refuses any shift that would push ink
    out of the bottom of the cell. Growing the frame is a separate, deliberate call
    (grow_frame.py --down) — cropping a fighter to make him fit is never the answer.
"""
import argparse, json, pathlib, re, sys
import numpy as np
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from keyer_emu import keyed_cell

Image.MAX_IMAGE_PIXELS = None
REPO = pathlib.Path(__file__).resolve().parents[2]
SP = REPO / 'web' / 'assets' / 'sprites'


def expand(spec):
    """'xidle1..6,idle,idle2' -> ['xidle1',...,'xidle6','idle','idle2']"""
    out = []
    for part in spec.split(','):
        part = part.strip()
        m = re.match(r'^([a-zA-Z_]+)(\d+)\.\.(\d+)$', part)
        if m:
            stem, a, b = m.group(1), int(m.group(2)), int(m.group(3))
            out += [f'{stem}{i}' for i in range(a, b + 1)]
        elif part:
            out.append(part)
    return out


def ink_bottom(arr):
    op = keyed_cell(arr)[..., 3] >= 80
    ys = np.nonzero(op.any(1))[0]
    return int(ys.max()) if len(ys) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('fighter')
    ap.add_argument('keys', help="e.g. 'xidle1..6,idle,idle2'")
    ap.add_argument('--gap', type=int, default=3, help='px of ink to leave above footY')
    ap.add_argument('--dry', action='store_true')
    args = ap.parse_args()

    jp, pp = SP / f'{args.fighter}.json', SP / f'{args.fighter}.png'
    man = json.loads(jp.read_text())
    F, W, H, footY, cols = man['frames'], man['frameW'], man['frameH'], man['footY'], man['cols']
    sheet = Image.open(pp).convert('RGBA')
    assert sheet.size == (cols * W, H), f'sheet {sheet.size} != {(cols * W, H)}'
    src = np.array(sheet)

    keys = expand(args.keys)
    missing = [k for k in keys if k not in F]
    if missing:
        sys.exit(f'REFUSE: no such key(s): {missing}')

    want = footY - args.gap
    plan, made = {}, {}          # key -> new index ; old cell -> new index
    new_cells = []
    for k in keys:
        ci = F[k]
        if ci in made:
            plan[k] = made[ci]
            continue
        cell = src[:, ci * W:(ci + 1) * W]
        b = ink_bottom(cell)
        if b is None:
            sys.exit(f'REFUSE: {k} (cell {ci}) has no ink')
        dy = want - b
        if dy == 0:
            print(f'  {k:10s} cell {ci:4d} already at gap {args.gap} — left alone')
            continue
        if dy < 0:
            sys.exit(f'REFUSE: {k} (cell {ci}) sits BELOW the target — this tool only '
                     f'lowers a floating row, it does not lift drawn ink off the floor')
        if b + dy > H - 1:
            sys.exit(f'REFUSE: {k} (cell {ci}) would push ink past the cell bottom. '
                     f'Grow the cell first: grow_frame.py {args.fighter} <taller> --down')
        out = np.zeros_like(cell)
        out[dy:] = cell[:H - dy]
        idx = cols + len(new_cells)
        new_cells.append(out)
        made[ci] = idx
        plan[k] = idx
        print(f'  {k:10s} cell {ci:4d} ink bottom {b} -> {b + dy}  (down {dy}px)  new cell {idx}')

    if not new_cells:
        print('  nothing to do'); return
    if args.dry:
        print(f'  DRY — would append {len(new_cells)} cells at {cols}..{cols + len(new_cells) - 1}; '
              f'repoint {sorted(plan)}')
        return

    before = {k: v for k, v in F.items()}
    out = np.zeros((H, (cols + len(new_cells)) * W, 4), np.uint8)
    out[:, :cols * W] = src
    for i, c in enumerate(new_cells):
        out[:, (cols + i) * W:(cols + i + 1) * W] = c
    assert (out[:, :cols * W] == src).all(), 'existing cells changed'
    Image.fromarray(out, 'RGBA').save(pp)

    F.update(plan)
    man['cols'] = cols + len(new_cells)
    jp.write_text(json.dumps(man, indent=2) + '\n')
    moved = [k for k in plan if before[k] != F[k]]
    print(f'  +{len(new_cells)} cells -> cols {cols}..{man["cols"] - 1}; repointed {sorted(moved)}')


if __name__ == '__main__':
    main()
