// CEREMONY — intro / win / ko. The ways these can be wired and still do nothing.
//
// 1. THE POSE IS NEVER DRAWN. The intro holds STATE.IDLE and the KO holds STATE.STUNNED,
//    so if ceremonyFrame is not consulted before the state switch the stance cell paints
//    straight over both — the same silent failure the taunt has.
// 2. NOTHING EVER SETS IT. `win`/`ko` ride a per-player field, and endRound has THREE
//    mode branches that each `return` on their own. A branch that never calls
//    beginCeremony ends its rounds with nobody posing, and it does not throw.
// 3. THE ROW IS NOT ON THE SHEET, or has a gap. `intro1..N` walks from 1: a hole at any
//    index truncates the row, and index 1 absent means the fighter silently has no pose.
// 4. THE KO PLAYS IN THE AIR. Its last beats are a body lying on the floor. Drawn while
//    the loser is still falling that is a ground frame in the air — the defect the 707
//    air sweep exists to prevent — so the branch must refuse when !isGrounded.
// 5. A DRAW SALUTES, or a time-over loser collapses. `ko` is earned by hp <= 0 and `win`
//    by being on the winning side; w = -1 must hand out no victory pose at all.
//
// Also runs the picker's arithmetic directly, which is the only real logic here: a
// one-shot row must start on beat 1, reach its LAST beat, and never index past it.
import { readFileSync } from 'node:fs';

const ROOT = new URL('../', import.meta.url);
const src = readFileSync(new URL('web/index.html', ROOT), 'utf8');
const NAMES = ['executioner', 'mizu', 'shin', 'tsubasa', 'ember', 'kael', 'mokurai', 'exile', 'oni'];
const ROWS = ['intro', 'win', 'ko'];

const fails = [];
const need = (cond, msg) => { if (!cond) fails.push(msg); };

// --- 1. the draw path --------------------------------------------------------
const raw = src.indexOf('function spriteFrameIndexRaw');
const call = src.indexOf('ceremonyFrame(p, F)', raw);
const stateSwitch = src.indexOf('switch (p.state) {', raw);
need(raw > 0 && call > raw && (stateSwitch < 0 || call < stateSwitch),
  'ceremonyFrame is not consulted before the state switch — the stance cell paints over the pose');
need(/const ceremony = ceremonyFrame\(p, F\);\s*\n\s*if \(ceremony !== undefined\) return ceremony;/.test(src),
  'ceremonyFrame is called but its result is not returned');

// --- 2. something sets it ----------------------------------------------------
need(/function beginCeremony\(w\)/.test(src), 'beginCeremony is missing');
const er = src.indexOf('function endRound()');
need(er > 0, 'endRound not found');
const body = src.slice(er, src.indexOf('\n        function ', er + 20));
const calls = (body.match(/beginCeremony\(/g) || []).length;
need(calls === 3,
  `endRound calls beginCeremony ${calls}x — it has three mode branches (brawl, tag, 1v1) `
  + 'that each return on their own, so each needs its own call');
need(/this\.ceremony = null;/.test(src), 'Player never initialises `ceremony`');

// --- 5. who earns which pose -------------------------------------------------
need(/q\.hp <= 0\s*\?\s*\{ row: 'ko'/.test(src),
  "the ko pose is not gated on hp <= 0 — a time-over loser would collapse while still standing");
need(/\(w >= 0 && side === w\)\s*\?\s*\{ row: 'win'/.test(src),
  'the win pose is not gated on the winning side — a draw (w = -1) would salute');

// --- 4. every pose stays on the floor ----------------------------------------
// This branch sits above the whole state switch, so an unguarded pose shadows any art
// the body is actually using. The intro doing exactly that to Shin's and Tsubasa's
// airborne held poses is why check_air_held_poses is a sibling of this file.
need(/ceremony\.row === 'ko' \? !p\.isGrounded : !standingStill\(p\)\) return undefined;/.test(src),
  'the ko row is not grounded-gated (or win lost its standing gate) — floor art would draw mid-fall');
need(/function ceremonyBusy\(p\) \{\s*\n\s*return p\.isAttackingState\(\) \|\| p\.grabbedBy/.test(src),
  'ceremonyBusy does not yield to an attacking or grabbed body');
need(/function standingStill\(p\) \{ return p\.isGrounded && !ceremonyBusy\(p\); \}/.test(src),
  'standingStill does not require a grounded, non-busy body');
need(/if \(!c\.length \|\| ceremonyBusy\(p\)\) return undefined;/.test(src),
  'the intro is not gated on ceremonyBusy — it shadows mid-move art');
// ⛔ AND THE INTRO MUST NOT TEST isGrounded. updateGame is gated on roundIntroTimer <= 0,
// so no physics runs during the intro and every fighter sits at spawn with isGrounded
// false — a ground test there is not a safety check, it is an off switch. Measured: the
// row drew xidle1 for all 90 intro frames the one time it was wired that way.
need(/if \(!matchActive \|\| paused \|\| roundIntroTimer > 0/.test(src),
  'the input lock on roundIntroTimer is gone — the intro can no longer assume a still body');
const cf = src.slice(src.indexOf('function ceremonyFrame'), src.indexOf('function spriteFrameIndexRaw'));
const introArm = cf.slice(0, cf.indexOf("if (!p.ceremony)"));
need(!/isGrounded/.test(introArm),
  'the intro arm tests isGrounded — physics is frozen during the intro, so it would never draw');

// --- 3. the art --------------------------------------------------------------
const carried = {};
for (const n of NAMES) {
  let man;
  try { man = JSON.parse(readFileSync(new URL(`web/assets/sprites/${n}.json`, ROOT), 'utf8')); }
  catch { continue; }                                   // not every name has a sheet here
  const F = man.frames;
  for (const row of ROWS) {
    const keys = Object.keys(F).filter(k => new RegExp(`^${row}\\d+$`).test(k));
    if (!keys.length) continue;                         // no art is a valid state, not a fault
    (carried[row] ||= []).push(n);
    let run = 0;
    while (F[row + (run + 1)] !== undefined) run++;
    need(run === keys.length,
      `${n}: ${row} has ${keys.length} keys but only ${run} are reachable from ${row}1 — there is a GAP`);
    for (let i = 1; i <= run; i++) {
      const c = F[row + i];
      need(Number.isInteger(c) && c >= 0 && c < man.cols,
        `${n}: ${row}${i} = ${c} is not a cell on a ${man.cols}-cell sheet`);
    }
  }
}
for (const row of ROWS)
  need((carried[row] || []).length > 0, `not one sheet carries a \`${row}\` row — it can never fire`);

// --- the picker's arithmetic, run for real -----------------------------------
const INTRO_TIME = Number((src.match(/const INTRO_TIME = ([\d.]+)/) || [])[1]);
const CEREMONY_TIME = Number((src.match(/const CEREMONY_TIME = ([\d.]+)/) || [])[1]);
need(INTRO_TIME > 0, 'INTRO_TIME is missing or not positive');
need(CEREMONY_TIME > 0, 'CEREMONY_TIME is missing or not positive');
const oneShot = (cells, t) => cells[Math.min(cells.length - 1, Math.floor(Math.max(0, t) * cells.length))];
for (const n of [1, 4, 6, 8, 12, 16]) {
  const cells = Array.from({ length: n }, (_, i) => i);
  const seen = new Set();
  for (let k = 0; k <= 480; k++) seen.add(oneShot(cells, k / 480));
  need(oneShot(cells, 0) === 0, `${n}-beat row does not start on beat 1`);
  need(oneShot(cells, 1) === n - 1, `${n}-beat row indexes past its end at t = 1`);
  need(oneShot(cells, 5) === n - 1, `${n}-beat row does not HOLD its last beat past the end`);
  need(oneShot(cells, -0.2) === 0, `${n}-beat row indexes below zero before it starts`);
  need(seen.size === n, `${n}-beat row only reaches ${seen.size} of its ${n} beats`);
}
// The intro's own clock: roundIntroTimer counts 1.5 -> 0, and the row must have played
// through by the time FIGHT! shows at 0.55, then hold.
const introAt = t => oneShot([0, 1, 2, 3, 4, 5, 6, 7], (1.5 - t) / INTRO_TIME);
need(introAt(1.5) === 0, 'the intro does not start on beat 1 when the round opens');
need(introAt(0.55) === 7, 'the intro has not reached its last beat by FIGHT!');
need(introAt(0.0001) === 7, 'the intro does not hold its last beat through FIGHT!');

if (fails.length) {
  console.error(`CEREMONY — ${fails.length} failure${fails.length > 1 ? 's' : ''}:`);
  for (const f of fails) console.error('  ' + f);
  process.exit(1);
}
const say = r => `${r}: ${(carried[r] || []).join(', ') || 'nobody'}`;
console.log('OK — intro/win/ko draw above the state switch, all three endRound branches set the '
  + 'pose, a draw salutes nobody, the ko row refuses to draw airborne, and a 1/4/6/8/12/16-cell '
  + `row plays every beat once and holds the last. Art: ${ROWS.map(say).join('  |  ')}.`);
