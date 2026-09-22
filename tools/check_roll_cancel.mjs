#!/usr/bin/env node
// A roll is COMMITTED. Mirrors the guard order in executeShunshin + handleMovement:
// handleMovement resolves grapple -> dash -> roll, so anything that sets dashTimer or
// grappleT while rollTimer is live FREEZES the roll's clock, and rollIFrames() reads
// that frozen clock — stretching the roll's intangible middle across the whole dash.
const ROLL_TIME = 0.28, DASH_TIME = 0.15, IN = 0.25, OUT = 0.72, DT = 1 / 60;

const mk = () => ({ rollTimer: 0, dashTimer: 0, grappleT: 0, rollRecover: 0, stamina: 100 });
const rollIFrames = p => {
  if (p.rollTimer <= 0) return false;
  const done = 1 - p.rollTimer / ROLL_TIME;
  return done >= IN && done <= OUT;
};
// the shipped precedence
const handleMovement = (p, dt) => {
  if (p.grappleT > 0) p.grappleT -= dt;
  else if (p.dashTimer > 0) p.dashTimer -= dt;
  else if (p.rollTimer > 0) p.rollTimer -= dt;
};
const shunshin = (p, guarded) => {
  if (guarded && (p.rollTimer > 0 || p.rollRecover > 0)) return;   // the fix
  if (!guarded && p.rollRecover > 0) return;                        // the old gate
  if (p.stamina < 15) return;
  p.dashTimer = DASH_TIME;
};

function trial(guarded) {
  const p = mk();
  p.rollTimer = ROLL_TIME;
  for (let i = 0; i < 6; i++) handleMovement(p, DT);   // roll into the i-frame window
  if (!rollIFrames(p)) throw new Error('setup: expected to be mid-i-frames');
  shunshin(p, guarded);
  let intangibleDashFrames = 0;
  for (let i = 0; i < 12 && p.dashTimer > 0; i++) {
    handleMovement(p, DT);
    if (rollIFrames(p)) intangibleDashFrames++;
  }
  return { dashStarted: p.dashTimer !== 0, intangibleDashFrames };
}

const before = trial(false), after = trial(true);
console.log('unguarded (the bug):', before);
console.log('guarded   (shipped):', after);

// a dash from neutral must still come out
const n = mk(); shunshin(n, true);
console.assert(n.dashTimer === DASH_TIME, 'a neutral dash must still work');
console.assert(before.intangibleDashFrames > 0, 'the bug should reproduce when unguarded');
console.assert(after.intangibleDashFrames === 0, 'no i-frames may survive into a dash');
console.assert(after.dashStarted === false, 'a dash must not start during a live roll');

const ok = before.intangibleDashFrames > 0 && after.intangibleDashFrames === 0 && n.dashTimer === DASH_TIME;
console.log(ok ? 'PASS — a roll cannot be cancelled into an invulnerable dash' : 'FAIL');
process.exit(ok ? 0 : 1);
