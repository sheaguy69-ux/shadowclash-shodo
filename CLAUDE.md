# ShadowClash — Claude entry point (READ FIRST, EVERY SESSION)

`AGENTS.md` is the full rulebook — read it before any work. This file is the short
version, because Claude Code auto-loads `CLAUDE.md` but not `AGENTS.md`.

## ⛔ STEP 0 — OPEN YOUR LANE

```bash
python3 tools/lane.py start "<your name>"    # e.g. "Opus 5", "Kimi", "Fable 5"
python3 tools/lane.py who                    # HEAD, foreign files, branches
```

**ONE TREE. `SHADOWCLASH-RECOVERED`. EVERYBODY.** Owner, Aug 22 2026: *"one fucking
server, one fucking tree."* `lane.py worktree` **refuses** now — it is what produced NINE
of them, and the cost was never disk, it was FORKED WORK: the owner spent Aug 22 reviewing
a Shin that was 29 commits stale because the finished art lived in one tree and the server
pointed at another, while two lineages drifted 29 commits against 54 with both sides
editing `web/index.html` and the same sprite sheets. Only he can merge that, and he should
never have been handed it. **If you think you need your own tree, that is his call, not
yours.**

Several agents share this tree, and the lane system is what makes that safe. `start`
snapshots what's already dirty — that's someone else's work, and the pre-commit hook
**refuses** commits containing it. Anything that goes dirty after you start, claim:
`lane.py claim <paths>`. Committing while another lane is open? `LANE_AS="<you>" git
commit` — it lands, stamped as a co-tenant commit, and their claims stay untouched.
`lane.py note "..."` posts to the channel; post-commit stamps it with your name + SHA.

⛔ **AND DO NOT COMMIT ANOTHER AGENT'S UNCOMMITTED FILES.** Dirty does not mean abandoned —
on Aug 22 three worktrees looked stale and were being written to that minute. The hook
refuses this for you; if it refuses, the answer is to leave it alone, not `--no-verify`.

Hooks not firing? `git config core.hooksPath tools/githooks`.

## ⛔ MEDIUM LAW — 2D CEL ILLUSTRATION, **NOT PIXEL ART**

*"Clean high-contrast 2D illustration/vector look — heavy black outlines, readable
silhouettes, controlled dark palette, glowing featureless angled eyes."*

Roster cells measure ~3900 unique colours; raw PixelLab output is 44. **PixelLab is the
wrong tool — do not use it, do not pack from it.**

## ⛔ MODEL LAW — two generators, named in `tools/sprites/fal_models.py`

Import from it; never hardcode a model id.

- **MOTION / i2v** = `bytedance/seedance-2.0/image-to-video` — **no `fal-ai/` prefix**
  (`fal-ai/bytedance/seedance/...` is the old 1.x family and silently gives worse frames).
- **STILLS / repose** = `fal-ai/nano-banana-pro/edit` (takes `image_urls[]`, not `image_url`).
- RETIRED: Kling v2.1, flux-pro/kontext. Do not reintroduce.
- `i2v_clip(..., loop=True)` closes a walk/run cycle on itself — never loop a one-shot
  attack, it rewinds the swing. Audio forced off; default 1080p.

**i2v is the frame source** for multi-frame motion (~$0.15 / 5s clip). Frames from ONE clip
are size-registered; independent stills never are. A still-editor **cannot invent a pose the
reference doesn't hold** (8/8 nano-banana walk attempts returned the standing stance) — for
locomotion always i2v, and *measure* the pass frames rather than eyeballing them.

## The frame pipeline (already built — reuse, don't rebuild)

- start frames: `media/polished-candidates/<fighter>/truecolor-raw/*.png`
- generate: `tools/sprites/gen_attack_i2v.py`, `gen_run_i2v.py`, `gen_registered_i2v.py`
- extract: ffmpeg at 12/24 fps → pick the side-profile window (clips drift front-facing)
- key: `magick` fuzz **42%** corner-floodfill (42, not 25 — drop-shadow needs it)
- pack: `pack_attack5.py` / `pack_i2v_run.py` / `extend_sheet.py`; MATCH_HEIGHT per-cell
  flattening IS the house look (engine bob supplies the bounce). Target 0.0% wobble.
- fal downloads: **curl, not python** (proxy breaks urllib SSL). `FAL_KEY` in WildComiks `.env.local`.

### ⛔ THE EMBER RECIPE — every jump / locomotion clip

1. **Seed** = `truecolor-raw/idle-lowseat.png` — character LOW in frame, space above.
2. **Model** = `--model kling` (Kling v3 4K). Only family with `negative_prompt`, so camera
   motion + ground shadow are FORBIDDEN, not merely unrequested. Seedance broke camera lock twice.
3. **Prompt** = six NUMBERED beats (crouch → launch BOTH FEET TOGETHER → rise/tuck → apex
   rotation fully mid-air → tuck opens, legs reach down → two-foot absorbing landing) + an
   explicit NEVER list for that fighter's failure mode + "stays on the SAME SPOT", "pure
   side profile", "both legs readable at every frame".
4. **2500-char cap** incl. the script's ~900-char wrapper → `--action` + `--identity` ≤ ~1600.
   Over = HTTP 422.
5. **ONE uniform scale** for the sequence, anchored on an upright frame vs the idle's body
   height. **NOT per-cell MATCH_HEIGHT** — it scales the compact apex ~2x against the
   stretched launch and causes size boil.
6. **Key** = fuzz 42% floodfill → keep largest connected component → purge sub-visible alpha LAST.
7. **Pose doesn't fit? GROW `frameH`/`footY`.** Never shrink the body, never cut the pose.
   **`frameH` is PER-FIGHTER — never assume 320.**
8. **Gate:** montage strip + GIF at game fps to the owner BEFORE the sheet is touched.

## The two brains — read the relevant one before nontrivial work

**Ledger** (`/Users/anthonyguy/OB-LOCAL_BRAIN/Claude-Brain/memory/`)
- `shadow-clash-channel.md` — live team inbox. Newest STATE OF THE WORLD outranks memory.
- `shadow-clash-sync.md` — append-only formal record. Read newest, append signed+dated.
- `shadow-clash-game.md` — history, pipelines, pitfalls.

**Art canon** (`/Users/anthonyguy/OB-LOCAL_BRAIN/ShadowClash-Second-Brain/`)
- **`17 - Sprite Animation Director Prompt.md` — ⛔ LOAD BEFORE any generation, cell review,
  QC, or packing.** Binding 12-dimension per-cell standard + the GRADE TABLE that ships with
  every contact sheet. **No cell packs without a grade.** >30% REDO/REJECT → don't ship the
  montage, propose a method change. *(Doc 17 is a standard, not canon authority — owner
  rulings and `<fighter>.json` outrank it.)*
- `05 - Animation and Art Bible.md` — quality bar, motion construction, frame budget
- `<Fighter>-Identity-True-Lock.md` — identity string, palette hexes, anchor poses, **NEVERs**
- `Attack-Clip-PromptPack-<fighter>.md` · `<Fighter>-AttackMatrix-Section4-v1.md`
- `11 - Art Implementation Instructions.md` · `10 - Visual Asset Manifest.md` · `12 - Runtime Sprite Sheets and Frame Map.md`
- `assets/approved/` — owner-approved reference art

**⛔ ONI — "THE FOUNDER". FINAL DESIGN, owner Aug 11 2026:** *"This is his only final
character design look."* He/him. The design sheet the owner supplied is canon:

- **White skull mask**, three claw-scratch gouges across it, **RED eyes**. Two dark horns.
- **Black hood + tattered black mantle**, ash-gray worn plate (chest, bracers, knees, boots).
- **Cloth wrappings on BOTH hands and forearms.**
- **RIGHT HAND CLAW ONLY** — five long dark-gunmetal blades. **LEFT HAND IS WRAPPED, NO CLAW.**
- **Two swords carried crossed on his back.**
- Palette: **black, ash gray, white mask, red eyes/FX**. Owner's checklist also forbids
  mirrored claw errors and extra appendages.
- Owner's animation rule, verbatim: **"face right, never flip claw to left."**

**THAT ANIMATION RULE IS ALREADY SETTLED BY THE SHIPPED GAME — confirm, don't re-decide.**
Every sprite is authored facing **LEFT** and **mirrored** for the fighter who faces RIGHT
(`ctx.scale(-p.facing,1)`) — verified on the art, not from a comment: crop any idle cell's
head and the eye sits left with the scarf trailing right, on all seven fighters measured.
So an asymmetric weapon swaps hands on turn — **and that is already how this game ships.**
**Kael is `Short & Long Sword`**, asymmetric, there is **no no-mirror flag anywhere in the
engine**, and his long blade has always changed sides when he turns. Exile's sickle-and-chain
does the same. So Oni's claw is not a new problem and needs no new mechanism: read *"no
mirrored claw errors"* as an **art QC rule** (don't draw the claw on the wrong hand in a
cell), which matches the whole roster. Reading it as *"the engine must never mirror him"*
would be a first for this game and would **double his frame count**. Owner confirms in one
look: watch kael turn around.

**SUPERSEDED — delete on sight, do not use as reference:** the white-maned / bone-pelt /
**purple-accent** oni. That was the previous redesign lane
(`RECOVERY/oni-redesign/NEW-ONI-DESIGN.png` + its 59 frames) and the new final design has
no mane, no pelt and **no purple at all**. The old "never fix purple out of new Oni art"
rule is DELETED, not qualified — following it now would repaint the wrong character.

**Still benched.** No unbench until the owner motion-gates the new design.

**Canon files for the above:** master `RECOVERY/oni-founder/ONI-BIBLE-FINAL.png`, identity `Oni-Identity-True-Lock.md` (measured hexes, frame specs, the mirror finding), and the owner's delivered kit archived in `RECOVERY/oni-founder/boards-aug9/` — states, moveset, mobility, wire, directional heavies/aerials/specials. Cut and key what is there; a frame that cannot be used goes back to the owner.

**⛔ "BUDDHA" IS MOKURAI — THE SAGE OF NOTHINGNESS** (owner, Aug 5 + Aug 7 2026; this is his only
epithet — "the Wild Monk" is deleted — and the word "Buddha" never ships). Bare hands and bead-wrapped
fists; **he has NO bo staff and never did.** Assets are `mokurai.*` — asset keys are
`spec.name.toLowerCase()`, so his name IS his file path.

## Non-negotiables (full list in AGENTS.md)

1. Sheets are **append-only**; original cells byte-identical; composite onto the existing png.
2. Bump `SHEET_V` in the SAME commit as any `web/assets/sprites/*` change.
3. **Never change art without showing the owner the frames first** and getting his OK.
4. **Show motion as a GIF/filmstrip** — cel cuts, never cross-fades. Static asserts can't see a ghost.
5. **⛔ NO PAID GENERATION. EVER.** (owner, Aug 11 2026: *"we're not paying for no art"*,
   *"never don't suggest payment or nothing... I'm not dealing with payment when it comes
   to this project anymore"*.) Do not call fal, do not run the i2v or still-edit scripts,
   do not price a batch, do not offer a paid option as a fallback or a "cheaper" variant.
   **New cells come from an outside still-generator the owner drives himself** — this repo's
   job is to hand it measured references and check what comes back. The fal tooling under
   `tools/sprites/` stays for reading and for the recipes it documents; it is not to be run.
6. Local commits only. **Never push, merge, or deploy** — the owner does that himself.
7. **Edition split:** the recovered rollback stays on `:9100`; this isolated Shodō worktree is
   reviewed on `:9101` (`python3 tools/serve.py 9101 web`); the approved-art gallery is on
   `:9102`. `tools/lane.py` allows exactly these three ports. Always verify the selected tree
   with `curl -s localhost:<port>/whoami` before review. `serve.py` sends `Cache-Control:
   no-store`; do not use a plain `http.server` for review.
8. **A fix DELETES the wrong version.** No `~~struck~~` text, no "this used to say X", no
   "do not restore", no parked CONFLICT markers. Current truth once; git holds the history.
   Decision genuinely open? Decide it and say so. Fix every copy in the same pass — the
   ledgers and second brain hold divergent duplicates.

## ⛔ ROSTER CANON — open the Story Bible before writing prose about a fighter

Never infer gender from name, design, or silhouette. Applies to UI strings, ending cards,
commit messages, `SHEET_V` entries, ledger notes. Corrections must be surgical — the
`SHEET_V` chain is one enormous line carrying every fighter's history.

**Genders:** Ember, Tsubasa, Kael, Shin, the Executioner, Mokurai, Oni **he/him** · Mizu, Exile
**she/her**.
Anyone else: open the Story Bible first.

**⛔ SILHOUETTE CANON — the Executioner is the OLDEST and TALLEST of the six, *slightly*.**
**Kael is the youngest** — the two bracket the cast. *Slightly* = an inch, not a boss
silhouette; **Oni** is the one who towers. This must survive to the SCREEN, so it constrains
`scale` in `<fighter>.json`, not just prose. Measured idle heights (Aug 2 2026): executioner
**70.4px**, kael 70.0, tsubasa 69.6, ember 69.3, shin 66.6, mizu 62.4 — he leads by 0.4px,
a rounding error. Any scale pass keeps him first with a visible margin (~2-3px), without
pushing him into boss territory.
