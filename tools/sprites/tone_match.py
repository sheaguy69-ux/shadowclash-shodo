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
    json.dump(man, open(mp, 'w'), separators=(',', ':'))
    print(f'{name}: {len(table)} cells tone-matched to {target}, {skipped} already at or below it')


if __name__ == '__main__' and len(__import__('sys').argv) > 1:
    _main()
