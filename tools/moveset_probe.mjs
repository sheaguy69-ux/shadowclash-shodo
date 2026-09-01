#!/usr/bin/env node
// Probe EVERY fighter's 30 attack inputs in ONE headless session and dump JSON.
//
//   node tools/moveset_probe.mjs > out.json      # needs :9100 serving THIS tree
//
// Same ruler as tools/movelist.mjs (one real press through executeAttack, drawn family
// sampled off spriteFrameIndex) — this one just does all nine in a single Chrome instead
// of nine, because nine back-to-back launches race each other for the debug port and
// three of them died with "chrome never came up".
import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const port = +(process.env.PORT || 9100), dbg = 9364;
const who = await fetch(`http://127.0.0.1:${port}/whoami`).then(r => r.json()).catch(() => null);
if (!who) { console.error(`no server on :${port} — python3 tools/serve.py 9100 web`); process.exit(1); }
const TREE = path.resolve(who.tree);
const profile = await mkdtemp(path.join(tmpdir(), 'ms-'));
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

const out = await ev(String.raw`(async()=>{
 for(let i=0;i<600;i++){ if(typeof NINJA_ROSTER!=='undefined'&&typeof SPRITES!=='undefined') break; await new Promise(r=>setTimeout(r,50)); }
 const TIERS={Light:'ATTACK_LIGHT',Heavy:'ATTACK_HEAVY',Special:'ATTACK_SPECIAL'};
 const DIRS={neutral:p=>{},fwd:p=>{p.getInputAxis=()=>p.facing;},back:p=>{p.getInputAxis=()=>-p.facing;},
             down:p=>{p.isDownPressed=()=>true;},up:p=>{p.isUpPressed=()=>true;}};
 const all={};
 for(const spec of NINJA_ROSTER){
  const NM=spec.name.toLowerCase();
  let man=null;
  for(let i=0;i<600;i++){ man=SPRITES[NM]; if(man&&man.ready&&man.frames) break; man=null; await new Promise(r=>setTimeout(r,50)); }
  if(!man) continue;
  const F=man.frames;
  const byIdx={}; for(const [k,i] of Object.entries(F)) (byIdx[i]||=[]).push(k);
  const famOf=i=>{ const s=new Set(); for(const k of (byIdx[i]||[])){ const m=k.match(/^([a-z_]+?)\d+$/); s.add(m?m[1]:k); } return [...s]; };
  const rows=[];
  for(const air of [false,true]){
   for(const [tier,st] of Object.entries(TIERS)){
    for(const [d,set] of Object.entries(DIRS)){
      if(typeof smokeFields!=='undefined') smokeFields.length=0;
      const p=new Player(1,150,GROUND_Y-(air?150:48),spec,true);
      p.opponent=new Player(2,240,GROUND_Y-48,spec,false); p.opponent.opponent=p;
      p.facing=1; p.isGrounded=!air; p.attackAir=air; p.vy=air?100:0;
      p.chakra=100; p.stamina=100;
      p.getInputAxis=()=>0; p.isDownPressed=()=>false; p.isUpPressed=()=>false;
      p.state=STATE.IDLE; p.attackT=0; p.lock=0; p.stunTimer=0; p.rollTimer=0; p.rollRecover=0; p.sayaLock=0;
      set(p);
      const b=p.kageActs.length;
      let err=null;
      try{ p.executeAttack(STATE[st]); }catch(e){ err=e.message.slice(0,60); }
      p.isGrounded=!air; p.attackAir=air;
      const fams=[], cells=[];
      for(let s2=0;s2<16;s2++){
        if(p.attackAnim) p.attackAnim.start=animClock*1000-(s2/16)*p.attackAnim.dur*0.99;
        else p.attackT=(s2/16)*0.45;
        let i2; try{ i2=spriteFrameIndex(p,F); }catch(e){ break; }
        if(!cells.includes(i2)) cells.push(i2);
        for(const f of famOf(i2)) if(!fams.includes(f)) fams.push(f);
      }
      rows.push({where:air?'air':'ground', tier, dir:d,
                 box:p.kageActs.length-b, proj:(p.projectiles||[]).length,
                 field:(typeof smokeFields!=='undefined'?smokeFields.length:0), err,
                 dmg:Math.round(p.kageActs.slice(b).reduce((a,k)=>a+(k.dmg||0),0)*10)/10,
                 dur:p.attackAnim?Math.round(p.attackAnim.dur):0,
                 cells,
                 drew:fams.filter(f=>!['idle','stand','run_clean'].includes(f))});
    }
   }
  }
  all[NM]={display:spec.name, rows, cols:man.cols};
 }
 return all;
})()`);
ws.close(); chrome.kill('SIGKILL');
console.log(JSON.stringify({ tree: TREE, sheet_v: who.sheet_v, head: who.head, fighters: out }, null, 1));
