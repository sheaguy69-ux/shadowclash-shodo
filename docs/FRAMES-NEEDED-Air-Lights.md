# GPT HANDOFF — the last two art fixes: MIZU and SHIN's air-light rows

**2026-08-07 (Fable 5), at SHEET_V 396.** With the four neutral air heavies
packed, the full-roster live sweeps leave exactly **two** flagged rows in the
whole game. Both are the 3-beat airborne LIGHT attack (`air1`, `air2`, `air3`).
Reference photos are in `docs/frame-handoff/air-light-brief/` and attached —
they show precisely which cells are kept and which are replaced.

- **MIZU:** `air3` is a smaller, flatter drawing from an older generation —
  it doesn't match the fighter in the two beats before it.
- **SHIN:** `air2` and `air3` are upside-down TUMBLE poses sitting on an
  attack row — when he presses light in the air, beat one is a clean shuriken
  strike and beats two and three are him falling head-first. See the photo.

**The ask: one page per fighter, THREE drawings each** — the full 3-beat move
redrawn as a unit so the beats match each other (mixing one new panel into an
old row is how these mismatches happen). The character is airborne in every
panel: no ground contact, no dust, feet free. Keep FX minimal — these are
quick pokes, not supers; the big FX belongs to the heavies.

---

## THE FOUR RULES (each one has caused a real re-do)

1. **Draw the fighter FACING LEFT.** The engine mirrors by facing; art drawn
   facing right renders backwards in play.
2. **No baked ground shadow.** The engine draws its own — and these are
   airborne poses anyway.
3. **No second character in the frame.** The engine draws the opponent.
4. **Real white gutters between panels.** One move per page, three panels in
   a row, each panel captioned with its slot name (`air1` `air2` `air3`).
   White background. Same body size in all three panels. Solid body through
   any motion streaks — never ghost the character into the FX.

## The three beats (same spine both pages)

An air light is one quick strike: **reach → contact → settle**. The contact
panel (beat 2) is the hit — weapon at extension, clean silhouette. Keep every
panel readable at thumbnail size.

---

## 1. MIZU — airborne staff jab (`air1` `air2` `air3`)

![mizu reference](frame-handoff/air-light-brief/mizu-air-ref.png)

**Identity (match the photo's idle):** Chibi ninja, roughly 3 heads tall,
strict side profile, FACING LEFT. PURPLE hood and violet robe with layered
skirt panels, white angled eyes in a solid-dark face, light slender frame.
**ONE LONG WOODEN BO STAFF (tan wood) — no blades.** One precise staff path.

Her `air1` and `air2` are current-generation and stay as style references —
match them exactly: same body size, same palette, same line weight. `air3`
is the one being replaced, but draw all three beats fresh so the set is one
hand.

| # | slot | pose |
|---|---|---|
| 1 | `air1` | reach — knees tucked, staff drawn back level, leading end aimed forward |
| 2 | `air2` | contact — the jab at full extension, staff dead horizontal, weight behind it |
| 3 | `air3` | settle — staff retracting to the air guard, body recentering for the fall |

## 2. SHIN — airborne kunai slash (`air1` `air2` `air3`)

![shin reference](frame-handoff/air-light-brief/shin-air-ref.png)

**Identity (match the photo's idle):** Chibi ninja, roughly 3 heads tall,
strict side profile, FACING LEFT. DEEP FOREST-GREEN hood and layered green
garb, TEAL-BLUE scarf streaming behind him, pale glowing angled eyes in a
solid-dark face, tan hand and shin wraps. **Weapons: SHURIKEN and a short
KUNAI — thrown steel and one small blade, never a sword.** His `hneu4` panel
in the photo is the quality bar for his air art.

His `air1` (clean shuriken strike) stays as the style reference. `air2` and
`air3` are the tumble poses being replaced — he must stay UPRIGHT and
striking through all three beats, never head-down.

| # | slot | pose |
|---|---|---|
| 1 | `air1` | reach — airborne, arm whipping the shuriken forward, scarf trailing |
| 2 | `air2` | contact — the kunai cross-slash at full extension, upright, committed |
| 3 | `air3` | settle — blade retracting to the air guard, knees tucking for the fall |

---

## Delivery

Two pages (or one composite with both), any size — bigger is better, the
last composite's ~140px figures packed fine but full-page strips like the
Oni boards (~2170px wide) cut cleaner. Transparent or white background both
work; the pipeline keys, scales against each fighter's live idle, and packs
onto the existing slots. The engine already draws these rows — the art
replaces in place, no wiring needed.
