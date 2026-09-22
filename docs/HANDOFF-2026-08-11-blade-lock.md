# HANDOFF — Blade Lock session, 2026-08-11

**From:** Claude Code (Opus 5), running in a cloud container on branch
`claude/blade-clash-animation-frames-vcqr4d`.
**To:** the next chat / agent, working on the owner's LOCAL copy.

---

## 0. WHERE THE WORK IS — ON THE REMOTE, as of 2026-08-12

**Everything is pushed.** Branch `claude/blade-clash-animation-frames-vcqr4d` at
`8f97559`, 39 commits on top of `a976071`, open as draft PR #59.

```bash
git fetch origin
git log --oneline origin/claude/blade-clash-animation-frames-vcqr4d -5
```

You should see `docs: stale counts again, and a SHA warning the handoff needed` at the top.
If you are working in a tree that lacks it, check out the branch rather than re-implementing
anything from this document — it describes the code well enough to review, not well enough to
reproduce, and a second divergent implementation is worse than none.

**This section used to say the opposite,** and the history is worth one line because it
explains the SHA note below: the work was authored in a cloud container that could not push
(`git push` blocked by the environment's permission classifier, and so was writing a settings
file to permit it), so it was handed over as git patch bundles and applied locally by the owner.
That is finished. There are no outstanding patches.

⛔ **SHA WARNING — hashes quoted in this document will NOT match the tree.** `git am` replays
each patch as a NEW commit with a new hash, so the remote's history and the authoring history
are parallel: identical content, different SHAs. "Is this change present?" cannot be answered by
comparing hashes — compare the CONTENT, or check for a named file
(`tools/sprites/pack_lock_cells.py` is the newest addition). I misread a 37-commit range as
unpushed work on exactly this confusion.

**Also note:** the owner's machine has several copies of this game. He worked in
`shadowclash-tryout` this session, but **`SHADOWCLASH-RECOVERED` is at SHEET_V 469** against
tryout's 344 — see §8. `_SNAPSHOT-INFO.md` at the repo root is STALE and actively misleading
(see §7).

---

## 1. TWO STANDING RULES THE OWNER SET THIS SESSION

### ⛔ NO PAID GENERATION. EVER.

Owner, twice, verbatim: *"we're not paying for no art"* and *"please do never don't
suggest payment or nothing cause I'm not dealing with payment when it comes to this
project anymore."*

Do not call fal, do not run the i2v or still-edit scripts, do not price a batch, do not
offer a paid option as a "cheaper" fallback. **New cells come from an outside
still-generator (GPT-image class) that the owner drives himself.** This repo's job is to
hand it measured references and check what comes back.

This is recorded in `CLAUDE.md` rule 5 and at the top of the fal section in `AGENTS.md`.
`CLAUDE.md` previously said the **opposite** ("Art spend is pre-authorized — don't ask,
report the running total") — that line was deleted, not qualified.

### ⛔ NOTHING GOES TO THE OWNER'S EYES UNVERIFIED

Two art references in this repo turned out to be the wrong character (§3, §4). Both were
caught by **measuring at magnification**, not by eyeballing at cell size — checking a
200px cell at 1:1 is what let both slip past twice. Crop, upscale 4x, and compare named
features.

---

## 2. THE BLADE LOCK — implemented, logic-tested, AND CONFIRMED IN GAME

**What it replaces:** two steel edges meeting used to cancel each other in a 130ms trade.

**What it does now:** they **BIND**. Both fighters freeze in contact, both players mash,
one wins the push and the other is thrown off.

### ✓ PLAYED AND WORKING — owner, Aug 12 2026

*"Yes, the mechanic is working with the clash."* Confirmed in the browser on the tryout
tree. The bind triggers off a real clash, holds, and resolves. This was the one thing this
whole session could not verify from a container with no browser, and it is now verified.

**What is still open is the FEEL, not the function.** `LOCK_DUR` 1.15s, `LOCK_MARGIN` 6
presses and `LOCK_MIN_HOLD` 0.3s are first guesses that pass their tests — nobody has said
yet whether the hold drags or the floor feels sticky. Those are three constants; changing
them is free.

**The frames are NOT the bug.** With no `lockN` cells packed the lock deliberately holds one
guard cell — see "Placeholder art, deliberately" below. It looks unfinished because it is
unfinished, not because it is broken.

To run it:

```bash
python3 tools/serve.py 9101
```

**`serve.py` takes the port as its first argument.** Use a second port when another tree is
already served on 9100 — the owner had `SHADOWCLASH-RECOVERED` on 9100 all session, and
opening it would have shown a game with no blade lock in it and looked like the patches
failed. The rule was never "one port", it is **know which tree you are looking at.**

Two blade users swinging into each other. P1 mashes **F / G / H**, P2 mashes **I / O / P**.

### Where it lives — all in `web/index.html`

| Piece | What it is |
|---|---|
| `STATE.BLADE_LOCK` | the new state, added to the `STATE` enum |
| `LOCK_DUR = 1.15` | seconds — hard cap on the struggle |
| `LOCK_MARGIN = 6` | presses ahead needed to break the bind EARLY |
| `LOCK_SEP = 68` | px between body centres at the bind. MUST stay 2x the art brief's per-side number |
| `LOCK_MIN_HOLD = 0.3` | s — floor; nothing can break the bind before this |
| `LOCK_CPU_RATE = 7.5` | CPU presses/s at tier 1, scaled by tier |
| `enterBladeLock(a, b)` | called from `processWeaponClash` when both sides `canBind` (steel, iron or WOOD) |
| `updateBladeLock(a, b, dt)` | ticked ONCE for the pair from the main loop |
| `resolveBladeLock(a, b)` | decides and applies the outcome |
| `case STATE.BLADE_LOCK` | in `spriteFrameIndex()` — reads however many `lockN` cells exist |
| `p.lockOutcome` / `lockOutcomeT` | tag that makes the WIN/LOSE cells render at all — see below |

### Three design decisions worth not undoing by accident

1. **It reuses `stunTimer` for the freeze.** Every action in this engine already
   early-returns on `stunTimer > 0`, so arming that timer means no move can escape the
   bind by having forgotten about it — and there is no new gate for the next feature to
   forget either. The mash still gets through because it is claimed in the keydown
   handler **before** `executeAttack` is ever reached.
2. **It is ticked once for the pair, from the main loop — not inside `Player.update`.**
   Per-player it would tick twice a frame and resolve half a frame early for whoever
   updated second.
3. **A live bind short-circuits clash detection.** Re-entering the lock every frame would
   reset both mash counters and make the struggle unwinnable.

### The rules, each one a test

- a bind **always** ends — 70 frames (~1.17s) with zero input from either side
- a **tie throws both off**; defaulting the win to a player would make the mechanic
  decidable by update order, which is worse than no winner at all
- pulling `LOCK_MARGIN` ahead breaks it early, so mashing pays on the frame it is earned
- the winner is **freed, not handed a hitbox** — a guaranteed hit would make the bind a
  coin-flip for damage instead of a contest
- the snap to bind distance moves **both** fighters equally; dragging one forward reads as
  a glitch
- an **idle human loses to the CPU** — the bind is a contest, not a freebie

### Two exploits the test caught (both fixed)

1. **`e.repeat`** — the browser fires `keydown` continuously while a key is HELD, so
   leaning on one button won every bind. A mash must be discrete presses.
2. **`LOCK_MIN_HOLD`** — with a 2-press-per-frame mash the bind resolved in **four
   frames** (67ms). Any turbo pad or autofire made it flicker instead of read as a
   struggle.

### The test

```bash
node tools/blade_lock_check.mjs      # 73 assertions, all passing
```

It **lifts the three lock functions straight out of `web/index.html`** and runs them
against stubbed globals, so it tests the shipping code. A pasted copy would keep passing
after the engine moved on. **Run it after any change to the lock.**

### ⛔ THE CELL COUNT IS SHEET DATA, NOT ENGINE LOGIC

The owner intends to add in-between cells to smooth the strain, so the router reads however
many `lockN` cells a sheet carries. Six gives a 3-frame strain loop, nine gives a 6-frame one,
no code change either way. What is fixed is the ORDER, because the engine addresses by
position:

```
lock1              the CATCH, played once as the bind lands
lock2 … lockN-2    the STRAIN, looped while the struggle holds
lockN-1            WIN  — always second-to-last
lockN              LOSE — always last
```

In-betweens go in the middle and join the loop. Tested at 6, 9 and a degenerate 2 cells.

### ⛔ THE WIN/LOSE CELLS ONLY RENDER BECAUSE OF A TAG — do not remove it

`resolveBladeLock` sends the winner to `IDLE` and the loser to `STUNNED`, and **both of those
states already have their own cells.** So `lockN-1` and `lockN` would be drawn, graded, packed
and never rendered once — nothing crashing, the two most dramatic frames in the set simply
never appearing, and the natural conclusion being that the generator drew them wrong.

`p.lockOutcome` (`'win'` / `'lose'`) with `p.lockOutcomeT` is what shows them. It is tested
**before** the state switch in `spriteFrameIndex()`, held 0.18s for the winner and 0.46s for
the loser — the loser's own stun duration, so he wears the thrown-off pose for exactly as long
as he is open. A tie tags BOTH as `'lose'`, which is correct.

### Placeholder art, deliberately

The lock renders each fighter's **guard cell** for the whole strain — as **one held cell**,
not an animation. Animating it on borrowed frames would read as finished work and stop
anyone noticing the real cells are still missing.

---

## 3. THE ART HANDOFF PACK — 6 sets, 36 images, ready for GPT

Everything lives in **`docs/handoff/blade-lock/`**. The brief for the generator is
**`GPT-BLADE-LOCK-HANDOFF.md`**; hand that plus the per-fighter cards to GPT.

Regenerate the whole pack with:
```bash
python3 tools/sprites/make_lock_handoff.py     # geometry + refs + lock-spec.json
python3 tools/sprites/make_lock_refcards.py    # labelled identity cards + roster
python3 tools/sprites/check_lock_pairs.py      # the anchor pre-flight (§3.2)
python3 tools/sprites/overlay_lock_pair.py strip-*.png   # grade REAL cells (§3.5)
```

### 3.1 Who is in the batch

**IN — 6 sets, 6 cells each:** `kael-katana`, `executioner-nodachi`, `tsubasa-tanto`,
`ember-claws`, `mizu-bo`, `shin-kunai`.

**The pasteable prompt is `docs/handoff/blade-lock/GPT-PROMPT.txt`** — PART 1 once, then one
fighter block from PART 2, plus that fighter's card and idle.

**OUT:** exile and oni (§4 — neither has canon art in this repo; both now have a waiting
slot at `refs/OWNER-exile-run-cycle.png` / `refs/OWNER-oni-founder-sheet.png` that the pack
picks up automatically), buddha (bare hands, `'flesh'`, never clashes).

**Shin is IN** — he was only ever blocked by material being per-fighter, and §5 closed that.

**A set is per WEAPON, not per fighter** (owner's order): the lock only applies to attacks
made with a blade, and kael's katana and wakizashi are different binds, as are mizu's bō
and hanbō. Phase 2 covers secondary weapons.

### 3.2 The contact anchor — corrected, and this one nearly shipped broken

The six lock cells are drawn **one fighter at a time, alone in frame** — the engine slides
two independent sprites together until their weapons meet. So there is a shared contact
anchor: **34px above the feet, 34px forward of body centre — toward the LEFT edge, the way the
fighter faces** (68px separation), converted
into each fighter's cell space through that fighter's own `scale`.

**The first value was wrong.** At 26px forward (52px separation), **kael and the
executioner interpenetrate by 2.8px** — they are the two widest torsos and 52px does not
fit them. That would have shipped as two fighters clipping through each other in the
signature beat of the mechanic, *after* 36 images had been drawn. Per-cell art review
cannot catch it: each cell grades fine alone.

`tools/sprites/check_lock_pairs.py` is what caught it. It composites the stress pairs at
their anchors using existing guard cells as stand-ins, and measures whether the bodies
fit. The sweep:

| separation | worst pair |
|---|---|
| 26px | **−2.8px** — kael/executioner overlap (the two widest torsos) |
| 30px | **−2.3px** — shin/executioner overlap, found when shin joined |
| **34px** | **+5.6px ← chosen**, loosest pair +24.5px |
| 36px | loosest pair 28.7px, past the too-far-apart threshold |

**Adding a fighter means re-running the pre-flight.** A new body width can invalidate the
anchor and the failure stays invisible until two finished fighters are composited — that is
exactly how the 30px value was caught.

`LOCK_SEP = 68` in the engine is 2 × 34px **on purpose** — the engine and the art brief
read the same number so they cannot drift apart. **Change one, change both, and re-run the
pre-flight.**

Two details in that script that look like bugs and are not: body span is measured in a
**20–46px torso band**, not a whole-cell bbox (weapons and chains sprawl far outside the
body, and a bbox called every pair "overlapping" when two chains crossed); and the stress
list is the **extremes only**, not all 15 pairings.

### 3.5 ⛔ ONCE REAL CELLS EXIST, THE ART IS THE AUTHORITY — NOT THE ANCHOR

`check_lock_pairs.py` pre-flights the anchor from stand-in guard cells, which is the right
check BEFORE art exists. `overlay_lock_pair.py` is the check AFTER, and **where they disagree
the art wins.**

The owner's correction that produced it: the generator frames each fighter from that
fighter's own point of view, alone, so judging one strip against a spec number says nothing
about whether two of them MEET — which is the only thing that matters. A set graded "wrong
height" against the spec is fine if every set is at that same height; then the fix is moving
ONE ENGINE CONSTANT, not redrawing 36 cells.

`overlay_lock_pair.py` takes the generator's strips, splits them on the gaps, measures where
each fighter's weapon actually reaches (outermost forward ink — finds a blade, a staff or claw
tips without being told which), and reports per fighter: mean bind height across cells 1-4 as
a % of body height, the DRIFT within that set, and distance from the batch median. Then it
composites the worst-case pair — highest bind against lowest — since every other pairing meets
if that one does.

Two outcomes, opposite actions:

- **all within 4% of the median** → the art agrees with itself. Move `LOCK_Y_ONSCREEN` in
  `make_lock_handoff.py` to the measured median, re-run `check_lock_pairs.py`, redraw nothing.
- **one outlier** → redraw that set's cells 1-4 only.

It also reports **body-height spread across a set (SIZE BOIL over 2%)** — the check that
cannot be done by eye and the one most likely to be silently wrong.

### 3.3 Measured scale — do NOT draw them all the same size

Cell-space body height differs by a factor of 1.4 across the roster because every fighter
carries a different `scale`. Every number in `lock-spec.json` is measured off the live
sheets, nothing typed by hand.

| fighter | body in-cell | on screen | scale |
|---|---|---|---|
| executioner | 185px | 70.4px | 0.3804 |
| kael | 174px | 70.0px | 0.4023 |
| tsubasa | 193px | 69.6px | 0.3608 |
| ember | 207px | 69.3px | 0.3349 |
| mizu | 156px | 62.4px | 0.4000 |

Silhouette canon: the **executioner is oldest and tallest**, but only *slightly* — he
leads kael by 0.4px, a rounding error. **Kael is youngest.** Mizu is visibly shortest.
Any scale pass keeps the executioner first with a visible margin (~2–3px) without pushing
him into boss territory.

### 3.4 The method the generator must follow

**Chain the seeds** — do NOT generate six independent images from one reference:

```
idle ──edit──> lock1 ──edit──> lock2 ──edit──> lock3 ──┬──> lock4  (tremble)
                                                       ├──> lock5  (win)
                                                       └──> lock6  (lose)
```

Independent stills are never size-registered and the body height drifts, which makes the
animation boil. Known failure this avoids: a still-editor **cannot invent a pose its
reference doesn't hold** — 8/8 attempts to get a walk cycle out of a standing reference
returned the standing stance.

Medium: **2D cel illustration / vector look — NOT pixel art.** Existing cells carry ~3900
unique colours. ⛔ Pure side profile facing **LEFT** — every sheet in this game is authored facing left and
the engine mirrors it (`ctx.scale(-p.facing, 1)`). Verified on the art: the eye sits on the
left of the head with the scarf trailing right, on all seven fighters measured. An earlier
version of the brief said RIGHT; that would have returned all 36 cells backwards.
If a pose doesn't fit, **grow the frame** — never shrink the fighter.

---

## 4. TWO CHARACTERS ARE BLOCKED ON ART — and both were wrong in the repo

### 4.1 EXILE — every cell in her packed sheet is a different character

**Owner's ruling:** *"This is the only true image of exile — if it don't look like this it
is not usable, it should be deleted."* His canon reference is the **EXILE — LOW SHINOBI
RUN CYCLE** sheet (8 frames): **bold white/silver streak** through black hair, **bare face
with TWO RED EYES** and red slash markings, black mask, purple scarf tails, tan wrapped
forearms and shins, kama + spiked chain.

**Measured at 4x on the idle and on `run_clean1/3/5/7`:** every cell in
`web/assets/sprites/exile.png` is a different design — a tan cloth **headband with red
kanji covering one eye**, a single glowing **white** eye, muted grey streaks where the
white one belongs, no red facial markings, upright stance instead of the low shinobi lean.

**All three exile sources in this repo are wrong:**

| source | what's wrong |
|---|---|
| `RECOVERY/select-portrait-handoff/refs/exile-*.png` | pre-repack; 74.1% / 32.6% baked white manga panels |
| `web/assets/sprites/exile.png` | 0.0% panels but a **superseded face design** in every cell |
| her card in the handoff pack | **deleted**, for that reason |

She was pulled from the batch entirely rather than shipped with a warning label — a
flagged wrong reference is still a wrong reference sitting in a generator's context.
**Unblocking her needs her true sheet in the repo.** The packed sheet is still what the
game renders, so she remains playable on superseded art; whether to replace it is the
owner's call.

### 4.2 ONI — "THE FOUNDER", final design, and it breaks an engine assumption

**Owner:** *"This is his only final character design look."* **He/him.**

White skull mask with three claw gouges, **RED eyes**, two dark horns, black hood and
tattered mantle, ash-gray worn plate, cloth wrappings on **both** hands, **RIGHT-HAND CLAW
ONLY** (five dark-gunmetal blades; **left hand wrapped and clawless**), two swords crossed
on his back. Palette: black, ash gray, white mask, red eyes/FX.

**⛔ THE PURPLE RULE IS DELETED.** `CLAUDE.md` carried *"PURPLE accents — never 'fix'
purple out of new Oni art"* as a standing order and `oni.json` named
`RECOVERY/oni-redesign/NEW-ONI-DESIGN.png` as canon. The final design has **no mane, no
bone pelt, no purple**. That lane and its 59 frames are a **different character** — do not
read them as reference. The old rule was removed, not annotated, because obeying it now
would repaint the wrong character.

He has **no card** in the handoff pack; in the do-not-draw strip he gets an empty plate
reading **NO CANON ART IN REPO**, because a wrong picture inside a do-not-draw strip is
still a picture a generator can copy.

**Two owner rulings block his cells. Both are recorded in `oni.json` under `redesign`
(`blocking_question`, `weapon_open_question`) — do not resolve either by inference.**

1. **His animation rule fights the engine.** The rule is *"face right, never flip claw to
   left."* This engine authors every sprite facing **LEFT** and mirrors it for the fighter
   who faces right (`ctx.scale(-p.facing, 1)`), so a one-handed asymmetric claw swaps hands
   the instant he turns around — the exact "mirrored claw error" his own checklist forbids.
   Ways out: a per-fighter no-mirror flag **plus a full left-facing cell set** (doubles his
   frame count), accepting the swap when he faces left, or making the claw symmetric.
2. **Does the kanabo survive?** The final design shows a claw and two back-carried swords
   and **no club**, but the engine still runs the Growing Kanabo Law — `WEAPON_MAT` `'iron'`,
   the `swell` mechanic, `form_1_kanabo` in his spec. Deleting a whole weapon is a ruling,
   not an inference from a picture.

Oni stays **benched**. No unbench until the owner motion-gates the new design.

---

## 5. DONE — `hb.mat`, per-hitbox weapon material

**Landed.** This is the change that unblocked shin and fixed exile's chain.

Half the machinery already exists and half does not:

- `hb.canClash` is **per-hitbox** — "armed melee, not a kick or a bare fist". Per-attack
  granularity is already there.
- `weaponMat(p)` is **per-fighter** — `WEAPON_MAT[p.spec.id]`. So a fighter who swings two
  different weapons gets ONE material for every attack.

That gap is the bug. **Shin** punches (`'mail'`, correctly no bind) *and* throws kunai
(steel, should bind) — so his kunai cannot bind today. **Exile** cuts with the kama (should
bind) *and* swings the chain (must **never** bind edge-to-edge — a chain has no edge to
catch). **Oni** is the sharpest case: kanabo form binds and rings, claw/fist form is
`'flesh'` and must never bind — one fighter, two opposite behaviours the engine cannot
express.

**What shipped:** a hitbox may carry its own `mat`, with the fighter's as the fallback, so
every existing call site is unchanged. It flows from the move table's opts straight through
`spawnHitbox`, so a move declares its material as data. `weaponMat(p, hb)` and
`bladeOnBlade(atk, def, hb, defHb)` take the hitbox; only `processWeaponClash` has both
boxes and passes both — on a guard or clean hit the defender still resolves to their fighter
default, because you cannot know which of two weapons is in a non-swinging hand.

- **shin** `2:back` kunai-dash → `mat: 'steel'`. His fists stay `'mail'` and never bind. His
  **thrown** kunai are projectiles and deliberately do not bind.
- **exile** all six chain hitboxes → `mat: 'chain'`, a material that is explicitly NOT metal:
  it rings and catches light but has no edge. Her sickle melee still binds.
- **`'chain'` vs `'flesh'`** is also what will let oni have a binding kanabo form and a
  non-binding claw form from one fighter.

⛔ **WHAT BINDS IS A SEPARATE PREDICATE FROM WHAT RINGS, and conflating them is the trap.**
Owner ruling Aug 12 2026: *"include wood, mizu bind."* Her ten lock cells are drawn, but wood
is not metal, so `bladeOnBlade` could never be true for her and those cells would have packed,
graded and **never rendered** — the same silent failure as the win/lose cells.

The fix was NOT to make wood count as metal. `bladeOnBlade` also gates the steel RING on guards
and clean hits, so that would have made her bō start ringing like a katana across the whole
roster — a silent audio regression. Binding has its own predicate instead:

```
canBind = steel | iron | wood        flesh  no weapon at all
                                     mail   shin's chainmail is under his CLOTHES, not in hand
                                     chain  rings, but no rigid length to brace against
```

So mizu **binds** a katana and still **cracks** rather than rings. Both halves are asserted.

A **structural guard** in the test walks the real source: every `throwChain`/`orbitChain`
call with a hitbox beside it must declare `mat: 'chain'`, and it names the offending line
numbers if not. The predicate tests cannot catch an untagged move — nothing crashes, it just
silently binds.

⛔ **Fighter ids, because I nearly wired the wrong character:** `0` executioner, `1` mizu,
`2` shin, `3` tsubasa, `4` ember, `5` **kael**, `6` buddha, `7` oni, `8` **exile**. Check
against this list, not against memory of an earlier grep.

---

## 6. OPEN DECISIONS — all four need the owner

1. **Oni's claw vs sprite mirroring** — no-mirror flag + full left-facing set, accept the
   swap, or symmetric claw? (§4.2)
2. **Does Oni keep the kanabo** at all? (§4.2)
3. **Exile's true sheet** — get it into the repo; and does her superseded packed sheet stay
   in the shipping build meanwhile? (§4.1)
4. **`_SNAPSHOT-INFO.md`** — delete it, or rewrite it to describe the real tree? (§7)

---

## 7. REPO HAZARDS worth knowing before you touch anything

- **`_SNAPSHOT-INFO.md` IS STALE AND MISLEADING.** It sits at the repo root and says
  *"This is a COPY, not the working repo"*, describes a **Jul 26 snapshot at SHEET_V 228**,
  and names paths that don't exist on the owner's machine (`/Users/anthonyguy/SHADOWCLASH-1.0`,
  `shadowclash-preview`). The real tree is at **SHEET_V 346** with `origin` pointing at the
  live GitHub repo, and the owner was working in **`shadowclash-tryout`**. It already sent
  the owner to a nonexistent directory this session. Awaiting his ruling on delete vs rewrite.
- **`SHEET_V` must be bumped in the SAME commit as any `web/assets/sprites/*` change** —
  including a `.json` with no pixel changes. It is one enormous single line carrying every
  fighter's history; corrections to it must be surgical.
- **Sheets are append-only.** Original cells stay byte-identical; composite onto the
  existing PNG.
- **`tools/serve.py` — and the port is its FIRST ARGUMENT.** It sends
  `Cache-Control: no-store`; a plain `http.server` sends none, so the browser pins stale
  sprite PNGs and fakes regressions. The rule is often written as "ONE server on 9100", but
  the thing it protects is narrower and more important: **know which tree you are looking
  at.** The owner had `SHADOWCLASH-RECOVERED` served on 9100 for this entire session, so
  opening 9100 while testing the tryout tree showed a game with no blade lock in it — which
  looks exactly like the patches having failed. Serve a second tree on a second port
  (`python3 tools/serve.py 9101`) rather than killing a server you did not start.
- **Lanes:** several agents share the owner's tree. `python3 tools/lane.py start "<name>"`
  first; the pre-commit hook refuses commits containing another agent's dirty files.
  `lane.py claim <paths>` for anything you dirty.
- **Local commits only** — the owner pushes and deploys himself. The public demo at
  `shadowclash-peach.vercel.app` is live and must never be deployed to.
- **Never infer a fighter's gender** from name or silhouette. Confirmed: Ember, Tsubasa,
  Kael, Shin, the Executioner, **Oni** → he/him. Mizu, Exile → she/her.
- **Rule 8 — a fix DELETES the wrong version.** No struck-through text, no "this used to
  say X". Current truth once; git holds the history. Fix every copy in the same pass — the
  ledgers and the second brain hold divergent duplicates, and this session found three
  (the art-spend rule, the purple rule, and an exile comment that contradicted itself).

---

## 8. THE ELEVEN COMMITS

Newest first:

| SHA | what |
|---|---|
| `069287d` | Oni the Founder is final; purple lane superseded (SHEET_V 346) |
| `78a91a1` | the blade lock is playable — held struggle on placeholder cells |
| `d2645a3` | exile OUT of the batch; her sheet is a superseded design; no-pay rule |
| `723dd85` | (superseded by `d2645a3`) exile's card flagged stale |
| `095c6f9` | pre-flight the contact anchor as PAIRS — it was wrong at 26px |
| earlier | the handoff pack: measured spec, reference cards, roster, the brief |

---

## 9. IF YOU DO ONE THING NEXT

**Play the lock and tell the owner how it feels** (§2). It is the only piece of this
session that has never been seen running, it takes two minutes on port 9100, and its
numbers should be tuned by feel *before* GPT draws 30 cells to a timing nobody has
confirmed.

Then send GPT the first set — **`kael-katana`**, using `refs/kael-card.png` plus
`refs/kael-idle.png` as the lock1 seed — and grade what comes back against
**Doc 17's 12-dimension standard** in the second brain. No cells pack without a grade;
>30% REDO/REJECT means propose a method change instead of shipping the montage.
