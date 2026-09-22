#!/usr/bin/env python3
"""CHAMPION MODE (Exile) — the smallest thing that fails if the mode breaks.

  python3 tools/serve.py &          # 9100, the only server
  python3 tools/check_champion.py

Drives the REAL page through tools/watch_game.py (headless Chrome, real rAF), because
every one of these can be true in the source and false in the game. Each assert is a way
the mode goes silently dead rather than visibly broken:

  * the key is bound but never reaches Exile      -> nothing happens, forever
  * the gauge never fills                         -> the mode is unreachable
  * the key fires below full                      -> it is a free button, not a cost
  * firing does not spend                         -> infinite uptime
  * frenzyTimer is set but the fragility stays on -> the mode does nothing she can feel

⛔ THE FRAGILITY IS MEASURED AS HP ACTUALLY LOST, not read off the flag. `frenzyTimer > 0`
proves the timer is running; it proves nothing about whether the damage multiplier ever
looked at it. Two identical hits on two fresh Exiles — one champion, one not — and the
ratio has to come out at the advertised 1.25x.

Exile is BENCHED on this branch, so her sheet is never preloaded and her card is hidden.
Neither is an engine gate: the check loads the sheet the same way the page would and
picks her by id, which is also the only way to test a benched fighter at all.
"""
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
OUT = REPO / 'media/audit/champion'

PROBE = r'''
const frame = () => new Promise(res => requestAnimationFrame(res));
if (!SPRITES['exile']) {
  const man = await (await fetch(`assets/sprites/exile.json?v=${SHEET_V}`)).json();
  await new Promise((res, rej) => {
    const img = new Image();
    img.onload = () => { man.img = img; man.ready = true; SPRITES['exile'] = man; res(); };
    img.onerror = rej; img.src = `assets/sprites/exile.png?v=${SHEET_V}`;
  });
}
gameMode = '2p'; cpuMode = false; attractMode = false;
p1Pick = 8; p2Pick = 0; stagePick = 'bamboo'; startNewGame(); roundIntroTimer = 0;
await frame(); await frame();
const p = player1, foe = player2;
const out = { name: p.spec.name, id: p.spec.id };
p.champion = 0; p.frenzyTimer = 0;

// 1. combat fills the gauge
p.hp = p.maxHp; p.invulnTimer = 0; p.stunTimer = 0; p.blockTimer = 0;
p.takeDamage(10, foe, {});
out.gaugeFromTaken = p.champion;

// 2. the key REFUSES below full, and spends nothing
p.stunTimer = 0; p.state = STATE.IDLE; p.isGrounded = true; p.vanishTimer = 0;
const before = p.champion;
p.modeKey();
out.refusedBelowFull = p.frenzyTimer <= 0 && p.champion === before;
out.stanceLeak = p.chudan === true;          // the shared key must not hand her chudan

// 3. at full it fires, and it SPENDS
p.champion = CHAMPION_MAX;
p.stunTimer = 0; p.state = STATE.IDLE; p.isGrounded = true;
p.modeKey();
out.firedAtFull = p.frenzyTimer > 0;
out.leftInGauge = p.champion;

// 4. the fragility is really off — HP LOST, on two fresh bodies, same raw damage
const hpLost = (championOn) => {
  const q = new Player(1, 150, GROUND_Y - 48, NINJA_ROSTER[8], true);
  q.opponent = foe; q.hp = q.maxHp; q.comboHits = 0;
  q.invulnTimer = 0; q.stunTimer = 0; q.blockTimer = 0;
  q.frenzyTimer = championOn ? 5 : 0;
  q.takeDamage(20, foe, {});
  return q.maxHp - q.hp;
};
out.hpLostNormal = hpLost(false);
out.hpLostChampion = hpLost(true);

// 5. THE REAL KEY PATH, not just the method. pressCombat drops everything unless the
//    match is actually live (matchActive, unpaused, intro over, no hitstop), so the
//    probe has to stand the match up before the press means anything.
p.frenzyTimer = 0; p.champion = CHAMPION_MAX;
p.stunTimer = 0; p.state = STATE.IDLE; p.isGrounded = true;
matchActive = true; paused = false; roundIntroTimer = 0; hitstopRemaining = 0;
window.dispatchEvent(new KeyboardEvent('keydown', { code: 'KeyV', bubbles: true }));
out.firedFromKeyV = p.frenzyTimer > 0;

// 6. REGRESSION — the mode key is shared, so the Executioner's stance must still
//    toggle on the same press. The refactor moved his grounded/stun guard ahead of
//    the sheet check; if it ever swallows him, chudan is gone and nothing says so.
p1Pick = 0; p2Pick = 1; startNewGame(); roundIntroTimer = 0;
await frame(); await frame();
const x = player1;
x.stunTimer = 0; x.state = STATE.IDLE; x.isGrounded = true;
x.modeKey(); out.execChudanOn = x.chudan === true;
x.state = STATE.IDLE;
x.modeKey(); out.execChudanOff = x.chudan === false;
return JSON.stringify(out);
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    script = OUT / 'probe.json'
    script.write_text(json.dumps([
        {"wait": 1.2}, {"key": "Space"}, {"wait": 0.5},
        {"eval": PROBE, "label": "CHAMPION"},
    ], indent=1))
    subprocess.run([sys.executable, str(REPO / 'tools/watch_game.py'),
                    '--script', str(script), '--out', str(OUT / 'run')],
                   check=True, capture_output=True, text=True)
    log = (OUT / 'run/log.txt').read_text()
    i = log.index('CHAMPION: ')
    raw = json.JSONDecoder().raw_decode(log[i + len('CHAMPION: '):])[0]
    r = json.loads(raw) if isinstance(raw, str) else raw

    fails = []

    def ok(cond, msg):
        print(f"  {'ok  ' if cond else 'FAIL'}  {msg}")
        if not cond:
            fails.append(msg)

    print('\nCHAMPION MODE — live checks\n')
    ok(r['id'] == 8, f"player1 is Exile (got {r['name']})")
    ok(r['gaugeFromTaken'] > 0, f"combat fills the gauge ({r['gaugeFromTaken']:.1f})")
    ok(r['refusedBelowFull'], 'the mode key refuses below a full gauge and spends nothing')
    ok(not r['stanceLeak'], 'the shared mode key does not put Exile in chudan')
    ok(r['firedAtFull'], 'the mode key fires at a full gauge')
    ok(r['leftInGauge'] == 0, f"firing SPENDS the gauge (left {r['leftInGauge']})")
    ok(r['firedFromKeyV'], 'a real V keydown reaches her, not just the method')
    ok(r['hpLostChampion'] < r['hpLostNormal'],
       f"fragility is OFF in champion: {r['hpLostNormal']:.2f} HP normal "
       f"vs {r['hpLostChampion']:.2f} champion")
    ratio = r['hpLostNormal'] / r['hpLostChampion'] if r['hpLostChampion'] else 0
    ok(abs(ratio - 1.25) < 0.02, f"...and it is exactly the advertised 1.25x (measured {ratio:.3f}x)")
    ok(r['execChudanOn'] and r['execChudanOff'],
       'REGRESSION: the shared key still toggles the Executioner into and out of chudan')

    if fails:
        print(f'\n{len(fails)} FAILED')
        return 1
    print('\nall good')
    return 0


if __name__ == '__main__':
    sys.exit(main())
