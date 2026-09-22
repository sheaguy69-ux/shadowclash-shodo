#!/usr/bin/env node
// SHIN'S SECOND FORM — KAGE-NUI (V) — pin the owner's melee mapping, and pin Form 1 not moving.
//
// Owner, Aug 21 2026: the Form-2 art is FINISHED and locked; the remaining work is wiring.
// His table, which this file is the executable copy of:
//
//   Light chain  step 0/1/2 -> f2_light1 Poke / f2_light2 Rising Slice / f2_light3 Double Thrust
//   Heavy chain  step 0/1/2 -> f2_heavy1 Tsuki / f2_heavy2 Cross-Slice / f2_heavy3 Disarm Hook
//   Crouch Light            -> f2_clow   Ankle Poke
//   Crouch Heavy            -> f2_csweep Sweeping Slice
//   Air Heavy               -> f2_air    Dive-Pierce
//
// ...and his hard constraint: those rows are active ONLY while the stance is set. Dropping it
// returns every Form-1 mapping unchanged.
//
// TWO REAL DEFECTS THIS EXISTS TO STOP COMING BACK (both shipped, both found by driving the
// real executor rather than by reading it):
//
//   1. The COMMAND KICKS block claims any grounded Light with a direction held and RETURNS,
//      so the Form-2 branch ~700 lines below never ran. Its escape hatch reads gldown/glfwd/
//      glback and Shin has no gl* family, so it never fired for him: Down+Light EXECUTED a
//      generic sweep kick while shinF2Frame, which only reads the stance, DREW the Poke.
//   2. Air Light has no Form-2 row, and fell past all three branches into THE STRINGS —
//      the grounded jab and its hitbox, played in mid-air.
//
// Cell numbers are deliberately absent: the rows have been re-indexed once already (the
// owner's own table still quotes the pre-reindex 204-257) and the KEYS are what survive.
//
// ⛔ NEVER SPAWN A SERVER. This CHECKS a designated port and fails with instructions.
import { spawn } from 'node:child_process';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const url = new URL(process.env.SHADOWCLASH_URL || 'http://127.0.0.1:9100');
const port = url.port || '9100';
const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const profile = await mkdtemp(path.join(tmpdir(), 'shin-mode2-'));

const who = await fetch(`http://127.0.0.1:${port}/whoami`).then(r => r.json()).catch(() => null);
if (!who) { console.error(`no server on :${port} — start it with: python3 tools/serve.py ${port} web`); process.exit(1); }
const here = process.cwd();
if (path.resolve(who.tree) !== path.resolve(here)) {
  console.error(`:${port} is serving ${who.tree}\nyou are in    ${here}\nrebind it (never add a port):\n  kill ${who.pid} && python3 tools/serve.py ${port} web`);
  process.exit(1);
}
const sleep = ms => new Promise(r => setTimeout(r, ms));

// ⛔ RETRY THE LAUNCH, WITH A REAL PAUSE. This harness family flakes and the port number was
// only ever the symptom: measured on this box, a Chrome started within ~2s of a previous one
// being killed does not come up AT ALL, on any port — 9352 succeeds cold and fails 1.5s after
// a kill, and `--remote-debugging-port=0` never even writes DevToolsActivePort. So back off
// and try again rather than chasing ports, and accept only a Chrome that has the GAME TAB.
// These are CDP sockets on loopback, not game servers — the one-server rule is about serve.py.
//
// ⛔ AND KILL THE PROCESS GROUP, NOT THE LAUNCHER. proc.kill() SIGTERMs the process node
// spawned; Chrome's helper processes outlive it and keep holding the port, so the NEXT run
// finds it busy and reports a launch failure. `detached` puts the whole browser in its own
// group and a negative-pid SIGKILL takes all of it. This is the actual cause of the flake —
// not the port number, which was only ever the symptom.
const killTree = proc => { try { process.kill(-proc.pid, 'SIGKILL'); } catch { try { proc.kill('SIGKILL'); } catch {} } };
const CDP = 9351;
const gameTab = list => list.find(t => t.type === 'page' && t.url.includes(String(port))) || null;

// REUSE a browser that is already parked on the game before spawning another. Chrome cannot
// restart within a few seconds of being killed (measured), so back-to-back runs of this check
// were failing on the launch, not on the game. Reuse removes that entirely.
// ⛔ AND RELOAD IT. A reused tab is holding the code it loaded, which is exactly how a driver
// in this repo once graded the PREVIOUS sheet twice and reported it as current. The reload is
// not optional and it carries a cache-buster.
let chrome = null, page = null, dbg = CDP, reused = false;
try {
  const found = gameTab(await fetch(`http://127.0.0.1:${CDP}/json/list`).then(r => r.json()));
  if (found) { page = found; reused = true; }
} catch {}

for (let attempt = 0; attempt < 6 && !page; attempt++) {
  if (attempt) await sleep(6000);   // measured: a cold start needs none, a restart needs seconds
  const proc = spawn(chromePath, ['--headless=new', '--disable-gpu', '--no-first-run',
    '--no-default-browser-check', `--remote-debugging-port=${CDP}`,
    `--user-data-dir=${profile}-${attempt}`, `http://127.0.0.1:${port}/`], { stdio: 'ignore', detached: true });
  for (let i = 0; i < 60 && !page; i++) {
    try { page = gameTab(await fetch(`http://127.0.0.1:${CDP}/json/list`).then(r => r.json())); } catch {}
    if (!page) await sleep(100);
  }
  if (page) chrome = proc; else killTree(proc);
}
if (!page) {
  console.error(`chrome never opened :${port} after 4 attempts on CDP :${CDP}.`);
  console.error('if this persists it is a stale browser, not the game: pkill -9 -f "headless=new"');
  process.exit(1);
}

// The reload, on its own connection: navigating tears the execution context down, so the
// socket that issues it is not the socket that should run the checks.
{
  const nav = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((res, rej) => { nav.addEventListener('open', res, { once: true }); nav.addEventListener('error', rej, { once: true }); });
  nav.send(JSON.stringify({ id: 1, method: 'Page.navigate', params: { url: `http://127.0.0.1:${port}/?cb=${process.pid}${reused ? '-reused' : ''}` } }));
  await sleep(1200);
  try { nav.close(); } catch {}
  for (let i = 0; i < 60; i++) {
    try { const t = gameTab(await fetch(`http://127.0.0.1:${CDP}/json/list`).then(r => r.json())); if (t) { page = t; break; } } catch {}
    await sleep(100);
  }
}

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
  await wait(() => typeof SPRITES !== 'undefined' && SPRITES.shin && SPRITES.shin.ready, 'shin sheet never loaded');
  const F = SPRITES.shin.frames;
  const byIndex = {};
  for (const [k, i] of Object.entries(F)) (byIndex[i] ||= []).push(k);
  // f2 rows are keyed f2_light1_3 — the family is everything before the FINAL number.
  const famOf = i => {
    const ks = byIndex[i] || [];
    for (const k of ks) { const m = k.match(/^(.*?)_?\d+$/); if (m && m[1]) return m[1]; }
    return ks[0] || ('cell' + i);
  };
  const spec = NINJA_ROSTER.find(s => s.name.toLowerCase() === 'shin');
  if (!spec) throw new Error('shin not on the roster');
  // ⛔ ART-GATED. SHEET_V 575 executed the owner's Aug 22 order — "no pre-Aug-20 frame may draw
  // anywhere" — and his nine f2_ rows were drawn Aug 8, so they were deleted. The stance now
  // falls back to his first-mode board art, which is what the engine is built to do. Everything
  // below describes the kit WHEN THE ART EXISTS; with the rows gone it would fail on correct
  // behaviour. The Form-1 half still runs, because that is the half that must not move.
  const hasForm2 = F.f2_light1_1 !== undefined;

  const errors = [], notes = [];
  const mk = (o = {}) => {
    const p = new Player(1, 150, GROUND_Y - 48, spec, true);
    const foe = new Player(2, 260, GROUND_Y - 48, spec, false);
    p.opponent = foe; foe.opponent = p;
    p.facing = 1; p.isGrounded = o.air ? false : true;
    p.getInputAxis = () => (o.ax || 0) * p.facing;
    p.isDownPressed = () => !!o.down;
    p.isUpPressed = () => !!o.up;      // Up is a real direction here: Up+Heavy is OMOTE SHUTO
    p.state = STATE.IDLE; p.attackT = 0; p.stamina = 100;
    p.stunTimer = 0; p.rollTimer = 0; p.rollRecover = 0;
    p.recoveryTimer = 0; p.attackCooldown = 0; p.chainComboTier = 0;
    p.kickKind = null; p.upAtkPending = false;
    p.kageNui = !!o.stance;
    return p;
  };
  const drew = p => famOf(spriteFrameIndex(p, F));
  const hit = (name, o, type, want, opt = {}) => {
    const p = mk(o);
    try { p.executeAttack(type); } catch (e) { errors.push(name + ': executeAttack threw ' + e.message); return null; }
    const f = drew(p);
    if (f !== want) errors.push(name + ': drew "' + f + '", the table says "' + want + '"');
    if (opt.noKick && p.kickKind) errors.push(name + ': the kick tier took the press (kickKind=' + p.kickKind + ')');
    if (opt.wantKick && p.kickKind !== opt.wantKick) errors.push(name + ': Form 1 kick changed — kickKind=' + p.kickKind + ', wanted ' + opt.wantKick);
    notes.push(name + ' -> ' + f + (p.kickKind ? ' [kick:' + p.kickKind + ']' : ''));
    return p;
  };

  if (!hasForm2) {
    notes.push('Form 2 art is deleted (Aug 22 purge) — stance assertions skipped, Form 1 still checked');
    const p = mk({ stance: 1 });
    try { p.executeAttack(STATE.ATTACK_HEAVY); } catch (e) { errors.push('stance heavy threw ' + e.message); }
    const f = drew(p);
    if (/^f2_/.test(f)) errors.push('the stance drew a Form-2 row that should not exist: ' + f);
    else notes.push('stance heavy falls back to ' + f + ' (Form 1, correct)');
  }

  // ---- 1. THE TOGGLE
  { const p = mk();
    p.toggleKageNui(); if (p.kageNui !== true) errors.push('V did not set the stance');
    p.toggleKageNui(); if (p.kageNui !== false) errors.push('second V did not drop the stance'); }

  // ---- 2. THE OWNER'S TABLE, IN THE STANCE
  if (hasForm2) hit('F2 crouch Light', { stance: 1, down: 1 },        STATE.ATTACK_LIGHT, 'f2_clow',   { noKick: 1 });
  if (hasForm2) hit('F2 crouch Heavy', { stance: 1, down: 1 },        STATE.ATTACK_HEAVY, 'f2_csweep', { noKick: 1 });
  if (hasForm2) hit('F2 fwd Light',    { stance: 1, ax: 1 },          STATE.ATTACK_LIGHT, 'f2_light1', { noKick: 1 });
  if (hasForm2) hit('F2 back Light',   { stance: 1, ax: -1 },         STATE.ATTACK_LIGHT, 'f2_light1', { noKick: 1 });
  if (hasForm2) hit('F2 air Heavy',    { stance: 1, air: 1 },         STATE.ATTACK_HEAVY, 'f2_air');

  if (hasForm2)
  // ---- 3. AIR LIGHT IS NOT IN THE KIT — it must not draw ANY f2_ row.
  { const p = mk({ stance: 1, air: 1 });
    try { p.executeAttack(STATE.ATTACK_LIGHT); } catch (e) { errors.push('F2 air Light threw ' + e.message); }
    const f = drew(p);
    if (/^f2_/.test(f)) errors.push('F2 air Light drew the Form-2 row "' + f + '" — the table lists Air HEAVY only');
    else notes.push('F2 air Light -> ' + f + ' (Form 1, correct)'); }

  if (hasForm2)
  // ---- 4. BOTH CHAINS REACH ALL THREE BEATS (f2_heavy3, the Disarm Hook, was unreachable)
  for (const [label, type, want] of [['light', STATE.ATTACK_LIGHT, ['f2_light1', 'f2_light2', 'f2_light3']],
                                     ['heavy', STATE.ATTACK_HEAVY, ['f2_heavy1', 'f2_heavy2', 'f2_heavy3']]]) {
    const p = mk({ stance: 1 }); const seen = [];
    for (let i = 0; i < 3; i++) {
      p.state = STATE.IDLE; p.attackAnim = null; p.recoveryTimer = 0; p.attackCooldown = 0; p.chainComboTier = 0;
      if (i) p.f2StepT = 0.5;
      try { p.executeAttack(type); } catch (e) { errors.push(label + ' chain threw ' + e.message); break; }
      seen.push(drew(p));
    }
    for (const w of want) if (!seen.includes(w)) errors.push(label + ' chain never reached ' + w + ' — saw [' + seen + ']');
    notes.push(label + ' chain -> [' + seen + ']');
  }

  if (hasForm2)
  // ---- 4b. THE STALE-LATCH REGRESSION. f2Air is a latch; before clearMoveArt owned it, a
  // Dive-Pierce left it true and EVERY later air Light drew the Dive-Pierce row over an
  // ordinary aerial light. Reproduce the exact sequence: dive, land, jump, light.
  { const p = mk({ stance: 1, air: 1 });
    try { p.executeAttack(STATE.ATTACK_HEAVY); } catch (e) { errors.push('dive threw ' + e.message); }
    if (!p.f2Air) errors.push('the Dive-Pierce did not set f2Air — this check is no longer testing anything');
    p.isGrounded = true; p.state = STATE.IDLE; p.attackAnim = null;
    p.recoveryTimer = 0; p.attackCooldown = 0; p.chainComboTier = 0;
    p.isGrounded = false;
    try { p.executeAttack(STATE.ATTACK_LIGHT); } catch (e) { errors.push('air light after dive threw ' + e.message); }
    if (p.f2Air) errors.push('f2Air survived the Dive-Pierce — clearMoveArt does not own it');
    const f = drew(p);
    if (/^f2_/.test(f)) errors.push('air Light after a Dive-Pierce drew "' + f + '" — stale f2Air latch is back');
    else notes.push('air Light after a Dive-Pierce -> ' + f + ' (Form 1, correct)'); }

  if (hasForm2)
  // ---- 4c. THE WINDOW BELONGS TO A TIER. A Light then a Heavy inside 0.55s used to advance
  // the HEAVY chain, so Tsuki — the owner's Heavy 1 — was unreachable after any light.
  { const p = mk({ stance: 1 });
    try { p.executeAttack(STATE.ATTACK_LIGHT); } catch (e) { errors.push('L threw ' + e.message); }
    const l = drew(p);
    p.state = STATE.IDLE; p.attackAnim = null; p.recoveryTimer = 0; p.attackCooldown = 0; p.chainComboTier = 0;
    try { p.executeAttack(STATE.ATTACK_HEAVY); } catch (e) { errors.push('H threw ' + e.message); }
    const h = drew(p);
    if (h !== 'f2_heavy1') errors.push('Light then Heavy opened the heavy chain on "' + h + '" — the table says Heavy 1 is Tsuki (f2_heavy1)');
    else notes.push('Light(' + l + ') then Heavy -> ' + h + ' (Tsuki, correct)'); }

  if (hasForm2)
  // ---- 4d. THE STANCE ONLY TAKES WHAT IT HAS ART FOR (owner, Aug 21: the Form-2 rule
  // "don't have to apply to everyone", and "I'm gonna give everybody a down air").
  // His four GROUND directional heavies and the roster-wide METEOR BREAK must survive it,
  // and the ART must agree with the MECHANICS on every one — a row reached through
  // DIR_MOVES that still draws f2_heavy is the same desync in a new place.
  for (const [label, o, wantArt] of [
        ['stance Fwd+Heavy',  { stance: 1, ax:  1 }, 'ghfwd'],
        ['stance Back+Heavy', { stance: 1, ax: -1 }, 'ghback'],
        ['stance Up+Heavy',   { stance: 1, up: 1 },  'ghup']]) {
    const p = mk(o);
    try { p.executeAttack(STATE.ATTACK_HEAVY); } catch (e) { errors.push(label + ' threw ' + e.message); continue; }
    if (p.moveArt !== wantArt) errors.push(label + ': executed "' + p.moveArt + '", wanted the ' + wantArt + ' board');
    const f = drew(p);
    if (f !== wantArt) errors.push(label + ': DREW "' + f + '" while EXECUTING "' + p.moveArt + '" — art/mechanics desync');
    else notes.push(label + ' -> ' + wantArt + ' (executes and draws the same move)');
  }
  if (hasForm2)
  { const p = mk({ stance: 1, down: 1 });
    try { p.executeAttack(STATE.ATTACK_HEAVY); } catch (e) { errors.push('stance Down+Heavy threw ' + e.message); }
    const f = drew(p);
    if (f !== 'f2_csweep') errors.push('stance Down+Heavy drew "' + f + '" — the table says Sweeping Slice, and ghdown stays Form 1');
    else notes.push('stance Down+Heavy -> f2_csweep (Sweeping Slice, not ghdown)'); }
  { const p = mk({ stance: 1, air: 1, down: 1 });
    try { p.executeAttack(STATE.ATTACK_HEAVY); } catch (e) { errors.push('stance air Down+Heavy threw ' + e.message); }
    if (!p.slamPhase) errors.push('METEOR BREAK is gone in the stance — the Dive-Pierce ate air Down+Heavy again');
    else notes.push('stance air Down+Heavy -> METEOR BREAK (slamPhase ' + p.slamPhase + ')');
    const f = drew(p);
    if (/^f2_/.test(f)) errors.push('METEOR BREAK drew the Form-2 row "' + f + '"'); }
  if (hasForm2)
  { const p = mk({ stance: 1, air: 1 });
    try { p.executeAttack(STATE.ATTACK_HEAVY); } catch (e) { errors.push('stance air Heavy threw ' + e.message); }
    const f = drew(p);
    if (f !== 'f2_air') errors.push('stance air Heavy drew "' + f + '", the table says Dive-Pierce (f2_air)');
    else notes.push('stance air Heavy -> f2_air (Dive-Pierce, still his)'); }

  // ---- 4e. THE DIRECTIONAL SPECIALS PAY, AND BACK IS THE TELEPORT. Fwd+Special used to
  // return above the chakra gate: zero cost, and it fired while winded. Back+Special was
  // caught by the same branch, so WIRE-STEP — which his own move list promises — was dead.
  const COST = (typeof SPECIAL_COST !== 'undefined' && SPECIAL_COST[2]) || 15;
  { const p = mk(); const before = p.stamina;
    try { p.executeAttack(STATE.ATTACK_SPECIAL); } catch (e) { errors.push('Fwd+Special threw ' + e.message); }
    p.getInputAxis = () => p.facing; }
  { const p = mk({ ax: 1 }); const before = p.stamina;
    try { p.executeAttack(STATE.ATTACK_SPECIAL); } catch (e) { errors.push('Fwd+Special threw ' + e.message); }
    if (p.stamina !== before - COST) errors.push('Fwd+Special cost ' + (before - p.stamina) + ' chakra, wanted ' + COST);
    else notes.push('Fwd+Special -> paid ' + COST + ' chakra, ' + (p.projectiles || []).length + ' stars'); }
  { const p = mk({ ax: 1 }); p.stamina = COST - 5; const before = p.stamina;
    try { p.executeAttack(STATE.ATTACK_SPECIAL); } catch (e) { errors.push('broke Fwd+Special threw ' + e.message); }
    if ((p.projectiles || []).length || p.stamina !== before) errors.push('Fwd+Special fired below its own cost');
    else notes.push('Fwd+Special below cost -> refused'); }
  { const p = mk({ ax: 1 }); p.windedTimer = 1;
    try { p.executeAttack(STATE.ATTACK_SPECIAL); } catch (e) { errors.push('winded Fwd+Special threw ' + e.message); }
    if ((p.projectiles || []).length) errors.push('Fwd+Special fired while winded');
    else notes.push('Fwd+Special while winded -> refused'); }
  { const p = mk({ ax: -1 }); const x0 = p.x;
    try { p.executeAttack(STATE.ATTACK_SPECIAL); } catch (e) { errors.push('Back+Special threw ' + e.message); }
    if (!(p.vanishTimer > 0)) errors.push('Back+Special did not WIRE-STEP — the retreating throw is still eating the input');
    else notes.push('Back+Special -> WIRE-STEP (vanish ' + p.vanishTimer.toFixed(2) + ', moved ' + Math.round(p.x - x0) + 'px)'); }

  if (hasForm2)
  // ---- 4f. THE KAGE-KAMI ECHO DIES WITH THE STANCE. It replayed Form-2 cells AND re-fired
  // Form-2 hitboxes with kageNui false — the one route that broke the owner's hard rule.
  { const p = mk({ stance: 1 });
    // animClock MUST advance: the anti-statue guard now measures how much HISTORY the tape
    // spans, so 40 samples all stamped with the same t buy nothing and the cast is refused —
    // which would quietly make this assertion vacuous.
    for (let i = 0; i < 40; i++) { p.drawCell = F.f2_heavy3_3; p.kageTapeT = 0; p.recordKageTape(1 / 30); animClock += 1 / 30; }
    const taped = p.kageTape.length;
    try { p.castKageKami(); } catch (e) { errors.push('castKageKami threw ' + e.message); }
    const cast = !!(p.clone && p.clone.kage);
    if (!cast) errors.push('no echo was cast, so the stance-drop assertion below tests nothing');
    p.toggleKageNui();
    if (p.clone && p.clone.kage) errors.push('the Kage-Kami echo outlived the stance');
    else if (p.kageTape.length) errors.push('the tape outlived the stance — the next echo can replay Form-2 cells');
    else notes.push('echo cast=' + cast + ' from a ' + taped + '-sample tape, both gone on stance drop'); }

  // ---- 4g. WIRE-STEP MUST NOT THROW. It borrows vanishTimer, and update() hands an expired
  // vanish to finishVanish() — this once threw an uncaught TypeError that killed the rest
  // of the frame, every single use.
  { const p = mk({ ax: -1 });
    try { p.executeAttack(STATE.ATTACK_SPECIAL); } catch (e) { errors.push('WIRE-STEP threw on press: ' + e.message); }
    let died = null;
    try { for (let i = 0; i < 14; i++) p.update(0.02); } catch (e) { died = e.message; }
    if (died) errors.push('WIRE-STEP still throws as the vanish expires: ' + died);
    else notes.push('WIRE-STEP vanish expires cleanly'); }

  // ---- 4h. METEOR BREAK'S LANDING IS STILL THE METEOR. slamPhase clears at TOUCHDOWN while
  // the attack lives another SLAM_LAG, so a guard that reads only slamPhase drew the Form-2
  // Tsuki over the floor detonation. In stance it must draw exactly what Form 1 draws.
  { const land = stance => {
      const p = mk({ stance: stance ? 1 : 0, air: 1, down: 1 });
      try { p.executeAttack(STATE.ATTACK_HEAVY); } catch (e) { errors.push('meteor threw ' + e.message); }
      p.slamPhase = 0; p.slamRecover = 0.30; p.isGrounded = true; p.attackAnim = null;
      p.recoveryTimer = 0.38; p.recoveryTotal = 0.38; p.state = STATE.ATTACK_HEAVY;
      return drew(p);
    };
    const a = land(false), b = land(true);
    if (/^f2_/.test(b)) errors.push('the METEOR landing draws the Form-2 row "' + b + '"');
    else if (a !== b) errors.push('METEOR landing differs by stance: Form 1 "' + a + '" vs stance "' + b + '"');
    else notes.push('METEOR landing -> ' + b + ' in BOTH forms (parity)'); }

  // ---- 4i. THE STANCE OWNS EVERY SPECIAL. Fwd+Special is a Form-1 volley filed ~1700 lines
  // above the Kage-Nui branch, so in stance it fired anyway — and once it started charging it
  // ate 15 a press for a move the stance is not supposed to have.
  { const p = mk({ stance: 1, ax: 1 }); const before = p.stamina; p.kageCastCd = 0;
    try { p.executeAttack(STATE.ATTACK_SPECIAL); } catch (e) { errors.push('stance Fwd+Special threw ' + e.message); }
    if ((p.projectiles || []).length) errors.push('stance Fwd+Special fired the Form-1 volley instead of the wire');
    else if (!(p.kageCastT > 0)) errors.push('stance Fwd+Special cast nothing — the wire never started');
    else notes.push('stance Fwd+Special -> the wire (spent ' + Math.round(before - p.stamina) + ', KAGE_COST)'); }

  // ---- 4j. NO STATUE ECHO. Dropping the stance wipes the tape, and castKageKami's only
  // refusal was 'length < 2', satisfied ~67ms later — so a cast right after a drop bought a
  // frozen shadow. The test has to be HISTORY, not sample count.
  { const p = mk({ stance: 1 });
    for (let i = 0; i < 40; i++) { p.drawCell = F.f2_heavy3_3; p.kageTapeT = 0; p.recordKageTape(1 / 30); animClock += 1 / 30; }
    p.toggleKageNui();
    for (let i = 0; i < 3; i++) { p.kageTapeT = 0; p.recordKageTape(1 / 30); animClock += 1 / 30; }
    const before = p.stamina;
    try { p.castKageKami(); } catch (e) { errors.push('castKageKami threw ' + e.message); }
    if (p.clone) errors.push('a Kage-Kami cast on a ' + p.kageTape.length + '-sample tape spawned a statue');
    else if (p.stamina !== before) errors.push('the refused cast still charged ' + (before - p.stamina) + ' chakra');
    else notes.push('cast on a short tape -> refused, nothing charged'); }

  // ---- 5. FORM 1 IS UNTOUCHED. The kick tier keeps these presses when the stance is off.
  hit('F1 crouch Light', { down: 1 },  STATE.ATTACK_LIGHT, 'ksweep', { wantKick: 'sweep' });
  hit('F1 fwd Light',    { ax: 1 },    STATE.ATTACK_LIGHT, 'kpush',  { wantKick: 'push' });
  hit('F1 back Light',   { ax: -1 },   STATE.ATTACK_LIGHT, 'kheel',  { wantKick: 'heel' });
  { const p = mk(); try { p.executeAttack(STATE.ATTACK_HEAVY); } catch (e) { errors.push('F1 heavy threw ' + e.message); }
    const f = drew(p);
    if (/^f2_/.test(f)) errors.push('F1 neutral Heavy drew a Form-2 row: ' + f);
    notes.push('F1 neutral Heavy -> ' + f); }

  // ---- 6. NO OTHER FIGHTER CAN REACH THESE ROWS
  for (const s of NINJA_ROSTER) {
    if (s.name.toLowerCase() === 'shin') continue;
    const man = SPRITES[s.name.toLowerCase()];
    if (man && man.frames && man.frames.f2_light1_1 !== undefined && s.id !== 3)
      errors.push(s.name + ' carries an f2_light1 row — shinF2Frame gates on spec.id 2, but check the draw order');
  }

  return { errors, notes };
})()`;

let out;
try { out = await evaluate(script); }
finally {
  try { ws.close(); } catch {}
  // ⛔ LEAVE IT RUNNING ON PURPOSE. Chrome cannot restart within a few seconds of being killed
  // on this box, so tearing it down here is what made consecutive runs fail on the LAUNCH and
  // report it like a game defect. The next run reuses this browser and force-reloads it, which
  // is both faster and the only version of reuse that cannot grade stale code.
  if (chrome) chrome.unref();
}

for (const n of out.notes) console.log('  ·', n);
if (out.errors.length) {
  console.error('\nFAIL');
  for (const e of out.errors) console.error('  ✗', e);
  process.exit(1);
}
console.log('\nSHIN KAGE-NUI: the owner\'s nine-family table holds, and Form 1 does not move.');
console.log(`(a headless Chrome is parked on :${CDP} for the next run — close it with: pkill -f "remote-debugging-port=${CDP}")`);
