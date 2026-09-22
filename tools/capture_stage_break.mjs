#!/usr/bin/env node
// STAGE BREAK — motion proof + self-check in one pass.
//
// Drives web/index.html in headless Chrome, loads the roof board, spikes a body
// into the tiles until the deck gives, and writes every frame of the transition
// to media/stage-break/ as PNGs (+ a GIF if ffmpeg is present). It ASSERTS the
// transition it filmed: board changed, both fighters left the old floor, the
// round reset puts the whole board back. If the break silently stops working
// this exits non-zero instead of quietly filming a stage that never broke.
//
//   node tools/capture_stage_break.mjs
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { readFile } from 'node:fs/promises';

const OUT = path.resolve('media/stage-break');
// ⛔ HOUSE RULE 7: ONE server, port 9100, and a driver NEVER starts its own. This tool
// shipped with `PORT = 4611` and spawned python3 tools/serve.py itself — a second port is
// how one agent grades a tree another agent is not editing. It now uses 9100 and checks it.
const PORT = 9100, DBG = 9341;
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const profile = await mkdtemp(path.join(tmpdir(), 'sc-break-'));
await mkdir(OUT, { recursive: true });

const probe = await fetch(`http://127.0.0.1:${PORT}/index.html`).catch(() => null);
if (!probe || !probe.ok) {
  console.error(`\n  \u26d4 nothing is serving http://127.0.0.1:${PORT} — this tool does NOT start one.`);
  console.error(`     python3 tools/serve.py ${PORT} web &\n`);
  process.exit(1);
}
const served = await probe.text();
const onDisk = await readFile('web/index.html', 'utf8');
if (served !== onDisk) {
  console.error(`\n  \u26d4 :${PORT} IS NOT SERVING THIS TREE — refusing to grade it.`);
  console.error(`     served ${served.length} bytes, web/index.html is ${onDisk.length}.`);
  console.error(`     kill $(lsof -nP -iTCP:${PORT} -sTCP:LISTEN -t) && python3 tools/serve.py ${PORT} web &\n`);
  process.exit(1);
}
const server = { kill() {} };   // not ours to stop
const chrome = spawn(CHROME, ['--headless=new', '--disable-gpu', '--no-first-run', '--mute-audio',
  '--window-size=800,500', `--remote-debugging-port=${DBG}`, `--user-data-dir=${profile}`,
  `http://127.0.0.1:${PORT}/index.html`], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
// Chrome is still flushing its profile as it dies, so the rmdir races it and
// throws ENOTEMPTY — an OS-temp dir left behind is not worth failing a run over.
const bye = async code => { chrome.kill(); server.kill(); await rm(profile, { recursive: true, force: true }).catch(() => {}); process.exit(code); };

let page;
for (let i = 0; i < 100 && !page; i++) {
  try {
    const list = await fetch(`http://127.0.0.1:${DBG}/json/list`).then(r => r.json());
    page = list.find(t => t.type === 'page' && t.url.includes(String(PORT)));
  } catch {}
  if (!page) await sleep(100);
}
if (!page) { console.error('chrome never came up'); await bye(1); }

const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.addEventListener('open', res, { once: true }); ws.addEventListener('error', rej, { once: true }); });
let id = 0; const pending = new Map();
ws.addEventListener('message', e => { const m = JSON.parse(e.data); const p = pending.get(m.id); if (p) { pending.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); } });
const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
const evaluate = async expr => {
  const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || 'eval threw');
  return r.result.value;
};
await send('Runtime.enable');
await sleep(2500);   // let the sprite sheets and stage art land

// The same deterministic sequence the mechanic ships with: two spikes load the
// wear, the third breaks it, and the loop resolves the break at end of frame.
const run = await evaluate(`(() => {
  document.querySelectorAll('#title-screen,#character-selection,#game-over-screen').forEach(e => e && e.classList.add('hidden'));
  p1Pick = 0; p2Pick = 1; gameMode = '2p'; cpuMode = false; stagePick = 'roof';
  startNewGame();
  roundIntroTimer = 0; roundBanner = null; stageToastT = 0;
  const shots = [];
  // JPEG at 640 wide: a PNG filmstrip of this length is a ~15MB single CDP
  // message and the socket sits on it long enough to look like a hang.
  const grab = () => { const c = document.createElement('canvas'); c.width = 640; c.height = 360;
    c.getContext('2d').drawImage(canvas, 0, 0, 640, 360); shots.push(c.toDataURL('image/jpeg', 0.82).slice(23)); };
  player1.x = 280; player1.y = GROUND_Y - player1.height; player1.isGrounded = true;
  player2.x = 430; player2.y = GROUND_Y - player2.height; player2.isGrounded = true;
  for (let i = 0; i < 2; i++) { player2.y = GROUND_Y - player2.height + 2; player2.vy = 700;
    player2.stunTimer = 0.6; player2.isGrounded = false; player2.applyPhysics(1/60); }
  // every link must resolve — a typo'd id is a surface that silently never breaks
  const dangling = STAGES.flatMap(s => [s.below, s.through].filter(Boolean)
    .filter(id => !STAGES.some(t => t.id === id)).map(id => s.id + '->' + id));
  const before = currentStage.id, wear = stageWear.floor;
  for (let i = 0; i < 6; i++) { updateGame(1/60); drawScene(); grab(); }      // the board, worn
  player2.y = GROUND_Y - player2.height - 150; player2.vy = 780; player2.stunTimer = 1.0; player2.isGrounded = false;
  for (let i = 0; i < 78; i++) { updateGame(1/60); drawScene(); if (i % 3 === 0) grab(); }
  const mid = { stage: currentStage.id, p1g: player1.isGrounded, p2g: player2.isGrounded };
  resetRound(); roundIntroTimer = 0; drawScene();
  const after = currentStage.id, wearAfter = stageWear.floor;   // read BEFORE the wall run moves the board again

  // SECOND SEQUENCE — the wall. A stunned body driven into the side of the
  // Broken Hall goes THROUGH it into the Buddha courtyard next door.
  const wshots = []; const wgrab = () => { const c = document.createElement('canvas'); c.width = 640; c.height = 360;
    c.getContext('2d').drawImage(canvas, 0, 0, 640, 360); wshots.push(c.toDataURL('image/jpeg', 0.82).slice(23)); };
  stageBase = STAGES.find(s => s.id === 'hall'); setStage(stageBase); stageToastT = 0;
  player1.x = 520; player1.y = GROUND_Y - player1.height; player1.isGrounded = true; player1.stunTimer = 0;
  player2.x = canvas.width - player2.width - 60; player2.y = GROUND_Y - player2.height - 30; player2.isGrounded = false;
  const wallBefore = currentStage.id;
  for (let i = 0; i < 3; i++) { wgrab(); updateGame(1/60); drawScene(); }
  for (let hit = 0; hit < 3; hit++) {
    player2.x = canvas.width - player2.width - 20; player2.y = GROUND_Y - player2.height - 30;
    player2.vx = 820; player2.vy = -40; player2.stunTimer = 0.8; player2.isGrounded = false; player2.wallStress = false;
    for (let i = 0; i < 14; i++) { updateGame(1/60); drawScene(); if (i % 2 === 0) wgrab(); }
  }
  for (let i = 0; i < 24; i++) { updateGame(1/60); drawScene(); if (i % 3 === 0) wgrab(); }
  const wall = { before: wallBefore, after: currentStage.id };

  // EVERY DECLARED LINK, DRIVEN — a link that reads fine but never fires (a
  // ledge'd board with no floor under the test spot, a target that closes its
  // own pit) is invisible until someone plays that exact board.
  const sweep = [];
  for (const st of STAGES) {
    for (const [kind, target] of [['floor', st.below], ['wall', st.through]]) {
      if (!target) continue;
      stageBase = st; setStage(st);
      const p = player1;
      p.hp = 150; p.stunTimer = 0; p.x = Math.round(canvas.width / 2 - p.width / 2);
      for (let i = 0; i < 6 && currentStage.id === st.id; i++) {
        if (kind === 'floor') { p.y = GROUND_Y - p.height + 2; p.vy = 760; p.stunTimer = 0.8; p.isGrounded = false; }
        else { p.x = canvas.width - p.width - 4; p.vx = 820; p.stunTimer = 0.8; p.isGrounded = false; p.wallStress = false; }
        p.applyPhysics(1 / 60);
        if (pendingBreak) { const b = pendingBreak; pendingBreak = null; breakStage(b.kind, b.x, b.y); }
      }
      sweep.push({ from: st.id, kind, want: target, got: currentStage.id });
    }
  }
  return { before, wear, mid, dangling, after, wearAfter, shots, wshots, wall, sweep };
})()`);

let n = 0;
for (const b64 of run.shots) await writeFile(path.join(OUT, `f${String(n++).padStart(3, "0")}.jpg`), Buffer.from(b64, 'base64'));
let w = 0;
for (const b64 of run.wshots) await writeFile(path.join(OUT, `w${String(w++).padStart(3, "0")}.jpg`), Buffer.from(b64, 'base64'));

const fail = [];
if (run.dangling.length) fail.push(`stage link points at no board: ${run.dangling.join(', ')}`);
if (run.before !== 'roof') fail.push(`started on ${run.before}, not roof`);
if (!(run.wear > 0)) fail.push('spiking the deck accrued no wear');
if (run.mid.stage !== 'hall') fail.push(`roof did not break into hall (ended on ${run.mid.stage})`);
if (!run.mid.p1g || !run.mid.p2g) fail.push('a fighter never landed on the new board');
if (run.after !== 'roof' || run.wearAfter !== 0) fail.push(`resetRound left ${run.after} wear=${run.wearAfter}`);
if (run.wall.after !== 'temple') fail.push(`wall slam did not break hall into temple (ended on ${run.wall.after})`);
for (const l of run.sweep) if (l.got !== l.want) fail.push(`${l.from} ${l.kind}-break went to ${l.got}, not ${l.want}`);
console.log(`links driven: ${run.sweep.map(l => `${l.from}-${l.kind}->${l.got}`).join('  ')}`);
console.log(`${n}+${w} frames -> ${OUT}   floor ${run.before} -> ${run.mid.stage} (reset ${run.after})   wall ${run.wall.before} -> ${run.wall.after}`);

for (const [src, gif] of [['f%03d.jpg', 'floor-break.gif'], ['w%03d.jpg', 'wall-break.gif']])
  await new Promise(r => spawn('ffmpeg', ['-y', '-framerate', '20', '-i', path.join(OUT, src),
    '-vf', 'scale=640:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse',
    path.join(OUT, gif)], { stdio: 'ignore' }).on('close', r));

if (fail.length) { console.error('FAIL:\n  ' + fail.join('\n  ')); await bye(1); }
console.log('OK — break, drop and reset all verified');
await bye(0);
