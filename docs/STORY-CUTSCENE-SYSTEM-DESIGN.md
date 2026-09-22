# STORY CUTSCENES — DESIGN NOTE

**Status: PROPOSAL — no code until the owner approves. DeepSeek, Aug 17 2026.**
Build target `web/index.html` (single file, `SHEET_V 554`). Every citation below is from
the tree as it stands; line numbers will drift the moment anyone else commits, so treat them
as pointers, not pins.

---

## One structural gift up front

**Story mode already exists.** `gameMode === 'story'` runs an authored climb —
`STORY_RIVALS[p1Pick]` (five rivals, ~14413) + `BOSS_TAIL` (Exile → Mokurai → Oni), with
per-fight boards (`STORY_BOARDS`, ~14423), a ramp (`STORY_RAMP`, ~14424), a run-scoped
toll (`storyToll`, ~14430), named door banners (`resetRound`, ~14706–14715), and
per-fighter ending cards (`ENDINGS`, ~14457). Phase 4 (the shadow selves,
`docs/PHASE4-SHADOW-DESIGN.md`) is an insertion into that machine. **Cutscenes are the
same kind of insertion** — a data-driven scene player that runs *between* the beats that
already exist, reusing the existing renderer and DOM overlays.

**What does not exist yet:** a prologue, an act/dialogue sequence, a pan/zoom, a
dialogue-box-with-portrait. Today "storytelling" is two surfaces:

- `roundBanner` (declared ~14541, drawn ~17910–17913) — one centered line.
- the victory card (`#game-over-content`, built ~16636–16722) — a styled DOM block + portrait.

A cutscene is the middle weight between them: a bounded, skippable list of beats with a
portrait and a dialogue box, advanced one beat at a time.

---

## 1. What "cutscene" means here (and what it does not)

- **IN-ENGINE, data-driven.** Characters render through the existing
  `drawSprite()` → `drawShodoFrame()` path (~11677 → ~1374); "camera moves" are pan/zoom
  over the painted stage backdrops already in `web/assets/stages/*`; dialogue is a DOM or
  canvas panel styled with the Ink & Ember tokens (`--ink-1`, `--line`, `--ember`,
  `--paper`).
- **NOT** pre-rendered MP4. NOT a new engine. NOT a new art pipeline. NOT the trailer path
  (`tools/trailer/`) — that is a separate standalone artifact with a different owner gate.

The hard boundary that keeps this cheap: **the MVP ships with zero new art.** Backdrops come
from the 14 existing `STAGES` (~16754); speakers come from `portraitSrc()` (~12388).
Any bespoke key-illustration is a *later, owner-driven* still-generator pass — flagged, not
a build dependency.

---

## 2. Run state — where the scene player lives

Hang it next to `storyToll` (~14430) and Phase 4's `wholeness`. Module-level,
run-scoped, **not persisted**:

```js
let cutscene = null;   // { key, beats:[], idx:0, t:0, onDone }  — null means "no scene"
```

- `cutscene === null` → the existing game loop runs untouched.
- Non-null → a **full simulation freeze** (Section 3), identical in spirit to how
  `roundIntroTimer > 0` and `paused` already behave.
- Lives exactly as long as `storyToll` does: reset in the same places, dies with
  `quitToSelect()` / `startNewGame()`. No save-schema change, no new key.

---

## 3. The freeze — reuse the three gates that already exist

`pressCombat()` already short-circuits on
`if (!matchActive || paused || roundIntroTimer > 0 || !player1 || !player2) return;`
(~12856). The game loop already early-returns the physics while `roundIntroTimer > 0`
(~15602–15607) and draws `roundBanner` on top (~17910). A cutscene plugs into these
three seams — it does **not** invent a fourth:

1. **Input** — add `|| cutscene` to the ~12856 guard. Also verify the two global
   keydown paths that must not fire mid-scene: the `Escape` pause toggle (~15087) and the
   capture-phase title dismiss (`window.addEventListener('keydown', () => dismissTitle(), {capture:true})`, ~13364 — it already no-ops unless `attractMode`, but must be checked).
2. **Simulation** — in the game loop, before physics:
   `if (cutscene) { cutscene.t += dt; drawScene(); drawCutscene(); return; }`
   — the same early-return shape as the round-intro gate at ~15602.
3. **Advance** — the scene owns a key/tap "advance" listener; each press steps
   `cutscene.idx`. On the last beat it clears `cutscene` and calls `cutscene.onDone`,
   which hands control to whatever is next (the fight's `roundIntroTimer`, the victory
   card, or select). Skip = hold the same key, or a `data-action="skip"` click.

---

## 4. The beats table — schema

One table, one file, no tree engine, no branching. Phase 4's `SHADOW_LINES` dialogue
field is the direct precedent — this generalizes it from "one banner" to "a sequence".

```js
const CUTSCENES = {
  prologue: [
    { board: 'lantern', type: 'still' },
    { type: 'dialogue', who: null, text: 'The light did not go out. It was taken.' },
    { type: 'dialogue', who: 'Executioner', portrait: 5, text: 'Only one walks out with the light.' },
    { type: 'title', text: 'THE CLIMB' },
  ],
  rival_intro: { /* keyed by STORY_RIVALS[p1Pick][arcadeIdx], fall back to a generic line */ },
  door_intro:   { 7: [/* Exile */], 6: [/* Mokurai */], 8: [/* Oni */] },
  epilogue:     { Kael: [/*...*/], Ember: [/*...*/], /* per-climber; replaces/augments ENDINGS */ },
};
```

Beat shapes (every field optional; defaults keep it minimal):

- `{ board, type:'still' }` — fade in on a stage backdrop (reuse `setStage()` / `STAGES`).
- `{ type:'dialogue', who, text, portrait? }` — dialogue box + speaker + `portraitSrc`.
- `{ type:'title', text }` — the centered line, `roundBanner`-style (reuse the ~17910 draw).
- `{ type:'fight' }` — end of scene: clear `cutscene`, hand to `roundIntroTimer` (the ROUND N → FIGHT! gate, ~15600).

`who: null` is the narrator (no portrait, italic, house-paper colour). `who` is always a
roster name resolved through `NINJA_ROSTER` — never a hard-coded pronoun or id.

---

## 5. Trigger points — where scenes start (all existing seams)

1. **Prologue** — `beginFight()` (~14467), inside the `gameMode === 'story'` branch
   (~14468), *before* `startNewGame()` (~14500): set the `prologue` scene; its `onDone`
   calls `startNewGame()`. (Guarded so it fires once per climb, not every continue.)
2. **Rival / door intros** — `resetRound()` (~14621), exactly where the boss banners
   already fire (~14706–14715). Queue the scene instead of (or before) setting
   `roundBanner`; `onDone` falls through into `roundIntroTimer` as normal. Same hook
   Phase 4 uses for its shadow dialogue.
3. **Epilogue** — the ladder-cleared branch of the victory builder (~16639–16670). v1
   keeps the card as-is and adds an `epilogue` scene that plays when the player taps
   "BACK TO SELECT" (~16670), with `ENDINGS[player1.spec.name]` (~16655) as its final
   beat.

The scene player is **mode-gated to `story`** (and optionally `arcade`) — it never fires
in `2p` / `watch` / `training`.

---

## 6. Render approach — reuse, no new art (MVP), no paid generation

- **Backdrop** — `setStage()` + the painted stage layer inside `drawScene()` (~17398,
  art drawn ~17419+). All 14 boards already exist.
- **Character body** — only through `drawSprite()` → `drawShodoFrame()` (~11677 →
  ~1374). Never a raw `ctx.drawImage` of a sheet. MVP uses portraits only, so this path
  is optional and can be deferred.
- **Portrait + name** — `portraitSrc(spec)` (~12388) + the HUD-name style.
- **Dialogue box** — a DOM overlay styled like `#game-over-content` (proven, cheap), or a
  canvas panel in the `roundBanner` font. DOM is the v1 default.
- ⛔ **No paid generation, ever** (owner, Aug 11 2026). The MVP needs none; any new art is
  the owner's still-generator's job, handed a measured reference.

---

## 7. Prose law — identical to Phase 4 §4, applied to every line

1. **Roster canon from the Story Bible only** (`shadowclash-story-bible.md`).
   Open the fighter's section before writing a line for them.
2. **Genders are settled** — Ember, Tsubasa, Kael, Shin, the Executioner, Mokurai, Oni are
   **he/him**; Mizu, Exile are **she/her**. Never infer from name or silhouette.
3. **Private roster stays private** — no locked-slot names/stats/ids/portraits in shipped prose.
4. **No plot the Bible doesn't state.** Door scenes may state only what that door's Bible
   section states; shadow scenes follow the Phase 4 law ("accusation, not exposition; never
   confirms death").
5. **Sample prose below is a DRAFT for owner review** — it ships only after he approves it
   against the Bible.

---

## 8. Sample — the prologue (draft, canon-checked against Bible §THE TOURNAMENT OF SHADOWS)

```js
prologue: [
  { board: 'lantern', type: 'still' },
  { type: 'dialogue', who: null, text: 'The light did not go out. It was taken — pulled down into a place under the world, and hung there like a lantern over a pit.' },
  { type: 'dialogue', who: null, text: 'Whoever holds it holds everything: name, memory, the world above.' },
  { type: 'dialogue', who: null, text: 'So the pit calls six — six who already have blood between them — and gives them one rule.' },
  { type: 'dialogue', who: null, text: 'Only one walks out with the light. The rest stay dark.' },
  { type: 'dialogue', who: null, text: 'But the light is not guarded by rules. It is guarded by three. They cannot win. They are the doors.' },
  { type: 'title', text: 'THE CLIMB' },
  { type: 'fight' },
],
```

(Whitespace-trimmed; the shipped lines will be tightened and owner-vetted. This is the
*shape* of a scene, not the final script.)

---

## 9. Approval gate & verification

- Code starts **only after the owner approves this note** — same gate as Phase 4.
- Prove it plays, don't just read it: a filmstrip/GIF of a full prologue → first fight and
  a door-intro scene; `tools/check_it_actually_plays.py` green on shared `:9100`.
- **New targeted check** (in the house `tools/check_*.mjs` style): start story mode,
  advance every beat, assert the scene hands off to the fight and that inputs stay locked
  until `type:'fight'`.
- No `SHEET_V` bump unless art bytes change (the MVP changes none). No sprite bytes
  touched, so no montage gate is required for v1.

---

## 10. Out of scope (flagged, not Phase 5)

- **Voiceover / scene audio** — see `docs/VOICE-BRIEF.md` / `SOUNDTRACK-BRIEF.md`; owner's call.
- **Pre-rendered cinematic MP4s** — the `tools/trailer/` path is a separate artifact.
- **Branching / dialogue trees / player choices** — v1 is a linear beats list.
- **New art** — v1 reuses stages + portraits; bespoke illustration is a separate owner-gated pass.
- **Persisting cutscene progress / skip-history** — scenes replay on every run, like the banners do.

---

**Owner approves this note → code starts. Any red line above he disagrees with, say so and it
changes here first.**
