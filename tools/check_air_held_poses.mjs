#!/usr/bin/env node
// The two HELD airborne cells must come off the fighter's own AIR row.
//
//   PORT=9101 node tools/check_air_held_poses.mjs
//
// The air up-poke and the meteor's hang/plunge do not play a row — each holds ONE cell —
// so they never went through the 707 air sweep, and their `??` chains ended on light3,
// upatk3, fall2 or ajump4. Rendered through the runtime keyer those are PLANTED stances
// on eight of the nine sheets, i.e. a fighter standing on the floor while he is in the
// sky. This asserts the held cell is a member of airAttackCells() (aneu / bair / kxcut),
// which 707 established are the genuinely tucked airborne bodies.
//
// Oni is the one exemption: he has a drawn dive row and keeps it.
import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const port = +(process.env.PORT || 9101), dbg = 9366;
const who = await fetch(`http://127.0.0.1:${port}/whoami`).then(r => r.json()).catch(() => null);
if (!who) { console.error(`no server on :${port} — python3 tools/serve.py ${port} web`); process.exit(1); }
if (path.resolve(who.tree) !== path.resolve(process.cwd())) {
  console.error(`:${port} is serving ${who.tree}, not ${process.cwd()}`); process.exit(1);
}
const profile = await mkdtemp(path.join(tmpdir(), 'ahp-'));
spawnSync('pkill', ['-f', `remote-debugging-port=${dbg}`], { stdio: 'ignore' });
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ['--headless=new', '--disable-gpu', '--no-first-run', `--remote-debugging-port=${dbg}`,
   `--user-data-dir=${profile}`, `http://127.0.0.1:${port}/`], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let page;
for (let i = 0; i < 300 && !page; i++) {
  try {
    const l = await fetch(`http://127.0.0.1:${dbg}/json/list`).then(r => r.json());
    page = l.find(t => t.type === 'page' && t.url.includes(String(port)));
  } catch {}
  if (!page) await sleep(200);
}
if (!page) { console.error('chrome never came up'); chrome.kill('SIGKILL'); process.exit(1); }
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

let rows;
try {
rows = await ev(String.raw`(async()=>{
 for(let i=0;i<600;i++){ if(typeof NINJA_ROSTER!=='undefined'&&typeof SPRITES!=='undefined') break; await new Promise(r=>setTimeout(r,50)); }
 const out=[];
 for(const spec of NINJA_ROSTER){
  const NM=spec.name.toLowerCase();
  let man=null;
  for(let i=0;i<600;i++){ man=SPRITES[NM]; if(man&&man.ready&&man.frames) break; man=null; await new Promise(r=>setTimeout(r,50)); }
  if(!man) continue;
  const F=man.frames;
  const air=airAttackCells(F)||[];
  const dive=[]; for(let i=1;F['dive'+i]!==undefined;i++) dive.push(F['dive'+i]);
  // Driven, not hand-set: spriteFrameIndex returns xidle for a Player that is not
  // actually mid-move, so a synthetic slamPhase on an IDLE body proves nothing.
  const mk=(up,down)=>{ const p=new Player(1,150,GROUND_Y-160,spec,true);
    p.opponent=new Player(2,240,GROUND_Y-48,spec,false); p.opponent.opponent=p;
    p.facing=1; p.isGrounded=false; p.attackAir=true; p.vy=100; p.chakra=100; p.stamina=100;
    p.getInputAxis=()=>0; p.isDownPressed=()=>!!down; p.isUpPressed=()=>!!up;
    p.state=STATE.IDLE; p.attackT=0; p.lock=0; p.stunTimer=0;
    p.rollTimer=0; p.rollRecover=0; p.sayaLock=0; return p; };
  // 1) the air up-poke — a real Up+Light in the air
  let p=mk(true,false);
  try{ p.executeAttack(STATE.ATTACK_LIGHT); }catch(e){ out.push({name:spec.name,err:String(e).slice(0,90)}); continue; }
  p.isGrounded=false; p.attackAir=true;
  const poke=spriteFrameIndex(p,F);
  // 2) the meteor — a real air Down+Heavy, which is what calls startSlam
  //    (startSlam writes attackAnim.dur, so it cannot be poked from the outside)
  p=mk(false,true);
  try{ p.executeAttack(STATE.ATTACK_HEAVY); }catch(e){ out.push({name:spec.name,err:String(e).slice(0,90)}); continue; }
  p.isGrounded=false; p.attackAir=true;
  const hang=p.slamPhase===1?spriteFrameIndex(p,F):-1;
  p.slamPhase=2; p.slamTimer=0;
  const plunge=spriteFrameIndex(p,F);
  out.push({name:spec.name, air, dive, poke, hang, plunge});
 }
 return out;
})()`);
} finally { try { ws.close(); } catch {} chrome.kill('SIGKILL'); }

let bad = 0;
for (const r of rows) {
  if (r.err) { bad++; console.log(`  FAIL ${r.name.padEnd(12)} threw: ${r.err}`); continue; }
  const ok = c => r.air.includes(c) || r.dive.includes(c);
  for (const [label, cell] of [['air up-poke', r.poke], ['meteor hang', r.hang], ['meteor plunge', r.plunge]]) {
    const beat = r.air.indexOf(cell);
    const src = r.dive.includes(cell) ? `dive${r.dive.indexOf(cell) + 1}`
              : beat >= 0 ? `air beat ${beat + 1}` : 'NOT AN AIR CELL';
    if (!ok(cell)) bad++;
    console.log(`  ${ok(cell) ? 'ok  ' : 'FAIL'} ${r.name.padEnd(12)} ${label.padEnd(14)} #${String(cell).padStart(3)}  ${src}`);
  }
}
console.log(bad === 0
  ? `\n  air held poses: ${rows.length * 3} checked, every one off the fighter's own air or dive row`
  : `\n  ${bad} held pose(s) are NOT airborne art`);
process.exit(bad === 0 ? 0 : 1);
