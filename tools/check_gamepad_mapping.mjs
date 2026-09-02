// Gamepad mapping + edge behaviour check (docs/COMPETITIVE-GAMEPAD-IMPLEMENTATION-BRIEF.md §5).
//
// ponytail: this runs the REAL pollGamepads source out of web/index.html inside a
// tiny stub, instead of driving a headless browser. pollGamepads touches exactly
// four things — navigator.getGamepads, the PAD_* tables, its own padHeld state and
// window.dispatchEvent — so stubbing those is a dozen lines, while the CDP route the
// other checks use needs a running server AND a working Chrome debug port (dead on
// this Mac). No browser, no framework, no server: `node tools/check_gamepad_mapping.mjs`.
//
// It fails if a button moves, if a held button repeats, if a release goes missing, if
// the dead zone drifts, or if a second pad can puppet a CPU opponent.
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const html = readFileSync(path.join(root, 'web/index.html'), 'utf8');

const start = html.indexOf('const PAD_KEYS = [');
const endMark = '\n        }\n';                       // closes pollGamepads
const end = html.indexOf(endMark, html.indexOf('function pollGamepads()'));
if (start < 0 || end < 0) { console.error('CHECK FAIL: could not find the gamepad block in web/index.html'); process.exit(1); }
const src = html.slice(start, end + endMark.length);

let p2Human = true;
const events = [];
const statusEl = { textContent: '' };
const sandbox = {
  navigator: { getGamepads: () => [null, null] },
  window: { dispatchEvent: e => events.push(e) },
  isP2Human: () => p2Human,
  // pollGamepads also writes the #pad-status line; give it somewhere to write.
  document: { getElementById: id => (statusEl.id = id, statusEl) },
  KeyboardEvent: class { constructor(type, init) { this.type = type; this.code = init.code; } },
};
vm.createContext(sandbox);
vm.runInContext(src, sandbox);
const { pollGamepads } = sandbox;

const pad = (buttons = [], axes = [0, 0]) => ({
  connected: true, mapping: 'standard',
  buttons: Array.from({ length: 16 }, (_, i) => ({ pressed: buttons.includes(i) })),
  axes,
});
// one poll with the given pads; returns the keydowns and keyups it produced
function poll(p1, p2 = null) {
  events.length = 0;
  sandbox.navigator.getGamepads = () => [p1, p2];
  pollGamepads();
  return {
    down: events.filter(e => e.type === 'keydown').map(e => e.code),
    up: events.filter(e => e.type === 'keyup').map(e => e.code),
  };
}
const release = () => poll(pad([]));            // drop everything between cases

let fails = 0, ran = 0;
const eq = (a, b) => JSON.stringify([...a].sort()) === JSON.stringify([...b].sort());
function check(name, got, want) {
  ran++;
  const ok = eq(got, want);
  if (!ok) { fails++; console.error(`  FAIL  ${name}\n        got  ${JSON.stringify(got)}\n        want ${JSON.stringify(want)}`); }
  else console.log(`  ok    ${name}`);
}

console.log('gamepad mapping — P1 face cluster (physical position, not printed label)');
for (const [btn, code, label] of [[0, 'KeyF', 'South = Light'], [2, 'KeyJ', 'West = Medium'],
                                  [3, 'KeyG', 'North = Heavy'], [1, 'KeyH', 'East = Special']]) {
  release();
  check(`${label} presses ${code}`, poll(pad([btn])).down, [code]);
  check(`${label} releases ${code}`, poll(pad([])).up, [code]);
}
console.log('gamepad mapping — shoulders, triggers, system, directions');
for (const [btn, codes, label] of [[4, ['KeyC'], 'LB = Block/Poof'], [5, ['KeyC'], 'RB = Block/Poof'],
                                   [6, ['KeyF', 'KeyG'], 'LT = throw macro'], [7, ['KeyF', 'KeyG'], 'RT = throw macro'],
                                   [8, ['KeyV'], 'Back = stance'], [9, ['Escape'], 'Start = pause'],
                                   [12, ['KeyW'], 'D-pad up'], [13, ['KeyS'], 'D-pad down'],
                                   [14, ['KeyA'], 'D-pad left'], [15, ['KeyD'], 'D-pad right']]) {
  release();
  check(`${label} presses ${codes.join('+')}`, poll(pad([btn])).down, codes);
  check(`${label} releases ${codes.join('+')}`, poll(pad([])).up, codes);
}

console.log('edge behaviour');
release();
poll(pad([2]));
check('a held button does not repeat (poll 2)', poll(pad([2])).down, []);
check('a held button does not repeat (poll 3)', poll(pad([2])).down, []);
check('unplugging mid-hold releases it', poll(null).up, ['KeyJ']);
release();
poll(pad([4, 14]));
check('unplugging mid-hold releases EVERY held key', poll(null).up, ['KeyC', 'KeyA']);

console.log('stick dead zone (0.4)');
release();
check('axis 0.39 walks nobody', poll(pad([], [0.39, 0])).down, []);
check('axis 0.41 walks right', poll(pad([], [0.41, 0])).down, ['KeyD']);
check('axis back under 0.4 releases', poll(pad([], [0.2, 0])).up, ['KeyD']);
release();
check('axis -0.41 walks left', poll(pad([], [-0.41, 0])).down, ['KeyA']);
const swap = poll(pad([], [0.41, 0]));
check('crossing the stick to +0.41 presses right', swap.down, ['KeyD']);
check('...and releases left, so nothing sticks', swap.up, ['KeyA']);
release();
check('vertical axis -0.41 is up', poll(pad([], [0, -0.41])).down, ['KeyW']);
release();

console.log('P2 seat');
p2Human = true;
check('pad 2 drives P2 when P2 is human', poll(pad([]), pad([2])).down, ['KeyU']);
poll(pad([]), pad([]));
p2Human = false;
check('pad 2 CANNOT puppet a CPU opponent', poll(pad([]), pad([2])).down, []);
check('...not even a direction', poll(pad([]), pad([], [0.9, 0])).down, []);
p2Human = true;
release(); poll(pad([]), pad([]));

console.log('pad-status line (select screen only, never over the canvas)');
release(); poll(pad([]), null);
check('one pad connected reads P1 only', [statusEl.textContent], ['P1 PAD \u2713   P2 PAD \u2014']);
poll(pad([]), pad([]));
check('two pads connected read both', [statusEl.textContent], ['P1 PAD \u2713   P2 PAD \u2713']);
poll(null, null);
check('no pad clears the line', [statusEl.textContent], ['']);

console.log('non-standard mapping is ignored, never guessed');
const weird = { ...pad([0, 2, 3]), mapping: '' };
check('a non-standard pad sends nothing', poll(weird).down, []);

console.log(fails ? `\nCHECK FAIL — ${fails} of ${ran} assertions failed` : `\nCHECK PASS — ${ran} assertions`);
process.exit(fails ? 1 : 0);
