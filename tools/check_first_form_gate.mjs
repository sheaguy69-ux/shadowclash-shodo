#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';

const lane = readFileSync(new URL('./lane.py', import.meta.url), 'utf8');
const html = readFileSync(new URL('../web/index.html', import.meta.url), 'utf8');
const agents = readFileSync(new URL('../AGENTS.md', import.meta.url), 'utf8');
const claude = readFileSync(new URL('../CLAUDE.md', import.meta.url), 'utf8');
const serve = readFileSync(new URL('./serve.py', import.meta.url), 'utf8');

const ports = lane.match(/^ALLOWED_PORTS\s*=\s*\{([^}]+)\}\s*$/m);
assert.ok(ports, 'lane ALLOWED_PORTS declaration is missing');
assert.deepEqual(ports[1].split(',').map(Number).sort((a, b) => a - b), [9100, 9101, 9102],
  'lane must allow exactly 9100, 9101, and 9102');

for (const [name, text] of [['AGENTS.md', agents], ['CLAUDE.md', claude], ['tools/serve.py', serve]]) {
  assert.match(text, /recovered rollback[\s\S]{0,100}:9100/i, `${name} must name recovered rollback :9100`);
  assert.match(text, /Shodō[\s\S]{0,100}:9101/i, `${name} must name Shodō :9101`);
  assert.match(text, /approved-art gallery[\s\S]{0,100}:9102/i, `${name} must name the gallery :9102`);
}
assert.match(serve, /PORT\s*=\s*int\(sys\.argv\[1\]\)\s*if len\(sys\.argv\) > 1 else 9101/,
  'serve.py default must be :9101 while preserving explicit port arguments');
assert.match(agents, /`python3 tools\/serve\.py 9101 web`/,
  'AGENTS operator guidance must provide the Shodō :9101 command');
assert.match(claude, /`python3 tools\/serve\.py 9101 web`/,
  'CLAUDE operator guidance must provide the Shodō :9101 command');
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
