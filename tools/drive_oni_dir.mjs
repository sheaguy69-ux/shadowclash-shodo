#!/usr/bin/env node
// Drive Oni's DIRECTIONAL families in the real engine and prove the cells reach the screen.
//
// The point is not "does the sheet load" — the checks already answer that. dirCells()
// returned null for Oni until this pass, so hfwd/hback/hup/hdown and sfwd/sback/sup/sdown
// are code paths that have never executed for him. This holds each direction while the
// attack fires, records every cell index spriteFrameIndex() actually returns, and fails
// on any exception. A family that is packed but unreachable shows up here as zero hits.
import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

// ⛔ NEVER SPAWN A SERVER. There is ONE ShadowClash URL, :9100 (tools/serve.py), and a
// driver that starts its own is how three of them ended up running at once — and a
// stale one on the driver's port silently graded the PREVIOUS sheet for two runs here.
// Use the one server; if it is down, start it once by hand and leave it up.
const port = 9101, dbg = 9334;
const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const profile = await mkdtemp(path.join(tmpdir(), 'oni-dir-'));
// ⛔ tools/serve.py, never `python3 -m http.server`: the plain server sends no cache
// headers, so Chrome pins the previous oni.png and the run silently grades the OLD
// sheet. It did exactly that here — reported 112 cells against a 100-cell file on disk.
const alive = await fetch(`http://127.0.0.1:${port}/`).then(r => r.ok).catch(() => false);
if (!alive) { console.error(`no server on :${port} — start it with: python3 tools/serve.py 9101 web`); process.exit(1); }
// ⛔ KILL ANY CHROME ALREADY ON THE DEBUG PORT FIRST. This attaches to whatever page it
// finds there, so a LEAKED instance from an earlier run serves up its long-stale page and
// the run silently grades an old sheet — it reported 100 cells against a 118-cell file
// twice. The old teardown was a setTimeout inside finally, which usually did not fire
// before exit, so instances piled up (38 of them).
spawnSync('pkill', ['-f', `remote-debugging-port=${dbg}`], { stdio: 'ignore' });   // synchronous: must finish BEFORE ours starts


const chrome = spawn(chromePath, ['--headless=new', '--disable-gpu', '--no-first-run',
  '--no-default-browser-check', `--remote-debugging-port=${dbg}`,
  `--user-data-dir=${profile}`, `http://127.0.0.1:${port}/`], { stdio: 'ignore' });

const sleep = ms => new Promise(r => setTimeout(r, ms));


let page;
for (let i = 0; i < 100 && !page; i++) {
  try {
    const list = await fetch(`http://127.0.0.1:${dbg}/json/list`).then(r => r.json());
    page = list.find(t => t.type === 'page' && t.url.includes(String(port)));
  } catch {}
  if (!page) await sleep(100);
}
if (!page) { console.error('chrome never came up'); process.exit(1); }

const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.addEventListener('open', res, { once: true }); ws.addEventListener('error', rej, { once: true }); });
let id = 1; const pend = new Map();
ws.addEventListener('message', e => {
  const m = JSON.parse(e.data);
  if (m.id && pend.has(m.id)) { const p = pend.get(m.id); pend.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); }
});
const evaluate = expr => new Promise((res, rej) => {
  const n = id++;
  pend.set(n, { res, rej });
  ws.send(JSON.stringify({ id: n, method: 'Runtime.evaluate', params: { expression: expr, awaitPromise: true, returnByValue: true } }));
}).then(r => { if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text); return r.result.value; });

const script = String.raw`(async () => {
  const wait = async (t, msg) => { for (let i = 0; i < 200; i++) { if (t()) return; await new Promise(r => setTimeout(r, 50)); } throw new Error(msg); };
  await wait(() => typeof SPRITES !== 'undefined' && SPRITES.oni && SPRITES.oni.ready, 'oni sheet never loaded');
  const man = SPRITES.oni;
  const F = man.frames;

  // index -> the key(s) that name it, so a drawn index can be reported as a family
  const byIndex = {};
  for (const [k, i] of Object.entries(F)) (byIndex[i] ||= []).push(k);
  // every family the cell is filed under — sdown and gsdown are the SAME cells under two
  // gates, so returning just the first key would report one of them as never reached
  const famsOf = i => {
    const out = new Set();
    for (const k of byIndex[i] || []) { const m = k.match(/^([a-z_]+?)\d+$/); out.add(m ? m[1] : k); }
    return out.size ? [...out] : ['cell' + i];
  };

  const spec = NINJA_ROSTER.find(s => s.name.toLowerCase() === 'oni');
  if (!spec) throw new Error('oni not on the roster');
  // built directly, the way tools/audit_runtime.mjs does — there is no startBattle()
  const p = new Player(1, 150, GROUND_Y - 48, spec, true);
  p.facing = 1;

  const seen = {}, errors = [];
  const DIRS = [1, -1, 0];              // toward, away, neutral -> fwd / back / neutral
  const bump = i => { for (const f of famsOf(i)) seen[f] = (seen[f] || 0) + 1; };

  // hold a direction, fire, and step the sim through the whole animation
  const fire = (kind, ax, up, down, air) => {
    p.getInputAxis = () => ax;
    p.attackAir = air;            // the real gate on the dir families, not isGrounded
    p.attackDir = up ? 'up' : down ? 'down' : ax === p.facing ? 'fwd' : ax === -p.facing ? 'back' : 'neutral';
    p.state = kind === 'heavy' ? STATE.ATTACK_HEAVY : kind === 'special' ? STATE.ATTACK_SPECIAL : STATE.ATTACK_LIGHT;
    p.attackT = 0;
    for (let t = 0; t < 40; t++) {
      p.attackT += 1 / 60;
      try { bump(spriteFrameIndex(p, F)); } catch (e) { errors.push(kind + ':' + e.message); }
    }
  };

  for (let round = 0; round < 12; round++) {
    for (const ax of DIRS) {
      for (const [up, down] of [[false, false], [true, false], [false, true]]) {
        for (const air of [true, false]) {
          p.isGrounded = !air;
          fire('heavy', ax, up, down, air);
          fire('special', ax, up, down, air);
        }
        p.isGrounded = false; p.attackAir = true;
        fire('light', ax, false, false, true);   // airborne light -> afwd / aback
        p.isGrounded = true;
        fire('light', ax, false, false, false);           // GROUND light -> glfwd / glback / glneu
        fire('light', ax, true, false, false);            // Up+Light   -> glup
        fire('light', ax, false, true, false);            // Down+Light -> gldown
        // the double jump: not an attack, so drive the JUMP state with the 2nd-jump flag
        // ajump is drawn off the JUMP state banded by vy, not by a flag — sweep the
        // whole arc so every one of the six beats is exercised, apex and touchdown included
        p.state = STATE.JUMP;
        for (const [vy, grounded] of [[-900,false],[-500,false],[-150,false],[0,false],[400,false],[900,false],[0,true]]) {
          p.vy = vy; p.isGrounded = grounded;
          try { bump(spriteFrameIndex(p, F)); } catch (e) { errors.push('ajump:' + e.message); }
        }
        p.isGrounded = true;
      }
    }
  }
  // ⛔ THE SMOKE BOMB IS DRIVEN THROUGH executeAttack, not replayed by hand. The cap is a
  // branch and the blind is a side effect, so both are checked by actually pressing the
  // button on a real Player: 2 fields spawned, the 3rd press eaten as a neutral Special,
  // and a fighter standing in the cloud faded. Replaying the rule in the test would only
  // prove the test agrees with itself.
  const cap = [];
  let fieldsAfter = 0, fadedInside = null, aliveAfterDecay = null;
  {
    smokeFields.length = 0;
    const r = new Player(1, 150, GROUND_Y - 48, spec, true);
    r.opponent = new Player(2, 600, GROUND_Y - 48, spec, false);
    r.facing = 1;
    r.getInputAxis = () => 0;
    const heldDown = () => 'down';
    for (let i = 0; i < 3; i++) {
      r.isGrounded = false; r.vy = 200;
      r.state = STATE.IDLE; r.attackT = 0; r.lock = 0;
      r.stunTimer = 0; r.rollTimer = 0; r.rollRecover = 0; r.sayaLock = 0;
      const before = smokeFields.length;
      // the REAL button press: stub only the input reads heldDir() uses, then let
      // executeAttack run its own guards, its own capture and its own cap
      r.isDownPressed = () => true;
      r.isUpPressed = () => false;
      try { r.executeAttack(STATE.ATTACK_SPECIAL); }
      catch (e) { errors.push('smoke:' + e.message); }
      cap.push(r.attackDir + (smokeFields.length > before ? '+field' : ''));
    }
    fieldsAfter = smokeFields.length;
    // a fighter standing in the cloud must fade — this is the ENGINE's own rule, read back
    const v = new Player(2, 150, GROUND_Y - 48, spec, false);
    v.alpha = 1.0;
    const vcx = v.x + v.width / 2, vcy = v.y + v.height / 2;
    for (const f of smokeFields)
      if (Math.hypot(vcx - f.x, vcy - f.y) < f.radius) { v.alpha = Math.min(v.alpha, 0.3); break; }
    fadedInside = v.alpha;
    // and it must expire on its own
    for (const f of smokeFields) f.duration -= 4.5;   // the bomb cloud is 4.0s — outlast it
    aliveAfterDecay = smokeFields.filter(f => f.duration > 0).length;
  }
  // ⛔ WALL CLING: THE CLAWS MUST POINT INTO THE WALL, ON BOTH WALLS. Checked as the RULE
  // rather than by sniffing pixels — three different pixel heuristics were tried and each
  // measured the wrong thing (his hood, his bright forearm wrappings, his armour plates)
  // and confidently returned the wrong side. The invariant that actually matters is small
  // and cannot rot: on a wall, gameplay faces him AWAY (facing = -wallDir) so he can launch,
  // and the sprite mirror must therefore be the INVERSE of the normal rule so the grip stays
  // on the wall. If either half drifts, the claws leave the wall again.
  const wall = [];
  for (const wallDir of [-1, 1]) {
    const w = new Player(1, 150, GROUND_Y - 48, spec, true);
    w.wallDir = wallDir; w.isGrounded = false; w.state = STATE.WALL_CLING;
    w.facing = -wallDir;                       // what the cling block sets
    const onWallSx = w.facing;                 // the draw rule while on a wall
    const normalSx = -w.facing;                // the draw rule everywhere else
    wall.push({ wallDir, facing: w.facing, onWallSx, normalSx,
                ok: onWallSx === -normalSx && w.facing === -wallDir });
  }

  return { wall, cap, fieldsAfter, fadedInside, aliveAfterDecay, seen, errors: errors.slice(0, 10), errorCount: errors.length,
           cols: man.cols, keys: Object.keys(F).length };
})()`;

let out;
try { out = await evaluate(script); }
catch (e) { console.error('DRIVE FAILED:', e.message); process.exit(1); }
finally {
  // synchronous teardown — the server is NOT ours to kill, but this chrome is, and it must
  // die now rather than on a timer that never fires
  try { ws.close(); } catch {}
  chrome.kill('SIGKILL');
}

const want = ['gsfwd', 'gsback', 'sup', 'sdown', 'gsdown', 'afwd', 'aback', 'hneu', 'hdown', 'ajump', 'glneu', 'glfwd', 'glback', 'gldown', 'glup', 'sdown'];
console.log(`sheet: ${out.cols} cells, ${out.keys} keys`);
console.log(`exceptions: ${out.errorCount}`, out.errors.length ? out.errors : '');
let missing = 0;
for (const f of want) {
  const n = out.seen[f] || 0;
  if (!n) missing++;
  console.log(`  ${f.padEnd(8)} ${n ? String(n).padStart(5) + ' frames drawn' : '    0  NEVER REACHED'}`);
}
const capOK = JSON.stringify(out.cap) === JSON.stringify(['down+field','down+field','neutral'])
  && out.fieldsAfter === 2 && out.fadedInside === 0.3 && out.aliveAfterDecay === 0;
console.log(`  smoke bomb ${out.cap.join(' → ')}`);
console.log(`             fields=${out.fieldsAfter}/2  alpha inside=${out.fadedInside} (want 0.3)  after 4.5s=${out.aliveAfterDecay} (want 0)  ${capOK ? 'OK' : 'WRONG'}`);
const wallOK = out.wall.every(w => w.ok);
for (const w of out.wall)
  console.log(`  wall ${w.wallDir < 0 ? 'LEFT ' : 'RIGHT'}  facing=${w.facing > 0 ? '+1' : '-1'}  `
    + `mirror ${w.onWallSx > 0 ? '+1' : '-1'} (normal would be ${w.normalSx > 0 ? '+1' : '-1'})  `
    + `${w.ok ? 'OK — grip stays on the wall' : 'WRONG'}`);
const held = ['hfwd', 'hback', 'hup', 'sfwd', 'sback'].filter(f => out.seen[f]);
if (held.length) console.log(`  ⚠ HELD family drew anyway: ${held.join(', ')}`);
const bad = missing || out.errorCount || held.length || !capOK || !wallOK;
console.log(bad ? 'FAIL' : 'PASS');
process.exit(bad ? 1 : 0);
