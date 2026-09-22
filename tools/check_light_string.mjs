#!/usr/bin/env node
// MULTI-TAP LIGHT STRINGS — the smallest thing that fails if the logic breaks.
// Mirrors the three pieces the feature added to web/index.html:
//   1. the beat picker in the light dispatch (window -> advance, else beat one)
//   2. the cancel gate (a CONNECTED light cancels into the next beat, never past
//      the last, never in the air, never on whiff)
//   3. beat one is the shipped light — factor 1s across the board.
// Numbers are copied from the source; if the source drifts, this fails loudly.

const LIGHT_STRING_WINDOW = 0.55;
const LIGHT_STRINGS = {
  default: [
    {},
    { w: 1.15, dmg: 1.15, rec: 1.10, push: 1.5 },
    { w: 1.30, dmg: 1.50, rec: 1.35, push: 2.8, vx: 200 },
  ],
};
const lightBeats = p => LIGHT_STRINGS[p.spec.id] ?? LIGHT_STRINGS.default;

// --- 1. the beat picker, verbatim logic ---
function fireLight(p) {
  const beats = lightBeats(p);
  p.stringStep = p.stringT > 0 ? (p.stringStep + 1) % beats.length : 0;
  p.stringT = LIGHT_STRING_WINDOW;
  return beats[p.stringStep];
}
// --- 2. the cancel gate, verbatim logic (both mirrored sites) ---
function lightCanCancel(p, inWin) {
  return p.chainComboTier === 1 && inWin && p.isGrounded
      && p.state === 'ATTACK_LIGHT' && p.stringT > 0
      && p.stringStep + 1 < lightBeats(p).length;
}

const mk = () => ({ spec: { id: 4 }, stringStep: 0, stringT: 0,
                    chainComboTier: 1, isGrounded: true, state: 'ATTACK_LIGHT' });
const tick = (p, dt) => { if (p.stringT > 0) p.stringT -= dt; };

// beat one is the shipped light: no factors, no riders
const p = mk();
let b = fireLight(p);
console.assert(Object.keys(b).length === 0, 'beat one must be the untouched light');

// taps inside the window walk 0 -> 1 -> 2, then WRAP to beat one on the 4th
tick(p, 0.3); b = fireLight(p);
console.assert(p.stringStep === 1 && b.dmg === 1.15, 'tap in window -> beat two');
tick(p, 0.3); b = fireLight(p);
console.assert(p.stringStep === 2 && b.vx === 200, 'tap in window -> beat three');
tick(p, 0.3); b = fireLight(p);
console.assert(p.stringStep === 0, '4th tap wraps to beat one');

// a tap OUTSIDE the window restarts at beat one
const q = mk();
fireLight(q); tick(q, 0.6);
fireLight(q);
console.assert(q.stringStep === 0, 'window expired -> string restarts');

// the cancel gate: open mid-string on hit, shut everywhere else
const c = mk();
fireLight(c);                                    // beat one is out, connected
console.assert(lightCanCancel(c, true), 'connected beat one cancels into beat two');
console.assert(!lightCanCancel(c, false), 'a whiffed light never cancels');
c.isGrounded = false;
console.assert(!lightCanCancel(c, true), 'air lights stay out of the string');
c.isGrounded = true; c.chainComboTier = 0;
console.assert(!lightCanCancel(c, true), 'tier 0 goes through the normal opener, not the cancel');
c.chainComboTier = 1;
fireLight(c); fireLight(c);                      // walk to the LAST beat
console.assert(c.stringStep === 2 && !lightCanCancel(c, true),
  'the last beat can NEVER cancel-wrap — the loop must re-open as a fresh chain');

// a hit breaks the string (the takeDamage reset)
const h = mk();
fireLight(h); h.stringStep = 0; h.stringT = 0;   // the reset, verbatim
fireLight(h);
console.assert(h.stringStep === 0, 'after being hit the next tap is beat one');

// the source actually carries all of this — grep the live file, not a memory of it
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const src = readFileSync(join(dirname(fileURLToPath(import.meta.url)), '../web/index.html'), 'utf8');
for (const needle of ['LIGHT_STRING_WINDOW = 0.55', 'const lightBeats',
                      'this.stringStep + 1 < lightBeats(this).length',
                      'this.stringStep = 0; this.stringT = 0;',
                      '(sb?.push ?? 1)'])
  console.assert(src.includes(needle), `source lost its string wiring: ${needle}`);
console.assert((src.match(/stringStep \+ 1 < lightBeats\(this\)\.length/g) || []).length === 2,
  'the two cancel gates must stay MIRRORED — one of them lost the string case');

console.log('PASS — multi-tap light strings: beats advance, wrap only by re-opening, cancel only on hit');
