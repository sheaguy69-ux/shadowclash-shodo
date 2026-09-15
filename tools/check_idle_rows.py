#!/usr/bin/env python3
"""The idle row is read from the SHEET, not hard-coded to six.

835 put a 12-beat feral prowl on Ember and the draw branch was
`[F.xidle1 .. F.xidle6]` — beats 7-12 would have been packed, referenced and never
drawn. It now reads rowCells(F,'xidle'), so this asserts three things that together
stop that regression:

  1. every fighter's xidle row is CONTIGUOUS (rowCells stops at the first hole, so a
     gapped row silently truncates where the old .filter() did not);
  2. the draw branch still reads the row rather than a fixed list;
  3. a row longer than the drawn breath WRAPS instead of cosine-scrubbing — a cycle
     played backwards drags his claws out of the dust they just made.

    python3 tools/check_idle_rows.py
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SP = ROOT / 'web' / 'assets' / 'sprites'
fails = []

for jp in sorted(SP.glob('*.json')):
    man = json.loads(jp.read_text())
    F, cols = man.get('frames', {}), man.get('cols', 0)
    row = [i for i in range(1, 17) if f'xidle{i}' in F]
    if not row:
        continue
    if row != list(range(1, len(row) + 1)):
        fails.append(f'{jp.name}: xidle row is gapped {row} — rowCells would truncate it')
    bad = [i for i in row if not isinstance(F[f'xidle{i}'], int) or not 0 <= F[f'xidle{i}'] < cols]
    if bad:
        fails.append(f'{jp.name}: xidle{bad} point outside 0..{cols - 1}')
    print(f'  {jp.stem:12s} xidle x{len(row):<2d} -> cells {[F[f"xidle{i}"] for i in row]}')

html = (ROOT / 'web' / 'index.html').read_text()
if "rowCells(F, 'xidle')" not in html:
    fails.append("index.html: the idle branch no longer reads rowCells(F,'xidle') — "
                 "a hard-coded list throws away every beat past the sixth")
if not re.search(r"poses\.length > 6\) return poses\[Math\.floor\(p\.animPhase\) % poses\.length\]", html):
    fails.append('index.html: the >6-beat WRAP is gone — a drawn cycle would ping-pong')

if fails:
    print('\n'.join('  FAIL ' + f for f in fails)); sys.exit(1)
print('  idle rows OK')
