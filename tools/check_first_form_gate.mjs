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
// 790 GAVE CHUDAN ITS SHODO ART and let that ONE form out of the gate, so the guard is
// no longer modeKey's first statement. The contract did not go away, it got narrower —
// so pin the narrower one: the bypass exists, and it is spelled out in terms of the
// Executioner plus an `idle_chudan` cell. Anything wider stops matching.
const modeKey = html.match(/modeKey\(\) \{([\s\S]*?)\n            \}/);
assert.ok(modeKey, 'modeKey definition is missing');
assert.match(modeKey[1], /if \(!chudanPress && secondFormBlocked\(this\)\) return;/,
  'modeKey is not guarded');
assert.match(modeKey[1], /const chudanPress = this\.spec\.id === 0\b/,
  'the chudan bypass is not pinned to the Executioner');
assert.match(modeKey[1], /frames\?\.idle_chudan !== undefined/,
  'the chudan bypass is not pinned to its shodo art');

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
