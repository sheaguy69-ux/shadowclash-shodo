// Self-check for the brawl hitbox-timer fix: a hitbox's startup/active must age
// once per FRAME, never once per opponent. Mirrors processHitboxes' timer logic.
function processHitboxes(attacker, dt, advance = true) {
  for (let i = attacker.hitboxes.length - 1; i >= 0; i--) {
    const h = attacker.hitboxes[i];
    if (h.delay > 0) { if (advance) h.delay -= dt; continue; }
    if (advance) { h.duration -= dt; if (h.duration <= 0) attacker.hitboxes.splice(i, 1); }
  }
}
const DT = 1 / 60, STARTUP = 0.233, ACTIVE = 0.067;
function run(nFoes, fixed) {
  const a = { hitboxes: [{ delay: STARTUP, duration: ACTIVE }] };
  let frames = 0, liveAt = null;
  while (a.hitboxes.length && frames < 600) {
    frames++;
    let first = true;
    for (let f = 0; f < nFoes; f++) {
      processHitboxes(a, DT, fixed ? first : true);
      first = false;
    }
    if (liveAt === null && a.hitboxes.length && a.hitboxes[0].delay <= 0) liveAt = frames;
  }
  return { startupFrames: liveAt, totalFrames: frames };
}
const want = run(1, true);                 // 1v1 is the authored reference
let bad = 0;
for (const foes of [1, 2]) {
  const fixed = run(foes, true), broken = run(foes, false);
  const ok = fixed.startupFrames === want.startupFrames && fixed.totalFrames === want.totalFrames;
  console.log(`foes=${foes}  FIXED startup=${fixed.startupFrames}f total=${fixed.totalFrames}f` +
              `   (unfixed startup=${broken.startupFrames}f total=${broken.totalFrames}f)` +
              `   ${ok ? 'matches 1v1' : 'DIVERGES'}`);
  if (!ok) bad++;
}
const b2 = run(2, false);
console.assert(b2.startupFrames < want.startupFrames, 'the old code should have been faster');
console.assert(bad === 0, 'fixed timings must not depend on the number of foes');
console.log(bad === 0 ? 'PASS — startup/active are frame-based, not foe-count-based' : 'FAIL');
process.exit(bad === 0 ? 0 : 1);
