// THE ROSTER IS NINJA_ROSTER IN web/index.html — NOWHERE ELSE.
//
// Six gates kept their own hardcoded copy of the fighter list. When Oni was retired the
// copies went stale, and three of them (check_dir_moves, check_kick_rows, check_run_cells)
// stopped reporting anything at all: they CRASHED on his deleted sheet before the first
// assertion ran. A red gate is survivable; a gate that dies on line one is a gate that
// cannot catch the next regression.
//
// Reading the engine's own array means the next roster change moves one file, not seven.
import { readFileSync } from 'node:fs';

const html = readFileSync(new URL('../web/index.html', import.meta.url), 'utf8');
const open = html.indexOf('const NINJA_ROSTER = [');
if (open < 0) throw new Error('NINJA_ROSTER not found in web/index.html');
const block = html.slice(open, html.indexOf('\n        ];', open));

/** Sheet keys, roster order: the same `name.toLowerCase()` the sprite loader uses. */
export const ROSTER = [...block.matchAll(/^\s*name: "([^"]+)"/gm)].map(m => m[1].toLowerCase());
if (ROSTER.length < 2) throw new Error(`NINJA_ROSTER parsed as ${ROSTER.length} fighters`);
