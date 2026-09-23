import { spawn, spawnSync } from 'node:child_process';
// HANBŌ NO KATA — Mizu's second mode. Proves the stance behaves, by driving the live
// engine, not by reading the code: toggle sets, lights turn into raps, the heavy is
// unblockable, the universal kicks survive the grip, the specials remap (ashi-barai
// trips, hane-age launches with NO vault, kaeshi catches-turns-and-expires), the mist
// falls through untouched, and dropping the stance hands the whole first form back.
// ponytail: CDP harness copied from check_mizu_invisible.mjs — one harness pattern per repo.

import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const dbg = 9339;

// A driver CHECKS the one server — it never starts its own. Find the port whose
// tree is THIS repo; anything else is someone else's build and would grade it.
let port = null;
for (const p of [9101, 9100]) {
    const who = await fetch(`http://127.0.0.1:${p}/whoami`).then(r => r.json()).catch(() => null);
    if (who && path.resolve(who.tree) === repo) { port = p; break; }
}
if (!port) {
    console.error(`no server is serving ${repo} — bind the owner's port to this tree first:`);
    console.error(`  python3 tools/serve.py <allowed port from tools/lane.py> web`);
    process.exit(1);
}

const profile = await mkdtemp(path.join(tmpdir(), 'hanbo-'));
spawnSync('pkill', ['-f', `remote-debugging-port=${dbg}`], { stdio: 'ignore' });
await new Promise(r => setTimeout(r, 800));
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    ['--headless=new', '--disable-gpu', '--no-first-run', `--remote-debugging-port=${dbg}`,
     `--user-data-dir=${profile}`, `http://127.0.0.1:${port}/`], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let page; for (let i = 0; i < 100 && !page; i++) { try { const l = await fetch(`http://127.0.0.1:${dbg}/json/list`).then(r => r.json()); page = l.find(t => t.type === 'page' && t.url.includes(String(port))); } catch {} if (!page) await sleep(100); }
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((r, j) => { ws.addEventListener('open', r, { once: true }); ws.addEventListener('error', j, { once: true }); });
let id = 1; const pend = new Map();
ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { const p = pend.get(m.id); pend.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); } });
const ev = x => new Promise((res, rej) => { const n = id++; pend.set(n, { res, rej }); ws.send(JSON.stringify({ id: n, method: 'Runtime.evaluate', params: { expression: x, awaitPromise: true, returnByValue: true } })); }).then(r => { if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text); return r.result.value; });

const out = await ev(String.raw`(async()=>{
  const wait=async(t,m)=>{for(let i=0;i<200;i++){if(t())return;await new Promise(r=>setTimeout(r,50));}throw new Error(m)};
  await wait(()=>typeof NINJA_ROSTER!=='undefined'&&typeof player1!=='undefined','engine');
  if(typeof dismissTitle==='function')try{dismissTitle();}catch(e){}
  const pick=n=>NINJA_ROSTER.findIndex(s=>s.name===n);
  gameMode='training'; if(typeof cpuMode!=='undefined')cpuMode=false;
  p1Pick=pick('Mizu'); p2Pick=pick('Kael');
  resetRound();
  const M=player1,K=player2,R={};
  // plant both on the floor directly — headless rAF timing makes loop-stepping flaky
  for(const p of [M,K]){p.y=GROUND_Y-p.height;p.vy=0;p.isGrounded=true;}
  R.grounded=M.isGrounded;
  const clear=p=>{p.recoveryTimer=0;p.recoveryTotal=0;p.state=STATE.IDLE;p.attackHasConnected=false;
    p.bufferedAttack=null;p.hitboxes.length=0;p.stunTimer=0;p.stamina=100;p.chainComboTier=0;
    p.stringT=0;p.attackAnim=null;p.kickKind=null;p.vaultAnim=false;};
  M.toggleHanbo(); R.stanceOn=M.hanbo===true;
  clear(M); M.executeAttack(STATE.ATTACK_LIGHT,null);
  R.koteFast=M.state===STATE.ATTACK_LIGHT&&M.recoveryTimer<0.30&&M.hitboxes.length>0;
  clear(M); M.executeAttack(STATE.ATTACK_HEAVY,null);
  R.makiUnblockable=!!(M.hitboxes.at(-1)?.unblockable);
  clear(M); const oD=M.isDownPressed.bind(M); M.isDownPressed=()=>true;
  M.executeAttack(STATE.ATTACK_LIGHT,'down'); R.kickSurvives=M.kickKind==='sweep';
  clear(M); M.executeAttack(STATE.ATTACK_SPECIAL,'down');
  R.ashiTrips=!!(M.hitboxes.at(-1)?.trip); M.isDownPressed=oD;
  clear(M); const oU=M.isUpPressed.bind(M); M.isUpPressed=()=>true;
  M.executeAttack(STATE.ATTACK_SPECIAL,'up');
  R.haneAge=M.hitboxes.at(-1)?.launch===true&&M.hitboxes.at(-1)?.launchVy===-380&&M.vaultAnim!==true;
  M.isUpPressed=oU;
  clear(M); const oA=M.getInputAxis.bind(M); M.getInputAxis=()=>-M.facing;
  M.executeAttack(STATE.ATTACK_SPECIAL,'back');
  R.kaeshiSets=M.kaeshiT>0&&M.kaeshiCd>0;
  const st=M.stamina; M.recoveryTimer=0;M.state=STATE.IDLE;M.attackAnim=null;
  M.executeAttack(STATE.ATTACK_SPECIAL,'back');
  R.cdRefunds=Math.abs(M.stamina-st)<0.01; M.getInputAxis=oA;
  clear(M); smokeFields.length=0; M.executeAttack(STATE.ATTACK_SPECIAL,null);
  R.mistFallsThrough=smokeFields.some(f=>f.kind==='mist'&&f.owner===M);
  clear(M);clear(K); K.x=M.x+M.width+10;K.facing=-1;M.facing=1;M.kaeshiT=0.25;
  const hp0=M.hp; M.takeDamage(12,K,{pushback:100,tier:STATE.ATTACK_HEAVY});
  R.kaeshiTurns=M.hp===hp0&&K.facing===1&&K.recoveryTimer>=0.4&&M.kaeshiT===0;
  clear(M);clear(K); K.facing=-1; const hp1=M.hp;
  M.takeDamage(12,K,{pushback:100,tier:STATE.ATTACK_HEAVY});
  R.expiredWindowLands=M.hp<hp1;
  M.toggleHanbo(); R.stanceDrops=M.hanbo===false;
  clear(M); const oU2=M.isUpPressed.bind(M); M.isUpPressed=()=>true;
  M.executeAttack(STATE.ATTACK_SPECIAL,'up'); R.vaultComesBack=M.vaultAnim===true;
  M.isUpPressed=oU2;
  return R;
})()`);

chrome.kill();
const fails = Object.entries(out).filter(([, v]) => v !== true);
for (const [k, v] of Object.entries(out)) console.log(`${v === true ? 'PASS' : 'FAIL'}  ${k}${v === true ? '' : ' = ' + JSON.stringify(v)}`);
if (fails.length) { console.error(`\n${fails.length} FAILED`); process.exit(1); }
console.log('\nHANBŌ NO KATA: all checks pass');
