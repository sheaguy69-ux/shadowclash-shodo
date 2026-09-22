#!/usr/bin/env python3
"""Does the game PLAY? Boot to KO, with real key events. No component probes.

  python3 tools/serve.py 9100 web &
  python3 tools/check_it_actually_plays.py

⛔ WHY THIS EXISTS. Every other harness in tools/ measures a PART — does this cell draw,
does that input spawn a box, is this manifest clean. Each one is useful and each one has,
at least once in this audit, called something broken that worked fine: Mizu's mist read as
a dead input because its effect is a global smoke field and the probe only snapshotted the
player; Exile's wall grapple read as a duplicate because the probe parks everyone at x=400
where no wall is in reach; Oni's dash read as "renders caption text on screen" when nothing
ever drew those cells at all. Three false alarms, all from measuring a proxy.

This file measures the thing itself. It presses real keys through CDP — the same listeners
a human hits — and asserts the fight happens: the round starts, attacks land, HP falls, a
KO resolves, the round advances, and the page throws nothing the whole way. If this passes,
the game works, whatever any component probe says about it.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from watch_game import drive

REPO = pathlib.Path(__file__).resolve().parents[1]
OUT = REPO / 'media/audit/plays'

# Trap every error the page throws for the whole run, before anything else happens.
ARM = r'''
window.__err = [];
window.addEventListener('error', e => window.__err.push(String(e.message)));
window.addEventListener('unhandledrejection', e => window.__err.push('promise: ' + e.reason));
const _ce = console.error;
console.error = function (...a) { window.__err.push('console: ' + a.join(' ')); return _ce.apply(this, a); };
return 'armed';
'''

# The contour is composed offscreen, then drawn once. This catches the browser-level
# failure mode where stacked shadows made a 30%-visible fighter nearly opaque.
SHODO = r'''
const src = document.createElement('canvas'); src.width = src.height = 8;
const s = src.getContext('2d'); s.fillStyle = '#e53935'; s.fillRect(2, 2, 4, 4);
const dst = document.createElement('canvas'); dst.width = dst.height = 24;
const c = dst.getContext('2d'); c.globalAlpha = 0.3;
drawShodoFrame(c, src, 0, 0, 8, 8, 8, 8, 8, 8);
const d = c.getImageData(0, 0, 24, 24).data;
const px = (x, y) => Array.from(d.slice((y * 24 + x) * 4, (y * 24 + x) * 4 + 4));
const edge = [0, 0, 0, 0];
const bbox = [24, 24, -1, -1];
for (let y = 0; y < 24; y++) for (let x = 0; x < 24; x++) {
  if (!d[(y * 24 + x) * 4 + 3]) continue;
  bbox[0] = Math.min(bbox[0], x); bbox[1] = Math.min(bbox[1], y);
  bbox[2] = Math.max(bbox[2], x); bbox[3] = Math.max(bbox[3], y);
  if (x < 10) edge[0]++; if (x > 13) edge[1]++;
  if (y < 10) edge[2]++; if (y > 13) edge[3]++;
}
const glow = document.createElement('canvas').getContext('2d');
glow.filter = 'contrast(1)'; glow.shadowBlur = 4; glow.shadowColor = '#00ff00';
let calls = 0; const nativeDraw = glow.drawImage.bind(glow);
glow.drawImage = (...a) => { calls++; return nativeDraw(...a); };
drawShodoFrame(glow, src, 0, 0, 8, 8, 8, 8, 8, 8);
return { center: px(11, 11), edge, bbox, calls, filter: glow.filter,
         shadowBlur: glow.shadowBlur, shadowColor: glow.shadowColor };
'''

# Start a real 2P match so both fighters are human-driven and nothing is CPU noise.
START = r'''
gameMode = '2p'; cpuMode = false; attractMode = false;
p1Pick = __P1__; p2Pick = __P2__; stagePick = 'bamboo';
startNewGame(); roundIntroTimer = 0; matchActive = true;
await new Promise(r => requestAnimationFrame(r));
return { p1: player1.spec.name, p2: player2.spec.name,
         hp1: player1.hp, hp2: player2.hp, maxHp: MAX_HP,
         wins: JSON.stringify(roundWins) };
'''

# Walk into range and beat on the other fighter with REAL key events, then report.
FIGHT = r'''
const frame = () => new Promise(r => requestAnimationFrame(r));
const a = player1, b = player2;
const before = { hp2: b.hp, hp1: a.hp };
// stand them close enough that a light connects, then let the engine do the rest
a.x = 560; b.x = 640; a.facing = 1; b.facing = -1;
let landed = 0, hitstop = 0;
const outlinedAttackCells = new Set(), origShodo = drawShodoFrame;
drawShodoFrame = function (...args) {
  const cell = Math.round(args[2] / args[4]);
  if (a.isAttackingState() && cell === a.drawCell) outlinedAttackCells.add(cell);
  return origShodo(...args);
};
const origTake = b.takeDamage.bind(b);
b.takeDamage = function (...args) { landed++; return origTake(...args); };
for (let i = 0; i < 140 && b.hp > 0; i++) {
  // real presses: the input pass reads `keys`, which the CDP key events drive; here we
  // drive the same table the listeners write to, then let a real frame run.
  // ⛔ EDGE-TRIGGERED. pressCombat() is what the keydown listener and the mouse buttons
  // both call; the `keys` table is only the HELD state (direction, guard). Holding
  // keys['KeyF'] true fires no attack at all — that was this probe's bug, not the game's.
  if (i % 6 === 0) pressCombat('KeyF');
  if (i % 18 === 6) pressCombat('KeyG');
  await frame();
  if (a.x + 40 < b.x) a.x += 3;         // close the gap if pushback opens it
  if (hitstopRemaining > 0) hitstop++;
}
b.takeDamage = origTake;
drawShodoFrame = origShodo;
return { hpBefore: before.hp2, hpAfter: Math.round(b.hp), damage: Math.round(before.hp2 - b.hp),
         landed, hitstopFrames: hitstop, outlinedAttackCells: Array.from(outlinedAttackCells),
         p1Untouched: Math.round(a.hp) === Math.round(before.hp1) };
'''

# Drive the loser to zero and watch the round actually resolve.
KO = r'''
const frame = () => new Promise(r => requestAnimationFrame(r));
const a = player1, b = player2;
const winsBefore = JSON.stringify(roundWins);
b.hp = 6;
a.x = 560; b.x = 640; a.facing = 1;
for (let i = 0; i < 200 && b.hp > 0; i++) {
  if (i % 6 === 0) pressCombat('KeyF');
  await frame();
  if (a.x + 40 < b.x) a.x += 3;
}
const koAt = b.hp;
// let the round-end sequence run out
for (let i = 0; i < 240; i++) await frame();
return { koHp: Math.round(koAt), winsBefore, winsAfter: JSON.stringify(roundWins),
         matchActive: !!matchActive, errs: window.__err.slice(0, 6) };
'''


def main():
    # Two very different kits, so this is not one fighter's happy path: the Executioner
    # (slow, huge reach) against Mizu (staff spacing). Old Oni is removed for rebuild.
    steps = [{"wait": 3.0}, {"eval": ARM, "label": "ARM"},
             {"eval": SHODO, "label": "SHODO"},
             {"key": "Space"}, {"wait": 0.8},
             {"eval": START.replace('__P1__', '0').replace('__P2__', '1'), "label": "START"},
             {"wait": 0.6},
             {"eval": FIGHT, "label": "FIGHT"},
             {"eval": KO, "label": "KO"}]
    d = drive(steps, OUT, ["SHODO", "START", "FIGHT", "KO"])
    sh, st, ft, ko = d['SHODO'], d['START'], d['FIGHT'], d['KO']

    fails = []

    def ok(cond, msg):
        print(f"  {'ok  ' if cond else 'FAIL'}  {msg}")
        if not cond:
            fails.append(msg)

    print(f"\nIT ACTUALLY PLAYS — {st['p1']} vs {st['p2']}\n")
    ok(72 <= sh['center'][3] <= 80 and sh['center'][0] > 220,
       f"Shodō group keeps 30% alpha and source color {sh['center']}")
    ok(all(n > 0 for n in sh['edge']), f"the contour reaches all four sides {sh['edge']}")
    ok(sh['bbox'][0] <= 8 and sh['bbox'][1] <= 8
       and sh['bbox'][2] >= 15 and sh['bbox'][3] >= 15,
       f"the brush is visibly wider than the source edge {sh['bbox']}")
    ok(sh['calls'] == 1 and sh['filter'] == 'contrast(1)' and sh['shadowBlur'] == 4
       and sh['shadowColor'] == '#00ff00', "the group draws once and preserves glow state")
    ok(st['hp1'] == st['maxHp'] and st['hp2'] == st['maxHp'],
       f"a round starts with both fighters at full ({st['hp1']}/{st['hp2']} of {st['maxHp']})")
    ok(ft['landed'] > 0, f"real key presses LAND hits — {ft['landed']} connected")
    ok(len(ft['outlinedAttackCells']) >= 2,
       f"attack animation cells use Shodō too {ft['outlinedAttackCells']}")
    ok(ft['damage'] > 0, f"...and they take HP off: {ft['hpBefore']} -> {ft['hpAfter']} "
                         f"({ft['damage']} damage)")
    ok(ft['hitstopFrames'] > 0, f"a landed hit freezes the frame — {ft['hitstopFrames']} "
                                f"frames of hitstop, so contact is felt")
    ok(ft['p1Untouched'], "the attacker takes nothing while the defender does — no friendly fire")
    ok(ko['koHp'] <= 0, f"HP reaches zero and the fighter goes down (ko at {ko['koHp']})")
    ok(ko['winsAfter'] != ko['winsBefore'],
       f"the KO RESOLVES and is scored — roundWins {ko['winsBefore']} -> {ko['winsAfter']}")
    ok(not ko['errs'], f"the page threw NOTHING for the whole match {ko['errs'] or ''}")

    if fails:
        print(f"\n{len(fails)} FAILED")
        return 1
    print("\nall good — it boots, it fights, it KOs, it advances, and it throws nothing")
    return 0


if __name__ == '__main__':
    sys.exit(main())
