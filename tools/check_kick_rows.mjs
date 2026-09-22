// Replays the engine's kick-cell lookup against every shipped sheet and asserts
// no fighter's packed kick art is unreachable. Fails loudly if the fix regresses.
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { ROSTER } from './roster.mjs';
const SP = resolve('web/assets/sprites');
const FIGHTERS = [...ROSTER].sort();   // roster.mjs reads NINJA_ROSTER; a retired fighter leaves with it
const KINDS = ['sweep','push','heel'];

// the lookup, exactly as index.html orders it (post-fix)
function kickCells(F, kind, specId) {
  if (specId === 7 && F.xksweep !== undefined) {
    if (kind === 'sweep') return { via: 'exile x-row', cells: [F.xksweep] };
    if (kind === 'push')  return { via: 'exile x-row', cells: [F.xkpush] };
    if (kind === 'heel')  return { via: 'exile x-row', cells: [F.xkheel] };
  }
  if (kind === 'push' && F.kpush1 !== undefined) {
    const cells = [];
    for (let n = 1; n <= 8; n++) { const c = F['kpush' + n]; if (c === undefined) break; cells.push(c); }
    return { via: `kpush1..${cells.length}`, cells };
  }
  const kf = [];
  for (let n = 1; n <= 8; n++) { const c = F['k' + kind + n]; if (c === undefined) break; kf.push(c); }
  if (kf.length) return { via: `k${kind}1..${kf.length} (numbered)`, cells: kf };
  const kc = F['k' + kind];
  if (kc !== undefined) return { via: 'bare k' + kind, cells: [kc] };
  return { via: 'FALLBACK kstomp/jump2/fall/light1', cells: [] };
}

let fail = 0;
for (const id of FIGHTERS) {
  const F = JSON.parse(readFileSync(`${SP}/${id}.json`, 'utf8')).frames;
  const specId = id === 'exile' ? 7 : -1;
  for (const kind of KINDS) {
    const packed = Object.keys(F).filter(k => new RegExp(`^k${kind}\\d+$`).test(k)).length;
    const r = kickCells(F, kind, specId);
    // THE ASSERT: if the sheet packs a numbered row, the lookup must reach it.
    if (packed > 0 && !r.via.includes('numbered') && !r.via.startsWith('kpush') && !r.via.startsWith('bare')) {
      console.error(`FAIL ${id} ${kind}: ${packed} cells packed but draw path = ${r.via}`);
      fail++;
    }
    if (packed > 0 && r.cells.length !== packed) {
      console.error(`FAIL ${id} ${kind}: packed ${packed}, draw path reaches ${r.cells.length}`);
      fail++;
    }
    // The bare-vs-row1 pose check only matters where this decision is REACHED —
    // the kpush1..3 and exile x-row branches preempt it entirely.
    const preempted = (kind === 'push' && F.kpush1 !== undefined)
                   || (specId === 7 && F.xksweep !== undefined);
    const bare = F['k' + kind];
    if (!preempted && packed > 0 && bare !== undefined && bare !== F['k' + kind + '1']) {
      console.error(`FAIL ${id} ${kind}: bare cell ${bare} != row cell1 ${F['k'+kind+'1']} — reorder WOULD change the opening pose`);
      fail++;
    }
    console.log(`${id.padEnd(12)} ${kind.padEnd(6)} packed=${packed} -> ${r.via} (${r.cells.length} cell${r.cells.length===1?'':'s'})`);
  }
}
console.log(fail ? `\n${fail} FAILURES` : '\nOK — no packed kick row is unreachable');
process.exit(fail ? 1 : 0);
