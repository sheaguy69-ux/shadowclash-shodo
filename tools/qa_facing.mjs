#!/usr/bin/env node
// K3 facing harness (reusable): runs fighters toward the opponent in a live match,
// screenshots the canvas mid-run. The ONLY honest facing gate (sheet cells + engine mirror
// make static reads unreliable for hooded chibis).
// Usage: node tools/qa_facing.mjs [outDir] [ids csv e.g. 6,7,8] [holdMs]
import { mkdtemp, rm, writeFile, mkdir } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import { tmpdir } from 'node:os';
import path from 'node:path';

const root = process.cwd();
const outputDir = process.argv[2] || 'media/facing-audit';
await mkdir(outputDir, { recursive: true });
const httpPort = +(process.env.PORT || 9101), debugPort = 9334;
const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const profile = await mkdtemp(path.join(tmpdir(), 'sc-facing-chrome-'));

// ⛔ ONE SERVER: :9100 (tools/serve.py). This used to spawn its own on a private port with
// plain `python3 -m http.server` — no cache headers, so it could pin a stale sprite PNG, and
// a leftover instance silently graded the PREVIOUS sheet. It also gave the owner a second URL
// backed by a different tree. Use the shared server; never start or kill one here.
const alive = await fetch(`http://127.0.0.1:${httpPort}/`).then(r => r.ok).catch(() => false);
if (!alive) {
  console.error(`no server on :${httpPort} — start it once with:  python3 tools/serve.py 9101 web`);
  process.exit(1);
}
const chrome = spawn(chromePath, ['--headless=new', '--disable-gpu', '--no-first-run', '--autoplay-policy=no-user-gesture-required',
  `--remote-debugging-port=${debugPort}`, `--user-data-dir=${profile}`, `http://127.0.0.1:${httpPort}/`], { stdio: 'ignore' });

const sleep = ms => new Promise(r => setTimeout(r, ms));
async function target() {
  for (let i = 0; i < 80; i++) {
    try {
      const list = await fetch(`http://127.0.0.1:${debugPort}/json/list`).then(r => r.json());
      const page = list.find(t => t.type === 'page' && t.url.includes(`127.0.0.1:${httpPort}`));
      if (page) return page;
    } catch {}
    await sleep(100);
  }
  throw new Error('no CDP page');
}
const HOLD_MS = Number(process.argv[4] || 450);
const NINJA_NAME_MAP = [[0,'executioner'],[1,'mizu'],[2,'shin'],[3,'tsubasa'],[4,'ember'],[5,'kael'],[6,'mokurai'],[7,'exile']];

class CDP {
  constructor(url) { this.socket = new WebSocket(url); this.nextId = 1; this.pending = new Map(); }
  open() { return new Promise((res, rej) => {
    this.socket.addEventListener('open', res, { once: true });
    this.socket.addEventListener('error', rej, { once: true });
    this.socket.addEventListener('message', ev => {
      const m = JSON.parse(ev.data);
      if (m.id && this.pending.has(m.id)) { const { res, rej } = this.pending.get(m.id); this.pending.delete(m.id);
        m.error ? rej(new Error(m.error.message)) : res(m.result); }
    });
  }); }
  send(method, params = {}) { const id = this.nextId++;
    return new Promise((res, rej) => { this.pending.set(id, { res, rej }); this.socket.send(JSON.stringify({ id, method, params })); }); }
  async evaluate(expression) {
    const r = await this.send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
    if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails));
    return r.result.value;
  }
}

const page = await target();
const cdp = new CDP(page.webSocketDebuggerUrl);
await cdp.open();
await cdp.send('Page.enable');
for (let i = 0; i < 100; i++) {
  const ready = await cdp.evaluate(`typeof SPRITES !== 'undefined' && Object.keys(SPRITES).length === NINJA_ROSTER.length && Object.values(SPRITES).every(s => s.ready)`).catch(() => false);
  if (ready) break;
  await sleep(100);
}

const picks = process.argv[3] ? process.argv[3].split(',').map(Number) : [6, 7, 8];
const names = Object.fromEntries(NINJA_NAME_MAP);
for (const id of picks) {
  const info = await cdp.evaluate(`(async () => {
    p1Pick = ${id}; p2Pick = 1; beginFight();
    await new Promise(r => setTimeout(r, 1600));
    window.dispatchEvent(new KeyboardEvent('keydown', { code: 'KeyD', bubbles: true }));
    await new Promise(r => setTimeout(r, ${HOLD_MS}));
    const p = player1;
    return { name: '${names[id]}', state: Object.keys(STATE).find(k => STATE[k] === p.state), vx: p.vx, facing: p.facing, x: Math.round(p.x) };
  })()`);
  const shot = await cdp.send('Page.captureScreenshot', { format: 'png' });
  await writeFile(path.join(outputDir, `run-${names[id]}.png`), Buffer.from(shot.data, 'base64'));
  console.log(JSON.stringify(info));
}
chrome.kill(); await rm(profile, { recursive: true, force: true }).catch(() => {});
console.log('done ->', outputDir);
process.exit(0);
