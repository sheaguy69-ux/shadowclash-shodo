#!/usr/bin/env node
// Every fighter's ground SPECIAL, every direction: does the input do anything DISTINCT?
//
// This exists because the answer was NO for thirteen of forty-five and nobody knew. Oni's
// entire Special layer — neutral, fwd, back, down, up — was animation with nothing behind
// it, which quietly made his whole razor-wire grab game unreachable: the bind opens when a
// Special CONNECTS, and none of his could connect. It passed every check that came before
// because every one of them opened the bind BY HAND.
//
// ⛔ AND IT DOES NOT MEASURE HITBOXES, because that was the wrong question and it produced
// two confident false alarms. Counting boxes reported Mizu and Tsubasa as having their
// ENTIRE Special layer dead. They do not: Mizu's Special is the MIST VANISH (it spawns a
// field and takes her alpha to 0) and Tsubasa's is a PARRY STANCE. Neither is supposed to
// hit anything. A parry that spawned a hitbox would be the bug.
//
// So each press is FINGERPRINTED by what it actually did — resulting state, boxes, fields,
// projectiles, alpha, moveArt — and two things are reported:
//   DOES NOTHING   every one of those is unchanged: the input is genuinely inert.
//   ALL IDENTICAL  every direction produced the SAME fingerprint, which means the neutral
//                  Special is eating the directional inputs. That is a real bug when the
//                  fighter has directional art packed, and it is how Mizu ended up DRAWING
//                  a staff rush (gsfwd1-6) and a low drive (gsdown1-6) while PERFORMING a
//                  mist vanish — 12 cells whose move never runs.
// kageActs is still the box counter where a box is expected: it is the tape spawnHitbox
// writes at its very top, before every multiplier and before any early return.
import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const port = +(process.env.PORT || 9101), dbg = 9354;
const profile = await mkdtemp(path.join(tmpdir(), 'sp-audit-'));
const who = await fetch(`http://127.0.0.1:${port}/whoami`).then(r => r.json()).catch(() => null);
if (!who) { console.error(`no server on :${port} — python3 tools/serve.py 9101 web`); process.exit(1); }
if (path.resolve(who.tree) !== path.resolve(process.cwd())) {
  console.error(`:9101 is serving ${who.tree}\nyou are in    ${process.cwd()}\nrebind (never add a second port):\n  kill ${who.pid} && python3 tools/serve.py 9101 web`);
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
 // ⛔ NINJA_ROSTER is a module-scope const, NOT on window — waiting on window.NINJA_ROSTER
 // waits forever and the run dies with "not defined".
 // ⛔ WAIT FOR THE SHEET TO BE READY, not merely for SPRITES to exist. Several moves guard
 // on their own art (SPRITES.oni.frames.gsup1 !== undefined), so with the sheet still
 // loading those branches are skipped and the audit reports a WORKING move as dead — it
 // did exactly that for the rising claw, which spawns a box every time when driven alone.
 for(let i=0;i<300;i++){
   if(typeof NINJA_ROSTER!=='undefined' && typeof SPRITES!=='undefined'
      && SPRITES.oni && SPRITES.oni.ready && SPRITES.oni.frames
      && Object.keys(SPRITES.oni.frames).length) break;
   await new Promise(r=>setTimeout(r,50));
 }
 const DIRS={neu:p=>{}, fwd:p=>{p.getInputAxis=()=>p.facing;}, back:p=>{p.getInputAxis=()=>-p.facing;},
             down:p=>{p.isDownPressed=()=>true;}, up:p=>{p.isUpPressed=()=>true;}};
 const res={}, errs=[];
 for(let i=0;i<NINJA_ROSTER.length;i++){
   const spec=NINJA_ROSTER[i], row={};
   for(const [d,set] of Object.entries(DIRS)){
     const p=new Player(1,150,GROUND_Y-48,spec,true);
     p.opponent=new Player(2,210,GROUND_Y-48,spec,false); p.opponent.opponent=p;
     p.facing=1; p.isGrounded=true; p.attackAir=false; p.chakra=100; p.stamina=100;
     p.getInputAxis=()=>0; p.isDownPressed=()=>false; p.isUpPressed=()=>false;
     p.state=STATE.IDLE; p.attackT=0; p.lock=0; p.stunTimer=0; p.rollTimer=0; p.rollRecover=0; p.sayaLock=0;
     set(p);
     if(typeof smokeFields!=='undefined') smokeFields.length=0;
     const b=p.kageActs.length;
     try{ p.executeAttack(STATE.ATTACK_SPECIAL); }catch(e){ errs.push(spec.name+':'+d+' '+e.message.slice(0,60)); }
     const st=Object.keys(STATE).find(k=>STATE[k]===p.state)||'?';
     // ⛔ AND WHAT DID IT DRAW? The entire bug class here is art and action DISAGREEING —
     // Mizu drew a staff rush while performing a mist vanish for as long as that art has
     // been packed. Reporting only "something happened" would have missed it, so the drawn
     // family is part of the record. attackAnim is walked rather than waited on because
     // animClock does not advance inside Runtime.evaluate.
     // ⛔ AND IT IS SAMPLED BEFORE THE SIM IS STEPPED. Sampled after, the attack has
     // already ended and every move 'draws' run_clean or idle — which is exactly what
     // this check reported for four Oni directions that were provably correct.
     let drew='?';
     try{
       const man=SPRITES[spec.name.toLowerCase()];
       if(man&&man.ready){
         const byIdx={}; for(const [k,i] of Object.entries(man.frames)) (byIdx[i]||=[]).push(k);
         const fams=new Set();
         for(let s2=0;s2<12;s2++){
           if(p.attackAnim) p.attackAnim.start=animClock*1000-(s2/12)*p.attackAnim.dur*0.99;
           else p.attackT=(s2/12)*0.4;
           const i=spriteFrameIndex(p,man.frames);
           for(const k of (byIdx[i]||[])){ const mm=k.match(/^([a-z_]+?)\d+$/); fams.add(mm?mm[1]:k); }
         }
         drew=[...fams].join(',')||'?';
       }
     }catch(e){}
     for(let t=0;t<70;t++){ try{ p.update(1/60); }catch(e){} }
     const box=p.kageActs.length-b;
     const field=(typeof smokeFields!=='undefined'?smokeFields.length:0);
     const proj=(p.projectiles||[]).length;
     const faded=(p.alpha??1)<1;
     row[d]={box, field, proj, faded, st, drew, art:p.moveArt||null,
             fp:[st,box,field,proj,faded?1:0,p.moveArt||''].join('|'),
             inert: box===0 && field===0 && proj===0 && !faded && st==='ATTACK_SPECIAL'};
   }
   res[spec.name]=row;
 }
 const packed={};
 for(let i=0;i<NINJA_ROSTER.length;i++){
   const n=NINJA_ROSTER[i].name, man=SPRITES[n.toLowerCase()];
   packed[n]=man&&man.frames?['gsfwd','gsback','gsdown','gsup'].filter(f=>man.frames[f+'1']!==undefined):[];
 }
 return {res, errs, packed};
})()`);
ws.close(); chrome.kill('SIGKILL');

const DIRS = ['neu', 'fwd', 'back', 'down', 'up'];
const what = r => r.box ? `box x${r.box}` : r.field ? 'field' : r.proj ? 'proj' : r.faded ? 'vanish'
            : r.st === 'PARRY_STANCE' ? 'parry' : r.st === 'CROUCH' ? 'crouch' : '--';
console.log('\n  ground SPECIAL — what each direction actually DOES\n');
console.log('  ' + 'fighter'.padEnd(14) + DIRS.map(d => d.padStart(9)).join(''));
let inert = 0, total = 0;
const shadowed = [], inertFighters = [];
for (const [name, row] of Object.entries(out.res)) {
  const fps = new Set(DIRS.map(d => row[d].fp));
  if (fps.size === 1) shadowed.push(name);
  const dead = DIRS.filter(d => row[d].inert);
  if (dead.length === DIRS.length) inertFighters.push(name);
  console.log('  ' + name.padEnd(14) + DIRS.map(d => what(row[d]).padStart(9)).join('') +
              (fps.size === 1 ? '   <- every direction IDENTICAL' : ''));
  for (const d of DIRS) { total++; if (row[d].inert) inert++; }
}
console.log(`\n  ${total - inert}/${total} fighter-directions do something`);
// art/action agreement: a direction with its OWN packed family must DRAW that family
const mism = [];
for (const [name, row] of Object.entries(out.res)) {
  for (const d of DIRS) {
    if (d === 'neu') continue;
    const fam = 'gs' + d;
    const r = row[d];
    if (r.drew && r.drew !== '?' && r.drew.split(',').includes(fam)) continue;
    if (out.packed && out.packed[name] && out.packed[name].includes(fam))
      mism.push(`${name} ${d}: has ${fam} packed but drew ${r.drew}`);
  }
}
if (mism.length) { console.log('\n  ⛔ ART/ACTION MISMATCH:'); mism.forEach(m => console.log('    ' + m)); }
if (shadowed.length) console.log(`  ⚠ neutral Special eats every direction for: ${shadowed.join(', ')}` +
  `\n    (a bug only where that fighter has directional art packed — check <name>.json for gsfwd/gsback/gsdown/gsup)`);
if (out.errs.length) { console.log('\n  errors:'); out.errs.forEach(e => console.log('    ' + e)); }
if (inertFighters.length) console.log(`\n  ⛔ entire Special layer INERT (does nothing at all): ${inertFighters.join(', ')}`);
// Oni is the one this was written for; the rest is reported, not enforced, because a
// non-damaging Special can be a real design choice (a blind, a stance, a teleport).
const oni = out.res.Oni || {};
// ⛔ `down` IS EXEMPT BY AN OWNER RULING, not by convenience: his smoke bomb is "blind
// ONLY — no damage, no chip, no stun", written into the engine beside the move. A hitbox
// was added there during this pass and REMOVED again on finding that comment. It is listed
// as exempt rather than silently skipped so nobody re-adds one.
const BLIND_ONLY = ['down'];
const oniDead = DIRS.filter(d => oni[d] && oni[d].box === 0 && !BLIND_ONLY.includes(d));
if (oniDead.length) { console.log(`\n  ONI SPECIALS DEAD: ${oniDead.join(', ')}`); process.exit(1); }
console.log(`\n  ONI: every direction spawns a hitbox except ${BLIND_ONLY.join(', ')} (blind-only, owner ruling)`);
