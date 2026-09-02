"""Pack GPT's chain-less Chain to the Wall board into exile's cell window.

Scale comes from a POSE-MATCHED comparison against the cells already packed for these
same eight beats (area median 0.764, which is the 0.76 this board family was approved
at). Each new cell is anchored to the ink bottom and centre-x of the cell it replaces,
so the move's existing arc — already wired and verified in the engine — is unchanged.
"""
import json, sys
import numpy as np
from PIL import Image
sys.path.insert(0, '/private/tmp/claude-501/-Users-anthonyguy-SHADOWCLASH-1-0-2/3fa5f15d-d94b-4fc3-a77b-8dbde6db14fe/scratchpad')
from keyer_emu import keyed_cell
Image.MAX_IMAGE_PIXELS = None
R = '/Users/anthonyguy/SHADOWCLASH.1.0*2/SHODO-EDITION/web/assets/sprites'
S = '/private/tmp/claude-501/-Users-anthonyguy-SHADOWCLASH-1-0-2/9551097b-df90-4c80-8abf-d16ed89ab400/scratchpad/xboard'
NAMES = ['ready', 'coil', 'cast', 'taut', 'yank', 'reel', 'wall-ready', 'brace']
SCALE = 0.764

def resize_premult(rgba, f):
    a = rgba[..., 3:4].astype(np.float64) / 255.0
    pm = np.concatenate([rgba[..., :3].astype(np.float64) * a, a * 255.0], -1)
    h, w = rgba.shape[:2]
    nw, nh = max(1, round(w * f)), max(1, round(h * f))
    ch = [np.array(Image.fromarray(pm[..., c].astype(np.float32), 'F').resize((nw, nh), Image.LANCZOS)) for c in range(4)]
    o = np.stack(ch, -1)
    na = np.clip(o[..., 3:4], 0, 255)
    rgb = np.where(na > 0.5, np.clip(o[..., :3] / np.maximum(na / 255.0, 1e-6), 0, 255), 0)
    return np.concatenate([rgb, na], -1).round().astype(np.uint8)

m = json.load(open(f'{R}/exile.json')); fw, fh, footY = m['frameW'], m['frameH'], m['footY']
sheet = np.array(Image.open(f'{R}/exile.png').convert('RGBA'))
rows = []
for k, nm in enumerate(NAMES, 1):
    cell = m['frames'][f'xanchor{k}']
    ref = keyed_cell(sheet[:, cell*fw:(cell+1)*fw]); ra = ref[..., 3] > 40
    rys, rxs = np.nonzero(ra)
    r_bottom, r_cx = rys.max(), (rxs.min() + rxs.max()) / 2.0
    src = np.array(Image.open(f'{S}/beat{k}_{nm}.png').convert('RGBA'))
    sc = resize_premult(src, SCALE)
    sa = sc[..., 3] > 40
    sys_, sxs = np.nonzero(sa)
    out = np.zeros((fh, fw, 4), np.uint8)
    oy = int(r_bottom - sys_.max())                                  # same ground/arc height as the cell it replaces
    ox = int(round(r_cx - (sxs.min() + sxs.max()) / 2.0))            # same centre-x
    for yy, xx in zip(sys_, sxs):
        ty, tx = oy + yy, ox + xx
        if 0 <= ty < fh and 0 <= tx < fw: out[ty, tx] = sc[yy, xx]
    # keyer disarm: exile's cells carry a faint border pixel so the runtime keyer does
    # not read the cell as a card and eat it (dropping it cost 55% of a cell once).
    border = np.zeros((fh, fw), bool); border[:3,:] = border[-3:,:] = border[:,:3] = border[:,-3:] = True
    faint = (ref[..., 3] > 0) & (ref[..., 3] <= 40) & border
    out[faint & (out[..., 3] == 0)] = ref[faint & (out[..., 3] == 0)]
    Image.fromarray(out).save(f'{S}/cell_xanchor{k}.png')
    na = out[..., 3] > 40
    nys, nxs = np.nonzero(na)
    kept = (keyed_cell(out)[..., 3] > 40).sum() / max(1, na.sum())
    clipped = nxs.min() <= 0 or nxs.max() >= fw-1 or nys.min() <= 0 or nys.max() >= fh-1
    rows.append(dict(beat=k, name=nm, cell=cell, ink=int(na.sum()), bottom=int(nys.max()),
                     ref_bottom=int(r_bottom), keyer=round(float(kept), 4), clipped=bool(clipped)))
    print(f"{k} {nm:11s} -> cell {cell:3d}  ink {int(na.sum()):6d}  bottom {int(nys.max())} (ref {int(r_bottom)})  keyer {kept:.4f}  clipped={clipped}")
json.dump(rows, open(f'{S}/pack_meta.json','w'), indent=1)
