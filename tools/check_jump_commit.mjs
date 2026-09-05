#!/usr/bin/env node
// A SWING IS COMMITTED — you cannot jump out of your own recovery.
//
// executeJump gated on stun, grab, throw and roll, but never on the attack state, so W
// lifted a fighter straight out of any attack's recovery tail: measured before the fix,
// all nine fighters and all four tiers, 36 of 36 presses cancelled windows of 0.18s to
// 0.73s. Every whiffed attack in the game was free.
//
// The guard is placed BELOW the wall-jump, ceiling-latch and anchor-release branches on
// purpose, so wall escapes during an attack still work (Exile and Shin throw from a
// cling). This check pins BOTH halves — the hole is closed AND nothing else was closed
// with it, which is the half a one-sided test would miss.
//
//   PORT=9101 node tools/check_jump_commit.mjs
import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const port = +(process.env.PORT || 9100), dbg = 9375;
const who = await fetch(`http://127.0.0.1:${port}/whoami`).then(r => r.json()).catch(() => null);
if (!who) { console.error(`no server on :${port}`); process.exit(1); }
if (path.resolve(who.tree) !== path.resolve(process.cwd())) {
  console.error(`:${port} serves ${who.tree} — rebind before trusting this`); process.exit(1);
}
spawnSync('pkill', ['-f', `remote-debugging-port=${dbg}`], { stdio: 'ignore' });
for (let i = 0; i < 60; i++) {
  const s = spawnSync('pgrep', ['-f', `remote-debugging-port=${dbg}`], { encoding: 'utf8' });
  if (!s.stdout || !s.stdout.trim()) break;
  await new Promise(r => setTimeout(r, 100));
}
const profile = await mkdtemp(path.join(tmpdir(), 'sg-'));
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ['--headless=new', '--disable-gpu', '--no-first-run', `--remote-debugging-port=${dbg}`,
   `--user-data-dir=${profile}`, `http://127.0.0.1:${port}/`], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let page = null;
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

const out = await ev(String.raw`(async()=>{
 for(let i=0;i<600;i++){
   const up = typeof NINJA_ROSTER!=='undefined' && typeof startNewGame==='function'
      && typeof fireCombatKey==='function' && typeof SPRITES!=='undefined';
   if (up && NINJA_ROSTER.every(s2 => { const m = SPRITES[s2.name.toLowerCase()]; return m && m.ready; })) break;
   await new Promise(r=>setTimeout(r,50));
 }
 const TIERS = { Light:'KeyF', Medium:'KeyJ', Heavy:'KeyG', Special:'KeyH' };
 const rows = [];
 for (let idx=0; idx<NINJA_ROSTER.length; idx++) {
  gameMode='versus'; p1Pick=idx; p2Pick = idx===0?1:0;
  try { startNewGame(); } catch(e) { rows.push({who:'?',kind:'fatal',err:e.message.slice(0,60)}); continue; }
  roundIntroTimer=0; paused=false; hitstopRemaining=0;
  const who = NINJA_ROSTER[idx].name;
  // A FULL reset. Leaving attackAir or a stale attackAnim behind made the next press
  // fall straight through to IDLE, and the run then "passed" on rows where no attack
  // had started at all.
  const reset = () => { for (const k in keys) keys[k]=false;
    const p=player1;
    p.x=300; p.facing=1; p.state=STATE.IDLE; p.attackT=0; p.lock=0; p.recoveryTimer=0;
    p.stunTimer=0; p.rollTimer=0; p.rollRecover=0; p.sayaLock=0; p.dashTimer=0;
    p.chakra=100; p.stamina=100; p._lt=p._ht=-1e9; p.isGrounded=true; p.vy=0;
    p.y=GROUND_Y-p.height; p.jumpsLeft=1; p.attackAir=false; p.chainComboTier=0;
    p.jumpDir=null; p.wallDir=0; p.ceilLatch=0; p.anchorTimer=0; p.attackAnim=null;
    p.recoveryTotal=0; p.spinAnim=false; p.moveArt=null; return p; };

  // ---- HALF ONE: the hole must be closed.
  for (const [tier,code] of Object.entries(TIERS)) {
    const p = reset();
    try { fireCombatKey(code); } catch(e) {}
    const rec = +(p.recoveryTimer||0).toFixed(2);
    const st = Object.keys(STATE).find(k=>STATE[k]===p.state) || '?';
    const vy0 = p.vy, gnd0 = p.isGrounded;
    try { fireCombatKey('KeyW'); } catch(e) {}
    rows.push({ who, kind:'cancel', tier, rec, st,
                bad: p.vy < vy0 - 50 || (gnd0 && !p.isGrounded), vy: Math.round(p.vy) });
  }

  // ---- HALF TWO: and nothing else may be closed with it.
  let p = reset();
  try { fireCombatKey('KeyW'); } catch(e) {}
  rows.push({ who, kind:'escape', tier:'idle jump', bad: !(p.vy < -50), vy: Math.round(p.vy) });

  p = reset(); p.isGrounded=false; p.y=GROUND_Y-p.height-140; p.vy=60; p.jumpsLeft=1;
  try { fireCombatKey('KeyW'); } catch(e) {}
  rows.push({ who, kind:'escape', tier:'air jump', bad: !(p.vy < -50), vy: Math.round(p.vy) });

  p = reset(); p.isGrounded=false; p.y=GROUND_Y-p.height-160; p.vy=40; p.wallDir=1; p.jumpsLeft=0;
  try { fireCombatKey('KeyF'); } catch(e) {}
  try { fireCombatKey('KeyW'); } catch(e) {}
  rows.push({ who, kind:'escape', tier:'wall jump mid-attack', bad: !(p.vy < -50 || p.vx !== 0), vy: Math.round(p.vy) });

  p = reset(); p.isGrounded=false; p.y=GROUND_Y-p.height-200; p.vy=0; p.ceilLatch=1;
  try { fireCombatKey('KeyF'); } catch(e) {}
  try { fireCombatKey('KeyW'); } catch(e) {}
  rows.push({ who, kind:'escape', tier:'latch drop mid-attack', bad: p.ceilLatch !== 0, vy: Math.round(p.vy) });
 }
 return rows;
})()`);
ws.close(); chrome.kill('SIGKILL');

console.log('\n  A SWING IS COMMITTED — and only the swing\n');
const fatals = out.filter(r => r.kind === 'fatal');
const noRec = out.filter(r => r.kind === 'cancel' && !(r.rec > 0));
const bad = out.filter(r => r.bad);
for (const r of out) {
  if (r.kind === 'fatal') { console.log(`  ⛔ ${r.who} FATAL ${r.err}`); continue; }
  if (!r.bad && !process.argv.includes('-v')) continue;
  const what = r.kind === 'cancel'
    ? `jumped out of its own recovery (rec=${r.rec}s, ${r.st}, vy ${r.vy})`
    : `NO LONGER POSSIBLE (vy ${r.vy})`;
  console.log(`  ⛔ ${r.who.padEnd(12)} ${String(r.tier).padEnd(22)} ${what}`);
}
const cancels = out.filter(r => r.kind === 'cancel'), escapes = out.filter(r => r.kind === 'escape');
console.log(`  ${cancels.filter(r=>!r.bad).length}/${cancels.length} attacks hold their recovery` +
            ` · ${escapes.filter(r=>!r.bad).length}/${escapes.length} escape routes still work`);
// ⛔ A ROW WHERE NO ATTACK STARTED PROVES NOTHING. Counting it as a pass is how an
// earlier version of this probe reported 36/36 clean on rows that never left IDLE.
if (noRec.length) console.log(`  ⛔ ${noRec.length} rows never entered a recovery — the press did nothing, so they are NOT evidence`);
console.log(`\n  ${bad.length + fatals.length + noRec.length ? '⛔ ' + (bad.length + fatals.length + noRec.length) + ' PROBLEM(S)' : 'all correct'}\n`);
process.exit(bad.length + fatals.length + noRec.length ? 1 : 0);
