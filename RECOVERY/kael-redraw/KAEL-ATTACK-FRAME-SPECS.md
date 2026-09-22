# KAEL — ATTACK FRAME SPECS FOR THE REDRAW

**Fighter:** Kael, roster id 5 · tree `/Users/anthonyguy/shadowclash-fable-5`
**Date:** Aug 21 2026 · **Status:** clean slate — every cell dated before Aug 21 2026 is INVALID and is not a style reference for anything below.

---

## THE TOTAL

| | |
|---|---|
| **Attack slots specced below** | **17** |
| **Rows in his actual attack kit** | **21** — see the correction under this table |
| **Beats specced** | **99** (16 rows × 6 beats, + `kpush` at 3) |
| **Scope** | **His WHOLE attack kit.** Not the gaps. Every grounded light, every heavy, every special, and every airborne row is being redrawn from scratch. |

> **⛔ CORRECTION — the aerial family is FIVE rows, not three.** This document specced A1/A2/A3
> (neutral air light, heavy, special) and stopped there. It missed **`afwd` and `aback`**, which
> are live engine rows carrying six cells each and drawn for air forward/back light, and
> **`aup` and `adown`**, which the engine gained on Aug 21. All four are now delivered and
> archived in `rows/`. Nothing below is wrong; it is incomplete, and the count of 17 is the
> number of slots THIS FILE covers, not the size of his kit.

Sheet geometry, measured from `web/assets/sprites/kael.json`: **frameW 300 · frameH 320 · footY 312 · render scale 0.4023**, one 217-cell strip.

### The Japanese names — owner ruling, Aug 21 2026

Eleven are **settled** — they arrived captioned on delivered boards: `L4 Ashi-barai`, the five
Special rows (`Kaiten-giri`, `Fumikomi-giri`, `Jūmonji-dome`, `Kiriage`, `Gyaku-kesa`) and the
whole Heavy tier (`Jūmonji-giri`, `Kuruma-giri`, `Gedan-barai`, `Ukenagashi`, `Hasami-giri`).
Six remain **proposals** and are marked as such — L1, L2, L3 and the three air rows; they
become canon the same way, by appearing on a board.

The scheme is Niten Ichi-ryū, which is the right school for a short-and-long swordsman and
the one his own guard boards already use — the five Nitō Seihō kamae (chūdan, jōdan, gedan,
hidari-waki, migi-waki) are Musashi's five.

Which are established budō terms and which are correctly-formed constructions is recorded
here so nobody later cites a construction as historical: **established** — ashi-barai,
mae-geri, ushiro-geri, kiri-kaeshi, fumikomi, kiriage, gyaku-kesa, gedan-barai, ukenagashi,
jūmonji. **Constructed** — kaiten-giri, kuruma-giri, hasami-giri, jūmonji-dome, and the
kūchū-/tobi- air compounds.

### Canon block — applies to all 99 beats

- **ONE LONG KATANA + ONE SHORT WAKIZASHI.** Never two long, never two near-equal blades. The measured ratio on the first clean-slate asset that passed is short : long **0.38–0.49** — the length difference must be obvious at a glance in *every* cell. The near-equal blades on the old air-special rows are one of the defects this redraw exists to kill.
- **The SHORT blade parries. The LONG blade counters.** That split is his Niten Ichi-ryū style, not a per-move choice, and it holds across `klowp`, `khigh` and `xparry`.
- **Black and GOLD.** Black tunic, gold hood-wrap, gold scarf/sash, dark cape/mantle, glowing gold eyes, hood up. **Purple is forbidden.**
- **He is the YOUNGEST of the six** — light-framed, quick, upright. **That axis is AGE, not
  height** (owner, Aug 21 2026: *"just cause Kael is the youngest don't mean he have to be the
  shortest"*). No height rank of his is canon. The Story Bible states one height fact only —
  the Executioner is tallest of the six, slightly — and records Kael sitting second without
  objection. Draw him at his normal build; his `scale` is a packing decision, not a pose one.
- **Every cell is authored FACING LEFT.** The engine mirrors for the right-facing fighter (`ctx.scale(-p.facing,1)`), so an asymmetric daishō legitimately swaps sides on turn. That is how the whole roster ships — **do not compensate for it in the art.**
- **Describe the ACTION.** Nothing below is a style note.

---

## THIN-ROW TRIAGE — read this before commissioning

These five have the least information to reconstruct a move from. The old art is not being kept either way, but on a thin row there is nothing on disk that even tells you *what the move looks like*, so the owner may need to make a call rather than approve a reconstruction.

| Row | Slot | Cells on disk today | Beats wanted | What the old art actually tells you | Owner call needed? |
|---|---|---|---|---|---|
| **`ksweep`** | Down + Light | **1** (bare `ksweep` key) | 6 | **Nothing about the move.** Cell 93 is a near-frontal deep squat, both hands empty, both swords sheathed, no leg extended anywhere. It is a generic crouch standing in for a leg reap. Only the hip height is reusable. | **YES** — the reap is reconstructed from the hitbox (52 × 16, floor-anchored) alone. |
| **`kheel`** | Back + Light | **1** (bare `kheel` key) | 6 | **The pose itself is honest.** Cell 94 genuinely depicts a rear heel kick at chest height, standing leg bent, foot flexed sole-out — roughly beat 3–4 of six. Everything before and after it is simply missing. | No — one good frame, five to invent around it. |
| **`kpush`** | Fwd + Light | **4 keys measured** (`kpush1/2/3` + a legacy bare `kpush`); **only 3 are ever drawn** — the router hardcodes `[F.kpush1, F.kpush2, F.kpush3]` | **3** | **Nothing.** All three are static armed sword-brandish portraits. No leg leaves the ground in any of them. The engine has been playing a 300-pushback *unarmed* shove over an armed standing pose. | **YES** — the action here comes from the ENGINE, not the art. Also carries a facing defect and a scale defect (below). |
| **`sneu`** | air Special (neutral) | **0 — the row does not exist** | 6 | Nothing. A neutral air Special currently borrows `kxcut1..6`, his air heavy. The engine file admits it in a `ponytail:` note. | **YES** — pure reconstruction from mechanics. `'neutral': 'sneu'` is *already in the draw map*, so packing it costs ZERO engine work. |
| **`aneu`** | air Light (neutral) | **0 dedicated** — falls through to the shared `air1..3` | 6 | Only as action: chamber → cross → follow-through. The shared 3-cell set is not his. | No — the action reads. The `aneu` branch is **ungated by `spec.id`**, so packing `aneu1..6` costs ZERO engine work. |

**Rows that already carry six drawn cells** (redraw replaces them beat-for-beat, timing unchanged): `kdual`, `kcross`, `kcyc`, `klowp`, `khigh`, `kscis`, `kxcut`, `kspin`, `ktrav`, `xparry`, `kfang`, `krise`.

**⛔ SIX IS A HARD NUMBER on every row that has an `ANIM_TRACKS` entry.** `attackCellIndex` only applies a track when `track.length === count`. A 5- or 7-cell delivery silently falls back to generic even exposure and puts the wrong cell under the hitbox — including the contact frame. `kpush` is the opposite case: its picker hardcodes three, so cells 4–6 would never be read.

---

# LIGHT TIER

## L1 · NEUTRAL Light — "DUAL SLASH COMBO"

**Kiri-kaeshi** 切り返し  *(proposed — not yet on a delivered board)*
**Row `kdual` · 6 cells today → 6 beats · grounded only**

**Engine.** `p.spec.id === 5 && p.isGrounded && F.kdual1` → `kdual1..6` on track `dual` = `[0, .12, .28, .46, .66, .86]` of a 180 ms window → 0–21.6 / 21.6–50.4 / 50.4–82.8 / 82.8–118.8 / 118.8–154.8 / 154.8–180 ms. Kael's stats are all 6, so every scalar is ×1.00.
**ONE hitbox per press:** 40 × 30, 8 damage, active 0.05 s, delay 57.6 ms, pushback 60 → **live 57.6 → 107.6 ms = drawn cells 3 and 4.** Recovery 0.25 s. Root motion `vx = facing * 110` — a real short step forward. Sets chainComboTier 1; cancels into Heavy/Special on connect. Stagger 15. 0 chakra. No launch, no invuln, no armor, no trip, no low.
**Multi-tap string:** a second/third tap inside 0.55 s **replays this identical row** with scaled numbers (beat 2: ×1.15 width/damage; beat 3: ×1.30 width, 12 damage, `vx = facing * 200`). Same art all three beats.
The engine spawns its own blade crescent at 45 ms and holds `kdual6` ~110 ms into recovery.

**Blades.** LONG katana = **RIGHT** hand (far/upstage arm) — it does the whole cut. SHORT wakizashi = **LEFT** hand (near/downstage arm) — hip guard, then it delivers the second thrust. Both in frame in all six cells.

**Beats.**
1. **WIND-UP, COILED.** Side-on to the opponent (opponent off to his LEFT), feet a little wider than his shoulders, weight sunk back over the rear foot, both knees bent. The LONG katana in his right hand chambered high beside his right ear, hilt at jaw height, blade angled forward-and-down about 45° over his shoulder. The SHORT wakizashi in his left hand out low across the front of his hips, point levelled at the opponent — the hand that holds the door shut. Hood up, gold eyes level. Nothing has crossed his own front line yet. *(On screen only ~22 ms — this beat has to read as a coil in silhouette alone.)*
2. **WEIGHT TRANSFER.** Front (left) foot plants a short step toward the opponent and the hips open square onto him; back leg straightening behind. The long blade has left the ear and is dropping — hilt leading, tip still high and behind the head, the arm uncoiling from the elbow. The short blade rotates edge-outward and pulls back tight to the near hip to clear the lane the long blade is about to swing through. Cloak hem and scarf lift back from the step. Still no contact.
3. **CONTACT — THE LONG CUT LANDS.** Right arm at full extension, shoulder driven through, the katana swept down-and-forward through the space directly in front of his chest so the blade is horizontal-to-shallow-diagonal at the opponent's chest height and clearly PAST his own front line. Front knee bent hard over the planted front foot, back leg straight and trailing, torso pitched forward over the front thigh. Short blade still tucked at the near hip, point forward. Maximum reach, maximum commitment, blade fully out of the body silhouette.
4. **SECOND CONTACT — THE BLADES PASS.** The long katana continues through the cut line and exits low: tip dropped to about knee height, right arm across and beyond the body. In the SAME instant the short wakizashi punches straight out from the near hip at chest height, point-first, arm extending toward the same target line — the two blades crossing in opposite directions in front of him, long one leaving low, short one arriving high. Torso rotated further open, weight still fully on the front foot, both feet planted.
5. **RECOVERY PULL.** The long blade whipped back up and inward toward his centre line, tip rising, elbow folding to the ribs. The short blade stays forward and high, crossing IN FRONT of the long blade's return path so the two make a shallow X in front of the chest. Weight beginning to shift back off the front foot, front knee straightening, hips closing back to side-on, shoulders squaring down.
6. **SETTLED GUARD — HELD.** Feet back to the even wide stance he started in, both knees softly bent, body side-on to the opponent, head level. LONG katana in the right hand held out forward and slightly downward, about 30° below horizontal, arm relaxed. SHORT wakizashi in the left hand across the chest, edge out, point forward. Must be stable enough to sit still for a tenth of a second AND match beat 1's silhouette closely enough that a second and third tap read as one continuous string, not three restarts.

**Redraw constraints.**
- **ONE PRESS = ONE HIT.** Six beats, a single hitbox. Do not draw three separate cuts trying to represent the three-tap string — the string replays this identical row.
- Cells 1+2 together get 50 ms — they are a **coil, not a story**. Cells 5+6 are pure recovery; cell 6 is held ~110 ms past the animation.
- The approved action (read off the old row as action only) is *high chamber → forward cut → follow-through → re-chamber → both blades out → return to guard*. That is preserved. What changed is the timing: the old row put the both-blades-out money frame on cell 5 (119–155 ms), **11 ms after the box had already died.**

---

## L2 · FWD + Light — "PUSH KICK / TEEP"

**Mae-geri** 前蹴り  *(proposed — not yet on a delivered board)*
**Row `kpush` · 3 drawn cells (4 keys on disk) → 3 beats · grounded only**

**Engine.** He has no `glfwd` row, so Fwd+Light routes to `executeKick('push')`. **Gate:** grounded, `chainComboTier === 0`, `recoveryTimer <= 0` — it only comes out fresh, never as a continuation of the light string.
`KICK_MS` 140 ms authored, **`vx = 0` — HE DOES NOT TRAVEL.** He plants and shoves; the opponent is what moves. Hitbox 46 × 28, 4 damage, active 0.12 s, **pushback 300** (five times the neutral light's 60 — the whole point) with a `wallsplat` rider, delay 44.8 ms. `floorCommitment` stretches the animation to ~165 ms, so with three cells and no track each holds ~55 ms: 0–55 / 55–110 / 110–165. **Box live 44.8 → 164.8 ms** — the last sliver of cell 1, all of cell 2, all of cell 3. Recovery 0.32 s; `kpush3` held ~144 ms into it.
Wallsplat: victim within 50 px of a wall gets +0.3 s stun and a screen shake of 9. `puntLogs`: a kawarimi log within ~85 px in front is booted into a 430 px/s projectile that detonates on whoever it slides into, including its owner.
**UNARMED, EXPLICITLY** — no blade crescent. Stagger 5. `canClash` false (tier `KICK`), so it cannot trade with steel. 0 chakra, fires while winded, does not advance the chain. No launch, no invuln, no armor, no low.

**Blades.** **NEITHER BLADE TOUCHES ANYTHING.** LONG katana = RIGHT hand, swept back and down behind the rear hip through beats 1–2, returning to a low forward guard in beat 3. SHORT wakizashi = LEFT hand, held vertical and flat against the chest through beats 1–2, dropped toward the hip in beat 3. Both visible in all three cells; he never sheathes and never drops one.

**Beats.**
1. **PLANT AND CHAMBER.** Standing side-on to the opponent (opponent off to his LEFT). The REAR (right) foot flat, planted and taking every ounce of weight — it never leaves its spot for the whole move. The FRONT (left) knee snaps up high, thigh horizontal, shin folded under it, foot cocked with the toes pulled back and the flat of the sole already turned toward the opponent. Torso leaned back over the standing leg to counterweight the raised knee, shoulders open. BOTH BLADES SWEPT OUT OF THE WAY AND THEY STAY THERE: long katana swung back and down behind the rear hip, arm extended behind him, edge trailing away from his own leg; short wakizashi raised vertical against the chest, flat side toward the opponent. Hood up, gold eyes fixed forward.
2. **FULL EXTENSION — THE SHOVE.** The front leg drives straight out toward the opponent, knee locked, and the whole flat of the sole slams forward at the opponent's stomach — his own hip height, a shove INTO the body, not a snap to the head. Hips thrust forward behind the foot so the force reads as coming from the pelvis, not the knee; standing leg straight and braced, back arched, both shoulders pulled back and away. The planted foot has not moved a pixel. Both blades still clear and well behind the line of the kick. **NOTHING METAL MAY BE IN FRONT OF HIM IN THIS FRAME.**
3. **RETRACT AND RE-GUARD — HELD.** The kicking leg folds back in fast: knee still up but the shin now hanging, foot dropping toward the floor, weight rocking back over the planted rear foot, torso coming upright. The long katana swings forward out of its trailing position into a low forward guard, tip toward the opponent and below horizontal; the short blade drops off the chest toward the near hip, point forward. A settled, balanced stance he can stand in for a seventh of a second without looking frozen mid-move — it is on screen well past the end of the animation.

**Redraw constraints.**
- **Three beats, not six.** The picker hardcodes `[F.kpush1, F.kpush2, F.kpush3]`; cells 4–6 would never be read. Three is also right for the window (55 ms each reads; six would be 27 ms each and blur). Six would need a one-line engine change plus an `ANIM_TRACKS` entry — **engine work, not commissioned here.**
- **Facing defect in the old row, do not repeat:** `kpush1`/`kpush3` are near-FRONT-facing and `kpush2` is three-quarter facing RIGHT, while the whole rest of the sheet is left-facing. Draw all three in LEFT-facing side profile like `kdual`.
- **Scale defect in the old row:** `kpush` cells measure 164 px of body bbox against `kdual`'s ~144 px — the row is oversized against the sheet. Draw at the `kdual` body height, feet on footY 312.
- The box goes live *inside cell 1*, so cell 1 cannot be an idle with a raised knee — the chamber must already read as loaded and about to fire.

---

## L3 · BACK + Light — "HEEL TURN"

**Ushiro-geri** 後ろ蹴り  *(proposed — not yet on a delivered board)*
**Row `kheel` · 1 cell today → 6 beats · grounded only · ⛔ THIN**

**Engine.** Fires from ATTACK_LIGHT when grounded, `chainComboTier === 0`, `recoveryTimer <= 0`, direction held AWAY from the opponent. Kael has no `glback*` row (measured: zero `gl*` keys), so it always falls to `executeKick('heel')`.
**`vx = 0` — ZERO travel.** 140 ms animation, startup 44.8 ms (~2.7 frames at 60 fps — his fastest telegraph). ONE hitbox 44 × 30, 6 damage, active 0.10 s, pushback 60, flagged `behind: true`. Recovery **0.24 s — his fastest kick recovery.**
**Geometry:** `behind` puts the box behind him; `oy` spans y 9–39 of a 48-tall body — **shoulder down to hip, it lands CHEST-HIGH.** Excluded from the +8 corner reach-back, so a true 44 px ≈ 1.5 body-widths behind him.
No launch, no trip, no wallsplat, **no invuln and no armor** — nothing in this move is safe. 0 chakra, no winded gate. Stagger 5, the lowest in the game. `canClash` false, `hasuji` false — no steel, no clash, no spark. On hit: victim knockback 160, hit mark `H05`.
**Six beats once wired:** no `ANIM_TRACKS` entry, so `ATTACK_EXPOSURES_6 = [0, .17, .32, .46, .60, .79]` × 140 ms = **0 / 23.8 / 44.8 / 64.4 / 84.0 / 110.6 ms.** The 44.8 ms hitbox lands **exactly on the start of beat 3** and stays live through beats 3–6. Beat 6 is then held ~108 ms into recovery.

**Blades.** LONG katana = **RIGHT** hand (far, since he faces LEFT). SHORT wakizashi = **LEFT** hand (near). **Neither blade ever enters the kick's line and neither cuts anything.** Beats 1–2: katana sweeps out high and back behind the far shoulder while the wakizashi drops low and forward across the near hip — both clearing the centre line. Beats 3–4: both arms locked wide as counterweights, katana tip angled up and away, wakizashi tip angled down and away, both edges turned outward. Beats 5–6: both back inboard — katana high at head height, wakizashi low across the belly, the Niten two-level guard.

**Beats.**
1. **Guard breaking backward.** Weight rolls off the lead foot onto the rear foot; hips and shoulders begin turning away from the opponent while the chin stays cranked back over the lead shoulder, so the hooded face and the gold eyes never leave him. Both arms swing outboard, wide of the ribs, clearing the whole centre line of the body. Both boots still flat on the floor.
2. **Deep chamber — the most compact silhouette of the move.** The lead knee rips up and folds tight: thigh pinned to the chest, heel tucked to the buttock, ankle dorsiflexed so the flat sole already faces backward. The standing leg bends and the torso folds forward over that knee, hips cocked back and up. Head still turned back over the shoulder, eyes locked on the target behind him. Nothing has extended yet.
3. **CONTACT.** The chambered leg fires straight back along one line — knee snapping to full lock, sole flat and heel leading, striking behind him at CHEST height, roughly one and a half body-widths back. Crown, spine, hips and extended leg form a single straight diagonal, torso folded low forward as the counterweight. The standing leg is bent hard with its sole planted flat and the ankle rolled slightly out. Loose black cloth at the hip snaps with the impact.
4. **Deepest extension, one beat further out.** The whole body is one rigid line: striking foot at its farthest point behind him, standing knee at maximum bend with the calf under visible tension. The hood snapped forward past the jaw by the recoil, the scarf blown straight forward off the shoulder. Both arms flung wide as counterweights, elbows locked, hands well clear of the leg's line.
5. **Recoil.** The knee re-folds fast and drags the shin back in under him, the foot still off the floor; the torso rises out of the fold, hips beginning to square back toward the opponent and the head coming round with them. The scarf still trails behind, through the empty space the heel just left.
6. **Settled and stable.** The kicking foot has set down behind him, weight even across both feet, knees soft, body turned back square to the opponent in a low compact guard, head level, eyes forward, hood settled. Both blades back inboard in front of the chest. Held on screen ~a tenth of a second after the kick ends — it must read as a finished GUARD, not a frame caught mid-move.

**Redraw constraints.**
- **The one existing cell is his only kick pose that actually depicts its move** — near-frontal ¾ hood, both swords sheathed behind the left hip, one wrapped fist chambered across the chest, far leg driven straight out behind at hip/chest height, foot flexed sole-out. That is roughly beat 3–4 of six and it matches the 30-tall mid-body box. Five of six beats are simply missing.
- **NOTHING IS INVULNERABLE.** No armorTimer, no i-frames. Do not draw the chamber as a dodge, slip or evade — it must read as *loading a kick*, or the pose promises a defensive property the engine does not give him.
- **The input is BACK; the movement is ZERO.** Put the turn-away in the body and the shoulders, **never as travel across the cell.**
- Authored facing LEFT, so the heel travels toward the **RIGHT** edge of the cell. This is the only row in his kit whose action leaves frame on the opposite side from all his sword attacks — the composition needs headroom on the right and the bbox will sit deliberately off-centre.
- The current cell's ink bbox is 140 × 138, one of the smallest on the sheet. Beats 3–4 will be far wider. **Grow the frame, never shrink the kick.** Standing sole on footY 312 in every beat except 5 (foot in air) and 6 (both down).
- **OPEN CALL — blades stowed vs in hand.** Both of his current kick cells have the swords sheathed, but sheathing and redrawing two blades inside a 140 ms move is physically impossible and every other cell on his sheet has both in hand. The brief above keeps them in hand and swings them clear, which still satisfies the engine's rule (no weapon swung, no crescent, no clash). If the owner rules them stowed it costs a real re-sheathe beat and the kick drops to five beats of action.
- Known and deliberately not drawn: a victim struck behind him is pushed along `attacker.facing`, i.e. toward Kael's front. Nothing in the art should imply a long shove — pushback is only 60 and the box lives 0.10 s.

---

## L4 · DOWN + Light — "SWEEP / ASHI-BARAI"

**Ashi-barai** 足払い
**Row `ksweep` · 1 cell today → 6 beats · grounded only · ⛔ THINNEST OF THE GROUNDED ROWS**

**Engine.** `isDownPressed()` is tested FIRST and wins over the forward/back axis, so Down+Light is always the sweep. No `gldown*` row exists, so it always reaches `executeKick('sweep')`.
**`vx = 0` — ZERO travel;** he reaps from a fixed spot. 140 ms animation, startup 44.8 ms. ONE hitbox **52 × 16**, 6 damage, active 0.12 s, pushback 40, flagged `low: true, trip: true`. Recovery **0.30 s — his longest kick recovery, the price of the trip.**
**Geometry:** `low` sets `oy = height - sh - 2` = 30 on a 48-tall body, so the box spans **y 30–46 of 48 — the bottom third. This is an ANKLE-TO-SHIN reap, not a thigh sweep.** Front-facing, so it takes the +8 corner reach-back: effective 60 wide, about two body-widths in front. **There is no rear arc.**
**Trip rider:** on a grounded victim, `stunTimer` is max'd to 0.55 s and `vy = -140` — legs out from under them, a small pop clear of the floor, a long floor stun. Hit mark `H06`, which outranks the ordinary kick mark.
No launch, no wallsplat, no second box, **no invuln, no armor.** 0 chakra, no winded gate. Stagger 5. `canClash` false, `hasuji` false.
**Six beats once wired:** same `ATTACK_EXPOSURES_6` = 0 / 23.8 / **44.8** / 64.4 / 84.0 / 110.6 ms. **Beat 3 is the contact frame;** the 0.12 s box stays live from beat 3 past the end of the animation (44.8 → 164.8 ms). Beat 6 is held ~135 ms into recovery.

**Blades.** LONG katana = **RIGHT** hand (far), held out high and back behind the far shoulder for every beat of the reap so the edge never crosses the sweeping leg's arc. SHORT wakizashi = **LEFT** hand (near), **and this is the hand that PLANTS on beat 2** — it must flip to a reverse grip (*gyaku-te*) with the short blade lying flat back along the underside of the forearm, edge turned away from the body, so the heel of the palm and the knuckles can take his full weight on the floor without letting go of it. Reverse-gripped through beats 2–5, rolled back to a forward grip on beat 6. Neither blade cuts anything.

**Beats.**
1. **Guard drops straight down.** Knees fold, hips sink vertically, chest stays upright over them, chin over the lead knee, eyes forward on the opponent. Both blades swing outboard, wide of the thighs, clearing the legs completely. Both boots still flat on the floor, feet about a shoulder and a half apart.
2. **Weight dumps onto the lead leg.** He tips forward and the near hand goes down — heel of the palm flat on the floor a boot-length ahead of the lead foot, elbow slightly bent taking the load. The trailing leg cocks in tight, heel pulled to the buttock, knee gathered under the hip. Hips at knee height. Head stays up, hood pushed back off the face, eyes still on the target.
3. **CONTACT.** The gathered leg whips out flat and horizontal across the floor in front of him — knee locking, boot sole leading edge-on, the shin parallel to the ground and almost touching it, the foot roughly two body-widths out. The planted hand carries his whole weight with that shoulder stacked over it; the support leg is folded into a full deep squat, sole flat. The strike is at ANKLE-TO-SHIN height — nothing in the arc rises above the knee. Dust flattens and streams along the ground line behind the boot.
4. **Through the arc.** The reaping leg continues past the point of contact, hips rotating open with it, torso rolling back and out over the planted hand as counterweight. The boot still skimming at the same low height, the leg now angled across his front rather than straight out. The free arm swings outward for balance. Ground dust lifting in a low horizontal band behind the sole.
5. **End of the reap.** The leg finishes crossed under his own body, hips low and turned, knee re-bending as it draws back in. The planted hand pushes off the floor, wrist rolling, that shoulder rising. The torso begins to lift out of the roll, head still up and forward.
6. **Recovered into a very low, compact crouch** — both boots flat and planted wide, hips just above heel height, back straight, head level, hood settled, eyes forward. Both blades back inboard in front of him. Held ~an eighth of a second after the reap ends, so it must read as a finished LOW GUARD, not as motion.

**Redraw constraints.**
- **The one cell on disk does not depict a sweep at all** (near-frontal deep squat, hands empty, both swords sheathed, no leg extended). Only the hip height is reusable. This action is reconstructed from the hitbox.
- **DO NOT DRAW A SPINNING 360 SWEEP.** `low` only overrides the box's height; `ox` stays front-facing and `vx` is pinned to 0. A spin would show him covering ground and threatening a rear arc the engine does not have.
- **KEEP THE WHOLE ARC BELOW THE KNEE.** 16 px of a 48 px body is one third of his height, floor-anchored. A thigh- or waist-high sweep lies about the hitbox and reads unblockable-high when it is a low.
- **The trip is the VICTIM's animation, not his.** His six beats depict the reap that causes it, never the takedown. His finish is a crouch, not a follow-up.
- Authored facing LEFT, so the reap travels toward the **LEFT** edge of the cell.
- Both the planted hand and the skimming boot sit on the footY-312 line on beats 2–5, and beats 3–4 will push the widest ink bbox this row has ever carried — **grow frameW/footY rather than shrinking the pose.**
- **OPEN CALL — blades stowed vs in hand.** Same call as the heel. The reverse-grip plant is the specific consequence of keeping them in hand; if the owner rules them stowed, the planting hand is simply an open palm and beat 2 changes.
- **Head read:** his hood and gold eyes are drawn near-frontal ¾ across the whole sheet while the BODY carries the direction. Keep that convention — do not flatten this row to a pure side profile when nothing else of his is.

---

# HEAVY TIER

## H1 · NEUTRAL + Heavy — "CROSS SLASH"

**Jūmonji-giri** 十文字斬り
**Row `kcross` · 6 cells today → 6 beats · grounded only**

**Engine.** `p.spec.id === 5 && p.isGrounded && F.kcross1` → `kcross1..6`. Airborne neutral Heavy falls through to `kxcut` instead. Duration **330 ms** (no `SLICE_SPEED` entry for id 5, so no speed-up). Track `heavy` = `[0, .08, .18, .44, .68, .88]` → cell1 0–26, cell2 26–59, cell3 59–145, cell4 145–224, cell5 224–290, cell6 290–330 ms.
**ONE hitbox:** 60 × 40 (rate = 1.0), **18 damage**, active 0.07 s, pushback 108, delay 138.6 ms → **live 138.6 → 208.6 ms.** That opens on the last ~6 ms of cell 3 and spends the rest of its life under **CELL 4.**
No launch, no low/trip, **no armour, no invulnerability.** Travel `vx = facing * 170` — near a body-width forward. Recovery **0.45 s.** Stagger 30. No chakra.
The engine adds its own FX: `pendingSlash` at 75 ms draws `WEAPON_FX[5] = 'cross'` — two straight steel-white strokes meeting in an X, r = 50 px, life 0.21 s, anchored at the shoulder pivot.

**Blades.** LONG katana = **REAR** hand — crosses high: cocked over the rear shoulder (b2), high-forward through the X (b3), fully extended high on the far side (b4), lifted back above the rear shoulder (b6). SHORT wakizashi = **LEAD** hand — flat across the belly (b2), low-forward through the X (b3), extended low on the far side (b4), forward-low at chest height (b6). **BOTH BLADES CUT ON THE SAME BEAT** — one hitbox, one instant, two edges.

**Beats.**
1. Feet planted a shoulder-and-a-half apart, weight settling onto the front foot, knees soft. Both arms hang open and wide, one blade out to each side of the body, tips angled slightly down and away. Nothing is crossed yet — the silhouette is a wide, open V of arms and steel.
2. **The load:** both arms swing IN and the wrists cross in front of the sternum. The long blade cocked back and up over the rear shoulder, edge turned outward; the short blade drawn flat across the belly pointing the other way. Shoulders coiled away from the direction he faces, chin tucked, front knee bent deep.
3. **The pass** — hips snap open and both arms fire outward THROUGH each other in the same instant. Catch the blades at the exact moment they cross at chest height: an X centred on the sternum, the long blade travelling high-forward while the short blade travels low-forward, each edge already clear of the other. Head down behind the crossing, back heel lifting as the hips rotate.
4. **CONTACT, full extension.** Both arms driven completely past the crossing and out to the opposite sides from where they started — both blades beyond the body's silhouette on the side he faces, arms straight, torso rotated hard, leading shoulder driven forward and the rear leg stretched out behind: the forward step has landed. This is the beat the damage happens on; it must read as steel finishing a cut, **not as a recovery.**
5. **Deceleration.** Elbows fold back in, both blades angled down and outward with the tips still trailing, chest opening back toward square, front foot still nailed to the floor. Hood, scarf and mantle whip late — still catching up to the body.
6. **Zanshin.** Back to the two-sword guard: long blade lifted and held edge-up above and behind the rear shoulder, short blade extended forward and low at chest height toward the direction he faces, knees soft, feet re-set square. Alert, not slumped.

**Redraw constraints.**
- **ONE HIT ONLY** — do not stage this as two separate strikes. The whole identity is that both blades arrive together.
- **The contact sits on BEAT 4, not beat 3.** The box opens at 138.6 ms and beat 3's window closes at 145 ms, so ~64 of the 70 ms active window plays under beat 4. Beats 3 AND 4 must both read as the cut; beat 4 in particular cannot look like a settle.
- **No launch** — the opponent is pushed back flat, not popped up. Nothing should read as rising/uppercut geometry.
- **No invulnerability** — no untouchable/phasing/after-image beat; he is fully hittable throughout.
- **Grounded only** — both feet in contact with the floor across all six beats.
- He covers about a body-width forward: beats 3–5 sit visibly further forward than beat 1.
- The engine lays its own steel-white cross trail over the sprite at 75 ms, and the old cell 3 *also* had a huge gold X painted in — so the shipped move carried two X effects for one swing. **Owner's call whether the redraw bakes an X in;** beat 3 already says where it would go.
- **Facing:** the old `kcross` row drifted near-frontal. Author at the idle's clean three-quarter facing LEFT, gold scarf and black mantle trailing behind on the right. The beat-6 guard must match the idle's Niten guard so the move settles straight back into stance.

---

## H2 · FWD + Heavy — "TWIN CYCLONE"

**Kuruma-giri** 車斬り
**Row `kcyc` · 6 cells today → 6 beats · grounded only**

**Engine.** `spec.id === 5 && isGrounded && axisH === facing && !down && !up`. **TWO HITS** — and the engine's own comment says the two hits are what separate it from his one-turn spinning Special.
Duration **380 ms.** Recovery 0.44 s. Travel `vx = facing * 150` — an **advancing** mid; it overwrites the generic 170 heavy step, so slightly slower but the whole move is longer and he genuinely crosses ground.
- **Hitbox 1:** 80 × 46, **10 damage**, active 0.12 s, pushback 70, delay 0.10 s → **live 100–220 ms.**
- **Hitbox 2:** 80 × 46, **11 damage**, active 0.12 s, pushback **120**, delay 0.20 s → **live 200–320 ms.**
21 damage total; the second hit pushes noticeably harder. No launch, no low/trip, no armour, no invulnerability, no chakra.
Track `cyclone` = `[0, .10, .26, .53, .74, .90]` → cell1 0–38, cell2 38–99, **CELL3 99–201, CELL4 201–281**, cell5 281–342, cell6 342–380 ms. The delays are deliberately married to the cells: **box 1 opens at 100 ms exactly as cell 3 comes up, box 2 at 200 ms exactly as cell 4 comes up. CELLS 3 AND 4 ARE THE TWO CONTACTS.**
FX: one `pendingSlash` at 75 ms only — a single 'cross' trail for the whole move, not one per ring.

**Blades.** LONG katana = **REAR** hand throughout: trails low behind (b1), whips round at waist height (b2), and **DRIVES THE FIRST RING** (b3) extended straight out at hip level, carried a full turn. SHORT wakizashi = **LEAD** hand: tucked flat across the belly (b1–2), then **LEADS THE SECOND RING** (b4) at chest height while the long blade sweeps the low half of that same revolution. Both trail behind on the entry side (b5), both return to the Niten guard (b6).

**Beats.**
1. **Entry step.** Deep forward lean, lead foot reaching out well ahead of the hips, torso low — he is already moving. Both arms swept back and down behind the hips, both blades trailing low behind him, edges out. Rear heel driving off the floor.
2. **The wind-up of the turn.** The shoulders begin rotating away from the direction of travel while the hips keep driving forward; the long blade whips around from behind at waist height, the short blade tucked flat across the belly. Front knee loaded, hood and mantle streaming straight back.
3. **FIRST RING — the first full horizontal revolution.** Body dropped into a low crouch, knees wide, spine near-vertical over the hips; the long blade extended straight out at WAIST height and carried all the way around him, so the cut path closes into a complete horizontal ring at hip level, passing in front of the shins and behind the shoulders. This is the first contact and must read as a blade landing, **not a windmill of empty air.**
4. **SECOND RING** — the turn continues into its second revolution, body dropped lower still, hips sunk almost to a squat. Now the short blade leads, extended out at CHEST height, while the long blade finishes the low half of the arc: two ring paths overlapping around him, one high across the chest and one wide and low near the ankles. Second contact — the harder one; the body is at its most compressed and most committed here, and he is at his deepest point of travel forward.
5. **Exit.** The spin unwinds: torso comes back up out of the crouch, still drifting forward, both arms crossing back over the chest, both blades trailing behind on the side he came from, tips still low. Feet re-planting under him, weight shifting back onto the rear leg to kill the slide.
6. **Zanshin.** Planted, square, both blades up in the two-sword guard: long blade lifted edge-up above and behind the rear shoulder, short blade forward and low at chest height toward the direction he faces. Knees soft, mantle settling.

**Redraw constraints.**
- **TWO VISIBLE CONTACTS IS THE WHOLE MOVE.** Beats 3 and 4 must each look like a blade landing on something, at two clearly different heights (hip, then chest). One ring plus a recovery means the second hitbox lands on a pose that isn't attacking and the move stops reading.
- **The two contact beats are pinned in time.** Do not reorder, and do not push the second contact later than the 4th of 6.
- **He travels the whole time** — 150 px/s over 380 ms is roughly a body-and-a-half of ground. Beat 4 sits visibly further forward than beat 1, and beat 6 further still. An advancing mid, not a stationary spin.
- **It is NOT his spinning Finisher.** The Special is one big sweeping turn that ends an exchange; this is two rings thrown ON THE WAY IN. Body low, compact, driving forward — not tall and flourishing.
- **No launch** (pushback 120 vs 70, but never lifts). **No invulnerability** — no untouchable blur, phase or after-image pass.
- Grounded only, feet on or very near the floor — a low pivoting turn, not an airborne spin.
- The engine spawns ONE cross trail for the entire move, so any drawn ring FX is additional. The old row painted big gold rings into cells 3, 4 and 5 and the crouch was largely hidden behind them, which is exactly why the two contacts were hard to tell apart. **The BODY under any FX has to hold the pose on its own.**
- **Facing:** old `kcyc` cells drift near-frontal. Author at the idle's three-quarter facing LEFT.

---

## H3 · BACK + Heavy — "KAEL LOW PARRY"

**Gedan-barai** 下段払い
**Row `klowp` · 6 cells today → 6 beats · grounded ONLY**

**Engine.** id 5, `isGrounded`, `axisH === -facing`, not Down, not Up. Sets `PARRY_STANCE`, `lowParryAnim`, recovery **0.45 s** (speedScale 1.0), **`parryFlashTimer = 0.15`** — the catch window.
**NO HITBOX on the stance** — the engine's own comment says "a parry that also swings beats everything". **ZERO travel. ZERO chakra/stamina. NO invulnerability** — it is a 0.15 s catch window, not i-frames; miss the timing and he eats the hit clean. Whiff cost is the 0.45 s recovery.
**Catch resolves two ways.** *Projectile* (no `sourceHitbox`): **REFLECTED** — a new projectile spawned at his chest travelling 480 px/s back at the thrower, **no counter swing at all.** *Melee:* `ATTACK_SPECIAL`, recovery 0.42, 300 ms anim, `nitenAnim`, **spawnHitbox 85 × 50, 15 damage, 0.16 s live, 190 pushback, delay 0.05, `launch: true, launchVy: -360`.** Attacker: `stunTimer 0.7`, STUNNED. **ONE hit, and it is a LAUNCHER — the counter's finish has to rise.**
**Draw:** stance plays `klowp1-3`; the counter replays **`[klowp4, klowp4, klowp5, klowp6]`** — **cell 4 is HELD for two beats.**

**Blades.** SHORT wakizashi = **LEAD/FRONT** hand. It does **100 % of the catching and never counters**: low and horizontal across the shins (b1), swept flat to ankle height (b2–3), shovelled outward (b4), parked low-forward as cover (b5–6). LONG katana = **REAR/TRAILING** hand. Completely silent through the catch, then delivers the **entire counter alone**: cocked overhead-behind (b4), one rising diagonal cut low-front to high (b5), held forward at head height (b6). This split is his declared style — `kael.json` discipline notes: off-hand blade parries, long blade counters.

**Beats.**
1. **READY** — standing tall and square, hood up, chin level, gold eyes forward. Weight even on both feet, front knee softened. The SHORT blade in his lead hand held low and horizontal across the front of his shins, edge angled down and forward. The LONG blade hangs in his rear hand at the trailing hip, tip pointed down and back at the ground behind him. Shoulders relaxed, both arms low — nothing above the waist.
2. **DROP INTO THE CATCH** — knees driving apart and sinking until his hips are near half his standing height, torso pitched forward over the front thigh, back flat. The lead arm sweeps the SHORT blade out flat and low across his whole front, the blade dead horizontal at shin/ankle height, a hand's width off the ground. The rear arm folds tight behind his ribs, LONG blade tucked back and out of the sweep's line. Head low, eyes still up and forward.
3. **THE CATCH** — the deep crouch held rigid, front arm locked out, SHORT blade braced flat across the incoming low line at ankle height, the rear hand brought in to press the flat of that blade's spine and take the shock through both arms. Feet wide and both heels planted, shins vertical, the whole body a low wedge with no gap under it. Chin tucked, eyes level, absolutely still — the beat that reads *nothing gets under me*.
4. **TURN OUT AND LOAD** — he begins to stand out of the crouch, hips lifting and rotating open. The SHORT blade shovels outward and away from his body at low-front, clearing the caught weapon aside. The LONG blade comes alive: the rear arm swings the katana up and back so its tip is overhead and behind his head, elbow high, that shoulder cocked back hard. Rear heel driving into the ground, front foot flat, spine already twisting. **Unstable and mid-turn — a loaded spring, never a resting pose.**
5. **THE RISING COUNTER CUT** — the LONG blade tears up on a steep diagonal from low-front to high, rear arm fully extended so the blade points up and forward above his head, edge trailing the arc. His chest thrown open, hips driven square through the cut, back leg extended, and he is rising onto the ball of his front foot with both heels lifting off the ground — the whole body is going UP behind the blade. The SHORT blade stays low and forward, still covering the shin line.
6. **ZANSHIN** — heels settling back to the floor, weight resettling square, knees re-bending into a low guard. The LONG blade brought down and held out forward at head height, arm three-quarters extended, tip levelled at the enemy. The SHORT blade drawn back across his waist, edge out. Body still, hood up, gold eyes locked forward — alert, not relaxed.

**Redraw constraints.**
- **Cell 4 is drawn ONCE but PLAYED TWICE** — on screen roughly twice as long as any other counter beat. It has to hold up as a loaded, mid-motion, about-to-fire pose. Drawn as a comfortable stance, the counter reads as two separate moves.
- **Grounded only.** Both feet on or near the floor for all six. The only air in it is the launcher rise in beat 5 (heels off, ball of the foot) — the −360 launch showing on his own body.
- **Beats 1–3 must read as ONE continuous sink,** because those same three cells are the whole move 100 % of the time it catches nothing.
- **The catch is LOW** — everything defensive happens between his knee and the floor. Nothing in beats 1–3 raised or overhead, or it becomes indistinguishable from the Up+Heavy high parry, which is its deliberate opposite number.
- He also reflects projectiles off this catch, and the reflect uses **no counter cells at all** — no extra pose needed for it.

---

## H4 · UP + Heavy — "KAEL HIGH PARRY"

**Ukenagashi** 受け流し
**Row `khigh` · 6 cells today → 6 beats · grounded OR rising in the air (`vy < -180`)**

**Engine.** `id 5 && (isGrounded || vy < -180) && isUpPressed()`. **⛔ Jump priority is explicit and deliberate:** Up IS the jump key, so a grounded-only gate meant holding Up to arm the parry had already launched him and the input fell through to his generic heavy. **The `vy < -180` clause is what makes the move exist** — he can arm and hold this parry a few pixels off the floor on the way UP.
Sets `PARRY_STANCE`, `highParryAnim`, recovery **0.45 s**, `parryFlashTimer = 0.15`. **NO hitbox** (same reason as the low one). **ZERO travel, ZERO chakra/stamina, NO invulnerability.**
**Catch resolves identically:** projectile → **REFLECTED** at 480 px/s, no counter swing. Melee → `ATTACK_SPECIAL`, recovery 0.42, 300 ms, `nitenAnim`, **85 × 50, 15 damage, 0.16 s live, 190 pushback, delay 0.05, `launch: true, launchVy: -360`;** attacker stunned 0.7 s. **ONE hit, LAUNCHER.**
**Draw:** stance `khigh1-3`; counter replays **`[khigh4, khigh4, khigh5, khigh6]`** — **cell 4 HELD for two beats.**

**Blades.** SHORT wakizashi = **LEAD/FRONT** hand — does the entire overhead catch and never counters: 45° up-forward (b1), punched flat overhead (b2), swept front-to-back across the crown (b3), then dropped to the waist as a guard (b4–6). LONG katana = **REAR/TRAILING** hand — silent under the roof, then delivers the whole counter alone: levelled at the chest (b4), one straight horizontal thrust (b5), back to an up-forward guard (b6).

**Beats.**
1. **READY** — standing tall, hood up, chin lifted a fraction, gold eyes angled up and forward at the ceiling line. The SHORT blade in his lead hand raised on a 45° up-forward angle, tip well above the top of the hood. The LONG blade in his rear hand held low and horizontal across his waist behind the lead hip. **Feet close together and knees compact with the weight centred — NOT a wide planted stance,** because this pose also plays while he is off the floor and rising.
2. **THE LIFT** — lead arm punching straight up over the crown of the hood, the SHORT blade rolling flat so it lies dead horizontal above his head, edge canted skyward, elbow high and locked. Head tucked slightly down between his shoulders, shoulders shrugged up into the block, both knees bending and the hips sinking under the blade to take the weight. Feet stay close, heels light. The LONG blade drops back behind the rear hip, out of the way.
3. **THE CATCH** — the overhead cover held and rotating: the SHORT blade sweeps flat across the top of his head from front to back, wrist rolled fully over, elbow above ear height, driving the descending weapon off behind him. The LONG blade rises in the rear hand to the shoulder, tip up and forward. Both blades above shoulder height, both arms up — the whole silhouette is a closed roof over his head. Knees deeply bent under it, gaze up and forward.
4. **DROP AND LOAD** — he drops hard out of the overhead cover into a wide, deep stance: knees far apart, hips sunk, torso turned and coiled back over the rear leg. The LONG blade comes down and forward into the rear hand at chest level, elbows pulled in tight against the ribs, tip levelled straight at the enemy's chest, forearm and blade in one line. The SHORT blade swings back down across the body to the waist. Shoulders wound back behind the levelled tip. **Mid-motion and coiled, never a settled guard.**
5. **THE COUNTER THRUST** — the LONG blade driven straight forward on a flat horizontal line out of the chest, rear arm fully extended, tip at the enemy's chest height, rear leg locked straight behind him and front knee deep, the whole spine and both shoulders stacked behind the point. **His hips lift and drive up through the thrust as it goes in.** The SHORT blade held flat across his waist, edge outward, as the guard.
6. **ZANSHIN** — the LONG blade drawn back up to a 45° up-forward guard at head height, arm half-bent. The SHORT blade tucked in tight against the ribs on the lead side, edge out. Knees re-bending, weight settling square over both feet, hood up, gold eyes still locked forward. Held, alert, not relaxed.

**Redraw constraints.**
- **⛔ Jump priority constrains the ART, not just the input.** Because the trigger accepts `vy < -180`, beats 1–3 can be on screen while he is genuinely **AIRBORNE and rising.** Draw them feet close together, knees compressed, weight centred — **no wide planted stance, no ground-contact dust, no foot splayed flat.** They must read correctly floating a few pixels above the floor as well as standing on it. Beats 4–6 always resolve grounded and can be fully planted.
- **Cell 4 is drawn once, played twice** — longest beat on screen; loaded and mid-drop, not a stance.
- **The counter here is a THRUST on a flat line.** That is what separates it from the low parry's RISING CUT. Both catch, both answer with the long blade, both launch — **the two answers must not be the same swing or the family collapses into one move.** Low parry = catch at the ankles, answer upward. High parry = catch over the head, answer straight through the chest.
- It launches (−360) even though the thrust is horizontal — show that as **his own hips driving UP through beat 5**, not as the blade angling up.
- Beats 1–3 are the whole move whenever it catches nothing, so they must be complete and readable on their own. Projectile reflects use no counter cells.

---

## H5 · DOWN + Heavy — "LOW-HIGH SCISSOR"

**Hasami-giri** 鋏斬り
**Row `kscis` · 6 cells today → 6 beats · grounded only**

**Engine.** `spec.id === 5 && isGrounded && isDownPressed()`. Sets `scissorAnim`, duration **400 ms**, recovery 0.42 s, **`vx = 0` — he does not travel a single pixel; both feet stay planted on the dirt for the whole move.** Stats 6/6/6 so every number below is literal.
**TWO HITS, TWO HEIGHTS:**
- **Box 1:** 72 × **22**, 9 damage, active 0.12 s, push 60, **`low: true`** (must be blocked crouching), delay **0.08 s.**
- **Box 2:** 72 × **52**, 11 damage, active 0.12 s, push 110, delay **0.18 s**, **`launch: true, launchVy: -300`** — pops the victim into juggle.
**No invulnerability** (no `invulnTimer` write anywhere in this branch). No chakra/stamina. Not unblockable, no armor-pierce, no trip.
Track `scissor` = `[0, .10, .20, .45, .68, .88]` → b1 0, b2 40, **b3 80, b4 180**, b5 272, b6 352 ms. **The two boxes are pinned to cells 3 and 4 on purpose** (engine comment): box 1 goes live at exactly 80 ms = the first frame of beat 3, box 2 at exactly 180 ms = the first frame of beat 4. **Beat 3 IS the low contact, beat 4 IS the launching contact.** They are also the two longest holds (100 ms and 92 ms). The branch does not null `pendingSlash`, so the engine paints its own 'cross' streak on top — the drawn body does not have to carry the whole read.

**Blades.** LONG katana = **RIGHT** hand (far side, matching the idle's raised far-hand blade). SHORT wakizashi = **LEFT** hand (near side). **The SHORT wakizashi makes the LOW cut (b3)** — the small blade, the weaker 9-damage low that must be blocked crouching. **The LONG katana makes the RISING cut (b4–5)** — the bigger blade, the 11-damage launcher. Long goes up, short goes low; they cross once, at beat 4, and that crossing is the move's whole read. **Never draw both blades doing the same half.**

**Beats.**
1. **Deep sink.** Both knees bent hard, hips dropped below knee height, front foot flat and turned in, rear knee almost brushing the dirt, hooded head low and tucked toward the leading shoulder. BOTH blades chambered back and low on his rear side: the long katana in the right hand cocked down behind the rear hip with its tip near his back heel, the short wakizashi in the left hand held flat across his shins, edge already parallel to the ground. Shoulders coiled away from the target. Nothing extended yet.
2. Weight snaps forward onto the front foot, front knee driving past the toes, torso pitched low over the leading leg. The left arm fires: the short wakizashi rips out of the shin-chamber and starts its sweep along the floor, blade still only half extended, forearm skimming the ground. The long katana stays back and drops even lower behind the rear hip, tip now pointing at the floor behind his heel — visibly loaded, doing nothing. Hood pushed back off the brow by the lunge.
3. **LOW CONTACT.** Lowest point of the whole move. Hips at ankle height, rear leg fully extended straight out behind him with the shin dragging, front leg folded under his chest, near hand almost touching the dirt for balance. The short wakizashi in the LEFT hand fully extended forward, arm locked, the blade horizontal at ankle-to-shin height and edge flat to the floor — **this is the cut, it travels at the ground and nothing above the knee is threatened.** The long katana in the RIGHT hand at its deepest chamber, tip down and behind, wrist cocked back. Both feet still touching the ground.
4. **RISING CONTACT.** The body uncoils upward **without leaving the floor**: legs straightening, hips driving up and forward, chest opening to the target, heels lifting but the balls of both feet STILL PLANTED on the dirt. The long katana in the RIGHT hand rips upward from behind the rear heel along the exact same diagonal the short blade just cut, forearm crossing his own body, blade caught mid-rise between hip and shoulder height with the tip climbing past his own head — the launching cut. The short wakizashi has swung back down and out to his rear side, tip low, clearing the line. **The two blades now travel in opposite directions through one shared line — jaws of a scissor closing.**
5. **Top of the swing.** Fully upright now, chest square, feet planted apart and flat, both heels down again. The long katana has finished past vertical and sits high above and slightly behind the head, arm extended, tip pointing back over his shoulder. The short wakizashi out to the near side at hip height, tip angled down and forward. Hood settling back onto the brow, scarf still lifted by the swing.
6. **Settle.** Solid planted stance, feet apart at shoulder width, knees soft, weight back to centre and evenly on both legs. Both arms drawn back in toward the body: the long katana angled up and out on his rear side, the short wakizashi angled down and forward on his near side, tips forming a wide open guard around the torso. Head level, eyes on the target.

**Redraw constraints.**
- **HE NEVER LEAVES THE FLOOR.** `vx = 0` and no `vy` is written anywhere in this branch — **the LAUNCH is applied to the VICTIM, not to Kael.** A redraw that has him hop, jump or rise on the up-half contradicts the engine and reads as a different move. Keep at least one foot in contact with the dirt in all six beats.
- **The two heights must be obviously different.** Box 1 is 22 px tall (ankle/shin), box 2 is 52 px (shin to chest). A viewer has to see that the first cut cannot be blocked standing and the second cannot be blocked crouching — engine comment: *"a low that pops you up is the whole point, so if the art and the boxes drift apart the move stops being readable."*
- Beats 3 and 4 are the only two carrying a hitbox. Beats 1–2 are 40 ms each and 5–6 are the tail; do not spend detail on them at the cost of the two contacts.
- Authored facing LEFT — the cut travels toward screen-left, the chamber is on screen-right.

---

# SPECIAL TIER

## S1 · NEUTRAL Special — "SPINNING FINISHER"

**Kaiten-giri** 回転斬り
**Row `kspin` · 6 cells today → 6 beats · grounded only**

**Engine.** `else if (specId === 5)`, reached only when no direction is held. **ONE hit:** `spawnHitbox(60, 35, 15, 0.09, 50, {delay: 0.218})` — a 60 × 35 box **centred on his own body, NOT a reach; it is a ring around him.** 15 damage flat, active 0.09 s (~5 frames), **pushback only 50, the lightest special push in his kit, so the victim stays in front of him.** No launch, no low, no trip, no armor, **no invulnerability** (that belongs to his Down+Special reversal).
Animation lengthened to **520 ms** (generic special base is 320) purely to hold the turn. **Chakra 25.** Recovery **0.6 s.** Travel: the branch sets no `vx` of its own, so he keeps only the generic special step `vx = facing * 140`, bled off by attack friction — **one step into the turn, essentially spinning ON THE SPOT.**
Track `spin` = `[0, .10, .22, .42, .66, .86]`. **The box goes live at 0.42 of the string, exactly where cell 4 comes up — CELL 4 IS THE CONTACT FRAME,** and cells 3+4 together own 40 % of the move.
**Airborne note:** pressed off the ground he does **not** draw this row — he borrows `kxcut`. So **every `kspin` cell is a grounded, both-feet-on-the-dirt drawing.**

**Blades.** RIGHT hand = the **LONG katana**, and it is the **outside edge of the circle** the whole way round — greatest radius, and its tip is what the hitbox reads as. LEFT hand = the **SHORT wakizashi**, riding the inside of the same sweep about half a body-width behind and closer to his ribs, so the two together **close the ring** instead of drawing one arc twice. Both stay in hand: nothing sheathed, nothing thrown, nothing swaps hands.

**Beats.**
1. Feet a little wider than shoulders, both flat on the ground, weight settling back onto the rear (right) foot. Hips already begun to open away from the viewer while the head stays turned front-left, hood low over the brow, gold eyes level. The LONG katana in his right hand swept out behind him at hip height, arm extended, tip trailing back and slightly down. The SHORT blade in his left hand pulled in tight across the belly, knuckles at the near hip, tip forward. Nothing has swung yet — this is the load.
2. The rear knee drives the hips around. Shoulders have turned a quarter, so his chest points toward the viewer while his head stays tucked and cranked to keep his eyes on the front. The LONG katana has swung from behind him to horizontal across his chest, edge outward, arm nearly straight. The SHORT blade tracks it about half a body-width behind, at waist height, travelling the same direction — the two starting one continuous line.
3. **Halfway round.** His back beginning to show, near shoulder rolled forward, both arms out at full span so the two blades sit on opposite sides of him and read as a single sweep passing through his hip line. The front foot has pivoted on the ball; the rear foot skims the ground on its toe. The LONG katana on the outside of the sweep at the greatest radius, the SHORT blade tucked inside it and closer to the ribs.
4. **CONTACT FRAME — the turn is fully round and the steel completely encircles him.** Both arms at maximum extension, level with the shoulders; the LONG katana's tip at its furthest reach and rising, the SHORT blade level beneath it on the opposite side of his body, so between them they **ring him from waist to shoulder with no gap in front, behind, or at either side.** Both boots planted, knees bent, torso vertical and centred over them — **he has NOT travelled off his spot.** Chin up, gold eyes forward through the turn. This frame must read as a closed circle of blade around a still centre.
5. **Unwinding out of the turn.** Rotation carries past centre: the LONG katana out past his lead side with the tip dropping toward the floor, the SHORT blade folding back in across the ribs. Weight transferred onto the lead (left) foot, rear heel lifting, torso leaning a touch into the direction of the spin.
6. **Stopped and settled.** Feet wide and both flat, knees soft, chest square to the front-left, chin up, eyes forward, hood settled back over the brow, mantle still swinging past him. The LONG katana held high and forward at head height, tip up and angled away; the SHORT blade dropped low and back, tip down behind his hip. The daishō split wide open at the end of the turn, **and the two blade lengths must be unmistakably different at a glance.**

**Redraw constraints.**
- **Pushback is deliberately tiny (50) and the box is body-sized rather than long-reaching: this hits AROUND him and keeps the opponent in front. It is not a poke.** Beat 4 has to sell that or the move is unreadable.
- **He must stay in place** — no lunge, no dash, no ground-skid; the only travel is one small step. Grounded in every cell.
- **Six beats is required, not preferred** — a mismatched count silently falls back to generic even exposure and puts the wrong cell under the hit.

---

## S2 · FWD + Special — "TRAVELLING CROSS SLASH"

**Fumikomi-giri** 踏み込み斬り
**Row `ktrav` · 6 cells today → 6 beats · grounded only**

**Engine.** Gated on `axis === this.facing && !upHeld && !down && this.isGrounded`. **ONE hit and it lands at the END of the travel:** `spawnHitbox(76, 52, 18, 0.13, 190, {delay: 0.22, tier: ATTACK_SPECIAL})` — 76 × 52, **18 damage (his biggest special number)**, active 0.13 s (~8 frames), **pushback 190 — heavy, it sends them away**, the opposite of the neutral spin's 50. No launch, no low, no trip, **no armor, NO invulnerability: this move is paid for entirely by commitment, not by immunity.**
**TRAVEL: `vx = facing * 330` against a 440 ms animation** — roughly twice the ground his Fwd+Heavy Twin Cyclone covers, which is the stated point of the move (the cyclone throws two rings on the way IN; this spends chakra to cross further and pay it off in one committed cut). **Chakra 25.** Recovery 0.46 s, hard-set, not speed-scaled.
Track `trav` = `[0, .08, .18, .30, .40, .50]` — **front-loaded on purpose:** the first five cells burn through the first half while he crosses the gap, then **cell 6 comes up at 0.50 — exactly the 0.22 s / 440 ms hitbox delay — and is HELD from there through the contact and out. Cell 6 is the money frame and is on screen for half the move.**

**Blades.** RIGHT hand = **LONG katana.** Carried HIGH and BEHIND the trailing shoulder for the entire travel (b1–3), swung up to vertical overhead as he lands (b4), cocked to its furthest point back (b5), then driven **DOWN from high-rear to low-front** as the upper stroke of the X (b6). LEFT hand = **SHORT wakizashi.** It **LEADS the whole travel** — held low and thrust forward, tip first, so the short blade is the first thing to arrive (b1–3) — then draws back across the chest (b4), sits low across the leading hip (b5), and drives **UP from low-front to high-rear** as the lower stroke of the X (b6). **The two strokes must be visibly OPPOSITE in direction; that is what makes it scissor rather than two parallel cuts.**

**Beats.**
1. **Coiled to launch.** Deep forward lean over a bent lead (left) knee, rear (right) leg extended straight back with the heel driving hard off the floor, torso low and close to horizontal, head up and eyes locked forward-left. The LONG katana cocked HIGH behind him in his right hand, tip pointing up and back over the trailing shoulder. The SHORT blade in his left hand held low and forward at hip height, tip aimed straight at the opponent, leading the way in. Mantle and scarf still hanging — the wind has not caught them yet.
2. **Push-off complete and accelerating.** Torso rising out of the deep lean, rear toe just breaking contact with the ground, front knee driving up and forward. Both blades hold exactly the same relationship as beat 1 — long high and back, short low and ahead — **because nothing has been swung yet; the body is doing all the work.** Hood pressed back against the skull by the speed, scarf and the tail of the mantle pulled dead straight out behind him.
3. **Full flight, the ground-covering frame.** Body stretched forward and nearly level with the floor, rear leg trailing straight out behind with the toe pointed, lead knee tucked up under the chest, BOTH feet clear of the ground. LONG katana still high and back over the trailing shoulder; SHORT blade thrust out in front at full arm extension, tip first. **He is a spear crossing the gap.**
4. **Still travelling, but the arms begin to load.** The LONG katana swings up from behind the shoulder to vertical, straight above his head; the SHORT blade draws back across his chest toward the far shoulder. Torso comes upright, hips back underneath him, both legs beginning to reach down for the floor. The forward lean nearly gone — he has arrived where he wanted to be.
5. **ARRIVAL AND WIND.** Both boots slam down wide and flat, knees folded deep to kill 330 px/s of momentum, torso dropped low over the front leg, mantle still surging forward past him. The LONG katana at its highest cock behind the trailing shoulder, edge back; the SHORT blade crossed under it at the opposite corner, low and across the leading hip. **The arms are wound as far APART as they get in the whole move. Nothing has been cut yet — this is the single frame of stillness at the end of the run.**
6. **THE SCISSOR — the contact frame, and the one held longest.** Both arms close through each other in one beat: the LONG katana driven DOWN from high-rear across to low-front, the SHORT blade driven UP from low-front across to high-rear, the two crossing in a hard X directly in front of his chest, wrists overlapped and forearms touching at the crossing point. Feet wide and planted flat, hips dropped, shoulders square to the front-left, head tilted down the line of the cut, gold eyes on the target. **The X sits in front of the body at chest height and is the whole read of the move.**

**Redraw constraints.**
- **The hit lands at the END of the travel, not during it,** so beats 1–5 must contain **NO cutting motion at all** — five frames of a body crossing ground with the blades parked, and one frame of the cut. If any early beat looks like a swing, the move stops matching the engine and becomes indistinguishable from Twin Cyclone, which is the one that hits on the way in.
- **Cell 6 is on screen for half the animation** and carries the only contact, the biggest damage in his special column (18) and the biggest pushback (190) — it must read as one hard, committed, symmetrical X, drawn to be looked at.
- **No armor, no invulnerability** — the pose should read committed and **exposed**, not guarded.

---

## S3 · BACK + Special — "NITEN PARRY"

**Jūmonji-dome** 十文字止め
**Row `xparry` · 6 cells today → 6 beats · grounded only**

**Engine.** `specId === 5 && axis === -this.facing && this.isGrounded`. Sets **`PARRY_STANCE`**, recovery **0.5 s** (honest whiff recovery), **`parryFlashTimer = 0.15`** — the strict catch window (compare Tsubasa 0.133, Mokurai 0.133/0.22). **NO hitbox, NO travel, NO invulnerability. Chakra 25.**
**Resolution.** Gate `state === PARRY_STANCE && parryFlashTimer > 0`: white sparks, `screenShakeAmount 15`, `sfx('parry')`, `parriedAt` stamped. If the incoming hit has **no `sourceHitbox` (a projectile) it is REFLECTED** back at the attacker at vx ±480 instead of countering. Otherwise: `nitenAnim`, `ATTACK_SPECIAL`, 300 ms anim, recovery 0.42, **`spawnHitbox(85, 50, 15, 0.16, 190, {delay: 0.05, launch: true, launchVy: -360, tier: ATTACK_HEAVY})`** — one 85 × 50 chest-height answer, 15 damage, 190 pushback, launches; attacker `stunTimer 0.7`, STUNNED.
**Draw:** the stance plays the whole strip `xparry1..6`; the counter replays **`xparry5, xparry5, xparry6`.**

**Blades.** **WAKIZASHI (short) = LEAD hand, and it is THE BLADE THAT CATCHES.** It is the outside blade of the X in beat 3, which is the entire identity of the move (the engine comment says exactly that). **KATANA (long) = REAR hand, THE BLADE THAT ANSWERS:** parked behind the hip (b1), cocked high beside the ear (b2), braced behind the wakizashi (b3), cocked over the rear shoulder (b4), and the **sole striking blade in beat 5**, out level at chest height. Neither blade leaves his hands and neither changes hands at any point.

**Beats.**
1. **READY.** Narrow stance, lead foot half a step forward, both feet flat, knees bent, weight centred and low; body bladed so the lead shoulder points at the opponent. Wakizashi in the LEAD hand up in front of the sternum, edge outward, tip angled up and forward. Katana in the REAR hand dropped back behind the rear hip, tip down and trailing, deliberately out of the way. Head level, gold eyes locked forward. **Nothing moves from this footprint for the next three beats.**
2. **THE BLADES PART — THE INVITATION.** No step. The lead arm pushes the wakizashi further forward and slightly across the centreline at chin height, tip up. The katana swings up out from behind the hip to a high rear diagonal beside the ear, tip up and back. The two blades now bracket his body — short one forward, long one back and high — **leaving an open lane down the middle.** Front knee deepens, rear leg braces.
3. **THE CATCH.** Both arms snap inward and the two blades cross in a tight X directly in front of his face and chest — **wakizashi on the OUTSIDE taking the load, the katana's flat braced behind it.** Elbows pinned to the ribs, shoulders hunched forward, chin tucked down behind the crossing point, front knee driven down, rear leg braced straight back, both feet flat and skidding a hand's-width backward. The entire body compressed behind the crossed steel; the crossing point is the highest-energy spot in the frame.
4. **TURN AND OPEN.** Head lifts, and the X unwinds **by torso rotation rather than by stepping**: the wakizashi sweeps down and outward past the lead hip, clearing whatever it caught aside onto a low-forward diagonal; the katana cocks up and back over the rear shoulder as the hips start to rotate. Rear foot pivots on the ball, weight loads onto the back leg. Both feet still on the ground.
5. **THE ANSWER — A COMPLETE, COMMITTED CUT.** Full step through with the lead foot, hips square, torso driven forward over the front knee. The katana out on a **LEVEL forward line at chest height** at the end of a fully extended rear arm that has crossed to the lead side of the body, edge leading, tip past his own reach. The wakizashi held low and back across the front of the belt, edge out, covering the line the katana left. Head forward, eyes sighting down the long blade. **This frame must read as a finished strike on its own — no wind-up implied anywhere in it.**
6. **ZANSHIN.** The follow-through arrests: the katana stays extended forward but the tip drops a hand's width and the elbow softens; the wakizashi lifts off the belt to a forward-low guard so the two blades again make an open cross in front of him — long blade high and forward, short blade low and forward. Weight settles evenly onto both flat feet, shoulders drop, chin returns level. He is standing on the footprints he started from.

**Redraw constraints.**
- **⛔ ORIENTATION DEFECT IN THE CURRENT ROW — MEASURED, NOT INFERRED.** Cells 20/21/22 (beats 1–3) are drawn **FACING RIGHT**; cells 23/24/25 (beats 4–6) face LEFT, as do the idle cells, `block2`, `kfang` and `krise`. In 20–22 the gold eyes sit on the RIGHT of the hood with the cloth trailing LEFT; in 23–25 the eyes sit LEFT with the cloth trailing RIGHT. **Today the parry visibly spins around at beat 4. ALL SIX REDRAWN CELLS MUST FACE LEFT.**
- **⛔ SECOND DEFECT:** current cell 20 (beat 1) shows only ONE blade in frame. **Both blades must be visible and identifiable in every one of the six.**
- **⛔ BEATS 5 AND 6 DO DOUBLE DUTY:** the stance plays 1–6 straight through, but the counter replays cell 5 **twice** then cell 6. Beat 5 must be a self-contained committed strike that survives being held for two beats; beat 6 must read as its settle.
- **The catch also REFLECTS PROJECTILES** — beat 3 must work for a thrown object as well as a blade, so **do not draw the crossed blades gripping, trapping or bending any specific enemy weapon.** The pose is a braced cross; whatever it caught is left to FX.
- Counter numbers to honour in beat 5: an 85 × 50 box at **CHEST height** that launches (−360) — so the cut is **level and forward, never downward or overhead.**

---

## S4 · UP + Special — "SKYWARD FANG"

**Kiriage** 切り上げ
**Row `kfang` · 6 cells today → 6 beats · jump-priority allowance**

**Engine.** `specId === 5 && upHeld && jumpOk && !down`. No `isGrounded` guard, **but nothing in the branch leaves the floor.** Sets `fangAnim`, 440 ms anim, recovery 0.44 s, **`this.vx = 0` — he does not travel a single pixel, and `vy` / `isGrounded` are NEVER touched, so he stays planted.**
**ONE hitbox:** `spawnHitbox(44, 140, 16, 0.12, 120, {delay: 0.15, up: true, tier: ATTACK_SPECIAL})` — **44 px wide by 140 px TALL, a thin column straight overhead with essentially no horizontal reach.** 16 damage, live 0.12 s starting 0.15 s in, pushback 120, **no launch flag — it SWATS the airborne opponent back down.** No invulnerability, no armor. **Chakra 25.** The engine comment is explicit: this is the *patient* anti-air, deliberately distinguished from Down+Special — no invuln, no movement, no launch.

**Blades.** **KATANA (long) = REAR hand** for all six: ear-guard (b1), the leading blade of the upward drive (b3), the higher of the two tips in the overhead V (b4), back to the ear-guard (b6). **WAKIZASHI (short) = LEAD hand** for all six: level across the belt (b1, b6), lifted onto the rising line (b2), trailing the katana by half an arm (b3), the second tip in the V (b4). Neither blade is ever released, thrown, planted or swapped, **and the two never cross each other — they travel parallel up one vertical line and finish as a narrow V, which is the 'fang'.**

**Beats.**
1. **ROOTED GUARD.** Both feet flat on the ground a shoulder-width apart, lead foot half a step forward, knees soft, weight settled slightly onto the rear heel. Katana in the REAR hand cocked back beside his ear, tip angled up and behind the hood. Wakizashi in the LEAD hand held low and level across the front of his belt, edge up. Hood up, chin lifted, gold eyes tracking something high and in front of him.
2. **LOAD.** Identical foot placement — no step, no slide, both soles still flat. Hips drop about a head's-width as both knees fold; the katana tip swings out of the ear-guard onto a steep up-forward diagonal; the wakizashi wrist rolls so its tip lifts off the belt line onto that same upward line. Shoulders stay square, spine still stacked over the hips.
3. **DRIVE.** Legs extend hard **but the feet never leave the floor** — heels stay down, calves and toes visibly loaded, a small skid of dust at the soles at most. Torso stacks vertically, both arms drive upward past the head: katana leading, wakizashi trailing it by half an arm, both blade tips now clearing the crown of the hood.
4. **THE COLUMN — CONTACT.** Both arms locked out overhead, spine straight, chest open, head tilted back to look up the blades. Katana (rear hand) and wakizashi (lead hand) held in a **narrow upright V, the two tips within a hand's width of each other**, edges turned outward. **Both feet STILL FLAT ON THE GROUND**, front foot a half-step ahead, knees just short of locked. The read is a tall thin column of steel directly above his own head and **nothing reaching sideways.**
5. **SHOCK RIDES BACK DOWN.** The V opens a little as the impact travels into him: wrists give, the katana tip drifts back over the rear shoulder, the wakizashi tip tips forward over the lead shoulder, elbows bend, both knees re-bend to absorb. Feet unchanged, still exactly where they started; shoulders compress toward the ears.
6. **SETTLE.** Arms come down to chest height **without a single step.** Katana returns to the high rear guard beside the ear, wakizashi returns level across the belt, weight redistributes evenly over both flat feet, chin lowers back to the horizon. He is standing on the same footprints as beat 1.

**Redraw constraints.**
- **⛔ THE CURRENT ART CONTRADICTS THE ENGINE AND MUST NOT BE COPIED.** Cells 159–161 (`kfang4-6`) draw him with **BOTH FEET OFF THE GROUND drifting upward, legs trailing** — but the branch sets `vx = 0` and never touches `vy` or `isGrounded`, so in game he is standing still on the floor the entire time. **FEET PLANTED IN ALL SIX BEATS is the whole point of this move and the only thing separating it from Down+Special.**
- The hitbox is **44 wide × 140 tall**, so nothing in the pose should swing horizontally — anything reaching sideways draws a hit that does not exist.
- **No launch flag,** so the finish is a downward SWAT: beat 5 reads as force coming back down into him, not as him carrying someone up.

---

## S5 · DOWN + Special — "RISING TWIN FANG"

**Gyaku-kesa** 逆袈裟
**Row `krise` · 6 cells today → 6 beats · grounded**

**Engine.** `specId === 5 && down && this.isGrounded`. Sets **`this.vy = -430; this.isGrounded = false`** — he leaves the floor hard; **`this.invulnTimer = 0.25` — a quarter-second of total invulnerability on startup, the game's first true reversal;** `risingAnim`, 520 ms anim.
No `recoveryTimer` is set in the branch, so it keeps the ATTACK_SPECIAL default: **0.6 s recovery**, brutally punishable on whiff, and he is airborne through most of it.
**ONE hitbox:** `spawnHitbox(48, 55, 12, 0.25, 60, {launch: true})` — body-sized, **no delay, live from frame one (that is what makes it a reversal)**, live a full 0.25 s, 12 damage, weak pushback 60, `launch: true` with no `launchVy` so it takes the default **−430 — identical to his own rise, so attacker and victim go up together and he keeps the juggle. Chakra 25.**
**Draw:** the row plays **`krise2..krise6` only — five cells; `krise1` is packed but never displayed.**

**Blades.** **KATANA (long) = REAR hand throughout, and it is the blade that CUTS:** low behind the hip (b2), the leading edge of the rising diagonal (b3), fully overhead (b4), high behind the shoulder (b5–6). **WAKIZASHI (short) = LEAD hand throughout, riding the same rising line one beat behind the katana:** across the shins (b1–2), chest-height on the arc (b3), crossing under the katana's wrist (b4), extended forward (b5–6). **The 'twin' in the name is the two blades tracing ONE arc a beat apart, not a scissor.** Both stay in hand for all six.

**Beats.**
1. **COILED CROUCH — THE INVULNERABLE BEAT.** Deep squat, both feet flat and close together under the hips, thighs folded onto the calves, torso curled forward over the knees, head tucked so the hood shadows the face. Katana in the REAR hand and wakizashi in the LEAD hand both drawn low and **crossed in front of his SHINS**, edges outward, tips forward and down. Nothing of his body reaches past his own knees — a small hard closed ball with steel across the front of it. This is the *nothing can touch me* frame.
2. **UNWIND, STILL ON THE FLOOR.** Same low crouch, but the crossed blades separate: the katana slides down and back behind the rear hip until its tip trails behind his heel, the wakizashi drops across the front of the shins at knee height. Heels lift, weight rolls forward onto the balls of both feet, head still down, back still rounded.
3. **LAUNCH — THE CUT.** Both legs snap straight and **both feet leave the ground TOGETHER**, toes pointed, the body a single straight line from toe to crown. The katana sweeps out from behind the rear hip up along that line in one continuous rising diagonal, edge leading, tip level with the top of the hood. The wakizashi follows a hand's-width behind on the same arc, its tip level with his chest. Face lifted, gold eyes forward, scarf and mantle snapping straight down past his heels.
4. **CLIMBING.** Higher off the ground, hips ahead of the feet, legs trailing and slightly bent behind him. Katana now fully overhead and past vertical; wakizashi arriving at head height on the same diagonal, its blade crossing UNDER the katana's wrist. Cloth streaming straight down. Nothing beneath him but air.
5. **OPENING AT THE TOP.** Shoulders square to the front, the katana arm at full stretch above and behind, the wakizashi arm extending forward and up, so the two blades form a wide open V above and around him. Knees drawing up under the body, feet clear and tucked, torso coming upright.
6. **APEX SETTLE.** Vertical body, knees tucked and ankles nearly crossed under the hips. Katana held high behind the shoulder, wakizashi held forward at chest height, both edges outward, both ready to fall. The whole figure reads as weight at the top of an arc with empty space underneath — the frame that hands over to the juggle.

**Redraw constraints.**
- **The engine draws only `krise2..krise6`** — beat 1's crouch is packed and unused. **Deliver all six regardless:** beat 1 is the only frame that can show the 0.25 s invulnerable startup, and the missing beat is one line of engine work, not a redraw problem.
- **The crossed blades in beat 1 sit at the SHINS.** Do NOT draw the chest-height X — that is `block2` and it belongs to the Back+Special parry; **the two moves must not read the same at their first frame.**
- **The hitbox is live from frame ZERO with no delay,** so beat 3 is already a contact beat — the cut must look committed and finished at launch, not still winding.
- Launch default is −430, the same as his own rise: beats 4–6 read as **him and the victim going up together**, so keep his own body vertical and rising, never slumping.
- The old cells 110–112 carried a large **drawn** gold crescent trail behind the katana. Drawn trail crops are permitted on this project (the *procedural* crescent is what was killed), but the beats above describe **BODY ONLY** — **whether the crescent returns is the owner's call, not the generator's.**

---

# AIR TIER

## A1 · air Light (neutral) — "ZERO-G CROSS" *(proposed row name — the move that stops him falling)*

**Kūchū jūmonji** 空中十文字  *(proposed — not yet on a delivered board)*
**Row `aneu` · 0 dedicated cells (falls to shared `air1..3`) → 6 beats · ⛔ THIN**

**Engine.** Direction and feet are captured at PRESS time, never redrawn from live input, so the pose must stay correct even if he lands mid-swing. Stats 6/6/6/6, so every scalar is ×1.00. Anim window **180 ms.** Recovery 0.25 s.
**⛔ THE DEFINING PROPERTY — ZERO-G CUT:** a neutral air light that is not Down-held **clamps `vy` to ≤ 40 and sets `airFloatT = 0.20 s`, during which gravity runs at 0.22×. HE STOPS FALLING AND HANGS FOR THE WHOLE SWING.** Capped at 2 per airtime, refreshed on landing and on wall contact.
**ONE hit, not two:** air lights never enter `LIGHT_STRINGS` (the string block is gated on `isGrounded`), so exactly one hitbox — 40 × 30, 8 damage, active 0.05 s, pushback 60, startup 57.6 ms. No launch, no low hit, no armor, no invulnerability, no travel, zero chakra/stamina.
**Draw path:** it falls past every dedicated branch and lands on the shared `air1..3`, three cells at ~60 ms each. **⛔ THE `aneu` BRANCH IS UNGATED BY `spec.id`: packing `aneu1..6` gives him this row with ZERO engine work.**

**Blades.** **LONG KATANA — right hand, every beat.** It chambers high over the right shoulder and comes DOWN through the crossing point; **it is the blade that owns the single contact.** **SHORT WAKIZASHI — left hand, every beat.** It stays tucked at the left ribs and drives STRAIGHT OUT through the same chest-height line, crossing under the katana at contact and finishing beneath it. Neither is sheathed, neither swaps hands, and they are never the same length.

**Beats.**
1. Airborne and squared up, facing left, both feet clear of the ground and drawn up under him, knees bent, ankles close. Torso upright, shoulders wound back to the right. The long katana in his RIGHT hand cocked back over the right shoulder with the tip angled up and behind him; the short wakizashi in his LEFT hand held level across the chest with the tip pointing left. Hood settled, scarf and mantle still hanging down.
2. **The hang — his fall has stopped dead and the whole body is motionless in the air.** Knees pulled tighter, shins together and tucked under the hips, toes pointed. Chest opened a few degrees toward the viewer, head turned hard left down the line of the cut. Long blade drawn even further back past the right shoulder, right elbow lifted high; short blade pulled in tight to the left ribs, both wrists loaded. **Scarf and mantle hang STRAIGHT DOWN, dead still — nothing is falling and nothing is streaming.**
3. Both arms fire at once and the blades are still travelling, edges not yet met. The right arm sweeps the long katana down and forward out of the high chamber, its tip cutting toward chest height; the left arm drives the short wakizashi straight out from the ribs on the same chest-height line. Hips begin a quarter rotation to the left. Legs stay tucked and off the ground; the body has not dropped a pixel.
4. **THE CONTACT, one instant.** Both edges cross in a tight X directly in front of his chest at chest-to-shoulder height, the long katana coming down through the line from above-right and the short wakizashi cutting straight through it from the ribs. Arms at full extension but **CLOSE to the body — a compact scissor about one arm's reach in front of him, not a wide arc.** Torso pitched slightly forward over the crossing point, head down the line, both feet still tucked and clear of the ground.
5. **Follow-through.** Both arms carried past each other and out to the left: the katana extended ahead at shoulder height angling slightly down, the short blade pulled back beneath it near the hip, the two edges now parallel. Body pitched forward over the extended arms, hips rotated fully through, the trailing leg beginning to unfold down and back. Mantle whipped out behind him to the right.
6. **Recovery, and the fall resumes.** Arms drawn back in to a closed guard — katana raised back over the right shoulder, wakizashi recovered flat across the belly, edge out. Torso back upright, knees dropping and both legs reaching down toward the ground with toes pointed. **Scarf and mantle now stream UPWARD past the shoulders, because he has started falling again.**

**Redraw constraints.**
- **THE HANG IS THE POINT.** The engine literally suspends gravity for 0.20 s here. Beats 2–4 must read as a body that is **NOT falling** — cloth hanging straight down or held, never streaming. **Beat 6 is where the streaming returns.**
- **Why this must not look like his others:** `afwd` is already a two-handed OVERHEAD CHOP straight down; `aback` is a reverse cut behind him with the short blade while the long stays low-forward; `kxcut` is his air HEAVY, a huge two-blade X. **This row is the fast, small, in-place one** — 40 × 30 box, 57.6 ms startup, chest height, in front of the body.
- **FEET NEVER TOUCH ANYTHING.** Every cell is airborne; leave clear space below the boots. **No ground spark, dirt puff, or contact shadow at the bottom of any cell.**
- Old reference read as ACTION only: chamber → cross → follow-through. That reading is preserved; the shared 3-cell set is not.

---

## A2 · air Heavy (NEUTRAL only) — "JUMPING X-CUT"

**Tobi jūmonji-giri** 飛び十文字斬り  *(proposed — not yet on a delivered board)*
**Row `kxcut` · 6 cells today → 6 beats**

**Engine.** `spec.id === 5 && !isGrounded && F.kxcut1`, on track `xcut`. **⛔ IT ONLY DRAWS ON A NEUTRAL AIR HEAVY.** The directional air-heavy branch sits above it and Kael owns full `hfwd`/`hback`/`hup`/`hdown` rows, so forward/back/up/down in the air each draw their own row; `kxcut` catches only the no-direction press. Down+air is a different move entirely (METEOR BREAK / `startSlam`).
No per-fighter branch exists, so it falls to the GENERIC heavy: 330 ms, rate 1, pow 1. **Root-motion lunge is gated on `isGrounded` — AIRBORNE, SO NO `vx` IS WRITTEN AT ALL:** he keeps whatever horizontal jump momentum he had, and no `vy` either, **so gravity is uninterrupted — NO hang, NO stall, NO dive.**
**ONE hit:** 60 × 40, **18 damage — his single biggest normal** (the scissor's two hits total 20 across two boxes), active 0.07 s, push 108, delay 138.6 ms. No launch, no low, no trip, no spike, no armor, no invulnerability, no chakra. Recovery **0.45 s**, longer than the animation — he will usually touch down still inside it.
Track `xcut` = `[0, .10, .22, .46, .70, .88]` → b1 0, b2 33, b3 73, b4 152, b5 231, b6 290 ms. **The hitbox is live 139 → 209 ms, straddling the END of beat 3 and the START of beat 4** — the cut must still be visibly cutting across **both**; beat 4 is follow-through, not recovery.
**DOUBLE DUTY:** this same row is also borrowed by Kael's **airborne neutral Special** (`spinAnim` off the ground), because his spin cells are a planted grounded stance. Whatever is drawn here plays for both inputs.

**Blades.** LONG KATANA = **RIGHT** hand (far side). SHORT WAKIZASHI = **LEFT** hand (near side). **Both used SIMULTANEOUSLY on the single contact** — that is what makes it an X-cut rather than two swings. The LONG katana takes the **HIGH-REAR → LOW-FRONT** diagonal (over the shoulder, down past the leading knee). The SHORT wakizashi takes the **LOW-REAR → HIGH-FRONT** diagonal (up from the hip, out past the far shoulder). They cross once, at beat 3, in front of his own chest. Beat 1 has them already crossed and closed at the chest; beat 4 has them fully reversed and past each other. The long blade must read visibly longer and more curved in every beat.

**Beats.**
1. **Airborne and compact.** Both knees pulled up under the chest, shins tucked back, torso curled forward, hood pressed down over the brow, scarf streaming back behind him. Arms folded tight across the front of the chest with the wrists overlapped — the long katana in the RIGHT hand laid across the body with its tip out past the near shoulder, the short wakizashi in the LEFT hand crossed under it with its tip past the far hip. **The X is closed.** Nothing extended; the smallest silhouette he will be in this move.
2. The arms rip apart while the body stays airborne. The RIGHT arm drives the long katana up and back over the head, blade nearly vertical, tip behind and above the hood. The LEFT arm drops the short wakizashi down and forward past the near hip, tip angled at the ground ahead of him. Torso begins to open, chest turning square to the target. Legs start to split — front knee still tucked, rear leg beginning to reach back. Both blades now at opposite ends of the same diagonal, loaded on the two arms of an X.
3. **THE X — CONTACT.** Both arms scythe through at once in opposite diagonals, crossing directly in front of the chest at the target's chest height. The long katana in the RIGHT hand caught mid-travel on the high-rear-to-low-front diagonal, blade angled down and forward past the near knee. The short wakizashi in the LEFT hand caught on the opposite low-rear-to-high-front diagonal, blade angled up and forward past the far shoulder. **The two blades physically cross, edges scissoring, right in the middle of his own frontal plane.** Torso squared and open, front knee still tucked up, rear leg trailing straight and long behind. **Body at full spread — the biggest silhouette of the move.**
4. **Follow-through, still cutting.** The arms have driven fully past each other and reversed: the long katana now points down and forward past the leading foot, arm extended and low; the short wakizashi now points up and back behind the far shoulder. Hips rotated hard from the swing, shoulders counter-turned, the tuck opening — both legs reaching down and apart. The blades are no longer crossed but the whole body still reads as being **carried through the cut, not settling.**
5. **Airborne recovery.** Both arms hauling back in toward the centre line, elbows folding, blades levelling out at chest height with the tips still forward. Torso straightening upright out of the twist, chest re-squaring. Legs swinging down beneath him, knees soft and slightly apart, toes pointed at the ground. Scarf snapping back the other way as the rotation stops. **Feet still clear of the ground — no dirt, no dust, no landing.**
6. **Airborne guard.** Fully upright in the air, body vertical, knees bent and both feet reaching down beneath the hips ready for a landing **that has not happened yet.** The long katana angled up and out on his far side, the short wakizashi angled down and forward on the near side — the same wide open guard the ground stance settles into, held in the air. Head level, gold eyes forward. **Still no ground contact and no impact FX.**

**Redraw constraints.**
- **⛔ THE OLD CELL 5 DRAWS A GROUND LANDING WITH A DIRT-BURST — THAT IS WRONG AND MUST NOT BE REDRAWN.** The engine writes no `vy` and no landing state anywhere in this path; the move can be pressed at the apex of a jump and the animation is only 330 ms while the fall is far longer. **Beats 5 and 6 must be AIRBORNE recovery.** Any drawn dirt, dust, ground line or planted foot will play with the character hanging metres above the floor.
- **NO HANG AND NO DIVE either.** Contrast Exile's air heavy, which explicitly writes `vy = min(vy, 40)` for a hang, and the roster meteor's `vy = min(vy, -60)`. Kael's neutral air heavy writes **neither**, so his existing jump arc continues unbroken through all six beats. Do not draw him stalling, floating, or driving downward.
- **ONE HIT, ONE MOMENT** — both blades cut in the SAME instant. Beat 3 is the money frame and beat 4 must still be follow-through.
- 18 damage is the largest single number on any Kael normal, and the box is small (60 × 40, roughly his own torso). A committed, close-range, no-launch hit costing 0.45 s of recovery — **draw it as a real full-body commitment, not a poke.**
- **NEUTRAL ONLY** — nothing directional (no forward lunge, backward retreat, upward reach or downward stomp); those four are already `hfwd`/`hback`/`hup`/`hdown`.
- **This row also plays for his airborne neutral Special.** Keep it a strong, generic twin-blade air cut that can stand in for both.

---

## A3 · air Special (neutral) — "AIR SPIN FINISHER"

**Tobi kaiten-giri** 飛び回転斬り  *(proposed — not yet on a delivered board)*
**Row `sneu` · ⛔ 0 CELLS — THE ROW DOES NOT EXIST → 6 beats**

**The finding, stated plainly: YES, he has an air Special, and it is neutral-only BY CONSEQUENCE, not by design.** All four of his directional Specials are grounded-gated — Fwd Travelling Cross Slash requires `isGrounded`, Up Skyward Fang requires `jumpOk`, Down Rising Twin Fang requires `isGrounded` — and `DIR_SPECIALS` carries no id-5 key. So **off the ground, whatever direction is held, execution falls through to the bare id-5 branch:** `spinAnim = true`, 520 ms, ONE hitbox 60 × 35, **15 damage**, active 0.09 s, pushback 50, delay 218 ms. Recovery 0.6 s. **Cost 25 stamina.** No launch, no invulnerability, no armor, **no travel — `vx` is not touched, so he keeps his jump arc.** The directional-pin that used to kill this layer was LIFTED.
**Draw path:** the airborne `dirCells` branch answers fwd/back/up/down from `sfwd`/`sback`/`sup`/`sdown` — **but the map's fifth key, `'neutral': 'sneu'`, points at a row that does not exist**, so a neutral air Special falls all the way through and borrows `kxcut1..6`, his air-heavy X-cut. The file admits it: the `ponytail:` note says it "doubles what the air HEAVY draws" and that "dedicated air-special art replaces these two lines and nothing else." **⛔ `sneu` IS ALREADY IN THE MAP: packing `sneu1..6` fills this slot with ZERO engine work.**

**Blades.** **LONG KATANA — right hand, every beat.** It is the **crossbar of the spin**: it traces the full flat horizontal circle and it is the blade at maximum extension on the contact beat. **SHORT WAKIZASHI — left hand, every beat.** Held **180° opposite** the katana through the turn and scissors **UNDER** it at the contact. Both stay drawn the whole row; neither swaps hands; **the length difference must be obvious in every cell.**

**Beats.**
1. Airborne, feet clear of the ground, facing left. Body upright and wound tight against itself: hips and shoulders rotated back to the right while the head stays turned hard LEFT down the line of attack. The long katana in his RIGHT hand drawn all the way back behind him at hip height with the edge turned outward; the short wakizashi in his LEFT hand crossed in front of the belly with its tip pointing back to the right. Knees bent, shins trailing.
2. **The turn breaks loose.** Hips and shoulders unwind and the whole body starts rotating, chest turning away from the viewer. The trailing leg whips out and around at hip height to drive the rotation, the other leg tucked in tight as the axle. The long katana swings out wide from behind him, its tip tracing a **FLAT HORIZONTAL line at chest height**; the short blade still held in against the chest, following the torso round.
3. **Three-quarters through the wind-up**, back now mostly to the viewer, arms opened out symmetrically. BOTH blades horizontal at chest height on opposite sides of the body, **180° apart** — long katana leading, short wakizashi trailing directly opposite it. Legs pulled together, straight and pointed, the whole body a single rigid axle with the blades as the crossbar.
4. **THE CONTACT — the front of the spin comes back around to face LEFT.** The long katana in the right hand arrives fully extended out to the left at chest height, edge flat to the cut, **at the widest reach of the entire turn**; the short wakizashi in the left hand sweeps under it at the same instant so the two edges scissor shut in front of him. Hips fully rotated through, torso squared to the left, both feet still off the ground. **This is the money frame — the flattest, longest line in the row.**
5. **Carrying through past the hit.** Rotation continues left: the katana sweeps on past and behind him, the wakizashi rises up across the chest, and the torso begins to pitch as the spin loses its axle. The lead leg unfolds and reaches down out of the tuck, the trailing leg still swung out behind.
6. **Settle.** Rotation stops with him facing LEFT again, arms drawn in and crossed into a closed guard — katana in the right hand angled down and back past the hip, wakizashi in the left held flat across the ribs. Torso upright, both legs reaching down toward the ground with toes pointed, **mantle and scarf streaming UPWARD as the jump arc resumes and he falls.**

**Redraw constraints.**
- **NO TRAVEL, NO LAUNCH, NO INVULN.** `vx` is untouched, so he **holds his existing jump arc** through the whole spin — do not draw him lunging forward or rising. He is spinning where he already was.
- **FEET NEVER TOUCH ANYTHING.** Six airborne cells, clear space under the boots, no ground spark, no dirt, no contact shadow.
- 520 ms over six beats is ~87 ms a cell, so every beat gets real exposure — a full-turn rotation genuinely reads at this length. **Six is the right count.**
- **⛔ FLAGGED FOR AN OWNER RULING, NOT DECIDED HERE:** airborne fwd+Special, back+Special, up+Special and down+Special **ALL execute this same neutral spin** — same 520 ms, same 60 × 35 box, same 15 damage — while the draw path hands them four different pictures (`sfwd`/`sback`/`sup`/`sdown`). **Those four rows are art-only variants of one move.**
- **AND THOSE FOUR ROWS MISREPRESENT IT.** Read as action: `sfwd` is a forward two-blade thrust with a spark at the tips; `sup` drives both blades straight overhead; **`sdown` is a plunging downward stab that ENDS IN A GROUND-CONTACT SPARK AND DIRT PUFF — a grounded impact inside an airborne row, on a move that never touches the floor and never moves him vertically.** If those rows get redrawn they need to read as a horizontal spin, or the mechanics need to change to match the pictures.
- **Canon defect in the old air-special art, for avoidance not preservation:** `sfwd`/`sback`/`sup`/`sdown` all draw **TWO NEAR-EQUAL SHORT BLADES.** The new row must show the length difference at a glance in all six cells.

---

# WHAT I COULD NOT DETERMINE — marked, not invented

1. **`kpush` cell count — resolved, but the brief and the spec disagreed.** The commissioning note said `kpush` holds 4; the slot spec said 3. **Measured in `web/assets/sprites/kael.json`: four `kpush`-prefixed keys exist (`kpush1`, `kpush2`, `kpush3`, plus a legacy bare `kpush`), but the draw router hardcodes `[F.kpush1, F.kpush2, F.kpush3]`, so only three are ever displayed.** The fourth is an unreferenced orphan. Both numbers were right about different things.
2. **`kheel` and `ksweep` hold exactly ONE cell each** — measured: the only keys are the bare `kheel` and `ksweep`, no numbered variants. Confirmed.
3. **`aneu` and `sneu` do not exist on the sheet at all** — measured: no `aneu*` or `sneu*` keys. `air1`, `air2`, `air3` and `kxcut1..6` are what actually get drawn in their place. Confirmed.
4. **Kael's height is NOT a redraw constraint.** An earlier note in this project claimed the
   owner had made him the shortest of the six; that claim was checked against the Story Bible,
   found unsupported, and retracted (commit `1d70bb1`). The Bible's only height law is that the
   Executioner is tallest, *slightly*. Kael anchors the OLDEST↔YOUNGEST axis by AGE. Nobody
   else's rank is canon — do not scale him against a height order that does not exist.
5. **Whether drawn FX return** — the gold X on `kcross`, the gold rings on `kcyc`, the gold crescent on `krise`. Drawn trail crops are permitted on this project; the *procedural* crescent is what was killed. **Every beat above describes BODY ONLY. Whether FX get baked in is an owner call, not a generator call.**
6. **Air UP+Light and air DOWN+Light are NOT covered by this sheet.** Air Up+Light sets `airUpAnim` and Kael has neither an `airkick2` nor an `upatk3` row, so it returns `F.air2` — **ONE FROZEN CELL held for the entire move.** Air Down+Light returns the single `kstomp` cell 76. Neither has an ungated key, so unlike `aneu` they need **engine work as well as art**. Reported, not solved, and not measured beyond the routing.
7. **Six-beat conversions for `kheel` and `ksweep` need engine work.** Their router line returns a bare cell index. Six beats requires manifest keys `kheel1..6` / `ksweep1..6` plus a router line beside the `kpush` one, and the exposure math above assumes `ATTACK_EXPOSURES_6` with no `ANIM_TRACKS` entry. **That is engine work, outside this brief.**
8. **The blades-stowed-vs-in-hand question on both kick rows is genuinely open** and is called out in each section. It is an owner ruling, not something the art can settle.

---

# PRODUCTION NOTE — how to order the images

- **One full-width reference strip per move**, ~**2172 × 724 px**, **6–8 beats per image** (the 3-beat `kpush` strip runs short — do not pad it to six).
- **At least 300 px of drawn body height per figure.** (For context on the bar: the first clean-slate Kael asset to pass 4K measured 269 px against a 260 px minimum, so 300 px is comfortably above it, not a stretch target.)
- **Every figure FACING LEFT**, side profile or the sheet's three-quarter left, matching the idle. The engine mirrors for the right-facing fighter — do not compensate.
- **Plain white background.** No ground line, no shadow, no environment — the air rows in particular must have nothing under the boots.
- **Nothing touching the frame edge.** Beats with extreme reach (`kheel` 3–4, `ksweep` 3–4, `ktrav` 3, `kxcut` 3) will push the widest bboxes on the sheet — leave margin on all four sides, and remember `kheel`'s action leaves frame on the **opposite** side from every sword attack, so that strip needs headroom on the right.
- **Beat numbers visible under each figure** on the reference strip, so the pack step can key cell → beat without guessing.
- **Grow `frameW`/`frameH`/`footY` rather than shrinking any pose.** `frameH` is per-fighter; Kael's is 320 today with footY 312, and several of these beats will not fit it.