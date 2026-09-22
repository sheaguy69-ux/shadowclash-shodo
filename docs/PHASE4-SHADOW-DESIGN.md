# PHASE 4 DESIGN NOTE — THE SHADOW SYSTEM
**Status: PROPOSAL — no code until Butta approves. Fable 5, Aug 7 2026.**
Build target `web/index.html` (13,506 lines, SHEET_V 403 — the outline's "9,600 lines / SHEET_V 314" was a stale snapshot; everything below is cited from the tree as it stands).

One structural gift up front: **story mode already exists in the engine.** `gameMode === 'story'` runs an authored climb — `STORY_RIVALS[p1Pick]` (five rivals) + `BOSS_TAIL = [7, 6]` (Exile → Mokurai), with per-fight boards (`STORY_BOARDS`), a ramp (`STORY_RAMP`), and a run-scoped toll (`storyToll`). Phase 4 is an insertion into that machine, not a new mode. Note: the code's second door is **Mokurai** (id 6) — he is the outline's "Sage." The `storyToll` string still says "BUDDHA"; renaming UI strings to the Sage framing is a Butta call, out of scope here.

---

## 1. Run state — where wholeness lives

**Hang it on the existing run-scoped globals next to `storyToll` (index.html ~10982).**

```js
let storyToll = { regenMul: 0, dmgMul: 0, hpCut: 0, paid: [] };   // existing
const WHOLENESS_FULL = 3;
let wholeness = WHOLENESS_FULL;                                    // NEW — the one integer
```

- Reset in the same place `storyToll` resets: the `gameMode === 'story'` branch of `beginFight()` (`storyToll = {...}; // a new climb owes nothing yet` → add `wholeness = WHOLENESS_FULL;`).
- **Why it survives across fights:** `arcadeQueue`, `arcadeIdx`, and `storyToll` are module-level `let`s that `startNewGame()`/`resetRound()` never touch — they already carry run state fight-to-fight. `wholeness` gets the identical lifetime for free.
- **Not persisted.** It is a run, not a career. `save.story` stays what it is (per-ninja clear counts). No save-schema change, no new key.

Exactly one integer, as specced. Nothing else fits better and nothing new is needed.

## 2. Mirror clone — how the shadow is spawned

**The clone is free.** `resetRound()` already builds both fighters from the shared data:

```js
player2 = new Player(2, 600, GROUND_Y - 48 * (NINJA_ROSTER[p2Pick].sizeScale || 1), NINJA_ROSTER[p2Pick], false);
```

A shadow fight is `p2Pick = p1Pick` down this exact path — same `spec`, same `SPRITES[spec.name.toLowerCase()]` sheet, same CPU brain. VS already permits mirror picks, so the engine has been running this case since Phase 1.

**Queue encoding:** `arcadeQueue` holds roster ids. Shadow entries get a sentinel (propose `-1`): when `beginFight()`/`arcade-next` reads a `-1`, it sets `p2Pick = p1Pick` and `player2.isShadow = true` after spawn. Wholeness decides how many `-1`s are spliced in front of the doors (full → one, before Exile only; low → one before each door, `cpuTierActive` stepped up per encounter using the existing `rampTier` machinery).

**Regression flag (the one real risk):** both `Player`s hold `NINJA_ROSTER[id]` **by reference** — the specs are shared, mutable singletons. Any shadow tinting/stat-nudging written onto `spec` (or onto the shared `SPRITES` manifest) corrupts the player and every later fight. Law for Phase 4 code: **the shadow is expressed only as instance state on the `Player` object (`isShadow`), never on `spec`.** No change to `NINJA_ROSTER`, the JSON manifests, or the sheets. Phases 1–3 untouched.

Secondary guards: the sentinel must be invisible to id-keyed code — door toll (`payToll`), win/unlock counters (`save.story`, `UNLOCK_ORDER`), HUD name (`NINJA_ROSTER[p2Pick].name` — shadow shows "KAEL'S SHADOW" or similar, Butta's wording), and the boss-tail banners. Each is a one-line `isShadow`/`-1` guard.

## 3. Shadow palette treatment — PROPOSAL, needs Butta in motion first

**Reuse the victim hit-flash machinery, not a new pipeline.** The engine already recolors a fighter per-frame: `flashScratch` + `source-in` fill + alpha-scaled overlay draw (index.html ~8896). That is a proven, cheap, sheet-untouched tint.

Proposed look, in the house palette:
1. Draw the sprite normally (the cel outlines and silhouette stay true).
2. Overlay the `source-in` copy filled `#0b0a12` (`OUTLINE_COLOR` — the house ink) at **globalAlpha ≈ 0.78**, with a slow breathe (±0.06 on a ~2s sine). The fighter reads as living ink; ~22% of his own colors ghost through so the player still reads which character it is.
3. Re-light the eyes: second `source-in` pass in the fighter's own `colors.eye`, composited `lighter`, eye-region only — the glowing-eyes law survives the blackout.

Zero new sprites, zero SHEET_V, zero dependencies. (Rejected alternative: `ctx.filter = 'saturate(.2) brightness(.4)'` — one line, but canvas filter support is uneven and the scratch-canvas path is already battle-tested in this exact engine.)

**Approval gate:** I build it behind a debug toggle, record a motion GIF of a shadow mirror round, Butta judges it moving. Nothing commits before his OK. Per the standing law, static stills don't count.

## 4. Dialogue table — schema + Kael's lines

**Delivery:** the existing `roundBanner = { text, until }` overlay (already draws in camera-space HUD; the boss tail already uses it for named intros). No VO, no tree engine. Trigger points already exist in code: round intro (`resetRound`, beside the boss banners), the damage path (~4471, where the `storyToll` hook sits) for low-HP one-shots, and round resolution for KO/defeat.

```js
// keyed by spec.name; arrays indexed by (encounter - 1), clamped — encounter 3 reuses
// the last line if wholeness never dropped that far. One-shot flags per round.
const SHADOW_LINES = {
    Kael: {
        intro: [
            "Two swords, and you still check whose stance you're copying.",
            "Balanced in all things. Say the other half. You say it in the dark — best at none.",
            "You measured all five of them today. You never once measured yourself.",
        ],
        playerLow: [ "There it is — the pause. Still waiting for someone older to step in." ],
        shadowLow: [ "Cut me down. The part of you that doubts isn't the part that falls." ],
        ko:        [ "Up. The youngest doesn't get to be tired. Your rule. Not mine." ],
        defeat: [
            "You kept your feet. So why are your hands still shaking?",
            "You won. Again. Tell me why it never feels like proof.",
            "Go on, then. …When did you last sleep, Kael?",
        ],
    },
};
```

Check against the three rules (3.3):
1. **No plot.** Nothing about the other five's secrets. Every line is Kael's own insecurity — youngest, all-round, master-of-none, needing to be measured — which he already knows and won't admit.
2. **Death-doubt planted, never confirmed.** Exactly one circling line, the final defeat line ("when did you last sleep"), hanging with no answer. Nothing anywhere states or implies the six are dead.
3. **Accusation, not exposition.** Every line is second-person and points at behavior he can't deny. Zero world-lore.

Written by someone who believes they are alive — the shadow included.

---

## Out of scope, flagged for later (not Phase 4)
- **Story/arcade are off the public-battle mode allowlist** (index.html ~755). Phase 4 is built and tested locally with story enabled on the working branch; the public gate stays as-is.
- **Ruled (owner, Aug 7 2026): any word "Buddha" is code for MOKURAI.** Live sweep done in `7bd25b6` — the `storyToll.paid` string now says MOKURAI. His epithet is ruled too (owner, Aug 7 2026): **Mokurai, the Sage of Nothingness** — he IS the outline's "Sage" boss, and that is the title to use wherever story prose names his door.
- The old bible archive header (canon ruling) — second-brain edit, separate pass.
- **Done already (separate commit `68a33cc`):** the ordered Tsubasa he/him text sweep — 9 comment spots in index.html + AGENTS.md, no SHEET_V bump. Repo `CLAUDE.md` already carried he/him.

**Butta approves this note → code starts. Any red line above he disagrees with, say so and it changes here first.**
