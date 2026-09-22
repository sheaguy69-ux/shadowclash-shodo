import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const html = fs.readFileSync(path.join(root, 'web/index.html'), 'utf8');

function extractFunction(name) {
    const start = html.indexOf(`function ${name}(`);
    assert.notEqual(start, -1, `missing ${name}`);
    const bodyStart = html.indexOf('{', start);
    let depth = 0;
    for (let index = bodyStart; index < html.length; index++) {
        if (html[index] === '{') depth++;
        if (html[index] === '}' && --depth === 0) return html.slice(start, index + 1);
    }
    assert.fail(`unterminated ${name}`);
}

const states = ['RUN', 'WALL_CLING', 'JUMP', 'ATTACK_LIGHT', 'ATTACK_HEAVY', 'ATTACK_SPECIAL', 'PARRY_STANCE', 'THROWING', 'THROWN', 'BLOCKING', 'CROUCH', 'ROLL', 'STUNNED'];
const context = {
    STATE: Object.fromEntries(states.map(state => [state, state])),
    THROW_TIME: 1,
    // Same class of gap as the missing tsubasaF2Frame: the CROUCH route reads animClock and
    // the ROLL route reads ROLL_TIME, so both threw in the sandbox and were recorded as
    // twelve broken routes. Lifted from the engine (ROLL_TIME) and stubbed at a fixed value
    // (animClock) — the routes under test pick a cell from a phase, so a frozen clock is a
    // deterministic sample, not a lie.
    ROLL_TIME: Number(/const ROLL_TIME = ([\d.]+)/.exec(html)[1]),
    CROUCH_SINK_T: Number(/CROUCH_SINK_T = ([\d.]+)/.exec(html)[1]),
    animClock: 0,
    attackCellIndex: () => 0,
    attackFrame: (_player, cells) => cells,
};
vm.createContext(context);
// ANIM_TRACKS/trackFor pick per-fighter exposure tracks; lift the real table so the
// light route is evaluated exactly as it is in play.
vm.runInContext(html.slice(html.indexOf('const ANIM_TRACKS = {'),
    html.indexOf('};', html.indexOf('const ANIM_TRACKS = {')) + 2), context);
vm.runInContext('const trackFor = (p, kind) => (ANIM_TRACKS[p.spec.name] || {})[kind];', context);
// dirCells belongs in this list: spriteFrameIndex reaches it for every directional family.
// It was only ever absent because no branch this harness EXERCISED called it — heavy and
// special are checked through heavyCells/specialCells, which do not go near it. The new
// ground-light family is the first to route through spriteFrameIndex into dirCells, and a
// missing helper reports as "7 fighters' light routing is broken" when nothing is broken
// but the sandbox. Verified against the live page, where all 13 directional families draw.
// ⛔ tsubasaF2Frame BELONGS IN THIS LIST FOR THE SAME REASON dirCells DOES. spriteFrameIndex
// calls it on its SECOND line, so without it every single route through this harness threw
// ReferenceError and check() recorded the throw as a route failure — 45 of them, including
// "dropping the stance returns Shin to his Form 1 art", the one assertion that exists to catch
// a Form-2 change leaking into Form 1. The gate read as broken art for months; nothing was
// broken but the sandbox. Verified against the live page.
for (const name of ['runCells', 'attackBodyCells', 'heavyCells', 'specialCells', 'shinF2Frame', 'tsubasaF2Frame', 'mizuF2Frame', 'dirCells', 'spriteFrameIndex']) {
    vm.runInContext(extractFunction(name), context);
}

// Expectations are the ROW NAMES each route resolves to, not cell numbers — a row
// that gets re-cut moves its cells and would break a numeric table for no reason,
// which is half of why this file rotted. The Executioner's special is listed beat
// by beat because it deliberately HOLDS xtsuki2 for three exposures (the money
// frame); expressing it as a name list keeps that visible instead of hiding it
// behind a count.
const expected = {
    Executioner: {
        heavy: ['heavy_i1', 'heavy_i2', 'heavy_i3', 'heavy_i4', 'heavy_i5'],
        special: ['xtsuki1', 'xtsuki2', 'xtsuki2', 'xtsuki2', 'xtsuki3'],
    },
    Mizu: {
        heavy: ['heavy_i1', 'heavy_i2', 'heavy_i3', 'heavy_i4', 'heavy_i5'],
        special: ['special1', 'special2', 'special3', 'special4', 'special5', 'special6', 'special7'],
    },
    // SHEET_V 561: sheavy1-5 and flying_kick1-6 were DELETED from shin.json on the owner's
    // order ("delete all the old frames"), so these expectations named keys that no longer
    // exist and built [undefined x5] — unfailable-in-the-right-way, i.e. permanently red.
    // His neutral heavy is the board-look charged punch and his neutral special is the board
    // body rush.
    Shin: {
        heavy: ['hneu1', 'hneu2', 'hneu3', 'hneu4', 'hneu5', 'hneu6'],
        special: ['special1', 'special2', 'special3', 'special4', 'special5', 'special6', 'special7'],
    },
    Tsubasa: {
        heavy: ['heavy_i1', 'heavy_i2', 'heavy_i3', 'heavy_i4', 'heavy_i5'],
        special: ['special1', 'special2', 'special3', 'special4', 'special5', 'special6', 'special7'],
    },
    Ember: {
        heavy: ['eheavy1', 'eheavy2', 'eheavy3', 'eheavy4'],
        special: ['espec1', 'espec2', 'espec3', 'espec4', 'espec5'],
    },
    Kael: {
        heavy: ['heavy_i1', 'heavy_i2', 'heavy_i3', 'heavy_i4', 'heavy_i5'],
        special: ['special1', 'special2', 'special3', 'special4', 'special5', 'special6', 'special7'],
    },
};
const byName = (frames, names) => names.map(n => frames[n]);

// Mirrors the engine's own light rule (SHEET_V 649): the generic chain is 1..N —
// collect whatever the sheet carries, same as heavy/special/kick/run. Ember keeps his
// planted claw barrage (elight1..5).
const expectedLight = (name, frames) => {
    if (name === 'Ember' && frames.elight1 !== undefined) return cells(frames, 'elight', 5);
    const out = [];
    for (let i = 1; frames['light' + i] !== undefined; i++) out.push(frames['light' + i]);
    return out;
};
const cells = (frames, prefix, count) => Array.from({ length: count }, (_, index) => frames[`${prefix}${index + 1}`]);

// THE RUN CYCLE IS 8-PHASE WHERE THE SHEET HAS IT. runCells prefers the full
// Williams cycle (contact/down/pass/up on both legs) and only falls back to 4,
// then to run1/run2. This check asserted a flat 4 and so had NEVER passed on
// this tree — every fighter carries run_clean1..8, so it failed on the first
// roster entry and aborted before reaching any other assertion. Mirror the
// engine's own rule instead of hardcoding a length it stopped using.
const expectedRun = frames =>
    frames.brun1 !== undefined
        ? cells(frames, 'brun', 8).filter(c => c != null)
    : frames.run_clean5 !== undefined ? cells(frames, 'run_clean', 8)
    : frames.run_clean1 !== undefined ? cells(frames, 'run_clean', 4)
    : cells(frames, 'run', 2);

// COLLECT, DO NOT ABORT. assert throws on the first mismatch, so a single stale
// expectation hid every assertion behind it — this file failed on Executioner's
// run and never reached the other five fighters at all. Gather them and report
// the lot, then fail once at the end.
const failures = [];
const check = (label, fn) => { try { fn(); } catch (e) { failures.push(`${label}: ${e.message.split('\n')[0]}`); } };

for (const [name, routes] of Object.entries(expected)) {
    const manifest = JSON.parse(fs.readFileSync(path.join(root, `web/assets/sprites/${name.toLowerCase()}.json`), 'utf8'));
    const frames = manifest.frames;
    // rollTimer belongs in the stub for the same reason ROLL_TIME belongs in the context: the
    // ROLL route indexes the drawn row BY it, so leaving it undefined made every fighter's
    // roll resolve to `undefined` and report as broken art. Mid-roll is the honest sample.
    const player = { spec: { name }, kickKind: null, isGrounded: true, isDownPressed: () => false,
                     rollTimer: context.ROLL_TIME / 2 };
    check(`${name} run`, () => assert.deepEqual(Array.from(context.runCells(frames)), expectedRun(frames)));
    check(`${name} heavy`, () => assert.deepEqual(Array.from(context.heavyCells(player, frames)), byName(frames, routes.heavy)));
    check(`${name} special`, () => assert.deepEqual(Array.from(context.specialCells(player, frames)), byName(frames, routes.special)));
    // THE LIGHT CHAIN GREW TO FIVE where the sheet has light5, and Ember got his own
    // drawn row (elight1..5). This asserted a flat light1..3 for everyone.
    check(`${name} light`, () => assert.deepEqual(
        Array.from(context.spriteFrameIndex({ ...player, state: 'ATTACK_LIGHT' }, frames)),
        expectedLight(name, frames)));
    // THE PUSH KICK IS A THREE-CELL SEQUENCE where the sheet has kpush3 — it stopped
    // being the single `kpush` cell this check asserted. Sweep and heel are still
    // single cells, with a documented leg-pose fallback when the sheet has neither.
    for (const kick of ['push', 'sweep', 'heel']) {
        check(`${name} ${kick} kick`, () => {
            const got = context.spriteFrameIndex({ ...player, state: 'ATTACK_LIGHT', kickKind: kick }, frames);
            if (kick === 'push' && frames.kpush3 !== undefined)
                assert.deepEqual(Array.from(got), cells(frames, 'kpush', 3));
            else if (frames[`k${kick}`] !== undefined)
                assert.equal(got, frames[`k${kick}`]);
            else
                assert.equal(got, frames.kstomp ?? frames.jump2 ?? frames.fall ?? frames.light1);
        });
    }
    check(`${name} air-down`, () => {
        // ⛔ attackAir/attackDir, NOT isDownPressed. The engine gates the dive-stomp on the
        // PRESS-TIME captures (`p.attackAir && p.attackDir === 'down'`), so a route that only
        // held Down never reached it and every fighter's air-down reported as broken art.
        const airDown = context.spriteFrameIndex({ ...player, state: 'ATTACK_LIGHT', isGrounded: false,
                                                   attackAir: true, attackDir: 'down',
                                                   isDownPressed: () => true }, frames);
        // same latent staleness as the light route above: the fallback is the light
        // chain, whatever length that fighter's sheet gives it
        // ⛔ THIS IS THE AIR-DOWN *LIGHT*, NOT THE METEOR. The dive-stomp cell answers here;
        // `hdown` is the air-down HEAVY and lives in the other state, so do not reach for it.
        // Order: kstomp where the sheet has one, else the fighter's own neutral-air row, else
        // the light chain. Shin lost kstomp at SHEET_V 567 (measured unreachable — dirCells
        // answers his air-down heavy with hdown, and nothing else read it) and now correctly
        // falls to his board-look air1..3.
        const airRow = [];
        for (let i = 1; frames['air' + i] !== undefined; i++) airRow.push(frames['air' + i]);
        if (frames.kstomp !== undefined) assert.equal(airDown, frames.kstomp);
        else if (airRow.length) assert.deepEqual(Array.from(airDown), airRow);
        else assert.deepEqual(Array.from(airDown), expectedLight(name, frames));
    });
    // ⛔ THESE TWO WERE PINNED TO THE PRE-487 FALLBACKS. SHEET_V 487 gave the WHOLE roster a
    // drawn crouch (crouch_1..4) and a drawn ground roll (roll_1..6) — owner ruling, and the
    // engine picks a beat out of those rows by crouchAt/rollTimer. Asserting `frames.kneel`
    // and `frames.roll` therefore failed on correct art for every fighter, and had done since
    // 487; nobody saw it because the missing tsubasaF2Frame binding was turning all 47 routes
    // into errors anyway. Assert MEMBERSHIP of the drawn row, not one beat: which beat comes
    // back depends on timers this sandbox stubs, and pinning a beat is how it rots again.
    const drawnRow = prefix => {
        const out = [];
        for (let i = 1; frames[prefix + i] !== undefined; i++) out.push(frames[prefix + i]);
        return out;
    };
    check(`${name} crouch`, () => {
        const got = context.spriteFrameIndex({ ...player, state: 'CROUCH' }, frames);
        const row = drawnRow('crouch_');
        if (row.length) assert.ok(row.includes(got), `crouch drew ${got}, not one of the drawn crouch_ beats [${row}]`);
        else assert.equal(got, frames.kneel);
    });
    check(`${name} roll`, () => {
        const got = context.spriteFrameIndex({ ...player, state: 'ROLL' }, frames);
        const row = drawnRow('roll_');
        if (row.length) assert.ok(row.includes(got), `roll drew ${got}, not one of the drawn roll_ beats [${row}]`);
        else assert.equal(got, frames.roll);
    });

    // STRUCTURAL, and the part that cannot rot: whatever a route resolves to, every
    // cell in it must be a real index on that fighter's sheet. This is what catches
    // a renamed or deleted row — the failure mode the numeric table was reaching for
    // and kept missing, because a re-cut row breaks the numbers without breaking the
    // game while a missing row yields undefined and draws cell 0.
    for (const [route, arr] of [['run', context.runCells(frames)],
                                ['heavy', context.heavyCells(player, frames)],
                                ['special', context.specialCells(player, frames)]]) {
        check(`${name} ${route} cells exist`, () => {
            const list = Array.from(arr);
            assert.ok(list.length > 0, 'empty route');
            for (const c of list) {
                assert.equal(typeof c, 'number', `undefined cell in ${route} — a row was renamed or removed`);
                assert.ok(c >= 0 && c < manifest.cols, `cell ${c} outside the sheet (cols ${manifest.cols})`);
            }
        });
    }
    if (name === 'Tsubasa') {
        check('Tsubasa parry sequence', () => assert.deepEqual(
            Array.from(context.spriteFrameIndex({ ...player, state: 'PARRY_STANCE' }, frames)), cells(frames, 'special', 2)));
    }
}
// ⛔ SHIN'S FORM 2 IS ART-GATED NOW. SHEET_V 575 executed the owner's Aug 22 order — "no
// pre-Aug-20 frame may draw anywhere" — and his nine f2_ rows were drawn Aug 8, so they were
// deleted. The stance falls back to his first-mode board art, which is correct and is what the
// engine is built to do. These assertions describe the kit WHEN IT EXISTS; with the rows gone
// they would fail on correct behaviour, so they skip. They come straight back with the art.
// SHIN'S FORM 2 (Kage-Nui stance). Its own router, so it needs its
// own coverage: the stance must take over every normal, each string step must draw
// its OWN row, and dropping the stance must hand the frame straight back to Form 1.
{
    const frames = JSON.parse(fs.readFileSync(path.join(root, 'web/assets/sprites/shin.json'), 'utf8')).frames;
    const base = { spec: { name: 'Shin', id: 2 }, kickKind: null, isGrounded: true,
                   isDownPressed: () => false, f2Air: false, f2Low: false,
                   f2LightStep: 0, f2HeavyStep: 0 };
    const rowOf = n => cells(frames, `${n}_`, 6);
    const hasForm2 = frames.f2_light1_1 !== undefined;
    const draw = extra => context.spriteFrameIndex({ ...base, ...extra }, frames);

    check('Shin Form 2 light string draws its three rows', () => {
        if (!hasForm2) return;   // rows deleted by the Aug 22 purge; the stance falls back to Form 1
        for (const [step, row] of [[0, 'f2_light1'], [1, 'f2_light2'], [2, 'f2_light3']])
            assert.deepEqual(Array.from(draw({ kageNui: true, state: 'ATTACK_LIGHT', f2LightStep: step })), rowOf(row));
    });
    check('Shin Form 2 heavy string draws its three rows', () => {
        if (!hasForm2) return;   // rows deleted by the Aug 22 purge; the stance falls back to Form 1
        for (const [step, row] of [[0, 'f2_heavy1'], [1, 'f2_heavy2'], [2, 'f2_heavy3']])
            assert.deepEqual(Array.from(draw({ kageNui: true, state: 'ATTACK_HEAVY', f2HeavyStep: step })), rowOf(row));
    });
    check('Shin Form 2 crouch + air draw their own rows', () => {
        if (!hasForm2) return;   // rows deleted by the Aug 22 purge; the stance falls back to Form 1
        assert.deepEqual(Array.from(draw({ kageNui: true, state: 'ATTACK_LIGHT', f2Low: true })), rowOf('f2_clow'));
        assert.deepEqual(Array.from(draw({ kageNui: true, state: 'ATTACK_HEAVY', f2Low: true })), rowOf('f2_csweep'));
        assert.deepEqual(Array.from(draw({ kageNui: true, state: 'ATTACK_HEAVY', f2Air: true })), rowOf('f2_air'));
    });
    check('dropping the stance returns Shin to his Form 1 art', () => {
        assert.deepEqual(Array.from(draw({ kageNui: false, state: 'ATTACK_LIGHT' })), expectedLight('Shin', frames));
    });
    // ⛔ NO NUMERIC FLOOR. This pinned `c >= 204`, the PRE-REINDEX numbering; the nine rows
    // have since shifted to 197-250 and the check failed on correct data. A cell range was
    // never the contract anyway — the next re-index breaks it again, and 251-257 are the
    // drawn roll and crouch, so trusting the old range invites a repack straight over them.
    // The real contract is: every row is complete, and every cell is on the sheet.
    check('every Form 2 cell exists on the sheet', () => {
        if (!hasForm2) return;   // rows deleted by the Aug 22 purge; the stance falls back to Form 1
        const cols = JSON.parse(fs.readFileSync(path.join(root, 'web/assets/sprites/shin.json'), 'utf8')).cols;
        for (const row of ['f2_light1','f2_light2','f2_light3','f2_heavy1','f2_heavy2',
                           'f2_heavy3','f2_clow','f2_csweep','f2_air'])
            for (const c of rowOf(row)) {
                assert.equal(typeof c, 'number', `${row} has a missing cell`);
                assert.ok(c >= 0 && c < cols, `${row} cell ${c} is off the sheet (cols ${cols})`);
            }
    });
}

if (failures.length) {
    console.error(`live routing check FAILED — ${failures.length} routes:`);
    for (const f of failures) console.error('  ' + f);
    process.exit(1);
}

assert.doesNotMatch(html, /ORIGINAL_ART_ANIMATION/);
assert.match(html, /name:\s*"Kael"[\s\S]*?renderScale:\s*1\.0,/);
console.log('live routing check passed');
