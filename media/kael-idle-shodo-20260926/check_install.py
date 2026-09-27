#!/usr/bin/env python3
"""Recheck the approved Kael idle installation from its repository source folder."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RECEIPT = json.loads((HERE / 'INSTALLATION.json').read_text())
BASE = RECEIPT['baseline_commit']

def before(path):
    return subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=REPO)

old = json.loads(before('web/assets/sprites/kael.json'))
man = json.loads((REPO / 'web/assets/sprites/kael.json').read_text())
old_art = Image.open(io.BytesIO(before('web/assets/sprites/kael.png'))).convert('RGBA')
art = Image.open(REPO / 'web/assets/sprites/kael.png').convert('RGBA')
assert old['cols'] == 345 and man['cols'] == 351
assert art.size == (351 * 300, 320)
assert art.crop((0, 0, old_art.width, old_art.height)).tobytes() == old_art.tobytes(), 'prior cells changed'
routes = {**{f'xidle{i+1}': 345+i for i in range(6)}, 'idle': 345, 'idle2': 345, 'land3': 345}
assert man['frames'] == {**old['frames'], **routes}, 'unrelated move route changed'
assert man['combatFrames'] == {key: old['frames'][key] for key in routes}
assert man['combatReferenceIdle'] == old['frames']['idle']
assert man['mirror'] == {**old['mirror'], **{str(i): True for i in range(345, 351)}}
assert man['footAdj'] == {**old.get('footAdj', {}), **{str(i): 1 for i in range(345, 351)}}
changed = {'cols', 'frames', 'mirror', 'footAdj', 'combatFrames', 'combatReferenceIdle'}
assert {k:v for k,v in man.items() if k not in changed} == {k:v for k,v in old.items() if k not in changed}
for i, digest in enumerate(RECEIPT['approved_frame_sha256'], 1):
    source = HERE / 'frames' / f'frame-{i:02d}.png'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest, f'source {i} changed'
    alpha = np.asarray(art.crop(((344+i)*300, 0, (345+i)*300, 320)))[..., 3]
    y, x = np.nonzero(alpha >= 128)
    assert len(x) and 0 < x.min() <= x.max() < 299 and 0 < y.min() <= y.max() < 319, f'cell {344+i} clipped'
    assert y.max() == 308, f'cell {344+i} floor differs'
old_index = json.loads(before('web/assets/runtime-sprites/index.json'))
index = json.loads((REPO / 'web/assets/runtime-sprites/index.json').read_text())
assert index['sheetVersion'] == 874
for key, value in old_index.items():
    if key not in ('sheetVersion', 'fighters'):
        assert index[key] == value, key
for fighter, descriptor in old_index['fighters'].items():
    if fighter != 'kael':
        assert index['fighters'][fighter] == descriptor, fighter
for path, digest in RECEIPT['preserved_asset_sha256'].items():
    assert hashlib.sha256((REPO / path).read_bytes()).hexdigest() == digest, f'unrelated asset changed: {path}'
# ponytail: reuse the existing runtime pixel oracle rather than building another pack checker.
subprocess.run([sys.executable, 'tools/build_runtime_sprites.py', '--check', '--fighter', 'kael'], cwd=REPO, check=True)
print('PASS: six approved sources, append-only atlas, collision routes, shared floor and runtime pixels')
