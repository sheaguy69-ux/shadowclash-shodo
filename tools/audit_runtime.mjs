#!/usr/bin/env node
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import { tmpdir } from 'node:os';
import path from 'node:path';

const root = process.cwd();
const outputDir = path.resolve(process.argv[2] || 'media/audit-runtime-2026-07-16');
const httpPort = +(process.env.PORT || 9100);
const debugPort = 9333;
const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const profile = await mkdtemp(path.join(tmpdir(), 'shadowclash-audit-chrome-'));
await mkdir(outputDir, { recursive: true });

// ⛔ ONE SERVER: :9100 (tools/serve.py). This used to spawn its own on a private port with
// plain `python3 -m http.server` — no cache headers, so it could pin a stale sprite PNG, and
// a leftover instance silently graded the PREVIOUS sheet. It also gave the owner a second URL
// backed by a different tree. Use the shared server; never start or kill one here.
const alive = await fetch(`http://127.0.0.1:${httpPort}/`).then(r => r.ok).catch(() => false);
if (!alive) {
  console.error(`no server on :${httpPort} — start it once with:  python3 tools/serve.py 9100 web`);
  process.exit(1);
}
const chrome = spawn(chromePath, [
  '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--autoplay-policy=no-user-gesture-required',
  `--remote-debugging-port=${debugPort}`, `--user-data-dir=${profile}`,
  `http://127.0.0.1:${httpPort}/`,
], { stdio: 'ignore' });

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
async function target() {
  for (let attempt = 0; attempt < 80; attempt++) {
    try {
      const targets = await fetch(`http://127.0.0.1:${debugPort}/json/list`).then(response => response.json());
      const page = targets.find(item => item.type === 'page' && item.url.includes(`127.0.0.1:${httpPort}`));
      if (page) return page;
    } catch {}
    await sleep(100);
  }
  throw new Error('Chrome DevTools endpoint did not start');
}

class CDP {
  constructor(url) {
    this.socket = new WebSocket(url);
    this.nextId = 1;
    this.pending = new Map();
    this.events = [];
  }
  async open() {
    await new Promise((resolve, reject) => {
      this.socket.addEventListener('open', resolve, { once: true });
      this.socket.addEventListener('error', reject, { once: true });
    });
    this.socket.addEventListener('message', event => {
      const message = JSON.parse(event.data);
      if (message.id) {
        const pending = this.pending.get(message.id);
        this.pending.delete(message.id);
        if (message.error) pending.reject(new Error(message.error.message));
        else pending.resolve(message.result);
      } else {
        this.events.push(message);
      }
    });
  }
  send(method, params = {}) {
    const id = this.nextId++;
    this.socket.send(JSON.stringify({ id, method, params }));
    return new Promise((resolve, reject) => this.pending.set(id, { resolve, reject }));
  }
  async evaluate(expression) {
    const result = await this.send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
    if (result.exceptionDetails) throw new Error(result.exceptionDetails.exception?.description || result.exceptionDetails.text);
    return result.result.value;
  }
  close() { this.socket.close(); }
}

const testExpression = String.raw`(async () => {
  const assert = (condition, message) => { if (!condition) throw new Error(message); };
  const waitFor = async (test, message) => {
    for (let attempt = 0; attempt < 100; attempt++) {
      if (test()) return;
      await new Promise(resolve => setTimeout(resolve, 50));
    }
    throw new Error(message);
  };
  await waitFor(() => typeof SPRITES !== 'undefined' && typeof NINJA_ROSTER !== 'undefined' && Object.keys(SPRITES).length >= NINJA_ROSTER.length && Object.values(SPRITES).every(sheet => sheet.ready), 'roster sprite sheets did not load');
  const sheets = NINJA_ROSTER.map(spec => {
    const sheet = SPRITES[spec.name.toLowerCase()];
    assert(sheet.img.width === sheet.frameW * sheet.cols, spec.name + ' sheet width mismatch');
    assert(sheet.img.height === sheet.frameH, spec.name + ' sheet height mismatch');
    return { name: spec.name, width: sheet.img.width, height: sheet.img.height, cols: sheet.cols };
  });

  const stateNames = ['IDLE','RUN','JUMP','WALL_CLING','ATTACK_LIGHT','ATTACK_HEAVY','ATTACK_SPECIAL','PARRY_STANCE','THROWING','THROWN','BLOCKING','CROUCH','ROLL','STUNNED','SUBSTITUTION'];
  const routedStates = {};
  for (const spec of NINJA_ROSTER) {
    const fighter = new Player(1, 150, GROUND_Y - 48, spec, true);
    fighter.isGrounded = true;
    fighter.attackAnim = { start: animClock * 1000, dur: 500 };
    fighter.recoveryTotal = fighter.recoveryTimer = 0.5;
    fighter.throwTimer = THROW_TIME / 2;
    const sheet = SPRITES[spec.name.toLowerCase()];
    routedStates[spec.name] = {};
    for (const stateName of stateNames) {
      fighter.state = STATE[stateName];
      fighter.vy = stateName === 'JUMP' ? -100 : 0;
      const index = spriteFrameIndex(fighter, sheet.frames);
      assert(Number.isInteger(index) && index >= 0 && index < sheet.cols, spec.name + ' invalid ' + stateName + ' frame');
      routedStates[spec.name][stateName] = index;
    }
  }

  const modePicks = { arcade: [0, null], cpu: [1, 2], '2p': [3, 4], watch: [5, 0] };
  const modes = {};
  for (const mode of ['arcade', 'cpu', '2p', 'watch']) {
    setGameMode(mode);
    [p1Pick, p2Pick] = modePicks[mode];
    beginFight();
    roundIntroTimer = 0;
    const t0 = roundTimer;
    for (let tick = 0; tick < 240; tick++) { updateGame(1 / 60); drawScene(); }
    assert(player1.maxHp === 150 && player2.maxHp === 150, mode + ' max HP mismatch');
    // measure the DELTA, not an absolute window: the page's own rAF loop also runs
    // while this expression executes, so wall-clock leakage shifts the absolute value
    // (nine-fighter routed-state scan made the old 80..90 window impossible to hit).
    assert(t0 - roundTimer >= 1 && t0 - roundTimer < 60, mode + ' round timer did not advance (t0=' + t0 + ' now=' + roundTimer + ')');
    modes[mode] = { p1: player1.spec.name, p2: player2.spec.name, hp: [player1.hp, player2.hp], timer: roundTimer };
  }

  setGameMode('2p'); cpuMode = false; attractMode = false; p1Pick = 0; p2Pick = 1; beginFight(); roundIntroTimer = 0; hitstopRemaining = 0; paused = false;
  player1.isGrounded = player2.isGrounded = true;
  window.dispatchEvent(new KeyboardEvent('keydown', { code: 'KeyF', bubbles: true }));
  assert(player1.state === STATE.ATTACK_LIGHT, 'keyboard light did not use combat path');
  window.dispatchEvent(new KeyboardEvent('keyup', { code: 'KeyF', bubbles: true }));
  resetRound(); roundIntroTimer = 0; player1.isGrounded = player2.isGrounded = true;
  document.getElementById('btn-t-p1-light').dispatchEvent(new Event('touchstart', { bubbles: true, cancelable: true }));
  assert(isTouchDevice && player1.state === STATE.ATTACK_LIGHT, 'touch light did not use combat path');
  document.getElementById('btn-t-p1-light').dispatchEvent(new Event('touchend', { bubbles: true, cancelable: true }));

  resetRound(); roundIntroTimer = 0;
  player1.isGrounded = player2.isGrounded = true;
  player1.x = 250; player2.x = 280; player1.y = player2.y = GROUND_Y - 48;
  keys.KeyA = true; player1.executeThrow(); keys.KeyA = false;
  assert(player1.state === STATE.THROWING && player1.throwBack, 'back throw selection failed');
  player1.updateThrow(THROW_TIME * THROW_RELEASE + 0.01);
  assert(player2.vx < 0 && player2.hp < 150, 'back throw release failed');

  resetRound(); roundIntroTimer = 0;
  player1.isGrounded = player2.isGrounded = true;
  player1.x = 250; player2.x = 270; player1.y = player2.y = GROUND_Y - 48;
  player1.hitboxes = [{ ox: 10, oy: 0, w: 40, h: 30, canClash: true }];
  player2.hitboxes = [{ ox: -10, oy: 0, w: 40, h: 30, canClash: true }];
  assert(processWeaponClash(player1, player2), 'eligible weapon clash did not resolve');
  assert(player1.hitboxes.length === 0 && player2.hitboxes.length === 0 && hitstopRemaining >= 115, 'weapon clash side effects failed h1=' + player1.hitboxes.length + ' h2=' + player2.hitboxes.length + ' hitstop=' + hitstopRemaining);

  const shin = new Player(1, 150, GROUND_Y - 48, NINJA_ROSTER[2], true);
  shin.isGrounded = true; shin.stamina = 100; shin.executeAttack(STATE.ATTACK_SPECIAL);
  assert(shin.vx > 0 && shin.projectiles.length === 0, 'Shin neutral special is not the flying kick');
  shin.state = STATE.IDLE; shin.recoveryTimer = 0; shin.chainComboTier = 0; shin.stamina = 100; shin.isGrounded = true; keys.KeyD = true;
  shin.executeAttack(STATE.ATTACK_SPECIAL); keys.KeyD = false;
  assert(shin.projectiles.length === 1, 'Shin forward special wire tool missing');

  resetRound(); roundIntroTimer = 0; roundWins = [0, 0]; player1.hp = 0; player2.hp = 0; endRound();
  assert(roundWins[0] === 1 && roundWins[1] === 1, 'double KO did not award both pips');
  clearTimeout(roundResetTimer);

  return { sheets, routedStates, modes, keyboard: true, touch: true, backThrow: true, clash: true, shinIdentity: true, doubleKO: true, maxHp: MAX_HP, damageScale: HEALTH_DAMAGE_SCALE, roundTime: ROUND_TIME };
})()`;

let cdp;
try {
  const page = await target();
  cdp = new CDP(page.webSocketDebuggerUrl);
  await cdp.open();
  await Promise.all(['Runtime.enable', 'Page.enable', 'Network.enable', 'Log.enable'].map(method => cdp.send(method)));
  await sleep(500);
  const result = await cdp.evaluate(testExpression);
  const screenshot = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
  await writeFile(path.join(outputDir, 'cumulative-runtime.png'), Buffer.from(screenshot.data, 'base64'));
  const errors = cdp.events.filter(event =>
    event.method === 'Runtime.exceptionThrown' ||
    event.method === 'Network.loadingFailed' ||
    (event.method === 'Log.entryAdded' && ['error', 'warning'].includes(event.params.entry.level)) ||
    (event.method === 'Network.responseReceived' && event.params.response.status >= 400)
  );
  const report = { result, errors, passed: errors.length === 0 };
  await writeFile(path.join(outputDir, 'cumulative-runtime.json'), JSON.stringify(report, null, 2) + '\n');
  if (errors.length) throw new Error(`browser emitted ${errors.length} console/network errors`);
  console.log(JSON.stringify(report, null, 2));
} finally {
  cdp?.close();
  chrome.kill('SIGTERM');
  // the :9100 server is SHARED — this tool never kills it
  await rm(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 });
}
