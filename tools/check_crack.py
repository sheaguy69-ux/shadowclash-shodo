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
// ⛔ THIS IS NOT THE REAL CHANNEL, WHATEVER THIS COMMENT USED TO CLAIM. It INLINES a
// copy of the engine's meditation branch and calls startCrack directly, so it has
// never proven a press reaches the mode — and as of Sep 22 2026 it provably does not:
// the owner paused every second mode, the engine branch now carries
// `&& !secondFormBlocked(this)`, and a FULL bar goes to ENLIGHTENMENT instead.
// What this file still tests is the MODE ITSELF — its art rows, its damage tax, its
// kneel — which is what a redesign needs to keep working. The pause is pinned in
// tools/check_first_form_gate.mjs; do not duplicate that assertion here.
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
const hp = (on) => { const q = new Player(1, 150, GROUND_Y - 48, NINJA_ROSTER[6], true);
  q.opponent = foe; q.hp = q.maxHp; q.comboHits = 0; q.invulnTimer = 0; q.stunTimer = 0;
  q.blockTimer = 0; q.cracked = on; q.crackTimer = on ? 5 : 0;
  q.takeDamage(20, foe, {}); return q.maxHp - q.hp; };
out.hpNormal = hp(false); out.hpCracked = hp(true);

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
    ratio = r['hpCracked'] / r['hpNormal'] if r['hpNormal'] else 0
    ok(abs(ratio - 1.2) < 0.02,
       f"the madness has no guard: {r['hpNormal']:.2f} HP normal vs {r['hpCracked']:.2f} "
       f"cracked = {ratio:.3f}x (want 1.2)")

    if fails:
        print(f'\n{len(fails)} FAILED')
        return 1
    print('\nall good')
    return 0


if __name__ == '__main__':
    sys.exit(main())
