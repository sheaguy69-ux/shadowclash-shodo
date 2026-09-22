# ⛔ CLEAN SLATE — OWNER RULING, Aug 21 2026

> *"I'm doing a due over on everybody looks and frames so I only worry about the new looks.
> I'm doing for everybody right now. **All the old frames before today is invalid.**"*

**Every cell packed before Aug 21 2026 is INVALID.** Not deprecated, not a fallback, not a
reference — invalid. The whole roster is being redrawn: new looks and new frames, all nine
fighters.

## ⛔ This is a DESIGN do-over. The SIZES are not in scope.

Owner, clarifying: *"the size of each character — like the Executioner being the tallest of
the six — is still valid. I'm talking about design wise."*

So the height canon survives the clean slate untouched. It is also **smaller than it looks**:

> **Executioner = TALLEST of the six, *slightly*.** That is the only height law in the Story
> Bible. **Kael is the YOUNGEST** — and that axis is AGE, not height: *"just cause Kael is
> the youngest don't mean he have to be the shortest"* (owner, Aug 21). **Oni** towers and is
> not one of the six.

### The order is already right. The margin is not.

True body height on screen, measured off the shipped sheets (crown = first row with ≥12px of
ink, so a raised blade is not counted as head):

| rank | fighter | screen body |
|---:|---|---:|
| 1 | **executioner** | **69.37px** ✅ correctly first |
| 2 | ember | 68.99px |
| 3 | kael | 68.79px |
| 4 | tsubasa | 67.11px |
| 5 | shin | 66.22px |
| 6 | mizu | 62.00px |

The Executioner leads by **0.38px** — invisible. The canon asks for a readable **~2–3px**.
That is the single height task in this campaign, it is a `scale` decision, and `scale` is
being re-derived from every new idle anyway, so it costs nothing if it is set during the
redraw. **No other fighter's rank is canon; do not reorder the rest.**

## What this deletes

**The "current cell" scaling target is dead.** Until this ruling, new art was being scaled
*down* to fit the geometry of the shipped sheets — Kael ×0.636, the Executioner ×0.651, and
so on. That was correct only while those sheets were staying. They are not. Shrinking new
art to fit cells that are themselves being replaced throws away resolution for nothing.

Any file named `*-PACKREADY.png` was built against that dead target and **must not be
packed**. They are kept only so the arithmetic is auditable.

## What the target is now

**The 4K minimum, and nothing else.** Minimum source body height (crown to sole, weapons
excluded) at which a fighter never upscales at 4K fullscreen:

| mizu | shin | ember · kael · tsubasa | executioner · mokurai · exile | oni |
|---|---|---|---|---|
| 240px | 250px | 260px | 270px | 310px |

Practical rule: **generate at least 300px of body** and every fighter clears with margin.

## What SURVIVES the ruling

The art is invalid. The measurements taken *from* it are not all equally dead:

| still valid | why |
|---|---|
| **Row names, keys, beat counts, engine playback** | that is code, not art — `xparry1..6` is still six cells of parry whoever draws it |
| **Pose beats in `docs/ART-UPGRADE-PACK.md` §4** | they describe what each row must *show* functionally; a run cycle is still a run cycle |
| **The silhouette canon** | a design rule about relative height, independent of any pixels |
| **The scaling laws** | one uniform scale per arc, foot anchoring, head geometry when poses differ |
| **The keying recipe** | fuzz-42 → largest component → purge alpha<16 last |

| now dead | why |
|---|---|
| **`frameW` / `frameH` / `footY` / `scale` per fighter** | they describe cells being rebuilt. `scale` gets re-derived from the new idle: `scale = screenH_target / (footY_new − crown_new)` |
| **Every `*-PACKREADY.png`** | scaled to old cell geometry |
| **Old art as a visual reference** | superseded by the new looks |
| **The append-only law, for this campaign** | a restyle replaces sheets; it does not append to them |

## The one thing that did not change

**Fewer frames per image.** Measured repeatedly across the same generator and the same
characters: 56-frame boards give ~111px of body, 18-frame boards 175–184px, 6-frame boards
205px, and **full-width strips of 6–8 beats at ~2172×724 give 250–460px and pass outright.**
Layout is the whole variable. One technique per strip.
