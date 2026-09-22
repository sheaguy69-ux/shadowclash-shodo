# ShadowClash — Combat Feel Handoff (2026-07-18)

**For:** Claude Code (or any agent picking up combat/animation work)
**From:** Cowork session with owner, 2026-07-18
**Read first:** `AGENTS.md` (hard rules), then this doc. Owner directives below override everything.

---

## 0. OWNER DIRECTIVES (non-negotiable, stated 2026-07-18)

1. **NOTHING gets pushed to `main` or any remote.** All work stays local on the current
   branch until the owner says attacks look right. Do not ask about pushing; he will say when.
2. Stop generating audit/handoff paperwork loops. Ship visible improvements instead.
3. The owner's standard: **"Can you tell the difference between attacks? Do they look
   dynamic?"** Every change is measured against that question, by eye, in the browser.
4. Show, don't describe: verify changes by running the game (`python3 -m http.server 8777`
   in `web/`, WATCH mode makes the CPUs fight so attacks fire constantly).
5. Taste over spectacle. "Don't make it corny — flavor, taste, juice." Restrained and crisp
   beats loud.

## 1. Current state

- Branch: `fix/parry-followthrough`. Last commit: `21c1348` (select-screen overflow fix).
- **Uncommitted in `web/index.html`:** the entire attack-feel layer described in §3.
  Owner has seen it run; not yet committed. Commit it as ONE commit:
  `feat(feel): attack signatures, victim flash, impact shards, slash shatter (F9 presets)`.
- Local server may still be running on `:8777` (`pkill -f "http.server 8777"` to stop).
- `.gitignore` has an unrelated uncommitted edit + stray `image-1784401178196.jpg` in repo
  root — leave both alone.

## 2. Research digest — what the owner's study material teaches

Sources the owner supplied (watch/absorb before touching animation):
- Yuusha — *Setting up combat in a 2D Game* (youtube r8Ad8TP56GI)
- Ali Elzoheiry — *Game Dev Tricks to Improve Combat* (l9XFMPqdRAo)
- Challacade — *Creating impactful combat* (q9Kzd6f5mR0)
- Typhoon — *The KEY to every GREAT fighting game* (SDCzh4nwrbQ)
- *How Do You Improve Turn Based Combat?* (ktogjiX3eI4)
- HeartBeast — *2D Hack-n-Slash* series (U0fQHIueFw4)
- Plus: GDQuest "Juicing up your game attacks", SLYNYRD Pixelblog #9 (melee attacks),
  gamedesignskills.com combat design.

The distilled laws:

1. **Anatomy: anticipation → activation → recovery.** Activation is 1–2 frames and FAST.
   Weight lives in anticipation; feel lives in recovery easing. More frames = mushier.
2. **Tiers are read from the anticipation, not the trail size.** Light = no wind-up
   (speed). Heavy = long cock-back (weight). Special = coil + sustained drive (power).
3. **The smear IS the slash.** One crescent, 1–2 frames, white-hot leading edge, tapered
   transparent tail. The eye infers the cut from pose-before + pose-after.
4. **Impact reads on the RECEIVER:** white hit-flash on the victim sprite, directional
   debris flying AWAY from the hit, knockback with ease-out. Hitstop shows all of it frozen.
5. **Follow-through breaks, it doesn't fade.** Arcs shatter into 2–3 drifting wisps.
   A uniform opacity fade is the tell of a lazy procedural effect.
6. **Hitbox syncs to the smear frame exactly** (HeartBeast discipline). Already correct in
   this codebase via `pendingSlash` delay — do not break it.

## 3. What was implemented this session (all in `web/index.html`, visual-only)

No gameplay timing, hitboxes, frame data, or sprite files touched. `SHEET_V` untouched.

| Piece | Where | What |
|---|---|---|
| Signature body curves | `drawSprite` attack block | Per-tier anticipation/recoil/lunge/lean/stretch (light snap / heavy cock-back / special coil) replacing one shared curve |
| Tier-colored trails | `SLASH_ARC` + `spawnSlash` | light `#f8fafc` thin 0.10s · heavy fighter-primary thick 0.19s · special `#22d3ee` wide 0.22s |
| Slash shatter | `drawSlashes` | Intact ribbon completes by 60% of life, then breaks into 2–3 deterministic drifting wisps + one white hot tip. No flicker (position-seeded). |
| Victim hit-flash | `takeDamage` sets `hitFlashT`; rendered in `drawSprite` via `flashScratch` canvas (source-in white) | Receiver blinks white ~0.08–0.10s, holds through hitstop, decays in game time (`update`) |
| Directional shards | `createSparks(x,y,color,dir)` + particle draw | Impact debris launches away from attacker with upward bias, drawn as velocity-stretched lines; white burst + colored embers |
| FEEL presets | `FEEL_PRESETS` / `FEEL` consts, **F9** in keydown handler | `punchy` vs `grounded` (anticipation, lunge, shake ×, hitstop ×). Yellow toast on canvas shows active preset. Owner picks by eye. |

Also committed earlier today: select-screen fix (`21c1348`) — `#character-selection` was
`lg:inset-0` inside a 2006px parent with `justify-between`, burying the roster below the
fold. Now `lg:top-0 lg:inset-x-0 lg:max-h-screen justify-start`.

## 4. THE REAL PROBLEM — backlog in priority order

The engine layer is now sound. The remaining gap is **the drawn frames themselves**
(SPRITE-HANDOFF.md §6 "pose-softness"): Kontext resists limb reposes, so `light1` isn't
wound back, `light2` doesn't thrust, `heavy2` never completes its downswing. The engine
cannot fake poses that were never drawn.

1. **Regenerate the attack cells with hard pose contrast.** Per SPRITE-HANDOFF §5 pipeline.
   Prompt principle: describe the EXTREME of the pose, name the weapon explicitly, and
   describe what the silhouette does ("blade cocked behind head, elbow high, torso twisted
   away" / "blade fully extended past the body, arm straight, torso driving forward").
   Generate → montage strip → **owner approves images BEFORE packing** (AGENTS.md rule 3).
   Append-only cells, bump `SHEET_V` same commit (rules 1–2).
2. **Fix the run-cycle shrink** (owner: "why when they run I gotta get small — that's
   stupid"). The run cells render smaller than idle: a height-match failure in the sheet,
   not engine code (`drawSprite` scales all frames identically). Re-normalize run cell
   heights per pack_sheet MATCH_HEIGHT house rule; verify with a live filmstrip
   (AGENTS.md rule 5), owner approves.
3. **Per-fighter curve flavor.** All six currently share FEEL curves. Executioner should
   swing heavier (longer ant, bigger recoil), Shin snappier. Small per-spec multipliers
   on the §3 signature block once owner locks a base preset.
4. **Tune wisp shatter per weapon.** Staff (Mizu) wisps should break flatter/straighter;
   claws (Ember) into shorter triple-scratches. Cheap: vary `nW`/drift by `spec.id`.
5. After owner locks a preset: delete the loser from `FEEL_PRESETS` and the F9 toggle,
   or keep as debug — his call.

## 5. Practical notes

- Verify by eye: WATCH mode + Chunin CPUs = constant attacks. Browser sheet cache is
  sticky: bust with `?v=N` or `fetch(url,{cache:'reload'})`.
- Tailwind CDN warning in console is expected noise.
- The `SHADOW CLASH` item on the Desktop was a broken symlink (now in Desktop/Misc);
  patches in `Downloads/Projects/SHADOWCLASH/` are historical — repo is source of truth.
- Second brain: `/Users/anthonyguy/OB-LOCAL_BRAIN/Claude-Brain/memory/shadow-clash-game.md`
  — append a dated entry after shipping (AGENTS.md).
