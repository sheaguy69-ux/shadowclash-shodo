# ONI — WHY HIS MOVES "DON'T WORK", and the one page still owed

**2026-08-13 (Fable 5).** Every move below was driven with **real key presses** in
the live game and the drawn cells recorded. Nothing here is read off the source.

---

## THE HEADLINE: his moves DO work. He just never tells you they exist.

| move | input | comes out? | draws its own art? | connects? |
|---|---|---|---|---|
| Light | `F` | ✅ | ✅ `glneu1-6` | ✅ (short reach) |
| Heavy | `G` | ✅ | ✅ `heavy_i1-5` | ✅ 17 dmg |
| Razor whip (special) | `H` | ✅ | ✅ `whip1-6` | ✅ 11 dmg |
| Draw-slash | `Fwd+G` | ✅ | ✅ `kdraw1-6` → `kslash1-6` | ✅ 12 dmg |
| Reversal cut | `Back+G` | ✅ | ✅ `ghback1-5` | ✅ |
| Rising anti-air | `Up+G` | ✅ | ✅ `ghup1-6` | ✅ |
| Low cut | `Down+G` | ✅ | ✅ `ghdown1-5` | ✅ 9 dmg |
| Wire lunge | `Fwd+H` | ✅ | ✅ `gsfwd1-6` | ✅ 20 dmg |
| Rising wire | `Up+H` | ✅ | ✅ `gsup1-5` | ✅ 11 dmg |
| Ground sweep special | `Down+H` | ✅ | ✅ `gsdown1-6` | ✅ 20 dmg |
| Sweep / heel / push kicks | dir + `F` | ✅ | ✅ `ksweep` `kheel` `kpush` | ✅ |

**59 of his 65 art rows are wired.** 7 of 8 attacks connected for damage on the
first try; only the light whiffed, and only because its reach is short at the
spacing I tested.

### So what was actually wrong

**He had no entry in the in-game move list.** Every other fighter has one; his
went out with the retired four-school Oni and was never replaced. Press `L` in
training as anyone else and you get their kit — as Oni you got a blank. There was
no statement of his moveset anywhere in the game, so the only way to find a move
was to guess. **Fixed — his kit is now listed, written from this audit.**

**`V` is his SECOND MODE** (owner spec, Aug 13 2026 — this replaced the retired
four-school wheel, which went out with the old Oni design). Bare `V` toggles it:
neutral light/heavy become the staff (`bostrike`/`bosweep`), the dash goes to the
full shadow-dissolve, and every move of his four boards keeps working inside it.
Stated in his move list. Check: `node tools/check_oni_mode2.mjs`.

---

## ✅ RESOLVED — the bo staff lives in his SECOND MODE

`bostrike1-6` / `bosweep1-6` were the only stranded rows he had — every input slot
was occupied, so they needed a surface, not a redraw. The owner's Aug 13 2026 spec
(*"implement these move sets to oni second mode = v input"*) gave them one: **bare
`V` toggles his second mode, and in it his neutral light/heavy are the staff.**
Directional presses keep drawing his board rows inside the mode, and the mode's
dash plays the full shadow-dissolve (the owner's Aug 11 look for exactly this
mode). Check: `node tools/check_oni_mode2.mjs`.

---

## WHAT NEEDS TO BE DRAWN

**Nothing, for his moves to function.** That is the honest answer to "which do we
need to redraw" — the functional gaps are wiring and documentation, and both are
either fixed or waiting on your ruling above.

The art wishes that remain are quality, not function, and they were already on the
books:

1. **Five ambiguous-claw cells** — `r1_1_crouch_stance`, `r1_5_prone_recover`,
   `r1_7_axe_kick`, `r3_3_claw_thrust1`, `r3_7_rising_slash2` — where talon mass
   reads on BOTH hands. His claw is the right hand only.
2. **Broader shoulders, DRAWN.** He measures 1.69 shoulder-widths-per-head against
   a 1.9–2.5 cast. This can only come from the art now: horizontal stretching is
   outlawed engine-wide (SHEET_V 488 deleted the `thicken` knob and the warp tool
   with it), so the mass has to be in the drawing or it does not exist.

Prompts for both are ready in `docs/GPT-ONI-BROAD-SHOULDERS-PROMPTS.md`.

**The run loop is DONE** (SHEET_V 488). The owner's own `board-RUN-CYCLE-8.png`
is cut and packed as `runb1..8`; the old boiling dash-smear cells are no longer
drawn. Verified live — `STATE.RUN` draws exactly cells 285–292.
