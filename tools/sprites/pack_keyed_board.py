#!/usr/bin/env python3
"""Append an ALREADY-KEYED 8-frame board to a fighter sheet, append-only.

    python3 tools/sprites/pack_keyed_board.py <fighter> <board_dir> <keyprefix> [--dry]
    python3 tools/sprites/pack_keyed_board.py tsubasa ~/Desktop/'tsubasa 2'/...-v3 lock --wire lock1..8

WHY NOT pack_shodo_row. That tool white-composites the board and re-keys it at
min-channel >= 205, which is right for a printed card and wrong here: these boards
arrive already keyed (alpha 0/255), and a second key eats Tsubasa's near-white eyes
and blade highlights (the 708 defect). Cells go in with their authored alpha and are
NOT re-keyed — the engine keys at draw time (keyedShodoCell).

THE RULER IS INK AREA ON THE BOARD'S READY-GUARD BEAT (beat 1 unless --anchor says
otherwise), matched to the fighter's packed idle. `eye_scale.py` lists tsubasa's eye as
UNMEASURABLE (the artist draws it 1.10x on run, 1.27x on divecut) and says to use ink
area. Validated against the eight boards already packed on this sheet: beat-1 anchoring
predicts the applied scale to 1.6% mean on the six sound rows (idle -0.1%, hook-throw
-0.7%, wallslide +1.0%, crouch +1.2%, run -1.8%, light-combo1 +4.1%), and disagrees only
with the two rows the size campaign already flags as oversized (air-talon +28%, roll
+11%). Both rulers — sqrt(area) and bbox height — agree to ~2% per board, so each board
really was packed at ONE uniform scale.

⛔ DO NOT ANCHOR ON THE LARGEST BEAT. A slash arc, an impact ring or a blood spray adds
ink far from the body: the victory board's beat 4 measures 1.9x its own stance and would
have packed the whole row at 0.41 instead of 0.54. Anchor on a beat that is a STANCE.

⛔ ONE SCALE PER BOARD, never per cell: per-cell height matching makes a curled beat the
same height as an extended one and the row boils.
⛔ SHARED WINDOW: the union ink bbox of all eight beats is placed once, so a beat that
leaves the ground stays off the ground and the sway between beats survives.
⛔ PREMULTIPLIED RESIZE: a straight-alpha LANCZOS pulls background colour into every
edge and fringes the whole silhouette.
⛔ GROW THE CELL, NEVER SHRINK THE FIGHTER: if a scaled beat will not fit frameW x
frameH this refuses. Bump the cell and re-run.

Anchor: union ink bottom lands on footY-3 (packed cells on this sheet measure 3-4px of
ink above footY, never on it).
"""
import argparse, glob, json, pathlib, sys
from collections import deque

import numpy as np
from PIL import Image

REPO = pathlib.Path(__file__).resolve().parents[2]
SP = REPO / 'web' / 'assets' / 'sprites'
FOOT_GAP = 3


def black_key(a):
    """Three of these boards ship on an opaque black card. Flood the pure-black
    background in from the border; the fighter's darkest ink measures (32,27,27)."""
    if (a[..., 3] < 8).mean() >= 0.20:
        return a
    H, W = a.shape[:2]
    dark = a[..., :3].max(2) <= 18
    seen = np.zeros((H, W), bool)
    q = deque()
    for x in range(W):
        for y in (0, H - 1):
            if dark[y, x] and not seen[y, x]:
                seen[y, x] = True; q.append((x, y))
    for y in range(H):
        for x in (0, W - 1):
            if dark[y, x] and not seen[y, x]:
                seen[y, x] = True; q.append((x, y))
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and dark[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True; q.append((nx, ny))
    out = a.copy()
    out[..., 3][seen] = 0
    return out


def ink_bbox(m):
    ys, xs = np.nonzero(m)
    return xs.min(), ys.min(), xs.max(), ys.max()


def premult_resize(a, w, h):
    f = a.astype(np.float64)
    al = f[..., 3:4] / 255.0
    pm = np.concatenate([f[..., :3] * al, f[..., 3:4]], 2)
    im = Image.fromarray(np.clip(pm, 0, 255).astype(np.uint8), 'RGBA').resize((w, h), Image.LANCZOS)
    o = np.array(im).astype(np.float64)
    al = np.maximum(o[..., 3:4] / 255.0, 1e-6)
    o[..., :3] = np.clip(o[..., :3] / al, 0, 255)
    return o.astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('fighter'); ap.add_argument('board'); ap.add_argument('prefix')
    ap.add_argument('--wire', default='', help='comma list key=beat, e.g. block=1,block2=2')
    ap.add_argument('--anchor', type=int, default=1, help='beat whose stance sets the scale')
    ap.add_argument('--scale', type=float, default=None,
                    help='explicit scale, overriding the anchor beat. For a board with NO '
                         'idle-like beat (a round intro that ends sword-out, a KO that ends '
                         'on the floor) the anchor ruler has nothing fair to measure against; '
                         '784 hit this and corrected all four executioner rows the same way.')
    ap.add_argument('--dry', action='store_true')
    args = ap.parse_args()

    jp, pp = SP / f'{args.fighter}.json', SP / f'{args.fighter}.png'
    man = json.loads(jp.read_text())
    W, H, FY, cols = man['frameW'], man['frameH'], man['footY'], man['cols']
    sheet = Image.open(pp).convert('RGBA')
    sarr = np.array(sheet)

    # canon = median ink area of the packed idle beats
    idle_cells = sorted({i for k, i in man['frames'].items()
                         if k in ('idle', 'idle2') or k.startswith('xidle')})
    canon = float(np.median([(sarr[:, c * W:(c + 1) * W, 3] >= 128).sum() for c in idle_cells]))

    frames = sorted(glob.glob(str(pathlib.Path(args.board) / 'frame-*.png')))
    assert frames, f'no frame-*.png in {args.board}'
    arrs = [black_key(np.array(Image.open(f).convert('RGBA'))) for f in frames]
    masks = [a[..., 3] >= 128 for a in arrs]
    areas = [int(m.sum()) for m in masks]
    scale = args.scale if args.scale else float(np.sqrt(canon / areas[args.anchor - 1]))

    boxes = [ink_bbox(m) for m in masks]
    ux0 = min(b[0] for b in boxes); uy0 = min(b[1] for b in boxes)
    ux1 = max(b[2] for b in boxes); uy1 = max(b[3] for b in boxes)
    uw, uh = round((ux1 - ux0 + 1) * scale), round((uy1 - uy0 + 1) * scale)
    if uw > W or uh > H - (H - FY) - FOOT_GAP:
        sys.exit(f'REFUSE: scaled window {uw}x{uh} exceeds cell {W}x{H} (footY {FY}) — grow the cell')

    dx = (W - uw) // 2 - round(ux0 * scale)
    dy = (FY - FOOT_GAP) - round(uy1 * scale)

    ruler = 'EXPLICIT --scale' if args.scale else f'anchor beat {args.anchor} {areas[args.anchor-1]}px'
    print(f'{args.fighter}/{args.prefix}: idle canon {canon:.0f}px  {ruler} '
          f'-> scale {scale:.4f}   window {uw}x{uh}  beats {len(frames)}')

    out = Image.new('RGBA', ((cols + len(frames)) * W, H), (0, 0, 0, 0))
    out.paste(sheet, (0, 0))          # paste, not composite: keeps the originals byte-identical
    newkeys = {}
    for n, a in enumerate(arrs):
        sw, sh = max(1, round(a.shape[1] * scale)), max(1, round(a.shape[0] * scale))
        im = Image.fromarray(premult_resize(a, sw, sh), 'RGBA')
        idx = cols + n
        out.alpha_composite(im, (idx * W + dx, dy))
        newkeys[f'{args.prefix}{n + 1}'] = idx

    # placement + art-loss gates, measured on the written cells
    oa = np.array(out)
    for n, m in enumerate(masks):
        c = cols + n
        cm = oa[:, c * W:(c + 1) * W, 3] >= 128
        if not cm.any():
            sys.exit(f'REFUSE: beat {n+1} landed empty')
        bx0, by0, bx1, by1 = ink_bbox(cm)
        want = round(m.sum() * scale * scale)
        loss = 1 - cm.sum() / max(want, 1)
        clipped = bx0 == 0 or by0 == 0 or bx1 == W - 1 or by1 == H - 1
        print(f'  beat{n+1}: ink {cm.sum():6d}px (want {want:6d}, dev {100*loss:+5.1f}%)  '
              f'bbox {bx1-bx0+1:3d}x{by1-by0+1:3d}  footY-bottom {FY-by1:2d}  {"CLIPPED" if clipped else ""}')
        if clipped:
            sys.exit('REFUSE: beat clipped by the cell edge — grow the cell')

    assert out.crop((0, 0, cols * W, H)).tobytes() == sheet.tobytes(), 'original cells changed'

    for spec in filter(None, args.wire.split(',')):
        k, b = spec.split('=')
        newkeys[k] = cols + int(b) - 1

    if args.dry:
        print(f'  DRY — would add {len(frames)} cells at {cols}..{cols+len(frames)-1}; '
              f'keys {sorted(newkeys)}')
        return
    man['frames'].update(newkeys)
    man['cols'] = cols + len(frames)
    out.save(pp)
    jp.write_text(json.dumps(man, indent=2) + '\n')
    print(f'  +{len(frames)} cells -> cols {cols}..{man["cols"]-1}; keys {sorted(newkeys)}')


if __name__ == '__main__':
    main()
