#!/usr/bin/env node
// Review the whole roster using real DOM inputs and consecutive live-loop captures.
import {mkdir,writeFile,mkdtemp} from 'node:fs/promises';
import { spawn, spawnSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { ROSTER } from './roster.mjs';

const port = +(process.env.PORT || 9101), dbg = 9385;
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


let ready=false;
for(let i=0;i<600&&!ready;i++){ready=await ev("typeof NINJA_ROSTER!=='undefined' && NINJA_ROSTER.every(s=>SPRITES[s.name.toLowerCase()]?.ready)").catch(()=>false);if(!ready)await sleep(50);}
const root=path.resolve(process.env.OUT||'media/direction-review-20260905');await mkdir(root,{recursive:true});
const results=[];
try{
 if(!ready)throw new Error('sheets unavailable');
 for(let id=0;id<ROSTER.length;id++){   // roster.mjs, not a hardcoded 9: id 8 is nobody since Oni retired
 const out=await ev(`(async()=>{
 const rightAuthored={"ember": [247, 248, 249, 250, 251, 252, 253, 254], "kael": [6, 7, 8, 9, 10, 11, 12, 13, 19, 20, 21, 22, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 135, 136, 191, 192], "mokurai": [98, 99, 100, 101, 186, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 324, 325, 326, 327, 328, 329, 330, 331, 355, 356, 357, 358, 359, 360, 361, 362], "mizu": [102], "shin": [339], "exile": [313]};
 // Sep7 native-frame review: these attack sources point right before rendering.
 const attackRight={"mizu":[166,167,168,169,170,171,172,173,109,110,111,112,113,114,115,116,198,199,200,201,202,203,205],"ember":[239,240,241,242,243,244,245,246,147,148,149,150,151,152,153,154,284,285,286,287,288,289,99,100,101,102,103,104,105,106],"kael":[222,223,224,225,226,227,228,236,194,195,196,197,198,199,200,201,202,203,204,205,206,207,305,209,291,292,293,294,295,296,297,298],"exile":[231,232,233,234,235,236],"tsubasa":[331,332,333,334,335,336,280,281,176,177,178]};
 for(const [name,cells] of Object.entries(attackRight))(rightAuthored[name]||=[]).push(...cells);
 // Source-reviewed replacement cells; direction comes from the drawings, not manifest flags.
 rightAuthored.oni=[601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 635, 636, 637, 639, 640, 641, 642, 643, 647, 648, 649, 650, 651, 652, 653, 654, 655, 656, 657, 658, 659];
 // Independently viewed right-authored ground families (source recovery 722–723).
 const groundRight={"mokurai":[371,372,373,374,375,376,377,378,379,380,381,382,383,384,385,386],"exile":[377,378,379,380,381,382,383,384,252,138,139,140,393,394,395,253,254,154,155,156,396,158,159,160],"oni":[584,585,578,579,580,581,582,583,362,363,364,365,589,590,368,369,232,233,234,591,592,329,238,239,386,593,388,389,390,391,392,393,586,587,588,378,379,380,594,595,596,384,385],"tsubasa":[314,315,316,319,320,321,355,356],"shin":[222,378,224,225,226]};
 // A retired fighter's review rows have no sheet to check — SKIP them, do not delete the
 // recorded review. Reading SPRITES.oni.mirror is what took this whole check down.
 for(const [name,cells] of Object.entries(groundRight)){if(!SPRITES[name])continue;for(const cell of cells)if(!SPRITES[name].mirror?.[cell])throw Error(name+' ground attack faces backward: '+cell);}
 // Shin's source returns to a left-authored crouch before and after its rightward release.
 for(const cell of [220,221,227])if(SPRITES.shin.mirror?.[cell])throw Error('Shin ready/settle faces backward: '+cell);
 rightAuthored.mokurai.push(387,234,235,236,238);
 // Contact-side review also covers the inherited air/rear attack families.
 const residualRight={"oni":[554,555,556,557,558,559,560,561],"ember":[225,226,227,228,229,230],"exile":[212,266,332,333],"executioner":[261,156]};
 for(const [name,cells] of Object.entries(residualRight))(rightAuthored[name]||=[]).push(...cells);
 const rows=[],shots=[],errors=[];window.onerror=(m)=>errors.push(String(m));let g=null,lastSign=0;
 const original=drawShodoFrame;
 drawShodoFrame=function(...args){if(args[0]===g)lastSign=Math.sign(g.getTransform().a);return original(...args);};
 const key=(code,v)=>window.dispatchEvent(new KeyboardEvent(v?'keydown':'keyup',{code,bubbles:true}));
 const wait=()=>new Promise(r=>requestAnimationFrame(r));
 const reset=(side)=>{dismissTitle();stagePick='bamboo';gameMode='2p';cpuMode=false;spectate=false;p1Pick=${id};p2Pick=${id===0?1:0};startNewGame();roundIntroTimer=0;paused=false;cutscene=null;for(const k in keys)keys[k]=false;physKeys.clear();player1.x=side===1?200:600;player2.x=side===1?600:200;for(const p of [player1,player2]){p.y=GROUND_Y-p.height;p.isGrounded=true;}};
 const take=(label,side)=>{const p=player1,man=SPRITES[p.spec.name.toLowerCase()];const c=document.createElement('canvas');c.width=c.height=480;g=c.getContext('2d');g.fillStyle='#e6e0d5';g.fillRect(0,0,480,480);g.save();g.translate(240-p.x-p.width/2,400-p.y-p.height);g.strokeStyle='#916b40';g.lineWidth=2;if(label.startsWith('wall')){const wx=side===-1?10:canvas.width-10;g.beginPath();g.moveTo(wx,0);g.lineTo(wx,GROUND_Y);g.stroke();}drawSprite(g,p);g.restore();const idx=p.drawCell;
 if(label.startsWith('run-')){const phase=p.animPhase,cells=runCells(man.frames);for(let i=0;i<cells.length;i++){p.animPhase=i+0.01;if(spriteFrameIndexRaw(p,man.frames)!==cells[i])throw new Error('run cycle plays backwards');}p.animPhase=phase;}
 const row={name:p.spec.name,label,side,facing:p.facing,vx:p.vx,wallDir:p.wallDir,wallJumpLock:p.wallJumpLock,ground:p.isGrounded,state:p.state,cell:idx,keys:Object.keys(man.frames).filter(k=>man.frames[k]===idx),scaleX:lastSign,wallFacing:lastSign*((rightAuthored[p.spec.name.toLowerCase()]||[]).includes(idx)?1:-1),visualFacing:lastSign*((rightAuthored[p.spec.name.toLowerCase()]||[]).includes(idx)?1:-1)};if(p.spec.id===2&&label==='run-away'){
 const tape=p.kageTape,timer=p.kageTapeT;p.kageTape=[];p.kageTapeT=0;p.recordKageTape(1/60);const echo={played:animClock};p.updateKageEcho(0,echo);
 if(echo.drawMirror!==p.drawMirror||echo.facing!==p.facing)throw new Error('echo lost visual/combat facing separation');p.kageTape=tape;p.kageTapeT=timer;row.echoMirrorPassed=true;
 }rows.push(row);shots.push({canvas:c,row});};
 try{for(const side of [1,-1]){
 reset(side);for(let i=0;i<3;i++)await wait();take('idle',side);
 key('KeyS',true);for(let i=0;i<5;i++){await wait();take('crouch',side);}key('KeyS',false);for(let i=0;i<3;i++)await wait();key('KeyC',true);for(let i=0;i<20;i++)await wait();for(let i=0;i<5;i++){await wait();take('guard',side);}key('KeyC',false);for(let i=0;i<3;i++)await wait();
 key(side===1?'KeyD':'KeyA',true);for(let i=0;i<5;i++){await wait();take('run-toward',side);}key(side===1?'KeyD':'KeyA',false);
 key(side===1?'KeyA':'KeyD',true);for(let i=0;i<5;i++){await wait();take('run-away',side);}key(side===1?'KeyA':'KeyD',false);
 for(let i=0;i<3;i++)await wait();take('stop',side);
 player2.x=player1.x-side*180;for(let i=0;i<3;i++)await wait();take('crossup',-side);
 // Establish contact using real physics and held input, not a forced wallDir.
 player1.x=side===-1?11:canvas.width-11-player1.width;player1.y=GROUND_Y-player1.height-200;player1.vy=0;player1.isGrounded=false;
 key(side===-1?'KeyA':'KeyD',true);
 for(let i=0;i<6;i++){await wait();take('wall-cling',side);}
 key('KeyG',true);key('KeyG',false);for(let i=0;i<5;i++){await wait();take('wall-heavy',side);}
 key(side===-1?'KeyA':'KeyD',false);for(let i=0;i<5;i++){await wait();take('wall-attack-release',side);}
 reset(side);player1.x=side===-1?11:canvas.width-11-player1.width;player1.y=GROUND_Y-player1.height-200;player1.vy=0;player1.isGrounded=false;key(side===-1?'KeyA':'KeyD',true);for(let i=0;i<6;i++)await wait();key(side===-1?'KeyA':'KeyD',false);for(let i=0;i<5;i++){await wait();take('wall-release',side);}key(side===-1?'KeyA':'KeyD',true);for(let i=0;i<6;i++)await wait();key('KeyW',true);key('KeyW',false);if(player1.wallJumpLock<=0||player1.wallDir!==0||player1.facing!==-side||Math.sign(player1.vx)!==-side)throw Error('wall kick did not start outward');for(let i=0;i<5;i++){await wait();take('wall-jump',side);}
 }}finally{drawShodoFrame=original;}
 const strips=[];for(const side of [1,-1])for(const label of ['idle','crouch','guard','run-toward','run-away','stop','crossup','wall-cling','wall-heavy','wall-release','wall-attack-release','wall-jump']){
 const frames=shots.filter(s=>s.row.side===side&&s.row.label===label);const c=document.createElement('canvas');c.width=frames.length*240;c.height=270;const x=c.getContext('2d');x.fillStyle='#e6e0d5';x.fillRect(0,0,c.width,c.height);frames.forEach((s,i)=>{x.drawImage(s.canvas,i*240,30,240,240);x.fillStyle='#111';x.font='12px sans-serif';x.fillText(s.row.cell+' '+s.row.state,i*240+5,18);});strips.push({label,side,png:c.toDataURL('image/png').split(',')[1]});}
 return {name:player1.spec.name,rows,strips,errors};
 })()`);
 const dir=path.join(root,out.name.toLowerCase());await mkdir(dir,{recursive:true});for(const s of out.strips){await writeFile(path.join(dir,s.label+'-'+s.side+'.png'),Buffer.from(s.png,'base64'));delete s.png;}
 // Wall-kick momentum is protected by simulation time, not five render frames.
 // Held into-wall input is intentionally effective again after the lock expires.
 const failures=out.rows.filter(r=>r.label.startsWith('run-')?r.visualFacing!==Math.sign(r.vx):['idle','stop','crossup','crouch','guard'].includes(r.label)?(r.facing!==r.side||r.visualFacing!==r.side):r.label==='wall-cling'&&r.state==='WALL_CLING'?r.wallFacing!==r.side:r.label==='wall-cling'&&r.wallDir!==0?r.visualFacing!==r.side:r.label==='wall-release'?(r.state==='WALL_CLING'?r.wallFacing!==r.side:r.visualFacing!==-r.side):r.label==='wall-heavy'&&r.state==='ATTACK_HEAVY'?r.visualFacing!==-r.side:r.label==='wall-jump'?(r.wallJumpLock>0?(r.facing!==-r.side||Math.sign(r.vx)!==-r.side||r.visualFacing!==-r.side):(Math.abs(r.vx)>.1&&r.visualFacing!==Math.sign(r.vx))):false);
 for(const side of [1,-1]){if(!out.rows.some(r=>r.label==='wall-jump'&&r.side===side&&r.wallJumpLock>0))failures.push({side,reason:'no preserved-momentum wall kick observed'});if(!out.rows.some(r=>r.label==='wall-cling'&&r.side===side&&r.wallDir===side&&r.state==='WALL_CLING'))failures.push({side,reason:'no wall contact'});if(!out.rows.some(r=>r.label==='wall-heavy'&&r.side===side&&r.state==='ATTACK_HEAVY'))failures.push({side,reason:'wall attack did not start'});}
 failures.push(...out.errors.map(error=>({error})));results.push({name:out.name,failures});await writeFile(path.join(dir,'trace.json'),JSON.stringify(out,null,2));console.log(out.name+': '+failures.length+' direction failures');
 }
}finally{ws.close();chrome.kill('SIGKILL');}
await writeFile(path.join(root,'summary.json'),JSON.stringify(results,null,2));if(results.some(r=>r.failures.length))process.exitCode=1;
