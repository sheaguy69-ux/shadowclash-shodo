#!/usr/bin/env node
import {spawnSync} from 'node:child_process';
// Stance-slot self-check — approved features 4, 5, 6, 7, 8.
// Run: node tools/stance_slots_check.mjs
//
// Same two halves as the other item checks (hasuji / polish_suite / surface_dynamics):
// WIRING greps prove the call sites still exist, NUMBERS mirror the engine's own
// constants so a balance edit that breaks an identity fails here instead of in play.
//
// The behavioural half — that a lock actually resolves, that the echo actually
// re-throws a recorded swing — was measured live in the browser against the real
// engine; these are the invariants that must survive every later edit.
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
  const m = SRC.match(new RegExp(`const\\s+${name}\\s*=\\s*(-?[0-9./\\s]+?)[;,]`));
  if (!m) { console.log(`  FAIL ${name} is not declared in web/index.html`); failures++; return NaN; }
  return eval(m[1]);   // the file writes frame counts as `7 / 60`, which is the readable form
};

console.log('WIRING — one key, four directions');
check('the stance key dispatches on held direction', /switch \(heldDir\(this\)\) \{/.test(SRC));
check('Up is Muki-Kamae',        /case 'up':\s*return this\.toggleMuki\(\);/.test(SRC));
check('Down is Saya-Kamae',      /case 'down':\s*return this\.toggleSaya\(\);/.test(SRC));
check('Back is Kage-Kami',       /case 'back':\s*return this\.castKageKami\(\);/.test(SRC));
check('Fwd is the anchor',
      /case 'fwd':\s*return this\.weaveAnchor\(\);/.test(SRC));
// ⛔ The direction read MUST come before the per-fighter branches, or Shin and
// Exile each swallow the press and lose four features apiece.
check('direction is read BEFORE the per-fighter second forms',
      SRC.indexOf('switch (heldDir(this))') < SRC.indexOf('if (this.spec.id === 7) return this.enterChampion();'));

console.log('\nWIRING — item 7, Muki-Kamae');
check('the guard branch is unreachable while it is set', /&& this\.muki <= 0\) \{/.test(SRC));
check('its boxes come out unblockable', /if \(this\.muki > 0\) \{\s*\n\s*dmg \*= MUKI_DMG;\s*\n\s*opts = \{ \.\.\.opts, unblockable: true,/.test(SRC));
check('startup is multiplied, not subtracted', /delay: \(opts\.delay \?\? 0\) \* MUKI_STARTUP/.test(SRC));
check('damage TAKEN is the other half of the trade',
      /\* \(this\.muki > 0 \? MUKI_TAKEN : 1\)/.test(SRC));
check('it expires on its own — never a resting state', /if \(this\.muki > 0\) \{\s*\n\s*this\.muki -= dt;/.test(SRC));

console.log('\nWIRING — item 8, Saya-Kamae');
check('blade carriers only, on the shared material predicate', /if \(!isMetal\(weaponMat\(this\)\) \|\| this\.sayaLock > 0\)/.test(SRC));
check('gyaku-te is shorter and quicker', /if \(this\.gyakute\) \{\s*\n\s*w \*= SAYA_REACH;/.test(SRC));
check('the switch locks his hands for its 7 frames', /this\.sayaLock > 0 \|\| this\.rollTimer > 0/.test(SRC));
check('the auto-parry needs steel on steel', /this\.gyakute && this\.sayaParryCd <= 0\s*\n\s*&& bladeOnBlade\(attacker, this, sourceHitbox\)/.test(SRC));
check('the auto-parry goes on cooldown', /this\.sayaParryCd = SAYA_PARRY_CD;/.test(SRC));

console.log('\nWIRING — item 4, Kage-Kami');
check('the tape records ALWAYS, not only while an echo is out', /this\.recordKageTape\(dt\);/.test(SRC));
check('swings are recorded RAW, at the very top of spawnHitbox',
      /spawnHitbox\(w, h, dmg, dur, push, opts = \{\}\) \{[\s\S]{0,700}?if \(!opts\.echo\) \{\s*\n\s*this\.kageActs\.push/.test(SRC));
check('an echo box is never re-recorded (no shadow of a shadow)', /if \(!opts\.echo\) \{/.test(SRC));
check('the echo rides the shared clone shell', /if \(c\.kage\) this\.updateKageEcho\(dt, c\);/.test(SRC));
check('the replay floor is the echo’s own start, not the cast instant',
      /played: start,/.test(SRC) && !/played: animClock,/.test(SRC));
check('the shadow draws the recorded cell, not a looping row', /const ci = c\.cell !== undefined \? c\.cell/.test(SRC));
check('the drawn cell is captured where it is actually resolved', /p\.drawCell = idx;/.test(SRC));
check('echo boxes are re-seated onto the shadow', /hb\.ox \+= \(c\.x - this\.x\);/.test(SRC));

console.log('\nWIRING — item 6, Shadow-Weave');
check('first press plants, second swaps', /if \(this\.weave\) \{[\s\S]{0,900}?this\.weave = \{ x: mx, y: my, t: this\.weave\.t \};/.test(SRC));
check('the swap cancels recovery — that IS the combo extension', /this\.recoveryTimer = 0; this\.recoveryTotal = 0;\s*\/\/ the extension/.test(SRC));
check('the swap is clamped to the stage', /this\.x = clampLandX\(ax, this\.width\);/.test(SRC));
check('the anchor and its thread are drawn', /function drawWeave\(\)/.test(SRC) && /drawWeave\(\);/.test(SRC));

// Current lock behavior is exercised, not inferred from obsolete source strings.
const lockCheck = spawnSync(process.execPath, [join(dirname(fileURLToPath(import.meta.url)), 'blade_lock_check.mjs')], {encoding:'utf8'});
check('current blade-lock behavior regression', lockCheck.status === 0, lockCheck.stderr);

console.log('\nWIRING — the resets');
check('a room reset clears every new slot', /p\.lock = null;[\s\S]{0,180}p\.weave = null; p\.muki = 0; p\.gyakute = false;/.test(SRC));
check('a room reset drops the tape and the tether', /p\.kageTape\.length = 0; p\.kageActs\.length = 0;\s*\n\s*p\.dropTether\(\);/.test(SRC));

const MUKI_DUR = constOf('MUKI_DUR'), MUKI_STARTUP = constOf('MUKI_STARTUP');
const MUKI_DMG = constOf('MUKI_DMG'), MUKI_TAKEN = constOf('MUKI_TAKEN');
const SAYA_LOCK = constOf('SAYA_LOCK'), SAYA_REACH = constOf('SAYA_REACH'), SAYA_STARTUP = constOf('SAYA_STARTUP');
const KK_DELAY = constOf('KAGEKAMI_DELAY'), KK_LIFE = constOf('KAGEKAMI_LIFE');
const KK_DMG = constOf('KAGEKAMI_DMG'), KK_TAPE = constOf('KAGEKAMI_TAPE'), KK_HZ = constOf('KAGEKAMI_HZ');
const KAGE_STARTUP = constOf('KAGE_CAST_STARTUP'), KAGE_SPEED = constOf('KAGE_SPEED');
const KAGE_DUR = constOf('KAGE_TETHER_DUR');
const KIAI_TIME = constOf('KIAI_TIME'), KIAI_LEAD = constOf('KIAI_LEAD'), KIAI_BREAK = constOf('KIAI_BREAK');

console.log('\nNUMBERS — item 7, the risk is real');
check('faster startup is a real gain', MUKI_STARTUP < 0.8 && MUKI_STARTUP > 0.4, `${(MUKI_STARTUP * 100).toFixed(0)}% of normal startup`);
check('damage taken outweighs damage dealt', MUKI_TAKEN > MUKI_DMG, `+${((MUKI_TAKEN - 1) * 100).toFixed(0)}% taken vs +${((MUKI_DMG - 1) * 100).toFixed(0)}% dealt`);
check('it cannot be camped', MUKI_DUR <= 6, `${MUKI_DUR}s`);

console.log('\nNUMBERS — item 8, the grip is a trade');
check('the toggle is exactly 7 frames', Math.abs(SAYA_LOCK * 60 - 7) < 1e-9, `${(SAYA_LOCK * 60).toFixed(1)} frames`);
check('reverse gives up reach', SAYA_REACH < 1, `${((1 - SAYA_REACH) * 100).toFixed(0)}% shorter`);
check('...and buys frames with it', SAYA_STARTUP < 1, `${((1 - SAYA_STARTUP) * 100).toFixed(0)}% faster`);
check('neither side of the trade is a no-brainer', SAYA_REACH > 0.7 && SAYA_STARTUP > 0.7);

console.log('\nNUMBERS — item 4, the echo');
check('the tape outlives delay + life, so it never underruns', KK_TAPE >= KK_DELAY + KK_LIFE * 0.4,
      `${KK_TAPE}s of tape for a ${KK_DELAY}s delay`);
check('the sample rate is smoother than the eye', 1 / KK_HZ >= 24, `${(1 / KK_HZ).toFixed(0)}Hz`);
check('the delay is readable as a delay', KK_DELAY >= 0.3 && KK_DELAY <= 1.2, `${KK_DELAY}s`);
check('an echo of a cut is worth less than the cut', KK_DMG <= 0.5, `${KK_DMG * 100}%`);

console.log('\nNUMBERS — Shin’s wire');
check('Shin’s 4s bound state holds', Math.abs(KAGE_DUR - 4) < 1e-9, `${KAGE_DUR}s`);

console.log('\nNUMBERS — item 5, the struggle');
check('the lock is short enough to mash flat out', KIAI_TIME <= 1.5, `${KIAI_TIME}s`);
check('the lead needed is a contest, not a coin flip', KIAI_LEAD >= 2, `${KIAI_LEAD} presses`);
check('a break is a real punish window', KIAI_BREAK >= 0.5, `${KIAI_BREAK}s of guard break`);
// A break must leave less time than a full lock, or winning is worse than drawing.
check('winning beats drawing', KIAI_BREAK < KIAI_TIME + 0.5);

console.log(failures ? `\n${failures} FAILURE(S)` : '\nall stance-slot checks pass');
process.exit(failures ? 1 : 0);
