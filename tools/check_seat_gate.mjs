#!/usr/bin/env node
// A HUMAN KEY MUST NOT DRIVE A CPU BODY.
//
// fireCombatKey gates every P2 branch on `p2Live = isP2Human()`. The P1 branches carry no
// seat gate at all — so in WATCH (both fighters have a brain), with the spectate modifier
// on, or in teams/brawl at teamsSeat 2, cpuThink drives player1 and the human's keys still
// fired his jump, all four attacks, kawarimi, stance and the throw pairing on top of the
// brain. This presses the real keys through the real funnel in each mode and asks a single
// question: did a fighter that isCpuDriven() reports as CPU respond to a human press?
//
//   PORT=9101 node tools/check_seat_gate.mjs
import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const port = +(process.env.PORT || 9100), dbg = 9373;
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
 // Every key fireCombatKey routes for a seat, with the seat it is supposed to drive.
 const P1KEYS = ['KeyW','KeyF','KeyJ','KeyG','KeyH','KeyC','KeyV'];
 const P2KEYS = ['ArrowUp','KeyI','KeyU','KeyO','KeyP','KeyM','KeyK'];
 // mode, spectate, teamsSeat — the three things that decide who has a brain.
 const CASES = [
   { mode:'versus',   spec:false, seat:0 },
   { mode:'2p',       spec:false, seat:0 },
   { mode:'training', spec:false, seat:0 },
   { mode:'watch',    spec:false, seat:0 },
   { mode:'versus',   spec:true,  seat:0 },
   { mode:'teams',    spec:false, seat:2 },
 ];
 const rows = [];
 for (const c of CASES) {
  gameMode = c.mode; spectate = c.spec;
  if (typeof teamsSeat !== 'undefined') teamsSeat = c.seat;
  p1Pick = 0; p2Pick = 1;
  try { startNewGame(); } catch(e) { rows.push({...c, key:'-', err:e.message.slice(0,70)}); continue; }
  roundIntroTimer = 0; paused = false; hitstopRemaining = 0;
  for (const [seat, KEYS] of [[1, P1KEYS], [2, P2KEYS]]) {
    const p = seat === 1 ? player1 : player2;
    if (!p) continue;
    // ⛔ THE AUTHORITY IS isP2Human(), NOT isCpuDriven(). In TRAINING the dummy is also
    // the sparring partner (owner: "play two controls don't work in training mode"), so
    // P2 is CPU-driven AND legitimately human-controllable at the same time. Asking
    // isCpuDriven() alone called that deliberate behaviour a leak.
    const allowed = seat === 2 ? !!isP2Human() : !p.isCpuDriven();
    for (const code of KEYS) {
      for (const k in keys) keys[k] = false;
      p.x = seat === 1 ? 200 : 400; p.isGrounded = true; p.vy = 0; p.attackAir = false;
      p.state = STATE.IDLE; p.attackT = 0; p.lock = 0; p.recoveryTimer = 0;
      p.stunTimer = 0; p.rollTimer = 0; p.rollRecover = 0; p.sayaLock = 0;
      p.dashTimer = 0; p.chakra = 100; p.stamina = 100; p._lt = p._ht = -1e9;
      const st0 = p.state, vy0 = p.vy, boxes0 = p.kageActs.length;
      let err = null;
      try { fireCombatKey(code); } catch(e) { err = e.message.slice(0,60); }
      const acted = p.state !== st0 || p.vy !== vy0 || p.kageActs.length !== boxes0;
      rows.push({ mode:c.mode, spec:c.spec, seat:c.seat, side:seat, code, allowed, acted, err });
    }
  }
 }
 return rows;
})()`);
ws.close(); chrome.kill('SIGKILL');

console.log('\n  SEAT GATE — a human key must not drive a CPU body\n');
const errs = out.filter(r => r.err);
const leaks = out.filter(r => !r.allowed && r.acted);
const byCase = {};
for (const r of out) {
  const k = `${r.mode}${r.spec ? '+spectate' : ''}${r.mode === 'teams' ? ' seat' + r.seat : ''}`;
  (byCase[k] ||= []).push(r);
}
for (const [k, rs] of Object.entries(byCase)) {
  for (const side of [1, 2]) {
    const mine = rs.filter(r => r.side === side);
    if (!mine.length) continue;
    const allowed = mine[0].allowed, hit = mine.filter(r => r.acted).map(r => r.code);
    const bad = !allowed && hit.length;
    console.log(`  ${bad ? '⛔' : ' ✓'} ${k.padEnd(20)} P${side} ${(allowed ? 'human' : 'CPU').padEnd(6)}` +
                ` responded to ${hit.length}/${mine.length}` + (bad ? `  ⟵ ${hit.join(' ')}` : ''));
  }
}
console.log(`\n  ${out.length} presses · ${leaks.length ? leaks.length + ' LEAKED to a CPU body' : 'no leaks'}` +
            `${errs.length ? ' · ' + errs.length + ' ERRORED (a failure, not a pass)' : ''}`);
process.exit(leaks.length + errs.length ? 1 : 0);
