// TWO RULES, ONE PASS, over web/index.html.
//
// 1. Every entry into an ATTACK_* state clears the ~35 art latches FIRST, or the frame
//    picker draws the PREVIOUS move (documented failure: Fwd+Heavy then Guard+Heavy drew
//    the drive stab under the slip). `clearMoveArt()` is the one clear site.
//    Exempt by call graph, not by convenience: `_executeAttack` owns the clear for itself
//    and for the three methods it is the sole caller of.
//
// 2. Nobody hand-writes a second copy of that latch list. A copy drifts the moment a new
//    move adds a latch to one site and not the other — which is exactly how the
//    recovery-end teardown ended up clearing 12 of the 35.
import { readFileSync } from 'node:fs';

const SRC = new URL('../web/index.html', import.meta.url);
const lines = readFileSync(SRC, 'utf8').split('\n');
const ENTRY_EXEMPT = new Set(['_executeAttack', 'triggerSpecialAction', 'castKageNui', 'reelInZip']);
const LIST_EXEMPT  = new Set(['clearMoveArt', 'constructor']);   // the one clear site + field decls

let method = '?', cleared = false, run = 0, runStart = 0;
const leaks = [], dupes = [];

const endRun = () => {
  if (run >= 5 && !LIST_EXEMPT.has(method)) dupes.push(`web/index.html:${runStart} — ${run} latches in ${method}()`);
  run = 0;
};

lines.forEach((ln, i) => {
  const m = ln.match(/^ {12}([A-Za-z_]\w*)\(.*\)\s*\{/);
  if (m) { endRun(); method = m[1]; cleared = false; }

  if (/this\.clearMoveArt\(\)/.test(ln)) cleared = true;
  if (/this\.state\s*=\s*STATE\.ATTACK_/.test(ln) && !cleared && !ENTRY_EXEMPT.has(method))
    leaks.push(`${method}() @ web/index.html:${i + 1}`);

  if (/^\s*this\.\w+ = (false|null);/.test(ln)) { if (run++ === 0) runStart = i + 1; }
  else if (!/^\s*(\/\/|$)/.test(ln)) endRun();
});
endRun();

const fail = (title, rows) => { console.error(title); for (const r of rows) console.error('  ' + r); };
if (leaks.length) fail(`STALE ART LATCH LEAK — ${leaks.length} attack entr${leaks.length > 1 ? 'ies' : 'y'} skip clearMoveArt():`, leaks);
if (dupes.length) fail('DUPLICATE LATCH LIST — clearMoveArt() is the one clear site:', dupes);
if (leaks.length || dupes.length) process.exit(1);
console.log('OK — every ATTACK_* entry clears first, and clearMoveArt() is the only clear site.');
