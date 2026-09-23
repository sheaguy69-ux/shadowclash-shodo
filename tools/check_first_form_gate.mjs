#!/usr/bin/env node
import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';

const lane = readFileSync(new URL('./lane.py', import.meta.url), 'utf8');
const html = readFileSync(new URL('../web/index.html', import.meta.url), 'utf8');
const agents = readFileSync(new URL('../AGENTS.md', import.meta.url), 'utf8');
const claude = readFileSync(new URL('../CLAUDE.md', import.meta.url), 'utf8');
const serve = readFileSync(new URL('./serve.py', import.meta.url), 'utf8');
const watch = readFileSync(new URL('./watch_game.py', import.meta.url), 'utf8');
const TOOLS = dirname(fileURLToPath(import.meta.url));

const ports = lane.match(/^ALLOWED_PORTS\s*=\s*\{([^}]+)\}\s*$/m);
assert.ok(ports, 'lane ALLOWED_PORTS declaration is missing');
assert.deepEqual(ports[1].split(',').map(Number).sort((a, b) => a - b), [9100, 9101, 9102],
  'lane must allow exactly 9100, 9101, and 9102');

// ⛔ :9101 IS THE TREE (owner, Sep 22 2026). This used to require all three rulebook files
// to recite the three-port split in one exact phrasing, which pinned WORDING rather than
// behaviour — commit 879 rewrote the rulebook, kept the ruling, and broke this gate for
// changing the sentence around it. What matters is that the TOOLS point at his tree, so
// that is what is asserted now. :9100 and :9102 stay reachable; they are just not defaults.
assert.match(serve, /PORT\s*=\s*int\(sys\.argv\[1\]\)\s*if len\(sys\.argv\) > 1 else 9101/,
  'serve.py default must be :9101 while preserving explicit port arguments');
assert.match(watch, /GAME_URL = os\.environ\.get\('SHADOWCLASH_URL', 'http:\/\/localhost:9101\/index\.html'\)/,
  'watch_game.py must default to :9101 — every check_*.py in tools/ inherits this URL');
for (const [name, text] of [['AGENTS.md', agents], ['CLAUDE.md', claude]])
  assert.match(text, /:9101/, `${name} must still name :9101 as the tree`);

// AND NO TOOL MAY QUIETLY DEFAULT BACK. A single re-introduced `port = 9100` sends a whole
// harness at the rollback tree while the work is committed here — the exact split that made
// an agent "STEAL 9100 from whoever held it just to run a probe".
const toolFiles = readdirSync(TOOLS).filter(f => (f.endsWith('.mjs') || f.endsWith('.py')) && !f.includes(' 2.'));
const offenders = [];
for (const f of toolFiles) {
  if (f === 'lane.py' || f === 'check_first_form_gate.mjs') continue;   // both legitimately name all three
  // CODE, not prose: watch_game.py documents the :9100 override in a comment on purpose,
  // and the help strings name it too. Strip comment lines before testing, or the gate
  // fails on its own instructions.
  const t = readFileSync(join(TOOLS, f), 'utf8')
    .split('\n').filter(l => !/^\s*(#|\/\/)/.test(l)).join('\n');
  if (/(?:\bport\s*=\s*|PORT\s*\|\|\s*|localhost:|127\.0\.0\.1:)9100\b/.test(t)) offenders.push(f);
}
assert.deepEqual(offenders, [], `these tools still default to :9100 — ${offenders.join(', ')}`);
assert.match(html, /const FIRST_FORM_ONLY = true;/,
  'first-form-only runtime constant is missing');
assert.match(html, /function secondFormBlocked\(player\)/,
  'shared second-form activation guard is missing');
// 790 GAVE CHUDAN ITS SHODO ART and let that ONE form out of the gate, so for a while the
// guard was not modeKey's first statement and this file pinned the NARROWER contract.
// Owner, Sep 22 2026 — "put everyone second on pause" — puts it back: no bypass at all,
// for anyone. The guard is the first statement again, and `chudanPress` must be GONE
// rather than merely unused, or the next edit re-wires a bypass that still compiles.
const modeKey = html.match(/modeKey\(\) \{([\s\S]*?)\n            \}/);
assert.ok(modeKey, 'modeKey definition is missing');
assert.match(modeKey[1], /^\s*(\/\/[^\n]*\n\s*)*if \(secondFormBlocked\(this\)\) return;/,
  'modeKey is not guarded by secondFormBlocked as its first statement');
// CODE, not prose: the comment above the guard names the deleted bypass on purpose, so
// strip comments before asserting the identifier is gone, or the gate fails on its own
// changelog.
const modeKeyCode = modeKey[1].replace(/^\s*\/\/.*$/gm, '');
assert.doesNotMatch(modeKeyCode, /chudanPress/,
  'the chudan bypass is back — every second mode is paused (owner, Sep 22 2026)');

// THE THREE THAT NEVER CAME THROUGH modeKey. The V-key gate was never the whole story:
// the Crack is on hold Down+C, and the two boss modes fire off a timer with no input at
// all. Each is pinned at its own trigger, because that is the only place they can be
// stopped — and because a pause that only covers the button is not a pause.
assert.match(html, /karma >= KARMA_MAX && !secondFormBlocked\(this\)/,
  "THE CRACK's full-karma trigger is not paused");
for (const [who, hp] of [['6', 'BOSS_ENLIGHT_HP'], ['7', 'BOSS_FRENZY_HP']]) {
  const re = new RegExp(`spec\\.id === ${who} && !this\\.boss\\w+Used && this\\.isCpuDriven\\(\\)\\s*\\n\\s*&& !secondFormBlocked\\(this\\)`);
  assert.match(html, re, `the CPU second mode gated on ${hp} is not paused`);
}

// EVERY MODE FLAG CLEARS, not just the three V stances — a mode set before the switch
// flipped has no other way out, and updateStance() calls this every frame for that.
const blocked = html.match(/function secondFormBlocked\(player\) \{([\s\S]*?)\n        \}/);
assert.ok(blocked, 'secondFormBlocked definition is missing');
for (const flag of ['kageNui', 'sakate', 'hanbo', 'chudan', 'cracked', 'crackTimer',
                    'crackIntro', 'frenzyTimer'])
  assert.match(blocked[1], new RegExp(`player\\.${flag} = `), `secondFormBlocked leaves ${flag} set`);
const stance = html.match(/updateStance\(\) \{([\s\S]*?)\n            \}/);
assert.ok(stance, 'updateStance definition is missing');
assert.match(stance[1], /secondFormBlocked\(this\)/,
  'updateStance is not the per-frame strand guard for paused modes');

// ...AND THE MOVE LIST MUST NOT ADVERTISE THEM. A list promising a button that does
// nothing is exactly the hole WIRE-STEP sat in for weeks.
assert.match(html, /const SECOND_FORM_LINE = /,
  'the second-mode move-list filter is missing');
assert.match(html, /!FIRST_FORM_ONLY \|\| !SECOND_FORM_LINE\.test\(line\)/,
  'the move list is not filtered by SECOND_FORM_LINE');
const movesList = html.match(/const MOVES_LIST = \{([\s\S]*?)\n        \};/);
assert.ok(movesList, 'MOVES_LIST is missing');
const lineRe = html.match(/const SECOND_FORM_LINE = (\/.*?\/);/);
const filter = eval(lineRe[1]);
for (const doc of ['V — CHUDAN', 'V (P2: K) — CHAMPION MODE', 'THE CRACK'])
  assert.ok([...movesList[1].matchAll(/"([^"]*)"|'([^']*)'/g)]
      .map(m => m[1] ?? m[2]).filter(l => l.includes(doc)).every(l => filter.test(l)),
    `a move-list line documenting "${doc}" is not hidden while second modes are paused`);

for (const method of ['toggleKageNui', 'toggleSakate', 'toggleHanbo']) {
  const body = html.match(new RegExp(`${method}\\(\\) \\{([\\s\\S]*?)\\n            \\}`));
  assert.ok(body, `${method} definition is missing`);
  assert.match(body[1], /secondFormBlocked\(this\)/, `${method} is not guarded`);
}

for (const router of ['shinF2Frame', 'tsubasaF2Frame', 'mizuF2Frame']) {
  const body = html.match(new RegExp(`function ${router}\\(p, F\\) \\{([\\s\\S]*?)\\n        \\}`));
  assert.ok(body, `${router} definition is missing`);
  assert.match(body[1], /secondFormBlocked\(p\)/, `${router} is not guarded`);
}

console.log('FIRST-FORM GATE: PASS');
