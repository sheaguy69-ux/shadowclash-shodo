#!/usr/bin/env node
// Surface-dynamics self-check (approved feature item 2): wall-running,
// ceiling-latching, stage wire traps.  Run: node tools/surface_dynamics_check.mjs
//
// Same two halves as tools/polish_suite_check.mjs — WIRING greps prove the call
// sites still exist, MATH mirrors the engine's own numbers. Edit the curves in
// index.html and re-mirror here, or this check lies.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const SRC = readFileSync(join(dirname(fileURLToPath(import.meta.url)), '..', 'web', 'index.html'), 'utf8');
let failures = 0;
const check = (label, cond, detail = '') => {
  if (cond) console.log(`  ok   ${label}`);
  else { console.log(`  FAIL ${label}${detail ? ' — ' + detail : ''}`); failures++; }
};
const constOf = name => {
  const m = SRC.match(new RegExp(`const\\s+${name}\\s*=\\s*(-?[0-9.]+)`));
  if (!m) { console.log(`  FAIL ${name} is not declared in web/index.html`); failures++; return NaN; }
  return parseFloat(m[1]);
};

console.log('WIRING');
check('owner wall hold stops vertical travel', /this\.wallRunning = false;\s*if \(this\.wallDir !== 0\) \{\s*this\.vy = 0;/.test(SRC));
check('the climb bills chakra from frame one', /if \(this\.wallRunning\) \{\s*\n\s*this\.stamina = Math\.max\(0, this\.stamina - WALL_RUN_DRAIN \* dt\)/.test(SRC));
check('regen pauses on EVERY paid surface, not just a hang',
      /const onPaidSurface = \(this\.wallDir !== 0 && \(this\.wallRunning \|\| this\.clingTime > WALL_DRAIN_DELAY\)\)\s*\n\s*\|\| this\.ceilLatch > 0;/.test(SRC));
check('the climb is stopped by a roof', /if \(this\.wallRunning && this\.y < CEIL_Y\)/.test(SRC));
check('the ceiling latch catches a rising head', /if \(this\.vy < 0 && this\.ceilLatch <= 0 && this\.isUpPressed\(\)/.test(SRC));
check('a spring frond can never be hung from', /if \(plat\.spring\) continue;/.test(SRC));
check('the latch drops on Down, a hit, or an empty bar',
      /if \(slipped \|\| this\.isDownPressed\(\) \|\| this\.stunTimer > 0 \|\| this\.stamina <= 0\)/.test(SRC));
check('jumping off a latch pushes DOWN and out', /if \(this\.ceilLatch > 0\) \{\s*\n\s*this\.ceilLatch = 0; this\.latchPlat = null;\s*\n\s*this\.vy = 140;/.test(SRC));
check('wire traps are built with the stage', /buildStageWires\(\);\s+\/\/ traps are stage data/.test(SRC));
check('wire traps tick in the main loop', /updateStageWires\(dt\);/.test(SRC));
check('wire traps are drawn', /drawStageWires\(\);\s+\/\/ taut steel/.test(SRC));
check('a snare tears you off any held surface', /p\.wallDir = 0; p\.ceilLatch = 0; p\.latchPlat = null;/.test(SRC));
check('a trap never deals damage', !/wireHit[\s\S]{0,900}?takeDamage/.test(SRC));
check('the yard advertises its hazard', /if \(st\.wires\) t\.push\('wire traps'\);/.test(SRC));

const WALL_RUN_SPEED = constOf('WALL_RUN_SPEED');
const WALL_RUN_DRAIN = constOf('WALL_RUN_DRAIN');
const CEIL_Y = constOf('CEIL_Y');
const CEIL_LATCH_MAX = constOf('CEIL_LATCH_MAX');
const CEIL_LATCH_DRAIN = constOf('CEIL_LATCH_DRAIN');
const WALL_DRAIN_RATE = constOf('WALL_DRAIN_RATE');
const WIRE_TRAP_CD = constOf('WIRE_TRAP_CD');
const WIRE_TRAP_STUN = constOf('WIRE_TRAP_STUN');
const GRAVITY = constOf('GRAVITY');
const REGEN = parseFloat(SRC.match(/this\.staminaRegenRate = ([0-9.]+)/)[1]);

console.log('\nWALL RUN');
check('a climb costs more than a hang', WALL_RUN_DRAIN > WALL_DRAIN_RATE, `${WALL_RUN_DRAIN} vs ${WALL_DRAIN_RATE}`);
check('a climb outruns its own regen — the wall is not a free ladder',
      WALL_RUN_DRAIN > REGEN, `drain ${WALL_RUN_DRAIN}/s vs regen ${REGEN}/s`);
const climbSecs = 100 / WALL_RUN_DRAIN;
check('a full bar buys a finite climb', climbSecs * WALL_RUN_SPEED < 1000,
      `${(climbSecs * WALL_RUN_SPEED).toFixed(0)}px over ${climbSecs.toFixed(1)}s`);
check('the roof is above the HUD but inside the world', CEIL_Y > 0 && CEIL_Y < 200);

console.log('\nCEILING LATCH');
check('a hang costs more than a wall hang, less than a climb',
      CEIL_LATCH_DRAIN > WALL_DRAIN_RATE && CEIL_LATCH_DRAIN < WALL_RUN_DRAIN,
      `${WALL_DRAIN_RATE} < ${CEIL_LATCH_DRAIN} < ${WALL_RUN_DRAIN}`);
check('a hang is an approach, not a camp spot', CEIL_LATCH_MAX <= 2, `${CEIL_LATCH_MAX}s`);
check('a full bar cannot outlast the hang timer', 100 / CEIL_LATCH_DRAIN > CEIL_LATCH_MAX,
      `bar lasts ${(100 / CEIL_LATCH_DRAIN).toFixed(1)}s, timer cuts at ${CEIL_LATCH_MAX}s`);

console.log('\nWIRE TRAPS');
const wires = SRC.match(/wires: \[\s*\{([^\]]+)\]/);
check('the Warrant Yard is rigged', !!wires);
const ys = [...SRC.matchAll(/\{ x0: (\d+), y0: (\d+), x1: (\d+), y1: (\d+) \}/g)]
  .map(m => ({ x0: +m[1], y0: +m[2], x1: +m[3], y1: +m[4] }));
check('two strands, both horizontal (a diagonal is only trippable at its low end)',
      ys.length === 2 && ys.every(w => w.y0 === w.y1), JSON.stringify(ys));
check('the cooldown outlasts the stagger — no wire stunlock', WIRE_TRAP_CD > WIRE_TRAP_STUN,
      `cd ${WIRE_TRAP_CD}s vs stun ${WIRE_TRAP_STUN}s`);
check('the stagger matches the soft wire snare it borrows from', WIRE_TRAP_STUN === 0.45);
// Both spawns are hardcoded at x 150 and 600; a trap on top of either would snare on FIGHT!.
check('neither strand covers a spawn', ys.every(w => !(150 >= w.x0 && 150 <= w.x1) && !(600 >= w.x0 && 600 <= w.x1)),
      JSON.stringify(ys.map(w => `${w.x0}-${w.x1}`)));
// Fighters are 48 tall; the trap radius is height*0.45 and the centre sits 24 above the feet.
const R = 48 * 0.45, CENTRE = 24;
const band = w => [w.y0 - R - CENTRE, w.y0 + R - CENTRE];   // feet-height range caught
const [lowA, lowB] = band(ys[0]), [hiA, hiB] = band(ys[1]);
check('the LOW strand trips a runner on the floor', lowA <= 0 && lowB >= 0, `catches feet ${lowA.toFixed(0)}..${lowB.toFixed(0)}`);
const jumpApexFeet = (450 ** 2) / (2 * GRAVITY);
check('the HIGH strand catches a jump-in and NOT a walk',
      hiA > 0 && jumpApexFeet >= hiA, `catches feet ${hiA.toFixed(0)}..${hiB.toFixed(0)}, jump apex ${jumpApexFeet.toFixed(0)}`);
check('the HIGH strand is clearable from above (double-jump apex sits over the band)',
      jumpApexFeet * 2 > hiB, `double apex ${(jumpApexFeet * 2).toFixed(0)} vs band top ${hiB.toFixed(0)}`);

console.log(failures ? `\n${failures} FAILED` : '\nall surface-dynamics checks passed');
process.exit(failures ? 1 : 0);
