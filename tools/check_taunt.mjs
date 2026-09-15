// TAUNT — the four ways it can be wired and still do nothing, none of which throw.
//
// 1. THE INPUT NEVER REACHES IT. fireCombatKey is the one funnel every source uses;
//    a taunt key added to the pad map but not to the funnel is a dead button, and the
//    seat gate means P2's line must sit inside the p2Live block or a CPU-driven P2
//    taunts on the human's keypress.
// 2. THE ART IS NEVER DRAWN. tauntT holds STATE.IDLE on purpose, so if tauntFrame is
//    not consulted before the state switch the idle cell paints straight over it and
//    the taunt is invisible while still costing the player 0.8s.
// 3. THE ROW IS NOT ON THE SHEET. `taunt1..N` walks from 1: a gap at any index ends
//    the row early, and taunt1 absent means the fighter silently cannot taunt at all.
// 4. IT NEVER ENDS. tauntT is a countdown with no state of its own — every place that
//    zeroes dashTimer/rollTimer for a transient action must zero it too, or a taunt
//    interrupted by a throw or a round reset resumes afterwards.
//
// Also asserts the frame picker's arithmetic directly, which is the one piece of real
// logic here: a one-shot row must reach its LAST beat and never index past it.
import { readFileSync } from 'node:fs';

const ROOT = new URL('../', import.meta.url);
const src = readFileSync(new URL('web/index.html', ROOT), 'utf8');
const NAMES = ['executioner', 'mizu', 'shin', 'tsubasa', 'ember', 'kael', 'mokurai', 'exile', 'oni'];

const fails = [];
const need = (cond, msg) => { if (!cond) fails.push(msg); };

// --- 1. the input path -------------------------------------------------------
need(/if \(code === 'KeyX'\) player1\.executeTaunt\(\);/.test(src),
  "fireCombatKey has no KeyX -> player1.executeTaunt() line — P1's taunt key is dead");
need(/if \(code === 'KeyN'\) player2\.executeTaunt\(\);/.test(src),
  "fireCombatKey has no KeyN -> player2.executeTaunt() line — P2's taunt key is dead");
// P2's line must be INSIDE the `if (p2Live) {` block, like every other P2 trigger.
const p2Open = src.indexOf('// Player 2 Combat Triggers');
const p2N = src.indexOf("code === 'KeyN'");
need(p2Open > 0 && p2N > p2Open,
  "P2's taunt is not in the p2Live block — a CPU-driven P2 would taunt on the human's key");
need(/taunt:\s*'KeyX'/.test(src) && /taunt:\s*'KeyN'/.test(src),
  'PAD_KEYS is missing a taunt binding for one of the seats');
need(/^\s*10:\s*'taunt',/m.test(src),
  "PAD_BUTTONS has no button mapped to 'taunt' — the pad cannot reach it");

// --- 2. the draw path --------------------------------------------------------
const raw = src.indexOf('function spriteFrameIndexRaw');
const tauntCall = src.indexOf('tauntFrame(p, F)', raw);
const stateSwitch = src.indexOf('switch (p.state) {', raw);
need(raw > 0 && tauntCall > raw && (stateSwitch < 0 || tauntCall < stateSwitch),
  'tauntFrame is not consulted before the state switch — the idle cell paints over the taunt');

// --- 3. the art --------------------------------------------------------------
let withArt = 0;
for (const n of NAMES) {
  let man;
  try { man = JSON.parse(readFileSync(new URL(`web/assets/sprites/${n}.json`, ROOT), 'utf8')); }
  catch { continue; }                                  // not every name has a sheet here
  const F = man.frames;
  const keys = Object.keys(F).filter(k => /^taunt\d+$/.test(k));
  if (!keys.length) continue;                          // no taunt art is a valid state, not a fault
  withArt++;
  let run = 0;
  while (F['taunt' + (run + 1)] !== undefined) run++;
  need(run === keys.length,
    `${n}: taunt row has ${keys.length} keys but only ${run} are reachable from taunt1 — there is a GAP`);
  for (let i = 1; i <= run; i++) {
    const c = F['taunt' + i];
    need(Number.isInteger(c) && c >= 0 && c < man.cols,
      `${n}: taunt${i} = ${c} is not a cell on a ${man.cols}-cell sheet`);
  }
}
need(withArt > 0, 'not one sheet carries a taunt row — the feature can never fire');

// --- 4. the countdown gets cleared -------------------------------------------
for (const [label, re] of [
  // ⛔ THESE MATCH "tauntT IS CLEARED HERE", NOT ONE EXACT LIST OF TIMERS. They used to
  // pin the whole assignment chain down to its final `= 0;`, so adding ANY new committed
  // timer beside tauntT failed all four — which is exactly what happened when the Scarlet
  // Phantom Rush's rushT joined the chain, with the taunt still being cleared correctly at
  // every one of the five sites. The tail is now open.
  ['grapple bite',   /this\.dashTimer = this\.rollTimer = this\.tauntT =[^;]*0;\n\s*this\.isGrounded = false;/],
  ['throw start',    /this\.dashTimer = this\.rollTimer = this\.tauntT =[^;]*0;\s*\/\/ no 800px\/s lurch/],
  ['throw victim',   /opp\.dashTimer = opp\.rollTimer = opp\.tauntT =[^;]*0;/],
  ['took damage',    /this\.dashTimer = 0; this\.rollTimer = 0; this\.tauntT = 0;/],
  ['round reset',    /p\.dashTimer = p\.rollTimer = p\.rollRecover = p\.wallJumpLock = p\.clingTime = p\.tauntT =[^;]*0;/],
]) need(re.test(src), `tauntT is not cleared at the ${label} reset — an interrupted taunt resumes`);
need(/this\.tauntT > 0 && \(axis !== 0/.test(src),
  'the taunt cancel is not in handleMovement — nothing ends a taunt early');

// --- the picker's arithmetic, run for real -----------------------------------
const TAUNT_TIME = Number((src.match(/const TAUNT_TIME = ([\d.]+)/) || [])[1]);
need(TAUNT_TIME > 0, 'TAUNT_TIME is missing or not positive');
const pick = (cells, tauntT) =>
  cells[Math.min(cells.length - 1, Math.floor((1 - tauntT / TAUNT_TIME) * cells.length))];
for (const n of [1, 4, 6, 8, 12]) {
  const cells = Array.from({ length: n }, (_, i) => i);
  const seen = new Set();
  for (let t = TAUNT_TIME; t > 0; t -= 1 / 240) seen.add(pick(cells, t));
  need(pick(cells, TAUNT_TIME) === 0, `${n}-beat row does not start on beat 1`);
  need(pick(cells, 1e-9) === n - 1, `${n}-beat row never reaches its last beat`);
  need(pick(cells, 0) === n - 1, `${n}-beat row indexes past its end at tauntT 0`);
  need(seen.size === n, `${n}-beat row only reaches ${seen.size} of its ${n} beats`);
}

if (fails.length) {
  console.error(`TAUNT — ${fails.length} failure${fails.length > 1 ? 's' : ''}:`);
  for (const f of fails) console.error('  ' + f);
  process.exit(1);
}
console.log(`OK — taunt reaches both seats and the pad, draws above the state switch, clears at all `
  + `five transient resets, and plays every beat of a 1/4/6/8/12-cell row exactly once. `
  + `${withArt} sheet${withArt > 1 ? 's' : ''} carr${withArt > 1 ? 'y' : 'ies'} the art.`);
