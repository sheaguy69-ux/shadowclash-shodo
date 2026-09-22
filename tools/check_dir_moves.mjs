// DIR_MOVES / DIR_SPECIALS integrity. Three silent-failure classes, none of which throw:
//
// 1. `track.length !== cellCount`. attackCellIndex only uses a track when its length
//    EQUALS the cell count; otherwise it silently falls through to the 5/6-cell default
//    exposures or a linear map. The authored timing is then ignored with no error, which
//    is invisible until someone watches the move frame by frame.
// 2. An art row the manifest does not have. `ma` is built by walking F[art+i] from 1, so a
//    missing row yields an EMPTY array and the move draws nothing.
// 3. `launch: true` with no `launchVy` — the box tags as a launcher and applies no impulse.
import { readFileSync, readdirSync } from 'node:fs';
import { ROSTER } from './roster.mjs';

const ROOT = new URL('../', import.meta.url);
const src = readFileSync(new URL('web/index.html', ROOT), 'utf8');

const NAMES = ROSTER;   // roster.mjs reads NINJA_ROSTER; a retired fighter leaves with it
const frames = NAMES.map(n =>
  JSON.parse(readFileSync(new URL(`web/assets/sprites/${n}.json`, ROOT), 'utf8')).frames);

const grab = name => {
  const i = src.indexOf(`const ${name} = {`);
  if (i < 0) throw new Error(`${name} not found`);
  let d = 0, j = src.indexOf('{', i);
  for (let k = j; k < src.length; k++) {
    if (src[k] === '{') d++;
    else if (src[k] === '}' && --d === 0) return src.slice(j, k + 1);
  }
  throw new Error(`${name} unterminated`);
};
// The tables are JS object literals, not JSON — evaluate them in place.
const DIR_MOVES = eval(`(${grab('DIR_MOVES')})`);
const DIR_SPECIALS = eval(`(${grab('DIR_SPECIALS')})`);

const cellCount = (F, art) => { let n = 0; while (F[art + (n + 1)] !== undefined) n++; return n; };

const fails = [];
for (const [table, moves] of [['DIR_MOVES', DIR_MOVES], ['DIR_SPECIALS', DIR_SPECIALS]]) {
  for (const [key, e] of Object.entries(moves)) {
    const id = Number(key.split(':')[0]);
    const F = frames[id];
    const n = cellCount(F, e.art);
    const where = `${table}['${key}'] (${NAMES[id]}, art '${e.art}')`;

    if (n === 0) fails.push(`${where}: art row MISSING from the manifest — the move draws nothing`);
    else if (e.track && e.track.length !== n)
      fails.push(`${where}: track has ${e.track.length} stops for ${n} cells — the track is SILENTLY IGNORED`);

    for (const b of e.box || []) {
      const o = b[5] || {};
      if (o.launch && o.launchVy === undefined)
        fails.push(`${where}: box tagged launch with no launchVy — no impulse is applied`);
    }
  }
}

if (fails.length) {
  console.error(`DIRECTIONAL MOVE TABLE — ${fails.length} silent failure${fails.length > 1 ? 's' : ''}:`);
  for (const f of fails) console.error('  ' + f);
  process.exit(1);
}
console.log(`OK — ${Object.keys(DIR_MOVES).length + Object.keys(DIR_SPECIALS).length} directional moves: every track matches its cell count, every art row exists, every launcher carries an impulse.`);
