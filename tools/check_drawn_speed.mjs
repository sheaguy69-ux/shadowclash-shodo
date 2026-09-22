#!/usr/bin/env node
// "THE STATE STRETCHES TO THE ART, NOT THE ART TO THE STATE" (owner, SHEET_V 490)
// — made roster-wide at 492. Mirrors floorCommitment() + the executeAttack wrapper
// gating: recovery >= box + 0.03, anim >= box, state >= anim; travelling boxes
// skipped; floors run only when THIS press authored an animation; a mid-chain
// press that cannot cancel buffers before touching anything.
const MARGIN = 0.03;

function floorCommitment(p) {
  const animS = (p.attackAnim && p.attackAnim.dur || 0) / 1000;
  let boxEnd = 0;
  for (const h of p.hitboxes) {
    const d = h.duration || 0;
    if (animS > 0 && d > animS) continue;              // travelling box, own state machine
    boxEnd = Math.max(boxEnd, (h.delay || 0) + d);
  }
  if (boxEnd > 0) {
    p.recoveryTimer = Math.max(p.recoveryTimer, boxEnd + MARGIN);
    if (p.attackAnim) p.attackAnim.dur = Math.max(p.attackAnim.dur, boxEnd * 1000);
  }
  if (p.attackAnim) p.recoveryTimer = Math.max(p.recoveryTimer, p.attackAnim.dur / 1000);
  return p;
}

// The mid-chain companion gate's cancel predicate (mirrors executeAttack).
function canCancel(type, tier, inWindow) {
  return type === 'heavy'   ? (tier === 1 && inWindow)
       : type === 'special' ? (tier < 3 && inWindow)
       : false;                                         // a light never cancels mid-chain
}

const ok = (c, m) => { console.assert(c, m); if (!c) process.exitCode = 1; };

// (3) state >= anim — Shin's shuriken volley shipped at 67%: authored 0.22/tax(1.5)
// = 0.1467s state against 220ms art, and it has NO hitbox (projectiles), so only
// the anim floor can save it.
const shin = floorCommitment({ attackAnim: { dur: 220 }, recoveryTimer: 0.22 / 1.5, hitboxes: [] });
ok(Math.abs(shin.recoveryTimer - 0.22) < 1e-9, 'volley state must reach its 220ms art');

// (1)+(2) recovery >= box+margin, anim >= box — the Iai: 620ms anim, 0.52s rec, noto box to 0.64s.
const iai = floorCommitment({ attackAnim: { dur: 620 }, recoveryTimer: 0.52,
                              hitboxes: [{ delay: 0.50, duration: 0.14 }] });
ok(iai.attackAnim.dur === 640, 'iai anim must reach the noto contact (620 -> 640)');
ok(Math.abs(iai.recoveryTimer - 0.67) < 1e-9, 'iai recovery must outlive the box');

// travelling box (meteor: 1.2s active vs 0.9s anim) is not floored against.
const met = floorCommitment({ attackAnim: { dur: 900 }, recoveryTimer: 1.2,
                              hitboxes: [{ delay: 0.18, duration: 1.2 }] });
ok(met.attackAnim.dur === 900 && met.recoveryTimer === 1.2, 'travelling box must be skipped');

// no anim authored (buffered no-op / non-anim path): nothing stretches.
const nop = floorCommitment({ attackAnim: null, recoveryTimer: 0.2, hitboxes: [] });
ok(nop.recoveryTimer === 0.2, 'no authored anim -> no state stretch');

// a floor never SHORTENS: slow bodies (Mokurai 0.72s state vs 320ms art) keep their pacing.
const mok = floorCommitment({ attackAnim: { dur: 320 }, recoveryTimer: 0.72, hitboxes: [] });
ok(mok.recoveryTimer === 0.72 && mok.attackAnim.dur === 320, 'floors must never shorten');

// mid-chain gate: light mash buffers, heavy cancels only from tier 1 in window.
ok(!canCancel('light', 1, true), 'light must buffer mid-chain');
ok(canCancel('heavy', 1, true) && !canCancel('heavy', 1, false), 'heavy cancels only in window');
ok(canCancel('special', 2, true) && !canCancel('special', 3, true), 'special caps at tier 3');

console.log(process.exitCode ? 'FAIL' : 'PASS — every fighter plays at drawn speed, and a mash touches nothing');
process.exit(process.exitCode || 0);
