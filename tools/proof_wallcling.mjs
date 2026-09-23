#!/usr/bin/env node
// Render Oni clinging to the LEFT and the RIGHT wall through the game's OWN draw path,
// and save it as a picture. Not a mock: it builds real Player objects, puts them in
// WALL_CLING with a real wallDir, and calls the engine's drawFighter/draw, so whatever
// the sprite mirror does in play is exactly what lands in this image.
//
// ⛔ Uses the one server on :9100 and never starts its own; reaps any stale Chrome on the
// debug port first, because attaching to a leftover instance grades an old page.
import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const port = +(process.env.PORT || 9101), dbg = 9339;   // own debug port — run_drill.mjs holds 9337 and the two raced
const out = process.argv[2] || '/tmp/PROOF-WALLCLING.png';
const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

const alive = await fetch(`http://127.0.0.1:${port}/`).then(r => r.ok).catch(() => false);
if (!alive) { console.error(`no server on :${port} — start it once: python3 tools/serve.py 9101 web`); process.exit(1); }

spawnSync('pkill', ['-f', `remote-debugging-port=${dbg}`], { stdio: 'ignore' });
const profile = await mkdtemp(path.join(tmpdir(), 'oni-proof-'));
const chrome = spawn(chromePath, ['--headless=new', '--disable-gpu', '--no-first-run',
  '--no-default-browser-check', '--window-size=1280,800',
  `--remote-debugging-port=${dbg}`, `--user-data-dir=${profile}`,
  `http://127.0.0.1:${port}/`], { stdio: 'ignore' });

const sleep = ms => new Promise(r => setTimeout(r, ms));
let page;
for (let i = 0; i < 120 && !page; i++) {
  try {
    const list = await fetch(`http://127.0.0.1:${dbg}/json/list`).then(r => r.json());
    page = list.find(t => t.type === 'page' && t.url.includes(String(port)));
  } catch {}
  if (!page) await sleep(100);
}
if (!page) { console.error('chrome never came up'); chrome.kill('SIGKILL'); process.exit(1); }

const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.addEventListener('open', res, { once: true }); ws.addEventListener('error', rej, { once: true }); });
let id = 1; const pend = new Map();
ws.addEventListener('message', e => {
  const m = JSON.parse(e.data);
  if (m.id && pend.has(m.id)) { const p = pend.get(m.id); pend.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); }
});
const evaluate = expr => new Promise((res, rej) => {
  const n = id++; pend.set(n, { res, rej });
  ws.send(JSON.stringify({ id: n, method: 'Runtime.evaluate', params: { expression: expr, awaitPromise: true, returnByValue: true } }));
}).then(r => { if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text); return r.result.value; });

const script = String.raw`(async () => {
  const wait = async (t, m) => { for (let i = 0; i < 200; i++) { if (t()) return; await new Promise(r => setTimeout(r, 50)); } throw new Error(m); };
  await wait(() => typeof SPRITES !== 'undefined' && SPRITES.oni && SPRITES.oni.ready, 'oni sheet never loaded');
  const spec = NINJA_ROSTER.find(s => s.name.toLowerCase() === 'oni');

  const W = 900, H = 460, WALL = 46;
  const cv = document.createElement('canvas');
  cv.width = W; cv.height = H;
  const c = cv.getContext('2d');
  c.imageSmoothingEnabled = false;
  c.fillStyle = '#1b1b20'; c.fillRect(0, 0, W, H);

  // two walls, one per panel, on opposite sides
  const panels = [
    { x0: 0,     label: 'LEFT WALL',  wallDir: -1, wallX: 8 },
    { x0: W / 2, label: 'RIGHT WALL', wallDir:  1, wallX: W / 2 + W / 2 - WALL - 8 },
  ];
  c.fillStyle = '#3a3a44';
  for (const p of panels) c.fillRect(p.wallX, 0, WALL, H);
  c.strokeStyle = '#2a2a32'; c.beginPath(); c.moveTo(W / 2, 0); c.lineTo(W / 2, H); c.stroke();

  const results = [];
  for (const p of panels) {
    const o = new Player(1, 0, 0, spec, true);
    o.wallDir  = p.wallDir;
    o.state    = STATE.WALL_CLING;
    o.isGrounded = false;
    o.vy = 0;
    o.alpha = 1;
    o.facing = -p.wallDir;            // exactly what the cling block sets
    // seat him against the wall face
    o.x = p.wallDir < 0 ? p.wallX + WALL : p.wallX - o.width;
    o.y = 150;
    if (typeof drawFighter === 'function') drawFighter(c, o); else o.draw(c);
    results.push({ label: p.label, wallDir: p.wallDir, facing: o.facing,
                   x: Math.round(o.x), wallX: Math.round(p.wallX) });
  }

  c.font = 'bold 15px monospace'; c.fillStyle = '#e8e8ef';
  c.fillText('LEFT WALL  — claws must point LEFT',  90, 28);
  c.fillText('RIGHT WALL — claws must point RIGHT', W / 2 + 70, 28);
  return { png: cv.toDataURL('image/png'), results };
})()`;

let r;
try { r = await evaluate(script); }
catch (e) { console.error('PROOF FAILED:', e.message); ws.close(); chrome.kill('SIGKILL'); process.exit(1); }
await writeFile(out, Buffer.from(r.png.split(',')[1], 'base64'));
for (const x of r.results) console.log(`  ${x.label.padEnd(10)} wallDir=${x.wallDir > 0 ? '+1' : '-1'} facing=${x.facing > 0 ? '+1' : '-1'}  sprite x=${x.x} wall x=${x.wallX}`);
console.log(`wrote ${out}`);
ws.close(); chrome.kill('SIGKILL');
