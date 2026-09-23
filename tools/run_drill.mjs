#!/usr/bin/env node
// Run a training DRILL headlessly and report what the mechanic actually does.
//
// ⛔ THIS IS THE POINT OF THE DRILL. A check proves a mechanic's arithmetic; only playing
// it proves the mechanic. This drives the real training dummy through a real drill for a
// real number of seconds and reports the outcome — how often the move came out, how much
// damage it did to a standing target, and whether the drill silently did nothing.
//   node tools/run_drill.mjs [drillIndex] [seconds]
import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
const port = 9101, dbg = 9337;
const drill = Number(process.argv[2] ?? 1), secs = Number(process.argv[3] ?? 8);
const profile = await mkdtemp(path.join(tmpdir(), 'drill-'));
// reap the previous run and WAIT for the port to actually free — back-to-back drills
// raced here and the second one attached to nothing ("cannot read webSocketDebuggerUrl")
spawnSync('pkill', ['-f', `remote-debugging-port=${dbg}`], { stdio: 'ignore' });
await new Promise(r => setTimeout(r, 800));
if (!await fetch(`http://127.0.0.1:${port}/`).then(r => r.ok).catch(() => false)) {
  console.error('no server on :9100 — python3 tools/serve.py 9101 web'); process.exit(1);
}
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ['--headless=new','--disable-gpu','--no-first-run',`--remote-debugging-port=${dbg}`,
   `--user-data-dir=${profile}`,`http://127.0.0.1:${port}/`], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let page;
for (let i=0;i<100&&!page;i++){try{const l=await fetch(`http://127.0.0.1:${dbg}/json/list`).then(r=>r.json());page=l.find(t=>t.type==='page'&&t.url.includes(String(port)));}catch{} if(!page) await sleep(100);}
if (!page) { console.error(`chrome never came up on :${dbg} — is another run still holding it?`); process.exit(1); }
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((r,j)=>{ws.addEventListener('open',r,{once:true});ws.addEventListener('error',j,{once:true});});
let id=1;const pend=new Map();
ws.addEventListener('message',e=>{const m=JSON.parse(e.data);if(m.id&&pend.has(m.id)){const p=pend.get(m.id);pend.delete(m.id);m.error?p.rej(new Error(m.error.message)):p.res(m.result);}});
const ev = x => new Promise((res,rej)=>{const n=id++;pend.set(n,{res,rej});ws.send(JSON.stringify({id:n,method:'Runtime.evaluate',params:{expression:x,awaitPromise:true,returnByValue:true}}));}).then(r=>{if(r.exceptionDetails)throw new Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;});

const out = await ev(`(async () => {
  const wait=async(t,m)=>{for(let i=0;i<200;i++){if(t())return;await new Promise(r=>setTimeout(r,50));}throw new Error(m)};
  await wait(()=>typeof SPRITES!=='undefined'&&SPRITES.oni&&SPRITES.oni.ready,'sheets');
  const want = DRILLS[${drill}].want;
  const pick = n => NINJA_ROSTER.findIndex(s => s.name === n);
  gameMode='training'; cpuMode=false;
  p1Pick = pick('Kael'); p2Pick = want ? pick(want) : 1;
  resetRound();
  drillIdx=${drill}; drillT=0;
  const P=player1, D=player2;
  P.x = D.x - ${process.env.GAP ?? 70};                     // stand the "player" right next to the dummy
  const hp0=P.hp, dt=1/60; let fired=0, maxFields=0, framesHidden=0, jumps=0, airborne=0;
  let lastSpecial=false, wasGrounded=true;
  for (let f=0; f<${secs}*60; f++) {
    runDrill(dt);
    D.update(dt, P); P.update(dt, D);
    // ⛔ RESOLVE HITBOXES, or every ordinary attack reports 0 damage and the drill blames
    // the MOVE for a hole in the harness — the cartwheel read as toothless at every range
    // until this line existed, when in fact it had simply never been allowed to connect.
    processHitboxes(D, P, dt);
    // count move activations by watching the dummy enter its special/light
    const nowSpecial = D.state===STATE.ATTACK_SPECIAL || D.state===STATE.ATTACK_LIGHT;
    if (nowSpecial && !lastSpecial) fired++;
    lastSpecial = nowSpecial;
    // ⛔ COUNT JUMPS TOO, or a movement drill reports 0 and reads as broken when it is
    // the METRIC that is blind — the double-jump drill did exactly that on its first run.
    if (wasGrounded && !D.isGrounded) jumps++;
    wasGrounded = D.isGrounded;
    if (!D.isGrounded) airborne++;
    maxFields = Math.max(maxFields, smokeFields.length);
    if (D.hiddenInSmoke) framesHidden++;
    for (let i=smokeFields.length-1;i>=0;i--){const fl=smokeFields[i];fl.duration-=dt;
      if(fl.kind==='smokebomb'&&fl.owner){fl.tick-=dt;if(fl.tick<=0){fl.tick=0.45;
        const vx=P.x+P.width/2,vy=P.y+P.height/2;
        if(Math.hypot(vx-fl.x,vy-fl.y)<fl.radius) P.takeDamage(4,fl.owner,{pushback:90,tier:STATE.ATTACK_SPECIAL});}}
      if(fl.duration<=0) smokeFields.splice(i,1);}
  }
  return { drill: DRILLS[${drill}].name, dummy: D.spec.name, fired, jumps,
           airbornePct: Math.round(airborne/(${secs}*60)*100),
           maxFields, framesHidden, dmgToPlayer: +(hp0-P.hp).toFixed(1),
           dps: +((hp0-P.hp)/${secs}).toFixed(2) };
})()`).catch(e => ({ ERR: e.message }));
ws.close(); chrome.kill('SIGKILL');
console.log(out);
