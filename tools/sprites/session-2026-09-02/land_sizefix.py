"""Central landing of the verify fleet's LAND rows (owner pre-approved Sep 1: "yes").
Append-only: each DISTINCT candidate image becomes one new cell at the end of its sheet
(keys that shared a cell before share the new one too); keys repointed; old cells left
as orphans for the two-step strip. Asserts the original sheet prefix is byte-identical."""
import json, sys, hashlib, numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
S = '/private/tmp/claude-501/-Users-anthonyguy-SHADOWCLASH-1-0-2/9551097b-df90-4c80-8abf-d16ed89ab400/scratchpad'
R = '/Users/anthonyguy/SHADOWCLASH.1.0*2/SHODO-EDITION/web/assets/sprites'
APPLY = '--apply' in sys.argv
d = json.load(open(f'{S}/verify_result.json'))
ledger = {}
for f in d['fighters']:
    name = f['fighter']; m = json.load(open(f'{R}/{name}.json')); fw, fh, cols = m['frameW'], m['frameH'], m['cols']
    png = np.array(Image.open(f'{R}/{name}.png').convert('RGBA')); assert png.shape == (fh, cols*fw, 4), (name, png.shape)
    by_hash, order, repoint, rows = {}, [], {}, []
    for r in f['rows']:
        if r['verdict'] != 'LAND': continue
        rows.append(r['row'])
        for c in r['cells']:
            key = c['key']; assert key in m['frames'], (name, key)
            im = np.array(Image.open(c['path']).convert('RGBA')); assert im.shape == (fh, fw, 4), (name, key, im.shape)
            h = hashlib.md5(im.tobytes()).hexdigest()
            if h not in by_hash: by_hash[h] = cols + len(order); order.append(im)
            repoint[key] = (m['frames'][key], by_hash[h])
    # keys that share an OLD cell must all be repointed together, or the untouched sibling keeps the small art
    old2new = {}
    for k, (o, n) in repoint.items(): old2new.setdefault(o, set()).add(n)
    split = {o: n for o, n in old2new.items() if len(n) > 1}
    assert not split, (name, 'one old cell got two different candidates', split)
    stragglers = [k for k, o in m['frames'].items() if o in old2new and k not in repoint]
    for k in stragglers: repoint[k] = (m['frames'][k], next(iter(old2new[m['frames'][k]])))
    ledger[name] = {'rows': rows, 'keys': len(repoint), 'new_cells': len(order), 'cols': [cols, cols + len(order)], 'stragglers': stragglers}
    print(f"{name:12s} rows {len(rows):2d} keys {len(repoint):3d} new cells {len(order):3d} cols {cols}->{cols+len(order)} stragglers {stragglers}")
    if not APPLY: continue
    out = np.concatenate([png] + order, axis=1)
    for k, (o, n) in repoint.items(): m['frames'][k] = n
    m['cols'] = cols + len(order)
    Image.fromarray(out).save(f'{R}/{name}.png'); json.dump(m, open(f'{R}/{name}.json', 'w'))
    chk = np.array(Image.open(f'{R}/{name}.png').convert('RGBA'))
    assert chk.shape == (fh, m['cols']*fw, 4) and (chk[:, :cols*fw] == png).all(), name
json.dump(ledger, open(f'{S}/land_ledger.json', 'w'), indent=1)
print('APPLIED' if APPLY else 'DRY RUN')
