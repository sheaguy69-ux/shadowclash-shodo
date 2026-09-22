#!/usr/bin/env python3
"""Cut a delivery board, register it to a fighter's body, append it to the sheet.

    python3 tools/sprites/pack_rows.py shin board.png --n 6 --keys gsback --dry
    python3 tools/sprites/pack_rows.py shin board.png --n 6 --keys gsback

Written after doing this by hand three times in one day (the Executioner's 14 boards,
Shin's second mode, Shin's taijutsu grid). The three steps that actually matter, and the
mistake each one exists to stop:

  CUT     — from the BEAT NUMERALS when the board has them. An even-pitch guess walks off
            the moment a figure lunges, and a boot-band anchor reads the caption printed
            under the figures (URONAME 3 put its first cut at x=90 on a 1448px board).
  SCALE   — ONE uniform factor for the whole board, anchored on the ready-guard beats.
            Never per-cell MATCH_HEIGHT: it scales a compact recoil ~2x against an
            extended lunge and the row boils.
  ANCHOR  — the board's FLOOR LINE, so a beat that leaves the ground stays off the ground.
            Measured INSIDE the crop; mixing page rows with crop rows puts a row hundreds
            of px out (caught on the taijutsu grid before it shipped).

Append-only: every existing cell is asserted byte-identical before the file is written,
and the json is edited with a regex so `json.dump` cannot reflow the owner's indentation.
"""
import argparse, json, pathlib, re, sys
import numpy as np
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import cut_strip
Image.MAX_IMAGE_PIXELS = None

DARK = 170          # his body reads under this; FX and highlights read over it


def num_cuts(path, n):
    """The pitch the generator drew on: the row holding exactly n small, evenly-spaced blobs."""
    from scipy import ndimage as nd
    A = np.asarray(Image.open(path).convert('RGB')).astype(int)
    H, W = A.shape[:2]
    lab, _ = nd.label(A.min(2) <= 224)
    objs = nd.find_objects(lab)
    for i, sl in enumerate(objs):
        h = sl[0].stop - sl[0].start
        if h < 10 or h > H * 0.12:
            continue
        peers = [j for j, s2 in enumerate(objs)
                 if s2 and abs((s2[0].stop - s2[0].start) - h) <= max(3, h * 0.18)
                 and s2[0].start < sl[0].stop and s2[0].stop > sl[0].start
                 and (s2[1].stop - s2[1].start) < W * 0.06]
        if len(peers) == n:
            xs = sorted((objs[j][1].start + objs[j][1].stop) / 2 for j in peers)
            dx = np.diff(xs)
            if dx.std() / dx.mean() < 0.12:
                return [int(round((xs[k] + xs[k + 1]) / 2)) for k in range(n - 1)]
    return None


def body_h(a):
    """Hood-top to boot-bottom. FX is thin, so take the band where he is actually wide."""
    m = (a[:, :, 3] > 128) & (a[:, :, :3].max(2) < DARK)
    wid = m.sum(1)
    if not wid.any():
        return a.shape[0]
    th = np.where(wid >= max(2, wid.max() * 0.18))[0]
    return int(th[-1] - th[0] + 1)


def foot_cx(a):
    """x of the boots. The engine plants him by the feet, not by the tip of his weapon."""
    m = a[:, :, 3] > 128
    ys = np.where(m.any(1))[0]
    band = m[max(ys[0], ys[-1] - max(4, int(len(ys) * 0.10))):ys[-1] + 1]
    xs = np.where(band.any(0))[0]
    return float((xs[0] + xs[-1]) / 2)


def resize_premul(im, scale):
    """Premultiply before LANCZOS or the transparent rim drags a dark halo into the edge."""
    a = np.asarray(im).astype(float)
    a[:, :, :3] *= a[:, :, 3:4] / 255.0
    sm = Image.fromarray(a.astype('uint8'), 'RGBA').resize(
        (max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
    b = np.asarray(sm).astype(float)
    b[:, :, :3] = np.clip(b[:, :, :3] * 255.0 / np.clip(b[:, :, 3:4], 1, None), 0, 255)
    return Image.fromarray(b.astype('uint8'), 'RGBA')


def target_body(sheet, cfg):
    """His own idle, measured — never a number carried over from another fighter."""
    a = np.asarray(sheet.crop((cfg['frameW'] * cfg['frames']['idle'], 0,
                               cfg['frameW'] * (cfg['frames']['idle'] + 1), cfg['frameH'])))
    return float(body_h(a))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('fighter'); ap.add_argument('board')
    ap.add_argument('--n', type=int, required=True)
    ap.add_argument('--keys', required=True, help='family name, or comma-separated key names')
    ap.add_argument('--title', type=float, default=0.13)
    ap.add_argument('--skip', default='', help='1-based beats to drop, e.g. 4,7')
    # ⛔ PANELLED BOARDS: the numeral finder needs a row of n evenly-spaced small blobs, and a
    # panel grid that prints its numeral INSIDE each box does not give it one — it then falls
    # back to even pitch, which walked off on the AJUMP row and returned a 268px body against
    # a 185px target. The panel WALLS are exact on such a board, so let the caller pass them.
    ap.add_argument('--cuts', default='', help='explicit x cut positions, e.g. 346,677,1003,1331')
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()

    jf = pathlib.Path(f'web/assets/sprites/{a.fighter}.json')
    pf = pathlib.Path(f'web/assets/sprites/{a.fighter}.png')
    cfg = json.loads(jf.read_text())
    W, H, FY = cfg['frameW'], cfg['frameH'], cfg['footY']
    sheet = Image.open(pf).convert('RGBA')
    TARGET = target_body(sheet, cfg)

    cuts = [int(x) for x in a.cuts.split(',') if x.strip()] or num_cuts(a.board, a.n)
    if cuts and len(cuts) != a.n - 1:
        sys.exit(f'{len(cuts)} cuts for {a.n} beats — need {a.n - 1}')
    cells, _ = cut_strip.cut(a.board, n=a.n, title=a.title, verbose=False, forced=cuts)
    skip = {int(s) for s in a.skip.split(',') if s.strip()}
    got = {i: c for i, c in enumerate(cells, 1) if c is not None and i not in skip}
    if not got:
        sys.exit('no cells cut')

    arrs = {i: c[0] for i, c in got.items()}
    anchors = [i for i in (1, a.n) if i in arrs] or sorted(arrs)[:2]
    scale = TARGET / np.mean([body_h(arrs[i]) for i in anchors])
    floor = float(np.median([c[2] + c[4] for c in got.values()]))   # page-y of each ink bottom

    names = a.keys.split(',') if ',' in a.keys else \
            [f'{a.keys}{k}' for k in range(1, len(got) + 1)]
    if len(names) != len(got):
        sys.exit(f'{len(names)} key names for {len(got)} cells')

    print(f'{a.fighter}: cut {len(got)}/{a.n} via {"explicit" if a.cuts else "numerals" if cuts else "pitch"}  '
          f'scale {scale:.4f} ({"UP" if scale > 1.02 else "down"})  '
          f'guard body {np.mean([body_h(arrs[i]) for i in anchors]):.1f}px -> {TARGET:.0f}px')
    # ⛔ NO CELL MAY OVERFLOW ITS FRAME. One uniform scale is right, but nothing checked that
    # the BIGGEST beat still fits, so an extended pose could be scaled past frameW/frameH and
    # get cropped by the paste — flying_kick4/5 came out with the head clipped at y0 and 126px
    # of the kick missing off the right edge. Shrink the whole row until the widest and tallest
    # beat both fit; uniform is preserved, and the row simply reads a touch smaller.
    fit = 1.0
    for i in arrs:
        _a = arrs[i]                     # not `a` — that is the argparse namespace
        ys, xs = np.where(_a[:, :, 3] > 0)
        if not len(ys):
            continue
        w, h = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
        # ⛔ AGAINST footY, NOT frameH. The paste is bottom-anchored at footY minus lift, so
        # the usable height is what sits ABOVE the floor line — checking the full frameH
        # passed a row that still clipped its head, because the extra room is all below him.
        fit = min(fit, (W - 8) / (w * scale), (FY - 6) / (h * scale))
    if fit < 1.0:
        print(f'  ⚠ row would overflow the {W}x{H} frame — scale {scale:.4f} -> {scale * fit:.4f}')
        scale *= fit
    if scale > 1.15:
        print(f'  ⚠ {scale:.2f}x UPSCALE — the board is undersized; those cells will read softer')

    n0 = sheet.width // W
    new, frames = [], {}
    for slot, i in enumerate(sorted(got)):
        sm = resize_premul(Image.fromarray(arrs[i].astype('uint8'), 'RGBA'), scale)
        ink = np.asarray(sm)[:, :, 3] > 0
        ys, xs = np.where(ink)
        lift = (floor - (got[i][2] + got[i][4])) * scale
        # ⛔ NOTHING GOES UNDER THE GROUND. The placed ink bottom is exactly footY - lift, so a
        # NEGATIVE lift buries the cell. That happens whenever a beat reaches a limb lower than
        # the row's median ink bottom — a flying kick's extended leg does it every time, and it
        # put flying_kick4/5 twenty-five pixels into the floor, which is the "his legs cut off"
        # the owner reported. Airborne beats keep their large positive lift untouched.
        lift = max(lift, 1.0)
        cell = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        cell.alpha_composite(sm, (int(round(W / 2 - foot_cx(np.asarray(sm).astype(int)))),
                                  int(round(FY - lift - (ys.max() + 1)))))
        frames[names[slot]] = n0 + len(new); new.append(cell)
        print(f'  beat {i} -> {names[slot]:<16} cell {n0 + len(new) - 1}  '
              f'body {body_h(np.asarray(cell).astype(int)):>3}px  lift {lift:+.0f}')
    if a.dry:
        print('DRY — nothing written'); return

    before = np.asarray(sheet).copy()
    out = Image.new('RGBA', (W * (n0 + len(new)), H), (0, 0, 0, 0))
    out.paste(sheet, (0, 0))
    for k, c in enumerate(new): out.paste(c, (W * (n0 + k), 0))
    out.save(pf)
    chk = Image.open(pf).convert('RGBA')
    assert (np.asarray(chk.crop((0, 0, W * n0, H))) == before).all(), 'ORIGINAL CELLS CHANGED'

    t = jf.read_text()
    t = re.sub(r'("cols":\s*)\d+', lambda m: m.group(1) + str(n0 + len(new)), t, count=1)
    m = re.search(r'("frames":\s*\{)(.*?)(\n\s*\})', t, re.S)
    keep = {k: v for k, v in frames.items() if f'"{k}"' not in t}
    repoint = {k: v for k, v in frames.items() if k not in keep}
    if keep:
        t = t[:m.end(2)] + ',\n' + ',\n'.join(f'   "{k}": {v}' for k, v in keep.items()) + t[m.end(2):]
    for k, v in repoint.items():                    # a REPLACEMENT row: repoint, do not duplicate
        t = re.sub(rf'("{re.escape(k)}":\s*)\d+', lambda mm: mm.group(1) + str(v), t, count=1)
    jf.write_text(t)
    d = json.loads(jf.read_text())
    assert max(d['frames'].values()) < d['cols']
    print(f'appended {len(new)} cells -> {d["cols"]}; {len(keep)} new keys, '
          f'{len(repoint)} repointed; originals byte-identical')


if __name__ == '__main__':
    main()
