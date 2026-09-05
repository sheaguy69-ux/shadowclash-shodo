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
 dismissTitle();
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
   { mode:'brawl',    spec:false, seat:2 },
   { mode:'teams',    spec:false, seat:0 },
 ];
 const rows = [];
 for (const c of CASES) {
  gameMode = c.mode; spectate = c.spec;
  if (typeof teamsSeat !== 'undefined') teamsSeat = c.seat;
  p1Pick = 0; p2Pick = 1;
  try { startNewGame(); } catch(e) { rows.push({...c, key:'-', err:e.message.slice(0,70)}); continue; }
  roundIntroTimer = 0; paused = false; hitstopRemaining = 0;
  for (const [seat, KEYS] of [[1, P1KEYS], [2, P2KEYS]]) {
    let p = seat === 1 ? player1 : player2;
    if (!p) continue;
    // ⛔ THE AUTHORITY IS isP2Human(), NOT isCpuDriven(). In TRAINING the dummy is also
    // the sparring partner (owner: "play two controls don't work in training mode"), so
    // P2 is CPU-driven AND legitimately human-controllable at the same time. Asking
    // isCpuDriven() alone called that deliberate behaviour a leak.
    const allowed = seat === 2 ? !!isP2Human() : !(c.spec || c.mode === 'watch' || (['teams','brawl'].includes(c.mode) && c.seat === 2));
    for (const code of KEYS) {
      startNewGame(); roundIntroTimer = 0; paused = false; hitstopRemaining = 0;
      p = seat === 1 ? player1 : player2;
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
 // Real event listeners and alternate controls bypass fireCombatKey for movement.
 // Expected ownership comes from the selected mode, not the helper under test.
 for (const c of CASES) {
  const allowed = !(c.spec || c.mode === 'watch' || (['teams','brawl'].includes(c.mode) && c.seat === 2));
  for (const source of ['keyboard dash', 'touch dash', 'mouse jump', 'hand jump', 'mouse steering', 'hand steering']) {
   gameMode = c.mode; spectate = c.spec; teamsSeat = c.seat;
   startNewGame(); roundIntroTimer = 0; paused = false; hitstopRemaining = 0;
   cutscene = null;
   for (const id of ['title-screen','character-selection','game-over-screen','pause-screen'])
    document.getElementById(id).classList.add('hidden');
   for (const k in keys) keys[k] = false;
   physKeys.clear();
   const p = player1;
   p.x = 200; p.y = GROUND_Y - p.height; p.isGrounded = true;
   p.vy = 0; p.state = STATE.IDLE; p.stamina = 100;
   p._tapT = 0; p._tapDir = 0;
   let err = null;
   try {
    if (source === 'keyboard dash') {
     for (let n=0;n<2;n++) {
      window.dispatchEvent(new KeyboardEvent('keydown', {code:'KeyD'}));
      window.dispatchEvent(new KeyboardEvent('keyup', {code:'KeyD'}));
     }
    } else if (source === 'touch dash') {
     document.getElementById('touch-controls').classList.remove('hidden');
     const pad = document.getElementById('pad-p1');
     pad.scrollIntoView({block:'center'});
     const r = pad.querySelector('[data-dir="right"]').getBoundingClientRect();
     const touch = {identifier:1, clientX:r.x+r.width/2, clientY:r.y+r.height/2};
     if (document.elementFromPoint(touch.clientX,touch.clientY)?.closest('[data-dir]')?.dataset.dir !== 'right')
      throw new Error('touch setup: right button not exposed');
     for (let n=0;n<2;n++) {
      for (const type of ['touchstart','touchend']) {
       const event = new Event(type, {bubbles:true,cancelable:true});
       Object.defineProperty(event,'changedTouches',{value:[touch]});
       pad.dispatchEvent(event);
      }
     }
    } else if (source.endsWith('steering')) {
     keys.KeyD = true; // the CPU's own rightward input must survive a stale pointer mode
     mouseMode = source === 'mouse steering'; handMode = !mouseMode;
     mouseAxis = handAxis = -1;
    } else if (source === 'mouse jump') {
     mouseMode = true; mouseWasAbove = false; mouseCX = 500; mouseCY = p.y-100;
     mouseControl();
    } else {
     handWasHigh = false;
     const lm = Array.from({length:21},()=>({x:0.5,y:0.2,z:0}));
     onHandResults({multiHandLandmarks:[lm]});
    }
   } catch(e) { err=e.message; }
   const acted = source.endsWith('steering') ? p.getInputAxis() === -1 : p.dashTimer > 0 || !p.isGrounded;
   if (!allowed && source.endsWith('steering') && p.getInputAxis() !== 1) err = 'pointer mode suppressed CPU steering';
   if (allowed && !acted && !err) err = 'human movement stopped working';
   rows.push({mode:c.mode,spec:c.spec,seat:c.seat,side:1,code:source,allowed,acted,err});
   mouseMode = handMode = false; mouseWasAbove = handWasHigh = false;
   handTargetX = null;
  }
  gameMode=c.mode; spectate=c.spec; teamsSeat=c.seat; startNewGame();
  const p2Allowed = !c.spec && (['2p','training'].includes(c.mode) || (['teams','brawl'].includes(c.mode) && c.seat === 0));
  keys.p2_poof=false;
  const guard=document.getElementById('btn-t-p2-poof');
  guard.dispatchEvent(new Event('touchstart',{bubbles:true,cancelable:true}));
  const held=!!keys.p2_poof;
  guard.dispatchEvent(new Event('touchend',{bubbles:true,cancelable:true}));
  rows.push({mode:c.mode,spec:c.spec,seat:c.seat,side:2,code:'touch guard',allowed:p2Allowed,acted:held,
    err:p2Allowed && !held ? 'human P2 touch guard stopped working' : null});
 }
 // Losing focus must release the physical registry too, otherwise the watch-mode
 // cleanup treats later CPU key residue as a real held human key.
 gameMode='versus'; spectate=false; startNewGame(); roundIntroTimer=0;
 window.dispatchEvent(new KeyboardEvent('keydown',{code:'KeyD'}));
 window.dispatchEvent(new Event('blur'));
 rows.push({mode:'versus',spec:false,seat:0,side:1,code:'blur release',allowed:true,acted:false,
   err: keys.KeyD || physKeys.has('KeyD') ? 'focus loss left KeyD registered as held' : null});
 return rows;
})()`);
ws.close(); chrome.kill('SIGKILL');

console.log('\n  SEAT GATE — a human key must not drive a CPU body\n');
const errs = out.filter(r => r.err);
for (const r of errs) console.error(r.mode, r.code, r.err);
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
