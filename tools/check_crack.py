#!/usr/bin/env python3
"""THE CRACK (Mokurai's second form) — does the mode actually work, and does it DRAW.

  python3 tools/serve.py &        # 9101, the owner's tree
  python3 tools/check_crack.py

The form was designed and packed on `fix/benched-trio-audit` and never merged. This file
is the standing proof that the merge onto public-battle kept it working, because a merged
mode can fail in two independent ways and only one of them is visible in the source:

  * the MECHANIC lands but the art does not      -> he cracks and still looks calm
  * the ART is packed but the trigger is dead    -> 114 cells nothing can reach

So every check below asserts the drawn CELL INDEX, not just a flag. Crack art lives at
cells 94-207; his base art is 0-93. A cell < 94 while `cracked` is true means the mode is
running with the wrong pictures, which is exactly what a bad merge produces.

Mokurai is benched on this branch, so his sheet is never preloaded — the probe loads it
the same way the page would. Benching is a roster-UI gate, not an engine gate.
"""
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
OUT = REPO / 'media/audit/crack'

PROBE = r'''
const frame = () => new Promise(r => requestAnimationFrame(r));
if (!SPRITES['mokurai']) {
  const man = await (await fetch(`assets/sprites/mokurai.json?v=${SHEET_V}`)).json();
  await new Promise((res, rej) => { const i = new Image();
    i.onload = () => { man.img = i; man.ready = true; SPRITES['mokurai'] = man; res(); };
    i.onerror = rej; i.src = `assets/sprites/mokurai.png?v=${SHEET_V}`; });
}
gameMode = '2p'; cpuMode = false; attractMode = false;
p1Pick = 6; p2Pick = 0; stagePick = 'bamboo'; startNewGame(); roundIntroTimer = 0;
matchActive = true;
await frame(); await frame();
const p = player1, foe = player2, F = SPRITES['mokurai'].frames;
const out = { name: p.spec.name, cols: SPRITES['mokurai'].cols };

const reset = () => { p.cracked = false; p.crackTimer = 0; p.crackIntro = 0;
  p.crackSpent = 0; p.feintFlash = 0; p.enlightenUsed = false; p.enlightenTimer = 0;
  p.meditateTimer = 0; p.stunTimer = 0; p.recoveryTimer = 0; p.isGrounded = true;
  p.attackAnim = null; p.state = STATE.IDLE; };

// 1. FULL KARMA -> THE CRACK.
// ⛔ THIS IS NOT THE REAL CHANNEL. It INLINES a copy of the engine's meditation branch
// and calls startCrack directly, so sections 1-4 prove the MODE — its art rows, its
// damage tax, its kneel — and never that a press reaches it. That is deliberate and it
// stays: those are the parts a redesign has to keep working. Section 5 below drives the
// REAL Down+Guard channel, with real held keys, and is where the earn loop is proven.
reset(); p.karma = KARMA_MAX;
for (let i = 0; i < 40; i++) { p.meditateTimer += 0.06;
  if (p.meditateTimer >= 2.0) { p.meditateTimer = 0;
    if (p.spec.id === 6 && p.karma >= KARMA_MAX) { p.karma = 0; p.enlightenUsed = true; p.startCrack(false); }
    else { p.enlightenUsed = true; p.enlightenTimer = 5; } break; } }
out.crackedOnFull = p.cracked === true;
out.karmaSpent = p.karma;
out.crackTimer = p.crackTimer;

// 2. the transformation and the in-mode form states must draw CRACK cells (>= 94)
p.crackIntro = 0.4; p.state = STATE.IDLE;
out.introCell = spriteFrameIndex(p, F);
p.crackIntro = 0;
p.state = STATE.IDLE; out.idleCell = spriteFrameIndex(p, F);
p.state = STATE.RUN;  p.vx = 200; out.runCell = spriteFrameIndex(p, F);
p.state = STATE.BLOCKING; p.vx = 0; out.blockCell = spriteFrameIndex(p, F);
p.state = STATE.STUNNED; out.hurtCell = spriteFrameIndex(p, F);
p.state = STATE.IDLE;

// 3. a cracked ATTACK draws its own row
p.laughAnim = true; p.state = STATE.ATTACK_SPECIAL;
p.attackAnim = { start: animClock * 1000, dur: 400 };
out.laughCell = spriteFrameIndex(p, F);
p.laughAnim = false; p.attackAnim = null; p.state = STATE.IDLE;

// 4. the madness has no guard: +20% taken while cracked
// 4. THE ILLUSION. Owner, Sep 23 2026: the screen must show him crumbling while he is in
//    fact winning. Four numbers, and every one of them is a way the trick dies quietly:
//      * he really takes MORE      -> the mode is still the old all-cost version
//      * he really deals LESS      -> "make it actually stronger" never landed
//      * the HUD tells the truth   -> there is no trick, just a buff
//      * the lie never reconciles  -> the bars stay wrong forever and read as a bug
const fresh = (on) => { const q = new Player(1, 150, GROUND_Y - 48, NINJA_ROSTER[6], true);
  q.opponent = foe; q.hp = q.maxHp; q.comboHits = 0; q.invulnTimer = 0; q.stunTimer = 0;
  q.blockTimer = 0; q.hpLie = 0; q.cracked = on; q.crackTimer = on ? 5 : 0; return q; };
// (a) what he REALLY takes
const taken = (on) => { const q = fresh(on); foe.cracked = false;
  q.takeDamage(20, foe, {}); return { real: q.maxHp - q.hp, shown: q.maxHp - hudHp(q) }; };
const tN = taken(false), tC = taken(true);
out.takenNormal = tN.real; out.takenCracked = tC.real; out.takenShownCracked = tC.shown;
// (b) what he REALLY deals — a fresh VICTIM hit by a cracked Mokurai
const dealt = (on) => { const v = new Player(2, 400, GROUND_Y - 48, NINJA_ROSTER[0], false);
  const m = fresh(on); v.opponent = m; m.opponent = v;
  v.hp = v.maxHp; v.comboHits = 0; v.invulnTimer = 0; v.stunTimer = 0; v.blockTimer = 0; v.hpLie = 0;
  v.takeDamage(20, m, {}); return { real: v.maxHp - v.hp, shown: v.maxHp - hudHp(v) }; };
const dN = dealt(false), dC = dealt(true);
out.dealtNormal = dN.real; out.dealtCracked = dC.real; out.dealtShownCracked = dC.shown;
// (c) THE REVEAL — once the madness ends the bars must walk back to the truth
const rv = fresh(true); foe.cracked = false;
rv.takeDamage(20, foe, {});
const lieAt = rv.hpLie;
rv.cracked = false; rv.crackTimer = 0;
for (let i = 0; i < 120; i++) rv.update(1 / 60, foe);   // 2s — CRACK_REVEAL is 0.7
out.lieDuring = lieAt; out.lieAfter = rv.hpLie;
out.revealedTruth = Math.abs(hudHp(rv) - rv.hp) < 0.5;
out.hpNormal = tN.real; out.hpCracked = tC.real;

// 5. the SPENT KNEEL draws its own art, not the base crouch
reset(); p.cracked = false; p.crackSpent = CRACK_SPENT; p.state = STATE.IDLE;
out.spentCell = spriteFrameIndex(p, F);

// 6. SHORT karma must still give the OLD calm Enlightenment, unchanged
reset(); p.karma = 3;
for (let i = 0; i < 40; i++) { p.meditateTimer += 0.06;
  if (p.meditateTimer >= 2.0) { p.meditateTimer = 0;
    if (p.spec.id === 6 && p.karma >= KARMA_MAX) { p.karma = 0; p.enlightenUsed = true; p.startCrack(false); }
    else { p.enlightenUsed = true; p.enlightenTimer = 5; } break; } }
out.calmOnShort = (p.cracked === false && p.enlightenTimer > 0);
// 5. THE EARN LOOP, THROUGH THE REAL CHANNEL. Owner, Sep 23 2026: earn = unlock once,
//    then charge every match. Mokurai's charge layer is KARMA, which already existed, so
//    he comes off the pause with Exile.
//
//    ⛔ HELD KEYS MUST GO IN physKeys. The engine scrubs P1's keys every frame unless the
//    key is physically down (the attract-mode residue guard), so setting keys[] alone
//    gives a channel that never accumulates — and a probe that reports "nothing happened",
//    which reads exactly like a successful block. That false green nearly shipped once.
const channel = () => {
  reset(); p.enlightenUsed = false; p.enlightenTimer = 0; p.karma = KARMA_MAX;
  keys['p1_down'] = keys['KeyS'] = keys['KeyC'] = true;
  physKeys.add('KeyS'); physKeys.add('KeyC');
  p.meditateTimer = 1.98;
  p.update(0.05, foe);
};
matchActive = true; paused = false; roundIntroTimer = 0; hitstopRemaining = 0;

//  a. THE TRIAL: a full karma bar, carried through live frames, earns the mode. Runs off
//     updateStance -> tickSecondUnlock, so it also proves the hook reaches the frame.
save.unlocked = {}; save.charged = {}; p.secondWasFull = false;
reset(); p.karma = KARMA_MAX;
out.lockedBefore = save.unlocked['Mokurai'] !== true;
await frame(); await frame();
out.unlockedByTrial = save.unlocked['Mokurai'] === true;
out.trialCounted = save.charged['Mokurai'];

//  b. EARNED: the REAL channel now cracks him.
channel();
out.channelCracked = p.cracked === true;
out.channelSpent = p.karma;
out.channelWentGold = p.enlightenTimer > 0;

//  c. LOCKED: the same channel goes GOLD instead — the ENLIGHTENMENT branch that was
//     always the other half of that `if`.
//     The latch is what holds him locked: tickSecondUnlock only fires on a RISING edge, so
//     leaving secondWasFull set keeps a full bar from re-earning the mode mid-test. That is
//     the honest way to observe a locked monk holding a full gauge — at one fill per trial
//     the two states otherwise never coexist for longer than a frame boundary.
save.unlocked = {}; save.charged = {}; p.secondWasFull = true;
channel();
out.lockedCracked = p.cracked === true;
out.lockedGoldTimer = p.enlightenTimer;

keys['p1_down'] = keys['KeyS'] = keys['KeyC'] = false;
physKeys.delete('KeyS'); physKeys.delete('KeyC');

return JSON.stringify(out);
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    script = OUT / 'probe.json'
    script.write_text(json.dumps([
        {"wait": 3.2}, {"key": "Space"}, {"wait": 0.6},
        {"eval": PROBE, "label": "CRACK"},
    ], indent=1))
    subprocess.run([sys.executable, str(REPO / 'tools/watch_game.py'),
                    '--script', str(script), '--out', str(OUT / 'run')],
                   check=True, capture_output=True, text=True)
    log = (OUT / 'run/log.txt').read_text()
    i = log.index('CRACK: ')
    raw = json.JSONDecoder().raw_decode(log[i + len('CRACK: '):])[0]
    r = json.loads(raw) if isinstance(raw, str) else raw

    fails = []

    def ok(cond, msg):
        print(f"  {'ok  ' if cond else 'FAIL'}  {msg}")
        if not cond:
            fails.append(msg)

    def crack_cell(v):
        return isinstance(v, int) and v >= 94

    print('\nTHE CRACK — live checks\n')
    ok(r['name'] == 'Mokurai', f"fighter is Mokurai (got {r['name']})")
    # >= not ==: the sheet is append-only and keeps growing past the crack block
    # (SHEET_V 365 put his new run at 208-211). What must hold is that the crack
    # art is still all there, which is cells 94-207.
    ok(r['cols'] >= 208, f"sheet carries the crack art: {r['cols']} cols (94 base + 114 crack + {r['cols'] - 208} since)")
    ok(r['crackedOnFull'], 'a FULL karma gauge cracks him instead of going gold')
    ok(r['karmaSpent'] == 0, f"cracking spends the whole gauge (left {r['karmaSpent']})")
    ok(abs(r['crackTimer'] - 6) < 0.01, f"the mode runs {r['crackTimer']}s")
    ok(r['calmOnShort'], 'a SHORT gauge still gives the old calm Enlightenment')
    print()
    ok(crack_cell(r['introCell']), f"the transformation draws crack art (cell {r['introCell']})")
    ok(crack_cell(r['idleCell']),  f"in-mode idle is the HOLLOW IDLE (cell {r['idleCell']})")
    ok(crack_cell(r['runCell']),   f"in-mode run is the SCUTTLE (cell {r['runCell']})")
    ok(crack_cell(r['blockCell']), f"in-mode guard is the CRACKED GUARD (cell {r['blockCell']})")
    ok(crack_cell(r['hurtCell']),  f"in-mode hurt is the cracked flinch (cell {r['hurtCell']})")
    ok(crack_cell(r['laughCell']), f"LAUGHING BELL draws its own row (cell {r['laughCell']})")
    ok(crack_cell(r['spentCell']), f"the SPENT KNEEL draws its own art (cell {r['spentCell']})")
    print()
    print('\n  THE ILLUSION — the HUD lies, the fight does not\n')
    tr = r['takenCracked'] / r['takenNormal'] if r['takenNormal'] else 0
    ok(tr < 0.99, f"REAL: cracked TAKES LESS — {r['takenNormal']:.2f} normal "
                  f"vs {r['takenCracked']:.2f} cracked ({tr:.3f}x)")
    dr_ = r['dealtCracked'] / r['dealtNormal'] if r['dealtNormal'] else 0
    ok(dr_ > 1.01, f"REAL: cracked DEALS MORE — {r['dealtNormal']:.2f} normal "
                   f"vs {r['dealtCracked']:.2f} cracked ({dr_:.3f}x)")
    ok(r['takenShownCracked'] > r['takenCracked'],
       f"SHOWN: his own bar drops MORE than he really lost — "
       f"{r['takenShownCracked']:.2f} shown vs {r['takenCracked']:.2f} real")
    ok(r['dealtShownCracked'] < r['dealtCracked'],
       f"SHOWN: their bar drops LESS than they really lost — "
       f"{r['dealtShownCracked']:.2f} shown vs {r['dealtCracked']:.2f} real")
    ok(r['lieDuring'] > 0, f"the lie is actually banked while it runs ({r['lieDuring']:.2f} HP hidden)")
    ok(abs(r['lieAfter']) < 0.001, f"THE REVEAL: the lie clears once it ends (left {r['lieAfter']:.4f})")
    ok(r['revealedTruth'], '...and the bar then reads the real HP')


    print('\n  THE EARN LOOP\n')
    ok(r['lockedBefore'], 'he starts LOCKED — nothing in the save says otherwise')
    ok(r['unlockedByTrial'],
       'THE TRIAL: carrying a FULL karma bar through live frames EARNS the mode')
    ok(r['trialCounted'] == 1, f"...and it counted exactly one fill (got {r['trialCounted']})")
    ok(r['channelCracked'], 'EARNED: the real Down+Guard channel now CRACKS him')
    ok(r['channelSpent'] == 0, f"...and it still spends all 15 karma (left {r['channelSpent']})")
    ok(not r['channelWentGold'], '...and it is the madness, not the gold')
    ok(not r['lockedCracked'], 'LOCKED: the same channel does NOT crack him')
    ok(r['lockedGoldTimer'] > 0,
       f"...it falls through to ENLIGHTENMENT instead ({r['lockedGoldTimer']}s of gold)")

    if fails:
        print(f'\n{len(fails)} FAILED')
        return 1
    print('\nall good')
    return 0


if __name__ == '__main__':
    sys.exit(main())
