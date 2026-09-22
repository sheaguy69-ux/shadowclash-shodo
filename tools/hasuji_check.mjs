#!/usr/bin/env node
// Hasuji self-check (approved feature item 3): frame-exact edge alignment.
// Run: node tools/hasuji_check.mjs
//
// Same two halves as the other item checks — WIRING greps prove the call sites
// still exist, MATH mirrors the engine's own numbers.
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
check('hitboxes carry the active span and the hasuji flag', /activeTotal: dur,\s*\n\s*hasuji: isMetal\(weaponMat\(this\)\)/.test(SRC));
check('only a real EDGE qualifies', /hasuji: isMetal\(weaponMat\(this\)\)/.test(SRC));
check('only committed swings qualify',
      /\[STATE\.ATTACK_HEAVY, STATE\.ATTACK_SPECIAL\]\.includes\(opts\.tier \|\| this\.state\)/.test(SRC));
check('the window is measured off elapsed ACTIVE time', /const elapsed = h\.activeTotal - h\.duration;/.test(SRC));
check('the window is capped at half the active span',
      /h\.hasujiHit = elapsed <= Math\.min\(HASUJI_WINDOW, h\.activeTotal \* 0\.5\);/.test(SRC));
check('body hits do not emit blade-contact sparks', !/createSparks\(defender\.lastHitX, defender\.lastHitY, bladeSheen\(attacker\)\)/.test(SRC));
check('extra hit-stop is added to the clean hit', /\+ \(sourceHitbox && sourceHitbox\.hasujiHit \? HASUJI_STOP : 0\)/.test(SRC));
check('chip bypass reads the same flag off the hitbox',
      /const edge = !!\(sourceHitbox && sourceHitbox\.hasujiHit\);/.test(SRC));
check('the block branch picks the bypass fraction',
      /dmg \* \(edge \? HASUJI_CHIP : 0\.15\) \* HEALTH_DAMAGE_SCALE/.test(SRC));
// The whole point: a guard still HOLDS. If this ever grants stun the move became unblockable.
check('a bypassed block still grants no stun',
      !/const edge = !!\(sourceHitbox[\s\S]{0,400}?stunTimer/.test(SRC));

const HASUJI_WINDOW = constOf('HASUJI_WINDOW');
const HASUJI_STOP = constOf('HASUJI_STOP');
const HASUJI_CHIP = constOf('HASUJI_CHIP');
const BASE_CHIP = 0.15;

console.log('\nNUMBERS');
check('the window is a real read, not a coin flip', HASUJI_WINDOW * 60 >= 2 && HASUJI_WINDOW * 60 <= 5,
      `${(HASUJI_WINDOW * 60).toFixed(1)} frames at 60fps`);
check('the extra freeze is felt but not a stall', HASUJI_STOP >= 30 && HASUJI_STOP <= 80,
      `${HASUJI_STOP}ms = ${(HASUJI_STOP / 16.67).toFixed(1)}f`);
check('chip bypass beats the baseline', HASUJI_CHIP > BASE_CHIP, `${HASUJI_CHIP} vs ${BASE_CHIP}`);
check('chip bypass is NOT an unblockable — blocking still more than halves the hit',
      HASUJI_CHIP < 0.5, `${HASUJI_CHIP} of full damage through a guard`);
check('the bypass is worth going for', HASUJI_CHIP / BASE_CHIP >= 2,
      `${(HASUJI_CHIP / BASE_CHIP).toFixed(1)}x the baseline chip`);

console.log('\nWINDOW MATH (mirrors processHitboxes)');
// `duration` only decays on frames the box did NOT connect, so activeTotal - duration
// is the elapsed active time.
const sweet = (activeTotal, lateFrames) => {
  const elapsed = lateFrames / 60;
  return elapsed <= Math.min(HASUJI_WINDOW, activeTotal * 0.5);
};
check('landing on frame 0 of the active window is sweet', sweet(0.20, 0));
check('landing 2 frames in is still sweet', sweet(0.20, 2));
check('landing 12 frames in is not', !sweet(0.20, 12));
check('a 4-frame box (0.067s) cannot be sweet for its whole life', !sweet(0.067, 3),
      `cap ${Math.min(HASUJI_WINDOW, 0.067 * 0.5).toFixed(3)}s`);
check('a 4-frame box can still be caught on frame 0', sweet(0.067, 0));
// Every real spawnHitbox duration in the file must have a reachable, non-total window.
const durs = [...SRC.matchAll(/spawnHitbox\(\s*[\w.*\s]+,\s*[\w.*\s]+,\s*[^,]+,\s*([0-9.]+)\s*,/g)]
  .map(m => parseFloat(m[1])).filter(d => d > 0);
check('every authored hitbox duration has a reachable sweet spot', durs.length > 0 && durs.every(d => sweet(d, 0)),
      `${durs.length} durations, shortest ${Math.min(...durs)}s`);
check('no authored duration is sweet for its ENTIRE span',
      durs.every(d => !sweet(d, Math.ceil(d * 60) - 1) || d * 60 <= 2),
      `longest fully-sweet ${Math.max(...durs.filter(d => sweet(d, Math.ceil(d * 60) - 1)), 0)}s`);

console.log(failures ? `\n${failures} FAILED` : '\nall hasuji checks passed');
process.exit(failures ? 1 : 0);
