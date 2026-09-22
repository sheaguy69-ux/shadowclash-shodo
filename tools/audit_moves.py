#!/usr/bin/env python3
"""The move tables and the cells behind them — asked of the RUNNING GAME, not of the text.

  python3 tools/serve.py 9100 web &      # 9100, the only server
  python3 tools/audit_moves.py

REPLACES tools/check_moves.py, which answered every question by regex over 2MB of source
and was wrong in three ways that each hid a real bug:

  * "IS THIS CELL WIRED?" was `does this string appear in the file`. Presence is not
    reachability. `airthrow` appears in DIR_SPECIALS, so the old checker passed it — while
    the lookup that would fire it builds the literal key "3:null" and matches nothing, so
    Shin's srisaa and Tsubasa's divecut and airthrow are 18 cells of art no input can
    reach. A text search can never see that. Firing the input can.
  * THE TABLE PARSER was a regex, and its own comments record it silently skipping the
    three moves with the most hitboxes, then failing 15 healthy entries on its first run.
    The tables are live objects in the page. Reading them needs no parser at all.
  * TWO CHECKS ASSERTED ON PROSE. The roll's jump-cancel rule was
    `'this.rollTimer = 0; // jumping cancels' not in src` — reformat the comment and the
    check evaporates while the bug returns. It is now driven: roll, press jump, measure.

WHAT IS STILL STATIC, and correctly so: questions about the MANIFEST are data questions,
not text questions — does a sheet carry a `roll` cell, do the executioner's placeholder
keys exist, is the cell-54 tombstone still marked. Those read the JSON directly.

THE ONE THING THIS CANNOT DO is prove a STATE is reachable in play. Forcing `p.cracked`
and sampling proves the crack cells are wired to the mode; it does not prove a player can
reach the mode. Input-driven checks below cover the moves; state coverage is by directed
setup and is listed in the output so the gap is visible rather than implied.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from watch_game import drive

REPO = pathlib.Path(__file__).resolve().parents[1]
OUT = REPO / 'media/audit/moves'
SPRITES = REPO / 'web/assets/sprites'

# Deliberately unreachable, with the ruling that made it so. An entry here is a decision,
# not a silenced failure — remove it and the check comes straight back.
KNOWN_UNREACHABLE = {
    'DIR_SPECIALS': (
        'PUBLIC BATTLE BUILD — NEUTRAL SPECIAL ONLY (owner, Aug 3 2026, index.html ~5437). '
        'axis/down/up are pinned neutral to drop the whole directional-special layer in one '
        'line, and this table is pinned alongside it. The art stays packed and the ruling is '
        'reversible. ⛔ The comment above the lookup still claims these three "stayed live" — '
        'they do not; see docs/AUDIT-2026-08-11.md item 5, which is an open owner decision.'),
}

# Keys the engine BUILDS at runtime, so no source text ever contains them whole.
CONSTRUCTED = {'ksweep', 'kheel', 'kpush'}

# Cells that are packed, unreachable, and meant to be. Reason required.
KNOWN_DARK = {
    ('oni', 'divekick2'):     'SUPERSEDED, not forgotten. His air-down was rewired onto a '
                              'dedicated six-cell row (adown1-6) when his sheet was '
                              're-packed; divekick1/2 were the two-cell pair that stood in '
                              'before it, and the engine now has zero references to '
                              'divekick2. Left in the sheet because it is append-only. '
                              'Retire it to divekick2_old on the next pass that touches '
                              'oni.json — it is not worth a SHEET_V bump on its own.',
    ('shin', 'idle_stance1'): 'cleaner key of the idle, but 5px narrower than idle2 so it '
                              'pops on the breath cycle; needs the pair re-keyed, not a swap',
    ('oni', 'shadowblur'):    '⛔ PARKED BY THE OWNER, Aug 11 2026. The full red-black '
                              'dissolve — frame 4 of CLEAN-DASHBLUR-6 — reserved for ONI\'S '
                              'SECOND MODE dash. His ruling: base attacks first, second mode '
                              'after, and HE specifies it. Packed only so the frame is not '
                              'hunted for twice. NOTHING MAY WIRE THIS until he says so; see '
                              'docs/ONI-NEW-KIT-AUG9.md §6b.',
}

# ---- probe 1: the tables, as live objects ---------------------------------------
TABLES = r'''
gameMode = '2p'; cpuMode = false; attractMode = false;
p1Pick = 0; p2Pick = 1; stagePick = 'bamboo'; startNewGame(); roundIntroTimer = 0;
const out = { DIR_MOVES: DIR_MOVES, DIR_SPECIALS: DIR_SPECIALS,
              BOX_DUR: 0.12, roster: {},
              ROLL_SPEED, ROLL_TIME, ROLL_RECOVER };
for (const s of NINJA_ROSTER) out.roster[s.id] = s.name.toLowerCase();
// The KEY the engine actually builds for each table, which is the whole point: a table
// nothing can look up is a table of dead moves no matter how well formed its entries are.
out.specialKeyShape = (function () {
  const src = Player.prototype.executeAttack.toString();
  const m = src.match(/DIR_SPECIALS\[([^\]]+)\]/);
  return m ? m[1].trim() : null;
})();
out.moveKeyShape = (function () {
  const src = Player.prototype.executeAttack.toString();
  const m = src.match(/DIR_MOVES\[([^\]]+)\]/);
  return m ? m[1].trim() : null;
})();
return JSON.stringify(out);
'''

# ---- probe 2: fire every table entry, see what actually comes out ----------------
REACH = r'''
const frame = () => new Promise(r => requestAnimationFrame(r));
const DIRKEY = { fwd: 'KeyD', back: 'KeyA', down: 'KeyS', up: 'KeyW' };
const got = {};
const fire = async (id, dir, tier) => {
  p1Pick = id; p2Pick = (id + 1) % 6; startNewGame(); roundIntroTimer = 0;
  await frame(); await frame();
  const p = player1;
  for (const k in keys) keys[k] = false;
  p.stamina = 100; p.chakra = 100; p.isGrounded = true; p.stunTimer = 0;
  // hold the direction ACROSS the press: the input pass rebuilds `keys` from a keyboard
  // holding nothing, so setting it only before the call lets go of the stick before the
  // move reads it — that hid wired moves completely when this was first written.
  keys[DIRKEY[dir]] = true;
  try { p.executeAttack(STATE[tier]); } catch (e) { return { err: e.message }; }
  keys[DIRKEY[dir]] = false;
  return { art: p.moveArt || null, dur: p.attackAnim ? Math.round(p.attackAnim.dur) : 0 };
};
for (const [tname, tbl] of [['DIR_MOVES', DIR_MOVES], ['DIR_SPECIALS', DIR_SPECIALS]]) {
  const tier = tname === 'DIR_MOVES' ? 'ATTACK_HEAVY' : 'ATTACK_SPECIAL';
  for (const key of Object.keys(tbl)) {
    const [id, dir] = key.split(':');
    got[tname + ' ' + key] = await fire(+id, dir, tier);
  }
}
return JSON.stringify(got);
'''

# ---- probe 3: which cells does the game actually DRAW? --------------------------
# spriteFrameIndex is a top-level function declaration, so it is a global binding and
# every caller resolves it at call time — wrapping it here observes the real draw path.
DRAWN = r'''
const frame = () => new Promise(r => requestAnimationFrame(r));
const seen = {};
const orig = spriteFrameIndex;
spriteFrameIndex = function (p, F) {
  const c = orig(p, F);
  const k = p.spec.name.toLowerCase();
  (seen[k] = seen[k] || {})[c] = 1;
  return c;
};
const DIRKEY = { neutral: null, fwd: 'KeyD', back: 'KeyA', down: 'KeyS', up: 'KeyW' };
for (const spec of NINJA_ROSTER) {
  const key = spec.name.toLowerCase();
  if (!SPRITES[key]) {
    const man = await (await fetch(`assets/sprites/${key}.json?v=${SHEET_V}`)).json();
    await new Promise((res, rej) => { const im = new Image();
      im.onload = () => { man.img = im; man.ready = true; SPRITES[key] = man; res(); };
      im.onerror = rej; im.src = `assets/sprites/${key}.png?v=${SHEET_V}`; });
  }
  p1Pick = spec.id; p2Pick = (spec.id + 1) % 6; startNewGame(); roundIntroTimer = 0;
  await frame();
  const p = player1, F = SPRITES[key].frames;
  const sample = () => { try { spriteFrameIndex(p, F); } catch (e) {} };
  // ⛔ recoveryTimer MUST be cleared. executeAttack refuses while a previous move is
  // recovering, so without this only the FIRST input of each fighter ever fires and every
  // later one silently no-ops — which reported 1817 of 1941 cells as never drawn. The art
  // latches go too, or a stale flag paints the next move with the last one's cells.
  const reset = () => { p.hp = 100; p.stamina = 100; p.chakra = 100; p.stunTimer = 0;
    p.state = STATE.IDLE; p.isGrounded = true; p.vx = 0; p.vy = 0; p.rollTimer = 0;
    p.grabbedBy = null; p.throwTimer = 0; p.vanishTimer = 0; p.dashTimer = 0;
    p.blockPushTimer = 0; p.landT = 0; p.parryFlashTimer = 0;
    p.recoveryTimer = 0; p.recoveryTotal = 0; p.attackHasConnected = false;
    p.chainComboTier = 0; p.connectTime = -1e9; p.windedTimer = 0; p.attackAnim = null;
    if (p.clearMoveArt) p.clearMoveArt(); };
  // Every state the frame picker branches on, forced. Modes included: this proves the
  // cells are WIRED to the mode, not that a player can reach the mode.
  const states = [
    ['IDLE',     () => {}],
    ['RUN',      () => { p.state = STATE.RUN; p.vx = 200; }],
    ['JUMP',     () => { p.state = STATE.JUMP; p.isGrounded = false; }],
    ['CROUCH',   () => { p.state = STATE.CROUCH; }],
    ['BLOCKING', () => { p.state = STATE.BLOCKING; }],
    ['BLOCKHIT', () => { p.state = STATE.BLOCKING; p.blockPushTimer = 0.2; }],
    ['ROLL',     () => { p.state = STATE.ROLL; p.rollTimer = ROLL_TIME * 0.5; }],
    ['STUNNED',  () => { p.state = STATE.STUNNED; p.stunTimer = 0.4; }],
    ['PARRY',    () => { p.state = STATE.PARRY_STANCE; p.parryFlashTimer = 0.1; }],
    ['DASH',     () => { p.dashTimer = DASH_TIME * 0.5; }],
    ['LAND',     () => { p.landT = 0.05; }],
    ['CRACK',    () => { p.cracked = true; p.state = STATE.IDLE; }],
    ['KAGE',     () => { p.kageNui = true; p.state = STATE.IDLE; }],
    ['SAKATE',   () => { p.sakate = true; p.state = STATE.IDLE; }],
    ['GYAKUTE',  () => { p.gyakute = true; p.state = STATE.IDLE; }],
    ['CHAMPION', () => { p.championTimer = 3; p.state = STATE.IDLE; }],
    // ---- the states the first version could not reach. Each one was sitting in the
    // "named but unswept" bucket, which is where Tsubasa's 30 stranded cells hid.
    ['WALLCLING',  () => { p.state = STATE.WALL_CLING; p.isGrounded = false;
                           p.wallDir = 1; p.vy = 20; }],
    ['WALLSLIDE',  () => { p.state = STATE.WALL_CLING; p.isGrounded = false;
                           p.wallDir = 1; p.vy = 200; }],
    ['WALLJUMP',   () => { p.state = STATE.JUMP; p.isGrounded = false;
                           p.wallJumpLock = 0.1; p.vy = -300; }],
    ['CEILING',    () => { p.state = STATE.JUMP; p.isGrounded = false; p.ceilLatch = 1; }],
    ['THROWING',   () => { p.state = STATE.THROWING; p.throwTimer = 0.2; }],
    ['THROWN',     () => { p.state = STATE.THROWN; p.isGrounded = false; }],
    ['FLOORED',    () => { p.state = STATE.STUNNED; p.stunTimer = 0.5; p.flooredT = 0.6; }],
    ['FLOORED2',   () => { p.state = STATE.STUNNED; p.stunTimer = 0.5; p.flooredT = 0.2; }],
    ['TUMBLE',     () => { p.state = STATE.STUNNED; p.stunTimer = 0.5;
                           p.tumbleT = 0.3; p.tumbleT0 = 0.4; }],
    ['VANISH',     () => { p.vanishTimer = 1; p.state = STATE.IDLE; }],
    ['WINDED',     () => { p.windedTimer = 1; p.state = STATE.IDLE; }],
    ['SLAM1',      () => { p.slamPhase = 1; p.isGrounded = false; }],
    ['SLAM2',      () => { p.slamPhase = 2; p.isGrounded = false; }],
    ['ENLIGHTEN',  () => { p.enlightenTimer = 3; p.state = STATE.IDLE; }],
    ['FRENZY',     () => { p.frenzyTimer = 2; p.state = STATE.IDLE; }],
    ['IAI',        () => { p.iaiWindow = 0.3; p.state = STATE.IDLE; }],
    ['KO',         () => { p.hp = 0; p.state = STATE.STUNNED; p.stunTimer = 1; }],
    ['CROUCHBLK',  () => { p.state = STATE.CROUCH; p.blockPushTimer = 0.2; }],
  ];
  for (const [, setup] of states) {
    reset(); p.cracked = false; p.kageNui = false; p.sakate = false;
    p.gyakute = false; p.championTimer = 0;
    setup();
    for (let i = 0; i < 14; i++) { p.animPhase = i; sample(); }
  }
  // ...and every attack input, in both stances and both modes.
  // ⛔ DO NOT await real frames here. 9 fighters x 2 modes x 2 stances x 5 directions x
  // 3 tiers x 26 frames is ~14000 frames — four minutes, and it blew the 20s CDP timeout.
  // The frame picker derives a move's progress from animClock against attackAnim.start,
  // so ADVANCING THE CLOCK samples the same cells instantly and deterministically.
  for (const mode of ['base', 'mode']) {
    for (const air of [false, true]) {
      for (const dn of Object.keys(DIRKEY)) {
        for (const tier of ['ATTACK_LIGHT', 'ATTACK_HEAVY', 'ATTACK_SPECIAL']) {
          reset();
          p.cracked = false; p.kageNui = false; p.sakate = false; p.championTimer = 0;
          if (mode === 'mode') {
            if (spec.id === 6) p.cracked = true;
            else if (spec.id === 2) p.kageNui = true;
            else if (spec.id === 3) p.sakate = true;
            else if (spec.id === 7) p.championTimer = 3;
            else continue;
          }
          if (air) { p.isGrounded = false; p.state = STATE.JUMP; p.y = GROUND_Y - 200; }
          if (DIRKEY[dn]) keys[DIRKEY[dn]] = true;
          const t0 = animClock;
          try { p.executeAttack(STATE[tier]); } catch (e) {}
          for (let s = 0; s <= 20; s++) { animClock = t0 + s * 0.03; sample(); }
          animClock = t0;
          if (DIRKEY[dn]) keys[DIRKEY[dn]] = false;
        }
      }
    }
  }
  // the jump/fall bands are chosen by vy, not by the clock
  for (const vy of [-500, -300, -100, 0, 100, 400, 800]) {
    reset(); p.state = STATE.JUMP; p.isGrounded = false; p.vy = vy; sample();
  }
  // ⛔ EVERY ART LATCH, READ OFF THE OBJECT rather than hardcoded — the list drifts, and a
  // hardcoded one silently stops covering whatever was added since. These `*Anim` flags
  // are how a fighter's dedicated move art is selected, so a latch nobody sets here is a
  // whole move's cells reported as "named but unswept".
  const animFlags = Object.keys(p).filter(k => /Anim$/.test(k));
  for (const flag of animFlags) {
    for (const st of ['ATTACK_LIGHT', 'ATTACK_HEAVY', 'ATTACK_SPECIAL']) {
      for (const air of [false, true]) {
        reset();
        p.state = STATE[st]; p[flag] = true; p.attackAir = air;
        if (air) { p.isGrounded = false; p.y = GROUND_Y - 200; }
        p.attackAnim = { start: animClock * 1000, dur: 400 };
        const t0 = animClock;
        for (let s = 0; s <= 12; s++) { animClock = t0 + s * 0.035; sample(); }
        animClock = t0; p[flag] = false;
      }
    }
  }
  // ⛔ THE CHAIN. light1..5 / heavy1..n are selected by chainComboTier, so a sweep that
  // leaves the counter at 0 only ever sees the FIRST link of every string — which is most
  // of what was left in the gap after the states went in.
  for (const tier of [0, 1, 2, 3, 4]) {
    for (const st of ['ATTACK_LIGHT', 'ATTACK_HEAVY']) {
      for (const air of [false, true]) {
        for (const dn of Object.keys(DIRKEY)) {
          reset();
          p.chainComboTier = tier; p.attackAir = air;
          if (air) { p.isGrounded = false; p.y = GROUND_Y - 200; p.state = STATE.JUMP; }
          if (DIRKEY[dn]) keys[DIRKEY[dn]] = true;
          const t0 = animClock;
          try { p.executeAttack(STATE[st]); } catch (e) {}
          p.chainComboTier = tier;                 // executeAttack advances it; hold it
          for (let s = 0; s <= 16; s++) { animClock = t0 + s * 0.025; sample(); }
          animClock = t0;
          if (DIRKEY[dn]) keys[DIRKEY[dn]] = false;
        }
      }
    }
  }
  // the four command kicks, grounded and airborne
  for (const kk of ['sweep', 'push', 'heel', 'stomp']) {
    for (const air of [false, true]) {
      reset();
      p.state = STATE.ATTACK_LIGHT; p.kickKind = kk; p.attackAir = air;
      if (air) { p.isGrounded = false; p.y = GROUND_Y - 200; }
      p.attackAnim = { start: animClock * 1000, dur: 300 };
      const t0 = animClock;
      for (let s = 0; s <= 10; s++) { animClock = t0 + s * 0.03; sample(); }
      animClock = t0; p.kickKind = null;
    }
  }
  // moveArt drives the table-driven moves: every art stem the sheet carries a row for
  const stems = new Set();
  for (const k of Object.keys(F)) { const m = k.match(/^(.*?)1$/); if (m) stems.add(m[1]); }
  for (const stem of stems) {
    if (F[stem + '6'] === undefined) continue;         // only full six-cell rows
    for (const air of [false, true]) {
      reset();
      p.state = STATE.ATTACK_SPECIAL; p.moveArt = stem; p.attackAir = air;
      if (air) { p.isGrounded = false; p.y = GROUND_Y - 200; }
      p.attackAnim = { start: animClock * 1000, dur: 400 };
      const t0 = animClock;
      for (let s = 0; s <= 12; s++) { animClock = t0 + s * 0.035; sample(); }
      animClock = t0; p.moveArt = null;
    }
  }
}
spriteFrameIndex = orig;
const out = {};
for (const k in seen) out[k] = Object.keys(seen[k]).map(Number).filter(n => !isNaN(n));
return JSON.stringify(out);
'''

# ---- probe 4: behaviour the old file asserted on TEXT ---------------------------
BEHAVIOUR = r'''
const frame = () => new Promise(r => requestAnimationFrame(r));
const R = {};
p1Pick = 0; p2Pick = 5; startNewGame(); roundIntroTimer = 0; matchActive = true;
await frame();
const p = player1, foe = player2;
const reset = () => { p.hp = 100; p.stamina = 100; p.chakra = 100; p.stunTimer = 0;
  p.state = STATE.IDLE; p.isGrounded = true; p.vy = 0; p.rollTimer = 0;
  p.blockedAt = -1e9; p.chudan = false; for (const k in keys) keys[k] = false; };

// 1. JUMP MUST NOT CANCEL THE ROLL. The old file asserted a COMMENT was absent.
reset(); p.state = STATE.ROLL; p.rollTimer = ROLL_TIME;
keys['KeyW'] = true; keys['Space'] = true;
for (let i = 0; i < 4; i++) { await frame(); keys['KeyW'] = true; keys['Space'] = true; }
R.rollSurvivesJump = p.rollTimer > 0 || p.state === STATE.ROLL;
R.rollLeftGround = !p.isGrounded;
reset();

// 2. THE RIPOSTE BEATS THE SLIP during blockstun. The old file regexed the order of two
//    identifiers; this presses the key with the guard genuinely held, which is the only
//    condition under which the bug appears.
reset(); p.state = STATE.BLOCKING;
p.takeDamage(10, foe, { pushback: 0, tier: STATE.ATTACK_HEAVY, canClash: true });
p.state = STATE.BLOCKING; p.stunTimer = 0;
keys['KeyH'] = true;                       // guard held, as it is during blockstun
R.reprisalArmed = animClock - p.blockedAt < REPRISAL_WINDOW;
const before = { rep: p.reprisalAnim, slip: p.slipAnim };
p.reprisalAnim = false; p.slipAnim = false;
fireCombatKey('KeyG', animClock);
R.tookRiposte = !!p.reprisalAnim;
R.tookSlip = !!p.slipAnim;
keys['KeyH'] = false;

// 3. A COUNTER MUST NOT INHERIT THE PREVIOUS MOVE'S ART LATCH.
reset(); keys['KeyD'] = true;
try { p.executeAttack(STATE.ATTACK_HEAVY); } catch (e) {}
keys['KeyD'] = false;
const stab = !!p.stabAnim;
p.state = STATE.BLOCKING; p.stunTimer = 0;
p.takeDamage(10, foe, { pushback: 0, tier: STATE.ATTACK_HEAVY, canClash: true });
p.state = STATE.BLOCKING; p.stunTimer = 0;
p.reprisalAnim = false;
fireCombatKey('KeyG', animClock);
R.hadStabBefore = stab;
R.staleStabAfterCounter = !!p.stabAnim && !!p.reprisalAnim;

return JSON.stringify(R);
'''


def main():
    d = drive([{"wait": 3.2}, {"key": "Space"}, {"wait": 0.6},
               {"eval": TABLES, "label": "TAB"},
               {"eval": REACH, "label": "REACH"},
               {"eval": BEHAVIOUR, "label": "BEH"},
               {"eval": DRAWN, "label": "DRAWN"}],
              OUT, ["TAB", "REACH", "BEH", "DRAWN"])
    T, REACHED, B, drawn = d['TAB'], d['REACH'], d['BEH'], d['DRAWN']
    roster = {int(k): v for k, v in T['roster'].items()}
    manifests = {n: json.loads((SPRITES / f'{n}.json').read_text()).get('frames')
                 for n in set(roster.values())}
    for n in manifests:
        if manifests[n] is None:
            manifests[n] = json.loads((SPRITES / f'{n}.json').read_text())

    fails, notes = [], []

    def check(cond, msg):
        if not cond:
            fails.append(msg)

    # ---- 1. table entries, read as objects — no parser to be wrong ---------------
    n_entries = 0
    for tname in ('DIR_MOVES', 'DIR_SPECIALS'):
        for key, e in T[tname].items():
            n_entries += 1
            label = f'{tname} {key}'
            who = roster[int(key.split(':')[0])]
            frames = manifests[who]
            art = e.get('art')
            missing = [i for i in range(1, 7) if f'{art}{i}' not in frames]
            check(not missing, f'{label}: {who} has no cells {missing} for art "{art}"')

            tr = e.get('track')
            check(tr and len(tr) == 6,
                  f'{label}: track has {len(tr) if tr else 0} stops, needs 6 '
                  f'or attackCellIndex ignores it')
            if tr and len(tr) == 6:
                check(tr[0] == 0, f'{label}: track must start at 0, starts at {tr[0]}')
                check(all(tr[i] < tr[i + 1] for i in range(5)),
                      f'{label}: track not increasing: {tr}')
                check(tr[-1] < 1.0, f'{label}: last stop {tr[-1]} is at or past the end')

            delays = [b[3] for b in e.get('box', []) if len(b) > 3]
            if delays:
                last = max(delays) + T['BOX_DUR']
                check(e['rec'] >= last - 1e-9,
                      f'{label}: last box lives to {last:.2f}s but recovery is only '
                      f'{e["rec"]:.2f}s — the move is free after it ends')

    # ---- 2. is the table REACHABLE? the check the old file could not make --------
    for tname, shape in (('DIR_MOVES', T['moveKeyShape']),
                         ('DIR_SPECIALS', T['specialKeyShape'])):
        entries = [k for k in REACHED if k.startswith(tname + ' ')]
        landed = [k for k in entries if REACHED[k].get('art')
                  and REACHED[k]['art'] == T[tname][k.split(' ', 1)[1]].get('art')]
        if tname in KNOWN_UNREACHABLE:
            notes.append(f'{tname}: {len(landed)}/{len(entries)} entries reachable — '
                         f'lookup key is `{shape}`. KNOWN: {KNOWN_UNREACHABLE[tname]}')
            continue
        check(landed, f'{tname} IS DEAD — the engine looks it up as `{shape}`, and firing '
                      f'every one of its {len(entries)} inputs produced none of its arts. '
                      f'Every move in this table is unreachable and its cells are wasted.')
        for k in entries:
            want = T[tname][k.split(' ', 1)[1]].get('art')
            got = REACHED[k].get('art')
            check(got == want,
                  f'{k}: table authors art "{want}" but firing that input drew "{got}"')

    # ---- 3. behaviour the old file asserted on prose -----------------------------
    check(B['rollSurvivesJump'],
          'jump CANCELS the roll — the recovery tail can be skipped, so the roll is free. '
          '(the old checker tested for the absence of a source COMMENT)')
    check(B['tookRiposte'] and not B['tookSlip'],
          f'during blockstun with guard held, Heavy gave slip={B["tookSlip"]} '
          f'riposte={B["tookRiposte"]} — the slip is eating the riposte, which is the one '
          f'moment the riposte exists')
    check(not B['staleStabAfterCounter'],
          'a counter inherited the previous move\'s stabAnim latch — it will draw the '
          'DRIVE STAB instead of its own art')

    # ---- 4. manifest facts: data questions, answered from data -------------------
    for name, frames in manifests.items():
        check('roll' in frames, f'{name}: no "roll" cell — the dodge roll would draw `jump`')
    for key in ('xiai1', 'xiai2', 'xiai3', 'xiai4', 'xiai5', 'xlow1', 'xlow5'):
        check(key in manifests.get('executioner', {}),
              f'executioner placeholder cell "{key}" is referenced but not in the sheet')
    check(any('DO_NOT_USE' in k for k in manifests.get('executioner', {})),
          'executioner: the cell-54 tombstone lost its DO_NOT_USE marker — it is a '
          'headless fragment. Do NOT wire or "fix" it.')
    check(T['ROLL_RECOVER'] > 0, 'ROLL_RECOVER is 0 — the roll has no punish window')
    check(T['ROLL_SPEED'] * T['ROLL_TIME'] > 60,
          'the roll travels too little to cross a body')

    # ---- 5. dark cells: TWO SIGNALS, runtime authoritative ----------------------
    # A cell the sweep never drew is not automatically dark — the sweep is directed, and
    # it cannot reach throws, wall states, KO or projectile paths. So "never drawn" alone
    # is a COVERAGE GAP, reported as a note.
    #
    # It only becomes a FAILURE when the source does not mention the key either. Runtime
    # says "I could not reach it"; the text says "nothing even names it". Together those
    # mean dark. That is strictly stronger than the old checker, which had only the text
    # signal and therefore passed `airthrow` — named in a table nothing can look up.
    src = '\n'.join(l for l in (REPO / 'web/index.html').read_text().split('\n')
                    if len(l) < 3000)          # drop the prose changelog: it names every
                                               # key ever packed, so it answers yes to all
    import re as _re

    def named(key):
        base = _re.sub(r'_?\d+$', '', key)
        if base in CONSTRUCTED:
            return True
        return bool(_re.search(r'\b' + _re.escape(key) + r'\b', src)
                    or (base != key and _re.search(r"['\"]" + _re.escape(base) + r"['\"]", src)))

    total_cells = uncovered = 0
    gap_families = {}
    for name, frames in manifests.items():
        live = set(drawn.get(name, []))
        by_cell = {}
        for k, c in frames.items():
            if isinstance(c, int):
                by_cell.setdefault(c, []).append(k)
        for c, ks in sorted(by_cell.items()):
            total_cells += 1
            if c in live:
                continue
            if all('_old' in k or 'DO_NOT_USE' in k
                   or _re.search(r'_v\d+$', k) for k in ks):
                continue
            if any((name, k) in KNOWN_DARK for k in ks):
                continue
            if any(named(k) for k in ks):
                uncovered += 1
                fam = _re.sub(r'_?\d+$', '', sorted(ks)[0])
                gap_families[fam] = gap_families.get(fam, 0) + 1
                continue
            fails.append(f'{name}: cell {c} ({",".join(sorted(ks))}) is packed, was never '
                         f'DRAWN by any state or input, and NO source line names it — '
                         f'nothing can reach it. Wire it, retire it as *_old, or add it '
                         f'to KNOWN_DARK with a reason')

    print(f'checked {n_entries} table entries as live objects · '
          f'{len(manifests)} sheets · {total_cells} cells against what the game drew')
    drew = sum(len(v) for v in drawn.values())
    print(f'the sweep DREW {drew} distinct cells — 16 forced states x 2 stances, plus '
          f'every attack input ground and air, base and mode')
    if uncovered:
        top = sorted(gap_families.items(), key=lambda kv: -kv[1])[:8]
        print(f'coverage gap: {uncovered} cells are NAMED in source but the directed '
              f'sweep never reached them. Not failures — the sweep cannot drive throws, '
              f'wall states, KO or projectile paths. Biggest families: '
              + ', '.join(f'{k}({n})' for k, n in top))
    for n in notes:
        print(f'  note: {n}')
    if fails:
        print(f'\n{len(fails)} FAILED:')
        for f in fails:
            print('  -', f)
        return 1
    print('\nall good')
    return 0


if __name__ == '__main__':
    sys.exit(main())
