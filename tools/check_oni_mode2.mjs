#!/usr/bin/env node
// ONI'S SECOND MODE (V) — prove the mode does what the owner specced and nothing more.
//
// Owner, Aug 13 2026: "implement these move sets to oni second mode = v input" — the four
// boards (wire grabs, dir specials, dir heavies, dir aerials). Those move sets are his kit
// in BOTH forms; the mode itself changes exactly three things, and this check pins all
// three plus the two regressions the old bo-stance stub actually shipped:
//
//   1. V toggles mode2 (grounded only), press again to drop it.
//   2. In mode, NEUTRAL light/heavy are the staff (bostrike/bosweep) — neutral ONLY.
//      The stub drew the staff over every direction, so a Fwd+G in stance fired ghfwd's
//      box while drawing bosweep's picture. A directional press in the mode must draw its
//      own board row.
//   3. The dash: base form keeps the SOLID beats of his blur row, the mode gets the full
//      dissolve (beats 3-4) — §6b, "he does not move fast, he stops being solid."
//   4. The wire game (bind -> conversion) fires identically inside the mode.
//
// Same harness as drive_oni_wire.mjs: real page, real executeAttack, walk the draw.
import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

// ⛔ NEVER SPAWN A SERVER. There is ONE ShadowClash URL, :9100 (tools/serve.py).
const port = 9100, dbg = 9339;
const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const profile = await mkdtemp(path.join(tmpdir(), 'oni-mode2-'));

const who = await fetch(`http://127.0.0.1:${port}/whoami`).then(r => r.json()).catch(() => null);
if (!who) { console.error(`no server on :${port} — start it with: python3 tools/serve.py 9100 web`); process.exit(1); }
const here = process.cwd();
if (path.resolve(who.tree) !== path.resolve(here)) {
  console.error(`:9100 is serving ${who.tree}\nyou are in    ${here}\nrebind it (never add a second port):\n  kill ${who.pid} && python3 tools/serve.py 9100 web`);
  process.exit(1);
}
spawnSync('pkill', ['-f', `remote-debugging-port=${dbg}`], { stdio: 'ignore' });

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
  const F = SPRITES.oni.frames;
  const byIndex = {};
  for (const [k, i] of Object.entries(F)) (byIndex[i] ||= []).push(k);
  const famOf = i => {
    const ks = byIndex[i] || [];
    for (const k of ks) { const m = k.match(/^([a-z_]+?)\d+$/); if (m) return m[1]; }
    return ks[0] || ('cell' + i);
  };
  const spec = NINJA_ROSTER.find(s => s.name.toLowerCase() === 'oni');
  if (!spec) throw new Error('oni not on the roster');

  const errors = [], notes = [];
  const mk = (opts = {}) => {
    const p = new Player(1, 150, GROUND_Y - 48, spec, true);
    const foe = new Player(2, 260, GROUND_Y - 48, spec, false);
    p.opponent = foe; foe.opponent = p;
    p.facing = 1; p.isGrounded = true;
    p.getInputAxis = () => (opts.ax || 0) * p.facing;
    p.isDownPressed = () => !!opts.down;
    p.isUpPressed = () => false;
    p.state = STATE.IDLE; p.attackT = 0;
    p.stunTimer = 0; p.rollTimer = 0; p.rollRecover = 0; p.sayaLock = 0;
    return p;
  };
  // Walk the whole animation and return the ordered art families it drew.
  const walk = p => {
    const fams = [];
    const dur = p.attackAnim ? p.attackAnim.dur : 400;
    for (let s = 0; s < 24; s++) {
      if (p.attackAnim) p.attackAnim.start = animClock * 1000 - (s / 24) * dur * 0.99;
      let i;
      try { i = spriteFrameIndex(p, F); } catch (e) { errors.push('draw threw: ' + e.message); break; }
      const f = famOf(i);
      if (fams[fams.length - 1] !== f) fams.push(f);
    }
    return fams;
  };

  // 1. THE TOGGLE.
  { const p = mk();
    p.modeKey(); if (p.mode2 !== true) errors.push('V did not enter the mode');
    p.modeKey(); if (p.mode2 !== false) errors.push('second V did not drop the mode');
    p.mode2 = false; p.isGrounded = false; p.modeKey();
    if (p.mode2) errors.push('mode entered in mid-air — the grounded gate is gone');
  }

  // 2. NEUTRAL STAFF, DIRECTIONS UNTOUCHED — both tiers, both forms.
  const artCase = (name, opts, tier, wantFirst, banned) => {
    const p = mk(opts.inputs || {});
    p.mode2 = !!opts.mode2;
    try { p.executeAttack(tier); } catch (e) { errors.push(name + ': ' + e.message); return; }
    const fams = walk(p);
    if (!fams.some(f => wantFirst.includes(f)))
      errors.push(name + ': drew [' + fams + '], wanted one of [' + wantFirst + ']');
    if (banned && fams.some(f => banned.includes(f)))
      errors.push(name + ': drew banned family [' + fams + '] — ' + banned + ' must not appear');
    notes.push(name + ' -> ' + fams.join(','));
  };
  artCase('mode2 neutral light  = staff strike', { mode2: true }, STATE.ATTACK_LIGHT, ['bostrike']);
  artCase('mode2 neutral heavy  = staff sweep',  { mode2: true }, STATE.ATTACK_HEAVY, ['bosweep']);
  artCase('mode2 fwd heavy      = ghfwd board',  { mode2: true, inputs: { ax: 1 } }, STATE.ATTACK_HEAVY, ['ghfwd'], ['bosweep']);
  artCase('mode2 down heavy     = ghdown board', { mode2: true, inputs: { down: 1 } }, STATE.ATTACK_HEAVY, ['ghdown'], ['bosweep']);
  artCase('mode2 down light     = gldown board', { mode2: true, inputs: { down: 1 } }, STATE.ATTACK_LIGHT, ['gldown', 'ksweep'], ['bostrike']);
  artCase('base  neutral light  = his knives',   {}, STATE.ATTACK_LIGHT, ['glneu'], ['bostrike']);
  artCase('base  neutral heavy  = katana chain', {}, STATE.ATTACK_HEAVY, ['heavy_i'], ['bosweep']);
  artCase('base  fwd heavy      = ghfwd board',  { inputs: { ax: 1 } }, STATE.ATTACK_HEAVY, ['ghfwd']);

  // 2b. THE STRING DRAWS HIS OWN BOARDS (owner frames, Aug 13) — punches in base
  // form, kicks in the mode, the staff poke as the mode's beat one, and a LAUNCHER
  // on beat three in both forms ("rising upper" / "rising crescent").
  const stringCase = (name, useMode) => {
    const p = mk();
    p.mode2 = useMode;
    const wantRows = useMode ? ['bostrike', 'kick2', 'kick3']
                             : ['glneu',    'punch2', 'punch3'];
    for (let tap = 0; tap < 3; tap++) {
      // recovery elapsed, window still open — the tap window (0.55s) outlives the
      // light's recovery, so this is the state a real double-tap arrives in. The
      // recovery tick that ends an attack also resets the chain tier (update()),
      // so the harness resets it too or the hierarchy gate buffers the tap.
      p.state = STATE.IDLE; p.attackT = 0;
      p.recoveryTimer = 0; p.bufferedAttack = null; p.chainComboTier = 0;
      try { p.executeAttack(STATE.ATTACK_LIGHT); }
      catch (e) { errors.push(name + ' tap' + (tap + 1) + ': ' + e.message); return; }
      // assert on CELL INDICES, not family names — famOf strips every trailing
      // digit, so punch2/punch3 both read back as "punch"
      const row = wantRows[tap];
      const rowCells = new Set([1,2,3,4,5,6].map(i => F[row + i]).filter(c => c !== undefined));
      const dur = p.attackAnim ? p.attackAnim.dur : 400;
      const drawn = new Set();
      for (let s = 0; s < 24; s++) {
        if (p.attackAnim) p.attackAnim.start = animClock * 1000 - (s / 24) * dur * 0.99;
        try { drawn.add(spriteFrameIndex(p, F)); }
        catch (e) { errors.push(name + ' tap' + (tap + 1) + ' draw: ' + e.message); break; }
      }
      const stray = [...drawn].filter(i => !rowCells.has(i));
      if (stray.length)
        errors.push(name + ' tap' + (tap + 1) + ': drew cells [' + [...drawn] + '] outside ' + row + ' [' + [...rowCells] + ']');
      if (tap === 2) {
        const act = p.kageActs[p.kageActs.length - 1];
        if (!act || !act.opts.launch)
          errors.push(name + ': beat 3 did not carry the launcher');
      }
    }
    if (p.stringStep !== 2) errors.push(name + ': stringStep ended at ' + p.stringStep);
    notes.push(name + ' -> beats draw ' + wantRows.join(', ') + ' + launcher ender');
  };
  stringCase('base punch string', false);
  stringCase('mode2 kick string', true);

  // 3. THE DASH SPLIT — base form solid, mode dissolved. blur3/blur4 are the particulate
  // beats; the base dash must never reach them, the mode dash must.
  { const dissolve = [F.blur3, F.blur4];
    const dashCells = p => {
      const got = new Set();
      for (let s = 0; s <= 12; s++) {
        p.dashTimer = DASH_TIME * (1 - s / 12.5);
        got.add(spriteFrameIndex(p, F));
      }
      p.dashTimer = 0;
      return got;
    };
    const base = mk(); const cellsBase = dashCells(base);
    const m2 = mk(); m2.mode2 = true; const cellsMode = dashCells(m2);
    if (dissolve.some(c => cellsBase.has(c)))
      errors.push('base dash reached the dissolve beats [' + [...cellsBase] + '] — those are the mode\'s');
    if (!dissolve.every(c => cellsMode.has(c)))
      errors.push('mode dash never fully dissolved [' + [...cellsMode] + ']');
    if (![F.blur1, F.blur2].every(c => cellsBase.has(c)))
      errors.push('base dash lost its own solid beats [' + [...cellsBase] + ']');
    notes.push('dash base -> [' + [...cellsBase] + '] mode -> [' + [...cellsMode] + ']');
  }

  // 4. THE WIRE GAME INSIDE THE MODE — a bind + fwd press must still take the katana.
  { const p = mk({ ax: 1 });
    p.mode2 = true;
    p.wireBind = 0.55; p.wireBindFoe = p.opponent;
    try { p.executeAttack(STATE.ATTACK_SPECIAL); } catch (e) { errors.push('wire in mode: ' + e.message); }
    if (p.wireConv !== 'katana')
      errors.push('wire conversion in the mode gave "' + p.wireConv + '", wanted katana');
    else {
      const fams = walk(p);
      if (!fams.includes('kdraw')) errors.push('katana execution in mode drew [' + fams + ']');
      notes.push('wire in mode -> ' + p.wireConv + ' [' + fams + ']');
    }
  }

  return { errors, notes };
})()`;

let out;
try { out = await evaluate(script); }
finally { try { ws.close(); } catch {} chrome.kill(); }

for (const n of out.notes) console.log('  ·', n);
if (out.errors.length) {
  console.error('\nFAIL');
  for (const e of out.errors) console.error('  ✗', e);
  process.exit(1);
}
console.log('\nONI SECOND MODE: all checks pass');
