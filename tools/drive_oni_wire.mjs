#!/usr/bin/env node
// Drive ONI'S FOUR WIRE FINISHERS in the real engine and prove each one reaches the screen.
//
// His four grab boards each end in a different weapon, and which one plays is decided by
// two things the engine already knows — whether HE is airborne, and whether his VICTIM is.
// That decision cannot be read off the source with any confidence: the same feature has
// now been broken twice by where a branch was FILED (a conversion sets ATTACK_SPECIAL, so
// a draw branch inside the JUMP case never ran and quietly drew cells 81-92 instead of the
// katana) and once by what it READ (speedScale, declared ~140 lines below, threw on the
// temporal dead zone every single time). Both were invisible to reading and obvious the
// moment the button was actually pressed.
//
// So this presses it. For each of the four cases it opens a real bind on a real victim,
// calls the real executeAttack, and then walks the draw function across the whole
// animation and records every cell index spriteFrameIndex() returns. A finisher that is
// packed but unreachable shows up here as zero hits on its family, which is exactly how
// the 18 cells before it sat unreachable for weeks.
import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

// ⛔ NEVER SPAWN A SERVER. There is ONE ShadowClash URL, :9100 (tools/serve.py). A driver
// that starts its own is how a stale one silently graded the PREVIOUS sheet twice.
const port = 9101, dbg = 9336;
const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const profile = await mkdtemp(path.join(tmpdir(), 'oni-wire-'));

const who = await fetch(`http://127.0.0.1:${port}/whoami`).then(r => r.json()).catch(() => null);
if (!who) { console.error(`no server on :${port} — start it with: python3 tools/serve.py 9101 web`); process.exit(1); }
// ⛔ AND IT MUST BE SERVING *THIS* TREE. :9100 served the main tree at SHEET_V 436 while
// the live work sat at 446, so a grade here described a sheet nobody was editing.
const here = process.cwd();
if (path.resolve(who.tree) !== path.resolve(here)) {
  console.error(`:9101 is serving ${who.tree}\nyou are in    ${here}\nrebind it (never add a second port):\n  kill ${who.pid} && python3 tools/serve.py 9101 web`);
  process.exit(1);
}
spawnSync('pkill', ['-f', `remote-debugging-port=${dbg}`], { stdio: 'ignore' });

const chrome = spawn(chromePath, ['--headless=new', '--disable-gpu', '--no-first-run',
  '--no-default-browser-check', `--remote-debugging-port=${dbg}`,
  `--user-data-dir=${profile}`, `http://127.0.0.1:${port}/`], { stdio: 'ignore' });

const sleep = ms => new Promise(r => setTimeout(r, ms));
let page;
for (let i = 0; i < 100 && !page; i++) {
  try {
    const list = await fetch(`http://127.0.0.1:${dbg}/json/list`).then(r => r.json());
    page = list.find(t => t.type === 'page' && t.url.includes(String(port)));
  } catch {}
  if (!page) await sleep(100);
}
if (!page) { console.error('chrome never came up'); process.exit(1); }

const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.addEventListener('open', res, { once: true }); ws.addEventListener('error', rej, { once: true }); });
let id = 1; const pend = new Map();
ws.addEventListener('message', e => {
  const m = JSON.parse(e.data);
  if (m.id && pend.has(m.id)) { const p = pend.get(m.id); pend.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); }
});
const evaluate = expr => new Promise((res, rej) => {
  const n = id++;
  pend.set(n, { res, rej });
  ws.send(JSON.stringify({ id: n, method: 'Runtime.evaluate', params: { expression: expr, awaitPromise: true, returnByValue: true } }));
}).then(r => { if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text); return r.result.value; });

const script = String.raw`(async () => {
  const wait = async (t, msg) => { for (let i = 0; i < 200; i++) { if (t()) return; await new Promise(r => setTimeout(r, 50)); } throw new Error(msg); };
  await wait(() => typeof SPRITES !== 'undefined' && SPRITES.oni && SPRITES.oni.ready, 'oni sheet never loaded');
  const F = SPRITES.oni.frames;
  const byIndex = {};
  for (const [k, i] of Object.entries(F)) (byIndex[i] ||= []).push(k);
  const famOf = i => {
    const ks = byIndex[i] || [];
    for (const k of ks) { const m = k.match(/^([a-z_]+?)\d+$/); if (m) return m[1]; }
    return ks[0] || ('cell' + i);
  };

  const spec = NINJA_ROSTER.find(s => s.name.toLowerCase() === 'oni');
  if (!spec) throw new Error('oni not on the roster');

  // Each case: is HE airborne, is the VICTIM airborne, which way is he holding, and which
  // of his four boards that ought to select. The expectation is written here as the FAMILY
  // NAME, so a wiring change that silently re-points a finisher at borrowed art fails.
  const CASES = [
    { name: 'ground fwd  -> KATANA',     air: false, foeAir: false, ax: +1, want: ['kdraw', 'kslash'] },
    { name: 'ground neu  -> KATANA',     air: false, foeAir: false, ax:  0, want: ['kdraw', 'kslash'] },
    { name: 'ground back -> CLAW RAKE',  air: false, foeAir: false, ax: -1, want: ['wclaw'] },
    { name: 'air, foe up -> KNIVES',     air: true,  foeAir: true,  ax:  0, want: ['knives'] },
    { name: 'air, foe dn -> SHORT WIRE', air: true,  foeAir: false, ax:  0, want: ['wslice'] },
  ];

  const errors = [], rows = [];

  // A control with NO bind must be completely untouched by any of this — if the conversion
  // ever fires without a bind it has eaten his normal neutral Special.
  const runOne = (c, withBind) => {
    const p = new Player(1, 150, GROUND_Y - 48, spec, true);
    const foe = new Player(2, 260, GROUND_Y - 48, spec, false);
    p.opponent = foe; foe.opponent = p;
    p.facing = 1;
    p.isGrounded = !c.air; p.vy = c.air ? 120 : 0;
    foe.isGrounded = !c.foeAir; foe.vy = c.foeAir ? -80 : 0;
    p.getInputAxis = () => c.ax * p.facing;
    p.isDownPressed = () => false;
    p.isUpPressed = () => false;
    p.state = STATE.IDLE; p.attackT = 0; p.lock = 0;
    p.stunTimer = 0; p.rollTimer = 0; p.rollRecover = 0; p.sayaLock = 0;
    if (withBind) { p.wireBind = 0.55; p.wireBindFoe = foe; }

    // kageActs is the tape spawnHitbox writes at its very TOP, before every multiplier and
    // before any early return, so it counts real swings for this fighter alone. An earlier
    // version counted a global named hitboxes; there is no such global, so it read 0 for
    // every case and failed all five while the conversions themselves were fine.
    const hbBefore = p.kageActs.length;
    try { p.executeAttack(STATE.ATTACK_SPECIAL); }
    catch (e) { errors.push(c.name + ': ' + e.message); return null; }
    const hbAfter = p.kageActs.length;

    // Walk the WHOLE animation. animClock does not advance inside Runtime.evaluate, so the
    // elapsed fraction is driven by moving attackAnim.start rather than by waiting — the
    // draw function reads el, and el is all it reads.
    const fams = [], idx = [];
    if (p.wireConv && p.attackAnim) {
      const dur = p.attackAnim.dur;
      for (let s = 0; s < 24; s++) {
        p.attackAnim.start = animClock * 1000 - (s / 24) * dur * 0.99;
        let i;
        try { i = spriteFrameIndex(p, F); } catch (e) { errors.push(c.name + ' draw: ' + e.message); break; }
        idx.push(i);
        const f = famOf(i);
        if (fams[fams.length - 1] !== f) fams.push(f);
      }
    }
    return { conv: p.wireConv, fams, first: idx[0], last: idx[idx.length - 1],
             spawned: hbAfter - hbBefore, bindLeft: p.wireBind, state: p.state };
  };

  for (const c of CASES) {
    const r = runOne(c, true);
    if (!r) { rows.push({ case: c.name, PASS: false, why: 'threw' }); continue; }
    const got = r.fams.filter(f => f !== 'idle');
    const covered = c.want.every(w => got.includes(w));
    const foreign = got.filter(f => !c.want.includes(f));
    rows.push({
      case: c.name, conv: r.conv, drew: got.join(' -> '),
      hitbox: r.spawned, bindConsumed: r.bindLeft === 0,
      PASS: covered && foreign.length === 0 && r.spawned === 1 && r.bindLeft === 0,
      why: !covered ? ('missing ' + c.want.filter(w => !got.includes(w)).join(','))
         : foreign.length ? ('borrowed ' + foreign.join(','))
         : r.spawned !== 1 ? ('hitboxes spawned: ' + r.spawned)
         : r.bindLeft !== 0 ? 'bind not consumed' : '',
    });
  }

  // the control
  const ctl = runOne(CASES[0], false);
  const control = { conv: ctl && ctl.conv, PASS: !!ctl && !ctl.conv };

  // ---- THE THREE BOARDS THAT HAD NO ENGINE HOME AT ALL -------------------------
  // Each needs a condition the plain sweep never builds: a dash in flight, a foe inside
  // whip range, or the one grounded Special direction the dirCells map never carried.
  // The near/far pair on the whip is the real check — if distance is not actually being
  // read, BOTH ends return the same move and the "trade" is fiction.
  const NEW = [
    { name: 'dash + Light  -> LUNGE CLAW',  want: 'lunge',   st: 'ATTACK_LIGHT',
      set: p => { p.dashTimer = 0.1; p.dashDir = p.facing; p.vx = 400; } },
    { name: 'Up + Special  -> RISING CLAW', want: 'gsup',    st: 'ATTACK_SPECIAL',
      set: p => { p.isUpPressed = () => true; p.attackDir = 'up'; } },
    { name: 'Special CLOSE -> WIRE WHIP',   want: 'whip',    st: 'ATTACK_SPECIAL',
      set: p => { p.opponent.x = p.x + 80; } },
    { name: 'Special FAR   -> wire shot',   want: 'special', st: 'ATTACK_SPECIAL',
      set: p => { p.opponent.x = p.x + 400; } },
  ];
  const newRows = [];
  for (const c of NEW) {
    const p = new Player(1, 150, GROUND_Y - 48, spec, true);
    p.opponent = new Player(2, 420, GROUND_Y - 48, spec, false);
    p.opponent.opponent = p;
    p.facing = 1; p.isGrounded = true; p.attackAir = false;
    p.getInputAxis = () => 0;
    p.isDownPressed = () => false; p.isUpPressed = () => false;
    p.state = STATE.IDLE; p.attackT = 0; p.lock = 0;
    p.stunTimer = 0; p.rollTimer = 0; p.rollRecover = 0; p.sayaLock = 0;
    c.set(p);
    const before = p.kageActs.length;
    try { p.executeAttack(STATE[c.st]); }
    catch (e) { errors.push(c.name + ': ' + e.message); newRows.push({ case: c.name, PASS: false, why: 'threw' }); continue; }
    const spawned = p.kageActs.length - before;
    const fams = [];
    const dur = p.attackAnim ? p.attackAnim.dur : 0;
    for (let s = 0; s < 24; s++) {
      if (p.attackAnim) p.attackAnim.start = animClock * 1000 - (s / 24) * dur * 0.99;
      else p.attackT = (s / 24) * 0.5;
      let i;
      try { i = spriteFrameIndex(p, F); } catch (e) { errors.push(c.name + ' draw: ' + e.message); break; }
      const f = famOf(i);
      if (fams[fams.length - 1] !== f) fams.push(f);
    }
    const got = fams.filter(f => f !== 'idle');
    newRows.push({ case: c.name, drew: got.join(' -> '), hitbox: spawned,
                   PASS: got.includes(c.want) && spawned >= 1,
                   why: !got.includes(c.want) ? ('wanted ' + c.want + ', got ' + (got.join(',') || 'nothing'))
                      : spawned < 1 ? 'no hitbox spawned' : '' });
  }

  // ---- THE LOOP THAT WAS NEVER CLOSED ------------------------------------------
  // Every check above opens the bind BY HAND, which is exactly how this feature came to
  // be reported as working while being unreachable: his Specials spawned no hitbox at all,
  // so nothing could ever connect, so wireBind was never set outside a harness. This runs
  // the real thing — press Special at a real foe, let processHitboxes resolve the real box,
  // and read wireBind back. If it is 0 here, the finishers are dead art no matter how many
  // of the checks above pass.
  const loop = {};
  for (const [name, gap] of [['shot (far)', 200], ['whip (close)', 80]]) {
    const p = new Player(1, 150, GROUND_Y - 48, spec, true);
    const foe = new Player(2, 150 + gap, GROUND_Y - 48, spec, false);
    p.opponent = foe; foe.opponent = p;
    p.facing = 1; foe.facing = -1;
    p.isGrounded = foe.isGrounded = true;
    p.attackAir = false; p.chakra = 100; p.stamina = 100;
    p.getInputAxis = () => 0; p.isDownPressed = () => false; p.isUpPressed = () => false;
    p.state = STATE.IDLE; p.attackT = 0; p.lock = 0;
    p.stunTimer = 0; p.rollTimer = 0; p.rollRecover = 0; p.sayaLock = 0;
    try { p.executeAttack(STATE.ATTACK_SPECIAL); } catch (e) { errors.push(name + ': ' + e.message); }
    let bound = 0, hpDrop = 0;
    const hp0 = foe.hp;   // NOT .health — there is no such field, and it read null
    for (let t = 0; t < 60; t++) {
      try { processHitboxes(p, foe, 1 / 60); } catch (e) { errors.push(name + ' hits: ' + e.message); break; }
      try { p.update(1 / 60); } catch {}
      bound = Math.max(bound, p.wireBind || 0);
      hpDrop = Math.max(hpDrop, hp0 - foe.hp);
    }
    loop[name] = { bindOpened: +bound.toFixed(2), damage: +hpDrop.toFixed(1),
                   PASS: bound > 0 && hpDrop > 0 };
  }

  // ---- THE RISING CLAW MUST ACTUALLY REVERSE --------------------------------
  // It had the leap, the launch and the anti-air box and NO invulnerability, so it traded
  // with the meaty it exists to beat — a reversal-shaped move that could not reverse. The
  // check is the DP contract itself, driven both ways: struck during startup he must take
  // nothing, and once the window lapses he must take it in full. Testing only the first
  // half would pass on a move that is invulnerable forever.
  const dp = {};
  {
    const p = new Player(1, 150, GROUND_Y - 48, spec, true);
    const foe = new Player(2, 210, GROUND_Y - 48, spec, false);
    p.opponent = foe; foe.opponent = p;
    p.facing = 1; p.isGrounded = true; p.attackAir = false; p.chakra = 100; p.stamina = 100;
    p.getInputAxis = () => 0; p.isDownPressed = () => false; p.isUpPressed = () => true;
    p.state = STATE.IDLE; p.attackT = 0; p.lock = 0;
    p.stunTimer = 0; p.rollTimer = 0; p.rollRecover = 0; p.sayaLock = 0;
    try { p.executeAttack(STATE.ATTACK_SPECIAL); } catch (e) { errors.push('dp: ' + e.message); }
    const window = +(p.invulnTimer || 0).toFixed(3);
    const hp0 = p.hp;
    try { p.takeDamage(20, foe); } catch (e) { errors.push('dp hit: ' + e.message); }
    const duringDrop = +(hp0 - p.hp).toFixed(1);
    // let the window lapse, then hit him again — he must be mortal on the other side
    p.invulnTimer = 0;
    p.stunTimer = 0; p.grabbedBy = null; p.vanishTimer = 0;
    const hp1 = p.hp;
    try { p.takeDamage(20, foe); } catch (e) {}
    const afterDrop = +(hp1 - p.hp).toFixed(1);
    dp.window = window;
    dp.duringDrop = duringDrop;
    dp.afterDrop = afterDrop;
    dp.PASS = window > 0 && duringDrop === 0 && afterDrop > 0;
  }

  return { rows, newRows, loop, dp, control, errors: errors.slice(0, 10), errorCount: errors.length,
           cols: SPRITES.oni.cols, hasWclaw: F.wclaw1 !== undefined, hasWslice: F.wslice1 !== undefined };
})()`;

let out;
try { out = await evaluate(script); }
catch (e) { console.error('DRIVE FAILED:', e.message); process.exit(1); }
finally {
  try { ws.close(); } catch {}
  chrome.kill('SIGKILL');
}

console.log(`sheet: ${out.cols} cells   wclaw ${out.hasWclaw ? 'packed' : 'MISSING'}   wslice ${out.hasWslice ? 'packed' : 'MISSING'}\n`);
let bad = 0;
for (const r of out.rows) {
  if (!r.PASS) bad++;
  console.log(`  ${r.PASS ? 'PASS' : 'FAIL'}  ${r.case.padEnd(26)} conv=${String(r.conv).padEnd(7)} drew ${r.drew}` +
              (r.why ? `\n           ⛔ ${r.why}` : ''));
}
console.log(`\n  ${out.control.PASS ? 'PASS' : 'FAIL'}  no bind -> no conversion (control)   conv=${out.control.conv}`);
if (!out.control.PASS) bad++;
console.log('');
for (const r of out.newRows) {
  if (!r.PASS) bad++;
  console.log(`  ${r.PASS ? 'PASS' : 'FAIL'}  ${r.case.padEnd(26)} drew ${r.drew}` + (r.why ? `\n           ⛔ ${r.why}` : ''));
}
console.log('\n  END TO END — the real box, resolved by processHitboxes, opening the real bind:');
for (const [k, v] of Object.entries(out.loop || {})) {
  if (!v.PASS) bad++;
  console.log(`  ${v.PASS ? 'PASS' : 'FAIL'}  Special ${k.padEnd(13)} bind opened ${v.bindOpened}s, ${v.damage} damage` +
              (v.PASS ? '' : '\n           ⛔ nothing connected — the finishers cannot be reached in play'));
}
const d = out.dp || {};
if (!d.PASS) bad++;
console.log(`\n  ${d.PASS ? 'PASS' : 'FAIL'}  RISING CLAW reverses — ${d.window}s invulnerable, ` +
            `${d.duringDrop} damage taken during it, ${d.afterDrop} after it lapses`);
if (out.errorCount) { console.log(`\n  ${out.errorCount} error(s):`); out.errors.forEach(e => console.log('    ' + e)); bad += out.errorCount; }
console.log(bad ? `\nWIRE DRIVE FAILED — ${bad} problem(s)` : '\nWIRE DRIVE PASSED — all four finishers reach the screen');
process.exit(bad ? 1 : 0);
