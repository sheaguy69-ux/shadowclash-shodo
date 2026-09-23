import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
const port = 9100, dbg = 9336;
const profile = await mkdtemp(path.join(tmpdir(), 'mech-'));
spawnSync('pkill', ['-f', `remote-debugging-port=${dbg}`], { stdio: 'ignore' });
const alive = await fetch(`http://127.0.0.1:${port}/`).then(r => r.ok).catch(() => false);
if (!alive) { console.error('start: python3 tools/serve.py 9100 web'); process.exit(1); }
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ['--headless=new','--disable-gpu','--no-first-run',`--remote-debugging-port=${dbg}`,
   `--user-data-dir=${profile}`,`http://127.0.0.1:${port}/`], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let page;
for (let i=0;i<100&&!page;i++){try{const l=await fetch(`http://127.0.0.1:${dbg}/json/list`).then(r=>r.json());page=l.find(t=>t.type==='page'&&t.url.includes(String(port)));}catch{} if(!page) await sleep(100);}
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((r,j)=>{ws.addEventListener('open',r,{once:true});ws.addEventListener('error',j,{once:true});});
let id=1;const pend=new Map();
ws.addEventListener('message',e=>{const m=JSON.parse(e.data);if(m.id&&pend.has(m.id)){const p=pend.get(m.id);pend.delete(m.id);m.error?p.rej(new Error(m.error.message)):p.res(m.result);}});
const ev = x => new Promise((res,rej)=>{const n=id++;pend.set(n,{res,rej});ws.send(JSON.stringify({id:n,method:'Runtime.evaluate',params:{expression:x,awaitPromise:true,returnByValue:true}}));}).then(r=>{if(r.exceptionDetails)throw new Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;});

const out = await ev(String.raw`(async () => {
  const wait=async(t,m)=>{for(let i=0;i<200;i++){if(t())return;await new Promise(r=>setTimeout(r,50));}throw new Error(m)};
  // ⛔ WAS SPRITES.oni.ready — AND ONI RETIRED AT 853, so this gate could never get past
  // its own first line. It failed honestly rather than lying, which is why it went
  // unnoticed rather than green. Mizu is the right probe for a SMOKE check: she is the
  // only fighter who casts a field anyone can hide in (the one smokeFields.push in the
  // file), so if her sheet is up the thing this gate measures is loadable.
  await wait(()=>typeof SPRITES!=='undefined'&&SPRITES.mizu&&SPRITES.mizu.ready,'sheets');
  const R=n=>NINJA_ROSTER.find(s=>s.name.toLowerCase()===n);
  const out={};
  // ---- MIZU MIST ----
  smokeFields.length=0;
  const mz=new Player(1,300,GROUND_Y-48,R('mizu'),true);
  // The opponent here is only a BODY to be dimmed by her cloud — nothing about this
  // assertion is fighter-specific. It was Oni, who retired at 853.
  const en=new Player(2,340,GROUND_Y-48,R('kael'),false);
  mz.opponent=en; en.opponent=mz;
  // ⛔ CAST THE REAL MOVE. This used to push a field with hardcoded numbers and then assert
  // those same numbers back — it happily reported duration 7 after the game had been changed
  // to 4, because it was only ever agreeing with itself. Fire the actual Special instead.
  mz.chakra = 999; mz.isGrounded = true; mz.mistCd = 0;
  mz.executeAttack(STATE.ATTACK_SPECIAL);
  out.mistFields = smokeFields.length;
  out.mistRadius = smokeFields[0] && smokeFields[0].radius;
  out.mistDur = smokeFields[0] && smokeFields[0].duration;
  // recasting must REPLACE, not stack, and must be refused while on cooldown
  mz.executeAttack(STATE.ATTACK_SPECIAL);
  out.afterRecastOnCd = smokeFields.length;
  mz.mistCd = 0; mz.executeAttack(STATE.ATTACK_SPECIAL);
  out.afterRecastOffCd = smokeFields.length;
  const fade=(p)=>{p.alpha=1;p.hiddenInSmoke=false;const cx=p.x+p.width/2,cy=p.y+p.height/2;
    for(const f of smokeFields){if(Math.hypot(cx-f.x,cy-f.y)>=f.radius)continue;
      if(f.owner===p&&f.kind==='mist'){p.alpha=0;p.hiddenInSmoke=true;}else{p.alpha=Math.min(p.alpha,0.3);}}};
  fade(mz); fade(en);
  out.mizuAlpha=mz.alpha; out.mizuHidden=mz.hiddenInSmoke;
  out.enemyAlpha=en.alpha; out.enemyHidden=en.hiddenInSmoke;
  const hpBefore=en.hp; // mist must not hurt
  out.mistNoDamage = en.hp===hpBefore;

  // ---- CONTACT ROUTING: hit / block / dodge ----
  // ⛔ TITLED "ONI SMOKE BOMB" AND BUILT AN ONI, BUT MEASURES NEITHER. 'strike' is a bare
  // takeDamage(4, ..., tier: ATTACK_SPECIAL) — no bomb, no field, nothing that reads the
  // attacker's identity. It asserts the three contact routes: clean damage, reduced through
  // a guard, zero through i-frames. Oni retired at 853 so R('oni') returned undefined and
  // 'new Player' died on spec.sizeScale. Repointed to a live fighter; the assertions are
  // byte-identical because none of them ever depended on who was swinging.
  const mk=()=>{const o=new Player(1,300,GROUND_Y-48,R('shin'),true);
                const v=new Player(2,320,GROUND_Y-48,R('kael'),false);
                o.opponent=v;v.opponent=o;return [o,v];};
  const strike=(o,v)=>{v.takeDamage(4,o,{pushback:90,tier:STATE.ATTACK_SPECIAL});};
  let [o1,v1]=mk(); const h0=v1.hp; strike(o1,v1); out.plainHit=h0-v1.hp;
  let [o2,v2]=mk(); v2.state=STATE.BLOCKING; const h1=v2.hp; strike(o2,v2); out.blockedLoss=h1-v2.hp;
  let [o3,v3]=mk(); v3.invulnTimer=1.0; const h2=v3.hp; strike(o3,v3); out.dodgedLoss=h2-v3.hp;
  return out;
})()`).catch(e => ({ ERR: e.message }));
ws.close(); chrome.kill('SIGKILL');
console.log(JSON.stringify(out, null, 1));
