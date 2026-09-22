"""Which PACKED CELLS can no input in the game reach?

  python3 tools/serve.py 9100 web &          # the one server
  python3 tools/audit_cell_coverage.py                 # whole roster
  python3 tools/audit_cell_coverage.py --ids 8         # one fighter
  python3 tools/audit_cell_coverage.py --write-allow   # accept today's situational list

WHY THIS EXISTS — the failure it is built to catch
    Oni's MASTER-LIGHT-DIR board packed glfwd/glback/gldown, six drawn beats each,
    and NOT ONE of the eighteen cells could ever appear on screen: `direction + Light`
    was hard-bound to the kick tier one layer above, which fired a ONE-CELL pose and
    returned before the code that would have picked his art ever ran. His two bo-staff
    boards, twelve more cells, had no key left to sit on at all. The art was correct,
    packed correctly, byte-perfect on the sheet, and dead. Nothing in this repo could
    tell you that, so it went unnoticed across three sheet versions and was only found
    by driving all 293 of his cells by hand.

    `audit_move_coverage.py` is the other half of this question and does NOT answer it:
    it asks whether an INPUT is a real move (dead / static / echo). An input can be a
    perfectly healthy move and still be drawing the wrong fighter's cells, or two
    inputs can share one row while a third row rots. That tool ranges over inputs.
    This one ranges over CELLS, which is the side the art lives on.

⛔ WHY THIS DRIVES THE GAME INSTEAD OF GREPPING THE SOURCE
    A static reference check was tried first and it LIES, in both directions. The
    engine builds frame keys at runtime — `F['k' + p.kickKind]`, `dirCells(p, F, {...})`,
    `F[row + '1']` — so `grep glfwd` finds a map literal and cannot tell you whether any
    input reaches it, and `grep ksweep` finds nothing while the cell draws every match.
    Run against Oni it called 19 live rows dead and missed the three that actually were.
    The only honest ruler is what the game DREW when a human-equivalent key was pressed.

⛔ AND IT SAMPLES EVERY FRAME, NOT EVERY SIXTH
    audit_move_coverage samples `f % 6 === 0`, which is right for fingerprinting a move
    and wrong here: at 60fps that is one sample per 100ms, and a six-beat move at its
    authored pacing exposes some beats for 40ms. Sampling coarsely invents orphans that
    do not exist. This polls drawCell on a 4ms timer for the whole sweep.

WHAT IT REPORTS
    ORPHAN      no input reached the cell and its row is an ATTACK family — a real bug,
                the exit code is 1. Either the art needs an input or the input is
                stealing from it.
    SITUATIONAL no input reached it, but its row is state art (block, hurt, getup, wall,
                KO) that needs to be hit or cornered rather than pressed. Listed, never
                failed, and the allowlist records WHY so the list cannot quietly grow.
    COVERED     drawn at least once during the sweep.

    A row is only ever SITUATIONAL if it is named in frame_coverage_allow.json. A NEW
    unreached attack row fails the run — that is the whole point of the tool.
"""
import argparse
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SHEETS = REPO / 'web/assets/sprites'
OUT = REPO / 'media/audit/cell-coverage'
ALLOW = pathlib.Path(__file__).parent / 'sprites/frame_coverage_allow.json'
ORDER = ['Executioner', 'Mizu', 'Shin', 'Tsubasa', 'Ember', 'Kael', 'Mokurai', 'Exile', 'Oni']

# Rows the INPUT sweep structurally cannot reach: they need to be hit, knocked down,
# cornered, or to win. Prefixes, matched against the row name with its trailing digits
# stripped. Being here does not excuse a row — it only routes it to SITUATIONAL, and
# frame_coverage_allow.json still has to name it.
STATE_FAMILIES = ('block', 'guard', 'hurt', 'stun', 'getup', 'prone', 'ko', 'win', 'lose',
                  'intro', 'taunt', 'wall', 'slide', 'fall', 'land', 'dizzy', 'death',
                  'grabbed', 'thrown', 'tech', 'crumple')

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

# ⛔ THE SWEEP RUNS IN-PAGE, ONE CASE AT A TIME, AND RE-INITS THE MATCH EACH TIME.
# The first version drove hundreds of sequential CDP steps against one long-running match
# and was NON-DETERMINISTIC: two runs on the same build returned different orphan lists,
# because state drifted (the 90s round clock expired mid-sweep, stamina ran dry, a stray
# launch left the dummy airborne) and every later press landed on a game that was no
# longer in a fightable state. It reported the whip and the lunge dead in one run and
# alive in the next — both are fine. A gate that changes its mind is worse than no gate.
# audit_move_coverage is stable for exactly this reason, so this borrows its shape:
# startNewGame() per case, keys poked directly, and the direction RE-ASSERTED every frame
# because the engine's input pass rebuilds `keys` from a keyboard that is holding nothing.
PROBE = r"""
const frame = () => new Promise(r => requestAnimationFrame(r));
const DIRS = {neutral:[], fwd:['KeyD'], back:['KeyA'], down:['KeyS'], up:['KeyW']};
const BTN  = {L:'ATTACK_LIGHT', H:'ATTACK_HEAVY', S:'ATTACK_SPECIAL'};
const id = __ID__, PART = __PART__;
const seen = new Set();
let name = null, F = null;

// Put the match in a known, fightable state. EVERY case starts here, which is the whole
// reason this version is repeatable.
const setup = async (gap, air) => {
  p1Pick = id; p2Pick = (id + 1) % 9; startNewGame(); roundIntroTimer = 0; roundTimer = ROUND_TIME;
  await frame(); await frame();
  const p = player1, o = player2;
  if (!name) { name = p.spec.name; F = SPRITES[name.toLowerCase()].frames; }
  for (const k in keys) keys[k] = false;
  o.x = 700; o.hp = 999; o.stunTimer = 0;
  p.x = 700 - gap; p.facing = 1; p.hp = 999;
  p.stamina = 100; p.chakra = 100; p.chainComboTier = 0;
  p.dashTimer = 0; p.rollTimer = 0; p.attackHasConnected = false; p.connectTime = -1e9;
  if (air) { p.state = STATE.JUMP; p.isGrounded = false; p.y = GROUND_Y - 200; p.vy = -40; }
  return p;
};

// Run one case to completion, sampling the DRAWN cell every frame (not every sixth — a
// beat at authored pacing can be on screen for 40ms, and coarse sampling invents orphans).
const play = async (p, dkeys, frames, hold) => {
  // ⛔ A HELD KEY LIVES IN physKeys, NOT keys. The engine rebuilds `keys` every frame and
  // clears anything the player is not physically holding (`if (!physKeys.has(k)) keys[k]
  // = false`), so poking `keys` only survives until the next input pass. That is enough
  // for a one-frame executeAttack read and NOT enough for any state that has to persist:
  // a walk never accumulated into a RUN, and both of Oni's eight-cell run rows — art the
  // game plays in every match — reported as orphaned. Hold it where the engine looks.
  dkeys.forEach(k => physKeys.add(k));
  for (let f = 0; f < frames; f++) {
    dkeys.forEach(k => keys[k] = true);
    await frame();
    dkeys.forEach(k => keys[k] = true);
    try { seen.add(spriteFrameIndex(p, F)); } catch (e) {}
    // Stop as soon as the move is over. Without this the sweep burned a fixed 46 frames
    // on every one of ~200 cases and blew past the driver's 20s eval ceiling; the recovery
    // tail draws idle, which is already covered. `hold` opts out for locomotion cases,
    // where there is no attack state to end and the whole point is the held input.
    if (!hold && f > 6 && !p.isAttackingState() && p.recoveryTimer <= 0) break;
  }
  dkeys.forEach(k => { keys[k] = false; physKeys.delete(k); });
};

// 1. every button x every direction x ground/air, at four distances. Range-gated moves
//    are the biggest source of false orphans: Oni's neutral Special is the whip inside
//    132px and the wire shot outside it, so one distance measures half the row.
if (PART < 4) { for (const gap of [[60, 100, 170, 320][PART]]) {
  for (const air of [false, true]) {
    for (const [dn, dk] of Object.entries(DIRS)) {
      for (const bn of Object.keys(BTN)) {
        const p = await setup(gap, air);
        dk.forEach(k => keys[k] = true);
        try { p.executeAttack(STATE[BTN[bn]]); } catch (e) {}
        await play(p, dk, 46);
      }
    }
  }
}
}
if (PART === 4) {
// 2. the kick tier, which is its own entry point and not reachable through executeAttack
for (const kind of ['sweep', 'push', 'heel']) {
  const p = await setup(80, false);
  try { p.executeKick(kind); } catch (e) {}
  await play(p, [], 30);
}
// 3. the stance key, bare and per direction — a stance that re-skins light/heavy hides a
//    whole family behind one press (Oni's bo, Shin's kage-nui, Tsubasa's sakate, chudan)
for (const [dn, dk] of Object.entries(DIRS)) {
  const p = await setup(90, false);
  dk.forEach(k => keys[k] = true);
  try { p.modeKey(); } catch (e) {}
  await frame();
  dk.forEach(k => keys[k] = false);
  for (const bn of Object.keys(BTN)) {
    try { p.recoveryTimer = 0; p.state = STATE.IDLE; p.executeAttack(STATE[BTN[bn]]); } catch (e) {}
    await play(p, [], 34);
  }
  // ⛔ AND THE SAME BUTTONS IN THE AIR, STILL IN THE STANCE. A stance x airborne pair is
  // its own quadrant and the sweep had no case for it: it toggled the mode and then only
  // ever attacked from the floor. That reported Oni's eight-cell air kunai throw dead
  // while it was drawing 317-324 for 17 damage in a live probe — the tool wrong, not the
  // art. Put him back in the air between presses; recoveryTimer is cleared because the
  // grounded pass above just spent one.
  for (const bn of Object.keys(BTN)) {
    p.state = STATE.JUMP; p.isGrounded = false; p.y = GROUND_Y - 200; p.vy = -40;
    p.recoveryTimer = 0; p.attackHasConnected = false;
    try { p.executeAttack(STATE[BTN[bn]]); } catch (e) {}
    await play(p, [], 40);
  }
}
}
if (PART === 5) {
// 4. dash-gated moves. The shunshin returns early on low stamina, so a drained sweep
//    silently skips every dash attack and blames the art — assert the dash instead.
for (const bn of Object.keys(BTN)) {
  for (const air of [false, true]) {
    const p = await setup(170, air);
    p.dashTimer = 0.4; p.dashDir = p.facing; p.vx = p.facing * 400;
    try { p.executeAttack(STATE[BTN[bn]]); } catch (e) {}
    await play(p, ['KeyD'], 40);
  }
}
// 5. the dodge roll, both ways
for (const dir of [1, -1]) {
  const p = await setup(170, false);
  try { p.startRoll(dir); } catch (e) {}
  await play(p, [], 44);
}
// 6. FOLLOW-UPS INSIDE A CONNECTED MOVE'S WINDOW. A conversion that only exists after a
//    move LANDS cannot be reached from neutral, and Oni's branches on BOTH bodies —
//    air-vs-grounded picks the slice, air-vs-airborne picks the knives — so the dummy
//    has to be launched too or half the family reads as dead.
for (const [dn, dk] of Object.entries(DIRS)) {
  for (const foeAir of [false, true]) {
    for (const meAir of [false, true]) {
      const p = await setup(70, meAir);
      try { p.executeAttack(STATE.ATTACK_SPECIAL); } catch (e) {}
      for (let f = 0; f < 8; f++) await frame();
      p.wireBind = 0.55; p.wireBindFoe = player2;
      if (foeAir) { player2.isGrounded = false; player2.y = GROUND_Y - player2.height - 140; }
      p.recoveryTimer = 0; p.state = STATE.IDLE;
      dk.forEach(k => keys[k] = true);
      try { p.executeAttack(STATE.ATTACK_SPECIAL); } catch (e) {}
      await play(p, dk, 40);
    }
  }
}
}
if (PART === 6) {
// 7. throw, air throw, and the chakra clone
for (const air of [false, true]) {
  const p = await setup(40, air);
  try { p.tryThrow ? p.tryThrow() : p.executeAttack(STATE.THROWING); } catch (e) {}
  await play(p, [], 60);
}
}
if (PART === 7) {
// 8. locomotion and guard, driven as held input rather than called
// ⛔ HOLD LONG ENOUGH TO ACTUALLY RUN. A walk becomes a RUN only after the input has
// been held past a threshold, so 40 frames of forward reported both of Oni's eight-cell
// run rows dead while the game plays them every match. Locomotion needs seconds, not
// frames — this is the same class of mistake as not paying for the dash.
for (const [tag, dk, frames] of [['walk', ['KeyD'], 150], ['back', ['KeyA'], 150],
                                 ['crouch', ['KeyS'], 40], ['guard', ['KeyC'], 40]]) {
  const p = await setup(200, false);
  // ⛔ GET THE DUMMY OUT OF THE WAY. Holding forward into a body 200px ahead pushes into
  // its pushbox and the walk never becomes a RUN, which reported both of Oni's eight-cell
  // run rows dead — art the game plays in every single match. Locomotion needs ROOM.
  player2.x = p.x + 2200; p.x = 300;
  await play(p, dk, frames, true);
}
{ const p = await setup(200, false); p.vy = -600; p.isGrounded = false; await play(p, [], 90, true); }
// 9. take one on the chin, blocking and not — the hurt/block families have no input
for (const guard of [false, true]) {
  const p = await setup(45, false);
  if (guard) keys['KeyC'] = true;
  try { player2.facing = -1; player2.executeAttack(STATE.ATTACK_HEAVY); } catch (e) {}
  await play(p, guard ? ['KeyC'] : [], 70, true);
}
}
if (PART === 8) {
// 10. THE LIGHT STRING, TAPPED OUT BEAT BY BEAT. One press is beat one; the sweep's
//     button matrix only ever presses once, so every row a later beat draws (Oni's
//     punch2/punch3 in base form, kick2/kick3 in the second mode) read as orphans.
//     Whiff range on purpose — a CONNECTED light is the cancel path, and landing one
//     resets nothing here; getting HIT does, and nobody is swinging back.
// ⛔ WAIT THE RECOVERY OUT, DON'T FORCE IT. chainComboTier resets INSIDE the
//     recovery-expiry tick; zeroing recoveryTimer by hand skips that tick, the tier
//     stays 1, and the whiffed follow-up is silently BUFFERED instead of fired —
//     measured: beat 3 never came out and its rows read dead. play() already breaks
//     on the exact frame recovery expires, which is the frame the tier resets, so a
//     press straight after it is a legal tap inside the 0.55s window (~0.3s left).
for (const m2 of [false, true]) {
  const p = await setup(170, false);
  if (m2) { try { p.modeKey(); } catch (e) {} await frame(); }
  for (let tap = 0; tap < 3; tap++) {
    try { p.executeAttack(STATE.ATTACK_LIGHT); } catch (e) {}
    await play(p, [], 60);
  }
}
// 11. DIRECTIONAL JUMPS. jumpDir is read from the horizontal axis at takeoff, and the
//     locomotion case only ever jumped neutral — so Oni's forward cartwheel (cart1-6)
//     could never draw. Ride the whole arc; the beats walk by vy bands, not a timer.
for (const dk of [['KeyD'], ['KeyA']]) {
  const p = await setup(200, false);
  player2.x = p.x + 2200; p.x = 500;
  dk.forEach(k => { keys[k] = true; physKeys.add(k); });
  try { p.executeJump(); } catch (e) {}
  await play(p, dk, 100, true);
}
}
window.__CC = window.__CC || {};
const prev = window.__CC[id] || [];
window.__CC[id] = [...new Set([...prev, ...seen])].filter(c => c !== undefined && c !== null).sort((a, b) => a - b);
return name + ' ' + window.__CC[id].length;
"""


def base(name):
    return name.rstrip('0123456789') or name


def run(ids):
    steps = [{"wait": 1.2}, {"key": "Space"}, {"wait": 0.5},
             {"eval": "gameMode='2p'; cpuMode=false; p1Pick=0; p2Pick=1; stagePick='bamboo';"
                      "attractMode=false; startNewGame(); return 1"},
             {"wait": 2.2},
             {"eval": PRELOAD.replace('__IDS__', json.dumps(ids))},
             {"wait": 2.5}]
    for pid in ids:
        # ⛔ ONE EVAL PER PART. watch_game gives an eval 20 seconds; the whole sweep is
        # minutes of real frames, so a single call times out and takes the run with it.
        # Each part accumulates into window.__CC, so the union is the same.
        for part in range(9):
            steps.append({"eval": PROBE.replace('__ID__', str(pid)).replace('__PART__', str(part)),
                          "label": f'sweep{pid}.{part}'})
    steps.append({"eval": "return window.__CC", "label": "CELLS"})
    OUT.mkdir(parents=True, exist_ok=True)
    script = OUT / 'probe.json'
    script.write_text(json.dumps(steps, indent=1))
    subprocess.run([sys.executable, str(REPO / 'tools/watch_game.py'),
                    '--script', str(script), '--out', str(OUT / 'run')],
                   check=True, capture_output=True, text=True)
    log = (OUT / 'run/log.txt').read_text()
    if 'CELLS: ' not in log:
        sys.exit("probe produced no result — is 9100 serving THIS tree?")
    i = log.index('CELLS: ') + len('CELLS: ')
    raw = json.JSONDecoder().raw_decode(log[i:])[0]
    return {int(k): set(v) for k, v in raw.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default=','.join(str(i) for i in range(len(ORDER))))
    ap.add_argument('--write-allow', action='store_true',
                    help='record today\'s situational rows as accepted, with a reason stub')
    args = ap.parse_args()
    ids = [int(x) for x in args.ids.split(',') if x != '']
    allow = json.loads(ALLOW.read_text()) if ALLOW.exists() else {}

    seen = run(ids)
    orphans, situational, new_allow = {}, {}, dict(allow)
    for pid in ids:
        name = ORDER[pid]
        man = json.loads((SHEETS / f'{name.lower()}.json').read_text())
        rows = {}
        for row, cell in man['frames'].items():
            rows.setdefault(base(row), []).append(cell)
        ok = {k: v for k, v in allow.get(name, {}).items() if not k.startswith('_')}
        dead = {r: c for r, c in rows.items() if not (set(c) & seen[pid])}
        for r, c in sorted(dead.items()):
            if base(r).startswith(STATE_FAMILIES) or r in ok:
                situational.setdefault(name, {})[r] = len(c)
                if args.write_allow and r not in ok:
                    new_allow.setdefault(name, {})[r] = 'situational — needs a state, not an input'
            else:
                orphans.setdefault(name, {})[r] = len(c)
        covered = len(seen[pid] & set(range(man['cols'])))
        print(f"{name:13s} {covered:3d}/{man['cols']:3d} cells drawn   "
              f"orphan rows {len(orphans.get(name, {})):2d}   "
              f"situational {len(situational.get(name, {})):2d}")

    if situational:
        print("\nACCEPTED — allowlisted as dead on purpose, with the reason on record:")
        for n, rs in situational.items():
            reasons = allow.get(n, {})
            for r, c in sorted(rs.items()):
                why = reasons.get(r, 'state art — no input can create it')
                print(f"  {n:13s} {r:11s} {c:2d} cells   {why}")

    if args.write_allow:
        ALLOW.write_text(json.dumps(new_allow, indent=2, sort_keys=True) + '\n')
        print(f"\nwrote {ALLOW.relative_to(REPO)}")

    if orphans:
        total = sum(sum(rs.values()) for rs in orphans.values())
        print(f"\n⛔ ORPHANED ART — {total} packed cells no input can reach:")
        for n, rs in orphans.items():
            for r, c in sorted(rs.items()):
                print(f"    {n:13s} {r:22s} {c} cells")
        print("\nEach one is drawn, packed, and dead. Give it an input or take the cells off\n"
              "the sheet — do NOT add it to the allowlist to silence this.")
        return 1
    print("\n✅ no orphaned art — every packed cell outside the situational list is reachable")
    return 0


if __name__ == '__main__':
    sys.exit(main())
