#!/usr/bin/env node
// MULTI-TAP LIGHT STRINGS, driven live. Real engine, real funnel (fireCombatKey),
// real time — not the mirror check (tools/check_light_string.mjs), which proves the
// logic; this proves the WIRING: taps walk the beats, the window closes, a connect
// cancels early, a whiff doesn't, the last beat never cancel-wraps.
//
//   node tools/drive_light_string.mjs            # defaults to kael
//   node tools/drive_light_string.mjs --name ember
//
// ⛔ ONE SERVER, AND THIS LANE ISN'T ON IT. :9100 serves whichever tree holds the
// live art work; this lane only changed web/index.html. So the driver hits the ONE
// URL and swaps in THIS tree's index.html via CDP request interception — inside a
// throwaway headless profile only. No second server, no rebind under a sibling's
// live session, and the file under test is pinned to this lane by construction.
// Sprites and JSON still come from :9100 (they are logic-neutral here).
import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp, readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const NAME = (process.argv.includes('--name')
  ? process.argv[process.argv.indexOf('--name') + 1] : 'kael').toLowerCase();
const port = 9100, dbg = 9371;
const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const html = await readFile(path.join(root, 'web/index.html'));
const alive = await fetch(`http://127.0.0.1:${port}/`).then(r => r.ok).catch(() => false);
if (!alive) { console.error(`no server on :${port} — python3 tools/serve.py 9100 web`); process.exit(1); }

const profile = await mkdtemp(path.join(tmpdir(), 'ls-'));
spawnSync('pkill', ['-f', `remote-debugging-port=${dbg}`], { stdio: 'ignore' });
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ['--headless=new', '--disable-gpu', '--no-first-run', `--remote-debugging-port=${dbg}`,
   `--user-data-dir=${profile}`, 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let page;
for (let i = 0; i < 100 && !page; i++) {
  try {
    const l = await fetch(`http://127.0.0.1:${dbg}/json/list`).then(r => r.json());
    page = l.find(t => t.type === 'page');
  } catch {}
  if (!page) await sleep(100);
}
if (!page) { console.error('chrome never came up'); process.exit(1); }
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener('open', r, { once: true }));
let id = 1; const pend = new Map();
ws.addEventListener('message', async e => {
  const m = JSON.parse(e.data);
  if (m.id && pend.has(m.id)) {
    const p = pend.get(m.id); pend.delete(m.id);
    m.error ? p.rej(new Error(m.error.message)) : p.res(m.result);
  } else if (m.method === 'Fetch.requestPaused') {
    const { requestId, request } = m.params;
    if (new URL(request.url).pathname === '/' || request.url.endsWith('/index.html'))
      cmd('Fetch.fulfillRequest', { requestId, responseCode: 200,
        responseHeaders: [{ name: 'Content-Type', value: 'text/html' },
                          { name: 'Cache-Control', value: 'no-store' }],
        body: html.toString('base64') });
    else cmd('Fetch.continueRequest', { requestId });
  }
});
const cmd = (method, params = {}) => new Promise((res, rej) => {
  const n = id++; pend.set(n, { res, rej });
  ws.send(JSON.stringify({ id: n, method, params }));
});
const ev = x => cmd('Runtime.evaluate',
  { expression: x, awaitPromise: true, returnByValue: true })
  .then(r => { if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text); return r.result.value; });

await cmd('Fetch.enable', { patterns: [{ urlPattern: '*', requestStage: 'Request' }] });
await cmd('Page.enable');
await cmd('Page.navigate', { url: `http://127.0.0.1:${port}/` });

const out = await ev(String.raw`(async()=>{
 const NM=${JSON.stringify(NAME)};
 const sleep=ms=>new Promise(r=>setTimeout(r,ms));
 for(let i=0;i<400;i++){
   if(typeof NINJA_ROSTER!=='undefined' && typeof startNewGame==='function'
      && typeof fireCombatKey==='function') break;
   await sleep(50);
 }
 const idx = NINJA_ROSTER.findIndex(s=>s.name.toLowerCase()===NM);
 if(idx<0) return {fatal:'not on the roster: '+NM};
 gameMode='training'; p1Pick=idx; p2Pick=idx===0?1:0;
 try{ startNewGame(); }catch(e){ return {fatal:'boot: '+e.message.slice(0,90)}; }
 // ⛔ BIND AFTER THE BOOT SETTLES. startNewGame rebuilds player1 during the intro,
 // so a reference grabbed here-and-now can be an ORPHAN: real taps act on the new
 // player1 while the instrumented old one reads zeros forever. Wait until the
 // object identity holds still and the match is live, THEN bind and wrap.
 let stable=0, last=null;
 for(let i=0;i<600 && stable<20;i++){
   roundIntroTimer=0; paused=false; hitstopRemaining=0;
   if(typeof matchActive!=='undefined' && matchActive && player1 && player2
      && player1===last) stable++; else stable=0;
   last=player1; await sleep(16);
 }
 if(stable<20) return {fatal:'boot never settled: matchActive='+(typeof matchActive!=='undefined'&&matchActive)};
 const p=player1, foe=player2;
 const pow=p.spec.stats.power/6, rate=p.spec.stats.reach/6;
 // measure at the SOURCE: kageActs is a rolling tape (timer-sampled, expiring) and
 // reads empty at tap speed. A test-side wrap of spawnHitbox records every box the
 // instant it exists, engine untouched.
 const rec=[];
 const orig=p.spawnHitbox.bind(p);
 p.spawnHitbox=(w,h,dmg,dur,push,opts)=>{ rec.push({w,h,dmg,push,t:+animClock.toFixed(3),st:Object.keys(STATE).find(k=>STATE[k]===p.state),cpu:p.isCpuDriven&&p.isCpuDriven()}); return orig(w,h,dmg,dur,push,opts); };

 // ⛔ HAND-STEPPED FRAMES. Wall-clock pacing flaked whenever the box was loaded
 // (three headless Chromes and the string window is missed by luck, not logic).
 // gameLoop's dt clamp explicitly supports a manually-driven frame, so the rAF
 // chain is cut and the clock advances EXACTLY 1/60s per step — deterministic on
 // any machine, any load.
 requestAnimationFrame = () => 0;   // the scheduled frame fires once, never re-arms
 await sleep(60);
 let T = lastTime;
 const step=(n)=>{ for(let i=0;i<n;i++){ T+=1000/60; gameLoop(T); } };
 const stepUntil=(f,max=120)=>{ for(let i=0;i<max;i++){ if(f()) return true; step(1); } return f(); };
 const settled=()=>p.recoveryTimer<=0 && p.state===STATE.IDLE;
 const reset=(foeX)=>{ for(const k in keys) keys[k]=false;
   roundIntroTimer=0; paused=false; hitstopRemaining=0;
   p.x=300; p.facing=1; p.isGrounded=true; p.vy=0; p.vx=0;
   p.state=STATE.IDLE; p.recoveryTimer=0; p.stunTimer=0; p.rollTimer=0;
   p.rollRecover=0; p.dashTimer=0; p.chainComboTier=0; p.attackHasConnected=false;
   p.stringStep=0; p.stringT=0; p.bufferedAttack=null; p.stamina=100; p.chakra=100;
   foe.x=foeX; foe.isGrounded=true; foe.vx=0; foe.vy=0; foe.state=STATE.IDLE;
   foe.stunTimer=0; foe.flooredT=0; foe.hp=foe.maxHp; p.hp=p.maxHp;   // a KO'd dummy resets the ROUND and orphans p
   hitstopRemaining=0; rec.length=0; step(2); };
 const park=()=>{ p.x=300; p.vx=0; foe.x=adj; foe.vx=0; foe.vy=0; foe.flooredT=0; foe.hp=foe.maxHp;
   // keep the dummy in HITSTUN — that is the true mid-string state, and a foe who
   // can block turns an armed beat into a blade BIND instead of a clean connect
   foe.stunTimer=0.5;
   // point-blank armed lights can trip the BLADE LOCK clash — a locked foe eats
   // every attack press as struggle mash, which is its own feature, not this one
   p.lock=null; foe.lock=null;
   if(p.state===STATE.BLADE_LOCK)p.state=STATE.IDLE;
   if(foe.state===STATE.BLADE_LOCK)foe.state=STATE.IDLE; };
 const adj = 300 + 35 + 20*rate;   // point-blank scaled to the fighter's reach — Ember's 20px claw whiffs at Kael's spacing
 const boxes=()=>rec.slice();
 const R={};

 // canary: a tap must fire at all before phases mean anything
 reset(1100); fireCombatKey('KeyF'); step(8);
 if(!rec.length) return {fatal:'taps never fire — the room is not playable'};
 if(player1!==p) return {fatal:'player rebuilt after bind — rerun'};

 // T1 — a single tap is the shipped light: dmg 8*pow, w 40*rate, push 10*power
 reset(1100); fireCombatKey('KeyF'); step(8);
 R.single={ boxes:boxes(), step:p.stringStep,
            wantDmg:8*pow, wantW:40*rate, wantPush:10*p.spec.stats.power };

 // T2 — whiff-rhythm taps as recovery ends (inside the 33-frame window) walk the
 // beats and wrap on the 4th
 reset(1100);
 const steps=[], fired=[];
 for(let i=0;i<4;i++){ fireCombatKey('KeyF'); step(2);
   steps.push(p.stringStep); fired.push(rec.length);
   stepUntil(settled); }
 R.walk={ steps, fired, boxes:boxes() };

 // T3 — a tap after the window expires restarts at beat one
 reset(1100); fireCombatKey('KeyF'); stepUntil(settled); step(40);
 fireCombatKey('KeyF'); step(8);
 R.expire={ step:p.stringStep, n:rec.length };

 // T5 — WHIFF double-tap: the 2nd press buffers, fires only after full recovery
 reset(1100); fireCombatKey('KeyF'); step(3); fireCombatKey('KeyF');
 stepUntil(()=>rec.length>=2, 90); step(2);
 const wb=boxes();
 R.whiff={ n:wb.length, gap: wb.length>=2 ? wb[1].t-wb[0].t : null, early:p.stringStep };

 // T4 — ON-HIT cancel: connect beat one, tap in the confirm window, beat two
 // spawns EARLIER than the whiff gap allows
 reset(adj);
 fireCombatKey('KeyF');
 const conn=stepUntil(()=>p.attackHasConnected, 30);
 fireCombatKey('KeyF'); step(8);
 const hb=boxes();
 R.hit={ connected:conn, n:hb.length, step:p.stringStep,
         gap: hb.length>=2 ? hb[1].t-hb[0].t : null };

 // T6 — the LAST beat never cancel-wraps: reach beat three (dummy re-parked each
 // beat — pushback shoves it out of a short fighter's 20px light), land it, tap
 // inside the confirm window, nothing new comes out
 reset(adj);
 fireCombatKey('KeyF'); stepUntil(settled); park();
 fireCombatKey('KeyF'); stepUntil(settled); park();
 fireCombatKey('KeyF');
 const c3=stepUntil(()=>p.attackHasConnected, 30); park();
 const nAt3=rec.length, stepAt3=p.stringStep;
 fireCombatKey('KeyF'); step(8);
 // the invariant is TIMING, not the connect flag: whether beat three connected
 // (cancel window live) or whiffed (dummy AI is nondeterministic), no box may
 // appear inside the confirm window — a 4th box is legal only at full rhythm
 const lgap = rec.length>nAt3 && nAt3>0 ? rec[rec.length-1].t-rec[nAt3-1].t : null;
 R.last={ c3, stepAt3, nAt3, nAfter:rec.length, lgap, step:p.stringStep };

 return { R, who:p.spec.name };
})()`);
ws.close(); chrome.kill('SIGKILL');
if (out.fatal) { console.error('FATAL: ' + out.fatal); process.exit(2); }

const { R, who } = out;
const near = (a, b) => Math.abs(a - b) < 1e-6;
let bad = 0;
const check = (ok, msg, detail) => {
  console.log(`${ok ? ' ok ' : 'FAIL'} ${msg}${detail ? '   ' + detail : ''}`);
  if (!ok) bad++;
};
console.log(`— ${who}, live on :9100 (document from this lane) —`);
const s0 = R.single.boxes[0] || {};
check(R.single.boxes.length === 1 && near(s0.dmg, R.single.wantDmg)
      && near(s0.w, R.single.wantW) && near(s0.push, R.single.wantPush) && R.single.step === 0,
  'single tap IS the shipped light',
  `dmg ${s0.dmg}=${R.single.wantDmg} w ${s0.w}=${R.single.wantW} push ${s0.push}=${R.single.wantPush}`);
check(JSON.stringify(R.walk.steps) === '[0,1,2,0]' && JSON.stringify(R.walk.fired) === '[1,2,3,4]',
  'taps in the window walk beats 1-2-3 and wrap on the 4th',
  `steps ${JSON.stringify(R.walk.steps)}`);
const wd = R.walk.boxes.map(b => +(b.dmg / R.single.wantDmg).toFixed(3));
check(JSON.stringify(wd) === '[1,1.15,1.5,1]',
  'beat damage factors are 1 / 1.15 / 1.5 / (wrap) 1', `got ${JSON.stringify(wd)}`);
check(R.expire.step === 0 && R.expire.n === 2, 'window expiry restarts at beat one');
check(R.whiff.n === 2 && R.whiff.early === 1,
  'whiffed double-tap: 2nd press waits out recovery (no free cancel)',
  `gap ${R.whiff.gap?.toFixed(3)}s`);
check(R.hit.connected && R.hit.n === 2 && R.hit.step === 1
      && R.hit.gap !== null && R.whiff.gap !== null && R.hit.gap < R.whiff.gap - 0.05,
  'a CONNECTED light cancels into beat two early',
  `hit gap ${R.hit.gap?.toFixed(3)}s vs whiff gap ${R.whiff.gap?.toFixed(3)}s`);
check(R.last.stepAt3 === 2 && R.last.nAt3 === 3
      && (R.last.nAfter === 3 || (R.last.lgap !== null && R.whiff.gap !== null
                                  && R.last.lgap >= R.whiff.gap - 0.05)),
  'the last beat never cancel-wraps inside the confirm window',
  `connected ${R.last.c3}, boxes ${R.last.nAt3}->${R.last.nAfter}` +
  (R.last.lgap !== null ? `, tail gap ${R.last.lgap.toFixed(3)}s vs whiff ${R.whiff.gap?.toFixed(3)}s` : ''));
if (bad) console.log('RAW ' + JSON.stringify(R));
console.log(bad === 0 ? `PASS — the string is live end to end (${who})` : `FAIL — ${bad} broken`);
process.exit(bad === 0 ? 0 : 1);
