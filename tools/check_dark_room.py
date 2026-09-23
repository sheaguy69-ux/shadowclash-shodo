#!/usr/bin/env python3
"""THE DARK ROOM + KUBIKIRI — the smallest thing that fails if the room breaks.

  python3 tools/serve.py &          # 9101, the owner's tree
  python3 tools/check_dark_room.py

Owner, Sep 23 2026: "Wall-break + dark room ambush. Big knockback smashes the wall; the
target lands in a dark room, the chaser sees only shadows; Kubikiri is an unblockable
ambush; the chaser checks with blind kunai or sweeps — need in the game." Rulings the same
day: dust + creaks only, a real partition, Kubikiri on its own multiplier, Mizu immune.

Drives the REAL page through tools/watch_game.py, because every one of these can be true
in the source and false in the game. Each block is a way the room dies quietly:

  A  the room exists on the hall and nowhere else; the shared STAGES entry is untouched
  B  a GUARDED shove smashes a wall the defender never lost (blockstun rides stunTimer)
  C  ONE real forward throw fails to open it, or sends the THROWER in too
  D  Kubikiri is not unblockable vs a blind entry — or it still is vs a checked one
  E  the blind checks (a low sweep, a thrown blade into the dark) never register
  F  a hit that finds the hider does not drag them into the light
  G  moving in the dark is silent, or standing still creaks
  H  Mizu, blind in the story bible, is fooled by the dark anyway
  I  a round reset leaves the room open
  J  the room's back wall bills the far door, or the real door stops working
  K  after-images draw a hidden fighter at full alpha (the leak a skeptic caught)
  L  the CPU tracks the hider through the dark, or cannot hear the creaks
  M  the mechanic ships without its drill (owner, Aug 10: every new mechanic does)

Held keys for P1 go in physKeys too: the engine scrubs P1's keys every frame otherwise,
and a probe that "sees nothing" would read exactly like a pass.
"""
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
OUT = pathlib.Path('/private/tmp/shadowclash-check-dark-room')

PROBE = r'''
const frame = () => new Promise(r => requestAnimationFrame(r));
const frames = async n => { for (let i = 0; i < n; i++) await frame(); };
const pick = n => NINJA_ROSTER.findIndex(s => s.name === n);
const HALL = STAGES.find(s => s.id === 'hall');
const out = {};
// Every board change and match restart is logged with who called it, so a stage that
// changes under the probe names its caller instead of surfacing as a null deep inside.
const stageLog = [];
const _setStage = setStage, _startNewGame = startNewGame;
const who = () => (new Error().stack || '').split('\n').slice(2, 5).map(l => l.trim()).join(' <- ');
setStage = function (st) { stageLog.push({ fn: 'setStage', to: st && st.id, sec: out.section, from: who() }); return _setStage(st); };
startNewGame = function (...a) { stageLog.push({ fn: 'startNewGame', pick: stagePick, attract: attractMode, sec: out.section, from: who() }); return _startNewGame(...a); };
try {
async function start(a, b) {
  gameMode = '2p'; cpuMode = false; attractMode = false; spectate = false;
  p1Pick = pick(a); p2Pick = pick(b); stagePick = 'hall';
  startNewGame(); roundIntroTimer = 0;
  await frames(2);
  matchActive = true; paused = false; hitstopRemaining = 0;
  for (const p of [player1, player2]) settle(p);
}
function settle(p) {
  p.stunTimer = 0; p.state = STATE.IDLE; p.recoveryTimer = 0; p.vx = 0;
  p.hitboxes.length = 0; p.revealT = 0; p.throwTimer = 0; p.grabbedBy = null;
}
function openWith(p) {
  currentStage.walls = (currentStage.walls || []).filter(w => !w.breach);
  breach.open = true; breach.owner = p;
  p.x = (breach.x0 + breach.x1) / 2 - p.width / 2; p.vx = 0;
}
const guardP1 = on => { keys['p1_poof'] = on; keys['KeyC'] = on; on ? physKeys.add('KeyC') : physKeys.delete('KeyC'); };

out.section = 'A';
// ---- A. the room exists on the hall, and only there -------------------------------
await start('Kael', 'Executioner');
out.onHall = currentStage.id === 'hall';
out.hallDark = currentStage.dark === -1;
out.partitions = (currentStage.walls || []).filter(w => w.breach).length;
out.sealed = !!breach && !breach.open;
out.room = breach && [breach.x0, breach.x1];
out.sharedUntouched = !(HALL.walls || []).some(w => w.breach);
out.tag = hazardTag(HALL);
out.clampSealed = clampLandX(20, 30);
out.partitionFace = breach.x1 + PARTITION_W;
setStage(STAGES.find(s => s.id === 'bamboo'));
out.bambooNoRoom = breach === null && !(currentStage.walls || []).some(w => w.breach);

out.section = 'B';
// ---- B. a GUARDED body driven into the partition does not break it -----------------
await start('Kael', 'Executioner');
{
  const v = player2;
  v.x = breach.x1 + PARTITION_W + 30; player1.x = v.x + 80;
  keys['p2_poof'] = true;
  await frames(3);
  v.state = STATE.BLOCKING; v.stamina = 100; v.stunTimer = 0.3; v.vx = -420;
  let sawBlockingAtWall = false;
  for (let i = 0; i < 20; i++) {
    await frame();
    if (v.x <= breach.x1 + PARTITION_W + 1 && v.state === STATE.BLOCKING) sawBlockingAtWall = true;
  }
  keys['p2_poof'] = false;
  out.guarded = { sawBlockingAtWall, sealed: !!breach && !breach.open, wear: stageWear.breach };
}

out.section = 'C';
// ---- C. ONE real forward throw opens it, and only the thrown body goes in ----------
await start('Kael', 'Executioner');
const T = player1, V = player2;
V.x = breach.x1 + PARTITION_W + 4;
T.x = V.x + V.width + 14;
await frames(2);
settle(T); settle(V);
const toastBefore = stageToastT;
// executeThrow returns nothing on success and false on refusal — read the state it sets
out.throwStarted = T.executeThrow() !== false && T.state === STATE.THROWING;
await frames(90);
out.thrown = {
  opened: !!breach && breach.open,
  partitionGone: !(currentStage.walls || []).some(w => w.breach),
  victimIn: inBreach(V), victimDark: V.inDark, victimAlpha: V.alpha,
  throwerOut: !inBreach(T), throwerDark: T.inDark, throwerAlpha: T.alpha,
  owner: !!breach && breach.owner === V, stillHall: currentStage.id === 'hall',
  noNewToast: stageToastT <= toastBefore,
};

out.section = 'D';
// ---- D. KUBIKIRI: blind entry vs checked entry vs still outside, guard held --------
async function strike(mode) {
  settle(T); settle(V); V.revealT = 0; V.ambushName = '';
  T.hp = T.maxHp; T.stamina = 100; T.facing = -1;
  if (mode === 'outside') T.x = breach.x1 + PARTITION_W + 6;
  else T.x = breach.x1 - T.width - 6;
  V.x = Math.max(breach.x0 + 2, (mode === 'outside' ? breach.x1 - V.width - 4 : T.x - V.width - 10));
  T.roomT = 0;
  guardP1(true);
  await frames(2);
  T.checkT = mode === 'checked' ? CHECK_T : 0;
  const rec = { tState: T.state, tRoomT: T.roomT, tIn: inBreach(T), vDark: V.inDark };
  const hp0 = T.hp;
  V.facing = T.x > V.x ? 1 : -1;
  V.executeAttack(STATE.ATTACK_HEAVY);
  rec.name = V.ambushName; rec.lit = V.revealT > 0;
  await frames(45);
  guardP1(false);
  rec.lost = +(hp0 - T.hp).toFixed(2);
  return rec;
}
settle(V); await frames(30);
out.blind = await strike('blind');
V.revealT = 0; await frames(60);
out.checked = await strike('checked');
V.revealT = 0; await frames(60);
out.outside = await strike('outside');

out.section = 'E';
// ---- E. the blind checks register ----------------------------------------------------
settle(T); T.checkT = 0; T.x = breach.x1 + 10; T.facing = -1;
keys['p1_down'] = true; keys['KeyS'] = true; physKeys.add('KeyS');
T.executeAttack(STATE.ATTACK_LIGHT);   // Down+Light: the universal sweep, a low
await frames(6);
keys['p1_down'] = false; keys['KeyS'] = false; physKeys.delete('KeyS');
out.sweepChecks = T.checkT > 0;
settle(T); T.checkT = 0; T.x = breach.x1 + 220;
T.projectiles.push({ kind: 'star', x: (breach.x0 + breach.x1) / 2, y: GROUND_Y - 40, vx: -1, vy: 0, spin: 1 });
await frames(1);
out.kunaiChecks = T.checkT > 0;
T.projectiles.length = 0;

out.section = 'F';
// ---- F. FOUND: a hit that finds the hider drags them into the light -----------------
settle(V); V.x = (breach.x0 + breach.x1) / 2 - V.width / 2; await frames(4);
out.found = { wasDark: V.inDark };
V.takeDamage(4, T, { pushback: 20 });
out.found.revealT = V.revealT;
await frames(2);
out.found.nowVisible = !V.inDark;

out.section = 'G';
// ---- G. moving in the dark creaks, standing still is silent -------------------------
settle(V); V.revealT = 0; V.x = (breach.x0 + breach.x1) / 2 - V.width / 2; await frames(5);
{
  const heard = new Set();
  let darkFrames = 0;
  for (let i = 0; i < 60; i++) {
    const left = i % 30 < 15;
    keys['p2_left'] = left; keys['p2_right'] = !left;
    await frame();
    if (V.inDark) darkFrames++;
    if (V.heardX !== undefined) heard.add(Math.round(V.heardX * 10));
  }
  keys['p2_left'] = keys['p2_right'] = false;
  // the walk can carry the hider out through the doorway (that is correct — out of the
  // room is out of the dark), so re-seat them in the middle before testing stillness
  V.x = (breach.x0 + breach.x1) / 2 - V.width / 2; settle(V);
  await frames(10);
  const before = V.heardX; let changed = 0;
  for (let i = 0; i < 120; i++) { await frame(); if (V.heardX !== before) changed++; }
  out.creaks = { moving: heard.size, darkFrames, stillChanges: changed, stillDark: V.inDark,
                 cx: +(V.x + V.width / 2).toFixed(1), inRoom: inBreach(V), owner: !!breach && breach.owner === V,
                 revealT: +(V.revealT || 0).toFixed(2), alpha: V.alpha, vx: +V.vx.toFixed(1), state: V.state };
}

out.section = 'H';
// ---- H. MIZU IS IMMUNE ------------------------------------------------------------------
await start('Mizu', 'Executioner');
openWith(player2); settle(player2); await frames(5);
out.mizu = { hiderDark: player2.inDark, hiderAlpha: player2.alpha };
await start('Kael', 'Executioner');
openWith(player2); settle(player2); await frames(5);
out.kael = { hiderDark: player2.inDark, hiderAlpha: player2.alpha };

out.section = 'I';
// ---- I. a round reset reseals the room --------------------------------------------------
resetRound(); await frames(2);
out.resealed = !!breach && !breach.open && (currentStage.walls || []).some(w => w.breach);

out.section = 'J';
// ---- J. the back wall bills nothing; the right wall is still the temple door ------------
await start('Kael', 'Executioner');
openWith(player2);
stageWear.wall = 0;
stageStress('wall', 2000, 12, 300);
out.backWallWear = stageWear.wall;
stageStress('wall', 2000, canvas.width - 12, 300);
out.doorQueued = !!pendingBreak && pendingBreak.kind === 'wall';
await frames(3);
out.movedToTemple = currentStage.id === 'temple';

out.section = 'K';
// ---- K. after-images never draw a hidden fighter -----------------------------------------
await start('Kael', 'Executioner');
openWith(player2); settle(player2); await frames(5);
{
  const man = SPRITES[player2.spec.name.toLowerCase()];
  const idle = Array.isArray(man.frames.idle) ? man.frames.idle[0] : man.frames.idle;
  player2.ghosts = [{ x: player2.x + 12, y: player2.y, idx: idle, facing: player2.facing, life: GHOST_LIFE }];
  let maxA = -1, calls = 0, err = null;
  const orig = drawShodoFrame;
  try {
    drawShodoFrame = function (c, ...r) { calls++; maxA = Math.max(maxA, c.globalAlpha); return orig.call(this, c, ...r); };
    ctx.save(); player2.draw(ctx); ctx.restore();
  } catch (e) { err = String(e); } finally { try { drawShodoFrame = orig; } catch (e) {} }
  out.ghosts = { hiddenAlpha: player2.alpha, dark: player2.inDark, calls, maxA, err };
  player2.ghosts = [];
}

out.section = 'L';
// ---- L. the CPU is blind to the dark, and hears it ---------------------------------------
await start('Kael', 'Executioner');
{
  const hid = player1, cpu = player2;
  hid.x = (breach.x1 + PARTITION_W) + 20; await frames(2);
  cpuThink(1 / 60, 1);                              // sees the hider once, in the open
  const sawAt = cpu.lastSawFoe;
  openWith(hid); settle(hid); await frames(4);      // the hider is now in the dark
  hid.x = breach.x0 + 4;                            // moves silently
  for (let i = 0; i < 120; i++) cpuThink(1 / 60, 1);
  const blindAt = cpu.lastSawFoe;
  hid.heardX = hid.x + hid.width / 2;               // a creak
  cpuThink(1 / 60, 1);
  out.cpu = { hidDark: hid.inDark, sawAt, blindAt, heardX: hid.heardX, heardAt: cpu.lastSawFoe };
  for (const k of ['p2_left', 'p2_right', 'p2_up', 'p2_down', 'p2_poof', 'KeyM']) keys[k] = false;
}

out.section = 'M';
// ---- M. the drill ships --------------------------------------------------------------
out.drill = DRILLS.some(d => /KUBIKIRI/.test(d.name || ''));
out.const = { KUBIKIRI_DMG, AMBUSH_DMG, BIG_KNOCK, ROOM_W };
// every restart/board change should have come from this probe's own start()/setStage calls
out.foreignStageChanges = stageLog.filter(e => !/start \(|probe|<anonymous>|eval/.test(e.from) && e.fn === 'startNewGame' && e.attract);
} catch (e) { out.__err = String(e) + ' — in section ' + out.section + ' (stage ' + (currentStage && currentStage.id) + ', breach ' + JSON.stringify(breach) + ')'; out.stageLog = stageLog; }
finally { setStage = _setStage; startNewGame = _startNewGame; }
return JSON.stringify(out);
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    script = OUT / 'probe.json'
    script.write_text(json.dumps([
        {"wait": 1.2}, {"key": "Space"}, {"wait": 0.5},
        # The probe runs past watch_game's 20s-per-eval CDP timeout on a loaded machine, so
        # it runs in the background and is polled; each poll returns the moment it is done.
        {"eval": "window.__darkR = null; window.__darkP = (async () => {" + PROBE + "})()"
                 ".then(r => window.__darkR = r, e => window.__darkR = JSON.stringify({__err: String(e)}));"
                 " return 'started';"},
        *[{"eval": "await Promise.race([window.__darkP, new Promise(r => setTimeout(r, 15000))]);"
                   " return window.__darkR !== null;"}] * 8,
        {"eval": "return window.__darkR;", "label": "DARK"},
    ], indent=1))
    subprocess.run([sys.executable, str(REPO / 'tools/watch_game.py'),
                    '--script', str(script), '--out', str(OUT / 'run')],
                   check=True, capture_output=True, text=True)
    log = (OUT / 'run/log.txt').read_text()
    i = log.index('DARK: ')
    raw = json.JSONDecoder().raw_decode(log[i + len('DARK: '):])[0]
    r = json.loads(raw) if isinstance(raw, str) else raw
    if r and r.get('__err'):
        print('the probe threw inside the page:', r['__err'])
        for e in r.get('stageLog', [])[-8:]:
            print('   ', e)
        return 1
    if r is None:
        print('the probe returned nothing — it threw inside the page; see', OUT / 'run/log.txt')
        return 1

    fails = []

    def ok(cond, msg):
        print(f"  {'ok  ' if cond else 'FAIL'}  {msg}")
        if not cond:
            fails.append(msg)

    print('\nTHE DARK ROOM — live checks\n')
    ok(r['onHall'] and r['hallDark'], 'the Broken Hall carries a dark room (dark: -1)')
    ok(r['partitions'] == 1 and r['sealed'], f"one sealed partition; room spans {r['room']}")
    ok(r['sharedUntouched'], 'the partition lives on a COPY — the shared STAGES entry is untouched')
    ok('dark room' in r['tag'], f"the stage tile says so ('{r['tag']}')")
    ok(r['clampSealed'] >= r['partitionFace'],
       f"nothing can land behind a sealed partition (clampLandX(20) = {r['clampSealed']} >= {r['partitionFace']})")
    ok(r['bambooNoRoom'], 'a board without `dark` has no room')

    g = r['guarded']
    ok(g['sawBlockingAtWall'], 'B setup: the guarding body really reached the partition while BLOCKING')
    ok(g['sealed'] and g['wear'] == 0, f"a GUARDED shove does not break it (wear {g['wear']})")

    t = r['thrown']
    ok(r['throwStarted'], 'C setup: the forward throw started')
    ok(t['opened'] and t['partitionGone'], 'ONE forward throw smashes the partition')
    ok(t['victimIn'] and t['victimDark'] and t['victimAlpha'] == 0,
       f"the thrown body is inside and gone (alpha {t['victimAlpha']})")
    ok(t['throwerOut'] and not t['throwerDark'] and t['throwerAlpha'] > 0.9,
       f"the THROWER stays outside and visible (alpha {t['throwerAlpha']:.2f})")
    ok(t['owner'], 'the room belongs to the one who went through')
    ok(t['stillHall'] and t['noNewToast'], 'no board swap and no toast — a wall fell, the fight did not move')

    b, c, o = r['blind'], r['checked'], r['outside']
    print(f"\n  Kubikiri, guard held: blind {b['lost']} hp, checked {c['lost']} hp, outside {o['lost']} hp\n")
    ok(b['vDark'] and b['tIn'] and b['tRoomT'] < 0.5 and b['tState'] == 'BLOCKING',
       f"D setup (blind): hider dark, chaser inside {b['tRoomT']:.2f}s, guarding ({b['tState']})")
    ok(b['name'] == 'KUBIKIRI' and b['lit'], 'a HEAVY at a blind entry is KUBIKIRI, and it lights the hider up')
    ok(b['lost'] > 20, f"...and it goes THROUGH the guard ({b['lost']} hp)")
    ok(c['name'] != 'KUBIKIRI', 'CHECKED first: the same heavy is not Kubikiri')
    ok(c['lost'] < b['lost'] / 3, f"...and the guard holds it ({c['lost']} hp vs {b['lost']})")
    ok(o['name'] != 'KUBIKIRI', f"a chaser still OUTSIDE gets an ordinary heavy ({o['lost']} hp)")

    ok(r['sweepChecks'], 'a low sweep into the dark counts as a check')
    ok(r['kunaiChecks'], 'a thrown blade into the dark counts as a check')

    f = r['found']
    ok(f['wasDark'] and f['revealT'] > 0 and f['nowVisible'], 'a hit that finds the hider drags them into the light')

    k = r['creaks']
    ok(k['moving'] >= 3, f"moving in the dark creaks ({k['moving']} creaks in 1.2 game-s, dark {k['darkFrames']}/60 frames)")
    ok(k['stillChanges'] == 0 and k['stillDark'], f"standing still in the dark is silent, and stays dark {({x: k[x] for x in ('cx','inRoom','owner','revealT','alpha','vx','state')})}")

    ok(not r['mizu']['hiderDark'] and r['mizu']['hiderAlpha'] > 0.9,
       f"MIZU IS IMMUNE: the dark hides nothing from her (hider alpha {r['mizu']['hiderAlpha']:.2f})")
    ok(r['kael']['hiderDark'] and r['kael']['hiderAlpha'] == 0, '...while the same room hides from anyone else')

    ok(r['resealed'], 'a round reset reseals the room')
    ok(r['backWallWear'] == 0, "the room's back wall bills nothing to the door")
    ok(r['doorQueued'] and r['movedToTemple'], 'the RIGHT wall is still the door to the temple')

    gh = r['ghosts']
    ok(gh['err'] is None and gh['calls'] > 1, f"K setup: the after-image path really drew ({gh['calls']} draws, err {gh['err']})")
    ok(gh['dark'] and gh['maxA'] == 0, f"after-images never draw a hidden fighter (max alpha {gh['maxA']})")

    cp = r['cpu']
    ok(cp['hidDark'] and abs(cp['blindAt'] - cp['sawAt']) < 1,
       f"the CPU stays blind in the dark — still steering by {cp['sawAt']:.0f} after 2s, not the true spot")
    ok(abs(cp['heardAt'] - cp['heardX']) < 1, f"...and a creak gives it a fresh fix ({cp['heardAt']:.0f})")

    ok(r['drill'], 'the KUBIKIRI drill ships with it')
    ok(not r.get('foreignStageChanges'),
       f"no match restart came from outside the probe (e.g. a late title/attract bout): {r.get('foreignStageChanges')}")
    print(f"\n  constants: {r['const']}")

    if fails:
        print(f'\n{len(fails)} FAILED')
        return 1
    print('\nall good')
    return 0


if __name__ == '__main__':
    sys.exit(main())
