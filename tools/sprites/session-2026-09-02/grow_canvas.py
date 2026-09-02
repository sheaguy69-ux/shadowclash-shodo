#!/usr/bin/env python3
"""Grow a fighter's cell window without moving the art.

  --width  N   frameW += N: every cell's pixels shift right by N//2 so centre-x is unmoved.
  --height N   frameH += N, footY += N: every cell's pixels shift DOWN by N so the foot line is unmoved.

Nothing is scaled, cropped or re-keyed. Asserts every cell byte-identical at its new offset,
and shifts handAnchor entries with the pixels. Usage:
  python3 grow_canvas.py executioner --width 10 [--apply]
  python3 grow_canvas.py mokurai --height 38 [--apply]
"""
import json, sys, warnings
import numpy as np
from PIL import Image
warnings.simplefilter('ignore', Image.DecompressionBombWarning)
Image.MAX_IMAGE_PIXELS = None
R = '/Users/anthonyguy/SHADOWCLASH.1.0*2/SHODO-EDITION/web/assets/sprites'

def main():
    name = sys.argv[1]
    dw = int(sys.argv[sys.argv.index('--width') + 1]) if '--width' in sys.argv else 0
    dh = int(sys.argv[sys.argv.index('--height') + 1]) if '--height' in sys.argv else 0
    apply_ = '--apply' in sys.argv
    assert (dw > 0) ^ (dh > 0), 'exactly one of --width / --height'
    m = json.load(open(f'{R}/{name}.json'))
    fw, fh, footY, cols = m['frameW'], m['frameH'], m['footY'], m['cols']
    png = np.array(Image.open(f'{R}/{name}.png').convert('RGBA'))
    assert png.shape == (fh, cols * fw, 4), (name, png.shape, (fh, cols * fw))
    nfw, nfh = fw + dw, fh + dh
    dx = dw // 2                       # keep centre-x: half the new width on each side
    out = np.zeros((nfh, cols * nfw, 4), np.uint8)
    for c in range(cols):
        src = png[:, c * fw:(c + 1) * fw]
        out[dh:dh + fh, c * nfw + dx:c * nfw + dx + fw] = src
        assert (out[dh:dh + fh, c * nfw + dx:c * nfw + dx + fw] == src).all()
    for k, v in (m.get('handAnchor') or {}).items():
        m['handAnchor'][k] = [v[0] + dx, v[1] + dh]
    m['frameW'], m['frameH'], m['footY'] = nfw, nfh, footY + dh
    print(f'{name}: frameW {fw}->{nfw}, frameH {fh}->{nfh}, footY {footY}->{footY+dh}, '
          f'{cols} cells shifted (+{dx}px x, +{dh}px y), handAnchor entries {len(m.get("handAnchor") or {})}')
    if not apply_:
        print('DRY RUN — pass --apply to write'); return
    Image.fromarray(out).save(f'{R}/{name}.png')
    json.dump(m, open(f'{R}/{name}.json', 'w'))
    chk = np.array(Image.open(f'{R}/{name}.png').convert('RGBA'))
    assert chk.shape == (nfh, cols * nfw, 4)
    for c in range(cols):
        assert (chk[dh:dh + fh, c * nfw + dx:c * nfw + dx + fw] == png[:, c * fw:(c + 1) * fw]).all(), c
    print('APPLIED — every cell byte-identical at its new offset')

main()
