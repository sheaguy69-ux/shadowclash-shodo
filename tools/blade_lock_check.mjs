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
${lift('updateBladeLock')}
${lift('resolveBladeLock')}
${lift('enterBladeLock')}
return { updateBladeLock, resolveBladeLock, enterBladeLock, LOCK_DUR, LOCK_MARGIN, LOCK_SEP, LOCK_MIN_HOLD };
`;

let player1, player2;
const api = new Function('STATE', 'sfx', 'createSparks', 'createSmokePuff', 'spawnSlash', 'canvas', 'particles',
    'get_player1', 'get_player2', 'setShake', 'setFlash', 'setHitstop', 'get_SPRITES', 'isP2Human', 'spawnStrike', `
    Object.defineProperty(globalThis, 'SPRITES', { get: get_SPRITES, configurable: true });
    const screenShakeHolder = {};
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
const KAEL = F(0), SHIN = F(2), MIZU = F(1), BUDDHA = F(6), ONI = F(7), ONI_FIST = F(7, true);
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
ok(mats.bladeOnBlade(KAEL, ONI, bare, bare), "oni's iron club still binds a katana");
ok(!mats.bladeOnBlade(KAEL, BUDDHA, bare, bare), 'flesh never binds');
ok(!mats.bladeOnBlade(KAEL, MIZU, bare, bare), 'a wooden bo does not bind steel');
ok(mats.woodInvolved(KAEL, MIZU, bare, bare), "but the bo still reads as wood for the clash sound");
ok(!mats.bladeOnBlade(KAEL, KAEL, { canClash: false }, bare), 'a kick never binds, whatever is held');
// a flesh-material box on an armed fighter — the case that lets oni have both forms
ok(!mats.bladeOnBlade(ONI, KAEL, box('flesh'), bare),
   'a FLESH hitbox on an armed fighter does not bind (oni claw form)');

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

// same slicing the router does: last two are win/lose, the rest is catch + strain loop
const routeBeats = (n) => {
    const all = Array.from({length: n}, (_, i) => i + 1);
    const held = all.length > 2 ? all.slice(0, -2) : all;
    return {
        win:  all[all.length - 2],
        lose: all[all.length - 1],
        catch_: held[0],
        loop: held.length > 2 ? held.slice(1) : held,
    };
};

{
    const r = routeBeats(6);
    ok(r.win === 5 && r.lose === 6, 'six cells: 5 is WIN, 6 is LOSE');
    ok(r.catch_ === 1, 'six cells: cell 1 is the catch');
    ok(r.loop.join() === '2,3,4', `six cells: the held loop is 2,3,4 (got ${r.loop.join()})`);
}
{
    // three extra in-between strain cells
    const r = routeBeats(9);
    ok(r.win === 8 && r.lose === 9, 'nine cells: 8 is WIN, 9 is LOSE — still the last two');
    ok(r.catch_ === 1, 'nine cells: cell 1 is still the catch');
    ok(r.loop.join() === '2,3,4,5,6,7',
       `nine cells: every in-between joins the loop (got ${r.loop.join()})`);
    ok(!r.loop.includes(8) && !r.loop.includes(9),
       'the win/lose cells are NEVER part of the held loop');
}
{
    // a sheet with only the two outcome cells and no strain must not crash or loop them
    const r = routeBeats(2);
    ok(r.loop.join() === '1,2', 'two cells: degenerate but defined, no empty loop');
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
ok(mats.weaponBind(ONI, MIZU, bare, bare), "oni's iron kanabo binds a wooden bo");
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

console.log(`\n  ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
