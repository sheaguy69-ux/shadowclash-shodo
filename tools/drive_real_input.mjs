#!/usr/bin/env node
// Press the ACTUAL KEYS. Every other check in this repo calls executeAttack directly with
// getInputAxis/isDownPressed/isUpPressed stubbed — which proves the move works once it is
// reached, and proves nothing about whether a key press reaches it.
//
// That gap is real: fireCombatKey is the single funnel every input source passes through,
// and it has early returns in it. A move can be perfect and still be unreachable because
// the funnel ate the press first.
//
//   node tools/drive_real_input.mjs                 # oni, versus + training
//   node tools/drive_real_input.mjs --name kael
//
// Direction is set by writing the REAL `keys` map, so getInputAxis() and isDownPressed()
// run their own code rather than a stub that agrees with the test.
import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const NAME = (process.argv.includes('--name')
  ? process.argv[process.argv.indexOf('--name') + 1] : 'oni').toLowerCase();
const port = +(process.env.PORT || 9100), dbg = 9368;
const profile = await mkdtemp(path.join(tmpdir(), 'ri-'));
const who = await fetch(`http://127.0.0.1:${port}/whoami`).then(r => r.json()).catch(() => null);
if (!who) { console.error(`no server on :${port} — python3 tools/serve.py 9100 web`); process.exit(1); }
if (path.resolve(who.tree) !== path.resolve(process.cwd())) {
  console.error(`:9100 is serving ${who.tree}\nrebind: kill ${who.pid} && python3 tools/serve.py 9100 web`);
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

const ALLF = process.argv.includes('--all');
const out = await ev(String.raw`(async()=>{
 const process_all=${ALLF};
 const NM=${JSON.stringify(NAME)};
 for(let i=0;i<400;i++){
   if(typeof NINJA_ROSTER!=='undefined' && typeof startNewGame==='function'
      && typeof fireCombatKey==='function' && typeof SPRITES!=='undefined'
      && SPRITES[NM] && SPRITES[NM].ready) break;
   await new Promise(r=>setTimeout(r,50));
 }
 const ALL = process_all;
 const picks = ALL ? NINJA_ROSTER.map((_,i)=>i)
                   : [NINJA_ROSTER.findIndex(s=>s.name.toLowerCase()===NM)];
 if(picks[0]<0) return {fatal:'not on the roster: '+NM};

 // P1 keys, straight out of fireCombatKey: W jump, F light, G heavy, H special.
 const PRESS = { Light:'KeyF', Heavy:'KeyG', Special:'KeyH' };
 const HOLD  = { neutral:[], fwd:['KeyD'], back:['KeyA'], down:['KeyS'], up:['KeyW'] };

 const results = {};
 for (const idx of picks) {
  const who = NINJA_ROSTER[idx].name;
  for (const mode of ['versus','training']) {
   gameMode = mode; p1Pick = idx; p2Pick = idx===0?1:0;
   try { startNewGame(); } catch(e) { results[who+'|'+mode] = {fatal:e.message.slice(0,80)}; continue; }
   const man = SPRITES[who.toLowerCase()];
   const byIdx = {};
   if (man && man.frames) for (const [k,i] of Object.entries(man.frames)) (byIdx[i]||=[]).push(k);
   const famOf = i => { const s2=new Set(); for(const k of (byIdx[i]||[])){const m=k.match(/^([a-z_]+?)\d+$/); s2.add(m?m[1]:k);} return [...s2]; };
   roundIntroTimer = 0; paused = false; hitstopRemaining = 0;
   const rows = [];
   for (const [tier, code] of Object.entries(PRESS)) {
     for (const [dir, held] of Object.entries(HOLD)) {
       // a clean fighter every press — no carried recovery, no stale chain
       for (const k in keys) keys[k] = false;
       const p = player1;
       p.x = 200; p.facing = 1;
       p.isGrounded = true; p.attackAir = false; p.vy = 0;
       p.state = STATE.IDLE; p.attackT = 0; p.lock = 0; p.recoveryTimer = 0;
       p.stunTimer = 0; p.rollTimer = 0; p.rollRecover = 0; p.sayaLock = 0;
       p.chainComboTier = 0; p.dashTimer = 0; p.chakra = 100; p.stamina = 100;
       p._lt = p._ht = -1e9;
       p.wireBind = 0; p.wireConv = null;
       if (player2) { player2.x = 290; player2.isGrounded = true; }
       for (const k of held) keys[k] = true;

       const before = p.kageActs.length;
       const st0 = p.state;
       let err = null;
       // ⛔ THE REAL FUNNEL. Not executeAttack — fireCombatKey, the one every keyboard,
       // touch and mouse press goes through, early returns and all.
       try { fireCombatKey(code); } catch(e) { err = e.message.slice(0,70); }
       const box = p.kageActs.length - before;
       const st1 = Object.keys(STATE).find(k=>STATE[k]===p.state) || '?';
       const moved = p.state !== st0;
       // what does it DRAW — so two buttons sharing one animation is visible, which is
       // the owner's other complaint and is invisible to a "did it fire" check
       let drew = '-';
       try {
         if (man && man.ready) {
           const fams = new Set();
           for (let s2=0; s2<14; s2++) {
             if (p.attackAnim) p.attackAnim.start = animClock*1000 - (s2/14)*p.attackAnim.dur*0.99;
             else p.attackT = (s2/14)*0.4;
             for (const f of famOf(spriteFrameIndex(p, man.frames))) fams.add(f);
           }
           drew = [...fams].filter(f=>!['idle','stand','run_clean'].includes(f)).join(',') || '-';
         }
       } catch(e) {}
       rows.push({ tier, dir, code, box, state: st1, drew, acted: box>0 || moved, err });
       for (const k in keys) keys[k] = false;
     }
   }
   results[who+'|'+mode] = { rows };
  }
 }
 return { results, all: ALL };
})()`);
ws.close(); chrome.kill('SIGKILL');

if (out.fatal) { console.error(out.fatal); process.exit(2); }

// ---- DEAD INPUTS: a press that produced neither a hitbox nor a state change ----
const rows = [];
for (const [key, r] of Object.entries(out.results)) {
  const [who, mode] = key.split('|');
  if (r.fatal) { rows.push({ who, mode, fatal: r.fatal }); continue; }
  for (const x of r.rows) rows.push({ who, mode, ...x });
}
const dead = rows.filter(r => !r.fatal && !r.acted);
const fatals = rows.filter(r => r.fatal);

console.log('\n  REAL-KEY AUDIT — every press through fireCombatKey, both modes\n');
console.log(`  ${rows.filter(r=>!r.fatal).length} presses driven across ` +
            `${new Set(rows.map(r=>r.who)).size} fighter(s)\n`);

// a press alive in versus and dead in training is the funnel eating it as a hotkey
const alive = {};
for (const r of rows) if (!r.fatal) alive[`${r.who}|${r.mode}|${r.dir}+${r.tier}`] = r.acted;
const eaten = [];
for (const k of Object.keys(alive)) {
  const [who, mode, inp] = k.split('|');
  if (mode !== 'versus' || !alive[k]) continue;
  if (alive[`${who}|training|${inp}`] === false) eaten.push(`${who} ${inp}`);
}

if (dead.length) {
  console.log(`  ⛔ DEAD INPUTS (${dead.length}) — key pressed, nothing happened:`);
  for (const d of dead) console.log(`     ${d.who.padEnd(12)} ${d.mode.padEnd(9)} ${(d.dir+' + '+d.tier).padEnd(18)} ${d.code}`);
  console.log('');
} else console.log('  \u2713 no dead inputs\n');

if (eaten.length) {
  console.log(`  \u26d4 EATEN BY A TRAINING HOTKEY (${eaten.length}) — works in versus, dead in training:`);
  for (const e of eaten) console.log(`     ${e}`);
  console.log('     A training hotkey that reuses a combat key returns before the attack');
  console.log('     dispatch. P1 owns W/F/G/H/C/V; P2 owns ArrowUp/I/O/P/M/K.\n');
}

// ---- SHARED FRAMES: two different inputs playing the same animation ----
console.log('  SHARED ANIMATIONS — one row of art on more than one button:\n');
let shareCount = 0;
for (const who of [...new Set(rows.map(r => r.who))]) {
  const mine = rows.filter(r => r.who === who && r.mode === 'versus' && !r.fatal && r.drew && r.drew !== '-');
  const byFam = {};
  for (const r of mine) (byFam[r.drew] ||= []).push(`${r.dir}+${r.tier}`);
  const shared = Object.entries(byFam).filter(([, v]) => v.length > 1);
  if (!shared.length) continue;
  console.log(`  ${who}`);
  for (const [fam, inputs] of shared) {
    shareCount++;
    console.log(`     ${fam.padEnd(22)} <- ${inputs.join(' , ')}`);
  }
}
if (!shareCount) console.log('     none');

const bad = dead.length + fatals.length;
console.log(`\n  ${bad ? bad + ' dead' : 'no dead inputs'} \u00b7 ${shareCount} shared-animation collision(s)`);
process.exit(bad ? 1 : 0);
