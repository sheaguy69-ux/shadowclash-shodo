#!/usr/bin/env node
// Airborne must never draw a GROUNDED beat. Owner ruling 2026-09-03.
//
// Beats 5 and 6 of every jump row are ground-contact art (landing impact burst; planted
// stance with its cast shadow), and Mokurai's bjump6-8 are the same. They are correct on
// the ground and wrong in the air. This sweeps the real vy range against the band logic
// LIFTED FROM web/index.html — not a copy, so the check cannot drift away from the engine.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const src = readFileSync(join(ROOT, 'web/index.html'), 'utf8');

const grab = (re, what) => {
  const m = src.match(re);
  if (!m) { console.error(`  air guard: could not find ${what} in web/index.html`); process.exit(1); }
  return m;
};

const airMax = Number(grab(/const JUMP_AIR_MAX = (\d+);/, 'JUMP_AIR_MAX')[1]);
const bAirMax = Number(grab(/const BJUMP_AIR_MAX = (\d+);/, 'BJUMP_AIR_MAX')[1]);
const bandSrc = grab(/const jumpBand = (\(vy, grounded\) =>[\s\S]*?);\n/, 'jumpBand')[1];
const jumpBand = eval(`(() => { const JUMP_AIR_MAX = ${airMax}; return ${bandSrc}; })()`);

// GRAVITY 1100, jump vy -450 -> descent tops out near +450; sweep well past it.
let bad = [];
for (let vy = -600; vy <= 900; vy += 1) {
  const b = jumpBand(vy, false);
  if (b > airMax) bad.push({ vy, b });
}
const g = jumpBand(0, true);

// Mokurai's table, same law, clamped in the draw site.
const bands = [-400, -250, -80, 80, 240, 380, 520];
const bjLen = 8;
let badB = [];
for (let vy = -600; vy <= 900; vy += 1) {
  let k = bands.findIndex(v => vy < v);
  if (k < 0) k = bands.length;
  let idx = Math.min(bjLen - 1, Math.round((k * (bjLen - 1)) / bands.length));
  idx = Math.min(idx, bAirMax);           // the guard the draw site applies when !isGrounded
  if (idx > bAirMax) badB.push({ vy, idx });
}

const fail = [];
if (bad.length) fail.push(`jumpBand returned a grounded beat while airborne at ${bad.length} vy values (e.g. vy=${bad[0].vy} -> beat ${bad[0].b + 1})`);
if (badB.length) fail.push(`mokurai band returned ${badB[0].idx} > ${bAirMax} while airborne`);
if (g !== 5) fail.push(`grounded no longer reaches the landing beat (got ${g}, want 5)`);
if (airMax >= 4) fail.push(`JUMP_AIR_MAX ${airMax} still allows beat ${airMax + 1}, which is ground-contact art`);
if (bAirMax >= 5) fail.push(`BJUMP_AIR_MAX ${bAirMax} still allows bjump${bAirMax + 1}, which carries the ground splash`);

if (fail.length) {
  console.log('  ⛔ AIR GUARD FAILED:');
  for (const f of fail) console.log(`    - ${f}`);
  process.exit(1);
}
console.log(`  air guard: 1501 vy values swept — airborne never exceeds beat ${airMax + 1} (ajump) / bjump${bAirMax + 1}; grounded still reaches beat 6`);
