#!/usr/bin/env node
// probe_key_reads.mjs — WHICH FRAME KEYS does the engine ask a fighter's sheet for,
// per state and per real key press? The 672 fallback repointed all 237 Oni keys at 8
// cells, so famOf(cellIndex) says "everything" and moveset_probe is blind. This logs
// the KEY NAMES read through a Proxy over SPRITES.<name>.frames — cell-agnostic, so
// it works on a doll sheet. Reads are truthful: missing keys stay undefined, gated
// branches behave exactly as live.
//
//   PORT=9101 node tools/probe_key_reads.mjs --name oni
import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const NAME = (process.argv.includes('--name')
  ? process.argv[process.argv.indexOf('--name') + 1] : 'oni').toLowerCase();
const port = +(process.env.PORT || 9101), dbg = 9371;
const who = await fetch(`http://127.0.0.1:${port}/whoami`).then(r => r.json()).catch(() => null);
if (!who) { console.error(`no server on :${port}`); process.exit(1); }
if (path.resolve(who.tree) !== path.resolve(process.cwd())) {
  console.error(`:${port} serves ${who.tree}, not this tree`); process.exit(1);
}
const profile = await mkdtemp(path.join(tmpdir(), 'kr-'));
spawnSync('pkill', ['-f', `remote-debugging-port=${dbg}`], { stdio: 'ignore' });
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ['--headless=new', '--disable-gpu', '--no-first-run', `--remote-debugging-port=${dbg}`,
   `--user-data-dir=${profile}`, `http://127.0.0.1:${port}/`], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let page;
for (let i = 0; i < 200 && !page; i++) {
  try {
    const l = await fetch(`http://127.0.0.1:${dbg}/json/list`).then(r => r.json());
    page = l.find(t => t.type === 'page' && t.url.includes(String(port)));
  } catch {}
  if (!page) await sleep(150);
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
 const NM=${JSON.stringify(NAME)};
 for(let i=0;i<600;i++){
   if(typeof NINJA_ROSTER!=='undefined'&&typeof startNewGame==='function'
      &&typeof SPRITES!=='undefined'&&SPRITES[NM]&&SPRITES[NM].ready) break;
   await new Promise(r=>setTimeout(r,50));
 }
 const idx=NINJA_ROSTER.findIndex(s=>s.name.toLowerCase()===NM);
 if(idx<0) return {fatal:'not on roster'};
 gameMode='versus'; p1Pick=idx; p2Pick=idx===0?1:0;
 startNewGame();
 roundIntroTimer=0; paused=false; hitstopRemaining=0;
 let p=player1; const man=SPRITES[NM];
 let log=null;
 const prox=new Proxy(man.frames,{
   get:(t,k)=>{ if(log&&typeof k==='string') log.add(k); return t[k]; },
   has:(t,k)=>{ if(log&&typeof k==='string') log.add(k); return k in t; }
 });
 const base=()=>{ for(const k in keys) keys[k]=false;
   p.x=300;p.facing=1;p.isGrounded=true;p.attackAir=false;p.vy=0;p.vx=0;
   p.state=STATE.IDLE;p.attackT=0;p.attackAnim=null;p.lock=0;p.recoveryTimer=0;
   p.stunTimer=0;p.rollTimer=0;p.rollRecover=0;p.dashTimer=0;p.chakra=100;p.stamina=100;
   p.chainComboTier=0;p.stringStep=0;p._lt=p._ht=-1e9;p.wireBind=0;p.wireConv=null;
   p.lungeAnim=p.whipAnim=p.spinAnim=false;p.dashAtkAnim=false;p.moveArt=null;
   p.flooredT=0;p.tumbleT=0;p.landT=0;p.wallJumpLock=0;p.wallThrowT=0;p.grabbedBy=null;
   p.slamPhase=0;p.slamRecover=0;p.athrowAnim=false;p.airUpAnim=false;p.upAtkAnim=false;
   if(player2){player2.x=390;player2.isGrounded=true;} };
 const sample=(n)=>{ for(let s=0;s<(n||14);s++){
     if(p.attackAnim) p.attackAnim.start=animClock*1000-(s/14)*p.attackAnim.dur*0.99;
     else p.attackT=(s/14)*0.5;
     try{ spriteFrameIndex(p,prox); }catch(e){ log.add('ERR:'+e.message.slice(0,40)); }
 } };
 const R={};
 const scen=(label,fn,n)=>{ base(); log=new Set(); try{ fn(); }catch(e){ log.add('SETUPERR:'+e.message.slice(0,40)); } sample(n); R[label]=[...log].sort(); log=null; };

 // ---- states ----
 scen('idle',()=>{});
 scen('run.fwd',()=>{ p.state=STATE.RUN; p.vx=200; p.animPhase=3; });
 scen('run.back',()=>{ p.state=STATE.RUN; p.vx=-200; p.animPhase=3; });
 scen('crouch',()=>{ p.state=STATE.CROUCH; p.crouchAt=animClock-0.02; });
 scen('crouch.held',()=>{ p.state=STATE.CROUCH; p.crouchAt=animClock-5; });
 scen('roll.through',()=>{ p.state=STATE.ROLL; p.rollAway=false; p.rollTimer=0.14; });
 scen('roll.away',()=>{ p.state=STATE.ROLL; p.rollAway=true; p.rollTimer=0.14; });
 scen('dash.window',()=>{ p.dashTimer=0.10; });
 scen('jump.neutral',()=>{ p.state=STATE.JUMP; p.isGrounded=false; p.jumpDir=null; p.vy=-350; });
 scen('jump.fwd',()=>{ p.state=STATE.JUMP; p.isGrounded=false; p.jumpDir='fwd'; p.vy=-100; });
 scen('jump.back',()=>{ p.state=STATE.JUMP; p.isGrounded=false; p.jumpDir='back'; p.vy=-100; });
 scen('jump.fall',()=>{ p.state=STATE.JUMP; p.isGrounded=false; p.vy=400; });
 scen('walljump.lock',()=>{ p.state=STATE.JUMP; p.isGrounded=false; p.wallJumpLock=0.1; p.vy=-300; });
 scen('wall.cling',()=>{ p.state=STATE.WALL_CLING; p.isGrounded=false; p.vy=80; });
 scen('wall.throw',()=>{ p.state=STATE.WALL_CLING; p.isGrounded=false; p.wallThrowT=0.3; });
 scen('block',()=>{ p.state=STATE.BLOCKING; });
 scen('block.push',()=>{ p.state=STATE.BLOCKING; p.blockPushTimer=0.1; });
 scen('block.hit',()=>{ p.state=STATE.BLOCKING; p.blockedAt=animClock-0.05; });
 scen('stun.deep',()=>{ p.state=STATE.STUNNED; p.stunTimer=0.35; p.stunPeak=0.4; });
 scen('stun.mid',()=>{ p.state=STATE.STUNNED; p.stunTimer=0.2; p.stunPeak=0.4; });
 scen('stun.tail',()=>{ p.state=STATE.STUNNED; p.stunTimer=0.05; p.stunPeak=0.4; });
 scen('stun.air',()=>{ p.state=STATE.STUNNED; p.isGrounded=false; p.vy=-200; p.stunTimer=0.3; });
 scen('stun.floored',()=>{ p.state=STATE.STUNNED; p.flooredT=0.5; });
 scen('stun.tumble',()=>{ p.state=STATE.STUNNED; p.tumbleT=0.3; p.tumbleT0=0.5; });
 scen('land',()=>{ p.landT=0.08; });
 scen('parry',()=>{ p.state=STATE.PARRY_STANCE; p.parryFlashTimer=0.1; });
 scen('throwing',()=>{ p.state=STATE.THROWING; p.throwTimer=THROW_TIME*0.5; });
 scen('thrown',()=>{ p.state=STATE.THROWN; p.grabbedBy=player2; if(player2)player2.throwTimer=THROW_TIME*0.5; });
 scen('wire.bind',()=>{ p.wireBind=0.3; });
 for(const cv of ['katana','knives','slice','claw'])
   scen('wire.conv.'+cv,()=>{ p.state=STATE.ATTACK_SPECIAL; p.wireConv=cv;
     p.attackAnim={start:animClock*1000,dur:400}; });
 scen('lunge',()=>{ p.state=STATE.ATTACK_LIGHT; p.lungeAnim=true; p.attackAnim={start:animClock*1000,dur:300}; });
 scen('whip',()=>{ p.state=STATE.ATTACK_SPECIAL; p.whipAnim=true; p.attackAnim={start:animClock*1000,dur:300}; });
 scen('aspin',()=>{ p.state=STATE.ATTACK_SPECIAL; p.spinAnim=true; p.attackAnim={start:animClock*1000,dur:300}; });

 // ---- real key presses, ground + air, all tiers/dirs ----
 const PRESS={Light:'KeyF',Heavy:'KeyG',Special:'KeyH'};
 const HOLD={neutral:[],fwd:['KeyD'],back:['KeyA'],down:['KeyS'],up:['KeyW']};
 for(const where of ['ground','air']){
  for(const [tier,code] of Object.entries(PRESS)){
   for(const [dir,held] of Object.entries(HOLD)){
     // the live loop ran through the state scenarios above — round may be over, a
     // fighter dead. Fresh match per press, like drive_real_input does per mode.
     try{ startNewGame(); }catch(e){}
     roundIntroTimer=0; paused=false; hitstopRemaining=0;
     p=player1;   // startNewGame rebuilds the players — the old ref is a corpse
     base();
     if(where==='air'){ p.isGrounded=false; p.vy=-120; p.y-=80; }
     for(const k of held) keys[k]=true;
     log=new Set();
     try{ fireCombatKey(code); }catch(e){ log.add('FIREERR:'+e.message.slice(0,40)); }
     const st=Object.keys(STATE).find(k=>STATE[k]===p.state)||'?';
     sample(14);
     // slam outlives attackAnim — walk its phases too
     if(p.slamPhase||p.slamRecover>0){ p.slamPhase=1;p.slamTimer=0.2;sample(2);
       p.slamPhase=2;sample(2);p.slamPhase=0;p.slamRecover=0.25;sample(2);p.slamRecover=0.05;sample(2); }
     R[where+'.'+dir+'+'+tier]=['state:'+st,...[...log].sort()];
     log=null;
   }
  }
 }
 return {sheet_v:typeof SHEET_V!=='undefined'?SHEET_V:null,results:R};
})()`);
ws.close(); chrome.kill('SIGKILL');
if (out.fatal) { console.error(out.fatal); process.exit(2); }
console.log(JSON.stringify(out, null, 1));
