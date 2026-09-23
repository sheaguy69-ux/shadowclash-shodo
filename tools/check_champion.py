#!/usr/bin/env python3
"""CHAMPION MODE (Exile) — the smallest thing that fails if the mode breaks.

  python3 tools/serve.py &          # 9101, the owner's tree
  python3 tools/check_champion.py

Drives the REAL page through tools/watch_game.py (headless Chrome, real rAF), because
every one of these can be true in the source and false in the game. Each assert is a way
the mode goes silently dead rather than visibly broken:

  * the gauge never fills                         -> the mode is unreachable
  * the mode fires below full                     -> it is a free button, not a cost
  * firing does not spend                         -> infinite uptime
  * frenzyTimer is set but the fragility stays on -> the mode does nothing she can feel

⛔ THE KEY PATH IS PAUSED, NOT TESTED-AS-WORKING. Owner, Sep 22 2026: every second mode is
on hold pending an earn/unlock redesign. So the mode is driven through enterChampion() and
the V key is asserted to do NOTHING — same assertions, opposite polarity, which flip back
the day champion is unlocked. The source-level pin lives in tools/check_first_form_gate.mjs.

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
// ⛔ BY NAME, NEVER BY INDEX. This read `p1Pick = 8` and Exile moved to 7 the day Oni
// retired, so it picked NOBODY: player1.spec was undefined and the whole probe died
// before its first assertion, reporting KeyError 'id' — a crash that reads like the mode
// is broken and is the check counting a roster that no longer exists.
const EXILE = NINJA_ROSTER.findIndex(s => s.name === 'Exile');
if (EXILE < 0) return JSON.stringify({ fatal: 'Exile is not on the roster' });
gameMode = '2p'; cpuMode = false; attractMode = false;
p1Pick = EXILE; p2Pick = 0; stagePick = 'bamboo'; startNewGame(); roundIntroTimer = 0;
await frame(); await frame();
const p = player1, foe = player2;
const out = { name: p.spec.name, id: p.spec.id, exileIdx: EXILE,
               defense: p.spec.stats.defense, fragile: 1.25 };
p.champion = 0; p.frenzyTimer = 0;

// 1. combat fills the gauge
p.hp = p.maxHp; p.invulnTimer = 0; p.stunTimer = 0; p.blockTimer = 0;
p.takeDamage(10, foe, {});
out.gaugeFromTaken = p.champion;

// ⛔ enterChampion(), NOT modeKey(), FROM HERE DOWN. Owner, Sep 22 2026 paused every
// second mode, so modeKey returns at its first statement and can no longer prove
// anything about the MODE — only about the pause. What this file is for is the mode
// itself: that the gauge fills, that it refuses below full, that firing SPENDS, and that
// the fragility really comes off. All of that is what a redesign needs to keep working,
// so it is driven through the mode's own entry. The PAUSE is asserted separately below,
// and pinned in source by tools/check_first_form_gate.mjs.

// 2. the mode REFUSES below full, and spends nothing
p.stunTimer = 0; p.state = STATE.IDLE; p.isGrounded = true; p.vanishTimer = 0;
const before = p.champion;
p.enterChampion();
out.refusedBelowFull = p.frenzyTimer <= 0 && p.champion === before;
out.stanceLeak = p.chudan === true;          // the shared key must not hand her chudan

// 3. at full it fires, and it SPENDS
p.champion = CHAMPION_MAX;
p.stunTimer = 0; p.state = STATE.IDLE; p.isGrounded = true;
p.enterChampion();
out.firedAtFull = p.frenzyTimer > 0;
out.leftInGauge = p.champion;

// 4. the fragility is really off — HP LOST, on two fresh bodies, same raw damage
const hpLost = (championOn) => {
  const q = new Player(1, 150, GROUND_Y - 48, NINJA_ROSTER[EXILE], true);
  q.opponent = foe; q.hp = q.maxHp; q.comboHits = 0;
  q.invulnTimer = 0; q.stunTimer = 0; q.blockTimer = 0;
  q.frenzyTimer = championOn ? 5 : 0;
  q.takeDamage(20, foe, {});
  return q.maxHp - q.hp;
};
out.hpLostNormal = hpLost(false);
out.hpLostChampion = hpLost(true);

// 5. THE PAUSE, LIVE. This used to assert the opposite — that a real V keydown reaches
//    her — and it is kept rather than deleted because the polarity is the only thing
//    that changed: when second modes become unlocks, it flips back. check_first_form_gate
//    pins the pause in the SOURCE; this is the behavioural half, with a full gauge and a
//    live match, which is the only state where a leak could show.
//    pressCombat drops everything unless the match is actually live (matchActive,
//    unpaused, intro over, no hitstop), so stand the match up or the press proves nothing.
p.frenzyTimer = 0; p.champion = CHAMPION_MAX;
p.stunTimer = 0; p.state = STATE.IDLE; p.isGrounded = true;
matchActive = true; paused = false; roundIntroTimer = 0; hitstopRemaining = 0;
p.modeKey();
out.methodPaused = p.frenzyTimer <= 0 && p.champion === CHAMPION_MAX;
window.dispatchEvent(new KeyboardEvent('keydown', { code: 'KeyV', bubbles: true }));
out.keyVPaused = p.frenzyTimer <= 0 && p.champion === CHAMPION_MAX;

// 6. ...AND THE SHARED KEY HANDS NOBODY ELSE A STANCE EITHER. This asserted that the
//    Executioner still toggles into chudan on the same press — he was the one second
//    mode carved out of the first-form gate at 790/793, and Sep 22 2026 put him back
//    behind it. Same press, same fighter, opposite expectation.
p1Pick = 0; p2Pick = 1; startNewGame(); roundIntroTimer = 0;
await frame(); await frame();
const x = player1;
x.stunTimer = 0; x.state = STATE.IDLE; x.isGrounded = true;
x.modeKey(); out.execChudanPaused = x.chudan === false;
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
    ok(r['name'] == 'Exile', f"player1 is Exile (roster index {r['exileIdx']}, got {r['name']})")
    ok(r['gaugeFromTaken'] > 0, f"combat fills the gauge ({r['gaugeFromTaken']:.1f})")
    ok(r['refusedBelowFull'], 'the mode key refuses below a full gauge and spends nothing')
    ok(not r['stanceLeak'], 'the shared mode key does not put Exile in chudan')
    ok(r['firedAtFull'], 'the mode fires at a full gauge')
    ok(r['leftInGauge'] == 0, f"firing SPENDS the gauge (left {r['leftInGauge']})")
    ok(r['hpLostChampion'] < r['hpLostNormal'],
       f"fragility is OFF in champion: {r['hpLostNormal']:.2f} HP normal "
       f"vs {r['hpLostChampion']:.2f} champion")
    # ⛔ THE RATIO IS NOT 1.25, AND IT NEVER WAS. Champion does not make her take NORMAL
    # damage — it drops her from the flat 1.25 fragility to her own stat-derived
    # defenseFactor, 1 + (6 - defense) * 0.03, which at defense 3 is 1.09. So the ratio
    # between the two is 1.25 / 1.09 = 1.147, and asserting a literal 1.25 conflated "the
    # 1.25 tax comes off" with "the ratio is 1.25". Derive it from her stats, so a defense
    # change moves the expectation instead of breaking the check.
    base = 1 + (6 - r['defense']) * 0.03
    want = r['fragile'] / base
    ratio = r['hpLostNormal'] / r['hpLostChampion'] if r['hpLostChampion'] else 0
    ok(abs(ratio - want) < 0.02,
       f"...and it is exactly {r['fragile']}/{base:.2f} = {want:.3f}x (measured {ratio:.3f}x)")
    ok(r['methodPaused'], 'PAUSED: modeKey does not give her champion at a full gauge')
    ok(r['keyVPaused'], 'PAUSED: a real V keydown does not give her champion either')
    ok(r['execChudanPaused'], 'PAUSED: the same key no longer puts the Executioner in chudan')

    if fails:
        print(f'\n{len(fails)} FAILED')
        return 1
    print('\nall good')
    return 0


if __name__ == '__main__':
    sys.exit(main())
