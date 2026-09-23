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

⛔ CHAMPION IS THE FIRST MODE OFF THE PAUSE (owner, Sep 23 2026: earn = unlock once, then
charge every match). So this file now drives the WHOLE EARN LOOP live, in the order a real
player meets it, because every step is a way the loop dies silently:

  * V fires while still LOCKED              -> the unlock is decoration
  * a full gauge never completes the trial  -> the mode is unreachable forever
  * V still dead after the unlock           -> earned and still denied
  * V fires on an EMPTY gauge once unlocked -> layer 2 is gone, the mode is a free button

Earning HER mode must open nothing else: the four roster-wide V+direction stances stay
paused for everyone, so an earned Exile holding a direction is checked too.

The Executioner is OPEN (owner, Sep 23 2026: "let excecu keep his 2nd from open out of
everyone") — CHUDAN on bare V, no trial, no gauge. Mizu, Shin and Tsubasa have no charge
rule yet and stay exactly as paused as 877 left them, so Shin is re-checked at the end.

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

// 5. THE EARN LOOP, LIVE — the whole of it, in the order a player meets it. Every step
//    runs against a REAL keydown as well as the method, because pressCombat has its own
//    gates (matchActive, unpaused, intro over, no hitstop) and a probe that only calls the
//    method proves the mode, never the button.
save.unlocked = {}; save.charged = {};          // deterministic: a previous run must not leak in
p.frenzyTimer = 0; p.champion = CHAMPION_MAX;
p.stunTimer = 0; p.state = STATE.IDLE; p.isGrounded = true;
matchActive = true; paused = false; roundIntroTimer = 0; hitstopRemaining = 0;

//  a. LOCKED, full gauge: nothing. Asserted before any frame runs, because the very next
//     frame is the one that completes her trial.
p.modeKey();
out.lockedMethodDead = p.frenzyTimer <= 0 && p.champion === CHAMPION_MAX;
window.dispatchEvent(new KeyboardEvent('keydown', { code: 'KeyV', bubbles: true }));
out.lockedKeyDead = p.frenzyTimer <= 0 && p.champion === CHAMPION_MAX;
out.lockedInSave = save.unlocked['Exile'] !== true;

//  b. THE TRIAL: a full gauge, carried through live frames, earns the mode. This runs off
//     updateStance -> tickSecondUnlock, so it also proves the hook is actually wired into
//     the frame and not merely defined.
await frame(); await frame();
out.unlockedBySurviving = save.unlocked['Exile'] === true;
out.trialCounted = save.charged['Exile'];

//  c. EARNED: the same press that did nothing a frame ago now fires.
p.stunTimer = 0; p.state = STATE.IDLE; p.isGrounded = true; p.champion = CHAMPION_MAX;
window.dispatchEvent(new KeyboardEvent('keydown', { code: 'KeyV', bubbles: true }));
out.firesOnceEarned = p.frenzyTimer > 0;
out.spentOnceEarned = p.champion;

//  d. ...BUT LAYER 2 STILL BITES. Unlocked is not unlimited: an empty gauge is still a
//     refusal, which is the half that makes the mode a decision instead of a button.
p.frenzyTimer = 0; p.champion = 0;
p.stunTimer = 0; p.state = STATE.IDLE; p.isGrounded = true;
window.dispatchEvent(new KeyboardEvent('keydown', { code: 'KeyV', bubbles: true }));
out.refusedEmptyAfterUnlock = p.frenzyTimer <= 0;

//  e. ...AND THE MOVE LIST FOLLOWS THE PLAYER, not the build. An earned mode is readable.
out.listShowsEarned = (MOVES_LIST['Exile'] || []).some(l => SECOND_FORM_LINE.test(l))
                      && !secondFormBlocked(p);

//  f. ...AND EARNING HER MODE OPENS NOTHING ELSE. The four roster-wide stances had no
//     guard of their own, so an earned Exile used to get MUKI on Up+V and SAYA on Down+V.
//     Held directions go through heldDir's own keys, which the residue guard scrubs unless
//     they are in physKeys — set both, or the "no stance" answer proves nothing.
const hold = (key, code, on) => { keys[key] = on; on ? physKeys.add(code) : physKeys.delete(code); };
const still = () => { p.stunTimer = 0; p.state = STATE.IDLE; p.isGrounded = true; p.vanishTimer = 0;
  p.frenzyTimer = 0; p.champion = 0; p.muki = 0; p.gyakute = false; };
still(); hold('p1_up', 'KeyW', true);   out.heldUp = heldDir(p);   p.modeKey(); hold('p1_up', 'KeyW', false);
out.leakMuki = p.muki > 0;
still(); hold('p1_down', 'KeyS', true); out.heldDown = heldDir(p); p.modeKey(); hold('p1_down', 'KeyS', false);
out.leakSaya = !!p.gyakute;

// 6. THE EXECUTIONER IS OPEN — no trial, no gauge, a clean save. Bare V toggles CHUDAN
//    both ways; a held direction falls through to it instead of reaching a paused stance;
//    and it survives live frames, because updateStance strand-clears anything BLOCKED and
//    an open mode must never read as blocked.
p1Pick = NINJA_ROSTER.findIndex(s => s.name === 'Executioner'); p2Pick = 1;
startNewGame(); roundIntroTimer = 0; await frame(); await frame();
save.unlocked = {}; save.charged = {};
const x = player1;
const xs = () => { x.stunTimer = 0; x.state = STATE.IDLE; x.isGrounded = true; x.vanishTimer = 0; };
xs(); x.chudan = false; x.modeKey(); out.execOn = x.chudan === true;
xs(); x.modeKey(); out.execOff = x.chudan === false;
xs(); x.chudan = false; x.muki = 0; hold('p1_up', 'KeyW', true); x.modeKey(); hold('p1_up', 'KeyW', false);
out.execUpFallsThrough = x.chudan === true && !(x.muki > 0);
x.chudan = true; await frame(); await frame(); out.execSurvivesFrames = x.chudan === true;
out.execListShows = (MOVES_LIST['Executioner'] || []).some(l => SECOND_FORM_LINE.test(l))
                    && !secondFormBlocked(x);
out.execNeededNoTrial = save.unlocked['Executioner'] !== true;

// 7. ...AND THE ONES WITH NO CHARGE RULE STAY PAUSED. Shin stands for the three.
p1Pick = NINJA_ROSTER.findIndex(s => s.name === 'Shin'); startNewGame(); roundIntroTimer = 0;
await frame(); await frame();
const sh = player1;
sh.stunTimer = 0; sh.state = STATE.IDLE; sh.isGrounded = true; sh.vanishTimer = 0;
sh.modeKey(); out.shinPaused = !sh.kageNui && secondFormBlocked(sh);
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
    print('\n  THE EARN LOOP\n')
    ok(r['lockedInSave'], 'she starts LOCKED — nothing in the save says otherwise')
    ok(r['lockedMethodDead'], 'LOCKED: a full gauge + modeKey gives her nothing')
    ok(r['lockedKeyDead'], 'LOCKED: a full gauge + a real V keydown gives her nothing')
    ok(r['unlockedBySurviving'],
       'THE TRIAL: carrying a full gauge through live frames EARNS the mode')
    ok(r['trialCounted'] == 1, f"...and it counted exactly one fill (got {r['trialCounted']})")
    ok(r['firesOnceEarned'], 'EARNED: the same V keydown now fires champion')
    ok(r['spentOnceEarned'] == 0, f"...and it still SPENDS the gauge (left {r['spentOnceEarned']})")
    ok(r['refusedEmptyAfterUnlock'],
       'LAYER 2 HOLDS: unlocked but empty is still a refusal — earned is not unlimited')
    ok(r['listShowsEarned'], 'the move list shows CHAMPION to the player who earned it')
    ok(r['heldUp'] == 'up' and r['heldDown'] == 'down',
       f"the held directions really registered (up={r['heldUp']}, down={r['heldDown']})")
    ok(not r['leakMuki'], 'EARNING HER MODE OPENS NOTHING ELSE: Up+V does not give her MUKI')
    ok(not r['leakSaya'], '...and Down+V does not give her SAYA')
    print('\n  THE EXECUTIONER IS OPEN\n')
    ok(r['execOn'], 'bare V puts him in CHUDAN — no trial, no gauge, clean save')
    ok(r['execOff'], '...and V again takes him out')
    ok(r['execUpFallsThrough'], 'a held direction falls through to CHUDAN, not to a paused stance')
    ok(r['execSurvivesFrames'], 'CHUDAN survives live frames — the strand guard does not clear an open mode')
    ok(r['execListShows'], 'his CHUDAN line is in the move list')
    ok(r['execNeededNoTrial'], '...and none of it needed a trial')
    ok(r['shinPaused'], 'STILL PAUSED: Shin has no charge rule, so V does nothing')

    if fails:
        print(f'\n{len(fails)} FAILED')
        return 1
    print('\nall good')
    return 0


if __name__ == '__main__':
    sys.exit(main())
