#!/usr/bin/env python3
"""Oni wall-shuriken toss (legacy check filename)."""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from watch_game import drive

REPO = pathlib.Path(__file__).resolve().parents[1]
OUT = REPO / 'media/audit/oni-needle'

PROBE = r'''
const frame = () => new Promise(r => requestAnimationFrame(r));
gameMode = '2p'; cpuMode = false; attractMode = false;
if (!SPRITES['oni']) {
  const man = await (await fetch('assets/sprites/oni.json?v=' + SHEET_V)).json();
  await new Promise((res, rej) => { const i = new Image();
    i.onload = () => { man.img = i; man.ready = true; SPRITES['oni'] = man; res(); };
    i.onerror = rej; i.src = 'assets/sprites/oni.png?v=' + SHEET_V; });
}
p1Pick = 8; p2Pick = 0; stagePick = 'bamboo'; startNewGame(); roundIntroTimer = 0;
matchActive = true;
await frame(); await frame();
const p = player1, foe = player2, F = SPRITES['oni'].frames;
const R = {};
const reset = () => { p.hp = 100; p.stamina = 100; p.chakra = 100; p.stunTimer = 0;
  p.state = STATE.IDLE; p.isGrounded = true; p.vx = 0; p.vy = 0; p.rollTimer = 0;
  p.recoveryTimer = 0; p.recoveryTotal = 0; p.dashTimer = 0; p.blockPushTimer = 0;
  p.wallJumpLock = 0; p.flooredT = 0; p.grabbedBy = null; p.throwTimer = 0;
  p.attackAnim = null; p.kickKind = null; p.attackHasConnected = false;
  p.chainComboTier = 0; p.connectTime = -1e9; p.windedTimer = 0;
  p.stars = 0; p.starCd = 0; p.wallThrowT = 0; p.projectiles = [];
  p.wallDir = 0; p.wallRunning = false; p.clingTime = 0;
  if (p.clearMoveArt) p.clearMoveArt();
  for (const k in keys) keys[k] = false; };

reset(); p.isGrounded = false; p.state = STATE.WALL_CLING; p.wallDir = -1;
p.facing = -p.wallDir; p.stars = ANCHOR_STARS;
R.clingCell = spriteFrameIndex(p, F);
R.canThrow = p.canThrowFromWall();

const before = p.projectiles.length;
let threw = false;
try { threw = p.throwWallProjectile(); } catch (e) { R.throwErr = e.message; }
R.threw = threw;
R.wallThrowT = p.wallThrowT;
R.projectileCount = p.projectiles.length - before;
R.projKind = p.projectiles.length ? p.projectiles[p.projectiles.length-1].kind : null;

const cells = [];
const t0 = p.wallThrowT;
for (let s = 0; s <= 8; s++) {
  p.wallThrowT = t0 * (1 - s/8);
  cells.push(spriteFrameIndex(p, F));
}
R.throwCells = cells;
p.wallThrowT = 0;
R.settleCell = spriteFrameIndex(p, F);

R.inv = (() => { const o = {}; for (const k in F) (o[F[k]] = o[F[k]] || []).push(k); return o; })();
return JSON.stringify(R);
'''


def main():
    R = drive([{"wait": 3.2}, {"key": "Space"}, {"wait": 0.6},
               {"eval": PROBE, "label": "ONI-NEEDLE"}], OUT, "ONI-NEEDLE")
    inv = {int(k): v for k, v in (R.get('inv') or {}).items()}
    fails = []
    def ok(cond, msg):
        print(f"  {'ok  ' if cond else 'FAIL'}  {msg}")
        if not cond: fails.append(msg)
    def nm(c): return ','.join(sorted(inv.get(c, ['?'])))

    print("\nONI WALL-NEEDLE TOSS\n")
    ok(R.get('canThrow') is True, f"canThrowFromWall() true for Oni on the wall (got {R.get('canThrow')})")
    ok(R.get('threw') is True, f"throwWallProjectile() fired (got {R.get('threw')})")
    ok(R.get('wallThrowT', 0) > 0, f"wallThrowT window opened ({R.get('wallThrowT')})")
    ok(R.get('projectileCount') == 1, f"one projectile spawned ({R.get('projectileCount')})")
    ok(R.get('projKind') == 'star', f"projectile is a SHURIKEN (got {R.get('projKind')})")
    tc = R.get('throwCells') or []
    # last sample is wallThrowT=0 (the settle), first 8 are the throw window
    throwFrames = tc[:-1]
    uniq = sorted(set(throwFrames))
    print(f"\n    throw anim cells sampled: {[nm(c) for c in tc]}")
    ok(len(uniq) >= 3, f"the toss ANIMATES across its window ({len(uniq)} distinct cells)")
    man = json.load(open(REPO / 'web/assets/sprites/oni.json'))
    needleCells = set(man['frames']['wallthrow'+str(i)] for i in range(1, 7))
    throwOnly = [c for c in uniq if c not in needleCells]
    ok(not throwOnly, f"every toss frame is a wallthrow cell (strays: {[nm(c) for c in throwOnly]})")
    print(f"    cling cell = {nm(R.get('clingCell'))}; settle cell = {nm(R.get('settleCell'))}")
    ok(R.get('settleCell') == man['frames']['wallslide'], "settle returns to wallslide (not a needle cell)")

    if fails:
        print(f"\n{len(fails)} FAILED")
        return 1
    print("\nall good")
    return 0

if __name__ == '__main__':
    sys.exit(main())
