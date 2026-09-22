# ShadowClash — Road to DONE (2026-07-28, SHEET_V 238)

Grounded in: the Story Bible (private), 01-Vision non-negotiables, 08-QA roadmap,
and what is actually in the 238 engine. Owner priorities may reorder anything.

**What "done" means here:** a stranger can open the game, understand the fiction
in 10 seconds, pick a fighter, climb the tournament, and reach an ending that
pays off that fighter's story — with music, on any device, without debug keys.

---

## P0 — REQUIRED for a complete game

### 1. STORY MODE — the climb (the biggest hole, mostly $0 code + text)
The bible IS a tournament structure and the engine already has both halves —
they're just not connected. Arcade = "other five shuffled" on random boards.
- **Pin the ladder to the boards**: rival fights happen ON the grudge boards
  (Kael↔Tsubasa at the dojo-adjacent board, Shin↔Ember at the Ash Village,
  Mizu↔Executioner at the Drowned Shrine / Warrant Yard), doors at their homes:
  Mokurai at The First Door, Exile at The Last Door,
  final ascent at The Lantern.
- **Rival intro text** (2 lines each, straight from the bible's Blood-with map).
  $0, enormous story payoff.
- **Real endings**: the one-liners in ENDINGS become 3-5 line endings answering
  each fighter's reason for descending (bible has every hook: Kael wants to
  carry the light back up; Tsubasa wants Kael to WATCH him take it; Shin came
  to stop someone; Ember's fire; Mizu knows what the light does; the
  Executioner's sentence). Text only, $0.
- **✅ DOOR ORDER — RULED (owner, 2026-07-28)**: Exile → Mokurai.
  The bible carries the ruling note.
  Story-mode build must renumber the door BOARD names to match the climb:
  tollgate='The First Door' (Exile's toll on entry), temple='The Second Door'
  (Mokurai).

### 2. STAGE SELECT — F7 is a debug key, not a feature
A normal player can never reach The Breaking Stair (roll:false + no UI).
- Stage picker on the character-select screen: Random (default, current pool)
  + the 12 boards; the abyss listed with a warning skull. ~1 evening.

### 3. MUSIC — the game has 68 sfx calls and ZERO music
The single loudest "not done" signal in a 2-minute play session.
- Per-board loops (12 boards can share ~5 tracks by mood: serene/grudge/
  door/lantern/abyss), menu theme, KO sting, results sting.
- Owner has Suno/audio pipelines from other projects; WebAudio loop player is
  ~50 lines. Spend: ~$0-10 depending on generation route. Volume slider +
  mute in pause. (Vision #5: impact is audio-first — music ties it together.)

### 4. TITLE / ATTRACT SCREEN — the fiction in 10 seconds
Game currently boots into character select with zero framing.
- Title card (logo exists in header), 3 lines of premise (the light was taken;
  the pit calls six; only one walks out), START. WATCH mode already exists —
  it IS the attract demo if idle at title. $0.

### 5. GAMEPAD SUPPORT
Keyboard/touch/mouse/hand exist; no Gamepad API. A 2D fighter without pad
support isn't done. Navigator.getGamepads polling mapped onto the existing
keys[] aliases ≈ 100 lines, $0. (Remappable keys = P1, below.)

### 6. ART DEBT already on the books (K3 lane, mostly in flight)
- Blade-family per-cell repack onto HEAD geometry (IN FLIGHT).
- 253 transparency purge re-apply.
- Exile: hurt/thrown is a confident stance (cell 2) — she never visibly
  recoils; block shares cell 12. The last "recycled cell" on the roster.
- Breaking Stair backdrop: OWNER GATE PENDING. Moonlit Edo ledge: OWNER CALL.
- QA-roadmap leftovers: Kael scale recheck beside all five; portrait set
  completeness on the select screen.

### 7. SHIP MECHANICS
- Deploy the private build somewhere the owner controls (separate Vercel
  project or password link — NEVER shadowclash-peach).
- Browser matrix pass (Safari/Chrome/Firefox + iOS Safari), mobile perf +
  console-error pass (QA doc).
- Save versioning: save.prefs already persists — verify old saves don't wedge
  new builds (mode/tier/pick guards exist; re-verify at ship).

## P1 — STRONGLY RECOMMENDED (the difference between done and good)

- **Survival / endless tower**: reuse arcade machinery, HP carries over,
  leaderboard-less streak counter. The pit "keeps calling" — story-true. ~$0.
- **Key remapping** (+ the accessibility pass that comes free with it).
- **Round count option** (FT1/FT2/FT3 — roundWins already generalizes).
- **Per-fighter arcade difficulty ramp balancing pass** with the boss tail.
- **Story-consistency sweep of stage roll**: grudge boards weighting in
  non-story modes (e.g., Ember vs Shin rolls Ash Village more often). Tiny.
- **Second private playtest** (the Jul 19 protocol) after story mode lands —
  the owner's own "done" bar was set by playtest, not feature count.

## P2 — POST-1.0 (do NOT block done on these)

- Online play (rollback etc.) — different project-sized effort.
- More fighters (QA doc: only after the nine reach production standard).
- The Godot port (08-roadmap "longer-term" — the web build IS the game).
- Replays, training-mode frame data overlay, combo trials.
- Unlockables/cosmetics.

## Explicitly NOT needed (checked against the engine — already done)
Parry + followthrough ✓ · throws/wall-slam ✓ · kawarimi/bomb-log deception ✓ ·
guard-crush stagger ✓ · chip ✓ · double-KO/time-over ✓ · training mode ✓ ·
WATCH mode ✓ · CPU tiers + boss-tail arcade ✓ · touch controls ✓ · win quotes ✓
· 12 stages w/ hazards+ledges+abyss ✓ · hitstop/juice framework ✓ · save ✓.

## Suggested order of attack
1. Stage select + title screen (one session, all $0, instantly "feels like a game")
2. Story mode structure + rival text + endings (two sessions, $0)
3. Music (one session + generation)
4. Gamepad (one session)
5. K3 art debt merges as it lands · ship pass last
