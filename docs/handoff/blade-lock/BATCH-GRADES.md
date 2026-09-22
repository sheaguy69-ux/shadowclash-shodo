# Batch grades

## ⛔ AND THE CONTACT-HEIGHT GRADE WAS MEASURED AGAINST THE WRONG THING

Second owner correction, also right. Kael's redo was failed for binding at ~80% of body
height instead of the spec's ~48%. But the spec number is one I chose; the ART is what has
to agree with ITSELF. Every set came from the same prompt, so if they all bind at the same
height they meet each other perfectly, and the fix is to move ONE ENGINE CONSTANT rather
than redraw 36 cells.

His point in his words: the generator framed each fighter from that fighter's own point of
view, so judging one strip alone says nothing — **put two together and look.**

`tools/sprites/overlay_lock_pair.py` now does exactly that. Feed it the generator's strips
and it splits each into cells, measures where each fighter's weapon actually reaches
(outermost forward ink, so it finds a blade, a staff or claw tips without being told
which), and composites frame N of one fighter against frame N of another — second one
mirrored, both scaled to equal body height, each positioned so its OWN measured contact
point lands on one shared line. If the weapons meet it looks like a bind; if they miss, the
two contact lines separate and it says by how many px.

It also reports the check no eye can do: **body-height spread across a set**, flagged as
SIZE BOIL over 2%.

So the contact height is now an EMPIRICAL question, not a spec-compliance one:

  python3 tools/sprites/overlay_lock_pair.py strip-*.png

Hand it every strip at once. It reports, per fighter, the mean bind height across cells 1-4,
how much that DRIFTS within the set, and how far it sits from the batch median — then names
the single outlier if there is one, and composites the worst-case pair (highest bind against
lowest) since every other pairing meets if that one does.

Two outcomes, and they lead to opposite actions:

- **all fighters within 4% of the median** — the art is self-consistent. Move
  `LOCK_Y_ONSCREEN` in `make_lock_handoff.py` to the measured median, re-run
  `check_lock_pairs.py`, and **redraw nothing.**
- **one fighter is an outlier** — redraw that one set's cells 1-4 to match the others. Not
  the whole batch.

It also flags DRIFT within a set: if one fighter's own four bind cells disagree with each
other by more than 4%, the contact point is moving between cells, which is the "must not
drift" rule in the prompt.

---

## ⛔ READ THIS BEFORE ACTING ON ANY GRADE BELOW — the grades are scoped to the HELD BIND

Owner's correction, and he is right: **a REDO grade here does NOT mean the frames are bad or
unusable.** Every grade below is measured against the blade LOCK spec, which is the strictest
use these cells have. The same art is fine for other uses, and this file was overstating its
case by not saying so.

What the difference actually is:

| use | duration | does a shared contact point matter? |
|---|---|---|
| the existing CLASH (two swings trading) | ~130ms, 8 frames | **No.** The fighters never hold a pose together, the spark burst covers the contact, and it is gone before the eye resolves where the blades are. Baked-in speed lines read as motion, which is correct at that speed. |
| the HELD BLADE LOCK | 1.15s, ~70 frames | **Yes, completely.** Both fighters are on screen, nearly static, supposedly touching, for long enough to stare at. Each is drawn ALONE and slid together by the engine, so the weapons meet only if both fighters put their weapon on the SAME world line. |

So a set graded REDO for the lock can still be **banked and used for the clash today.** Cells
5 and 6 (win / lose) are usable for the lock as-is too — those extend by design and carry no
shared anchor. Only cells 1-4, the held bind, actually depend on the contact height.

**Nothing here should be re-rolled from scratch on the strength of a REDO grade.** Keep the
art; fix the contact point in cells 1-4.


**Graded:** 2026-08-11 · Claude Code (Opus 5)
**What arrived:** five 6-frame strips from the owner's generator — mizu, ember, tsubasa,
executioner, kael. `shin-kunai` was not in the batch.

Doc 17 requires a grade table with every contact sheet, and **no cell packs without a
grade.** This is that table.

---

## What the batch got RIGHT

- **Facing is correct — all five face LEFT.** This is the big one. The first version of the
  brief said RIGHT, which would have made every cell arrive mirrored and unusable. The
  corrected brief worked.
- **Identity holds.** Palettes match the roster on all five: mizu purple/hooded, ember green
  with the scarf, tsubasa black with red sash and spiked hair, the executioner purple/orange
  and horned, kael black and gold.
- **Medium is right.** Cel illustration, heavy outlines, white background — not pixel art,
  not posterized.
- **Cells 5 and 6 read correctly** — the raised push-through and the knocked-wide recovery
  are both legible as what they are.

---

## The grades

| set | identity | facing | weapon | pose arc | grade |
|---|---|---|---|---|---|
| `mizu-bo` | pass | pass | pass — wooden bō, both hands | thrust, not a braced lever | **REDO 1–4** |
| `ember-claws` | pass | pass | pass — claws, correct count | thrust, not a trap | **REDO 1–4** |
| `tsubasa-tanto` | pass | pass | **FAIL — one knife, forward grip** | thrust | **REJECT** |
| `executioner-nodachi` | pass | pass | **FAIL — one-handed, light katana** | thrust | **REDO** |
| `kael-katana` | pass | pass | **FAIL — off-hand blade missing** | thrust | **REDO 1–4** |

**5/5 need work; 3/5 carry an identity error.** Doc 17's rule is that >30% REDO/REJECT means
proposing a method change rather than shipping the montage — so this batch is not packed,
and the brief is corrected instead (below).

---

## The one fault all five share

**Cells 1–4 are a THRUST, not a BIND.**

Every set drew the weapon held out straight at arm's length with the body upright behind it.
That is a poke. A blade lock is the opposite motion: the fighter is pressing *into*
resistance that pushes back. Nobody in the batch looks like they are straining against
anything.

What the redo needs:

- weight pitched forward **onto the front foot**, not sitting back over the hips
- elbows **bent and compressed**, weapon held **close**, not extended
- rear leg straight and **braced**, rear foot dug in
- shoulders low and driving forward, head up
- cells 3 and 4: the body is **one straight line from the rear heel to the weapon**

Reference feel: tug-of-war, or a rugby scrum. Cells 5 and 6 are the only ones where the arms
extend — and those two came back right.

This is now the first thing the prompt says after the medium rules
(`GPT-PROMPT.txt`, "THIS IS A STRAINING BIND, NOT A THRUST").

---

## The three identity errors, now in the prompt as per-fighter NEVERs

| fighter | what was drawn | what it must be |
|---|---|---|
| tsubasa | **one** knife, **forward** grip, like a dagger thrust | **two** tantō, **both reverse grip**, blade back along the forearm, both involved in the bind |
| executioner | nodachi held **one-handed**, drawn light like a katana | **two hands** on the grip in every cell; long, wide, heavy; he binds with his **weight** |
| kael | off-hand blade **absent** — drawn one-sword | the **short blade in frame and live** in every cell, even though the long one is what is caught |

---

## ⛔ NOT GRADED — and it is the failure most likely to be present

**Body-height consistency across the six cells of each set.** That is what causes size boil
on screen, it cannot be judged by eye, and it needs the actual PNG files — these were graded
from chat images, which are not files on disk.

**Drop the strips anywhere in the repo and this becomes a measurement**, per set: the body
height of all six cells and the exact pixel deltas between them. Doc 17's grade is not
complete without it, and "looks the same size" has been wrong before in this project.

Everything above is what *can* be judged from the images alone.


---

# Batch 2 — kael redo

**Graded:** 2026-08-11. One strip, `kael-katana`, six cells.

## What the corrections FIXED — both prompt changes worked

- **The off-hand blade is back.** Two blades, in frame and live, in all six cells. That was
  the identity error from batch 1 and it is resolved.
- **It is a BIND now, not a thrust.** Elbows bent, blades held close to the body, genuine
  forward lean with a braced rear leg in cells 3 and 4. This was the fault shared by all
  five of batch 1, and the rewritten body-mechanics block corrected it.

Worth recording because it says something about the method: naming the specific mechanics
(weight onto the front foot, elbows compressed, rear leg braced) worked where the adjective
"straining" had not.

## The grade

| set | identity | facing | weapon | pose | contact height | grade |
|---|---|---|---|---|---|---|
| `kael-katana` v2 | pass | pass | **pass — both blades** | pass — braced, elbows bent | **FAIL** | **REDO 1–4** |

## Why it still fails — the contact point is at head height

The blades cross at roughly **80% of his body height**, tips angled upward beside his head.
The shared anchor is **34px above the feet on a ~70px fighter — just under half height,
mid-chest**.

This matters more than it looks. Every fighter binds on the SAME world line: mizu is the
shortest in the roster and holds the longest weapon, and she binds at that same mid-chest
height. Kael binding at head height and mizu binding at chest height means **their weapons
never touch on screen.**

And no tool can catch it. `check_lock_pairs.py` verifies the anchor GEOMETRY is consistent
between fighters; it cannot know that the drawn blade sits somewhere other than the anchor.
Within one fighter's six cells the art looks perfectly self-consistent. It would only have
surfaced once two finished sets were composited — after all 36 images were drawn.

## Two smaller notes

- **Speed lines in cell 5 and shake strokes in cell 6 must come out.** The engine draws its
  own motion FX and composites these cells directly, so baked-in strokes sit frozen on a
  held frame and read as artifacts.
- Cells 5 and 6 are otherwise correct — those two extend by design.

## Now in the prompt

`GPT-PROMPT.txt` carries the height as a MEASUREMENT rather than a description — "just under
half the figure's total body height, about 480px up on a 1000px figure, level and roughly
horizontal" — plus the explicit NOT-beside-the-head note, a no-drift rule across cells 1-4,
and a ban on baked-in motion FX.

## Still not graded

**Body-height consistency across the six cells** — same as batch 1. Needs the PNG files;
cannot be judged from chat images. It is the failure most likely to be silently present.


---

# Batch 3 — kael, ember, executioner

**Graded:** 2026-08-12. Three strips (kael's was sent three times; graded once).

⛔ **VISUAL READ, NOT A MEASUREMENT.** These were graded from chat images, so body-height
consistency and exact contact height are NOT verified — the two things that most need numbers.
The percentages below are eyeballed, and the whole reason `overlay_lock_pair.py` exists is that
eyes are unreliable about exactly this. Save the strips as files and the grade becomes exact.

## The grades

| set | weapon | facing | bind pose | contact height | grade |
|---|---|---|---|---|---|
| `kael-katana` v3 | **pass — two blades** | pass | **pass** | high, ~70–80% | **REDO 1–4**, height only |
| `ember-claws` v2 | pass | pass | pass — braced, low | **pass, ~50%** | **REDO 1–5**, needs variation |
| `executioner-nodachi` v2 | **FAIL — one-handed** | pass | fail — thrust | pass | **REDO** |

## What landed from the previous corrections

- **kael has both blades** in all six cells. That identity error is fixed.
- **The bind reads as a bind** on kael and ember — elbows bent, weapon held close, forward lean
  deepening through 3–4, braced rear leg. The body-mechanics rewrite worked.
- **No baked-in motion FX.** The speed lines and shake strokes from kael v2 are gone.
- **Ember's contact height is right** — claws level at roughly mid-chest, which is what the
  measurement-based height instruction asked for.

## What still needs work, per set

**kael** — the blades still cross around shoulder/head height with tips angled up. Everything
else about the set is right, so this is cells 1–4 for height alone, nothing more.

**ember** — the opposite problem to kael's, and it is a real one: **cells 1–5 barely differ.**
Catch, settle and both strain frames read as nearly the same drawing, so the loop will look
frozen rather than straining. Cell 5 also does not read as a WIN — it needs to drive forward
and open the chest, not hold the same brace. The spec's beats have to be *distinguishable*, not
merely present.

**executioner** — the nodachi is **one-handed with the arm extended straight**, which is both
the batch-1 identity error repeating and the thrust problem. His height is fine. Both hands on
the grip, elbows in, weight forward: he binds by leaning his mass into it, not by reaching.

## ⛔ THE USEFUL SIGNAL IN THIS BATCH

**Ember's contact height is right while kael's is high.** That means the mid-chest instruction
*can* land — it is not too vague to follow. So the fix is kael's set alone, not another rewrite
of the spec. Had all three come back high, the instruction would have been the problem.

This is the kind of thing a per-set grade shows and a per-cell grade cannot.
