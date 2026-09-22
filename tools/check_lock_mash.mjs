#!/usr/bin/env node
// BLADE LOCK MASH. fireCombatKey is a plain function reached from pressCombat, the
// hitstop flush, the mouse, the pad and the touch pad — none of which have a DOM
// event. It read `e.repeat`, which is only in scope in the keydown handler, so every
// attack press during a bind threw ReferenceError BEFORE lockMash was incremented:
// a human could never win a lock. The flag is now threaded in as a parameter.
//
// Both properties have to hold: a real press counts, a HELD button does not.

function fireCombatKey(state, code, repeat = false) {
  if (state.lockT > 0 && ['KeyF', 'KeyG', 'KeyH'].includes(code)) {
    if (!repeat) state.lockMash++;
    return 'claimed';
  }
  return 'passed';
}
// what the code used to do — `e` unbound in this scope
function fireCombatKey_broken(state, code) {
  if (state.lockT > 0 && ['KeyF', 'KeyG', 'KeyH'].includes(code)) {
    if (!e.repeat) state.lockMash++;   // eslint-disable-line no-undef
    return 'claimed';
  }
  return 'passed';
}

const mk = () => ({ lockT: 1.0, lockMash: 0 });

// the bug reproduces
let threw = false;
try { fireCombatKey_broken(mk(), 'KeyF'); } catch (e) { threw = e instanceof ReferenceError; }
console.log('old code throws ReferenceError:', threw);

// discrete presses count
const tap = mk();
for (let i = 0; i < 20; i++) fireCombatKey(tap, 'KeyF', false);
// a held button counts nothing
const held = mk();
for (let i = 0; i < 20; i++) fireCombatKey(held, 'KeyF', true);
// and the press is CLAIMED either way, so it never leaks into executeAttack mid-lock
const claimed = fireCombatKey(mk(), 'KeyG', true) === 'claimed';
// outside a lock the press passes through untouched
const free = mk(); free.lockT = 0;
const passes = fireCombatKey(free, 'KeyF', false) === 'passed' && free.lockMash === 0;

console.log({ discretePresses: tap.lockMash, heldButton: held.lockMash, claimed, passes });
console.assert(threw, 'the bug must reproduce in the old shape');
console.assert(tap.lockMash === 20, 'discrete presses must count');
console.assert(held.lockMash === 0, 'a held button must win nothing');
console.assert(claimed, 'the press must be claimed during a lock');
console.assert(passes, 'outside a lock the press must pass through');

const ok = threw && tap.lockMash === 20 && held.lockMash === 0 && claimed && passes;
console.log(ok ? 'PASS — a bind is won by mashing, and mashing is counted' : 'FAIL');
process.exit(ok ? 0 : 1);
