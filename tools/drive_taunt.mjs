#!/usr/bin/env node
// PRESS THE ACTUAL TAUNT KEY, THEN RUN THE ACTUAL SIM.
//
// check_taunt.mjs reads the source and proves the wiring is present. It cannot prove the
// press SURVIVES fireCombatKey's early returns, that updateGame really counts tauntT down,
// or that the cell the engine draws is the taunt row rather than the idle it holds. This
// does all three the only way that is not a guess: fireCombatKey for the press, updateGame
// at a fixed dt for the clock, spriteFrameIndex for the drawing.
//
//   node tools/drive_taunt.mjs          # needs python3 tools/serve.py 9101 web
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
 const DT = 1/60;
 const idxOf = n => NINJA_ROSTER.findIndex(s=>s.name.toLowerCase()===n);

 // A clean neutral P1 of the named fighter, standing, out of the round-intro gate.
 function neutral(name){
   gameMode='versus'; p1Pick=idxOf(name); p2Pick=p1Pick===0?1:0;
   startNewGame();
   roundIntroTimer=0; paused=false; hitstopRemaining=0;
   for(const k in keys) keys[k]=false;
   const p=player1;
   p.x=200; p.y=GROUND_Y-p.height; p.isGrounded=true; p.vx=0; p.vy=0;
   p.state=STATE.IDLE; p.attackT=0; p.recoveryTimer=0; p.stunTimer=0;
   p.rollTimer=0; p.rollRecover=0; p.dashTimer=0; p.tauntT=0; p.sayaLock=0;
   if(player2){ player2.x=700; player2.isGrounded=true; }
   return p;
 }
 const cellsOf = name => {
   const F=SPRITES[name].frames, c=[];
   for(let n=1;F['taunt'+n]!==undefined;n++) c.push(F['taunt'+n]);
   return c;
 };
 const drawn = p => spriteFrameIndex(p, SPRITES[p.spec.name.toLowerCase()].frames);
 const R = {};

 // --- 1. the press reaches it, and the WHOLE row draws, in order --------------
 {
   const p=neutral('tsubasa'), row=cellsOf('tsubasa');
   fireCombatKey('KeyX');
   const started=p.tauntT;
   const seq=[]; let ticks=0;
   while(p.tauntT>0 && ticks<240){ seq.push(drawn(p)); updateGame(DT); ticks++; }
   const after=drawn(p);
   R.press={ row, started:+started.toFixed(3), ticks,
             distinct:[...new Set(seq)], inOrder:JSON.stringify([...new Set(seq)])===JSON.stringify(row),
             endsOnIdle: !row.includes(after), stateHeld:Object.keys(STATE).find(k=>STATE[k]===p.state) };
 }
 // --- 2. it cancels on the first real input, SAME frame -----------------------
 for (const [label, arm] of [['walk', ()=>{keys.p1_right=true;}],
                             ['duck', ()=>{keys.p1_down=true;}],
                             ['guard',()=>{keys.p1_poof=true;}],
                             ['swing',()=>fireCombatKey('KeyF')],
                             ['hit',  ()=>{player1.takeDamage(10, player2);}]]) {
   const p=neutral('tsubasa');
   fireCombatKey('KeyX');
   const armed=p.tauntT>0;
   arm();
   updateGame(DT);                       // ONE frame — the cancel must not need a second
   (R.cancel||=[]).push({ label, armed, tauntT:+p.tauntT.toFixed(4), cancelled:p.tauntT===0 });
   for(const k in keys) keys[k]=false;
 }
 // --- 3. no art, no taunt -----------------------------------------------------
 {
   const noArt = NINJA_ROSTER.map(s=>s.name.toLowerCase()).filter(n=>!cellsOf(n).length);
   const p=neutral(noArt[0]);
   fireCombatKey('KeyX');
   R.noArt={ fighter:noArt[0], others:noArt.length, tauntT:p.tauntT, refused:p.tauntT===0,
             stillDrawsIdle: drawn(p)===spriteFrameIndex(p, SPRITES[noArt[0]].frames) };
 }
 // --- 4. refused when the body is busy ----------------------------------------
 {
   const busy={};
   for (const [label, arm] of [['airborne', p=>{p.isGrounded=false;}],
                               ['stunned',  p=>{p.stunTimer=0.4;}],
                               ['rolling',  p=>{p.rollTimer=0.2;}],
                               ['attacking',p=>fireCombatKey('KeyG')]]) {
     const p=neutral('tsubasa'); arm(p);
     fireCombatKey('KeyX');
     busy[label]=p.tauntT===0;
   }
   R.busy=busy;
 }
 // --- 5. the pad's L3 lands on the same key -----------------------------------
 R.pad={ p1:PAD_KEYS[0].taunt, p2:PAD_KEYS[1].taunt, button10:PAD_BUTTONS[10] };
 // updateGame scales the caller's dt by COMBAT_TEMPO before anything sees it, so the
 // frame count is only meaningful against the same clock ROLL_TIME and DASH_TIME use.
 R.clock={ tempo:COMBAT_TEMPO, dt:DT, taunt:TAUNT_TIME, roll:ROLL_TIME };
 return R;
})()`);
} finally { ws.close(); chrome.kill('SIGKILL'); }

if (out.fatal) { console.error(out.fatal); process.exit(2); }

const fails = [];
const need = (c, m) => { if (!c) fails.push(m); };
const P = out.press;
console.log('  TAUNT — DRIVEN THROUGH THE REAL FUNNEL AND THE REAL SIM\n');
console.log(`  press KeyX   tauntT armed to ${P.started}s, ran ${P.ticks} frames at 1/60`);
console.log(`  row          taunt1..${P.row.length} = cells ${P.row.join(',')}`);
console.log(`  drew         ${P.distinct.join(',')}   ${P.inOrder ? '(every beat, in order)' : '⛔ NOT the row, in order'}`);
console.log(`  after        back to ${P.stateHeld}, drawing outside the taunt row: ${P.endsOnIdle}`);
console.log(`  clock        ${out.clock.taunt}s game time x COMBAT_TEMPO ${out.clock.tempo}`
  + ` = ${(out.clock.taunt / out.clock.tempo).toFixed(3)}s on the wall`
  + ` (${(P.row.length / (out.clock.taunt / out.clock.tempo)).toFixed(0)} beats/sec);`
  + ` the dodge roll is ${out.clock.roll}s on the same clock`);
need(P.inOrder, 'the drawn cells are not the taunt row in order');
const want = Math.ceil(out.clock.taunt / (out.clock.dt * out.clock.tempo));
need(P.ticks === want, `taunt ran ${P.ticks} frames — ${want} expected for ${out.clock.taunt}s of game time at dt ${out.clock.dt.toFixed(5)} x COMBAT_TEMPO ${out.clock.tempo}`);
need(P.endsOnIdle, 'the taunt never lets go of the art');
need(P.stateHeld === 'IDLE', `taunt held STATE.${P.stateHeld}, not IDLE`);

console.log('\n  cancels in ONE frame:');
for (const c of out.cancel) {
  console.log(`    ${c.label.padEnd(6)} armed=${c.armed ? 'Y' : 'n'}  -> tauntT ${c.tauntT}  ${c.cancelled ? 'cancelled' : '⛔ STILL RUNNING'}`);
  need(c.armed, `${c.label}: the taunt never armed, so the cancel proves nothing`);
  need(c.cancelled, `${c.label} did not cancel the taunt in one frame`);
}

console.log(`\n  no art, no taunt: ${out.noArt.fighter} refused = ${out.noArt.refused}`
  + `  (${out.noArt.others} of the roster have no taunt row)`);
need(out.noArt.refused, `${out.noArt.fighter} has no taunt art but entered the taunt anyway`);

console.log('  refused while busy: ' + Object.entries(out.busy).map(([k, v]) => `${k}=${v ? 'Y' : '⛔n'}`).join('  '));
for (const [k, v] of Object.entries(out.busy)) need(v, `taunt started while ${k}`);

console.log(`  pad: L3 (button 10) -> '${out.pad.button10}' -> P1 ${out.pad.p1} / P2 ${out.pad.p2}`);
need(out.pad.button10 === 'taunt' && out.pad.p1 === 'KeyX' && out.pad.p2 === 'KeyN',
  'the pad does not reach the taunt keys');

if (fails.length) {
  console.error(`\n  ⛔ ${fails.length} failure${fails.length > 1 ? 's' : ''}:`);
  for (const f of fails) console.error('    ' + f);
  process.exit(1);
}
console.log('\n  ✓ pressed, drawn, cancelled and refused exactly as specified');
