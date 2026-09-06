// BLADE LOCK — logic check for the bind's resolution rules.
//
// The three lock functions are pulled STRAIGHT OUT of web/index.html and run against
// stubbed globals, so this tests the shipping code rather than a copy that can drift
// away from it. A copy-paste test would keep passing after the engine changed, which is
// the failure mode worth designing out.
//
// What it pins down — the rules that decide matches, and that a static read of the diff
// cannot confirm:
//   · a bind always ends: the timer expires even if neither side ever presses
//   · a tie throws BOTH off, so the outcome never falls to update order
//   · pulling LOCK_MARGIN ahead breaks the bind early, before the timer runs out
//   · the winner's cut comes THROUGH the lock: the loser takes damage, is stunned and
//     knocked away, and the winner emerges on the far side (a cross-up) facing back in
//   · nobody is teleported further than their opponent when the bind snaps to distance
//
// Run: node tools/blade_lock_check.mjs
import { readFileSync } from 'fs';
import { runInNewContext } from 'node:vm';

const src = readFileSync(new URL('../web/index.html', import.meta.url), 'utf8');

// Lift the constants and the three functions by name. Anchored on `function <name>(`
// through the line that closes it at the same indentation, which is how the file is
// formatted throughout.
function lift(name) {
    const m = src.match(new RegExp(`\\n(\\s*)function ${name}\\([^)]*\\) \\{[\\s\\S]*?\\n\\1\\}`, ''));
    if (!m) throw new Error(`could not lift ${name}() out of web/index.html`);
    return m[0];
}
const consts = ['LOCK_DUR', 'LOCK_MARGIN', 'LOCK_SEP', 'LOCK_CPU_RATE', 'LOCK_MIN_HOLD',
                'LOCK_DMG', 'LOCK_PUSH', 'LOCK_CROSS_GAP'].map(n => {
    const m = src.match(new RegExp(`const ${n} = ([0-9.]+)`));
    if (!m) throw new Error(`could not read ${n} out of web/index.html`);
    return `const ${n} = ${m[1]};`;
}).join('\n');

const clearArtMethod = src.match(/\n(\s*)clearMoveArt\(\) \{[\s\S]*?\n\1\}/)[0];
const clearArt = new Function('return ({' + clearArtMethod + '}).clearMoveArt')();

const STATE = { IDLE: 'IDLE', STUNNED: 'STUNNED', BLADE_LOCK: 'BLADE_LOCK', ATTACK_HEAVY: 'ATTACK_HEAVY' };

// enterBladeLock reads each fighter's own measured reach out of the loaded sheet manifest
// (SPRITES[name].lockReach, written by pack_lock_cells.py). The harness owns this object so
// the tests can drive both paths: a sheet WITH lock cells packed, and one without.
let SPRITES = {};
let sfxLog = [], slashLog = [], strikeLog = [], shake = 0, flash = 0, hitstop = 0;
let p2Cpu = false;   // test knob: is P2 CPU-driven (drives the mash clock)

function mkPlayer(name, x, specName = 'kael') {
    return { name, x, y: 100, width: 30, height: 48, facing: 1, isGrounded: true, vx: 0,
             spec: { name: specName },
             hp: 150,
             hitboxes: [], state: STATE.IDLE, stunTimer: 0, recoveryTimer: 0, staggerMeter: 0,
             dashTimer: 0, lockT: 0, lockMash: 0, lockCpuT: 0,
             pendingSlash: null, pendingChainStarter: null, attackHasConnected: false,
             fxSched: [], clearMoveArt: clearArt,
             isCpuDriven() { return this === player2 && p2Cpu; },
             // Minimal mirror of Player.takeDamage — just the effects the lock payout
             // depends on: the loser takes the hit, is stunned, and is knocked away
             // from the winner's (new) position.
             takeDamage(dmg, attacker, sourceHitbox = null) {
                 this.hp -= dmg;
                 this.state = STATE.STUNNED;
                 this.stunTimer = 0.35 + dmg * 0.01;
                 const push = sourceHitbox ? sourceHitbox.pushback : 80;
                 this.vx = attacker.facing * (100 + push);
             } };
}

const harness = `
${consts}
${lift('bladeLockFrame')}
${lift('cancelBladeLock')}
${lift('fitBladeLockPair')}
${lift('updateBladeLock')}
${lift('resolveBladeLock')}
${lift('enterBladeLock')}
return { updateBladeLock, resolveBladeLock, enterBladeLock, cancelBladeLock, bladeLockFrame, LOCK_DUR, LOCK_MARGIN, LOCK_SEP, LOCK_MIN_HOLD };
`;

let player1, player2;
const api = new Function('STATE', 'sfx', 'createSparks', 'createSmokePuff', 'spawnSlash', 'canvas', 'particles',
    'get_player1', 'get_player2', 'setShake', 'setFlash', 'setHitstop', 'get_SPRITES', 'isP2Human', 'spawnStrike', `
    Object.defineProperty(globalThis, 'SPRITES', { get: get_SPRITES, configurable: true });
    const screenShakeHolder = {};
    const createBladeSparks = createSparks;
    let screenShakeAmount = 0, flashAmount = 0, hitstopRemaining = 0, cpuTier = 1;
    Object.defineProperty(globalThis, 'player1', { get: get_player1, configurable: true });
    Object.defineProperty(globalThis, 'player2', { get: get_player2, configurable: true });
    globalThis.p2Live = true;
    ${harness}
`)(STATE, k => sfxLog.push(k), () => {}, () => {}, (p, type) => slashLog.push({ name: p.name, type }), { width: 1200 }, [],
   () => player1, () => player2, v => shake = v, v => flash = v, v => hitstop = v,
   () => SPRITES, () => !p2Cpu,
   (x, y, o) => strikeLog.push({ x, y, mirror: o && o.mirror }));

let pass = 0, fail = 0;
const ok = (cond, label, detail = '') => {
    if (cond) { pass++; console.log(`  ok    ${label}`); }
    else { fail++; console.log(`  FAIL  ${label}${detail ? '   ' + detail : ''}`); }
};

function fresh(x1 = 400, x2 = 520, sprites = {}) {
    player1 = mkPlayer('p1', x1, 'kael'); player2 = mkPlayer('p2', x2, 'mizu');
    SPRITES = sprites;
    sfxLog = [];
    slashLog = [];
    strikeLog = [];
    p2Cpu = false;
    return [player1, player2];
}

console.log('\nBLADE LOCK — resolution rules\n');

// 1. entering the bind
{
    const [a, b] = fresh(400, 560);
    a.hitboxes.push({ w: 10 }); b.hitboxes.push({ w: 10 });
    api.enterBladeLock(a, b);
    ok(a.state === 'BLADE_LOCK' && b.state === 'BLADE_LOCK', 'both fighters enter BLADE_LOCK');
    ok(a.lockT === api.LOCK_DUR && b.lockT === api.LOCK_DUR, 'both get the full duration');
    ok(a.stunTimer >= api.LOCK_DUR, 'the stun freeze is armed, so no action can escape');
    ok(a.hitboxes.length === 0 && b.hitboxes.length === 0, 'live hitboxes are cleared');
    ok(a.facing === 1 && b.facing === -1, 'they turn to face each other');
    const sep = Math.abs((a.x + a.width / 2) - (b.x + b.width / 2));
    ok(Math.abs(sep - api.LOCK_SEP) < 0.01, `separation snaps to LOCK_SEP (${sep.toFixed(1)}px)`,
       `expected ${api.LOCK_SEP}`);
}

// 2. NOBODY IS DRAGGED FURTHER THAN THEIR OPPONENT — an asymmetric snap reads as a glitch
{
    const [a, b] = fresh(400, 560);
    const ax0 = a.x, bx0 = b.x;
    api.enterBladeLock(a, b);
    const moved = [Math.abs(a.x - ax0), Math.abs(b.x - bx0)];
    ok(Math.abs(moved[0] - moved[1]) < 0.01,
       'the snap to distance moves both fighters equally',
       `p1 moved ${moved[0].toFixed(1)}, p2 moved ${moved[1].toFixed(1)}`);
}

// 3. A BIND ALWAYS ENDS, even with zero presses from either side
{
    const [a, b] = fresh();
    api.enterBladeLock(a, b);
    let frames = 0, done = false;
    while (frames++ < 600 && !done) done = api.updateBladeLock(a, b, 1 / 60);
    ok(done, 'the bind resolves on its own with no input at all');
    ok(frames < 600, `it ends in ${frames} frames (~${(frames / 60).toFixed(2)}s), not forever`);
    ok(a.lockT === 0 && b.lockT === 0, 'both timers are cleared on resolve');
}

// 4. A TIE THROWS BOTH OFF — the outcome must never fall to update order
{
    const [a, b] = fresh();
    api.enterBladeLock(a, b);
    let done = false, n = 0;
    while (n++ < 600 && !done) {
        a.lockMash = b.lockMash = n;          // dead even, every frame
        done = api.updateBladeLock(a, b, 1 / 60);
    }
    ok(a.state === 'STUNNED' && b.state === 'STUNNED', 'a tie stuns BOTH fighters');
    ok(Math.sign(a.vx) !== Math.sign(b.vx), 'a tie pushes them in opposite directions',
       `p1 vx ${a.vx}, p2 vx ${b.vx}`);
}

// 5. EARLY BREAK — pulling ahead ends it before the timer
{
    const [a, b] = fresh();
    api.enterBladeLock(a, b);
    let done = false, n = 0;
    while (n++ < 600 && !done) { a.lockMash += 2; done = api.updateBladeLock(a, b, 1 / 60); }
    ok(done && a.lockT === 0, 'a mash lead breaks the bind');
    ok(n < api.LOCK_DUR * 60 - 2, `it breaks EARLY — ${n} frames, under the ${Math.round(api.LOCK_DUR * 60)}-frame cap`);
    // A TURBO PAD MUST NOT FLICKER THE BIND. This test mashes 2x per frame (120/s, far past
    // human), so without the floor it resolved in 4 frames — 67ms, no struggle to read.
    ok(n >= api.LOCK_MIN_HOLD * 60,
       `even an inhuman mash cannot break it before LOCK_MIN_HOLD (${n} frames >= ${Math.round(api.LOCK_MIN_HOLD * 60)})`);
    ok(a.state === 'IDLE' && b.state === 'STUNNED', 'winner is freed, loser is stunned');
    ok(a.recoveryTimer > 0, 'the winner still carries a short recovery after the cross-up');
    ok(slashLog.some(s => s.name === 'p1' && s.type === 'ATTACK_HEAVY'), 'the winner draws a heavy slash through the bind');
    ok(strikeLog.length === 1 && strikeLog[0].mirror === a.facing,
       `the winner's strike FX fires across the loser, mirrored to the winner's new facing`);
    ok(b.hp < 150, `the winner's tech made it through — the loser takes damage (${150 - b.hp}hp)`);
    ok(b.stunTimer > a.stunTimer, 'the loser is open longer than the winner');
    ok(a.x + a.width / 2 > b.x + b.width / 2, 'the winner emerges on the far side of the loser');
    ok(a.facing === -1, 'the winner turns to face back in at the loser');
    ok(Math.sign(b.vx) === a.facing, 'the loser is knocked away from the winner\'s new position');
}

// 6. the winner is whoever actually mashed more — either side, no player bias
for (const [lead, expectWin, expectLose] of [['p1', 'p1', 'p2'], ['p2', 'p2', 'p1']]) {
    const [a, b] = fresh();
    api.enterBladeLock(a, b);
    let done = false, n = 0;
    while (n++ < 600 && !done) {
        if (lead === 'p1') a.lockMash += 2; else b.lockMash += 2;
        done = api.updateBladeLock(a, b, 1 / 60);
    }
    const winner = a.state === 'IDLE' ? 'p1' : 'p2';
    ok(winner === expectWin, `${lead} mashing harder wins the bind`, `won: ${winner}`);
}

// 7. CPU MASHES — an unattended P2 must not lose every bind by default
{
    const [a, b] = fresh();
    p2Cpu = true;                           // P2 is CPU now
    api.enterBladeLock(a, b);
    // Checked MID-BIND: after resolve every counter is zeroed, so asserting on the
    // cleared value would pass whether the CPU ever pressed or not.
    for (let i = 0; i < 20; i++) api.updateBladeLock(a, b, 1 / 60);
    ok(b.lockMash > 0, `the CPU side actually mashes (${b.lockMash} presses in 20 frames)`);
    ok(a.lockMash === 0, 'the human side banks nothing without input');
    let done = false, n = 0;
    while (n++ < 600 && !done) done = api.updateBladeLock(a, b, 1 / 60);
    ok(b.lockMash === 0 && a.lockMash === 0, 'counters are cleared after resolve');
    ok(b.state === 'IDLE' && a.state === 'STUNNED',
       'an idle human LOSES to the CPU — the bind is a contest, not a freebie');
    p2Cpu = false;
}

// ---------------------------------------------------------------------------------
// PER-HITBOX WEAPON MATERIAL — lifted from web/index.html the same way, because these
// four one-liners decide which attacks can bind at all, and getting them wrong is silent:
// nothing crashes, a fighter just quietly stops (or starts) binding.
console.log('\nPER-HITBOX MATERIAL — who can bind\n');

// Lifted by scanning LINES rather than with a regex: these declarations span two lines
// and contain the arrow-function bodies, so a character-class regex either stops at the
// first semicolon inside a body or swallows the rest of the file.
const srcLines = src.split('\n');
function liftConst(name) {
    const start = srcLines.findIndex(l => l.trimStart().startsWith(`const ${name} =`));
    if (start < 0) throw new Error(`could not lift ${name} out of web/index.html`);
    const out = [];
    for (let i = start; i < srcLines.length; i++) {
        out.push(srcLines[i]);
        // Test the terminator with any trailing line-comment removed — several of these
        // declarations end `…;   // why`, and without this the scan runs past the semicolon
        // and swallows the NEXT declaration too (which then double-declares and throws).
        if (srcLines[i].replace(/\/\/.*$/, '').trimEnd().endsWith(';')) break;
    }
    return out.join('\n') + '\n';
}
const matSrc = ['WEAPON_MAT', 'weaponMat', 'isMetal', 'bladeless', 'canBind', 'weaponBind',
                'bladeOnBlade', 'woodInvolved'].map(liftConst).join('');
const mats = new Function(`${matSrc}
    return { WEAPON_MAT, weaponMat, isMetal, bladeless, canBind, weaponBind, bladeOnBlade,
             woodInvolved };`)();

const F = (id, fistMode = false) => ({ spec: { id }, fistMode });
const KAEL = F(0), SHIN = F(2), MIZU = F(1), BUDDHA = F(6), ONI = F(8), ONI_FIST = F(8, true);
const box = (mat) => ({ canClash: true, mat });
const bare = { canClash: true };

// the fighter default still decides when a hitbox names no material
ok(mats.weaponMat(SHIN, bare) === 'mail', "shin's default material is still mail");
ok(mats.weaponMat(KAEL, bare) === 'steel', 'an unlisted fighter still defaults to steel');
ok(mats.weaponMat(ONI_FIST, bare) === 'flesh', 'fist-mode oni is still flesh');
ok(mats.weaponMat(MIZU, undefined) === 'wood', 'no hitbox at all still resolves to the fighter');

// the whole point: one fighter, two materials
ok(mats.weaponMat(SHIN, box('steel')) === 'steel', "a hitbox's own material overrides the fighter");
ok(!mats.bladeOnBlade(SHIN, KAEL, bare, bare), "shin's MAIL strikes still do not bind a katana");
ok(mats.bladeOnBlade(SHIN, KAEL, box('steel'), bare), 'shin WITH A KUNAI IN HAND binds a katana');

// 'chain' rings but has no edge, so it must never bind
ok(!mats.isMetal('chain'), 'chain is deliberately NOT metal — no edge to catch');
ok(!mats.bladeOnBlade(KAEL, KAEL, box('chain'), bare), 'a chain cannot bind a blade');
ok(!mats.bladeless('chain'), 'chain still catches light — it is not bladeless');

// nothing else moved
ok(mats.bladeOnBlade(KAEL, ONI, bare, bare), "oni's armed claws still bind a katana");
ok(!mats.bladeOnBlade(KAEL, BUDDHA, bare, bare), 'flesh never binds');
ok(!mats.bladeOnBlade(KAEL, MIZU, bare, bare), 'a wooden bo does not bind steel');
ok(mats.woodInvolved(KAEL, MIZU, bare, bare), "but the bo still reads as wood for the clash sound");
ok(!mats.bladeOnBlade(KAEL, KAEL, { canClash: false }, bare), 'a kick never binds, whatever is held');
// a flesh-material box on an armed fighter — the case that lets oni have both forms
ok(!mats.bladeOnBlade(ONI, KAEL, box('flesh'), bare),
   'a FLESH hitbox on an armed fighter does not bind (oni bare fist)');

// ---------------------------------------------------------------------------------
// STRUCTURAL GUARD — every chain strike must declare mat:'chain'.
//
// The predicate tests above prove a chain CANNOT bind. They cannot prove that exile's
// actual moves are tagged as chain, and that is the half that rots: someone adds her a
// new chain move next month, forgets `mat`, and it silently binds like a sword because
// her fighter default is steel. Nothing crashes and no test fails. So this walks the real
// source instead — for every throwChain/orbitChain call that HAS a hitbox next to it, the
// hitbox must carry the material.
console.log("\nSTRUCTURAL — exile's chain strikes are all tagged\n");

const chainCalls = [];
srcLines.forEach((l, i) => {
    if (/this\.(throwChain|throwChainUp|throwChainDown|orbitChain)\(/.test(l)) chainCalls.push(i);
});
ok(chainCalls.length > 0, `found ${chainCalls.length} chain-throw call sites to check`);

const untagged = [];
let withBox = 0;
for (const i of chainCalls) {
    // the hitbox for a chain strike is spawned just before the rope is thrown
    let boxLine = -1;
    for (let j = i; j > Math.max(0, i - 6); j--) {
        if (srcLines[j].includes('spawnHitbox(')) { boxLine = j; break; }
    }
    if (boxLine < 0) continue;                       // visual-only rope (anchor, grapple) — fine
    withBox++;
    // the opts object can wrap onto the next line
    const decl = srcLines[boxLine] + ' ' + (srcLines[boxLine + 1] || '');
    if (!decl.includes("mat: 'chain'")) untagged.push(boxLine + 1);
}
ok(withBox > 0, `${withBox} of them spawn a hitbox`);
ok(untagged.length === 0,
   'every chain strike that spawns a hitbox declares mat:\'chain\'',
   untagged.length ? `untagged at web/index.html line(s): ${untagged.join(', ')}` : '');

// ---------------------------------------------------------------------------------
// FRAME ROUTING — the lockN cells must map to the right BEATS at any cell count.
//
// The owner intends to add in-between cells to smooth the strain, so the router reads
// however many lockN cells the sheet has rather than naming two. This pins the mapping at
// 6 cells and at 9, because an off-by-one here is silent: it plays a real cell at the wrong
// moment, which looks like a slightly-wrong animation, not like a bug.
console.log('\nFRAME ROUTING — lockN cells to beats\n');

// Exercise the SHIPPING router, including the first loop transition and form-2 priority.
for (const n of [6, 9, 10, 12]) {
    const F = Object.fromEntries(Array.from({length:n}, (_, i) => ['lock' + (i + 1), i + 1]));
    const p = { state: STATE.BLADE_LOCK, lockT: api.LOCK_DUR };
    const frame = elapsed => { p.lockT = api.LOCK_DUR - elapsed; return api.bladeLockFrame(p, F); };
    ok(frame(0) === 1 && frame(0.08) === 1, `${n} cells: catch is shown first`);
    ok(frame(0.10) === 2 && frame(0.17) === 2, `${n} cells: settle is shown before straining`);
    const strain = Array.from({length:n-4}, (_, i) => frame(0.181 + i / 12));
    ok(strain.join() === Array.from({length:n-4}, (_, i) => i + 3).join(),
       `${n} cells: every strain pose plays in order, no catch/outcomes repeat`);
    p.lockOutcome = 'win'; p.lockOutcomeT = 0.1; p.state = STATE.IDLE;
    ok(api.bladeLockFrame(p, F) === n-1, `${n} cells: IDLE winner renders win`);
    p.lockOutcome = 'lose'; p.state = STATE.STUNNED;
    ok(api.bladeLockFrame(p, F) === n, `${n} cells: stunned loser renders lose`);
    p.lockOutcomeT = 0;
    ok(api.bladeLockFrame(p, F) === undefined, `${n} cells: expired outcome releases the normal router`);
}
for (const n of [0, 1, 2]) {
    const F = Object.fromEntries(Array.from({length:n}, (_, i) => ['lock' + (i + 1), i + 1]));
    const p = {state: STATE.BLADE_LOCK, lockT: 0.4};
    ok(api.bladeLockFrame(p, F) === (n || undefined), `${n} cells: partial sheet stays defined or falls back`);
}
{
    // A second-form idle can no longer claim the winner before his outcome is drawn.
    const F = {lock1:10, lock2:11, lock3:12, lock4:13, lock5:14, lock6:15};
    const p = {state:STATE.IDLE, lockT:0, lockOutcome:'win', lockOutcomeT:.1};
    const route = runInNewContext(lift('spriteFrameIndexRaw') + '; spriteFrameIndexRaw(p,F)', {
        p,F,bladeLockFrame:api.bladeLockFrame,
        shinF2Frame:()=>999,tsubasaF2Frame:()=>998,mizuF2Frame:()=>997,
    });
    ok(route === 14, 'real sprite router draws the win before form-2 idle');
}

// ---------------------------------------------------------------------------------
// PER-FIGHTER BIND REACH — the art decides the spacing once cells are packed.
//
// This is worth testing because it is a SILENT behaviour change: with no lockReach in the
// manifest the bind must space exactly as it always did, and with one it must use it. Get the
// fallback wrong and every fighter without packed cells binds at the wrong distance, with
// nothing to indicate it but the picture.
console.log('\nPER-FIGHTER BIND REACH\n');

const sep = (a, b) => Math.abs((a.x + a.width / 2) - (b.x + b.width / 2));

{
    const [a, b] = fresh(400, 560, {});          // no sheets loaded at all
    api.enterBladeLock(a, b);
    ok(Math.abs(sep(a, b) - api.LOCK_SEP) < 0.01,
       `no lockReach -> falls back to LOCK_SEP exactly (${sep(a, b).toFixed(1)}px)`,
       `expected ${api.LOCK_SEP}`);
}
{
    // both fighters carry a measured reach: separation is the SUM of the two, not 2x either
    const [a, b] = fresh(400, 560, { kael: { lockReach: 20 }, mizu: { lockReach: 40 } });
    api.enterBladeLock(a, b);
    ok(Math.abs(sep(a, b) - 60) < 0.01,
       `two measured reaches sum (20 + 40 = 60px, got ${sep(a, b).toFixed(1)})`);
}
{
    // a short-reach fighter is stood CLOSER — the whole point of the change
    const [a, b] = fresh(400, 560, { kael: { lockReach: 15 }, mizu: { lockReach: 15 } });
    api.enterBladeLock(a, b);
    ok(sep(a, b) < api.LOCK_SEP,
       `a close-bound pair stands closer than the shared constant (${sep(a, b).toFixed(1)} < ${api.LOCK_SEP})`);
}
{
    // one sheet packed, one not: the unpacked side still gets the old half-constant
    const [a, b] = fresh(400, 560, { kael: { lockReach: 10 } });
    api.enterBladeLock(a, b);
    ok(Math.abs(sep(a, b) - (10 + api.LOCK_SEP / 2)) < 0.01,
       `mixed packed/unpacked pairs still meet (${sep(a, b).toFixed(1)}px)`);
}
{
    // ⛔ WITH UNEVEN REACHES THE BODIES ARE NOT SYMMETRIC ABOUT THE MIDPOINT — and must not be.
    // A short-reach fighter STANDS CLOSER; that is the entire point. My first version of this
    // test asserted body symmetry and failed, because it was asserting the wrong invariant.
    //
    // What actually has to hold is that the CONTACT POINT does not move: each fighter sits
    // exactly their own reach from the original midpoint, so the weapons still meet where the
    // clash happened rather than the whole bind sliding down the stage.
    const [a, b] = fresh(400, 560, { kael: { lockReach: 10 }, mizu: { lockReach: 50 } });
    const mid0 = ((a.x + a.width / 2) + (b.x + b.width / 2)) / 2;
    api.enterBladeLock(a, b);
    const ac = a.x + a.width / 2, bc = b.x + b.width / 2;
    ok(Math.abs((mid0 - ac) - 10) < 0.01 && Math.abs((bc - mid0) - 50) < 0.01,
       'each fighter sits at their OWN reach from the original contact point',
       `p1 ${(mid0 - ac).toFixed(1)} (want 10), p2 ${(bc - mid0).toFixed(1)} (want 50)`);
    ok(Math.abs((bc - ac) - 60) < 0.01, 'so the weapons still meet: 10 + 50 = 60px apart');
}

// ---------------------------------------------------------------------------------
// WHAT CAN BIND vs WHAT RINGS — owner ruling: wood binds, so mizu can lock.
//
// These are two DIFFERENT predicates on purpose and conflating them is the whole risk. If
// wood were made to count as metal instead, mizu would bind AND her bo would start ringing
// like a katana on every guard and clean hit — a silent audio regression across the roster.
console.log('\nWHAT CAN BIND — wood binds, but does not ring\n');

ok(mats.canBind('steel') && mats.canBind('iron'), 'steel and iron bind');
ok(mats.canBind('wood'), 'WOOD BINDS — mizu can lock (owner ruling)');
ok(!mats.canBind('flesh'), 'flesh cannot bind — no weapon at all');
ok(!mats.canBind('mail'), "mail cannot bind — shin's chainmail is under his clothes, not in hand");
ok(!mats.canBind('chain'), 'chain cannot bind — no rigid length to brace against');

// the separation that matters: mizu BINDS a katana but must never RING like one
ok(mats.weaponBind(MIZU, KAEL, bare, bare), "mizu's bo BINDS kael's katana");
ok(!mats.bladeOnBlade(MIZU, KAEL, bare, bare), "...but it still does NOT ring as steel");
ok(mats.woodInvolved(MIZU, KAEL, bare, bare), '...it reads as WOOD for the clash sound');

// and everything that must still not bind
ok(!mats.weaponBind(BUDDHA, KAEL, bare, bare), 'buddha never binds');
ok(!mats.weaponBind(SHIN, KAEL, bare, bare), "shin's fists never bind");
ok(mats.weaponBind(SHIN, KAEL, box('steel'), bare), 'shin WITH A KUNAI still binds');
ok(!mats.weaponBind(KAEL, KAEL, box('chain'), bare), "exile's chain still never binds");
ok(!mats.weaponBind(ONI, KAEL, box('flesh'), bare), "oni's fist form still never binds");
ok(mats.weaponBind(ONI, MIZU, bare, bare), "oni's armed claws bind a wooden bo");
ok(!mats.weaponBind(KAEL, KAEL, { canClash: false }, bare), 'a kick still never binds');


// ---- WHO IS ALLOWED TO BIND AT ALL ------------------------------------------
// The rules above decide whether two weapons CAN catch. This section pins the
// entry gate that decides whether the game lets them — lifted from the source,
// so it fails if the gate is loosened again rather than silently passing.
//
// It was loosened once: a newer `bindPair` branch was added ABOVE the steel-only
// kiai block and returned first, and it carried neither the floor test nor the
// banner the older block still had. The older block's own comment states the
// intent — "a mid-air lockup has no floor to brace against and would just hang
// two bodies in space until the timer ran out" — and two air heavies that caught
// each other did exactly that, silently.
const gate = src.match(/if \(bindPair && clashCd <= 0([\s\S]{0,220}?)\) \{/);
ok(!!gate, 'the bind entry gate is still findable in web/index.html');
const gateSrc = gate ? gate[1] : '';
ok(/a\.isGrounded/.test(gateSrc) && /b\.isGrounded/.test(gateSrc),
   'A BIND IS GROUNDED-ONLY — both fighters, on the live bindPair branch');
ok(/!a\.lock/.test(gateSrc) && /!b\.lock/.test(gateSrc),
   'neither side may already be locked (no re-entering a live bind)');
ok(/a\.stunTimer <= 0/.test(gateSrc) && /b\.stunTimer <= 0/.test(gateSrc),
   'a stunned fighter cannot bind');
ok(/roundBanner/.test(src.slice(src.indexOf('if (bindPair && clashCd <= 0'),
                                 src.indexOf('if (bindPair && clashCd <= 0') + 900)),
   'the BLADE LOCK banner fires on the branch that actually runs');

// And the reason the old block below it is unreachable: every steel pair is also a
// bind pair, so `steelPair && ...` can never be true where `bindPair && ...` was
// false. Proved over the whole material matrix rather than asserted.
const MATS = ['steel', 'iron', 'wood', 'flesh', 'mail', 'chain'];
let shadowed = 0, exceptions = [];
for (const ma of MATS) for (const mb of MATS) {
  const A = box(ma), B = box(mb);
  const steelPair = mats.bladeOnBlade(KAEL, KAEL, A, B) && mats.bladeOnBlade(KAEL, KAEL, B, A);
  const bindPair  = mats.weaponBind(KAEL, KAEL, A, B)   && mats.weaponBind(KAEL, KAEL, B, A);
  if (steelPair && !bindPair) exceptions.push(`${ma}/${mb}`);
  if (steelPair) shadowed++;
}
ok(exceptions.length === 0,
   `every steel pair is also a bind pair (${shadowed} steel combos, ${exceptions.length} exceptions` +
   `${exceptions.length ? ': ' + exceptions.join(' ') : ''}) — so the old steel-only block below` +
   ' the bind branch is unreachable and was deleted');

// Windup boxes exist immediately but cannot touch another weapon yet.
for (const [delayA, delayB, want] of [[0.2, 0, false], [0, 0.2, false], [0.2, 0.2, false], [0, 0, true]]) {
    const a = mkPlayer('a', 100), b = mkPlayer('b', 100);
    a.hitboxes = [{ ox: 0, oy: 0, w: 40, h: 30, delay: delayA, duration: 0.1, canClash: true }];
    b.hitboxes = [{ ox: 0, oy: 0, w: 40, h: 30, delay: delayB, duration: 0.1, canClash: true }];
    let binds = 0;
    const hit = runInNewContext(lift('processWeaponClash') + '; processWeaponClash(a, b)', {
        a, b, bladeOnBlade: () => true, woodInvolved: () => false, weaponBind: () => true,
        clashCd: 0, CLASH_COOLDOWN: 1, enterBladeLock: () => binds++,
    });
    ok(hit === want && binds === Number(want)
       && a.hitboxes.length === Number(!want) && b.hitboxes.length === Number(!want),
       `clash waits for BOTH startups: delays ${delayA}/${delayB}`, `clashed=${hit}`);
}

// ---- BOUNDARIES, INTERRUPTION, INPUT AND CPU CLOCKS -----------------------
console.log('\nBIND INTEGRITY — walls, cancellation, input and clocks\n');
for (const [x1,x2] of [[10,30],[1140,1160],[30,10],[1160,1140]]) {
    const [a,b] = fresh(x1,x2, {kael:{lockReach:58},mizu:{lockReach:44}});
    api.enterBladeLock(a,b);
    ok(Math.abs(sep(a,b)-102)<.001 && Math.min(a.x,b.x)>=10
       && Math.max(a.x+a.width,b.x+b.width)<=1190, `wall entry ${x1}/${x2} keeps measured spacing inside arena`);
    a.lockMash = 8;
    api.resolveBladeLock(a,b);
    const gap = Math.max(a.x,b.x) - Math.min(a.x+a.width,b.x+b.width);
    ok(Math.abs(gap-8)<.001 && Math.min(a.x,b.x)>=10
       && Math.max(a.x+a.width,b.x+b.width)<=1190, `wall win ${x1}/${x2} crosses without overlap`);
    ok(a.facing === Math.sign(b.x-a.x) && b.facing === -a.facing, 'both face each other after cross-up');
}
{
    const [a,b] = fresh();
    a.thrustSlide = 1; a.speedTrail = 1; a.fxQueue = [{t:.2}]; a.fxSched.push({t:.3});
    a.attackAnim={dur:500}; a.moveArt='old'; a.bufferedAttack={ttl:1}; a.recoveryTimer=2;
    a._lt=99; a._ht=99;
    api.enterBladeLock(a,b);
    ok(!a.thrustSlide && !a.speedTrail && !a.fxQueue && !a.fxSched.length && !a.bufferedAttack,
       'bind cancels pending motion, attack FX and buffered swings');
    ok(!a.attackAnim && !a.moveArt && !a.recoveryTimer && a._lt < 0 && a._ht < 0,
       'shared art cancellation removes stale move/recovery/throw pairing');
    api.cancelBladeLock(a);
    ok(a.lockT===0 && b.lockT===0 && !a.lockFoe && !b.lockFoe && a.stunTimer===0 && b.stunTimer===0,
       'cancelling either partner releases the whole bind');
    ok(!api.updateBladeLock(a,b,.1) && a.hp===150 && b.hp===150, 'cancelled bind cannot pay out later');
}
{
    const [a,b]=fresh(); api.enterBladeLock(a,b); a.lockMash=8;
    b.takeDamage=function(){this.hp=0;this.state='KO';this.stunTimer=.9;};
    api.resolveBladeLock(a,b);
    ok(b.hp===0 && b.state==='KO' && b.stunTimer===.9 && b.lockOutcome==='lose',
       'winning cut preserves the damage handler KO state and still shows loss art');
}
for (const kind of ['hit','air','KO']) {
    const [a,b]=fresh(); api.enterBladeLock(a,b); a.lockMash=20;
    if(kind==='hit') { b.state=STATE.STUNNED; b.stunTimer=.7; }
    if(kind==='air') b.isGrounded=false;
    if(kind==='KO') { b.hp=0; b.state=STATE.STUNNED; b.stunTimer=1; }
    api.updateBladeLock(a,b,1/60);
    ok(!a.lockT && !b.lockT && a.hp===150 && b.hp===(kind==='KO'?0:150), `${kind} cancels without an extra cut`);
    if(kind!=='air') ok(b.state===STATE.STUNNED && b.stunTimer>0, `${kind} preserves the actual hit/KO state`);
}
{
    // Real training reset, with only unrelated stage/tether presentation stubbed.
    const [a,b]=fresh(); api.enterBladeLock(a,b);
    for(const p of [a,b])Object.assign(p,{maxHp:150,ghosts:[],echoTrail:[],kageTape:[],kageActs:[],dropTether(){}});
    const env={player1:a,player2:b,seedAbyss(){},cancelBladeLock:api.cancelBladeLock,
               canvas:{width:1200},GROUND_Y:600,STATE,trainingStats:{},clashCd:7};
    runInNewContext(lift('trainingReset')+'; trainingReset(false);',env);
    ok(!a.lockT && !b.lockT && !a.lockOutcomeT && !b.lockOutcomeT && env.clashCd===0,
       'training reset clears the contest, outcome art and cooldown');
}
{
    const takeDamage = src.match(/\n(\s*)takeDamage\([^)]*\) \{[\s\S]*?\n\1\}/)[0];
    const [a,b]=fresh(); api.enterBladeLock(a,b);
    b.rollIFrames=()=>false; b.fxSched=[];
    const env={gameMode:'2p',cancelBladeLock:api.cancelBladeLock,STATE,CRACK_TAKEN:1.2, b,a};
    // Stop at the first downstream hit bookkeeping; cancellation must already be done.
    b.grayHoldT=1;
    Object.defineProperty(b,'grayHoldT',{set(){throw new Error('hit reached');}});
    let reached=false;
    try {runInNewContext('const hit=({'+takeDamage+'}).takeDamage; hit.call(b,5,a);',env);}
    catch(e){reached=e.message==='hit reached';}
    ok(reached && !a.lockT && !b.lockT, 'real takeDamage cancels the pair at a confirmed hit');
}
{
    // Lift the full combat funnel: mashes must return BEFORE throwing/attack dispatch.
    const [a,b]=fresh(); api.enterBladeLock(a,b);
    let throws=0, attacks=0;
    for(const p of [a,b]) {p.executeThrow=()=>{throws++;return false;};p.executeAttack=()=>attacks++;}
    const env={player1:a,player2:b,isP2Human:()=>true,performance:{now:()=>500},
               P1_COMBAT_CODES:['KeyF','KeyG','KeyJ','KeyH'],gameMode:'2p'};
    runInNewContext(lift('fireCombatKey')+`; for(const key of ['KeyF','KeyG','KeyJ','KeyH','KeyI','KeyO','KeyU','KeyP']) {
        fireCombatKey(key,500,false); fireCombatKey(key,501,true);
    }`,env);
    ok(a.lockMash===4 && b.lockMash===4 && !throws && !attacks && a._lt<0 && b._ht<0,
       'real mash presses count once, ignore repeats and never arm throw/attack');
    a.isCpuDriven=()=>true; b.isCpuDriven=()=>true; env.isP2Human=()=>false;
    runInNewContext(lift('fireCombatKey')+`;fireCombatKey('KeyF',502);fireCombatKey('KeyI',502);`,env);
    ok(a.lockMash===4 && b.lockMash===4, 'spectator keys cannot boost either CPU');
}
for(const wood of [false,true]) {
    const [a,b]=fresh(); api.enterBladeLock(a,b,wood);a.lockMash=8;api.resolveBladeLock(a,b);
    ok(sfxLog.filter(k=>k===(wood?'clash_wood':'clash')).length===2
       && (!wood || !sfxLog.includes('clash')), `${wood?'wood':'metal'} uses its own bind entry/release sound`);
}
for(const hz of [30,60,120]) {
    for(const faster of [0,1]) {
        const [a,b]=fresh(); a.isCpuDriven=b.isCpuDriven=()=>true;p2Cpu=true;
        api.enterBladeLock(a,b);
        ok(a.lockCpuRate>=7.5*1.18*.88 && a.lockCpuRate<=7.5*1.18*1.12,
           `CPU cadence stays within its tier's bounded effort (${hz}Hz)`);
        // Reproducible independent rates, swapped across seats: scoring is time-based.
        a.lockCpuRate=faster===0?9.7:8; b.lockCpuRate=faster===1?9.7:8;
        a.lockCpuT=b.lockCpuT=0;
        for(let i=0;i<hz*2 && a.lockT>0;i++)api.updateBladeLock(a,b,1/hz);
        ok((faster===0?a:b).lockOutcome==='win', `${hz}Hz: either CPU can win from its own cadence`);
    }
}
p2Cpu=false;
{
    const p={lockOutcome:'win',lockOutcomeT:.18}; clearArt.call(p);
    ok(!p.lockOutcome && !p.lockOutcomeT, 'a new move releases old outcome art through the shared clear');
}
ok(/const CLASH_COOLDOWN = 10\.0/.test(src), 'owner ten-second cooldown is retained');

console.log(`\n  ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
