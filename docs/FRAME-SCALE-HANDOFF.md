# FRAME-SCALE AUDIT HANDOFF — for GPT (multimodal, watches the animations in motion)

> **Job:** watch the fighter animations IN MOTION and report every frame whose SCALE is
> wrong — bigger or smaller than the fighter's own idle, warped, or "boiling" (the body
> visibly popping size between beats). You report; the coding agent fixes.

## 1. The rules (canon — do not override)

**Silhouette law (Story Bible):** the Executioner is the OLDEST and TALLEST of the six —
*by an inch, not a boss*. He must read tallest **in every state**, and it must never
happen that another fighter's frame is taller or bigger than him in a comparable state.
Oni is the one who towers (he is allowed to exceed everyone).

**Measured idle heights (on-screen, canvas px):**

| fighter | drawn idle height |
|---|---|
| Executioner | 72.5px (tallest) |
| Kael | 70.0px |
| Tsubasa | 69.6px |
| Ember | 69.3px |
| Shin | 66.6px |
| Mizu | 62.4px (shortest) |

A fighter's **body** should stay at their own idle height across all their frames; only
the LIMBS / WEAPON extend in an attack, and only the POSE compacts in a crouch/roll/jump
tuck. The head (the scale invariant) never changes size.

## 2. The files

Sprites live in web/assets/sprites/<fighter>.png (a horizontal strip of cells) with a
manifest web/assets/sprites/<fighter>.json that maps frame NAMES to CELL indices and
holds frameW, frameH, footY, and scale. The six originals:

- executioner.png / .json — one slim katana, horned mask (TALLEST)
- kael.png / .json — one SHORT + one LONG sword (youngest)
- tsubasa.png / .json — two small tantō, no hood
- ember.png / .json — tekko-kagi claws, both hands
- shin.png / .json — hand-to-hand + wire, no blade
- mizu.png / .json — long bo staff (shortest)

The game is served at http://localhost:9100 (Ctrl/Cmd+Shift+R to force-refresh).
You can open any fighter's PNG and slice it by frameW × frameH cells to inspect
individual frames, and you can watch the game live to see them in motion.

## 3. What to check (in motion)

For **each fighter**, watch these and flag any frame that breaks scale:

1. **idle → run → walk** — the body must stay one size; watch for a beat that "pops."
2. **block / guard** — must be ~the idle height (a guard is standing, not crouched). A
   guard that visibly shrinks the fighter is wrong.
3. **hurt / hit reaction** — the body may recoil but must not shrink or grow.
4. **crouch / kneel** — must be a genuine crouch (~0.6–0.8× idle). A "crouch" that is as
   tall as standing is wrong.
5. **every attack (light/heavy/special, grounded + air)** — the WIND-UP and RECOVER beats
   should be ~idle body size; only the IMPACT beat extends (limbs/weapon). If the whole
   BODY (head-to-feet) grows on a wind-up or recover beat, that's a scale bug.
6. **throw, jump, roll** — the body compacts (jump tuck, roll) or stays neutral; a jump or
   roll beat that is *bigger* than idle is wrong.
7. **CROSS-CHECK vs the Executioner** — whenever two fighters are on screen, confirm the
   Executioner is never the smaller one in a comparable state (idle vs idle, block vs
   block, hurt vs hurt, run vs run). Flag any moment he isn't.

## 4. Known issues already measured (start here — confirm or correct)

The coding agent measured these and wants a second pair of eyes before touching them:

| fighter | frame | measured | suspected problem |
|---|---|---|---|
| Executioner | block | 0.81× idle (58.8px) | undersized — he shrinks when guarding, drops below everyone |
| Executioner | hurt | 0.92× idle | undersized — Ember/Kael hurt read taller than him |
| Mizu | block | 1.39× idle (86.8px) | her bo staff is held vertical — confirm her BODY is still 62.4px |
| Kael | block | 0.79× idle (55.5px) | undersized guard |
| Kael | kneel | 1.08× idle (75.6px) | taller than standing — looks like it is NOT a kneel |
| Ember | ajump5 | 1.35× idle | a jump beat 35% bigger — likely the strongest bug |
| Ember | ehook2 / espec5 | ~1.13–1.16× | maybe legit wide finish, confirm |
| Tsubasa | sdown4 / hup3 | ~1.14–1.18× | maybe legit, confirm |
| Shin | f2_heavy3_4/5 | ~1.12–1.15× | Form-2 heavy, confirm |
| Executioner | xsky6 | ~1.10× | sky-cleave finish, confirm |

## 5. What to output (the SPECS)

Report as a table. One row per broken frame. Use this exact format so the coding agent
can act on it directly:

fighter | frame name(s) | cell index (from the .json) | state | problem (bigger / smaller / warped / boil) | rough % off | fix suggestion (rescale to X% or redraw)

Also state, for any frame you flag: **which neighboring frames in the same cycle are the
correct size** (so the fix can anchor on them).

Do NOT suggest deleting art. The sheet is append-only — fixes are rescale-in-place or
"needs redraw", never "remove the cell".

## 6. Hard do-nots

- Do not flag a CROUCH / ROLL / JUMP-TUCK for being smaller — that's the pose.
- Do not flag an ATTACK IMPACT for being bigger — limbs/weapon extend on the hit frame.
- The thing to flag is the BODY (head-to-feet) changing size when it shouldn't — a guard
  that shrinks, a run beat that pops, a wind-up that balloons, a jump that's bigger than
  standing.
- The Executioner is the ruler: if he is ever not the tallest on screen, flag it.
