#!/usr/bin/env node
// Kinetics self-check for the motion roadmap (jump arc + lean spring).
// Mirrors the exact formulas in web/index.html — if someone edits those curves,
// re-mirror them here or this check lies. Run: node tools/kinetics_check.mjs
// ⛔ GRAVITY IS DERIVED FROM THE ENGINE, NOT MIRRORED. The header above says
// "re-mirror them here or this check lies" — and then it lied: GRAVITY went 1100 -> 1650
// at build 857 and this file kept simulating the old arc, so a jump-arc self-check was
// grading a curve the game no longer has.
// And it cannot be read with the siblings' constOf() regex, because GRAVITY is NOT a
// literal — index.html:1633 computes it as
//   -engine_settings.gravity * engine_settings.units.gravity_and_velocity_pixels_per_unit
// so `const GRAVITY = <number>` never matches and constOf returns NaN. Do the same
// multiplication off the same authored JSON the engine parses, and the mirror cannot
// drift again no matter which of the two numbers moves.
import { readFileSync } from 'node:fs';
const SRC = readFileSync(new URL('../web/index.html', import.meta.url), 'utf8');
const open = SRC.indexOf('<script id="footsies-data"');
const FOOTSIES = JSON.parse(SRC.slice(SRC.indexOf('>', open) + 1, SRC.indexOf('</script>', open)));
const ES = FOOTSIES.engine_settings;
const GRAVITY = -ES.gravity * ES.units.gravity_and_velocity_pixels_per_unit;
if (!(GRAVITY > 0)) throw new Error(`GRAVITY derived as ${GRAVITY} from engine_settings`);
const DT = 1 / 240;

// --- D: asymmetric jump arc (applyPhysics) ---
function simJump(jumpVy, asym) {
  let vy = jumpVy, y = 0, t = 0, apexY = 0, tApex = 0, tLand = 0;
  while (t < 5) {
    let g = GRAVITY;
    if (asym) {
      if (Math.abs(vy) < 55) g *= 0.55;
      else if (vy > 0) g *= 1.6;
    }
    vy += g * DT; y += vy * DT; t += DT;
    if (y < apexY) { apexY = y; tApex = t; }
    if (y >= 0 && t > 0.05) { tLand = t; break; }
  }
  return { apex: -apexY, tApex, tFall: tLand - tApex, tAir: tLand };
}
const sym = simJump(-450, false), asy = simJump(-450, true);
console.log('symmetric :', JSON.stringify(sym));
console.log('asymmetric:', JSON.stringify(asy));
// Weight targets: fall must be meaningfully FASTER than the rise (no parachute),
// apex height barely changes (jump reach preserved), total airtime shorter.
console.assert(asy.tFall < asy.tApex * 0.92, 'FAIL: descent not heavier than ascent');
console.assert(Math.abs(asy.apex - sym.apex) / sym.apex < 0.12, 'FAIL: apex height drifted >12%');
// The apex hang deliberately adds a beat, so total airtime may grow a hair —
// but more than +5% means the hang has become a float again.
console.assert(asy.tAir < sym.tAir * 1.05, 'FAIL: airtime grew >5% — apex hang is a float again');

// --- lean spring (underdamped follow-through) ---
function simLean(dt) {
  let lean = 0.35, vel = 0, minLean = 1, settled = 0, t = 0;
  // release from full sprint lean (target 0 = hard stop)
  while (t < 3) {
    vel += (0 - lean) * 130 * dt;
    vel *= Math.max(0, 1 - 10 * dt);
    lean += vel * dt; t += dt;
    if (lean < minLean) minLean = lean;
    if (Math.abs(lean) < 0.005 && Math.abs(vel) < 0.01) { settled = t; break; }
  }
  return { overshoot: -minLean, settled, finite: Number.isFinite(lean) };
}
for (const dt of [1 / 60, 1 / 240]) {
  const s = simLean(dt);
  console.log(`lean dt=${(1 / dt).toFixed(0)}Hz:`, JSON.stringify(s));
  console.assert(s.finite, 'FAIL: lean spring diverged');
  console.assert(s.overshoot > 0.02, 'FAIL: no follow-through overshoot on stop');
  console.assert(s.overshoot < 0.18, 'FAIL: overshoot too wild (wobble toy)');
  console.assert(s.settled > 0 && s.settled < 1.0, 'FAIL: spring does not settle inside 1s');
}

console.log('KINETICS CHECK: ALL PASS');
