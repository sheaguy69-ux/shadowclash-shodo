#!/usr/bin/env python3
"""Pull a light-grey Ember cell back to the sheet's own body tone.

⛔ NOT A FLAT MULTIPLY. A flat gain dims the drawn white slash FX and the ivory
eye along with the cloth, and those are the two things on him that must stay
bright. So the gain is applied to the MID-TONES only and faded out at both ends:
black outline (already ~0, nothing to take) and anything at or above BRIGHT
(FX, eye, steel highlights) are left exactly as drawn.

Hue is preserved: the gain multiplies R,G,B together, so the warm khaki rag
stays khaki and only its value moves. Alpha is never touched.
"""
import numpy as np

# ⛔ THE KNEE IS RELATIVE TO THE CELL, NOT A GLOBAL CONSTANT. A fixed knee at 95
# protects CLOTH on his light cells -- their body tone is 70-87, so much of the
# garment already sits above 95 and gets only partial gain. adown5 asked for 44.6
# and landed at 64. Scaling the knee off the cell's own body tone darkens the
# garment fully while still leaving the drawn white slash FX and the ivory eye
# (which sit at 3-5x the body tone) untouched.
KNEE_MUL   = 1.6   # below body*1.6 -> full gain
BRIGHT_MUL = 2.6   # at/above body*2.6 -> untouched
KNEE_MIN, BRIGHT_MIN = 95.0, 150.0


def body_tone(keyed):
    """Mean luminance of the cell's cloth, with outline and FX deciles removed."""
    al = keyed[:, :, 3] >= 128
    if al.sum() < 200:
        return None
    rgb = keyed[:, :, :3].astype(float)
    lum = (0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2])[al]
    lo, hi = np.percentile(lum, [10, 90])
    mid = lum[(lum > lo) & (lum < hi)]
    return float(np.mean(mid)) if mid.size else float(np.median(lum))


def darken(rgba, gain, body=None):
    """gain < 1 darkens. Returns a new array; alpha and bright pixels untouched."""
    out = rgba.copy()
    rgb = out[:, :, :3].astype(float)
    lum = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]
    b = body if body else KNEE_MIN / KNEE_MUL
    knee = max(KNEE_MIN, b * KNEE_MUL)
    bright = max(BRIGHT_MIN, b * BRIGHT_MUL, knee + 1.0)
    w = np.clip((bright - lum) / (bright - knee), 0.0, 1.0)[:, :, None]
    g = 1.0 + (gain - 1.0) * w
    out[:, :, :3] = np.clip(rgb * g, 0, 255).astype(np.uint8)
    return out


def to_tone(rgba, target, iters=4):
    """Solve for the gain that actually lands the body tone on `target`."""
    b0 = body_tone(rgba)
    if not b0 or b0 <= target:
        return rgba, 1.0, b0
    g = target / b0
    out = rgba
    for _ in range(iters):
        out = darken(rgba, g, b0)
        got = body_tone(out)
        if not got or abs(got - target) < 0.4:
            break
        g *= target / got
        g = max(0.15, min(1.0, g))
    return out, g, body_tone(out)


if __name__ == '__main__':
    # self-check: a mid-grey darkens, pure white and pure black do not
    a = np.zeros((1, 3, 4), np.uint8); a[..., 3] = 255
    a[0, 0, :3] = 0; a[0, 1, :3] = 70; a[0, 2, :3] = 255
    out = darken(a, 0.75)
    assert tuple(out[0, 0, :3]) == (0, 0, 0), out[0, 0]
    assert 50 <= out[0, 1, 0] <= 55, out[0, 1]
    assert tuple(out[0, 2, :3]) == (255, 255, 255), out[0, 2]
    assert (out[..., 3] == 255).all()
    print('darken self-check OK — black held, white held, mid-grey 70 ->', out[0, 1, 0])


# ---------------------------------------------------------------------------
# CLI: write a fighter's per-cell tone-match table into his manifest.
#
#   python3 tools/sprites/tone_match.py ember 44.6
#
# Writes manifest["bodyTone"] = { "<cell>": [gain, body] }. The engine reads it
# in keyedShodoCell and applies the same curve this file defines, once per cell,
# into the cell cache -- so it costs one multiply per cell for the whole match,
# and the atlas PNG is never rewritten. Delete the key to undo.
# ---------------------------------------------------------------------------
def new_art_chroma(pack_dir, alpha=200):
    """Value-preserving chroma offsets sampled from the approved new boards.

    ⛔ WHY A VALUE->CHROMA CURVE AND NOT A PER-MATERIAL RECOLOUR: the live sheet is
    ACHROMATIC. Clustered, every one of its levels sits at saturation 0.00-0.07 and
    R-B +0.2..+1.6 -- his scarf is drawn GREY. There is no colour signal in the source
    to segment scarf from steel, so a per-material map has nothing to key off. What the
    new art does give is a strong, measurable relationship between VALUE and chroma:
    neutral below lum 85, a warm hump of R-B +14..+23 across 85-139 (the khaki rag), and
    falling again above 175. Transferring that curve puts the khaki on the scarf band.

    # ponytail: 1-D on luminance. Ceiling: steel highlights that share the rag's value
    # get warmed too (per-band R-B sd is 11-19, so the band is not pure). Upgrade path is
    # a real scarf mask, which only exists once the new art replaces the cells outright.

    Offsets are value-neutral by construction (the grey of the mean is subtracted), so
    they add hue without moving the tone the per-cell gain just set.
    """
    import json, os
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    man = json.load(open(os.path.join(pack_dir, 'MANIFEST.json')))
    px = []
    for s in man['sheets']:
        a = np.asarray(Image.open(os.path.join(pack_dir, s['file'])).convert('RGBA'))
        al = a[:, :, 3] >= alpha
        if al.sum():
            px.append(a[:, :, :3][al])
    x = np.vstack(px).astype(float)
    rng = np.random.default_rng(0)
    if len(x) > 4_000_000:
        x = x[rng.choice(len(x), 4_000_000, replace=False)]
    lum = 0.2126 * x[:, 0] + 0.7152 * x[:, 1] + 0.0722 * x[:, 2]
    b = np.clip(lum, 0, 255).astype(int)
    sums = np.zeros((256, 3)); cnt = np.zeros(256)
    np.add.at(sums, b, x); np.add.at(cnt, b, 1)
    ok = cnt >= 200
    idx = np.where(ok)[0]
    mean = np.zeros((256, 3))
    for ch in range(3):
        mean[:, ch] = np.interp(np.arange(256), idx, (sums[idx, ch] / cnt[idx]))
    k = np.ones(9) / 9
    for ch in range(3):
        mean[:, ch] = np.convolve(np.pad(mean[:, ch], (4, 4), mode='edge'), k, mode='valid')
    mlum = 0.2126 * mean[:, 0] + 0.7152 * mean[:, 1] + 0.0722 * mean[:, 2]
    off = mean - mlum[:, None]
    off[:4] = 0                      # the black contour stays black
    return [[round(float(v), 3) for v in row] for row in off]


def _main():
    import json, os, sys
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from keyer_emu import keyed_cell

    name = sys.argv[1] if len(sys.argv) > 1 else 'ember'
    target = float(sys.argv[2]) if len(sys.argv) > 2 else 44.6
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'web', 'assets', 'sprites')
    mp = os.path.join(base, f'{name}.json')
    man = json.load(open(mp))
    W, H, C = man['frameW'], man['frameH'], man['cols']
    sheet = np.asarray(Image.open(os.path.join(base, f'{name}.png')).convert('RGBA'))
    idxs = sorted({v for v in man['frames'].values() if isinstance(v, int)})
    assert max(idxs) < C, f'{name} is not a single row; the engine indexes cells by sx/sw'

    table, skipped = {}, 0
    for i in idxs:
        fh = 419 if (name == 'ember' and i < 385) else H
        c, r = i % C, i // C
        a = sheet[r * H:r * H + fh, c * W:c * W + W]
        if fh < H:
            a = np.vstack([a, np.zeros((H - fh, W, 4), np.uint8)])
        k = keyed_cell(a)
        b = body_tone(k)
        if not b or b <= target:
            skipped += 1
            continue
        _, g, got = to_tone(k, target)
        table[str(i)] = [round(g, 4), round(b, 2)]
    man['bodyTone'] = table
    pack = os.environ.get('NEW_ART_PACK')
    if pack:
        man['bodyChroma'] = new_art_chroma(pack)
        print(f'  chroma LUT sampled from {pack}')
    json.dump(man, open(mp, 'w'), separators=(',', ':'))
    print(f'{name}: {len(table)} cells tone-matched to {target}, {skipped} already at or below it')


if __name__ == '__main__' and len(__import__('sys').argv) > 1:
    _main()
