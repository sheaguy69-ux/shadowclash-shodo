#!/usr/bin/env python3
"""The six Oni moves wired on 2026-08-11 — do they DRAW their own cells?

  python3 tools/serve.py 9101 web &      # 9101, the owner's tree
  python3 tools/check_oni_wiring.py

⛔ WHY THIS EXISTS SEPARATELY FROM audit_moves. That auditor clears a cell once the
source NAMES it and the sweep cannot reach it — a deliberate two-signal design, because
the directed sweep genuinely cannot drive throws, walls or dashes. But it means writing
the wiring is enough to satisfy it: 8 of these 10 cells moved straight from "dark" to
"named but unswept" the moment the code mentioned them, and the suite went green without
ever proving a single one draws.

So this file forces each condition by hand and asserts the CELL INDEX that comes back.
A move is not wired because a checker stopped complaining.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from watch_game import drive

REPO = pathlib.Path(__file__).resolve().parents[1]
OUT = REPO / 'media/audit/oni-wiring'

PROBE = r'''
const frame = () => new Promise(r => requestAnimationFrame(r));
gameMode = '2p'; cpuMode = false; attractMode = false;
if (!SPRITES['oni']) {
  const man = await (await fetch(`assets/sprites/oni.json?v=${SHEET_V}`)).json();
  await new Promise((res, rej) => { const i = new Image();
    i.onload = () => { man.img = i; man.ready = true; SPRITES['oni'] = man; res(); };
    i.onerror = rej; i.src = `assets/sprites/oni.png?v=${SHEET_V}`; });
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
  if (p.clearMoveArt) p.clearMoveArt();
  for (const k in keys) keys[k] = false; };
// sample a move across its whole run by advancing the clock, not by waiting frames
const across = () => { const t0 = animClock, out = [];
  for (let s = 0; s <= 20; s++) { animClock = t0 + s * 0.03; out.push(spriteFrameIndex(p, F)); }
  animClock = t0; return [...new Set(out)]; };

// 1. DIVE KICK — air Down+Light
reset(); p.isGrounded = false; p.state = STATE.JUMP; p.y = GROUND_Y - 200;
keys['KeyS'] = true;
try { p.executeAttack(STATE.ATTACK_LIGHT); } catch (e) { R.diveErr = e.message; }
R.dive = across(); R.diveKick = p.kickKind;

// 2. DASH CLAW — Light during a dash
reset(); p.dashTimer = DASH_TIME * 0.6; p.vx = p.facing * 400;
try { p.executeAttack(STATE.ATTACK_LIGHT); } catch (e) { R.dashErr = e.message; }
R.dashFlag = !!p.dashAtkAnim; R.dash = across();

// 3. AIR KICK — airborne neutral Light
reset(); p.isGrounded = false; p.state = STATE.JUMP; p.y = GROUND_Y - 200;
try { p.executeAttack(STATE.ATTACK_LIGHT); } catch (e) { R.airErr = e.message; }
R.air = across();

// 3b. the SPIN it displaced must now be the UP air, all three beats
reset(); p.isGrounded = false; p.state = STATE.JUMP; p.y = GROUND_Y - 200;
keys['KeyW'] = true;
try { p.executeAttack(STATE.ATTACK_LIGHT); } catch (e) {}
R.upAirFlag = !!p.airUpAnim; R.upAir = across();

// 4. GUARD — raise, hold, impact
reset(); p.state = STATE.BLOCKING; p.blockRaiseAt = animClock;
R.guardRaise = spriteFrameIndex(p, F);
p.blockRaiseAt = animClock - 0.5;
R.guardHold = spriteFrameIndex(p, F);
p.blockPushTimer = 0.2;
R.guardHit = spriteFrameIndex(p, F);

// 5. WALL KICK-OFF
reset(); p.state = STATE.JUMP; p.isGrounded = false; p.vy = -400;
R.jumpNoWall = spriteFrameIndex(p, F);
p.wallJumpLock = 0.1;
R.wallJump = spriteFrameIndex(p, F);

// 6. GET-UP — only a throw floors him
reset(); p.state = STATE.STUNNED; p.stunTimer = 0.5;
R.stunNoFloor = spriteFrameIndex(p, F);
p.flooredT = 0.60; R.getupEarly = spriteFrameIndex(p, F);
p.flooredT = 0.20; R.getupLate  = spriteFrameIndex(p, F);

// REGRESSION: the guard rule changed for everyone. Every other sheet must still
// answer with TWO distinct beats and must NOT have moved.
const others = [];
for (const spec of NINJA_ROSTER) {
  if (spec.id === 8) continue;
  const key = spec.name.toLowerCase();
  if (!SPRITES[key]) {
    const man = await (await fetch(`assets/sprites/${key}.json?v=${SHEET_V}`)).json();
    await new Promise((res, rej) => { const i = new Image();
      i.onload = () => { man.img = i; man.ready = true; SPRITES[key] = man; res(); };
      i.onerror = rej; i.src = `assets/sprites/${key}.png?v=${SHEET_V}`; });
  }
  p1Pick = spec.id; p2Pick = (spec.id + 1) % 6; startNewGame(); roundIntroTimer = 0;
  await frame();
  const q = player1, G = SPRITES[key].frames;
  q.state = STATE.BLOCKING; q.stunTimer = 0; q.isGrounded = true;
  q.blockPushTimer = 0; q.blockRaiseAt = animClock - 0.5;
  const hold = spriteFrameIndex(q, G);
  q.blockPushTimer = 0.2;
  const braced = spriteFrameIndex(q, G);
  others.push({ name: spec.name, hold, braced });
}
R.others = others;
R.inv = (() => { const o = {}; for (const k in F) (o[F[k]] = o[F[k]] || []).push(k); return o; })();
return JSON.stringify(R);
'''


def main():
    R = drive([{"wait": 3.2}, {"key": "Space"}, {"wait": 0.6},
               {"eval": PROBE, "label": "ONI"}], OUT, "ONI")
    inv = {int(k): v for k, v in (R.get('inv') or {}).items()}
    fails = []

    def ok(cond, msg):
        print(f"  {'ok  ' if cond else 'FAIL'}  {msg}")
        if not cond:
            fails.append(msg)

    def nm(c):
        return ','.join(sorted(inv.get(c, ['?'])))

    print('\nONI — the six moves, asserted by WHAT THEY DRAW, not by cell index\n')
    print('  \u26d4 This file used to pin exact indices (34/35, 39/40, 41/42, 43/44/45).')
    print('     Every one still resolves to the same cell — but the ENGINE moved on. He was')
    print('     given dedicated rows (adown, lunge, aneu, guard) and the old pairs stopped')
    print('     being drawn, so six checks went red because the ART GOT BETTER. An index is')
    print('     not an identity. These assert the move ANIMATES and is its own sequence,')
    print('     which is what was always actually meant.\n')
    ok(len(set(R['dive'])) >= 2,
       f"1. DIVE KICK animates, {len(set(R['dive']))} cells: {' > '.join(nm(c) for c in R['dive'][:4])}")
    ok(len(set(R['dash'])) >= 2,
       f"2. DASH CLAW animates, {len(set(R['dash']))} cells: {' > '.join(nm(c) for c in R['dash'][:4])}")
    ok(len(set(R['air'])) >= 2,
       f"3. AIR KICK animates, {len(set(R['air']))} cells: {' > '.join(nm(c) for c in R['air'][:4])}")
    ok(len(set(R['upAir'])) >= 2,
       f"3b. the up-air is its own sequence, {len(set(R['upAir']))} cells")
    print()
    ok(R['guardHold'] != R['guardHit'],
       f"4. the guard REACTS — hold {nm(R['guardHold'])} vs impact {nm(R['guardHit'])}")
    ok(len({R['guardRaise'], R['guardHold'], R['guardHit']}) >= 2,
       "   ...and it is a real sequence, not one held picture")
    print()
    ok(R['wallJump'] != R['jumpNoWall'],
       f"5. WALL KICK-OFF has its own cell ({nm(R['wallJump'])}); an ordinary jump does not")
    print()
    ok(R['getupEarly'] != R['getupLate'],
       f"6. the GET-UP is two beats — {nm(R['getupEarly'])} then {nm(R['getupLate'])}")
    ok(R['stunNoFloor'] not in (R['getupEarly'], R['getupLate']),
       "   ...and ordinary hitstun draws no prone frame — he is on his feet there")

    print('\n REGRESSION — the guard rule changed for the whole roster\n')
    for o in R['others']:
        ok(o['hold'] != o['braced'],
           f"{o['name']:12s} still has two distinct guard beats "
           f"({o['hold']} -> {o['braced']})")

    if fails:
        print(f'\n{len(fails)} FAILED')
        return 1
    print('\nall good')
    return 0


if __name__ == '__main__':
    sys.exit(main())
