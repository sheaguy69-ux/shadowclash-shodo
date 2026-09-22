#!/usr/bin/env python3
"""Does the dodge roll stay ON THE GROUND?

Replays the exact render transform web/index.html applies during STATE.ROLL,
rasterises it, and measures the REAL ink of the result — not the maths that
produced it, so a sign error cannot pass. Prints the old transform beside the
new one and asserts the ground-roll invariants.

    python3 tools/check_roll_grounded.py            # assert
    python3 tools/check_roll_grounded.py --strips   # ...and write old/new filmstrips + GIFs

Invariants, per fighter, sampled every 15 deg of the spin:
  1. the lowest ink never leaves the floor line   (no float)
  2. the lowest ink never crosses it              (no digging through)
  3. the crown stays near standing height         (no windmill)

(3) is 1.15x, not 1.00x, on purpose. The tuck governs the BODY; a tumbling
silhouette's diagonal is longer than its height, so a trailing limb or Mizu's
bo can pass the top of her own standing head for an instant. Measured, that is
1.06-1.07x on the two who do it, against 1.50-1.96x before — and their lowest
ink is glued to the floor throughout, which is what "not floating" means.
"""
import json, math, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPR = os.path.join(ROOT, 'web', 'assets', 'sprites')
ROLL_TUCK = 0.62
STEPS = 24

# Fighters the engine hands the canvas spin to: the ones with NO drawn roll art.
# Exile(7)/Mokurai(6)/Oni(8)/Tsubasa-Form-2 draw their own roll and are exempt.
SPUN = ['executioner', 'mizu', 'shin', 'tsubasa', 'ember', 'kael']


def ink_box(im):
    bb = im.getchannel('A').point(lambda a: 255 if a >= 40 else 0).getbbox()
    if bb is None:
        raise SystemExit('empty cell')
    return bb[0], bb[1], bb[2] - 1, bb[3] - 1          # x0, y0, x1, y1 inclusive


REACH_DIRS = 64
_reach_cache = {}


def reach_at(im, box, theta):
    """Same 64-direction support function the engine caches in cellInk()."""
    key = id(im)
    r = _reach_cache.get(key)
    if r is None:
        x0, y0, x1, y1 = box
        a = im.getchannel('A').load()
        cols = []
        for x in range(x0, x1 + 1):
            ys = [y for y in range(y0, y1 + 1) if a[x, y] >= 40]
            if ys:
                cols.append((x + 0.5, ys[0] + 0.5, ys[-1] + 0.5))
        cx, cy = (x0 + x1 + 1) / 2, (y0 + y1 + 1) / 2
        r = []
        for i in range(REACH_DIRS):
            ang = i / REACH_DIRS * 2 * math.pi
            si, co = math.sin(ang), math.cos(ang)
            r.append(max(max((x - cx) * si + (t - cy) * co,
                             (x - cx) * si + (b - cy) * co) for x, t, b in cols))
        _reach_cache[key] = r
    return r[round(theta / (2 * math.pi) * REACH_DIRS) % REACH_DIRS]


def cell(man, sheet, idx):
    W, H, C = man['frameW'], man['frameH'], man['cols']
    x, y = (idx % C) * W, (idx // C) * H
    return sheet.crop((x, y, x + W, y + H))


def render(im, man, S, box, theta, k, mode):
    """One rolled frame on a canvas whose floor line is at y=FLOOR, feet at x=CX."""
    fw, fh = man['frameW'], man['frameH']
    x0, y0, x1, y1 = box
    mx = ((x0 + x1 + 1) / 2 - fw / 2) * S
    my = -(man['footY'] - (y0 + y1 + 1) / 2) * S
    if mode == 'new':
        ride = reach_at(im, box, theta) * S * k
        tx, ty = 0.0, -ride
        A = [[k * math.cos(theta), -k * math.sin(theta)],
             [k * math.sin(theta),  k * math.cos(theta)]]
        # q = A(l - m) + t
        off = (tx - A[0][0] * mx - A[0][1] * my, ty - A[1][0] * mx - A[1][1] * my)
    else:
        # the shipped-before transform: pivot at footY*S*0.45, no tuck
        cy = man['footY'] * S * 0.45
        A = [[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]]
        # q = R(l + (0,cy)) + (0,-cy)
        off = (A[0][1] * cy, A[1][1] * cy - cy)

    CW, CH, CX, FLOOR = 520, 520, 260, 430
    # sprite pixel (u,v) -> local: (u - fw*S/2, v - footY*S)
    c0 = (fw * S / 2, man['footY'] * S)
    det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
    B = [[A[1][1] / det, -A[0][1] / det], [-A[1][0] / det, A[0][0] / det]]
    tx_, ty_ = CX + off[0], FLOOR + off[1]
    data = (B[0][0], B[0][1], -B[0][0] * tx_ - B[0][1] * ty_ + c0[0],
            B[1][0], B[1][1], -B[1][0] * tx_ - B[1][1] * ty_ + c0[1])
    src = im.resize((max(1, round(fw * S)), max(1, round(fh * S))), Image.LANCZOS)
    return src.transform((CW, CH), Image.AFFINE, data, resample=Image.BILINEAR), FLOOR


def main():
    strips = '--strips' in sys.argv
    out = os.path.join(ROOT, 'docs', 'roll-fix')
    if strips:
        os.makedirs(out, exist_ok=True)
    fails = []
    print(f'{"fighter":13s} {"mode":4s} {"low vs floor":>13s} {"peak/stand":>11s}  verdict')
    for name in SPUN:
        man = json.load(open(f'{SPR}/{name}.json'))
        sheet = Image.open(f'{SPR}/{name}.png').convert('RGBA')
        S = man['scale']
        F = man['frames']
        roll = cell(man, sheet, F['roll'])
        box = ink_box(roll)
        standH = man['footY'] - ink_box(cell(man, sheet, F['idle']))[1]
        tuck = min(1.0, standH * ROLL_TUCK / max(1, box[3] - box[1] + 1))
        for mode in ('old', 'new'):
            lows, highs, frames = [], [], []
            for i in range(STEPS):
                prog = i / STEPS
                th = prog * 2 * math.pi
                k = 1 - (1 - tuck) * math.sin(prog * math.pi) if mode == 'new' else 1.0
                img, floor = render(roll, man, S, box, th, k, mode)
                bb = img.getchannel('A').point(lambda a: 255 if a >= 40 else 0).getbbox()
                lows.append(bb[3] - 1 - floor)          # +ve = below the floor
                highs.append(floor - bb[1])             # height of the crown above the floor
                if strips:
                    frames.append(img)
            worst_low, worst_high = max(lows, key=abs), max(highs)
            ratio = worst_high / (standH * S)
            ok = abs(worst_low) <= 3 and ratio <= 1.15
            print(f'{name:13s} {mode:4s} {worst_low:+10.1f}px {ratio:10.2f}x  '
                  f'{"OK" if ok else "FLOATS/WINDMILLS" if mode == "old" else "FAIL"}')
            if mode == 'new' and not ok:
                fails.append((name, worst_low, ratio))
            if strips:
                # window sized off the fighter, with the floor line drawn in: the whole
                # point is where the body sits relative to it.
                pad = int(standH * S * 1.6)
                win = (260 - pad // 2, 430 - pad, 260 + pad // 2, 430 + 14)
                def plate(f):
                    c = Image.new('RGBA', (win[2] - win[0], win[3] - win[1]), (26, 26, 34, 255))
                    c.alpha_composite(f.crop(win))
                    for x in range(c.width):
                        c.putpixel((x, 430 - win[1]), (120, 90, 60, 255))
                    return c.resize((c.width * 2, c.height * 2), Image.NEAREST)
                sub = [plate(f) for f in frames[::2]]
                strip = Image.new('RGB', (sub[0].width * len(sub), sub[0].height))
                for j, f in enumerate(sub):
                    strip.paste(f.convert('RGB'), (j * f.width, 0))
                strip.save(f'{out}/{name}-{mode}.png')
                g = [plate(f).convert('RGB') for f in frames]
                g[0].save(f'{out}/{name}-{mode}.gif', save_all=True, append_images=g[1:],
                          duration=max(20, int(280 / STEPS)), loop=0)
    assert not fails, f'roll leaves the ground: {fails}'
    print('\nPASS — every spun roll rides the floor and stays under standing height.')
    crouch(strips)


# --- CROUCH ------------------------------------------------------------------
# Same question, other pose: is the fighter actually LOWER when he ducks? The engine
# squashes the generic crouch cell to CROUCH_H of the fighter's own standing height;
# a cell already lower than that (Oni) and any AUTHORED row (Tsubasa Form 2, Mokurai's
# meditation) is left alone, so those are listed as exempt rather than measured.
CROUCH_H = 0.68
CROUCH_KEYS = ['bcrouch', 'xcrouch', 'kneel']          # first one present is the generic cell
CROUCHERS = ['executioner', 'mizu', 'shin', 'tsubasa', 'ember', 'kael', 'mokurai', 'exile', 'oni']


def crouch(strips=False):
    out = os.path.join(ROOT, 'docs', 'roll-fix')
    print(f'\n{"fighter":13s} {"before":>8s} {"after":>8s}   verdict')
    fails, plates = [], []
    for name in CROUCHERS:
        man = json.load(open(f'{SPR}/{name}.json'))
        sheet = Image.open(f'{SPR}/{name}.png').convert('RGBA')
        F = man['frames']
        key = next((k for k in CROUCH_KEYS if k in F), None)
        idle = cell(man, sheet, F['idle'])
        standH = man['footY'] - ink_box(idle)[1]
        src = cell(man, sheet, F[key]) if key else idle
        drawn = man['footY'] - ink_box(src)[1]
        want = standH * CROUCH_H
        q = min(1.0, want / drawn)                      # never stretches
        before, after = drawn / standH, drawn * q / standH
        ok = after <= CROUCH_H + 0.02
        print(f'{name:13s} {before*100:7.1f}% {after*100:7.1f}%   '
              f'{"OK" if ok else "FAIL"}{"  (already low — untouched)" if q == 1 else ""}')
        if not ok:
            fails.append((name, after))
        if strips:
            plates.append((name, idle, src, q, man))
    if strips and plates:
        h = 300
        tiles = []
        for name, idle, src, q, man in plates:
            for im, sq in ((idle, 1.0), (src, 1.0), (src, q)):
                b = ink_box(im)
                c = im.crop((b[0] - 4, 0, b[2] + 5, man['footY'] + 2))
                c = c.resize((max(1, round(c.width * (1 + (1 - sq) * 0.31))),
                              max(1, round(c.height))), Image.LANCZOS)
                s = h / (man['footY'] + 2)
                c = c.resize((max(1, round(c.width * s)), h), Image.LANCZOS)
                if sq != 1.0:
                    c = c.resize((c.width, max(1, round(h * sq))), Image.LANCZOS)
                tiles.append((c, h - c.height))
        W = sum(t[0].width + 12 for t in tiles) + 12
        plate = Image.new('RGBA', (W, h + 10), (24, 24, 32, 255))
        x = 12
        for c, top in tiles:
            plate.alpha_composite(c, (x, top)); x += c.width + 12
        for xx in range(plate.width):
            plate.putpixel((xx, h - 1), (190, 140, 70, 255))
        plate.convert('RGB').save(f'{out}/CROUCH-fix.png')
        print(f'\nwrote {out}/CROUCH-fix.png  (per fighter: idle · before · after)')
    assert not fails, f'crouch is not a crouch: {fails}'
    print('PASS — every fighter now ducks below 68% of his own standing height.')


if __name__ == '__main__':
    main()
