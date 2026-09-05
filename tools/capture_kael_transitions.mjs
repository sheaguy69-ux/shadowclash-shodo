#!/usr/bin/env node
// Capture consecutive animation ticks around Kael's real input transitions.
import {mkdir,writeFile} from 'node:fs/promises';
import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const port = +(process.env.PORT || 9101), dbg = 9383;
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

const candidate=process.argv.includes('--candidate');
let out;
try {
 out=await ev(`(async()=>{
 for(let i=0;i<600;i++){if(typeof SPRITES!=='undefined'&&SPRITES.kael?.ready&&SPRITES.mizu?.ready)break;await new Promise(r=>setTimeout(r,50));}
 window.captureErrors=[];window.addEventListener('error',e=>window.captureErrors.push(e.message));dismissTitle();stagePick='bamboo';gameMode='2p';cpuMode=false;spectate=false;p1Pick=5;p2Pick=1;startNewGame();roundIntroTimer=0;paused=false;cutscene=null;
 for(const k in keys)keys[k]=false;physKeys.clear();
 player1.x=200;player2.x=canvas.width-100;player1.isGrounded=true;player1.y=GROUND_Y-player1.height;
 player2.isGrounded=true;player2.y=GROUND_Y-player2.height;
 if(${candidate}){
  const src=spriteFrameIndexRaw.toString();
  const from='p.spec.id === 5 && !p.isGrounded && F.kxcut1 !== undefined';
  if(!src.includes(from))throw new Error('candidate source anchor changed');
  spriteFrameIndexRaw=eval('('+src.replace(from,'p.spec.id === 5 && (p.attackAir || !p.isGrounded) && F.kxcut1 !== undefined')+')');
 }
 const groups=[],ring=[],trace=[];let collecting=null;
 const shot=()=>{const c=document.createElement('canvas');c.width=c.height=480;const g=c.getContext('2d');g.fillStyle='#e6e0d5';g.fillRect(0,0,480,480);
  g.strokeStyle='#8b8274';g.beginPath();g.moveTo(0,440);g.lineTo(480,440);g.stroke();
  g.save();g.translate(240-player1.x-player1.width/2,440-GROUND_Y);drawSprite(g,player1);g.restore();return c;};
 const key=(code,down)=>window.dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code,bubbles:true}));
 let prev={state:player1.state,ground:true},frame=0;
 await new Promise(resolve=>{function tick(){
  const p=player1,m={frame,state:Object.keys(STATE).find(k=>STATE[k]===p.state),ground:!!p.isGrounded,cell:p.drawCell,air:!!p.attackAir,recovery:p.recoveryTimer,active:matchActive,hp:[p.hp,player2.hp]};trace.push(m);
  const snap={canvas:shot(),meta:m};
  let label=null;
  if(frame>2 && prev.state===STATE.IDLE && p.state===STATE.RUN)label='idle-to-run';
  if(prev.state===STATE.RUN && p.state===STATE.IDLE)label='run-to-idle';
  if(prev.state===STATE.ATTACK_HEAVY && p.state===STATE.IDLE)label='heavy-to-recovery';
  if(!prev.ground && p.isGrounded && p.attackAir && p.state===STATE.ATTACK_HEAVY)label='air-heavy-landing';
  if(label&&!groups.some(g=>g.label===label)){collecting={label,shots:ring.slice(-3),remaining:5};groups.push(collecting);}
  if(collecting){collecting.shots.push(snap);if(--collecting.remaining<=0)collecting=null;}
  ring.push(snap);if(ring.length>3)ring.shift();
  prev={state:p.state,ground:!!p.isGrounded};
  if(frame===15)key('KeyD',true);
  if(frame===40)key('KeyD',false);
  if(frame===65){key('KeyG',true);key('KeyG',false);}
  if(frame===110)key('KeyW',true);
  if(frame===115)key('KeyW',false);
  if(frame===135){key('KeyG',true);key('KeyG',false);}
  if(++frame<180)requestAnimationFrame(tick);else resolve();
 }requestAnimationFrame(tick);});
 const strips=groups.map(group=>{const c=document.createElement('canvas');c.width=1280;c.height=Math.ceil(group.shots.length/4)*350;const g=c.getContext('2d');g.fillStyle='#e6e0d5';g.fillRect(0,0,c.width,c.height);
  group.shots.forEach((s,i)=>{const x=i%4*320,y=Math.floor(i/4)*350;g.drawImage(s.canvas,x,y+30,320,320);g.fillStyle='#151515';g.font='14px sans-serif';g.fillText('tick '+s.meta.frame+' / cell '+s.meta.cell+' / '+(s.meta.ground?'ground':'air'),x+8,y+20);});
  return {label:group.label,frames:group.shots.map(s=>s.meta),png:c.toDataURL('image/png').split(',')[1]};});
 return {candidate:${candidate},trace,strips,errors:window.captureErrors};
 })()`);
} finally {ws.close();chrome.kill('SIGKILL');}
const dir=path.resolve(process.env.OUT||'media/kael-smoothness-review-20260905');await mkdir(dir,{recursive:true});
for(const s of out.strips){await writeFile(path.join(dir,s.label+'.png'),Buffer.from(s.png,'base64'));delete s.png;}
await writeFile(path.join(dir,'trace.json'),JSON.stringify(out,null,2));
console.log(JSON.stringify({dir,candidate,errors:out.errors,transitions:out.strips.map(s=>({label:s.label,frames:s.frames}))},null,2));
if(!out.strips.some(s=>s.label==='air-heavy-landing'))process.exitCode=1;
