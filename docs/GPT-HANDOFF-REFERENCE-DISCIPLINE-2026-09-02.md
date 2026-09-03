# Handoff to GPT / Codex — why two approved boards were thrown out, and what changes

Written 2026-09-02 by Fable 5 (Claude Code) against SHODO-EDITION at `SHEET_V 694`.
Audience: the image-generation lane. Read section 1 before generating anything else.

---

## 1. What happened

Two delivered packages were **rejected by Anthony on 2026-09-02**:

- `art/production/handoff/SHODO-MIZU-HANBO-KAESHI-V2-REJECTED-DO-NOT-INTEGRATE-2026-09-02/`
- `art/production/handoff/SHODO-TSUBASA-SAKATE-BACKHAND-RAKE-V2-REJECTED-DO-NOT-INTEGRATE-2026-09-02/`

Both carry a `REJECTED-BY-OWNER.md`:

> Anthony rejected this handoff on 2026-09-02 because an old animation/choreography source
> was used as a generation reference. Do not pack, wire, copy, or hand these frames forward.

Both were originally named `...-APPROVED-READY-...`, with the rejection visible only in a
file inside them. They have been **renamed to `...-REJECTED-DO-NOT-INTEGRATE-...`** so the
name matches the ruling — anyone listing the directory now sees the status before opening
anything. Their contents are untouched.

⛔ **A folder name is not a status.** Check for `REJECTED-BY-OWNER.md` before treating any
package as usable, whatever it is called.

### The specific cause

From the rejected package's own `PROMPT.md`:

> References: current `mizu-shodo-exact-style-idle-8f-v1-codex-review` frame 1 for identity,
> **and the recovered old `hb_catch` row for choreography only.** The old one-eye face was
> not identity truth.

The old row was fed in as a movement reference. That is the entire reason for the rejection.

---

## 2. Why that is a real problem, not a technicality

**It reproduces the poses of art that was already discarded.** Mizu has **zero** `hb_*`
cells packed on her sheet — verified against `web/assets/sprites/mizu.json`. That
"recovered old `hb_catch` row" is not live art; it is a lineage that never shipped. Taking
choreography from it means the new board inherits the movement of the exact thing it was
meant to replace: new paint, dead poses.

**The prompt distrusted the source and then relied on it anyway.** The same file says *"The
old one-eye face was not identity truth."* If a reference is known to be wrong about who
the character is, nothing establishes that it is right about how the character moves. It
was demoted for identity and silently promoted for motion.

**Contamination is invisible once packed.** After a row lands in the atlas there is no way
to tell which beats came from the dead lineage. This tree has paid for that repeatedly —
the superseded purple Oni redesign, Shin's outgoing olive second form, the pre-Aug-20
frames purged in August. Contaminated art does not announce itself; it sits in the sheet
until someone measures a row, cannot explain the result, and has to re-derive the history.

**It also wastes the owner's review.** He approves against what he is shown. If the
provenance is contaminated, his approval was given on a false premise, which is why the
rejection came after an approval rather than instead of one.

---

## 3. The standard that replaces it

The **fresh trio** built the same three moves the correct way. From its `PROVENANCE.md`:

> Built with the built-in image generator. Each fighter used exactly one approved idle image
> as an identity/style reference. **No old move board, recovered animation strip, packed
> sprite cell, or rejected candidate was supplied to generation.**

That is the rule going forward, stated as a rule:

1. **Identity reference: one approved idle image. Nothing else.**
2. **Choreography comes from the written prompt, not from a picture.** Describe the beats in
   words. If the motion needs a picture to be understood, the prompt is not finished.
3. **Never supply as a reference:** an old move board, a recovered animation strip, a packed
   sprite cell, a rejected candidate, or anything from `RECOVERY/`.
4. **Declare every reference in `PROVENANCE.md` with its path and SHA-256.** The rejection
   above was only catchable because the prompt file was honest about its inputs. Keep that.
5. If a move genuinely cannot be drawn without seeing prior motion, **say so and stop** —
   that is an owner decision, not a generation shortcut.

---

## 4. Where that leaves the three moves

The fresh boards were reviewed, cut and keyed. They are in
`art/production/handoff/SHODO-TRIO-FRESH-MOVE-ART-REVIEW-2026-09-02/`:

| Board | Grade | State |
|---|---|---|
| Mizu — Hanbo Kaeshi (6 beats) | KEEP | cut, keyed, registered |
| Shin — Kage-Nui Poke (6 beats) | KEEP | cut, keyed, registered |
| Tsubasa — Sakate Backhand Rake (6 beats) | KEEP | cut, keyed, registered |

All three passed: identity against each fighter's live idle, weapon discipline, palette,
pose readability, runtime keyer a no-op on all 18, no fragments, no canvas-edge ink.
Extracted frames and a `registration.json` per fighter are in `extracted/`.

**They are not packed, and must not be.** All three are second-mode moves and the engine
gates second mode off at seven call sites (`FIRST_FORM_ONLY = true`, `web/index.html:1120`).
Mizu has 0 of the 10 `hb_*` rows packed; Shin and Tsubasa 0 of 19 `f2_*` each. Landing one
row into a mode that cannot be entered produces orphans on arrival. That is an owner
decision and it is open.

**No redraw is requested on these three.** Two findings I raised earlier were withdrawn on
measurement and are recorded here so they are not re-litigated:

- A "floating kunai with no hand" on Shin's DRIVE and a "floating stub" on Mizu's PIVOT were
  **not real** — they were artifacts of cutting the board at caption midpoints, which slices
  a neighbour's forward-thrust weapon. Measured whole-board, Shin and Tsubasa have **zero**
  detached components; Mizu had exactly one 45px speck, now removed.
- Mizu's VEIL and GUARD failing a binary-silhouette test was **withdrawn**. At her true
  on-screen height of 62px the tan hanbō reads at Weber contrast 2.20 and 2.63 against the
  robe, where ~0.25 is the threshold. The silhouette is blobbier than her shipped cells
  (0.65 fill vs her live max 0.53), but it does not cost readability.

---

## 5. One technical change that would save real work

The review boards arrive as **RGB with a baked checkerboard**, and the ready packages arrive
as true alpha. The RGB review boards cost a full day of extraction work this session, for a
reason worth knowing:

**Pure-neutral white art is indistinguishable from page white.** Mizu's and Tsubasa's eyes
measure core luminance 249.0-251.4 with channel spread 0.03-0.30. The page measures 251.4.
Every separator that was tried failed: colour, neutrality, flatness, ring brightness, and
re-flooding at a looser threshold. The house keyer deleted **both eyes from every beat**
before this was caught, and a later rule deleted **the steel inside Tsubasa's kunai blades**.

Two asks, in order of preference:

1. **Deliver review boards with genuine alpha**, the way the ready packages already do. Then
   none of the above can happen — the alpha states what is art and no inference is needed.
2. If a baked background is unavoidable, **do not use a neutral background**. Any saturated
   colour the art does not contain (a magenta or a green) makes the separation exact.

Also useful: the boards are cut on caption-centre pitch, so **keep the gutters generous
enough that no beat's weapon crosses into a neighbour's column**. Two of the false findings
above came from a thrust kunai overlapping the next figure's band.

---

## 6. What is actually still owed

| Item | State |
|---|---|
| Executioner `xrise`/`xkiriage` beat 5 | **Approved and ready**, package `SHODO-EXECUTIONER-XRISE-BEAT5-V2-APPROVED-READY-2026-09-02`, awaiting integration. **No GPT work.** |
| Shin four-beat getup | Candidate `shin-getup-4f-one-scale-v1-RGB-REVIEW.png` delivered, **awaiting Anthony's approval**. No regeneration unless he rejects it. |
| Mizu / Shin / Tsubasa second-mode moves | Art done. Blocked on the `FIRST_FORM_ONLY` engine decision. |

Nothing else is requested from the generation lane right now. If that changes, the request
will come as a brief that states the TARGET, not the current defect.

---

## 7. House rules that keep applying

- ONE row per image, left-facing, transparent background, captions BELOW the row.
- One body size for the whole row — heads, hands and weapons the same beat to beat. A tuck
  keeps the same head; do not shrink tucked beats.
- No motion blur, no speed lines, no ground shadow, no background, no border.
- Nothing ends in a straight cut. An effect leaving the figure fades to nothing inside the
  frame; a smear touching the canvas edge is a reject.
- Match the fighter's existing design exactly — these are replacement beats inside a live
  animation, not a redesign. **Count the weapon against the fighter's own shipped cells, not
  against a doc.** Ember carries FOUR claw blades per hand; a handoff README said three.
