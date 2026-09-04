// Run: node tools/check_portraits.mjs [http://localhost:9101/]
// Catches broken portrait URLs, altered approved pixels, and stale HUD faces after a tag.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import vm from 'node:vm';
const root = new URL('../', import.meta.url);
const html = readFileSync(new URL('web/index.html', root), 'utf8');
const source = html.match(/function portraitSrc\(spec\) \{[^\n]+\}/)?.[0];
const hud = html.match(/function setHudFighter\(side, spec\) \{[\s\S]*?\n        \}/)?.[0];
assert(source && hud, 'Shared portrait source and HUD updater must exist');
const nodes = Object.fromEntries([1, 2].flatMap(side =>
    ['name', 'portrait'].map(part => [`hud-p${side}-${part}`, {}])));
const context = vm.createContext({document:{getElementById:id=>nodes[id]}, ninjaFallback(){}});
vm.runInContext(source + '\n' + hud, context);
const fixtures = [
    [0,'Executioner','executioner'], [1,'Mizu','mizu'], [2,'Shin','shin'],
    [3,'Tsubasa','tsubasa'], [4,'Ember','ember'], [5,'Kael','kael'],
    [6,'Mokurai','mokurai'], [8,'Oni','oni-new-look']
];
const hash = data => createHash('sha256').update(data).digest('hex');
for (const [id,name,file] of fixtures) {
    const spec = {id,name};
    const src = context.portraitSrc(spec);
    const reference = readFileSync(new URL(`web/_review/shodo-face-cards-20260904/${name.toLowerCase()}.png`,root));
    const packed = readFileSync(new URL(`web/assets/ninjas/${file}.png`,root));
    assert.equal(hash(packed),hash(reference),`${name}: approved artwork changed`);
    const res = await fetch(new URL(src, process.argv[2] || 'http://localhost:9101/'));
    assert.equal(res.status,200,`${name}: portrait fails to load`);
    assert.equal(hash(Buffer.from(await res.arrayBuffer())),hash(reference),`${name}: server returns wrong portrait`);
    // Set both sides repeatedly: a new fighter must replace the previous face/name.
    for (const side of [1,2]) {
        context.setHudFighter(side,spec);
        assert.equal(nodes[`hud-p${side}-name`].textContent,name.toUpperCase());
        assert.equal(nodes[`hud-p${side}-portrait`].src,src);
        assert.equal(nodes[`hud-p${side}-portrait`].alt,name);
        assert.equal(typeof nodes[`hud-p${side}-portrait`].onerror,'function');
    }
}
for (const match of html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)) {
    if (match[1].trim()) new vm.Script(match[1]);
}
console.log(`${fixtures.length} approved portraits: local/server hashes match; both HUD sides update; inline JS parses.`);
