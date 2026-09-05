#!/usr/bin/env node
// Press the ACTUAL KEYS. Every other check in this repo calls executeAttack directly with
// getInputAxis/isDownPressed/isUpPressed stubbed — which proves the move works once it is
// reached, and proves nothing about whether a key press reaches it.
//
// That gap is real: fireCombatKey is the single funnel every input source passes through,
// and it has early returns in it. A move can be perfect and still be unreachable because
// the funnel ate the press first.
//
//   node tools/drive_real_input.mjs                 # oni, versus + training
//   node tools/drive_real_input.mjs --name kael
//
// Direction is set by writing the REAL `keys` map, so getInputAxis() and isDownPressed()
// run their own code rather than a stub that agrees with the test.
import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const NAME = (process.argv.includes('--name')
  ? process.argv[process.argv.indexOf('--name') + 1] : 'oni').toLowerCase();
const port = +(process.env.PORT || 9101), dbg = 9368;
const profile = await mkdtemp(path.join(tmpdir(), 'ri-'));
const who = await fetch(`http://127.0.0.1:${port}/whoami`).then(r => r.json()).catch(() => null);
if (!who) { console.error(`no server on :${port} — python3 tools/serve.py ${port} web`); process.exit(1); }
if (path.resolve(who.tree) !== path.resolve(process.cwd())) {
  console.error(`:${port} is serving ${who.tree}; run against this tree's server`);
  process.exit(1);
}
spawnSync('pkill', ['-f', `remote-debugging-port=${dbg}`], { stdio: 'ignore' });
// ⛔ WAIT FOR IT TO ACTUALLY BE GONE. pkill returns immediately; the old Chrome is still
// listening on the debug port for a moment, so back-to-back runs attached to the DYING
// page and died mid-sweep with "Execution context was destroyed" — which reads exactly
// like an engine crash and is not one. Cost a bisect to find out.
for (let i = 0; i < 60; i++) {
  const still = spawnSync('pgrep', ['-f', `remote-debugging-port=${dbg}`], { encoding: 'utf8' });
  if (!still.stdout || !still.stdout.trim()) break;
  await new Promise(r => setTimeout(r, 100));
}
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ['--headless=new', '--disable-gpu', '--no-first-run', `--remote-debugging-port=${dbg}`,
   `--user-data-dir=${profile}`, `http://127.0.0.1:${port}/`], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let page;
for (let i = 0; i < 100 && !page; i++) {
  try {
    const l = await fetch(`http://127.0.0.1:${dbg}/json/list`).then(r => r.json());
    page = l.find(t => t.type === 'page' && t.url.includes(String(port)));
  } catch {}
  if (!page) await sleep(100);
}
if (!page) { console.error('chrome never came up'); process.exit(1); }
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener('open', r, { once: true }));
let id = 1; const pend = new Map();
ws.addEventListener('message', e => {
  const m = JSON.parse(e.data);
  if (m.id && pend.has(m.id)) { const p = pend.get(m.id); pend.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); }
});
const ev = x => new Promise((res, rej) => {
  const n = id++; pend.set(n, { res, rej });
  ws.send(JSON.stringify({ id: n, method: 'Runtime.evaluate', params: { expression: x, awaitPromise: true, returnByValue: true } }));
}).then(r => { if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text); return r.result.value; });

const ALLF = process.argv.includes('--all');
let out;
try {
  out = await ev(String.raw`(async()=>{
 const process_all=${ALLF};
 const NM=${JSON.stringify(NAME)};
 for(let i=0;i<400;i++){
   if(typeof NINJA_ROSTER!=='undefined' && typeof startNewGame==='function'
      && typeof fireCombatKey==='function' && typeof SPRITES!=='undefined'
      && NINJA_ROSTER.every(s => SPRITES[s.name.toLowerCase()]?.ready)) break;
   await new Promise(r=>setTimeout(r,50));
 }
 if (typeof NINJA_ROSTER === 'undefined' || typeof SPRITES === 'undefined'
     || !NINJA_ROSTER.every(s => SPRITES[s.name.toLowerCase()]?.ready))
   return {fatal:'roster sheets did not become ready'};
 const ALL = process_all;
 const picks = ALL ? NINJA_ROSTER.map((_,i)=>i)
                   : [NINJA_ROSTER.findIndex(s=>s.name.toLowerCase()===NM)];
 if(picks[0]<0) return {fatal:'not on the roster: '+NM};

 // P1 keys, straight out of fireCombatKey: W jump, F/J/G/H attacks.
 const PRESS = { Light:'KeyF', Medium:'KeyJ', Heavy:'KeyG', Special:'KeyH' };
 // ⛔ THE DIAGONALS ARE NOT DECORATION. getInputAxis() is nonzero on up-fwd and
 // down-back, so a branch that tests the axis without !down && !up EATS a diagonal
 // belonging to a move filed below it. Five cardinals can never see that class of bug:
 // it only exists where two directions are held at once.
 const HOLD  = { neutral:[], fwd:['KeyD'], back:['KeyA'], down:['KeyS'], up:['KeyW'],
                 upfwd:['KeyW','KeyD'], upback:['KeyW','KeyA'],
                 downfwd:['KeyS','KeyD'], downback:['KeyS','KeyA'] };

 // DIRS=upfwd,back  narrows the sweep — used to bisect which press kills the page.
 const ONLY = ${JSON.stringify(process.env.DIRS ? process.env.DIRS.split(',') : null)};
 if (ONLY) for (const k of Object.keys(HOLD)) if (!ONLY.includes(k)) delete HOLD[k];

 const results = {};
 for (const idx of picks) {
  const who = NINJA_ROSTER[idx].name;
  for (const mode of ['versus','training']) {
   gameMode = mode; p1Pick = idx; p2Pick = idx===0?1:0;
   try { startNewGame(); } catch(e) { results[who+'|'+mode] = {fatal:e.message.slice(0,80)}; continue; }
   const man = SPRITES[who.toLowerCase()];
   const byIdx = {};
   if (man && man.frames) for (const [k,i] of Object.entries(man.frames)) (byIdx[i]||=[]).push(k);
   const famOf = i => { const s2=new Set(); for(const k of (byIdx[i]||[])){const m=k.match(/^([a-z_]+?)\d+$/); s2.add(m?m[1]:k);} return [...s2]; };
   roundIntroTimer = 0; paused = false; hitstopRemaining = 0;
   const rows = [];
   for (const [tier, code] of Object.entries(PRESS)) {
     for (const [dir, held] of Object.entries(HOLD)) {
       // a clean fighter every press — no carried recovery, no stale chain
       for (const k in keys) keys[k] = false;
       startNewGame();
       roundIntroTimer = 0; paused = false; hitstopRemaining = 0;
       const p = player1;
       p.x = 200; p.facing = 1;
       // ⛔ y TOO. Without it a press that ends airborne (the chain anchor) leaves the
       // NEXT press starting in mid-air with isGrounded lied back to true, and its dy
       // measures from the wrong floor.
       p.y = GROUND_Y - p.height;
       p.isGrounded = true; p.attackAir = false; p.vy = 0;
       p.state = STATE.IDLE; p.attackT = 0; p.lock = 0; p.recoveryTimer = 0;
       p.stunTimer = 0; p.rollTimer = 0; p.rollRecover = 0; p.sayaLock = 0;
       p.chainComboTier = 0; p.dashTimer = 0; p.chakra = 100; p.stamina = 100;
       p._lt = p._ht = -1e9;
       p.wireBind = 0; p.wireConv = null;
       // MODE2=1 drives the SECOND stance/mode, where several fighters have a whole
       // replacement branch set. Those branches are unreachable with the mode off, so a
       // cardinal-or-diagonal sweep that never toggles it is blind to half the routing.
       if (${JSON.stringify(!!process.env.MODE2)}) {
         if (p.spec.id === 6) { p.karma = 100; p.cracked = true; }
         if (p.spec.id === 2) p.kageNui = true;
         if (p.spec.id === 1) p.hanbo = true;
       }
       if (player2) { player2.x = 290; player2.isGrounded = true; }
       for (const k of held) keys[k] = true;
       // W keydown jumps before the attack keydown; merely holding W invents a
       // grounded up-attack. Keep this assertion so the harness cannot regress silently.
       if (held.includes('KeyW')) {
         fireCombatKey('KeyW');
         if (p.isGrounded) throw new Error(who + ': Up did not jump');
       }

       const before = p.kageActs.length;
       const st0 = p.state, x0 = p.x, y0 = p.y;
       let err = null;
       // ⛔ THE REAL FUNNEL. Not executeAttack — fireCombatKey, the one every keyboard,
       // touch and mouse press goes through, early returns and all.
       try { fireCombatKey(code); } catch(e) { err = e.message.slice(0,70); }
       const box = p.kageActs.length - before;
       const st1 = Object.keys(STATE).find(k=>STATE[k]===p.state) || '?';
       const moved = p.state !== st0;
       // what does it DRAW — so two buttons sharing one animation is visible, which is
       // the owner's other complaint and is invisible to a "did it fire" check
       let drew = '-';
       try {
         if (man && man.ready) {
           const fams = new Set();
           for (let s2=0; s2<14; s2++) {
             if (p.attackAnim) p.attackAnim.start = animClock*1000 - (s2/14)*p.attackAnim.dur*0.99;
             else p.attackT = (s2/14)*0.4;
             for (const f of famOf(spriteFrameIndex(p, man.frames))) fams.add(f);
           }
           drew = [...fams].filter(f=>!['idle','stand','run_clean'].includes(f)).join(',') || '-';
         }
       } catch(e) { err = e.message.slice(0,70); }
       rows.push({ tier, dir, code, box, state: st1, drew, acted: box>0 || moved, err,
                   gnd: !!p.isGrounded, dx: Math.round(p.x-x0), dy: Math.round(p.y-y0) });
       for (const k in keys) keys[k] = false;
     }
   }
   results[who+'|'+mode] = { rows };
  }
 }
 return { results, all: ALL };
})()`);
} finally {
  ws.close(); chrome.kill('SIGKILL');
}

if (out.fatal) { console.error(out.fatal); process.exit(2); }

// ---- DEAD INPUTS: a press that produced neither a hitbox nor a state change ----
const rows = [];
for (const [key, r] of Object.entries(out.results)) {
  const [who, mode] = key.split('|');
  if (r.fatal) { rows.push({ who, mode, fatal: r.fatal }); continue; }
  for (const x of r.rows) rows.push({ who, mode, ...x });
}
if (process.argv.includes('--raw')) {
  for (const r of rows.filter(x => x.mode === 'versus' && !x.fatal))
    console.log(`${r.who.padEnd(11)} ${(r.dir+'+'+r.tier).padEnd(17)} box=${String(r.box).padEnd(2)}`
      + ` ${String(r.state).padEnd(15)} gnd=${r.gnd?'Y':'n'} dx=${String(r.dx).padStart(4)}`
      + ` dy=${String(r.dy).padStart(4)} drew=${r.drew}${r.err ? ' ERR='+r.err : ''}`);
}
const dead = rows.filter(r => !r.fatal && !r.acted);
const fatals = rows.filter(r => r.fatal);
const errors = rows.filter(r => r.err);
for (const r of [...fatals, ...errors]) console.error(r.who, r.mode, r.dir, r.tier, r.fatal || r.err);

console.log('\n  REAL-KEY AUDIT — every press through fireCombatKey, both modes\n');
console.log(`  ${rows.filter(r=>!r.fatal).length} presses driven across ` +
            `${new Set(rows.map(r=>r.who)).size} fighter(s)\n`);

// a press alive in versus and dead in training is the funnel eating it as a hotkey
const alive = {};
for (const r of rows) if (!r.fatal) alive[`${r.who}|${r.mode}|${r.dir}+${r.tier}`] = r.acted;
const eaten = [];
for (const k of Object.keys(alive)) {
  const [who, mode, inp] = k.split('|');
  if (mode !== 'versus' || !alive[k]) continue;
  if (alive[`${who}|training|${inp}`] === false) eaten.push(`${who} ${inp}`);
}

if (dead.length) {
  console.log(`  ⛔ DEAD INPUTS (${dead.length}) — key pressed, nothing happened:`);
  for (const d of dead) console.log(`     ${d.who.padEnd(12)} ${d.mode.padEnd(9)} ${(d.dir+' + '+d.tier).padEnd(18)} ${d.code}`);
  console.log('');
} else console.log('  \u2713 no dead inputs\n');

if (eaten.length) {
  console.log(`  \u26d4 EATEN BY A TRAINING HOTKEY (${eaten.length}) — works in versus, dead in training:`);
  for (const e of eaten) console.log(`     ${e}`);
  console.log('     A training hotkey that reuses a combat key returns before the attack');
  console.log('     dispatch. P1 owns W/F/G/H/C/V; P2 owns ArrowUp/I/O/P/M/K.\n');
}

// ---- DIAGONAL STEAL -------------------------------------------------------
// A diagonal holds a vertical AND a horizontal at once. If the diagonal behaves
// EXACTLY like its horizontal half while its vertical half does something else,
// the vertical was ignored: some branch tested getInputAxis() without !down && !up
// and ate a press that belonged to a move filed below it. That is a whole move the
// player cannot reach, and no cardinal-only sweep can see it.
// ⛔ NO ART IN THIS FINGERPRINT. Exile's Iai cross draws `gsback,glback` on Back+Special
// and `light` on UpBack+Special — different cells, but the SAME move: both travel 784px
// in one frame. Fingerprinting on art called that two moves and hid the steal. What a
// move IS is what it does: the state it enters, where it puts you, what it spawns.
const fp = r => r && !r.fatal ? `${r.state}|${r.gnd}|${r.box}|${r.dx}|${r.dy}` : null;
const at = (who, dir, tier) =>
  fp(rows.find(r => r.who === who && r.mode === 'versus' && r.dir === dir && r.tier === tier));
const DIAG = { upfwd: ['up', 'fwd'], upback: ['up', 'back'],
               downfwd: ['down', 'fwd'], downback: ['down', 'back'] };
const steals = [], hshadow = [];
for (const who of [...new Set(rows.map(r => r.who))]) {
  for (const tier of ['Light', 'Medium', 'Heavy', 'Special']) {
    for (const [d, [v, h]] of Object.entries(DIAG)) {
      if (v === 'up') continue; // Up jumps: comparing it with a grounded horizontal is invalid.
      const fd = at(who, d, tier), fv = at(who, v, tier), fh = at(who, h, tier);
      if (!fd || !fv || !fh) continue;
      // the vertical move is real and distinct, yet the diagonal played the horizontal
      if (fd === fh && fv !== fh) steals.push({ who, d, tier, v, h });
      else if (fd === fv && fh !== fv) hshadow.push({ who, d, tier, v, h });
    }
  }
}
if (steals.length) {
  console.log(`  ⛔ DIAGONAL STEAL (${steals.length}) — the vertical half of the input is ignored,`);
  console.log('     so the move on that vertical is UNREACHABLE while a direction is held:\n');
  for (const s2 of steals)
    console.log(`     ${s2.who.padEnd(12)} ${(s2.d + '+' + s2.tier).padEnd(18)} played ${s2.h}+${s2.tier}`
                + `  — ${s2.v}+${s2.tier} never runs`);
  console.log('');
} else console.log('  ✓ no down-diagonal steals detected (Up combinations start airborne)\n');
if (hshadow.length) {
  console.log(`  · vertical wins the diagonal (${hshadow.length}) — normal where the vertical move is`);
  console.log('    the more specific one; listed so the choice is visible, not a defect:');
  for (const s2 of hshadow)
    console.log(`     ${s2.who.padEnd(12)} ${(s2.d + '+' + s2.tier).padEnd(18)} played ${s2.v}+${s2.tier}`);
  console.log('');
}

// ---- SHARED FRAMES: two different inputs playing the same animation ----
console.log('  SHARED ANIMATIONS — one row of art on more than one button:\n');
let shareCount = 0;
for (const who of [...new Set(rows.map(r => r.who))]) {
  const mine = rows.filter(r => r.who === who && r.mode === 'versus' && !r.fatal && r.drew && r.drew !== '-');
  const byFam = {};
  for (const r of mine) (byFam[r.drew] ||= []).push(`${r.dir}+${r.tier}`);
  const shared = Object.entries(byFam).filter(([, v]) => v.length > 1);
  if (!shared.length) continue;
  console.log(`  ${who}`);
  for (const [fam, inputs] of shared) {
    shareCount++;
    console.log(`     ${fam.padEnd(22)} <- ${inputs.join(' , ')}`);
  }
}
if (!shareCount) console.log('     none');

const bad = dead.length + fatals.length + errors.length;
console.log(`\n  ${bad ? bad + ' failures (dead inputs or errors)' : 'no dead inputs or errors'} \u00b7 ${shareCount} shared-animation collision(s)`);
process.exit(bad ? 1 : 0);
