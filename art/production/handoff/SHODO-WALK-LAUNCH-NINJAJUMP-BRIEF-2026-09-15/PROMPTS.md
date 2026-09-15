# Prompts — per fighter, per row

Read `§0` before generating anything and `BOARD-SPEC.md` before delivering anything.

**The paste-ready per-fighter prompts live in `prompts/<fighter>.md`** — one self-contained
file per character, carrying all three rows, that fighter's beats, prompt text, pitfalls and
packing notes. This file is the shared law they all assume: the canon table (§0), the scaffold
and the packing traps (§1), and the per-row rules (§2–§4).

---

## §0 — Canon is law. Get this wrong and the board is scrap

Wrong weapon count is the single most common failure on this project. Before every prompt,
check the fighter against this table and against `refs/<fighter>-refs.png`.

| fighter | weapon — exact | head | palette | never |
|---|---|---|---|---|
| **Executioner** | ONE slim katana | deep-purple hood, two curved horns in the hood silhouette | orange `#f97316` scarf/sash, orange-yellow eyes | no greatsword (retired) |
| **Mizu** | ONE long tan wooden bo staff, both hands | hood | purple robe `#7e22ce`, `#a855f7`, `#c084fc` scarf, white eyes | never a blade |
| **Shin** | bare hands + ONE four-point wire shuriken, chainmail head to toe | dark-green hood | deep-teal scarf, pale-cyan eyes | **no blades**; **ONE eye is canon — never "fix" it** |
| **Tsubasa** | exactly TWO small tantō, **reverse grip** | **NO HOOD** — spiky black hair, red streaks | black / dark red, red scarf | never a hood, never three knives |
| **Ember** | tekkō-kagi claws — blade count **CONTESTED, see below** | hood | ⛔ **GREY / achromatic — not green** | **never a sword** |
| **Kael** | ONE **long** katana + ONE **short** wakizashi — difference obvious at a glance | gold/amber hood | black body, gold scarf + sash, glowing amber eyes | never two equal blades |
| **Mokurai** | **BARE HANDS**, prayer beads wrapped round the fists | no hood, gray carved stone mask, red forehead jewel | saffron/ochre, maroon scarf | **never a staff, ever** |
| **Exile** | long-bladed kusarigama, **SPIKED** iron ball, long chain | **UNHOODED** — huge black-and-silver mane, tan cloth eye-wrap, dark-red kanji | red iris `#B94828` | never hooded; never a smooth ball |

**Purple belongs to the Executioner and Mizu only.** It is forbidden on the other six.

### ⛔ Two Ember corrections, both caught late and both measured

**1 — Ember is GREY, not green.** Owner ruling 2026-09-11 (the story-bible merge): *"Ember is
grey, with grey eyes. The roster row saying Green is wrong and is never used."* The sheet
agrees — measured on his newest idle cell 505, saturation spread averages **4.7** and peaks at
**24**, with **zero** pixels above 40. It is achromatic warm grey. The greens still in the
roster data (`#84cc16` / `#3f6212` / `#15803d`) drive the **UI and the vector fallback**, not
the shodō sheet. **Do not put a green in an Ember prompt.**

**2 — His blade count is genuinely contested and is an OWNER RULING, not mine to make.**

| evidence | says |
|---|---|
| his **newest** packed idle, cells 505 / 509 (`SHEET_V 836–837`, days old) | **THREE** per hand |
| older attack rows — `clawrend4` (287), `erake4` (318) | **FOUR** per hand |
| his newest source boards, named `…three-claw-corrected` | **THREE** |
| the standing note in my own memory | **FOUR**, "never shrink to three" |

Both are on the sheet right now. The prompts in `prompts/ember.md` say **three**, because a new
row has to match the art it will sit beside and the newest approved art is three — **but if the
owner says four, it is a one-word change in three places.** Ask before generating Ember.

Pronouns: Mizu and Exile are **she/her**. Everyone else is he/him. Ember is **male** —
this has been got wrong before.

---

## §1 — The scaffold every prompt needs

Every prompt in this file already contains it. If you write a new one, it must carry all of
this or the board will not pack:

> 8 frames in one horizontal row, evenly spaced, identical camera and identical character
> scale in every frame. Full body, both feet visible, nothing touching the frame edge. Plain
> flat background — **no ground line, no cast shadow, no floor bar, no dust**. Side-on 2D
> fighting-game view. Sumi-e ink-brush *shodō* styling on an ash-grey palette: full-black
> sumi and bone-white light. No motion-blur smear running off the frame.

The "no ground shadow" clause is not stylistic. The packer welds the board's **lowest ink**
to the floor line, so a painted shadow *becomes* the feet and the fighter hovers above it.

### ⛔ Generate as a ROW, deliver as EIGHT FILES

The prompts ask for one horizontal row on purpose — eight beats generated in one pass hold
one body size, and the packer applies **one scale to the whole board**, so a size drift
between beats ships as a fighter who changes size mid-animation. But the packer globs
`frame-01.png … frame-08.png`, **one file per beat**. So: generate the row, then **slice it
into eight equal files** at even gutters before delivering. `BOARD-SPEC.md` has the layout.

### ⛔ Two packing traps, and one of them hits 16 of the 24 rows

**1 — the scale anchor.** `pack_keyed_board.py` measures ink area on **beat 1** by default and
applies that scale to the whole row. That is right for a walk, where beat 1 is a stance. It is
**wrong for every launched row and every second-jump row**, because beat 1 there is the pop or
the launch — the most extended frame in the board — and anchoring on it packs the whole row
too small. The banner in the tool says it outright: *"DO NOT ANCHOR ON THE LARGEST BEAT."*
For those 16 rows pass an explicit `--scale` taken from that fighter's idle, or `--anchor` at
the most neutral beat in the row. **Always `--dry` first and read the deviation column.**

**2 — the cell is not tall enough for an airborne arc.** The union of eight airborne beats is
taller than a standing pose, and the packer refuses rather than crop: `REFUSE: scaled window
exceeds cell — grow the cell`. Budget `grow_frame.py --down` (this is how Tsubasa went 320→332).
It is not a reason to shrink the fighter.

### Cell aspect, per fighter

Frame the board to the fighter's own cell or the pack wastes resolution:

| shin | executioner | mokurai | exile | kael · mizu | tsubasa | ember |
|---|---|---|---|---|---|---|
| 1.41 | 1.30 | 1.21 | 1.11 | 0.94 | 0.91 | 0.87 |

---

## §2 — Row A · `walk1..8` · the walk cycle

*Per-fighter prompts: **`prompts/<fighter>.md`**, Row A.*

**The one rule that overrides everything else in this row: every beat must be equally strong.**

One push lasts ~8 frames and shows about three consecutive cells — but **`animPhase` is never
reset**, so each push resumes the cycle wherever the last one stopped. Driven live: push 1
showed beats 5·6·7, push 2 showed 1·2·3, push 3 showed 5·6. **All eight are reachable and the
window moves.** A cycle with two hero poses and six in-betweens will stutter every time a push
lands on the in-betweens.

*(An earlier draft of this brief said only beats 1–3 are ever seen and told you to front-load
them. That was wrong and is corrected — see `MEASUREMENTS.md` §1.)*

**RULED Sep 15 2026:** each fighter now walks exactly **one full loop** before breaking into
the run — 0.514s (Shin, Exile) to 1.029s (Mokurai), derived per fighter, no table. All eight
beats are seen in order every push. Draw a true loop: beat 8 must flow back into beat 1 with
no jump, and make every beat count.

Second rule: the walk is paced **flat**. A run has contact holds because a sprint slams; a
stroll does not. Even cadence, even spacing.

Third rule, from the same code: `footDust`, body lean and travel-facing are **`STATE.RUN`-only**,
so **the walk row plays forward while backpedalling**. Upright, weight-centred, no strong
forward lean.

---

## §3 — Row B · `airhurt1..8` · the launched hurt arc

*Per-fighter prompts: **`prompts/<fighter>.md`**, Row B.*

**Beat 1 is on screen for more than half the launch.** Measured against a −390 launcher with
0.5s of hitstun: `airhurt1` covers roughly **0 → 0.28s** (the entire rise), beat 2 gets 0.14s
at the apex, beat 3 gets 0.08s. Spread across eight beats the shape holds — **the early beats
carry the move**. A launched pose that only becomes interesting at beat 6 is wasted.

**The one thing this row is for:** at the apex there is **no muscle tone, no guard, no
intent**. A rag, not a pose. This is the only row in the game where the silhouette should
read as broken rather than composed. Weapons stay in hand — nobody is disarmed — but they
hang loose and trail.

⛔ **"Launched" is the name, not the trigger.** The engine cannot tell a launcher from any
other air hit: a plain airborne hit already forces `vy = min(vy, -250)`, which lands in the
same band as a −390 uppercut. `launch` only changes the **attacker's** impact FX. So **this row
plays on every air hit, including a light air jab** — draw violence the fighter can survive
being shown for a poke as well as for a 192px launch. Do not make beat 1 so extreme it reads
as absurd on a jab.

---

## §4 — Row C · `njump1..8` · THE SECOND JUMP

> **Owner, Sep 15 2026:** *"make the extra flip a second jump… jump and roll into a ball in
> air"* · *"a more athletic flexible jump with a curl into a ball, maybe people have a
> different type of jump."*

This is the **air jump** — the second press, while already airborne. Every fighter already
has one; today it is a procedural 360° rotation of the standing flight drawing, which is why
it reads as a cardboard cut-out spinning rather than a body tumbling.

**Shared rules for all eight:**

- **Beat 1 is already off the ground and already committing.** The crouch-load is not in this
  row — `jsquat` owns that, and this jump starts in mid-air anyway.
- **One full revolution across the eight beats, and it must land upright.** Beat 8 is the
  body opening back out, legs down, ready for the landing row to take over.
- **The rotation is the read.** Each beat must be unmistakably further round than the last.
  Two beats at the same angle is a wasted frame and a visible stutter.
- **Volume must not change.** The single hardest thing about this row: a curled body is the
  same mass at every angle. Limbs do not vanish behind the torso and reappear larger.
- **Weapons never clip the body.** Nobody curls onto their own blade.
- This runs **0.45 seconds** — about 56ms a beat. It is fast. Read it as a silhouette.

### §4.1 Tsubasa — the tightest ball on the roster

*Precision as a religion. The smallest, cleanest revolution — no wasted arc.*

> 8 frames in one horizontal row, evenly spaced, identical camera and identical character
> scale in every frame. Full body, both feet visible, nothing touching the frame edge. Plain
> flat background, no ground line, no cast shadow, no floor bar. Side-on 2D fighting-game
> view, sumi-e ink-brush shodō styling on ash grey.
> A lean young ninja, **no hood**, spiky black hair with red streaks, black and dark-red
> outfit with a long red scarf, holding **exactly two small tantō knives in reverse grip**,
> performing a tight forward somersault in mid-air.
> Frame 1: feet leaving, knees starting up, chin tucking, scarf snapping straight down.
> Frame 2: knees to chest, arms drawing in, both knives crossed flat over the shins.
> Frame 3: a tight compact ball, body a quarter turn forward, scarf beginning to whip round.
> Frame 4: half turn, fully inverted, ball as small as it gets, scarf a red ring around him.
> Frame 5: three-quarter turn, the ball just starting to open, knees releasing.
> Frame 6: legs extending downward, arms opening, knives coming back to guard.
> Frame 7: nearly upright, legs reaching for the ground, body still angled forward.
> Frame 8: upright, knees soft, both knives in reverse-grip guard, scarf settling.

### §4.2 Shin — the fastest, the lowest, barely a ball at all

*Speed 10. His revolution is the quickest on the roster and he unwinds into his own low stance.*
Backward tuck, arms wrapped round the shins, chainmail bunching at the joints.
**No blades in any frame** — bare hands, and **one eye**.

> …A compact ninja in **full chainmail head to toe** under a dark-green hood with a deep-teal
> scarf, **pale-cyan single eye**, **no weapons at all, bare hands**, performing a very fast
> tight backward tuck in mid-air.
> Frame 1: feet snapping up behind him, spine beginning to round backward.
> Frame 2: arms clamping round the shins, head tucking to the knees, chainmail bunching.
> Frame 3: quarter turn backward, a hard compact ball, scarf trailing forward.
> Frame 4: half turn, inverted, the smallest and fastest point of the tumble.
> Frame 5: three-quarter turn, grip on the shins releasing.
> Frame 6: legs whipping down and forward, arms out for balance.
> Frame 7: nearly upright, weight already dropping into a crouch.
> Frame 8: his low fighting stance, knees deep, hands open and empty.

### §4.3 Ember — a feral ball, not a gymnastic one

*His idle is a twelve-beat animal prowl. His air jump should look like a cat balling up, not
a gymnast.* Spine-first curl, claws drawn in tight against the chest, then he **snaps open
claws-first**. Predatory, not schooled.

> …A hooded ninja in **achromatic warm greys — black, ash and bone, no green anywhere**, pale
> grey eyes, wearing **tekkō-kagi claw gauntlets with THREE long parallel silver blades on each
> hand — claws, never swords** (see the blade-count note in §0 before generating), curling into
> a feral ball in mid-air like an animal.
> Frame 1: spine rounding first, shoulders hunching, head dropping — the curl starts at the back.
> Frame 2: knees driving up outside the elbows, all six claw blades drawn in tight across the chest.
> Frame 3: quarter turn forward, a hunched irregular ball, claws glinting inside the tuck.
> Frame 4: half turn, inverted, body coiled and tense — compressed, not relaxed.
> Frame 5: three-quarter turn, the coil beginning to release, claws leading.
> Frame 6: snapping open claws-first, arms thrown wide, legs still trailing.
> Frame 7: landing shape, claws forward and low, back still arched.
> Frame 8: the low forward prowl stance, both clawed hands leading.

### §4.4 Kael — the schooled somersault, and he curls around his own blades

*The last student of a real school. His is the only textbook-correct rotation — and the only
one with the problem of two drawn blades.* **You do not curl onto your own edges**: both
swords are held out and away from the tuck through the whole revolution.

> …A young ninja in black with a **gold-amber hood**, gold scarf and sash, glowing amber eyes,
> holding **one LONG katana in one hand and one clearly SHORTER wakizashi in the other — the
> length difference obvious at a glance**, performing a disciplined forward somersault in mid-air.
> Frame 1: feet leaving, knees rising, both blades sweeping outward away from the body.
> Frame 2: knees to chest in a clean tuck, both swords held out wide, clear of the legs.
> Frame 3: quarter turn forward, textbook ball, blades extended on either side like outriggers.
> Frame 4: half turn, fully inverted, hood and gold scarf trailing a full circle, blades still clear.
> Frame 5: three-quarter turn, tuck opening, blades beginning to draw back in.
> Frame 6: legs extending down, both swords returning toward a guard.
> Frame 7: nearly upright, long blade high and short blade low.
> Frame 8: upright landing stance, long katana high, wakizashi across the body.

### §4.5 Mizu — she cannot ball up around a two-metre staff, so the staff becomes the axis

*The owner's own "maybe people have a different type of jump", made literal.* She does not
curl around her own centre — she curls **around the bo**, which stays horizontal through the
rotation while she pivots on it.

> …A slender kunoichi in a purple robe `#7e22ce` with a light-purple `#c084fc` scarf and white
> eyes, holding **one long tan wooden bo staff in both hands**, spinning around the staff in
> mid-air. The staff stays roughly horizontal in every frame and she rotates around it.
> Frame 1: staff snapping horizontal across her hips, knees folding up toward it.
> Frame 2: knees hooked up over the staff, hands wide on the shaft, body folding around it.
> Frame 3: quarter turn, curled tight around the horizontal staff, robe billowing.
> Frame 4: half turn, inverted, hanging in a compact curl around the staff's axis.
> Frame 5: three-quarter turn, legs beginning to unhook.
> Frame 6: legs swinging down past the staff, hands sliding to the ends.
> Frame 7: nearly upright, staff rotating toward a vertical guard.
> Frame 8: upright, staff planted in a two-handed guard, robe settling.

### §4.6 The Executioner — he does not tuck. He pikes

*The oldest, tallest and slowest man on the roster, in heavy robes, carrying a katana. A
somersault would be a lie.* His second jump is a **heavy half-turn pike** — legs straight,
hinged at the hips, the sword carried overhead through the arc. Weight over agility. He is
the one fighter whose air jump should look like it costs him something.

> …A tall, heavy, broad-shouldered figure in a **deep-purple hood with two curved horns built
> into the hood silhouette**, bright orange `#f97316` scarf and sash, orange-yellow eyes,
> holding **one slim katana**, performing a slow heavy piked turn in mid-air — legs straight,
> folded at the hips, never curled into a ball.
> Frame 1: feet leaving heavily, hips hinging, sword sweeping up.
> Frame 2: a deep pike — legs straight, body folded forward at the waist, sword overhead.
> Frame 3: quarter turn, still piked, robes dragging behind the rotation.
> Frame 4: half turn, inverted and piked, horns and orange sash flaring wide.
> Frame 5: three-quarter turn, the fold beginning to open.
> Frame 6: legs swinging down, sword coming round and down with the weight.
> Frame 7: nearly upright, heavy, sword low and trailing.
> Frame 8: upright, planted wide, katana in a two-handed low guard, robes settling last.

### §4.7 Mokurai — the only serene rotation in the game

*A monk who does not rise for anyone. He still curls — but it is a **seated meditation tuck**,
full lotus, hands together, turning slowly and calmly while everyone else tumbles.*
**Bare hands with prayer beads. Never a staff.**

> …A calm monk with **no hood**, a **gray carved stone mask with a red jewel on the forehead**,
> saffron and ochre robes, maroon scarf, **bare hands with prayer beads wrapped round both
> fists — no weapon, no staff**, drawing up into a seated meditation posture in mid-air and
> rotating slowly.
> Frame 1: feet lifting, legs beginning to fold inward, hands coming together.
> Frame 2: legs crossing into a lotus fold, palms pressed, beads swinging out.
> Frame 3: quarter turn, a serene seated ball, robes settling around him.
> Frame 4: half turn, inverted, still perfectly composed and still seated, beads orbiting.
> Frame 5: three-quarter turn, hands beginning to part.
> Frame 6: legs unfolding downward, beads trailing.
> Frame 7: nearly upright, one foot reaching.
> Frame 8: upright, feet planted, hands open at his sides, beads settling.

### §4.8 Exile — the chain does the curling

*A long chain and a spiked ball are the problem and the answer.* She curls, and the **chain
wraps around her** through the rotation while the spiked ball orbits outside the tuck. Her
mane is half the silhouette.

> …An unhooded kunoichi with a **huge black-and-silver mane**, a **tan cloth wrap over one
> eye with dark-red kanji on it**, one visible red eye, holding a **long-bladed kusarigama on
> a long chain with a SPIKED iron ball on the other end**, curling into a ball in mid-air
> while the chain wraps around her and the spiked ball orbits outside.
> Frame 1: feet leaving, chain slack and beginning to loop, ball swinging wide.
> Frame 2: knees drawn up, sickle held close, the first wrap of chain crossing her back.
> Frame 3: quarter turn, tight ball, chain wrapping, ball flung out at the end of its arc.
> Frame 4: half turn, inverted, mane fanned wide, chain looped around the tuck, ball at full extension.
> Frame 5: three-quarter turn, chain beginning to unwind, ball swinging back in.
> Frame 6: legs dropping, sickle coming out to lead, chain paying out.
> Frame 7: nearly upright, ball landing back in her free hand or trailing low.
> Frame 8: upright, sickle forward, chain hanging in a slack loop, mane settling.

---

## §5 — How to actually produce Row C, and probably Row B

**Row A (walk) is fine as stills.** Eight upright poses in one row is what a stills generator
is good at.

**Row C is a rotation, and rotation is exactly where independent stills fall apart.** The
failure is always the same: the volume changes. Limb count drifts, the weapon gains or loses
a blade at 180°, the body is a different size at beat 4 than at beat 2 — and the packer
applies **one scale to the whole board**, so a drift between beats lands in the game as a
fighter who changes size mid-tumble.

The owner's own instinct here is right: **block the motion first, then style it.**

1. **Blockout.** A crude 3D figure — proportions only, no detail — curled and rotated through
   one revolution. Even primitives work. The point is that the volume, the limb count and the
   weapon are *locked* by construction, and the silhouette at 180° is derived rather than
   imagined.
2. **Motion pass** through your motion lane, using the blockout as the structure and the
   fighter's existing sheet as the look reference. Reference `refs/<fighter>-refs.png` and
   `refs/ROSTER-true-scale.png` so the body size matches what is already packed.
3. **Pull 8 keyframes** at even rotation intervals — even *angle*, not even time.
4. Deliver as `frame-01..08.png` per `BOARD-SPEC.md` and it packs like any other board.

**Row B (the launched arc) benefits from the same treatment** for the same reason — it is a
body rotating through an arc while limp, and the apex is where a stills generator will quietly
give the victim their posture back.

Model choice is the owner's existing motion lane; this brief does not name one and does not
need to. **No paid generation is proposed by this document and none was performed to write it.**

---

## §6 — Order

1. **Pilot: Tsubasa `airhurt1..8`** — one board, proves generate → key → pack → one-line
   engine change → driven live.
2. The rest of `airhurt` — highest payoff per board.
3. `njump` — start with **Mokurai** (3 distinct flight poses today) and the **Executioner**
   (4), who have the most to gain.
4. `walk` — hold until the `WALK_TIME` ruling so the art is drawn to the right window.
