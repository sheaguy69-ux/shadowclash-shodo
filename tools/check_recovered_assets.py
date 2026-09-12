#!/usr/bin/env python3
"""Verify the recovered approved799 checkpoint: python3 tools/check_recovered_assets.py [git-ref]."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REF = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'
MANIFEST = 'docs/recovery/recovered-assets-799.json'

def read(path):
    return subprocess.check_output(['git', 'show', f'{REF}:{path}'], cwd=ROOT)

record = json.loads(read(MANIFEST))
blobs = {}
for path, digest in record['files'].items():
    data = read(path)
    assert hashlib.sha256(data).hexdigest() == digest, f'Unexpected bytes: {path}'
    blobs[path] = data
assert b'const SHEET_V = 799;' in blobs['web/index.html']
for fighter in 'executioner mizu shin tsubasa ember kael mokurai exile'.split():
    stem = f'web/assets/sprites/{fighter}'
    meta = json.loads(blobs[stem + '.json'])
    png = blobs[stem + '.png']
    assert png[:8] == b'\x89PNG\r\n\x1a\n', fighter
    width, height = struct.unpack('>II', png[16:24])
    assert (width, height) == (meta['frameW'] * meta['cols'], meta['frameH']), fighter
    assert all(isinstance(meta['frames'][f'dive{i}'], int) and 0 <= meta['frames'][f'dive{i}'] < meta['cols'] for i in range(1, 7)), fighter
print(f'PASS: {len(blobs)} exact recovered files; eight complete DownHeavy atlas routes; build799.')
