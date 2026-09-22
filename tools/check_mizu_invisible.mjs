import { spawn, spawnSync } from 'node:child_process';
// Prove Mizu renders NOTHING while hidden — by counting pixels her own draw() puts on an
// offscreen canvas, not by reading the code. 2139 px visible vs 0 px hidden. A ring, a
// contact shadow or a motion trail sneaking back in shows up here as a non-zero count;
// "alpha is 0" would not catch any of them, because each has its own alpha term.

import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
const port=9100, dbg=9338;
const profile=await mkdtemp(path.join(tmpdir(),'invis-'));
spawnSync('pkill',['-f',`remote-debugging-port=${dbg}`],{stdio:'ignore'});
await new Promise(r=>setTimeout(r,800));
if(!await fetch(`http://127.0.0.1:${port}/`).then(r=>r.ok).catch(()=>false)){console.error('no :9100');process.exit(1);}
const chrome=spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
 ['--headless=new','--disable-gpu','--no-first-run',`--remote-debugging-port=${dbg}`,
  `--user-data-dir=${profile}`,`http://127.0.0.1:${port}/`],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let page;for(let i=0;i<100&&!page;i++){try{const l=await fetch(`http://127.0.0.1:${dbg}/json/list`).then(r=>r.json());page=l.find(t=>t.type==='page'&&t.url.includes(String(port)));}catch{} if(!page)await sleep(100);}
const ws=new WebSocket(page.webSocketDebuggerUrl);
await new Promise((r,j)=>{ws.addEventListener('open',r,{once:true});ws.addEventListener('error',j,{once:true});});
let id=1;const pend=new Map();
ws.addEventListener('message',e=>{const m=JSON.parse(e.data);if(m.id&&pend.has(m.id)){const p=pend.get(m.id);pend.delete(m.id);m.error?p.rej(new Error(m.error.message)):p.res(m.result);}});
const ev=x=>new Promise((res,rej)=>{const n=id++;pend.set(n,{res,rej});ws.send(JSON.stringify({id:n,method:'Runtime.evaluate',params:{expression:x,awaitPromise:true,returnByValue:true}}));}).then(r=>{if(r.exceptionDetails)throw new Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;});
const out=await ev(String.raw`(async()=>{
  const wait=async(t,m)=>{for(let i=0;i<200;i++){if(t())return;await new Promise(r=>setTimeout(r,50));}throw new Error(m)};
  await wait(()=>typeof SPRITES!=='undefined'&&SPRITES.mizu&&SPRITES.mizu.ready,'sheets');
  const pick=n=>NINJA_ROSTER.findIndex(s=>s.name===n);
  gameMode='training'; cpuMode=false; p1Pick=pick('Mizu'); p2Pick=pick('Kael');
  resetRound();
  const M=player1;
  // an OFFSCREEN canvas so nothing else (HUD, stage) is counted — only her draw call
  const c=document.createElement('canvas'); c.width=400; c.height=400;
  const g=c.getContext('2d');
  const countInk=()=>{const d=g.getImageData(0,0,400,400).data;let n=0;
    for(let i=3;i<d.length;i+=4) if(d[i]>4) n++; return n;};
  const render=()=>{g.clearRect(0,0,400,400);g.save();
    g.translate(200-(M.x+M.width/2),300-(M.y+M.height));M.draw(g);g.restore();};
  smokeFields.length=0; M.alpha=1; M.hiddenInSmoke=false;
  render(); const visible=countInk();
  // now hide her exactly the way the game does
  M.chakra=999; M.isGrounded=true; M.executeAttack(STATE.ATTACK_SPECIAL);
  M.update(1/60, player2);
  render(); const hidden=countInk();
  // ⛔ AND THE OTHER HALF OF THE RULE: HER ATTACKS MUST GIVE HER AWAY (owner). Being
  // unseeable is the reward for not swinging — sparks and slash FX are the cost of acting.
  // They live in the global particle/slash lists with their OWN life-based alpha, drawn
  // outside her draw(), so they are unaffected by her being at alpha 0. Asserted here so a
  // future "hide everything about her" change cannot quietly take the tell away too.
  particles.length = 0; slashes.length = 0;
  M.attackDir = 'neutral'; M.attackAir = false; M.isGrounded = true;
  M.executeAttack(STATE.ATTACK_LIGHT);
  for (let i = 0; i < 30; i++) { M.update(1/60, player2); processHitboxes(M, player2, 1/60); }
  const fx = particles.length + slashes.length;
  render(); const bodyStillHidden = countInk();
  return { fieldsUp:smokeFields.length, alpha:M.alpha, hiddenFlag:M.hiddenInSmoke,
           pixelsVisible:visible, pixelsWhileHidden:hidden,
           attackFxWhileHidden: fx, bodyPixelsWhileAttacking: bodyStillHidden };
})()`).catch(e=>({ERR:e.message}));
ws.close(); chrome.kill('SIGKILL');
console.log(out);
