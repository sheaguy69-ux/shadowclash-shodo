#!/usr/bin/env node
// "A hitbox that outlives its recovery is a free move." executeAttack floors
// recoveryTimer against the longest box the swing actually spawned, because every
// branch except the heavy one just wrote `authored / speedScale` — and speedScale is
// curSpeed/6, where curSpeed carries CHAIN FRENZY (x1.2) and TAG HEAT (up to x1.65).
// Mirrors the shipped tail of executeAttack.
const MARGIN = 0.03;

// boxes: [{delay, duration}], animS: the move's own animation length in seconds
function floorRecovery(authored, speedScale, boxes, animS) {
  let rec = authored / speedScale;
  let end = 0;
  for (const h of boxes) {
    const d = h.duration || 0;
    if (animS > 0 && d > animS) continue;      // travelling box, own state machine
    end = Math.max(end, (h.delay || 0) + d);
  }
  if (end > 0) rec = Math.max(rec, end + MARGIN);
  return { rec: +rec.toFixed(4), boxEnd: +end.toFixed(4) };
}

const HEAVY = [{ delay: 0.1386, duration: 0.07 }];   // startup 0.42*330ms, active 0.07
const ANIM = 0.330, AUTHORED = 0.45;

const normal  = floorRecovery(AUTHORED, 1.5, HEAVY, ANIM);
const frenzy  = floorRecovery(AUTHORED, 1.8, HEAVY, ANIM);
const extreme = floorRecovery(AUTHORED, 6.0, HEAVY, ANIM);
const unfloored = +(AUTHORED / 6.0).toFixed(4);

console.log('normal   speedScale 1.5 ->', normal);
console.log('frenzy   speedScale 1.8 ->', frenzy);
console.log('extreme  speedScale 6.0 ->', extreme, ' (unfloored would be', unfloored + ')');

// the buff must still speed recovery up when that is safe
console.assert(frenzy.rec < normal.rec, 'frenzy must still shorten recovery');
// but never below the box
for (const [n, t] of [['normal', normal], ['frenzy', frenzy], ['extreme', extreme]])
  console.assert(t.rec >= t.boxEnd, `${n}: recovery must outlive the hitbox`);
// and at an extreme divisor the floor must actually bind
console.assert(extreme.rec === +(extreme.boxEnd + MARGIN).toFixed(4), 'floor must bind');
console.assert(unfloored < extreme.boxEnd, 'the bug should reproduce unfloored');

// a travelling box (meteor descent: 1.2s active against a 0.9s anim) is NOT floored against
const meteor = floorRecovery(0, 1, [{ delay: 0.18, duration: 1.2 }], 0.9);
console.assert(meteor.boxEnd === 0, 'a box outliving its animation must be skipped');
console.log('meteor descent skipped ->', meteor);

const ok = frenzy.rec < normal.rec && extreme.rec >= extreme.boxEnd
        && unfloored < extreme.boxEnd && meteor.boxEnd === 0;
console.log(ok ? 'PASS — a buff can make you quicker, never safe behind your own swing' : 'FAIL');
process.exit(ok ? 0 : 1);
