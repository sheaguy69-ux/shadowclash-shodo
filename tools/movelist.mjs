#!/usr/bin/env node
// Print a fighter's REAL move list — every input, what it draws, what it does.
//
//   node tools/movelist.mjs            # oni
//   node tools/movelist.mjs --name mizu
//
// Not read off the sheet and not off the docs: every row here is one real press through
// executeAttack on a real Player, with the drawn family sampled from spriteFrameIndex and
// the hitbox counted off kageActs. The reason it works that way is that this codebase has
// repeatedly had art and action disagree — a staff rush that DREW while a mist vanish RAN,
// a claw finisher wired to a trigger that could not fire, six separate branch-order bugs.
// A move list assembled from key names would have reported every one of those as fine.
//
// EMPTY means the input produced no hitbox, no field, no projectile and no state change:
// a genuinely free slot. It is the list to work from when adding a move.
import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const NAME = (process.argv.includes('--name')
  ? process.argv[process.argv.indexOf('--name') + 1] : 'oni').toLowerCase();
const port = 9101, dbg = 9364;
const profile = await mkdtemp(path.join(tmpdir(), 'ml-'));
const who = await fetch(`http://127.0.0.1:${port}/whoami`).then(r => r.json()).catch(() => null);
if (!who) { console.error(`no server on :${port} — python3 tools/serve.py 9101 web`); process.exit(1); }
if (path.resolve(who.tree) !== path.resolve(process.cwd())) {
  console.error(`:9101 is serving ${who.tree}\nrebind: kill ${who.pid} && python3 tools/serve.py 9101 web`);
  process.exit(1);
}
spawnSync('pkill', ['-f', `remote-debugging-port=${dbg}`], { stdio: 'ignore' });
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

const out = await ev(String.raw`(async()=>{
 const NM=${JSON.stringify(NAME)};
 for(let i=0;i<300;i++){ if(typeof NINJA_ROSTER!=='undefined'&&typeof SPRITES!=='undefined'&&SPRITES[NM]&&SPRITES[NM].ready) break; await new Promise(r=>setTimeout(r,50)); }
 const spec=NINJA_ROSTER.find(s=>s.name.toLowerCase()===NM);
 const man=SPRITES[NM], F=man.frames;
 const byIdx={}; for(const [k,i] of Object.entries(F)) (byIdx[i]||=[]).push(k);
 const famOf=i=>{ const s=new Set(); for(const k of (byIdx[i]||[])){ const m=k.match(/^([a-z_]+?)\d+$/); s.add(m?m[1]:k); } return [...s]; };

 const TIERS={Light:'ATTACK_LIGHT',Heavy:'ATTACK_HEAVY',Special:'ATTACK_SPECIAL'};
 const DIRS={neutral:p=>{},fwd:p=>{p.getInputAxis=()=>p.facing;},back:p=>{p.getInputAxis=()=>-p.facing;},
             down:p=>{p.isDownPressed=()=>true;},up:p=>{p.isUpPressed=()=>true;}};
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
     try{ p.executeAttack(STATE[st]); }catch(e){ err=e.message.slice(0,50); }
     p.isGrounded=!air; p.attackAir=air;
     const fams=[];
     for(let s2=0;s2<16;s2++){
       if(p.attackAnim) p.attackAnim.start=animClock*1000-(s2/16)*p.attackAnim.dur*0.99;
       else p.attackT=(s2/16)*0.45;
       let i2; try{ i2=spriteFrameIndex(p,F); }catch(e){ break; }
       for(const f of famOf(i2)) if(!fams.includes(f)) fams.push(f);
     }
     const box=p.kageActs.length-b;
     const proj=(p.projectiles||[]).length;
     const field=(typeof smokeFields!=='undefined'?smokeFields.length:0);
     const dmg=p.kageActs.slice(b).reduce((a,k)=>a+(k.dmg||0),0);
     rows.push({where:air?'air':'ground', tier, dir:d, box, proj, field, err,
                dmg:Math.round(dmg*10)/10,
                drew:fams.filter(f=>!['idle','stand','run_clean'].includes(f)).join(',')||'-'});
   }
  }
 }
 // which packed families nothing above ever produced
 const seen=new Set(rows.flatMap(r=>r.drew.split(',')));
 const allFam=new Set();
 for(const k of Object.keys(F)){ const m=k.match(/^([a-z_]+?)\d+$/); allFam.add(m?m[1]:k); }
 const unused=[...allFam].filter(f=>!seen.has(f)).sort();
 return {rows, unused, cols:man.cols, name:spec.name, power:spec.stats.power};
})()`);
ws.close(); chrome.kill('SIGKILL');

console.log(`\n  ${out.name.toUpperCase()} — real move list, ${out.cols} cells, power ${out.power}\n`);
let where = '';
for (const r of out.rows) {
  if (r.where !== where) { where = r.where; console.log(`  ── ${where.toUpperCase()} ──`); }
  const does = [r.box ? `hit ${r.dmg}` : '', r.proj ? `${r.proj} proj` : '', r.field ? 'field' : '']
    .filter(Boolean).join(' + ') || 'EMPTY';
  console.log(`  ${(r.dir + ' + ' + r.tier).padEnd(18)} ${does.padEnd(14)} ${r.drew}` + (r.err ? `  ⛔ ${r.err}` : ''));
}
const empties = out.rows.filter(r => !r.box && !r.proj && !r.field);
console.log(`\n  FREE SLOTS (${empties.length}): ` + (empties.map(r => `${r.where} ${r.dir}+${r.tier}`).join(', ') || 'none'));
console.log(`  PACKED BUT NEVER DRAWN BY ANY INPUT (${out.unused.length}): ${out.unused.join(', ')}`);
