#!/usr/bin/env python3
"""Which sign does the fighter BODY get mirrored by, frame by frame, around a wall cling?

Reads the engine's own `onWall` expression on the real player object, through a wall
contact the engine established itself. Three questions, one run:

  EDGE    does the sign differ on the contact frame vs the settled cling?
          (state is written at the TOP of applyPhysics from LAST frame's wallDir, and
           wallDir at the BOTTOM of the same function — so they are one frame out of
           phase on every transition)
  ATTACK  does the sign differ while attacking on the wall?
          (`onWall` needs state===WALL_CLING, but an attack replaces the state while
           wallDir stays set)
  RELEASE does the sign differ on the frame the wall is let go?

  python3 tools/check_wall_mirror.py                       # grades :9100
  SHADOWCLASH_URL=http://localhost:9101/index.html python3 tools/check_wall_mirror.py
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from watch_game import drive  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
OUT = REPO / 'media/audit/wall-mirror'

# ⛔ THE PROBE RE-STATES THE ENGINE'S EXPRESSION, SO IT CAN DRIFT AWAY FROM IT AND KEEP
# PASSING. That is the failure mode this repo has hit twice — `attackAir` made the DEAD
# branch unfirable and "0 dead inputs" was arithmetic, not a measurement. So the copy is
# pinned to the source: lift the real `const onWall = ...` out of index.html and refuse
# to run if it is not the string the probe encodes. Change the engine and this fails
# loudly with both versions printed, instead of grading a rule that no longer ships.
ONWALL_IN_PROBE = 'p.wallDir !== 0 || p.state === STATE.WALL_CLING'


def assert_probe_matches_engine():
    src = (REPO / 'web/index.html').read_text()
    m = re.search(r'const onWall\s*=\s*(.*?);', src, re.S)
    if not m:
        sys.exit('⛔ no `const onWall = ...` in web/index.html — the draw path moved; '
                 'find it and re-pin ONWALL_IN_PROBE.')
    engine = ' '.join(m.group(1).split())
    if engine != ONWALL_IN_PROBE:
        sys.exit('⛔ THIS CHECK IS STALE — it would grade a rule the engine no longer uses.\n'
                 f'   engine: {engine}\n'
                 f'   probe : {ONWALL_IN_PROBE}\n'
                 '   Update ONWALL_IN_PROBE and the `const onWall` line inside PROBE together.')
    return engine


PROBE = r'''
const p = player1, q = player2;
q.x = 700;                                   // opponent far away, out of the way
const rows = [];
// The exact expression at index.html:11884, evaluated on the live object.
const sample = (tag) => {
  const onWall = p.wallDir !== 0 || p.state === STATE.WALL_CLING;
  rows.push({ tag, state: Object.keys(STATE).find(k => STATE[k] === p.state),
              wallDir: p.wallDir, facing: p.facing,
              onWall, sx: onWall ? p.facing : -p.facing });
  return rows[rows.length - 1];
};
const frame = () => new Promise(r => requestAnimationFrame(() => r()));
// getInputAxis() reads the PREFIXED alias always, and raw KeyA only when
// usesRawKeys() && isP1 — so hold both rather than assume which path is live.
const LEFT = p.getPrefix() + 'left';
const hold = (v) => { keys[LEFT] = v; keys['KeyA'] = v; };
const pin = () => { p.x = 10; p.y = 200; p.vy = 0; p.isGrounded = false; hold(true); };

for (const k in keys) keys[k] = false;

// --- reach the wall: airborne, at the left wall, holding INTO it (index.html:4001)
let contactAt = -1;
for (let i = 0; i < 60; i++) {
  pin(); await frame(); pin();
  if (p.wallDir !== 0) { contactAt = i; break; }
}
if (p.wallDir === 0) {
  hold(false);
  // report WHY, rather than just that it failed — index.html:4001 needs all four
  return { error: 'never reached the wall', why: {
    x: p.x, y: p.y, isGrounded: p.isGrounded, stunTimer: p.stunTimer,
    inputAxis: p.inputAxis, axisFn: p.getInputAxis ? p.getInputAxis() : null,
    keyA: keys['KeyA'], leftAlias: LEFT, rawKeys: p.usesRawKeys(), isP1: p.isP1,
    roundIntro: typeof roundIntroTimer !== 'undefined' ? roundIntroTimer : null,
    state: Object.keys(STATE).find(k => STATE[k] === p.state) } };
}

// the contact frame itself, then four more so `state` can catch up to `wallDir`
const edge = sample('edge.contact');
for (let i = 0; i < 4; i++) { pin(); await frame(); pin(); sample('settle.' + i); }
const cling = sample('cling.settled');

// --- attack while still pinned to the wall
p.stamina = 100; p.chakra = 100;
p.executeAttack(STATE.ATTACK_HEAVY);
const atk = [];
for (let f = 0; f < 24; f++) { pin(); await frame(); pin(); atk.push(sample('attack.' + f)); }

// --- let go of the wall
hold(false);
const rel = [];
for (let f = 0; f < 4; f++) {
  p.x = 10; p.y = 200; p.isGrounded = false;
  await frame(); rel.push(sample('release.' + f));
}

// --- LAND from the cling. This is the regression risk of widening `onWall` to an OR:
// if STATE.WALL_CLING survives even one frame after touchdown, a GROUNDED fighter would
// now draw at +facing (backwards) where the old && test drew him correctly.
p.x = 400; p.y = GROUND_Y - p.height; p.vy = 40;
const land = [];
for (let f = 0; f < 8; f++) {
  await frame();
  const onWallNow = p.wallDir !== 0 || p.state === STATE.WALL_CLING;
  land.push({ f, grounded: p.isGrounded, wallDir: p.wallDir,
              state: Object.keys(STATE).find(k => STATE[k] === p.state),
              onWall: onWallNow });
}
const groundedOnWall = land.filter(r => r.grounded && r.onWall);

const atkFlipped = atk.filter(r => r.sx !== cling.sx);
const relFlipped = rel.filter(r => r.sx !== cling.sx && r.state === 'WALL_CLING');
return {
  fighter: p.spec.name,
  clingSx: cling.sx, clingState: cling.state,
  edgeSx: edge.sx, edgeState: edge.state, edgeFlipped: edge.sx !== cling.sx,
  attackFlipped: atkFlipped.length, attackTotal: atk.length,
  attackStates: [...new Set(atkFlipped.map(r => r.state))],
  releaseStaleClingFlipped: relFlipped.length,
  groundedOnWall: groundedOnWall.length, landRows: land,
  rows,
};
'''

PRELOAD = r'''
const want = [0,1,2,3,4,5].map(i => NINJA_ROSTER[i]).filter(n => n && !SPRITES[n.name.toLowerCase()]);
await Promise.all(want.map(async n => {
  const key = n.name.toLowerCase();
  const man = await (await fetch(`assets/sprites/${key}.json?v=${SHEET_V}`)).json();
  await new Promise((res, rej) => {
    const img = new Image();
    img.onload = () => { man.img = img; man.ready = true; SPRITES[key] = man; res(); };
    img.onerror = rej; img.src = `assets/sprites/${key}.png?v=${SHEET_V}`;
  });
}));
return Object.keys(SPRITES).join(',');
'''

steps = [{"wait": 1.2}, {"key": "Space"}, {"wait": 0.5},
         {"eval": "gameMode='2p';cpuMode=false;p1Pick=0;p2Pick=1;stagePick='bamboo';"
                  "attractMode=false;startNewGame();roundIntroTimer=0;return 1", "label": "boot"},
         {"wait": 2.2},
         {"eval": PRELOAD, "label": "preload"},
         {"wait": 1.5},
         {"eval": PROBE, "label": "WALL"}]

print(f'grading  onWall = {assert_probe_matches_engine()}\n')
d = drive(steps, OUT, "WALL")
if d.get('error'):
    sys.exit('probe never established wall contact: ' + d['error']
             + '\n' + json.dumps(d.get('why'), indent=1))

(OUT / 'rows.json').write_text(json.dumps(d['rows'], indent=1))
print(f"{d['fighter']}: settled cling draws at sx={d['clingSx']} (state {d['clingState']})\n")

bad = 0
print(f"  EDGE     contact frame state={d['edgeState']:<12} sx={d['edgeSx']:+d}   "
      f"{'⛔ FLIPPED vs the cling' if d['edgeFlipped'] else 'ok'}")
bad += d['edgeFlipped']
print(f"  ATTACK   {d['attackFlipped']}/{d['attackTotal']} frames flipped   "
      f"{'⛔ states: ' + ','.join(d['attackStates']) if d['attackFlipped'] else 'ok'}")
bad += d['attackFlipped'] > 0
print(f"  RELEASE  {d['releaseStaleClingFlipped']} stale-WALL_CLING frames flipped   "
      f"{'⛔' if d['releaseStaleClingFlipped'] else 'ok'}")
bad += d['releaseStaleClingFlipped'] > 0

print(f"  LANDING  {d['groundedOnWall']} grounded frames would draw wall-mirrored   "
      f"{'⛔ REGRESSION — the OR leaks onto the ground' if d['groundedOnWall'] else 'ok'}")
bad += d['groundedOnWall'] > 0
print(f"\nfull frame log: {OUT / 'rows.json'}")
sys.exit(1 if bad else 0)
