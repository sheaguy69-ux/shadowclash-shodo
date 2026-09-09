"""Which of the 30 inputs per fighter are actually DIFFERENT moves?

  python3 tools/serve.py &                       # 9100, the only server
  python3 tools/audit_move_coverage.py

Fires every (grounded/airborne x 5 directions x 3 buttons) on each of the six originals
and fingerprints what came back. Two inputs with the SAME fingerprint are the same move —
one of them has no move of its own and is falling through to the other.

⛔ THE RULER IS THE spawnHitbox CALL, NOT DAMAGE AND NOT THE LIVE hitboxes ARRAY. Both of
those were tried on Aug 2 2026 and both lied:

  * polling `p.hitboxes` once per frame MISSES a box that spawns and expires between two
    samples — it called Tsubasa's forward Special dead when it does 8 damage.
  * damage against a parked opponent depends on where everyone is STANDING. Every
    airborne attack read 0 because the target was 120px below it, and Ember's 28px-wide
    claw cannot reach an opponent 62px away. That ruler reported 86 dead inputs of 180.

⛔ AND THE RULER ITSELF LIED ONCE MORE. This file used to claim here that the real
number of dead inputs is ZERO. It was not measured — `attackAir` is set by every press
and was missing from COST_ONLY, so the DEAD branch could not fire for any input on any
fighter and the zero was arithmetic. Corrected Aug 11 2026: 19 on the tree that had it
wrong, 16 today. Mizu's whole Special column and every one of Oni's ten Special inputs
spend chakra and return nothing.

Wrapping spawnHitbox records what the move ASKS FOR at the moment it is authored, which
is independent of positions and of the frame clock.

⛔ "DID ANYTHING HAPPEN" IS A DIFF OF THE WHOLE PLAYER, NOT A LIST OF FIELDS YOU THOUGHT OF.
A hitbox is only one way a move can be real. The first version of this tool watched five
named parry flags and declared seven inputs dead. Every one of them was a real move:
Ember's and Kael's Back+Specials are PARRY_STANCE with parryFlashTimer, Tsubasa's neutral
Special is the same stance at a stricter 0.133, and Shin's Back+Special is a vanish
(vanishTimer, and it flips his facing). Shin's kunai and wire are projectiles. A guessed
field list can only find the mechanisms you already remembered — snapshotting every scalar
on the player before and after finds the ones you didn't. The do-nothing control proves
the diff is clean: press nothing, and NOTHING changes.

A fighter is reset with startNewGame() before EVERY input. Sharing one fighter across all
30 let a move's lingering lock bleed into the next nine inputs, which reads exactly like a
row of missing moves.
"""
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
OUT = REPO / 'media/audit/move-coverage'
DIRS = ['neutral', 'fwd', 'back', 'down', 'up']
BTN = ['L', 'M', 'H', 'S']
ORDER = ['Executioner', 'Mizu', 'Shin', 'Tsubasa', 'Ember', 'Kael', 'Mokurai', 'Exile', 'Oni']
# The six originals are the default because they are the only kits with a known-good
# baseline to assert against. `--ids 6,8` audits a BENCHED fighter (benched is a roster-UI
# gate, not an engine gate — startNewGame takes any id), which is the only way to see
# Mokurai's and Exile's coverage at all.
IDS = [int(x) for x in (sys.argv[sys.argv.index('--ids') + 1].split(',')
                        if '--ids' in sys.argv else '0,1,2,3,4,5,6,7,8'.split(','))]
# ⛔ ONE PARKING SPOT CANNOT TELL AN ECHO FROM A RANGE GATE. The Aug 13 sweep's first
# false-orphan cause was distance: a move that needs a wall or a nearby foe falls through
# to the neutral one at x=400 and reads as a duplicate of it. So the whole matrix is
# measured at three positions and an ECHO is only reported where it holds at ALL of them.
XS = [int(x) for x in (sys.argv[sys.argv.index('--x') + 1].split(',')
                       if '--x' in sys.argv else '140,400,760'.split(','))]
SLOTS = len(DIRS) * len(BTN)

PROBE = r'''
const frame = () => new Promise(r => requestAnimationFrame(r));
const DIRS = {neutral:[],fwd:['KeyD'],back:['KeyA'],down:['KeyS'],up:['KeyW']};
const BTN = {L:'ATTACK_LIGHT',M:'ATTACK_MEDIUM',H:'ATTACK_HEAVY',S:'ATTACK_SPECIAL'};
window.__DM = window.__DM || {};
const id = __ID__, air = __AIR__;
let name = null, F = null, CELL = null;
for (const [dn, dkeys] of Object.entries(DIRS)) {
  for (const [bn, stk] of Object.entries(BTN)) {
    p1Pick = id; p2Pick = (id + 1) % 6; startNewGame(); roundIntroTimer = 0;
    await frame(); await frame();
    const p = player1;
    if (!name) {
      name = p.spec.name; F = SPRITES[name.toLowerCase()].frames;
      CELL = {}; for (const k in F) (CELL[F[k]] = CELL[F[k]] || []).push(k);
      window.__DM[name] = window.__DM[name] || {};
    }
    const spawned = [];
    const orig = p.spawnHitbox.bind(p);
    p.spawnHitbox = function (w, h, dmg, delay, kb, opt) {
      spawned.push([Math.round(w), Math.round(h), Math.round(dmg), +(delay||0).toFixed(2),
                    Math.round(kb||0),
                    Object.keys(opt||{}).filter(k=>opt[k]===true).sort().join('+')].join('/'));
      return orig(w, h, dmg, delay, kb, opt);
    };
    for (const k in keys) keys[k] = false;
    p.x = __X__; p.facing = 1; p.stamina = 100; p.chakra = 100;
    p.chainComboTier = 0; p.attackHasConnected = false; p.connectTime = -1e9;
    if (air) { p.state = STATE.JUMP; p.isGrounded = false; p.y = GROUND_Y - 200; p.vy = -40; }
    // position and the anim clock move on their own every frame — everything else that
    // differs is the move doing something
    const NOISE = ['x','y','vx','vy','animPhase','animTime','facing'];
    const snap = () => { const o = {}; for (const k in p) {
      const v = p[k]; if (typeof v === 'number' || typeof v === 'boolean') o[k] = v; } return o; };
    // ⛔ A MOVE CAN ACT ON THE WORLD, NOT ON THE PLAYER. snap() walks the fighter's own
    // scalars, so a special whose entire effect is a push onto a GLOBAL list reads as
    // doing nothing — which is exactly what happened to Mizu's mist, her signature move
    // and the one her whole card is built on. It spends chakra, pushes a smokeField and
    // sets not one field on her, so this tool called it dead. The player diff was the
    // right idea and still is; it was just not the whole world.
    const globalsBefore = { smoke: smokeFields.length,
                            particles: (typeof particles !== 'undefined' ? particles.length : 0) };
    const before = snap();
    dkeys.forEach(k => keys[k] = true);
    let err = null;
    try { p.executeAttack(STATE[stk]); } catch (e) { err = e.message; }
    const after = snap();
    const touched = Object.keys(after).filter(k => before[k] !== after[k] && !NOISE.includes(k));
    // particles are deliberately NOT counted as "did something" — almost every move makes
    // a few, so they would make the dead check as useless as attackAir did. A smoke FIELD
    // is different: it is a persistent world object that changes what both fighters and
    // the CPU can see, and only a handful of moves create one.
    if (smokeFields.length !== globalsBefore.smoke) touched.push('smokeFields');
    const stName = Object.keys(STATE).find(k => STATE[k] === p.state);
    const cells = []; let proj = 0;
    const dur = p.attackAnim ? Math.round(p.attackAnim.dur) : 0;
    // the diff above is already taken, so this loop only has to see the move's own art
    // and its projectiles — it can stop as soon as the move is over. isAttackingState()
    // counts PARRY_STANCE, so a stance is not mistaken for the move having ended.
    for (let f = 0; f < 70; f++) {
      // ⛔ RE-ASSERT THE DIRECTION EVERY FRAME. No real key is down, so the game's own
      // input pass clears `keys` after one frame — the press lands with forward held but
      // by sampling time the axis is 0, and every direction-varying DRAW branch reads as
      // the neutral one. That is not the engine falling through, it is the probe letting
      // go of the stick, and it hid a wired move completely.
      dkeys.forEach(k => keys[k] = true);
      await frame();
      dkeys.forEach(k => keys[k] = true);   // ...and AFTER, because the frame we just
      // awaited rebuilds `keys` from the real keyboard, which is holding nothing. Setting
      // it only before the frame leaves the axis at 0 by the time we sample the cell.
      proj = Math.max(proj, (p.projectiles || []).length);
      if (p.attackAnim && f % 6 === 0) cells.push(spriteFrameIndex(p, F));
      if (!p.isAttackingState() && f > 6) break;
    }
    dkeys.forEach(k => keys[k] = false);
    p.spawnHitbox = orig;
    const uniq = [...new Set(cells)];
    window.__DM[name][(air?'air':'gnd')+'.'+dn+'.'+bn] = {
      box: [...new Set(spawned)].sort().join(' | '), nbox: spawned.length, proj, dur,
      cells: uniq.join(','), alias: uniq.map(i => (CELL[i]||[]).join('=')).join(' > '),
      state: stName, touched: touched.sort(), err };
  }
}
return name + (air ? ' air' : ' gnd');
'''


PRELOAD = r'''
const want = __IDS__.map(i => NINJA_ROSTER[i]).filter(n => n && !SPRITES[n.name.toLowerCase()]);
await Promise.all(want.map(async n => {
  const key = n.name.toLowerCase();
  const man = await (await fetch(`assets/sprites/${key}.json?v=${SHEET_V}`)).json();
  await new Promise((res, rej) => {
    const img = new Image();
    img.onload = () => { man.img = img; man.ready = true; SPRITES[key] = man; res(); };
    img.onerror = rej;
    img.src = `assets/sprites/${key}.png?v=${SHEET_V}`;
  });
}));
return Object.keys(SPRITES).join(',');
'''


def measure(x=400):
    steps = [{"wait": 1.2}, {"key": "Space"}, {"wait": 0.5},
             {"eval": "gameMode='2p';cpuMode=false;p1Pick=0;p2Pick=1;stagePick='bamboo';"
                      "attractMode=false;startNewGame();return 1", "label": "boot"},
             {"wait": 2.2},
             # A BENCHED fighter's sheet is never preloaded (public-battle skips them), so
             # SPRITES has no entry and the probe dies on `.frames`. Load exactly the ones
             # asked for, the same way the page would have.
             {"eval": PRELOAD.replace('__IDS__', json.dumps(IDS)), "label": "preload"},
             {"wait": 2.5}]
    for i in IDS:
        for air in ('false', 'true'):
            steps.append({"eval": PROBE.replace('__ID__', str(i)).replace('__AIR__', air)
                                       .replace('__X__', str(x)),
                          "label": f'{ORDER[i]}.{air[0]}'})
    steps.append({"eval": "return window.__DM", "label": "MATRIX"})
    OUT.mkdir(parents=True, exist_ok=True)
    script = OUT / f'probe-x{x}.json'
    script.write_text(json.dumps(steps, indent=1))
    subprocess.run([sys.executable, str(REPO / 'tools/watch_game.py'),
                    '--script', str(script), '--out', str(OUT / f'run-x{x}')],
                   check=True, capture_output=True, text=True)
    log = (OUT / f'run-x{x}/log.txt').read_text()
    i = log.index('MATRIX: ')
    return json.JSONDecoder().raw_decode(log[i + len('MATRIX: '):])[0]


# stamina/chakra are SPENT by any press, and the chain counter and recovery timers move
# on every attack — a move that changes only these has taken your resources and given you
# nothing back. Anything beyond them is the move actually doing something.
COST_ONLY = {'stamina', 'chakra', 'chakraCd', 'chainComboTier', 'recoveryTimer',
             'recoveryTotal', 'attackHasConnected', 'connectTime', 'state', 'lastAttackType',
             # ⛔ attackAir MADE THIS CHECK A TAUTOLOGY. executeAttack sets it
             # unconditionally on every press — measured in 270 of 270 probed inputs — so
             # `did` was never empty and the DEAD branch could not fire under any input on
             # any fighter. "0 dead of 180" was not a measurement, it was arithmetic, and
             # it was reported as evidence for hours. A detector that cannot fail proves
             # nothing; this is the second time in one audit that a green number came from
             # a broken ruler rather than a healthy game.
             'attackAir'}


def fp(v):
    """What makes two inputs the SAME move.

    Projectiles and the touched-field set belong here, not just the hitbox. Shin's
    forward Special throws a wire and his back Special is a vanish; both spawn no hitbox
    and reuse his neutral art, so a (box, cells, duration) key called them one move.
    """
    return v['box'], v['cells'], v['dur'], v['proj'], tuple(sorted(set(v['touched']) - COST_ONLY))


# A move sampled every 6th frame over `dur` ms yields dur/16.7/6 samples, so anything at
# or above this has room for at least two. Below it, one distinct cell proves nothing.
STATIC_MIN_MS = 250


def report(mats):
    """mats: {x: matrix}. A bucket is only reported where it holds at EVERY position."""
    base = mats[XS[len(XS) // 2]]
    dead, echo, static, stances, art = [], [], [], [], []
    for f in ORDER:
        if f not in base: continue
        for st in ('gnd', 'air'):
            groups, artgroups = {}, {}
            for d in DIRS:
                for b in BTN:
                    k = f'{st}.{d}.{b}'
                    vs = [mats[x][f][k] for x in XS if f in mats[x]]
                    v = base[f][k]
                    # DEAD/STATIC only where it is true at every parking spot.
                    if all(w['nbox'] == 0 and w['proj'] == 0
                           and not (set(w['touched']) - COST_ONLY) for w in vs):
                        dead.append((f, f'{st}.{d}+{b}', v['dur'], v['alias']))
                    cs = [c for c in v['cells'].split(',') if c != '']
                    if all(w['dur'] >= STATIC_MIN_MS
                           and len({c for c in w['cells'].split(',') if c != ''}) == 1 for w in vs):
                        (static if (v['nbox'] or v['proj']) else stances).append(
                            (f, f'{st}.{d}+{b}', v['dur'], v['alias']))
                    for x in XS:
                        if f in mats[x]:
                            groups.setdefault((x, fp(mats[x][f][k])), []).append(f'{d}+{b}')
                    if cs:
                        artgroups.setdefault(v['cells'], []).append((f'{d}+{b}', fp(v)))
            # ECHO: the same group of inputs collides at every position, not just one.
            seen = {}
            for (x, key), ks in groups.items():
                if len(ks) > 1: seen.setdefault(tuple(ks), set()).add(x)
            for ks, xs in seen.items():
                if len(xs) == len(XS): echo.append((f, st, list(ks)))
            # SHARED ART: different moves, same drawn cells — it LOOKS like a repeat.
            for cells, entries in artgroups.items():
                if len(entries) > 1 and len({e[1] for e in entries}) > 1:
                    art.append((f, st, [e[0] for e in entries], cells))
    total = len(ORDER) * SLOTS if len(base) == len(ORDER) else len(base) * SLOTS

    print('DEAD — spends stamina and chakra and does nothing else: no hitbox, no')
    print(f'       projectile, no stance, no movement, no timer of its own (all x in {XS})')
    for f, k, dur, alias in dead:
        print(f'  {f:12s} {k:18s} {dur:>4}ms  draws {alias[:52]}')
    print(f'  {len(dead)} of {total * 2}\n')

    print(f'STATIC — runs {STATIC_MIN_MS}ms+ and draws ONE cell the whole way: a still')
    print('         frame that deals damage')
    for f, k, dur, alias in static:
        print(f'  {f:12s} {k:18s} {dur:>4}ms  draws {alias[:52]}')
    print(f'  {len(static)} of {total * 2}\n')

    print(f'STANCE — a hitboxless stance held on ONE cell for {STATIC_MIN_MS}ms+. Deals no')
    print('         damage, so it is not the bucket above — but its peers animate.')
    for f, k, dur, alias in stances:
        print(f'  {f:12s} {k:18s} {dur:>4}ms  draws {alias[:52]}')
    print(f'  {len(stances)} of {total * 2}\n')

    print('ECHO — identical hitbox spec, cells, duration, projectiles and touched fields')
    print(f'       to another input, at EVERY parking spot {XS}. One of them has no move')
    print('       of its own. (A range-gated move that only collides at one x is not here.)')
    for f, st, ks in echo:
        print(f'  {f:12s} {st}  {" == ".join(ks)}')
    print(f'  {sum(len(k[2]) - 1 for k in echo)} redundant inputs of {total * 2}\n')

    print('SHARED ART — DIFFERENT moves drawing the SAME cells: the input is real, the')
    print('             animation is a repeat, so on screen the two look identical.')
    for f, st, ks, cells in art:
        print(f'  {f:12s} {st}  {" / ".join(ks):34s} cells {cells[:40]}')
    print(f'  {len(art)} shared rows\n')

    print(f'{"fighter":12s} {"ground":>12s} {"air":>12s}   distinct moves of {SLOTS}')
    tg = ta = 0
    for f in ORDER:
        if f not in base: continue
        g = len({fp(base[f][f'gnd.{d}.{b}']) for d in DIRS for b in BTN})
        a = len({fp(base[f][f'air.{d}.{b}']) for d in DIRS for b in BTN})
        tg, ta = tg + g, ta + a
        print(f'  {f:12s} {g:>8}/{SLOTS} {a:>9}/{SLOTS}')
    print(f'  {"TOTAL":12s} {tg:>8}/{total} {ta:>9}/{total}')
    return dead, echo, static, art


def main():
    mats = {}
    for x in XS:
        mats[x] = measure(x)
        print(f'  measured at x={x}: {len(mats[x])} fighters', file=sys.stderr)
    (OUT / 'matrix.json').write_text(json.dumps(mats, indent=1))
    dead, echo, static, art = report(mats)
    m = mats[XS[len(XS) // 2]]
    # The check that fails if this ever silently stops measuring. Each line is a mechanism
    # that is NOT a hitbox, and each one was reported as a dead button before it was added.
    if IDS != [0, 1, 2, 3, 4, 5, 6, 7, 8]:
        return 0          # --ids is a probe of a subset; the asserts below need the roster
    assert len(m) == 9, f'expected the nine, got {list(m)}'
    assert m['Shin']['gnd.down.S']['proj'] > 0, "lost sight of Shin's kunai"
    assert m['Kael']['gnd.back.H']['touched'], "lost sight of Kael's low parry"
    assert m['Kael']['gnd.back.S']['state'] == 'PARRY_STANCE', "Kael's niten parry"
    assert m['Ember']['gnd.back.S']['state'] == 'PARRY_STANCE', "Ember's blade-trap parry"
    assert 'vanishTimer' in m['Shin']['gnd.back.S']['touched'], "Shin's back vanish"
    # MEDIUM is a real tier (owner, Sep 1 2026), not a copy of Light: if the probe ever
    # stops reaching it, every M column would echo its L neighbour and read as art debt.
    assert any(m[f]['gnd.neutral.M']['box'] != m[f]['gnd.neutral.L']['box'] for f in m), \
        'MEDIUM never differs from LIGHT — the probe is not reaching the medium tier'
    return 0


if __name__ == '__main__':
    sys.exit(main())
