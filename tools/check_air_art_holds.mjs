#!/usr/bin/env node
// AN AIR ATTACK MUST KEEP ITS AIR ART UNTIL ITS RECOVERY ENDS.
//
// p.attackAir is the PRESS-TIME latch; p.isGrounded is LIVE. A draw-path branch that reads
// the live flag repaints a swing that is already in the air the moment the feet touch — the
// player sees the pose change halfway through one move. Three of these were fixed at
// SHEET_V 711; that pass MISSED Kael's two and the shared MEDIUM board, which is exactly
// why this check exists: it presses in the air, lands the fighter WITHOUT a new press, and
// compares the drawn cell family on both sides of the landing.
//
//   PORT=9101 node tools/check_air_art_holds.mjs
import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const port = +(process.env.PORT || 9101), dbg = 9371;
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
const profile = await mkdtemp(path.join(tmpdir(), 'aah-'));
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ['--headless=new', '--disable-gpu', '--no-first-run', `--remote-debugging-port=${dbg}`,
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

const out = await ev(String.raw`(async()=>{
 // WAIT FOR THE SHEETS, not just the symbols. SPRITES exists long before any PNG has
 // decoded, and a sheet that is merely present has no .frames — which read as "no sheet"
 // for all nine and still let the run report a clean pass.
 for(let i=0;i<600;i++){
   const up = typeof NINJA_ROSTER!=='undefined' && typeof startNewGame==='function'
      && typeof fireCombatKey==='function' && typeof SPRITES!=='undefined';
   if (up && NINJA_ROSTER.every(s2 => { const m = SPRITES[s2.name.toLowerCase()];
                                        return m && m.ready && m.frames; })) break;
   await new Promise(r=>setTimeout(r,50));
 }
 // P1 attack keys straight out of fireCombatKey.
 const PRESS = { Light:'KeyF', Medium:'KeyJ', Heavy:'KeyG', Special:'KeyH' };
 const rows = [];
 for (let idx=0; idx<NINJA_ROSTER.length; idx++) {
  const who = NINJA_ROSTER[idx].name;
  gameMode='versus'; p1Pick=idx; p2Pick = idx===0?1:0;
  try { startNewGame(); } catch(e) { rows.push({who,tier:'-',err:e.message.slice(0,60)}); continue; }
  const man = SPRITES[who.toLowerCase()];
  if (!man || !man.frames) { rows.push({who,tier:'-',err:'no sheet'}); continue; }
  const byIdx={}; for (const [k,i] of Object.entries(man.frames)) (byIdx[i]||=[]).push(k);
  const famOf = i => { const s=new Set(); for(const k of (byIdx[i]||[])){const m=k.match(/^([a-z_]+?)\d+$/); s.add(m?m[1]:k);} return [...s]; };
  const draw = p => { const f=new Set();
    for (let s=0;s<12;s++){
      if (p.attackAnim) p.attackAnim.start = animClock*1000 - (s/12)*p.attackAnim.dur*0.99;
      else p.attackT = (s/12)*0.4;
      for (const x of famOf(spriteFrameIndex(p, man.frames))) f.add(x);
    }
    return [...f].sort().join(',') || '-'; };
  roundIntroTimer=0; paused=false; hitstopRemaining=0;
  for (const [tier,code] of Object.entries(PRESS)) {
    for (const k in keys) keys[k]=false;
    const p = player1;
    p.x=300; p.facing=1; p.state=STATE.IDLE; p.attackT=0; p.lock=0;
    p.recoveryTimer=0; p.stunTimer=0; p.rollTimer=0; p.rollRecover=0; p.sayaLock=0;
    p.chainComboTier=0; p.dashTimer=0; p.chakra=100; p.stamina=100; p._lt=p._ht=-1e9;
    // PRESS IT IN THE AIR.
    p.isGrounded=false; p.y = GROUND_Y - p.height - 120; p.vy = -80; p.attackAir=true;
    if (player2) { player2.x=420; }
    let err=null;
    try { fireCombatKey(code); } catch(e) { err=e.message.slice(0,60); }
    const air = draw(p);
    const latch = !!p.attackAir, rec = +(p.recoveryTimer||0).toFixed(2);
    // ...NOW LAND. No new press, no state reset: exactly what happens when a short hop
    // ends before the swing's recovery does.
    p.isGrounded=true; p.y = GROUND_Y - p.height; p.vy=0;
    const land = draw(p);
    // air->land: the move began airborne, so the art must NOT change when the feet land.
    rows.push({ dir:'air->land', who, tier, air, land, latch, rec, err, bad: air!==land,
                why: air!==land ? 'repainted mid-swing' : '' });

    // THE OTHER DIRECTION. Press it standing, then get LAUNCHED (a juggle, a trip, a
    // launcher hit) before recovery ends. A latch-only fix passes the test above and
    // still paints a planted, floor-shadowed ground beat in mid-air here — which is the
    // owner's 2026-09-03 ruling, the opposite failure. Both must hold.
    for (const k in keys) keys[k]=false;
    p.state=STATE.IDLE; p.attackT=0; p.recoveryTimer=0; p.stunTimer=0;
    p.chainComboTier=0; p.chakra=100; p.stamina=100; p._lt=p._ht=-1e9;
    p.isGrounded=true; p.y = GROUND_Y - p.height; p.vy=0; p.attackAir=false;
    let err2=null;
    try { fireCombatKey(code); } catch(e) { err2=e.message.slice(0,60); }
    const gnd = draw(p);
    // ⛔ IS THIS EVEN REACHABLE? Forcing isGrounded=false proves nothing if no real move
    // can leave the floor mid-swing — that is how this session has repeatedly "fixed"
    // states the game cannot produce. So run the REAL update loop for the whole recovery
    // and record whether the fighter genuinely goes airborne while the attack is still up.
    let selfAir = false;
    try {
      const st = p.state;
      for (let f=0; f<40; f++) {
        p.update(1/60, player2);
        if (!p.isGrounded && p.state === st) { selfAir = true; break; }
        if (p.state !== st) break;
      }
    } catch(e) {}
    p.isGrounded=false; p.y = GROUND_Y - p.height - 130; p.vy=-260;
    const flown = draw(p);
    // gnd->air: the OPPOSITE verdict. Owner ruling 2026-09-03 — airborne must never draw
    // a grounded beat — so here the art is REQUIRED to change. Staying put is the failure.
    rows.push({ dir:'gnd->air', who, tier, air:gnd, land:flown, latch:!!p.attackAir,
                rec:+(p.recoveryTimer||0).toFixed(2), err:err2, selfAir,
                // Airborne must draw the AIR body — so the test is against the air-pressed
                // art, not "did it change". Shin's neutral Special leaves the floor by
                // design and already draws aneu standing; holding aneu is correct, and
                // comparing to gnd alone called that a defect.
                bad: selfAir && flown !== air,
                why: !selfAir ? 'not reachable — no real move leaves the floor mid-swing'
                     : flown !== air ? 'REACHABLE and wrong: airborne draws ' + flown + ', air press draws ' + air : '' });
  }
 }
 return rows;
})()`);
ws.close(); chrome.kill('SIGKILL');

console.log('\n  A SWING KEEPS ONE BODY OF ART — both directions across the floor line\n' +
            '  air->land : pressed airborne, landed mid-recovery (must not become ground art)\n' +
            '  gnd->air  : pressed standing, launched mid-recovery (must not stay ground art)\n');
// ⛔ AN ERROR IS A FAILURE, NOT A PASS. The first run of this check reported
// "none swapped" while all nine rows had errored out with no sheet loaded.
const errs = out.filter(r => r.err);
const bad = out.filter(r => r.bad);
for (const r of out) {
  if (r.err) { console.log(`  ${r.who.padEnd(12)} ${String(r.tier).padEnd(8)} ERR ${r.err}`); continue; }
  const mark = r.bad ? '⛔' : ' ✓';
  const tail = `  ${r.air}` + (r.air !== r.land ? `  ->  ${r.land}` : '  (held)') + (r.why ? `   ${r.why}` : '');
  if (r.bad || process.argv.includes('-v'))
    console.log(`  ${mark} ${r.who.padEnd(12)} ${String(r.tier).padEnd(8)} ${String(r.dir).padEnd(10)} rec=${r.rec}s${tail}`);
}
console.log(`\n  ${out.length} air presses across ${new Set(out.map(r=>r.who)).size} fighters` +
            ` · ${bad.length ? bad.length + ' WRONG' : 'all correct'}` +
            `${errs.length ? ' · ' + errs.length + ' ERRORED (this is a FAILURE, not a pass)' : ''}`);
process.exit(bad.length + errs.length ? 1 : 0);
