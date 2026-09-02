"""Land ember's judge-approved size rows. Append-only, same law as land_sizefix.py:
one new cell per DISTINCT candidate image, keys repointed together, originals byte-identical."""
import json, sys, hashlib
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
S = '/private/tmp/claude-501/-Users-anthonyguy-SHADOWCLASH-1-0-2/9551097b-df90-4c80-8abf-d16ed89ab400/scratchpad'
R = '/Users/anthonyguy/SHADOWCLASH.1.0*2/SHODO-EDITION/web/assets/sprites'
APPLY = '--apply' in sys.argv
j = json.load(open(f'{S}/ember_result.json'))['judge']
m = json.load(open(f'{R}/ember.json')); fw, fh, cols = m['frameW'], m['frameH'], m['cols']
png = np.array(Image.open(f'{R}/ember.png').convert('RGBA')); assert png.shape == (fh, cols*fw, 4)
by_hash, order, repoint = {}, [], {}
for r in j['land_rows']:
    for c in r['cells']:
        im = np.array(Image.open(c['path']).convert('RGBA')); assert im.shape == (fh, fw, 4), c
        h = hashlib.md5(im.tobytes()).hexdigest()
        if h not in by_hash: by_hash[h] = cols + len(order); order.append(im)
        repoint[c['key']] = (m['frames'][c['key']], by_hash[h])
old2new = {}
for k, (o, n) in repoint.items(): old2new.setdefault(o, set()).add(n)
split = {o: n for o, n in old2new.items() if len(n) > 1}
assert not split, ('one old cell got two candidates', split)
strag = [k for k, o in m['frames'].items() if o in old2new and k not in repoint]
for k in strag: repoint[k] = (m['frames'][k], next(iter(old2new[m['frames'][k]])))
print(f"ember rows {len(j['land_rows'])} keys {len(repoint)} new cells {len(order)} cols {cols}->{cols+len(order)} stragglers {strag}")
if APPLY:
    out = np.concatenate([png] + order, axis=1)
    for k, (o, n) in repoint.items(): m['frames'][k] = n
    m['cols'] = cols + len(order)
    Image.fromarray(out).save(f'{R}/ember.png'); json.dump(m, open(f'{R}/ember.json', 'w'))
    chk = np.array(Image.open(f'{R}/ember.png').convert('RGBA'))
    assert chk.shape == (fh, m['cols']*fw, 4) and (chk[:, :cols*fw] == png).all()
    print('APPLIED — original', cols, 'cells byte-identical')
else:
    print('DRY RUN')
