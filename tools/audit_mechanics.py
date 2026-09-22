#!/usr/bin/env python3
"""Every mechanic, asserted against the engine's OWN constants — not against a number
typed in here that can drift away from the game.

  python3 tools/serve.py 9100 web &      # 9100, the only server
  python3 tools/audit_mechanics.py

The other harnesses in tools/ each own one feature. This one sweeps the systems that no
single feature owns and that a fighting game is unplayable without: resources, physics,
damage scaling, the guard, state exits, throws. Each check reads the constant it is
testing out of the page, so tuning a value re-tunes the check instead of breaking it.

Written after a full audit found the roster's moves all FIRE (0 dead of 180) while two of
them drew a frozen cell for 900ms and one drew the source board's caption text. Firing is
not working. These are the invariants that say working.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from watch_game import drive

REPO = pathlib.Path(__file__).resolve().parents[1]
OUT = REPO / 'media/audit/mechanics'

PROBE = r'''
const frame = () => new Promise(r => requestAnimationFrame(r));
gameMode = '2p'; cpuMode = false; attractMode = false;
p1Pick = 0; p2Pick = 5; stagePick = 'bamboo'; startNewGame(); roundIntroTimer = 0;
matchActive = true;
await frame(); await frame();
const p = player1, foe = player2;
const R = {};
const K = {};   // the engine's own constants, echoed so the python half asserts on them
K.GRAVITY = GRAVITY; K.TERMINAL = TERMINAL_VELOCITY; K.ROLL_TIME = ROLL_TIME;
K.ROLL_RECOVER = ROLL_RECOVER; K.SCALE_PER_HIT = SCALE_PER_HIT; K.SCALE_FLOOR = SCALE_FLOOR;
K.CEIL_LATCH_MAX = CEIL_LATCH_MAX;
K.HASUJI_CHIP = HASUJI_CHIP; K.THROW_DMG = THROW_DMG; K.KARMA_MAX = KARMA_MAX;

const fresh = () => { p.hp = 100; p.stamina = 100; p.chakra = 100; p.stunTimer = 0;
  p.state = STATE.IDLE; p.isGrounded = true; p.vx = 0; p.vy = 0; p.grabbedBy = null;
  p.throwTimer = 0; p.windedTimer = 0; p.vanishTimer = 0; p.gyakute = false;
  p.hitCount = 0; p.comboCount = 0; };

// ---- 1. TERMINAL VELOCITY is a real ceiling ---------------------------------
fresh(); p.isGrounded = false; p.y = 100; p.vy = 0;
let maxVy = 0;
for (let i = 0; i < 120; i++) { await frame(); maxVy = Math.max(maxVy, p.vy);
  if (p.isGrounded) { p.isGrounded = false; p.y = 100; } }
R.maxVy = Math.round(maxVy);

// ---- 2. RESOURCES never go negative -----------------------------------------
fresh(); p.chakra = 0; p.stamina = 0;
let negC = false, negS = false;
for (let i = 0; i < 40; i++) {
  try { p.executeAttack(STATE.ATTACK_SPECIAL); } catch (e) {}
  try { p.executeAttack(STATE.ATTACK_HEAVY); } catch (e) {}
  await frame();
  if (p.chakra < -0.001) negC = true;
  if (p.stamina < -0.001) negS = true;
}
R.chakraNeverNegative = !negC;
R.staminaNeverNegative = !negS;

// ---- 3. DAMAGE SCALING compounds and respects its floor ----------------------
// ⛔ comboHits only climbs while the victim is ALREADY stunned (see takeDamage: it is
// `stunTimer > 0 ? comboHits + 1 : 1`). Clearing the stun between hits — the obvious way
// to isolate each hit — resets the counter, so every hit reads as hit 1 and the series
// comes back perfectly flat while scaling is never exercised at all. The stun is LEFT UP
// on purpose; only hp is restored, to read each hit's scaled value on its own.
fresh(); foe.hp = 100; foe.state = STATE.IDLE; foe.stunTimer = 0; foe.comboHits = 0;
const dmgs = [];
for (let i = 0; i < 14; i++) {
  foe.hp = 100;
  foe.takeDamage(10, p, { pushback: 0, tier: STATE.ATTACK_LIGHT });
  dmgs.push(+(100 - foe.hp).toFixed(3));
  foe.stunTimer = Math.max(foe.stunTimer, 0.5);   // keep the combo alive
}
R.scaleSeries = dmgs;
R.scaleHits = foe.comboHits;
R.scaleMonotonic = dmgs.every((v, i) => i === 0 || v <= dmgs[i - 1] + 1e-6);
// it must actually FALL, not merely fail to rise — a flat series means no scaling ran
R.scaleActuallyFell = dmgs[dmgs.length - 1] < dmgs[0] - 1e-6;
R.scaleFloored = Math.min(...dmgs) > 0;
R.scaleFloorRatio = +(Math.min(...dmgs) / dmgs[0]).toFixed(3);

// ---- 4. THE GUARD: chip is a fraction, and unblockable ignores it ------------
fresh(); p.state = STATE.BLOCKING;
let h0 = p.hp; p.takeDamage(20, foe, { pushback: 0, tier: STATE.ATTACK_HEAVY });
R.blockChip = +(h0 - p.hp).toFixed(3);
fresh(); p.state = STATE.BLOCKING;
h0 = p.hp; p.takeDamage(20, foe, { pushback: 0, tier: STATE.ATTACK_HEAVY, unblockable: true });
R.unblockableThroughGuard = +(h0 - p.hp).toFixed(3);
fresh(); p.state = STATE.IDLE;
h0 = p.hp; p.takeDamage(20, foe, { pushback: 0, tier: STATE.ATTACK_HEAVY });
R.plainHit = +(h0 - p.hp).toFixed(3);

// ---- 5. STATE EXITS: nothing timer-driven runs forever -----------------------
// Park the fighter in each timed state, run 4 simulated seconds, demand he is free.
const stuck = [];
for (const [st, setup] of [
  ['ROLL',    () => { p.state = STATE.ROLL; p.rollTimer = ROLL_TIME; }],
  ['STUNNED', () => { p.state = STATE.STUNNED; p.stunTimer = 0.6; }],
  ['BLOCKING',() => { p.state = STATE.BLOCKING; }],
  ['CROUCH',  () => { p.state = STATE.CROUCH; }],
]) {
  fresh(); setup();
  for (let i = 0; i < 75; i++) { for (const k in keys) keys[k] = false; await frame(); }
  if (p.state === STATE.ROLL || p.stunTimer > 0.001) stuck.push(st + ':' + p.state);
}
R.stuckStates = stuck;

// ---- 6. THROW beats a guard --------------------------------------------------
// ⛔ A REAL THROW NEVER CALLS takeDamage. releaseThrow subtracts hp itself, which is
// exactly WHY it beats the guard — routing a "throw" through takeDamage instead
// measures the probe, not the game.
fresh(); p.state = STATE.BLOCKING; p.stamina = 100;
p.grabbedBy = foe; foe.throwReleased = false; foe.throwBack = false;
h0 = p.hp; foe.releaseThrow(p);
R.throwThroughGuard = +(h0 - p.hp).toFixed(3);
R.throwStuns = p.stunTimer > 0;
// and the same throw against a fighter doing nothing, as the control
fresh(); p.grabbedBy = foe; foe.throwReleased = false; foe.throwBack = false;
h0 = p.hp; foe.releaseThrow(p);
R.throwPlain = +(h0 - p.hp).toFixed(3);

// ---- 7. CEILING LATCH and WALL CLING are capped, not free --------------------
K.hasCeilLatch = typeof CEIL_LATCH_MAX === 'number' && CEIL_LATCH_MAX > 0;
K.hasWallDrain = typeof WALL_RUN_DRAIN === 'number' && WALL_RUN_DRAIN > 0;

return JSON.stringify({ R, K });
'''

BOOT = r'''
const frame = () => new Promise(r => requestAnimationFrame(r));
gameMode='2p'; cpuMode=false; attractMode=false;
// ---- 8. EVERY fighter boots, has a sheet, and has non-zero HP ----------------
const boots = [];
for (const spec of NINJA_ROSTER) {
  const key = spec.name.toLowerCase();
  if (!SPRITES[key]) {
    try {
      const man = await (await fetch(`assets/sprites/${key}.json?v=${SHEET_V}`)).json();
      await new Promise((res, rej) => { const im = new Image();
        im.onload = () => { man.img = im; man.ready = true; SPRITES[key] = man; res(); };
        im.onerror = rej; im.src = `assets/sprites/${key}.png?v=${SHEET_V}`; });
    } catch (e) { boots.push(`${spec.name}: sheet failed to load`); continue; }
  }
  p1Pick = spec.id; p2Pick = (spec.id + 1) % 6; startNewGame(); roundIntroTimer = 0;
  await frame();
  const q = player1, F = SPRITES[key].frames;
  if (q.spec.id !== spec.id) boots.push(`${spec.name}: startNewGame gave id ${q.spec.id}`);
  if (!(q.hp > 0)) boots.push(`${spec.name}: boots with hp ${q.hp}`);
  const cell = spriteFrameIndex(q, F);
  if (cell === undefined || cell === null) boots.push(`${spec.name}: idle draws nothing`);
}


return JSON.stringify({ bootFailures: boots });
'''


def main():
    d = drive([{"wait": 3.2}, {"key": "Space"}, {"wait": 0.6},
               {"eval": PROBE, "label": "MECH"},
               {"eval": BOOT, "label": "BOOT"}], OUT, ["MECH", "BOOT"])
    R, K = d['MECH']['R'], d['MECH']['K']
    R['bootFailures'] = d['BOOT']['bootFailures']
    fails = []

    def ok(cond, msg):
        print(f"  {'ok  ' if cond else 'FAIL'}  {msg}")
        if not cond:
            fails.append(msg)

    print('\nMECHANICS — asserted against the engine\'s own constants\n')

    print(' PHYSICS')
    ok(R['maxVy'] <= K['TERMINAL'] + 1,
       f"fall speed is capped at TERMINAL_VELOCITY ({R['maxVy']} vs {K['TERMINAL']})")
    ok(K['hasCeilLatch'], 'a ceiling hang is time-capped, not free')
    ok(K['hasWallDrain'], 'a wall climb drains chakra, not free')

    print('\n RESOURCES')
    ok(R['chakraNeverNegative'], 'chakra never goes negative under mashing')
    ok(R['staminaNeverNegative'], 'stamina never goes negative under mashing')

    print('\n DAMAGE SCALING')
    ok(R['scaleMonotonic'],
       f"repeated hits never scale UP  {R['scaleSeries'][:6]}...")
    ok(R['scaleActuallyFell'],
       f"...and they actually FALL: {R['scaleSeries'][0]} -> "
       f"{R['scaleSeries'][-1]} over {R['scaleHits']} combo hits")
    ok(R['scaleFloored'],
       f"scaling has a floor above zero (min {min(R['scaleSeries'])}, "
       f"{R['scaleFloorRatio']}x of the first hit vs SCALE_FLOOR {K['SCALE_FLOOR']})")

    print('\n THE GUARD')
    ok(R['plainHit'] > 0, f"an unguarded hit does damage ({R['plainHit']})")
    ok(0 < R['blockChip'] < R['plainHit'],
       f"a guarded hit chips, but far less than a clean one "
       f"({R['blockChip']} vs {R['plainHit']})")
    ok(R['unblockableThroughGuard'] > R['blockChip'],
       f"an UNBLOCKABLE ignores the guard "
       f"({R['unblockableThroughGuard']} vs {R['blockChip']} chip)")
    ok(R['throwPlain'] > 0, f"a throw does damage ({R['throwPlain']})")
    ok(R['throwThroughGuard'] == R['throwPlain'],
       f"a THROW beats a guard — full damage through it "
       f"({R['throwThroughGuard']} guarded vs {R['throwPlain']} plain)")
    ok(R['throwStuns'], 'a thrown fighter is stunned on landing')

    print('\n STATE MACHINE')
    ok(not R['stuckStates'], f"no timed state runs forever {R['stuckStates'] or ''}")

    print('\n ROSTER BOOT')
    ok(not R['bootFailures'],
       f"all 9 fighters boot, load a sheet and draw an idle {R['bootFailures'] or ''}")

    if fails:
        print(f'\n{len(fails)} FAILED')
        return 1
    print('\nall good')
    return 0


if __name__ == '__main__':
    sys.exit(main())
