#!/usr/bin/env node
// KAEL CEREMONY: PRESS THE REAL KEY / RUN THE REAL ROUND TIMER, AND READ WHAT IS DRAWN.
//
// check_taunt.mjs reads the source and proves the wiring is present. It cannot prove the
// press SURVIVES fireCombatKey's early returns, that updateGame really counts tauntT down,
// or that the cell the engine draws is the taunt row rather than the idle it holds. This
// does all three the only way that is not a guess: fireCombatKey for the press, updateGame
// at a fixed dt for the clock, spriteFrameIndex for the drawing.
//
//   node tools/drive_kael_ceremony.mjs          # needs python3 tools/serve.py 9101 web
import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const port = +(process.env.PORT || 9101), dbg = 9369;
const profile = await mkdtemp(path.join(tmpdir(), 'tt-'));
const who = await fetch(`http://127.0.0.1:${port}/whoami`).then(r => r.json()).catch(() => null);
if (!who) { console.error(`no server on :${port} — python3 tools/serve.py ${port} web`); process.exit(1); }
if (path.resolve(who.tree) !== path.resolve(process.cwd())) {
  console.error(`:${port} is serving ${who.tree}; run against this tree's server`); process.exit(1);
}
spawnSync('pkill', ['-f', `remote-debugging-port=${dbg}`], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
for (let i = 0; i < 60; i++) {
  const alive = await fetch(`http://127.0.0.1:${dbg}/json/version`).then(() => true).catch(() => false);
  if (!alive) break;
  await sleep(100);
}
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ['--headless=new', '--disable-gpu', '--no-first-run', `--remote-debugging-port=${dbg}`,
   `--user-data-dir=${profile}`, `http://127.0.0.1:${port}/`], { stdio: 'ignore' });
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
}).then(r => {
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text);
  return r.result.value;
});

let out;
try {
  out = await ev(String.raw`(async()=>{
 for(let i=0;i<400;i++){
   if(typeof NINJA_ROSTER!=='undefined' && typeof startNewGame==='function'
      && typeof fireCombatKey==='function' && typeof updateGame==='function'
      && typeof SPRITES!=='undefined'
      && NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)) break;
   await new Promise(r=>setTimeout(r,50));
 }
 if(typeof updateGame!=='function') return {fatal:'page never booted'};
 const DT=1/60, F=()=>SPRITES.kael.frames;
 const idxOf = n => NINJA_ROSTER.findIndex(s=>s.name.toLowerCase()===n);
 const row = n => { const f=F(), c=[]; for(let i=1;f[n+i]!==undefined;i++) c.push(f[n+i]); return c; };
 const drawn = p => spriteFrameIndex(p, SPRITES[p.spec.name.toLowerCase()].frames);
 function neutral(){
   gameMode='versus'; p1Pick=idxOf('kael'); p2Pick=p1Pick===0?1:0;
   startNewGame();
   roundIntroTimer=0; paused=false; hitstopRemaining=0;
   for(const k in keys) keys[k]=false;
   const p=player1;
   p.x=200; p.y=GROUND_Y-p.height; p.isGrounded=true; p.vx=0; p.vy=0;
   p.state=STATE.IDLE; p.attackT=0; p.recoveryTimer=0; p.stunTimer=0;
   p.rollTimer=0; p.rollRecover=0; p.dashTimer=0; p.tauntT=0; p.ceremony=null;
   if(player2){ player2.x=700; player2.isGrounded=true; }
   return p;
 }
 const R={ rows:{ taunt:row('taunt'), intro:row('intro'), win:row('win'), ko:row('ko') } };

 // 1. TAUNT — the real key, the real clock, every beat once, back to idle
 { const p=neutral(), r=row('taunt'); fireCombatKey('KeyX');
   const seq=[]; let t=0;
   while(p.tauntT>0 && t<240){ seq.push(drawn(p)); updateGame(DT); t++; }
   const d=[...new Set(seq)];
   R.taunt={ ticks:t, distinct:d, inOrder:JSON.stringify(d)===JSON.stringify(r),
             everyBeat:d.length===r.length, endsOffRow:!r.includes(drawn(p)) }; }

 // 2. TAUNT CANCELS on the first real input, same frame
 { R.tauntCancel=[];
   for(const [l,arm] of [['walk',()=>{keys.p1_right=true;}],['duck',()=>{keys.p1_down=true;}],
                         ['guard',()=>{keys.p1_poof=true;}],['swing',()=>fireCombatKey('KeyF')]]){
     const p=neutral(); fireCombatKey('KeyX'); const armed=p.tauntT>0; arm(); updateGame(DT);
     R.tauntCancel.push({l,armed,cancelled:p.tauntT===0}); for(const k in keys) keys[k]=false; } }

 // 3. INTRO — driven off the REAL round timer, not a poke
 { const p=neutral(), r=row('intro'); roundIntroTimer=1.5;
   const seq=[]; let t=0;
   while(roundIntroTimer>0 && t<400){ seq.push(drawn(p)); roundIntroTimer-=DT; updateGame(DT); t++; }
   const d=[...new Set(seq)];
   R.intro={ ticks:t, distinct:d, inOrder:JSON.stringify(d)===JSON.stringify(r),
             everyBeat:d.length===r.length, holdsLast:seq[seq.length-1]===r[r.length-1] };
   roundIntroTimer=0; }

 // 4. WIN — through beginCeremony, the same call endRound makes
 { const p=neutral(), r=row('win'); beginCeremony(p.isP1?0:1);
   const seq=[]; for(let t=0;t<90;t++){ seq.push(drawn(p)); updateGame(DT); }
   const d=[...new Set(seq)];
   R.win={ pose:p.ceremony&&p.ceremony.row, distinct:d, inOrder:JSON.stringify(d)===JSON.stringify(r),
           everyBeat:d.length===r.length, holdsLast:seq[seq.length-1]===r[r.length-1] }; }

 // 5. KO — earned by hp<=0, and REFUSED airborne (the 707 defect)
 { const p=neutral(), r=row('ko'); p.hp=0; beginCeremony(p.isP1?1:0);
   const seq=[]; for(let t=0;t<90;t++){ seq.push(drawn(p)); updateGame(DT); }
   const d=[...new Set(seq)];
   R.ko={ pose:p.ceremony&&p.ceremony.row, distinct:d, inOrder:JSON.stringify(d)===JSON.stringify(r),
          everyBeat:d.length===r.length, holdsLast:seq[seq.length-1]===r[r.length-1] };
   const q=neutral(); q.hp=0; beginCeremony(q.isP1?1:0); q.isGrounded=false; q.vy=-200;
   R.koAirborne={ drew:drawn(q), onKoRow:r.includes(drawn(q)) }; }

 // 6. A DRAW salutes nobody
 { const p=neutral(); beginCeremony(-1);
   R.draw={ ceremony:p.ceremony, drewWin:row('win').includes(drawn(p)) }; }
 return R;
})()`);
} catch (e) { out = { fatal: String(e) }; }
ws.close(); chrome.kill();
console.log(JSON.stringify(out, null, 1));
