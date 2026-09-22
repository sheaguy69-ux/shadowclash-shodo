# Shadow Clash — BLADE LOCK cell handoff

**For:** an outside still-image generator (GPT-image class) drawing new animation
cells for Shadow Clash.
**From:** Claude Code (Opus 5) · 2026-08-11 · repo `sheaguy69-ux/SHADOWCLASH-1.0`
**Method (owner order):** frame-by-frame **STILLS**. No video, no i2v clips, no
harvesting frames out of a clip. Every image you make is a shipped cell.

Everything numeric below was **measured off the live sprite sheets** by
`tools/sprites/make_lock_handoff.py`, not typed by hand. Re-run that script to
regenerate this pack.

---

## 1. What we are building

The game already has a **weapon clash**: two swings meeting cancel each other with
sparks and a ring, over in about 130ms. We are turning that into a held **blade
lock** — weapons bind, both fighters strain against each other, and one wins the
push. Think the deadlock struggle from a samurai duel.

You are drawing **one fighter at a time, alone in the frame.** You are *not* drawing
two fighters locked together. The engine draws two independent sprites and slides
them together until their weapons meet, so a two-fighter picture cannot be used —
and with 6 lockers there would be 30+ pairings to draw. Each fighter presses against
**an opponent who is not in the image.**

---

## 2. THE MEDIUM — read this before anything else

> Clean high-contrast **2D cel illustration / vector look** — heavy black outlines,
> readable silhouettes, controlled dark palette, glowing featureless angled eyes.

**This is NOT pixel art.** Existing cells carry ~3900 unique colours. Do not
pixelate, do not posterize, do not reduce the palette, do not add a pixel grid.

⛔ **Every cell is a pure side profile facing LEFT.** Not right — **left**. Every sheet in
this game is authored facing left and the engine mirrors it for the fighter who faces right,
so a right-facing cell arrives backwards and every one of the 36 images would have to be
redone. Verified on the art itself: crop the head of any idle cell and the eye sits on the
**left** of the head with the scarf or hair trailing **right**. Never draw a right-facing or
three-quarter cell.

---

## 2b. ⛔ A SET IS PER WEAPON, NOT PER FIGHTER

The lock only applies to **attacks made with a blade**, and several fighters swing more
than one weapon. Those are different binds and need different cells — kael's long
katana and his off-hand wakizashi do not lock the same way, and mizu's long bō and
short hanbō are nothing alike.

So a set is named `<fighter>-<weapon>`, and the six cells are
`<fighter>-<weapon>-lock1..6.png`.

| set | phase | notes |
|---|---|---|
| `executioner-nodachi` | **1** | Two-handed nodachi. His only weapon — one set covers him. |
| `kael-katana` | **1** | The long blade, the bind he leads with. |
| `kael-wakizashi` | 2 | Off-hand short blade. Niten Ichi-ryū parries with it, so it is a genuinely different bind — close in, elbow high, long blade still live. |
| `tsubasa-tanto` | **1** | Both reverse-grip tantō together. He never binds with just one. |
| `ember-claws` | **1** | Tekkō-kagi. Not a cross — he **traps** the opponent's edge. |
| `mizu-bo` | **1** | Long wooden bō, hands wide. A lever braced across the body. **Wood BINDS** (owner ruling, Aug 12) — it does not ring like steel, but a bō catching a katana and holding it is the classic version of this mechanic. |
| `mizu-hanbo` | 2 | Short stick. Much closer bind, one hand, nothing like the bō pose. |

| `exile-kama` | **BLOCKED ON ART** | The packed sheet is a **superseded design** — cloth headband with red kanji over one eye, one glowing white eye. Her true look (owner's LOW SHINOBI RUN reference) is a bare face, **two red eyes**, red slash markings, a **bold white hair streak**. **Do not draw her from anything in this repo.** Her cells wait for that sheet. |
| `shin-kunai` | **1** | The **kunai he HOLDS** — short steel, very close bind. His **fists never bind** ('mail'), and his **thrown** kunai deliberately don't either. |
| `oni-claw` / `oni-kanabo` | **BLOCKED ON ART + AN OWNER RULING** | **Final design supersedes the drawn frames.** Iron kanabo, binds and rings. The club scales 1.0x → 2.0–2.5x on a strike, so a bind pose must show it **projecting**, not at idle size. Waiting on his sheet being packed, not on a design decision. |
| `oni-fist` | — | **NEVER BINDS.** His claw/fist form is `'flesh'` in the engine (`fistMode`), so it has no steel to meet an edge. |

**Phase 1 is the batch: 6 sets, 36 images.** (Exile was in it until her reference was
found to be a superseded design; she is out until her true sheet is in the repo.)

**Oni is two forms, and that is the sharpest illustration of why sets are per weapon:**
his kanabo form binds and rings, his claw/fist form is `'flesh'` and must never bind at
all. One fighter, two opposite behaviours — which the engine cannot express today,
because material hangs off the fighter rather than the hitbox. Phase 2 is a later pass; until it exists
the engine falls back to that fighter's phase-1 set, which is approximately right
rather than wrong.

**Shin is no longer blocked — the engine change landed.** Material used to be
per-**fighter** (`WEAPON_MAT[p.spec.id]`), so shin was `'mail'` for every attack and his
steel kunai could not ring while his fists correctly could not. A hitbox may now carry its
own `mat`, with the fighter's as the fallback, and his kunai-dash (`2:back`) is `'steel'`.
His **fists still never bind** — that is his fighter default doing the right thing.

Note his **thrown** kunai are projectiles and were deliberately left alone: they have their
own rules, and a blade in flight should not drag anyone into a held struggle. So his set is
the kunai he holds, not the ones he throws.

---

## 3. The cells — SIX IS THE MINIMUM, NOT THE LIMIT

**In-between cells are welcome.** The engine reads however many `lockN` cells a sheet
carries, so a set can be six or nine or twelve without any code change. What is fixed is the
**order of the beats**, because the engine addresses them by position:

```
lock1                    the CATCH, played once as the bind lands
lock2 … lockN-2          the STRAIN, looped for as long as the struggle holds
lockN-1                  WIN  — always the second-to-last cell
lockN                    LOSE — always the last cell
```

So extra in-betweens go **in the middle**, joining the strain loop. Win and lose stay the
last two, whatever the count. Six cells gives a 3-frame strain loop; nine gives a 6-frame
one, which is smoother.

## 3b. The six cells

Six stills per set, in this order. `<f>` is the fighter, `<w>` the weapon.

| # | file | beat | direction |
|---|---|---|---|
| 1 | `<f>-<w>-lock1.png` | **BIND — impact** | Weapons have just caught. Weight pitched forward over the front foot, both arms braced, head up. This is the frame of the catch, not the swing before it. |
| 2 | `<f>-<w>-lock2.png` | **BIND — settle** | The catch absorbs. Elbows compress slightly, rear foot digs in, shoulders drop. Body height must **not** change from lock1. |
| 3 | `<f>-<w>-lock3.png` | **STRAIN — a** | The held push. Deep forward lean, both hands committed, the whole body one straight line from rear heel to weapon. |
| 4 | `<f>-<w>-lock4.png` | **STRAIN — b** | Same stance, the tremble: a few pixels of shift in the shoulders and weapon **only**. lock3 and lock4 loop for as long as the struggle lasts, so they must read as **one pose breathing**, never as two different poses. |
| 5 | `<f>-<w>-lock5.png` | **WIN — push through** | Shoves the bind open. Front foot steps *through*, weapon drives forward and up past the crossing point, chest open, full extension. |
| 6 | `<f>-<w>-lock6.png` | **LOSE — thrown off** | Loses the bind. Torso rocks back, weapon knocked wide off the centre line, guard broken open, back foot catching the weight. Off balance but **still standing on both feet** — this is not a knockdown. |

---

## 4. ⛔ THE METHOD — chain the seeds

Do **not** generate six independent images from the same reference. Independent
stills are never size-registered to each other, and the fighter's body height will
drift between cells, which makes the animation boil on screen.

```
<f>-idle.png (reference)  ──edit──>  lock1
                     lock1  ──edit──>  lock2
                     lock2  ──edit──>  lock3
                     lock3  ──edit──>  lock4
                     lock3  ──edit──>  lock5      (branch: win comes off the strain)
                     lock3  ──edit──>  lock6      (branch: lose comes off the strain)
```

Each step is a **small delta** off an image that already holds the pose, so identity,
outline weight, palette and body size carry forward instead of being re-rolled. If
one cell comes back wrong, regenerate **that one cell** from its parent — never the
whole set.

**Known failure this avoids:** a still-editor cannot invent a pose its reference
doesn't hold. Eight of eight attempts to get a walk cycle out of a standing reference
returned the standing stance. A blade lock is a much better case — same footing,
near-static stance, small deltas — but only if each step is small. Do not try to jump
straight from the idle to the deep strain.

---

## 5. ⛔ SIZE — bigger than the target, never smaller

The cells get downscaled into the sprite sheet, so extra resolution survives as edge
quality. Too small and the packer has to invent pixels.

- Render at **2K on the long edge minimum** (4K is better, cost permitting).
- Never render below the target cell size in the table in §7.
- **The body must be the same size in all six cells.** Only the pose changes. If a
  pose doesn't fit the frame, **grow the frame** — never shrink the fighter, never
  crop the pose.

---

## 6. Background & keying

The cells are keyed to transparency by a corner floodfill, so:

- Background: **flat pure white `#FFFFFF`**, edge to edge, nothing else in frame.
- **No ground shadow. No drop shadow. No cast shadow.** The engine draws its own.
- No background elements, no scenery, no motion blur, no speed lines, no sparks, no
  impact flashes, no dust. The engine adds all VFX. A baked spark becomes a permanent
  white blob welded to the sprite.
- No text, no watermark, no signature, no frame border, no letterboxing.

---

## 7. ⛔ PER-FIGHTER SPEC — the scaling, measured

**The fighters are NOT all the same size in-cell.** Every fighter carries a different
`scale` factor, so the same on-screen height comes from a different pixel height in
the cell — ember is 207px tall in his cell and the executioner is 185px in his, yet
they stand within a pixel of each other on screen. Drawing them all the same in-cell
size is the one mistake that wastes a whole batch.

Match each fighter to **its own row**, and use the paired `refs/<f>-spec.png`, which
draws these lines on the actual art.

⛔ **BUT NOTE WHOSE JOB THIS IS.** These numbers are for CHECKING what comes back, not for
instructing the generator. Two size questions get confused and only one of them is the
generator's problem:

- **Between fighters — not the generator's job.** `pack_lock_cells.py` rescales each delivered
  set against that fighter's own existing in-game art at pack time. If the generator returns
  mizu at 1000px and the executioner at 1000px, they land at 62.4px and 70.0px on screen
  correctly, with no instruction. Asking a generator to hit relative sizes across independent
  images is asking for a failure it has no way to verify.
- **Within a set — entirely the generator's job, and unfixable afterwards.** One uniform scale
  cannot reconcile a catch drawn at 900px with a strain at 1000px. The packer refuses over 6%
  source spread for that reason.

So the prompt carries exactly one size rule — identical body height in every cell, feet to
crown, hair and horns included, weapon excluded — and tells the generator explicitly NOT to
think about other fighters.

⛔ **A MEASUREMENT TRAP, recorded because it produced a wrong answer once.** Excluding the
weapon by dropping ink narrower than 12% of body width also strips the executioner's HORNS and
tsubasa's HAIR SPIKES, which are part of the silhouette. That method ranked the executioner
5th of 6 and contradicted the roster canon that he is tallest. The correct method keeps
anything sitting over the head and drops only what juts away from it: take the head's widest
row in the upper half, widen that column band by 25%, and the topmost ink inside it is the
crown. Measured that way he is 70.0px and first, as the canon says — and the original bbox
figures in the table below were right all along.

| fighter | cell (WxH) | feet at y | body height in-cell | on screen | scale | weapon |
|---|---|---|---|---|---|---|
| **kael** | 300 × 320 | 312 | **174 px** | 70.0 px | 0.4023 | Katana & wakizashi / tantō |
| **executioner** | 300 × 412 | 404 | **185 px** | 70.4 px | 0.3804 | Nodachi / single katana |
| **tsubasa** | 301 × 320 | 312 | **193 px** | 69.6 px | 0.3608 | Dual tantō knives (reverse grip) |
| **ember** | 340 × 377 | 369 | **207 px** | 69.3 px | 0.3349 | Tekkō-kagi (iron claws) |
| **mizu** | 300 × 320 | 312 | **156 px** | 62.4 px | 0.4000 | Bō (wooden staff) |
| **shin** | 300 × 320 | 312 | **194 px** | 66.6 px | 0.3431 | Kunai (held, not thrown) |

**Silhouette canon, and it must survive to the screen:** the **executioner is the
oldest and tallest** of the roster — but only *slightly*, an inch, not a boss
silhouette. **Kael is the youngest.** **Mizu is visibly the shortest.** Keep that
order intact; do not "improve" anyone's height.

### The contact anchor — where the weapons meet

The blades have to meet in world space for *any* pairing, so the crossing point is
fixed on screen and converted into each fighter's cell space:

- **34 px above the feet** — mid-chest on a 70px fighter
- **34 px forward of body centre — toward the LEFT edge of the cell**, since the fighter
  faces left (so the two fighters stand 68 px apart)

| fighter | crossing point in cell space |
|---|---|
| kael | x **64**, y **227** |
| executioner | x **60**, y **315** |
| tsubasa | x **57**, y **218** |
| ember | x **68**, y **267** |
| mizu | x **65**, y **227** |
| shin | x **52**, y **213** |


These numbers are **verified, not assumed.** `tools/sprites/check_lock_pairs.py`
composites the stress pairs at their anchors and measures whether the two bodies fit.
This number has moved **twice**, both times because the pre-flight caught bodies
interpenetrating that a per-cell review cannot see: at **26px** kael and the executioner
overlapped by 2.8px (the two widest torsos), and at **30px** shin and the executioner
overlapped by 2.3px — found the moment shin joined the batch. At **34px** all six stress
pairs clear, the tightest by 5.6px. **Adding a fighter means re-running the pre-flight**:
a new body width can invalidate the anchor, and the failure stays invisible until two
finished fighters are composited.

**Put the weapon's binding edge on that point in cells 1–4.** In cell 5 the weapon
drives *past* it; in cell 6 it is knocked *off* it.

Two things that look like errors and are not:

1. **34px is 48% of the executioner's height but 54% of mizu's.** A shorter fighter
   binds higher relative to her own body. World height is what matters.
2. 34px, rather than the ~62%-of-body-height a realistic figure would use, because
   **this cast is chibi** — the head eats the top third, so 62% lands at the chin.
   34px is mid-chest, where these fighters actually hold a weapon.

---

## 8. Per-fighter notes

- **kael** — dual wield, Niten Ichi-ryū. The bind is the **long katana**; the
  wakizashi/tantō stays live in the off hand, ready to counter. Do not let the
  off-hand blade go slack or disappear.
- **executioner** — the nodachi is huge and two-handed. His bind is a **weight**
  bind: he leans into it, he does not muscle it with his arms. Tallest, by a hair.
- **tsubasa** — **reverse grip**, both tantō. Blades are short, so the bind is close
  to his body and his elbows are high. Never flip him to a forward grip.
- **ember** — **iron claws, not a sword.** He catches an edge in the claws rather
  than crossing blades — the trap is the pose. He already has a blade-trap parry;
  this is that read, held. Count his claws against the reference and do not change
  the number.
- **shin** — the **kunai he HOLDS** (his back+Heavy dash), a short steel blade, so the bind
  is very close in. **Not** his fists, which are chainmail and never bind, and **not** a
  thrown kunai. One blade, held.
- **mizu** — **wooden bō**, two hands wide apart on the shaft. A staff bind is a
  *lever*, braced across the body, not an edge-to-edge cross. Shortest fighter, and
  she holds the longest weapon.

---

## 9. ⛔ NEVER

1. Never draw the opponent, their weapon, or any second figure.
2. Never a three-quarter or front view. Never facing left.
3. Never pixel art, and never reduce the palette.
4. Never a ground shadow, drop shadow, spark, flash, blur or speed line.
5. Never change body size between the six cells.
6. Never change a fighter's identity: mask, hood, palette, scarf, weapon count,
   weapon type, eye shape. The eyes are **glowing, featureless, angled** — no pupils,
   no irises, no whites.
7. Never crop or shrink a pose to fit — the frame grows instead.
8. Never a knockdown or a fall in cell 6. Both feet stay on the ground.
9. Never output JPEG or anything lossy. **PNG only.**

---

## 10. Deliverable

**Phase 1: 36 PNGs — 6 cells × 6 sets** — named exactly:

```
kael-katana-lock1.png        … kael-katana-lock6.png
executioner-nodachi-lock1.png … executioner-nodachi-lock6.png
tsubasa-tanto-lock1.png      … tsubasa-tanto-lock6.png
ember-claws-lock1.png        … ember-claws-lock6.png
mizu-bo-lock1.png            … mizu-bo-lock6.png
shin-kunai-lock1.png         … shin-kunai-lock6.png
```

Flat white background, PNG, 2K+ long edge, body size identical within each fighter's
set.

**Start with `kael-katana` only — all six cells — and send those back before drawing
anything else.** It is the reference case: if that set passes, the method is proven and
the rest can run. If it fails we have spent 6 images finding out, not 36.

Then do **`ember-claws` second**, not last. He is the only set with no blade at all — the
claws trap the opponent's edge — so he is the most likely to come back as a sword
fighter, and that is worth finding out early.

---

## 11. Reference art in this pack

Cut straight out of the shipped sheets, so it is exactly what the engine draws today
— not concept art, not an intermediate.

| file | what it is |
|---|---|
| `roster-labelled.png` | **Named, all five binders at true relative height, plus a DO-NOT-DRAW strip.** Start here. |
| `scale-reference.png` | The same heights without the labels. |
| `refs/<f>-card.png` | One fighter: name, weapon, the weapon's failure mode, three poses. |
| `refs/<f>-idle.png` | The identity + height anchor. **This is the seed for lock1.** |

⛔ **Nothing in this repo is exile's canon look — do not draw her from any of it.**
Three sources, all wrong: the portrait refs under
`RECOVERY/select-portrait-handoff/refs/` are pre-repack with baked white manga panels
(74.1% and 32.6% near-white pixels); `web/assets/sprites/exile.png` has 0.0% panels but
carries a **superseded face design** in every cell — a cloth headband with red kanji over
one eye and a single glowing white eye; and her card has been removed from this pack for
that reason. Her canon is the owner's **LOW SHINOBI RUN** reference — bold white hair
streak, bare face, **two red eyes**, red slash markings — which is not in the repo yet.
| `refs/<f>-guard.png` | Closest existing pose to a bind — nearest thing to the target. |
| `refs/<f>-swing.png` | Mid-swing; shows the weapon extended at full reach. |
| `refs/<f>-spec.png` | The idle with the foot line (green), lock height (amber) and crossing point (red crosshair) drawn on the art. |
| `lock-spec.json` | Every number above, machine-readable. |

**One gap, owner to fill:** the binding identity strings, palette hex values and
per-fighter NEVER lists live in the `<Fighter>-Identity-True-Lock.md` files in the
second brain, which is not in this repo. The reference PNGs carry identity visually
and §8 covers the pose-critical points, but paste the identity string in alongside
this doc if you have it to hand.

---

## 12. What is NOT in this batch, and why

---

## 13. What happens to these cells after you send them

So the constraints above make sense:

1. Keyed to transparency (corner floodfill, 42% fuzz) — hence the flat white.
2. **One uniform scale** applied across all six, anchored on lock1 against the idle's
   body height. Not per-cell height matching, which would boil the size between the
   upright bind and the deep lean.
3. Appended to `web/assets/sprites/<f>.png`. Sheets are **append-only** — existing
   cells stay byte-identical, new cells go on the end. First free cell index:
   kael 224, executioner 307, tsubasa 184, ember 218, mizu 180.
4. Gated as a montage strip + a GIF at game framerate to the owner **before** any
   sheet is touched, plus a pair-overlay image proving the weapons actually meet at
   the anchor across the height extremes (executioner × mizu).
