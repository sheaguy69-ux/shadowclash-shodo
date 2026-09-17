#!/usr/bin/env python3
"""A drawn ROW has to play as a row — read from the sheet, never collapsed to one cell.

Owner, Sep 16 2026: "fix all his specials frames by frames, and dont make them all one
moments." Four rows have hit this, three of them because the engine never named them at all:

  xidle  — 835 held the feral prowl on ONE cell and 836 packed his twelve-beat board, but
           the draw branch was a hard-coded [xidle1..xidle6]; beats 7-12 would have been
           packed, referenced and never drawn.
  slip   — SHADOW SLIP REVERSAL. The branch was gated on spec.id === 0 and read `xslip1..6`,
           a key NO sheet carries, so it never fired for anybody while Ember's eight drawn
           beats sat dark.
  gblk   — eight drawn guard beats; the guard rule picked ONE still for the whole block.
  hitm   — eight drawn flinch beats on Ember AND Tsubasa; only hurt2/hurt3 borrowed two
           cells out of the middle.

So this asserts both halves: the sheet still carries a contiguous row, and the engine still
reads it as a row. A hole in the row silently truncates it (rowCells stops at the first
gap), and a fixed list in the code silently throws the tail away.

    python3 tools/check_drawn_rows.py
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SP = ROOT / 'web' / 'assets' / 'sprites'
HTML = (ROOT / 'web' / 'index.html').read_text()
CODE = '\n'.join(l for l in HTML.split('\n')
                 if 'const SHEET_V' not in l and not l.lstrip().startswith('//'))

# row -> (minimum beats worth having, why the engine must read it generically)
ROWS = {
    'xidle': (3, "rowCells(F, 'xidle')"),
    'slip':  (4, "rowCells(F, 'slip')"),
    'gblk':  (4, "rowCells(F, 'gblk')"),
    'hitm':  (4, "rowCells(F, 'hitm')"),
}
fails = []

for jp in sorted(SP.glob('*.json')):
    F = json.loads(jp.read_text()).get('frames', {})
    cols = json.loads(jp.read_text()).get('cols', 0)
    for row, (need, _) in ROWS.items():
        have = [i for i in range(1, 17) if f'{row}{i}' in F]
        if not have:
            continue
        if have != list(range(1, len(have) + 1)):
            fails.append(f'{jp.name}: {row} row is gapped {have} — rowCells truncates at the hole')
        if len(have) < need:
            fails.append(f'{jp.name}: {row} has {len(have)} beats, fewer than the {need} this draws')
        out = [i for i in have if not isinstance(F[f'{row}{i}'], int) or not 0 <= F[f'{row}{i}'] < cols]
        if out:
            fails.append(f'{jp.name}: {row}{out} point outside 0..{cols - 1}')
        print(f'  {jp.stem:12s} {row:6s} x{len(have):<2d} -> {[F[f"{row}{i}"] for i in have]}')

for row, (_, reader) in ROWS.items():
    if reader not in CODE:
        fails.append(f"index.html: the {row} branch no longer reads {reader} — "
                     f"a fixed list throws away every beat past the ones it names")

# the idle cycle specifically: longer than the drawn breath must WRAP, not ping-pong
if not re.search(r'poses\.length > 6\) return poses\[Math\.floor\(p\.animPhase\) % poses\.length\]', CODE):
    fails.append('index.html: the >6-beat idle WRAP is gone — a drawn cycle would ping-pong, '
                 'raking his claws back out of the dust they just made')
# the slip must not be re-gated to one fighter
if re.search(r"p\.spec\.id === 0 && p\.slipAnim", CODE):
    fails.append('index.html: the slip is gated to spec.id === 0 again — that branch has '
                 'never fired for anybody, because no sheet carries an xslip key')

if fails:
    print('\n'.join('  FAIL ' + f for f in fails)); sys.exit(1)
print('  drawn rows OK')
