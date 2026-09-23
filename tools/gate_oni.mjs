#!/usr/bin/env node
// Catch the defect BEFORE the owner sees it.
//
//   node tools/gate_oni.mjs            # gate Oni
//   node tools/gate_oni.mjs --name kael
//
// Owner, Aug 11 2026: "why you gotta do a test to see if it worked or not instead
// of telling me oh try it out — I need you to catch the defects before it even
// comes to me."
//
// Fair. Every defect that reached him in the Oni pass was machine-findable, and
// each one is a check here:
//
//   DARK      a family is packed and NOTHING ever draws it. The cartwheel was
//             packed, wired and repaired across three SHEET_V bumps and still never
//             drew, because its branch sat below one gated on `F.ajump1` and Oni has
//             an ajump row. The code was right; its POSITION was wrong. Reading a
//             branch cannot prove it executes — only driving it can, which is why
//             this walks the real spriteFrameIndex instead of grepping.
//   AIR-ONLY  a family that draws ONLY airborne, or only grounded. h*/s* are the AIR
//             directional families; ground rows packed into them drew 36 frames each
//             in the air and zero on the floor, i.e. a standing staff thrust playing
//             mid-jump. The split is reported so a human can see the mismatch.
//   BANNER    caption text packed in as art. A figure's topmost row is narrow (a horn
//             tip); a banner is nearly as wide as the whole cell. dash1..3 carried
//             "5. FORWARD DASH MID", "6. BACKSTEP PREP" and "8. RECOVERY" plus panel
//             rules off MASTER-STATES-CLEAN.png; re-cut clean at SHEET_V 465, and
//             this check is what keeps them that way. Note BANNER is worth failing on
//             even when DARK also fires: those three were never drawn by anything, so
//             nobody ever saw the text — a cell can be wrong without being visible,
//             and it is cheaper to fix while it is still off screen.
//   CLIPPED   art touching the frame box edge — the pose was cropped rather than the
//             box grown, which is backwards per the house rule.
//
// ⛔ USES THE ONE SERVER and refuses to guess which tree it is. :9100 is the only
// ShadowClash URL and several worktrees can bind it; this asks /whoami and aborts if
// it is serving a different tree, because grading someone else's sheet and reporting
// PASS is worse than not running.
import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const NAME = (process.argv.includes('--name')
  ? process.argv[process.argv.indexOf('--name') + 1] : 'oni').toLowerCase();
const port = 9101, dbg = 9335;
const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const sleep = ms => new Promise(r => setTimeout(r, ms));

const here = spawnSync('git', ['rev-parse', '--show-toplevel'], { encoding: 'utf8' }).stdout.trim();
let who;
try { who = await fetch(`http://127.0.0.1:${port}/whoami`).then(r => r.json()); }
catch { console.error(`no server on :${port} — start it: python3 tools/serve.py 9101 web`); process.exit(2); }
if (!who || !who.tree) { console.error('server has no /whoami — it is an old serve.py; restart it from this tree'); process.exit(2); }
if (path.resolve(who.tree) !== path.resolve(here)) {
  console.error(`⛔ :${port} is serving ${who.tree}\n   you are in    ${here}\n   Refusing to grade another tree's sheet. Rebind it first.`);
  process.exit(2);
}
console.log(`  gating ${NAME} @ ${who.branch} SHEET_V ${who.sheet_v}`);

spawnSync('pkill', ['-f', `remote-debugging-port=${dbg}`], { stdio: 'ignore' });
const profile = await mkdtemp(path.join(tmpdir(), 'gate-'));
const chrome = spawn(chromePath, ['--headless=new', '--disable-gpu', '--no-first-run',
  '--no-default-browser-check', `--remote-debugging-port=${dbg}`,
  `--user-data-dir=${profile}`, `http://127.0.0.1:${port}/`], { stdio: 'ignore' });

let page;
for (let i = 0; i < 120 && !page; i++) {
  try {
    const list = await fetch(`http://127.0.0.1:${dbg}/json/list`).then(r => r.json());
    page = list.find(t => t.type === 'page' && t.url.includes(String(port)));
  } catch {}
  if (!page) await sleep(100);
}
if (!page) { console.error('chrome never came up'); process.exit(2); }

const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.addEventListener('open', res, { once: true }); ws.addEventListener('error', rej, { once: true }); });
let id = 1; const pend = new Map();
ws.addEventListener('message', e => {
  const m = JSON.parse(e.data);
  if (m.id && pend.has(m.id)) { const p = pend.get(m.id); pend.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); }
});
const evaluate = expr => new Promise((res, rej) => {
  const n = id++; pend.set(n, { res, rej });
  ws.send(JSON.stringify({ id: n, method: 'Runtime.evaluate', params: { expression: expr, awaitPromise: true, returnByValue: true } }));
});

for (let i = 0; i < 100; i++) {
  const r = await evaluate(`(() => { const m = SPRITES['${NAME}']; return !!(m && m.ready); })()`);
  if (r.result?.value) break;
  await sleep(150);
}

const script = `(() => {
  const NAME = ${JSON.stringify(NAME)};
  const man = SPRITES[NAME], F = man.frames;
  const spec = NINJA_ROSTER.find(s => s.name.toLowerCase() === NAME);
  const fam = k => k.replace(/[0-9]+$/, '');
  const cellFam = {};
  for (const k in F) (cellFam[F[k]] ||= new Set()).add(fam(k));

  const groundHits = new Set(), airHits = new Set();
  const errors = [];
  const mk = () => {
    const p = new Player(1, 260, GROUND_Y - 48, spec, true);
    p.opponent = new Player(2, 520, GROUND_Y - 48, spec, false);
    p.facing = 1; p.chakra = 100; p.stamina = 100;
    return p;
  };
  // ⛔ CLEAR attackAnim BEFORE SWEEPING. attackFrame reads elapsed as
  // (animClock*1000 - attackAnim.start)/dur, and animClock does not advance inside a
  // Runtime.evaluate — so with an attackAnim live, every sample returns the SAME cell
  // and the sweep reports a fifth of the sheet unreachable. Nulling it drops into the
  // attackT path, which is the one that actually walks a six-beat row.
  const sample = (p, into) => {
    p.attackAnim = null;
    for (let t = 0; t < 30; t++) {
      p.attackT = (p.attackT || 0) + 1 / 60;
      try { into.add(spriteFrameIndex(p, F)); } catch (e) { errors.push(e.message.slice(0, 60)); return; }
    }
  };
  const DIRS = ['fwd', 'back', 'up', 'down', null];

  // ATTACKS — driven through the real executeAttack so its own guards and the
  // press-time direction capture run, not a hand-replay of what we think it does.
  for (const air of [false, true]) {
    for (const d of DIRS) {
      for (const st of [STATE.ATTACK_LIGHT, STATE.ATTACK_HEAVY, STATE.ATTACK_SPECIAL]) {
        const p = mk();
        p.isGrounded = !air; p.attackAir = air;
        p.getInputAxis = () => d === 'fwd' ? p.facing : d === 'back' ? -p.facing : 0;
        p.isDownPressed = () => d === 'down';
        p.isUpPressed = () => d === 'up';
        try { p.executeAttack(st); } catch (e) { errors.push('atk ' + e.message.slice(0, 50)); continue; }
        p.isGrounded = !air; p.attackAir = air;
        sample(p, air ? airHits : groundHits);
        // AND the same state driven directly, without executeAttack having chosen a
        // move first: a fighter's plain directional row draws through attackDir, and
        // an executeAttack that resolved to a named command move never reaches it.
        const q = mk();
        q.isGrounded = !air; q.attackAir = air; q.state = st; q.attackT = 0;
        q.attackDir = d || 'neutral';
        q.getInputAxis = () => d === 'fwd' ? q.facing : d === 'back' ? -q.facing : 0;
        q.isDownPressed = () => d === 'down';
        q.isUpPressed = () => d === 'up';
        sample(q, air ? airHits : groundHits);
      }
    }
  }
  // ⛔ THE LUNGE AND THE WHIP NEED A STATE THE SWEEP ABOVE NEVER BUILDS. The lunge only
  // exists while a dash is in flight (dashTimer > 0), the whip only when the foe is
  // inside WHIP_RANGE (mk() parks the dummy 260px away, more than twice that), and the
  // air spin only while AIRBORNE on a neutral Special. None is
  // reachable by pressing buttons at a distant opponent, so both would read as packed-and-
  // dark forever while working perfectly in a real match. Same attackAnim walk as below.
  for (const kind of ['lunge', 'whip', 'spin']) {
    const p = mk();
    const air = kind === 'spin';
    p.isGrounded = !air; p.attackAir = air; p.vy = air ? 100 : 0;
    p.getInputAxis = () => 0;
    p.isDownPressed = () => false; p.isUpPressed = () => false;
    if (kind === 'lunge') { p.dashTimer = 0.1; p.dashDir = p.facing; p.vx = 400; }
    else if (kind === 'whip') { p.opponent.x = p.x + 80; }   // inside WHIP_RANGE (132)
    try { p.executeAttack(kind === 'lunge' ? STATE.ATTACK_LIGHT : STATE.ATTACK_SPECIAL); }
    catch (e) { errors.push(kind + ' ' + e.message.slice(0, 50)); continue; }
    p.isGrounded = !air; p.attackAir = air;
    if (!p.attackAnim) continue;
    const dur = p.attackAnim.dur;
    for (let s = 0; s < 24; s++) {
      p.attackAnim.start = animClock * 1000 - (s / 24) * dur * 0.99;
      try { (air ? airHits : groundHits).add(spriteFrameIndex(p, F)); }
      catch (e) { errors.push(kind + ' draw ' + e.message.slice(0, 40)); break; }
    }
  }
  // ⛔ THE WIRE CONVERSION IS ITS OWN SWEEP, because sample() cannot reach it. sample()
  // nulls attackAnim on purpose — that is what makes the six-beat rows walk — but the
  // conversion's draw branch reads its elapsed fraction FROM attackAnim, so with it null
  // the branch reads el=1, clears wireConv and falls straight through. The result was a
  // gate calling all four finishers dark while they were demonstrably on screen
  // (tools/drive_oni_wire.mjs), i.e. crying wolf at its own blind spot. Here the fraction
  // is driven by moving attackAnim.start, which is the only input that branch has.
  for (const [air, foeAir, ax] of [[false, false, +1], [false, false, 0], [false, false, -1],
                                   [true, true, 0], [true, false, 0]]) {
    const p = mk();
    p.isGrounded = !air; p.vy = air ? 120 : 0;
    p.opponent.isGrounded = !foeAir; p.opponent.vy = foeAir ? -80 : 0;
    p.getInputAxis = () => ax * p.facing;
    p.isDownPressed = () => false; p.isUpPressed = () => false;
    p.wireBind = 0.55; p.wireBindFoe = p.opponent;
    try { p.executeAttack(STATE.ATTACK_SPECIAL); }
    catch (e) { errors.push('wire ' + e.message.slice(0, 50)); continue; }
    if (!p.wireConv || !p.attackAnim) continue;
    const dur = p.attackAnim.dur;
    for (let s = 0; s < 24; s++) {
      p.attackAnim.start = animClock * 1000 - (s / 24) * dur * 0.99;
      try { (air ? airHits : groundHits).add(spriteFrameIndex(p, F)); }
      catch (e) { errors.push('wire draw ' + e.message.slice(0, 40)); break; }
    }
  }
  // JUMPS — every direction, walked along the real vy arc.
  for (const d of DIRS) {
    for (const dbl of [false, true]) {
      const p = mk(); p.isGrounded = true; p.jumpsLeft = 2;
      p.getInputAxis = () => d === 'fwd' ? p.facing : d === 'back' ? -p.facing : 0;
      p.isDownPressed = () => false; p.isUpPressed = () => false;
      try { p.executeJump(); if (dbl) { p.isGrounded = false; p.executeJump(); } }
      catch (e) { errors.push('jump ' + e.message.slice(0, 50)); continue; }
      for (const vy of [-460, -380, -260, -150, -40, 0, 60, 150, 260, 380, 470]) {
        p.vy = vy; p.isGrounded = false; p.state = STATE.JUMP;
        try { airHits.add(spriteFrameIndex(p, F)); } catch (e) { errors.push('jump draw ' + e.message.slice(0, 40)); }
      }
    }
  }
  // ⛔ THE DASH ITSELF, not a dash attack. The lunge sweep below runs dashTimer through
  // executeAttack, which consumes it — so the plain "dashing and NOT attacking" frames were
  // never sampled, and a blur row drawn for exactly that window read as packed-and-dark.
  for (const g of [true, false]) {
    for (const t of [0.15, 0.11, 0.07, 0.03]) {
      const p = mk();
      p.isGrounded = g; p.dashTimer = t; p.dashDir = p.facing; p.vx = p.facing * 800;
      p.state = STATE.IDLE;
      try { (g ? groundHits : airHits).add(spriteFrameIndex(p, F)); }
      catch (e) { errors.push('dash ' + e.message.slice(0, 40)); }
    }
  }
  // ⛔ THE WALL KICK-OFF, for the same reason as the dash: wallJumpLock is a momentum
  // window rather than a state, so no button press in this harness produces it and a cell
  // drawn only for that window reads as packed-and-dark forever.
  for (const t of [0.12, 0.06]) {
    const p = mk();
    p.isGrounded = false; p.wallJumpLock = t; p.vy = -300; p.state = STATE.JUMP;
    try { airHits.add(spriteFrameIndex(p, F)); }
    catch (e) { errors.push('walljump ' + e.message.slice(0, 40)); }
  }
  // ⛔ THE METEOR PLUNGE, because nothing else in this sweep sets slamPhase. It is a flag
  // read straight out of the draw function (if p.slamPhase return F.kstomp ...), not a
  // state you can reach by pressing a button here — so without it the sweep cannot see the
  // one path a shared cell like kstomp still lives on. That mattered the moment Oni got his
  // own down-air: kstomp stopped being his airborne Down+Light picture and the gate called
  // it a REGRESSION, when it is still exactly as reachable as it was, on the plunge.
  for (const phase of [1, 2]) {
    const p = mk();
    p.isGrounded = false; p.attackAir = true; p.vy = 700;
    p.state = STATE.ATTACK_HEAVY; p.slamPhase = phase; p.attackT = 0;
    try { airHits.add(spriteFrameIndex(p, F)); }
    catch (e) { errors.push('slam ' + e.message.slice(0, 40)); }
  }
  // PLAIN STATES.
  for (const st of ['IDLE', 'RUN', 'BLOCKING', 'STUNNED', 'CROUCH', 'PARRY_STANCE']) {
    if (STATE[st] === undefined) continue;
    for (const g of [true, false]) {
      const p = mk(); p.isGrounded = g; p.state = STATE[st];
      sample(p, g ? groundHits : airHits);
    }
  }

  const drawn = new Set([...groundHits, ...airHits]);
  const famG = new Set(), famA = new Set();
  for (const c of groundHits) for (const f of (cellFam[c] || [])) famG.add(f);
  for (const c of airHits) for (const f of (cellFam[c] || [])) famA.add(f);

  const all = new Set(Object.keys(F).map(fam));
  const dark = [...all].filter(f => !famG.has(f) && !famA.has(f)).sort();
  const famAll = {}; for (const f of all) famAll[f] = true;
  const airOnly = [...famA].filter(f => !famG.has(f)).sort();

  // ---- static pixel checks on the sheet the browser actually loaded ----
  const c = document.createElement('canvas');
  c.width = man.frameW; c.height = man.frameH;
  const g2 = c.getContext('2d', { willReadFrequently: true });
  const banner = [], clipped = [];
  const byCell = {};
  for (const k in F) (byCell[F[k]] ||= []).push(k);
  for (let col = 0; col < man.cols; col++) {
    g2.clearRect(0, 0, man.frameW, man.frameH);
    g2.drawImage(man.img, col * man.frameW, 0, man.frameW, man.frameH, 0, 0, man.frameW, man.frameH);
    const d = g2.getImageData(0, 0, man.frameW, man.frameH).data;
    let minY = 1e9, maxY = -1, minX = 1e9, maxX = -1;
    const rowW = new Array(man.frameH).fill(0);
    for (let y = 0; y < man.frameH; y++)
      for (let x = 0; x < man.frameW; x++)
        if (d[(y * man.frameW + x) * 4 + 3] > 24) {
          rowW[y]++; if (y < minY) minY = y; if (y > maxY) maxY = y;
          if (x < minX) minX = x; if (x > maxX) maxX = x;
        }
    if (maxY < 0) continue;
    const names = (byCell[col] || ['cell' + col]).join(',');
    const widest = Math.max(...rowW);
    if (widest && rowW[minY] / widest > 0.70 && rowW[minY] > 20)
      banner.push({ cell: names, topRow: rowW[minY], widest });
    const edges = [];
    if (minY <= 0) edges.push('top');
    if (maxY >= man.frameH - 1) edges.push('bottom');
    if (minX <= 0) edges.push('left');
    if (maxX >= man.frameW - 1) edges.push('right');
    if (edges.length) clipped.push({ cell: names, edges });
  }

  return { cols: man.cols, keys: Object.keys(F).length,
           box: [man.frameW, man.frameH, man.footY],
           cellsDrawn: drawn.size, dark, airOnly, banner, clipped, famAll,
           errors: [...new Set(errors)].slice(0, 8) };
})()`;

let out;
try { out = await evaluate(script); } finally { chrome.kill('SIGKILL'); }
if (out.exceptionDetails) { console.error(out.exceptionDetails.text || 'evaluate threw'); process.exit(2); }
const r = out.result.value;

console.log(`  box ${r.box[0]}x${r.box[1]} footY ${r.box[2]} · ${r.cols} cells · ${r.keys} keys · ${r.cellsDrawn} cells reachable`);
let fail = 0;
const say = (tag, list, fmt) => {
  if (!list.length) { console.log(`  ✓ ${tag}: none`); return; }
  fail++;
  console.log(`  ⛔ ${tag}: ${list.length}`);
  for (const x of list.slice(0, 14)) console.log('       ' + fmt(x));
  if (list.length > 14) console.log(`       ...and ${list.length - 14} more`);
};
// ⛔ DARK IS A REGRESSION CHECK, NOT AN ABSOLUTE ONE, and that distinction is the
// difference between a gate people run and a gate people ignore. A sweep cannot reach
// every state a real match reaches — dash, landing and get-up need setup this harness
// does not do — so reporting every unreached family as a defect produces a wall of
// false positives. check_moves.py already learned this the expensive way: it cried 151
// dead cells of which exactly ONE was real, and the noise is why nobody read it.
//
// So the baseline records what WAS reachable. A family fails only if it regressed
// (drew before, dark now) or is NEW and never draws — which is precisely the cartwheel
// case: packed, wired, and silent through three SHEET_V bumps.
const BASE = path.join(here, 'tools', `gate_${NAME}.baseline.json`);
const fs = await import('node:fs');
let base = null;
try { base = JSON.parse(fs.readFileSync(BASE, 'utf8')); } catch {}
if (process.argv.includes('--update-baseline')) {
  const reachable = [...new Set(Object.keys(r.famAll).filter(f => !r.dark.includes(f)))].sort();
  fs.writeFileSync(BASE, JSON.stringify({ reachable, knownDark: r.dark.sort() }, null, 1) + '\n');
  console.log(`  baseline written: ${reachable.length} reachable, ${r.dark.length} known-dark`);
} else if (!base) {
  console.log(`  ⓘ no baseline yet — run once with --update-baseline to record the current state`);
  console.log(`     (dark right now: ${r.dark.length} families, unjudged)`);
} else {
  const regressed = base.reachable.filter(f => r.dark.includes(f));
  const newDark = r.dark.filter(f => !base.knownDark.includes(f) && !base.reachable.includes(f));
  say('REGRESSED families (drew at baseline, dark now)', regressed, x => x);
  say('NEW families that never draw (packed but unwired)', newDark, x => x);
}
say('BANNER cells (caption text packed as art)', r.banner, x => `${x.cell}  top row ${x.topRow}px of ${x.widest}px widest`);
say('CLIPPED cells (art on the frame box edge)', r.clipped, x => `${x.cell}  ${x.edges.join(',')}`);
if (r.errors.length) { fail++; console.log('  ⛔ exceptions while driving:'); r.errors.forEach(e => console.log('       ' + e)); }
if (r.airOnly.length) console.log(`  ⓘ air-only families (check none are grounded art): ${r.airOnly.join(', ')}`);

console.log(fail ? `\n  GATE FAILED — ${fail} defect class(es). Fix before showing the owner.\n`
                 : '\n  GATE PASSED\n');
process.exit(fail ? 1 : 0);
