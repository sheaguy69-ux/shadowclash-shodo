#!/usr/bin/env python3
"""EVERY fighter's guard must REACT — the braced beat, drawn, on a hit the guard ate.

  python3 tools/serve.py 9101 web &      # 9101, the owner's tree
  python3 tools/check_guard_beat.py

The guard is two pictures: the hold, and the beat where the body braces behind it.
`blockPushTimer` is the engine's own answer to "did this guard just absorb something" —
it is nonzero on exactly that frame and never on an idle guard — so the rule is one line
and the only thing that varies per fighter is which KEY the braced beat was packed under.

That variance is the whole bug this file exists for. Two sheets had `block2` aliased onto
`block` at the time their braced beat was drawn, so it went in under its own name:

  * exile   -> xblock2   (found and wired earlier)
  * mokurai -> mblock2   (packed at cell 226 and left DARK — his guard was one still
                          picture, and a `bblock` early-return above the rule meant he
                          could not have reacted even if the key had been right)

Asserting the drawn CELL INDEX, not a flag: a guard that "works" while drawing the same
cell for both beats is exactly the failure that shipped twice.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from watch_game import drive

REPO = pathlib.Path(__file__).resolve().parents[1]
OUT = REPO / 'media/audit/guard-beat'

PROBE = r'''
const frame = () => new Promise(r => requestAnimationFrame(r));
const ROSTER = [0,1,2,3,4,5,6,7,8];
const out = [];
for (const id of ROSTER) {
  const key = NINJA_ROSTER.find(s => s.id === id).name.toLowerCase();
  if (!SPRITES[key]) {                       // benched fighters are never preloaded
    const man = await (await fetch(`assets/sprites/${key}.json?v=${SHEET_V}`)).json();
    await new Promise((res, rej) => { const i = new Image();
      i.onload = () => { man.img = i; man.ready = true; SPRITES[key] = man; res(); };
      i.onerror = rej; i.src = `assets/sprites/${key}.png?v=${SHEET_V}`; });
  }
  gameMode = '2p'; cpuMode = false; attractMode = false;
  p1Pick = id; p2Pick = (id + 1) % 6; stagePick = 'bamboo'; startNewGame();
  roundIntroTimer = 0; matchActive = true;
  await frame();
  const p = player1, F = SPRITES[key].frames;
  p.state = STATE.BLOCKING; p.stunTimer = 0; p.isGrounded = true;
  p.blockPushTimer = 0;
  const hold = spriteFrameIndex(p, F);
  p.blockPushTimer = 0.2;                    // the engine's own "this guard ate one"
  const braced = spriteFrameIndex(p, F);
  out.push({ id, name: p.spec.name, hold, braced });
}
return JSON.stringify(out);
'''


def main():
    rows = drive([
        {"wait": 3.2}, {"key": "Space"}, {"wait": 0.6},
        {"eval": PROBE, "label": "GUARD"},
    ], OUT, "GUARD")

    fails = []
    print('\nGUARD BEAT — the drawn cell, per fighter\n')
    print(f"  {'fighter':14s} {'hold':>6s} {'braced':>7s}")
    for r in rows:
        distinct = isinstance(r['hold'], int) and isinstance(r['braced'], int) \
            and r['hold'] != r['braced']
        flag = 'ok  ' if distinct else 'FAIL'
        print(f"  {flag}  {r['name']:14s} {str(r['hold']):>6s} {str(r['braced']):>7s}")
        if not distinct:
            fails.append(f"{r['name']}: guard never reacts — hold and braced are both "
                         f"cell {r['hold']}")

    if fails:
        print(f'\n{len(fails)} FAILED')
        for f in fails:
            print(f'  - {f}')
        return 1
    print('\nall good — every guard has two beats')
    return 0


if __name__ == '__main__':
    sys.exit(main())
