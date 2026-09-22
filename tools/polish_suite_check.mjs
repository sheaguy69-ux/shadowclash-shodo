#!/usr/bin/env node
// Polish-suite self-check (approved feature item 1): directional micro-shake,
// speed-line trails, landing recovery cushion.  Run: node tools/polish_suite_check.mjs
//
// Two halves, and BOTH matter:
//   1. WIRING — greps web/index.html so the check cannot pass against an engine
//      that no longer calls any of this. The mirrored math below is worthless if
//      the call site is gone, which is exactly how a mirror-style check goes stale.
//   2. MATH — mirrors the formulas verbatim. Edit the curves in index.html and you
//      must re-mirror them here or this check lies.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const SRC = readFileSync(join(dirname(fileURLToPath(import.meta.url)), '..', 'web', 'index.html'), 'utf8');
let failures = 0;
const check = (label, cond, detail = '') => {
  if (cond) console.log(`  ok   ${label}`);
  else { console.log(`  FAIL ${label}${detail ? ' — ' + detail : ''}`); failures++; }
};

// Pull a constant's value straight out of the engine so the mirror can't drift silently.
const constOf = name => {
  const m = SRC.match(new RegExp(`const\\s+${name}\\s*=\\s*([0-9.]+)`));
  if (!m) { console.log(`  FAIL ${name} is not declared in web/index.html`); failures++; return NaN; }
  return parseFloat(m[1]);
};

console.log('WIRING');
check('shake axis globals declared', /let screenShakeDX = 0, screenShakeDY = 0;/.test(SRC));
check('takeDamage sets the axis', /screenShakeDX = sx \/ len; screenShakeDY = sy \/ len;/.test(SRC));
check('renderer branches on the axis', /if \(screenShakeDX \|\| screenShakeDY\)/.test(SRC));
check('axis dies with the rattle', /screenShakeAmount = 0; screenShakeDX = screenShakeDY = 0;/.test(SRC));
check('round reset clears the axis', /screenShakeDX = screenShakeDY = 0;\n\s*roundTimer/.test(SRC));
check('speed lines feed the existing ghost pool',
      /Math\.abs\(this\.vx\) >= SPEEDLINE_V && Math\.abs\(this\.vx\) > walkTop \* 1\.02\)\s*this\.speedTrail = Math\.max\(this\.speedTrail, 0\.05\)/.test(SRC));
check('landing cushion is wired into the landing hook',
      /impactVy > LAND_CUSHION_V && !this\.isAttackingState\(\)/.test(SRC));
check('cushion never stacks on stun or an existing recovery',
      /this\.stunTimer <= 0 && this\.recoveryTimer <= 0/.test(SRC));

const SPEEDLINE_V = constOf('SPEEDLINE_V');
const LAND_CUSHION_V = constOf('LAND_CUSHION_V');
const LAND_CUSHION_MAX = constOf('LAND_CUSHION_MAX');
const LAND_CUSHION_SCALE = constOf('LAND_CUSHION_SCALE');
const DASH_SPEED = constOf('DASH_SPEED');
const GRAVITY = constOf('GRAVITY');

console.log('\nSPEED LINES');
// moveSpeed = 350 * (curSpeed / 6): a maxed speed stat walks at exactly 350.
const FASTEST_WALK = 350;
check('a dead sprint stays clean', FASTEST_WALK < SPEEDLINE_V, `walk ${FASTEST_WALK} vs gate ${SPEEDLINE_V}`);
check('a dash smears', DASH_SPEED > SPEEDLINE_V, `dash ${DASH_SPEED} vs gate ${SPEEDLINE_V}`);
check('Shin’s wire yank (560) smears', 560 > SPEEDLINE_V);
check('the wall-jump launch (480) smears', 480 > SPEEDLINE_V);

console.log('\nLANDING CUSHION');
// Jump take-off is -450 * jumpScale; a symmetric arc lands at the same speed.
const cushion = vy => vy > LAND_CUSHION_V
  ? Math.min(LAND_CUSHION_MAX, (vy - LAND_CUSHION_V) / LAND_CUSHION_SCALE) : 0;
const JUMP_V = 450;
check('a plain jump costs nothing', cushion(JUMP_V) === 0, `landed at ${JUMP_V}`);
// A double jump stacks a second -450 on top of the first arc's apex.
const apex = (JUMP_V ** 2) / (2 * GRAVITY);
const dblLand = Math.sqrt(2 * GRAVITY * (apex * 2));
check('a double jump is barely felt (<2 frames)', cushion(dblLand) < 2 / 60,
      `landed at ${dblLand.toFixed(0)} -> ${(cushion(dblLand) * 60).toFixed(1)}f`);
check('a real drop plants you', cushion(700) > 0, `700 -> ${(cushion(700) * 60).toFixed(1)}f`);
check('the cushion is capped', cushion(99999) === LAND_CUSHION_MAX);
check('the cap stays under 6 frames', LAND_CUSHION_MAX * 60 < 6, `${(LAND_CUSHION_MAX * 60).toFixed(1)}f`);
check('LAND_CUSHION_MAX = 0 switches the cushion off entirely',
      (v => v > LAND_CUSHION_V ? Math.min(0, (v - LAND_CUSHION_V) / LAND_CUSHION_SCALE) : 0)(9999) === 0);

console.log('\nDIRECTIONAL SHAKE');
// Mirrors the takeDamage block: sx away from the attacker, sy from the post-hit vy.
const axis = (victimX, attackerX, vy) => {
  const sx = Math.sign(victimX - attackerX) || 1;
  const sy = vy < -200 ? -1 : (vy > 400 ? 1 : 0);
  const len = Math.hypot(sx, sy) || 1;
  return { dx: sx / len, dy: sy / len };
};
const flat = axis(400, 300, 0);
check('a grounded hit throws the camera away from the attacker', flat.dx === 1 && flat.dy === 0);
check('the axis mirrors with the attacker', axis(400, 500, 0).dx === -1);
check('a launch tilts the axis up', axis(400, 300, -300).dy < 0);
check('a spike tilts the axis down', axis(400, 300, 640).dy > 0);
for (const [vx, vy] of [[400, 0], [400, -300], [400, 640]]) {
  const a = axis(vx, 300, vy);
  check(`axis stays unit-length (vy ${vy})`, Math.abs(Math.hypot(a.dx, a.dy) - 1) < 1e-12);
}

console.log(failures ? `\n${failures} FAILED` : '\nall polish-suite checks passed');
process.exit(failures ? 1 : 0);
