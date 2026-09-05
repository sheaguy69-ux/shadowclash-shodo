#!/usr/bin/env node
// Review all nine fighters using real DOM inputs and consecutive live-loop captures.
import {mkdir,writeFile,mkdtemp} from 'node:fs/promises';
import { spawn, spawnSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import path from 'node:path';

const port = +(process.env.PORT || 9101), dbg = 9384;
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
  ['--headless=new', '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--disable-gpu', '--no-first-run', `--remote-debugging-port=${dbg}`,
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

// Initial navigation can replace the execution context before the sheets decode.
let ready=false;
for(let n=0;n<600&&!ready;n++){
 ready=await ev("typeof NINJA_ROSTER!=='undefined' && NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)").catch(()=>false);
 if(!ready)await sleep(50);
}
const root=path.resolve(process.env.OUT||'media/roster-animation-review-20260905');
const results=[];
try {
 if(!ready)throw new Error('roster did not load');
 const names=await ev('NINJA_ROSTER.map(s=>s.name)');
 for(let idx=0;idx<names.length;idx++)for(const [tier,code] of Object.entries({Light:'KeyF',Medium:'KeyJ',Heavy:'KeyG',Special:'KeyH'})){
  if(process.env.NAME&&names[idx].toLowerCase()!==process.env.NAME.toLowerCase())continue;
  if(process.env.TIER&&tier.toLowerCase()!==process.env.TIER.toLowerCase())continue;
  const out=await ev(`(async()=>{
   window.rosterCaptureErrors=[];window.onerror=(m)=>window.rosterCaptureErrors.push(String(m));
   dismissTitle();stagePick='bamboo';gameMode='2p';cpuMode=false;spectate=false;p1Pick=${idx};p2Pick=${idx===0?1:0};startNewGame();roundIntroTimer=0;paused=false;cutscene=null;
   for(const k in keys)keys[k]=false;physKeys.clear();
   player1.x=200;player2.x=canvas.width-100;
   for(const p of [player1,player2]){p.isGrounded=true;p.y=GROUND_Y-p.height;}
   if(${!!process.env.CHUDAN} && player1.spec.id===0)player1.chudan=true;
   const man=SPRITES[player1.spec.name.toLowerCase()],byCell={};
   for(const [key,cell] of Object.entries(man.frames))(byCell[cell]||=[]).push(key);
   const attack=STATE['ATTACK_${tier.toUpperCase()}'];
   const groups=[],ring=[],trace=[];let collecting=null,frame=0;
   const shot=()=>{const c=document.createElement('canvas');c.width=c.height=480;const g=c.getContext('2d');g.fillStyle='#e6e0d5';g.fillRect(0,0,480,480);g.strokeStyle='#8b8274';g.beginPath();g.moveTo(0,440);g.lineTo(480,440);g.stroke();g.save();g.translate(240-player1.x-player1.width/2,440-GROUND_Y);drawSprite(g,player1);g.restore();return c;};
   const key=(code,down)=>window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,bubbles:true}));
   let prev={state:player1.state,ground:true};
   await new Promise(resolve=>{function tick(){
    const p=player1,canvas=shot(),meta={frame,state:Object.keys(STATE).find(k=>STATE[k]===p.state),ground:!!p.isGrounded,cell:p.drawCell,keys:byCell[p.drawCell]||[],air:!!p.attackAir,recovery:p.recoveryTimer,active:matchActive,hp:[p.hp,player2.hp]};trace.push(meta);
    const snap={canvas,meta};let label=null;
    if(frame>2&&prev.state===STATE.IDLE&&p.state===STATE.RUN)label='idle-to-run';
    if(prev.state===STATE.RUN&&p.state===STATE.IDLE)label='run-to-idle';
    if([attack,STATE.THROWING,STATE.PARRY_STANCE].includes(prev.state)&&p.state!==prev.state&&frame<140)label='ground-recovery';
    if(frame===66)label='ground-start';
    if(frame===${Number(process.env.AIR_FRAME||165)+1})label='air-start';
    if(frame>140&&!prev.ground&&p.isGrounded)label='landing';
    if(label&&!groups.some(g=>g.label===label)){collecting={label,shots:ring.slice(-3),remaining:5};groups.push(collecting);}
    if(collecting){collecting.shots.push(snap);if(--collecting.remaining<=0)collecting=null;}
    ring.push(snap);if(ring.length>3)ring.shift();prev={state:p.state,ground:!!p.isGrounded};
    if(frame===15)key('KeyD',true);if(frame===40)key('KeyD',false);
    if(frame===65){key('${code}',true);key('${code}',false);}
    if(frame===140)key('KeyW',true);if(frame===145)key('KeyW',false);
    if(frame===${Number(process.env.AIR_FRAME||165)}){key('${code}',true);key('${code}',false);}
    if(++frame<230)requestAnimationFrame(tick);else resolve();
   }requestAnimationFrame(tick);});
   const strips=groups.map(group=>{const c=document.createElement('canvas');c.width=1280;c.height=Math.ceil(group.shots.length/4)*350;const g=c.getContext('2d');g.fillStyle='#e6e0d5';g.fillRect(0,0,c.width,c.height);group.shots.forEach((s,i)=>{const x=i%4*320,y=Math.floor(i/4)*350;g.drawImage(s.canvas,x,y+30,320,320);g.fillStyle='#151515';g.font='14px sans-serif';g.fillText('tick '+s.meta.frame+' / cell '+s.meta.cell+' / '+(s.meta.ground?'ground':'air'),x+8,y+20);});return {label:group.label,frames:group.shots.map(s=>s.meta),png:c.toDataURL('image/png').split(',')[1]};});
   return {name:player1.spec.name,tier:'${tier}',trace,strips,airCells:airAttackCells(man.frames),errors:window.rosterCaptureErrors};
  })()`);
  const dir=path.join(root,out.name.toLowerCase(),tier.toLowerCase());await mkdir(dir,{recursive:true});
  for(const s of out.strips){await writeFile(path.join(dir,s.label+'.png'),Buffer.from(s.png,'base64'));delete s.png;}
  await writeFile(path.join(dir,'trace.json'),JSON.stringify(out,null,2));
  const landing=out.strips.find(s=>s.label==='landing');
  const failures=[];
  for(const label of ['ground-start','air-start','landing'])if(!out.strips.some(s=>s.label===label))failures.push('missing '+label);
  for(const label of ['ground-start','air-start']){const f=out.strips.find(s=>s.label===label)?.frames[3];if(f&&!['ATTACK_'+tier.toUpperCase(),'THROWING','PARRY_STANCE'].includes(f.state))failures.push(label+' did not start: '+f.state);}
  if(process.argv.includes('--check-landing')&&(tier==='Medium'||tier==='Special'&&!['Shin','Tsubasa','Kael','Oni'].includes(out.name))){
   const active=landing?.frames.filter(f=>f.state==='ATTACK_'+tier.toUpperCase()&&f.recovery>0)||[];
   if(!active.some(f=>f.ground)||active.some(f=>!out.airCells.includes(f.cell)))failures.push('air attack changed cell family at landing');
  }
  const summary={failures,name:out.name,tier,errors:out.errors,transitions:out.strips.map(s=>s.label),landing:landing?.frames.map(f=>({cell:f.cell,keys:f.keys,ground:f.ground,state:f.state,recovery:f.recovery}))};
  results.push(summary);console.log(JSON.stringify(summary));
  if(out.errors.length||failures.length)process.exitCode=1;
 }
}finally{ws.close();chrome.kill('SIGKILL');}
await mkdir(root,{recursive:true});await writeFile(path.join(root,'summary.json'),JSON.stringify(results,null,2));
