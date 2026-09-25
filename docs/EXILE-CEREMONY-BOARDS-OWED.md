# EXILE — the three ceremony boards still owed

**2026-09-10 · SHODO-EDITION · reviewed on `localhost:9101`.** Hand this to the generator.
No engine work follows any of them: `ceremonyFrame` and `tauntCells` are LIVE and
art-gated (`node tools/check_ceremony.mjs` → OK). A sheet without the row draws what it
drew before; the day these cells land with the right keys, they play.

## Where the roster stands

| fighter | taunt | intro | win | ko |
|---|---|---|---|---|
| ember, executioner, shin, tsubasa | ✅ | ✅ | ✅ | ✅ |
| mizu | ✅ | — | — | — |
| **exile** | **—** | **—** | **—** | **—** |
| kael, mokurai, oni | — | — | — | — |

Exile is 197 cells with **zero** ceremony rows.

**Her `defeat-ko` board already exists and is approved** —
`art/production/exile/exile-shodo-defeat-ko-8f-v2-approved-review.png` (v1 and v2 are also
in `art/shodo-source/exile/`). That one is not owed: it is `ko1..8` waiting on your OK to
pack. The three below have no board anywhere on disk.

---

## House spec — every board

- ONE row of 8 frames, equal-width cards, ~1900–2000px wide total, on washi/parchment.
- Side profile, **figure faces LEFT**, same figure scale as her idle board
  (`exile-shodo-kusarigama-idle-8f-v5-safe-margin-approved-review`, body target **72.3px**
  packed) — match head size to the idle board, not the canvas.
- Feet on one consistent ground line; grounded poses never float.
- No drawn card borders, no drawn walls, floors or props — the stage provides those.
- Cel beats, not a cross-fade: each frame a distinct pose in reading order.

## Identity string — paste verbatim into all three prompts

> Chibi ninja, roughly 3 heads tall, strict side profile. NO HOOD. A huge windswept BLACK
> MANE with silver-white streaks, long and streaming behind her. A TAN CLOTH EYE-WRAP
> covering one eye with dark-red kanji brushed on it. A BLACK CLOTH MASK over nose and
> mouth; the one visible eye is pale and hard under a heavy dark brow. Pale skin. BLACK and
> charcoal ninja garb — wrapped sleeves, layered skirt panels over black trousers. A DEEP
> PURPLE SCARF at the neck and two long purple sash tails off the waist. TAN BANDAGE WRAPS
> on forearms, hands, shins and ankles. In one hand a KAMA SICKLE (silver curved blade, dark
> wrapped handle, red-brown grip). In the other a CHAIN with a heavy dark iron weight ball,
> links clearly readable.

**Chain laws** (the reject list): thrown = TAUT, no sag · hanging or circling = SAG, a
natural hanging curve · ONE continuous unbroken chain hand→ball on every frame · the sickle
never swaps hands, never duplicates · never a hood, never a faceless void, never both eyes
uncovered, never a katana or kunai, never red eyes, never gold or red FX.

**The ball — SPIKED. Settled.** Owner, Sep 23 2026: *"whatever it's right now, it's what
we going with"* — and what stands is a morningstar, roughly eight spikes. Her drawn cells
and every Shodō board carry it, and `Exile-Identity-True-Lock.md` was rewritten on Sep 11
to say the same, superseding his Aug 11 preference for a smooth ball. New boards draw it
spiked; nothing gets repainted.

One thing still disagrees and is NOT being changed unasked: the engine's **procedural**
chain (the links it draws during the grapple, `web/index.html`) renders a round smooth
ball and cites the dead Aug 11 call in its comment. Her grapple therefore swings a smooth
ball while every drawn cell of her carries a spiked one. Say the word and it becomes
spiked to match.

---

## 1. TAUNT — "Chain Orbit Dare" → keys `taunt1..8`

She never stops moving, so her taunt is the ball never stopping. A lazy vertical orbit at
her side, and the sickle tipped at the opponent like a question.

**Beats:** low guard, ball hanging and still → sickle hand drops loose, ball swings back,
chain SAGS → ball rises into a slow vertical orbit, chain straightening → orbit at the top,
chain TAUT at full extension, mane lifted by it → she tips her head and points the sickle
forward — the dare, ball still up → ball falls back through the orbit, sag returns → catch,
ball slaps into the wrap on her palm → shoulder roll, sash tails settle → her guard stance.

*Zero engine work: `tauntCells` has read `taunt1..N` since 782 and `executeTaunt` refuses a
fighter without the row.*

## 2. ROUND-START INTRO — "Chain Uncoil" → keys `intro1..8`

**Beat 8 must be her idle-guard pose**, matched to beat 1 of the idle board — the intro
holds its last cell through **FIGHT!**, so she opens on the guard the board ends in, not a
half-rise. This is the one hard constraint on this board.

**Beats:** standing loose and off-guard, chain coiled over the shoulder, sickle low →
head turns to the opponent, the one eye reads → she flicks the coil off her shoulder, links
spilling down → chain falls into a hanging sag from her fist, ball just off the floor →
sickle turns up into the lead hand, blade facing forward → half-step down into the low
stance, mane thrown forward → mane settles back, sash tails catching up → **her exact idle
guard**, chain sagging, ball at rest.

## 3. VICTORY — "Widow's Salute" → keys `win1..8`

The fastest body on the roster wins by going still. She catches the ball out of the air,
wraps the chain twice around her forearm, and lowers the blade across her chest.

**Beats:** guard, ball still swinging from the last exchange → she snaps the chain up and
CATCHES the ball at head height → ball in the palm, chain slack across the body → one wrap
of chain around the forearm, links laid over the tan bandage → second wrap, ball drawn in
tight against the fist → sickle brought across the chest, blade turned inward, no threat in
it → head lowers, mane falls forward over the shoulder → held salute, dead still, the one
eye up.

---

## Packing, when the boards land

```bash
python3 tools/sprites/pack_shodo_row.py exile <board_dir> taunt1 taunt2 taunt3 taunt4 taunt5 taunt6 taunt7 taunt8
```

Same command for `intro1..8`, `win1..8`, `ko1..8`. Append-only, one idle-anchored scale per
board, originals asserted byte-identical. Bump `SHEET_V` in the same commit. Frames and GIFs
at game cadence go to the owner before the sheet is touched.
