#!/usr/bin/env python3
"""SAYA-KAMAE must not ARM IRON GUARD REPRISAL — the Executioner's double-dip.

  python3 tools/serve.py 9100 web &      # 9100, the only server
  python3 tools/check_saya_reprisal.py

Saya-Kamae (V+Down) is roster-wide: `modeKey` reads the direction BEFORE it branches on
fighter, and `toggleSaya` gates on the WEAPON, not the id — `WEAPON_MAT` has no entry for
id 0, so the Executioner falls through to 'steel' and can hold the reverse grip.

Iron Guard Reprisal gates the other way: `executeReprisal` is `spec.id !== 0 -> false`.

So the two overlap on exactly one fighter, and the auto-parry branch of `takeDamage`
stamped `blockedAt` alongside the real BLOCKING branch. That hands the Executioner a
Special-tier riposte off a defence that already won the exchange outright — no chip, no
shove, attacker stunned 0.32s and recoiled. The riposte is supposed to be the payment for
EATING a hit; a turned hit was never eaten.

The invariant is stated in the source at the Reprisal comment ("blockedAt is only ever
stamped in the BLOCKING branch of takeDamage") and enforced statically by
tools/check_moves.py, which counts the stamps. This file is the runtime half: it drives
the actual collision instead of reading the source, so a stamp that reappears behind a
different flag still fails.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from watch_game import drive

REPO = pathlib.Path(__file__).resolve().parents[1]
OUT = REPO / 'media/audit/saya-reprisal'

PROBE = r'''
const frame = () => new Promise(r => requestAnimationFrame(r));
gameMode = '2p'; cpuMode = false; attractMode = false;
// p1 = Executioner (id 0, the only fighter who owns the riposte).
// p2 = Kael (id 5): no WEAPON_MAT entry either, so he is 'steel' and the hit is
// blade-on-blade, which is what the auto-parry requires.
p1Pick = 0; p2Pick = 5; stagePick = 'bamboo'; startNewGame(); roundIntroTimer = 0;
matchActive = true;
await frame(); await frame();
const p = player1, foe = player2;
const out = { name: p.spec.name, foe: foe.spec.name, mat: weaponMat(p), foeMat: weaponMat(foe) };

// A guarded, clashing steel hit — the exact shape the Saya branch answers.
const STEEL_HIT = { pushback: 80, tier: STATE.ATTACK_HEAVY, canClash: true };

const guard = (gyakute) => {
  p.hp = 100; p.stamina = 100; p.chakra = 100;
  p.gyakute = gyakute; p.sayaParryCd = 0; p.chudan = false;
  p.blockedAt = -1e9; p.parryFlashTimer = 0; p.parriedAt = -9;
  p.stunTimer = 0; p.vanishTimer = 0; p.grabbedBy = null; p.throwTimer = 0;
  p.windedTimer = 0; p.kawarimiWindow = 0; p.isGrounded = true;
  p.state = STATE.BLOCKING;
};

// --- 1. the ordinary guard: eats chip, and SHOULD arm the riposte ------------
guard(false);
const hpBefore = p.hp;
p.takeDamage(10, foe, STEEL_HIT);
out.plainChip = +(hpBefore - p.hp).toFixed(3);
out.plainStamped = animClock - p.blockedAt < 0.001;
p.state = STATE.BLOCKING; p.stunTimer = 0;   // executeReprisal refuses while stunned
out.plainReprisal = p.executeReprisal();

// --- 2. the SAYA auto-parry: turns the hit, and must NOT arm the riposte -----
guard(true);
const hpBefore2 = p.hp;
p.takeDamage(10, foe, STEEL_HIT);
out.sayaFired = p.parryFlashTimer > 0;                  // the parry branch ran
out.sayaChip = +(hpBefore2 - p.hp).toFixed(3);          // a turned hit costs nothing
out.sayaFoeStun = +foe.stunTimer.toFixed(3);            // ...and the attacker eats it
out.sayaStamped = animClock - p.blockedAt < 0.001;      // <- the bug
p.state = STATE.BLOCKING; p.stunTimer = 0;
out.sayaReprisal = p.executeReprisal();                 // <- the payoff of the bug

return JSON.stringify(out);
'''


def main():
    r = drive([
        {"wait": 3.2}, {"key": "Space"}, {"wait": 0.6},
        {"eval": PROBE, "label": "SAYA"},
    ], OUT, "SAYA")

    fails = []

    def ok(cond, msg):
        print(f"  {'ok  ' if cond else 'FAIL'}  {msg}")
        if not cond:
            fails.append(msg)

    print('\nSAYA-KAMAE vs IRON GUARD REPRISAL — live checks\n')
    ok(r['name'] == 'Executioner', f"p1 is the Executioner (got {r['name']})")
    ok(r['mat'] == 'steel' and r['foeMat'] == 'steel',
       f"both hold steel, so the hit is blade-on-blade ({r['mat']} vs {r['foeMat']})")
    print()
    # The control. If this half ever fails, the riposte is unreachable and the
    # Saya result below proves nothing.
    ok(r['plainChip'] > 0, f"an ordinary guard still eats chip ({r['plainChip']} HP)")
    ok(r['plainStamped'], 'an ordinary guard stamps blockedAt')
    ok(r['plainReprisal'], 'an ordinary guard ARMS the riposte — this is the move working')
    print()
    ok(r['sayaFired'], 'the Saya auto-parry fires on a guarded steel hit')
    ok(r['sayaChip'] == 0, f"a turned hit costs the guard nothing ({r['sayaChip']} HP)")
    ok(r['sayaFoeStun'] > 0, f"...and the attacker eats the recoil ({r['sayaFoeStun']}s stun)")
    print()
    ok(not r['sayaStamped'], 'a turned hit does NOT stamp blockedAt')
    ok(not r['sayaReprisal'],
       'a turned hit does NOT arm Iron Guard Reprisal — the parry already won the exchange')

    if fails:
        print(f'\n{len(fails)} FAILED')
        return 1
    print('\nall good')
    return 0


if __name__ == '__main__':
    sys.exit(main())
