# SHIN — every input, its name, and what it does

Names and descriptions are canon where a source says so; the cell counts and the
ash/green status are measured live off `ember.png` every time this is regenerated
(`python3 tools/make_move_names.py`). **Source** is the honest part:

| tag | meaning |
|---|---|
| `board` | a delivered board or moveset file names this move |
| `engine` | the engine names it, usually straight from an owner ruling |
| `spec` | the Wolverine claw-combo spec or the identity lock |
| **`PROPOSED`** | nobody has named it — this is a working name from what the row does, and it is yours to overrule |

**Weapon:** ONE four-point wire shuriken on the hip in Form 1; **kunai only** in KAGE-NUI. Never a knife in Form 1.  
**Stats:** Speed 9 · Power 4 · Reach 7 · Defense 4 — speed / assassin.  
**He/him.** His silhouette signature is a **permanent low crouch**. A single glowing eye in side profile is CANON — never flag it.


## GROUND — Light

| input | row | cells | look | name | what it does |
|---|---|---|---|---|---|
| neutral + Light | `light` | 5 | green 29% | **Light Punch Chain**<br>`board` | His bare-handed jab string — the taijutsu board draws it in six. |
| forward + Light | `kpush` | 4 | green 28% | **Shoving Front Kick**<br>`engine` | The teep, shared kick tier: shove + wall-splat + log punt. Box 46x28 for 3. |
| back + Light | `kheel` | 1 | green 36% | **Reverse Heel Kick**<br>`engine` | Hits BEHIND him. ⛔ ONE DRAWN CELL for the whole move — the kick tier reads `kheel1..N` as a row already, so six beats play the moment they are packed. |
| down + Light | `ksweep` | 1 | green 35% | **Low Trip Sweep**<br>`engine` | Low and it trips. ⛔ ONE DRAWN CELL. Same as the heel: pure art, no engine work. |

## GROUND — Heavy

| input | row | cells | look | name | what it does |
|---|---|---|---|---|---|
| neutral + Heavy | `sheavy` | 5 | green 20% | **Fudo Ken**<br>`board` | The powered straight — his own board calls it FUDO KEN (POWERED STRAIGHT). Box 70x40 for 12. |
| forward + Heavy | `taijutsu` | 6 | green 32% | **Body Rush Taijutsu**<br>`board` | The shoulder-and-elbow rush off the taijutsu board, six beats. |
| back + Heavy | `kunaidash` | 6 | green 35% | **Wire-Step**<br>`engine` | The 180px teleport dash on the wire, priced at 15 chakra. Box 120x24 for 5 — a long, thin box because the damage is the PASS, not a swing. |
| up + Heavy | `cjknee` | 6 | green 36% | **Rising Knee**<br>`engine` | His anti-air knee. Box 40x96 for 7 — tall and narrow, it beats a jump-in. |
| down + Heavy | `slowsweep` | 6 | green 35% | **Low Sweep to Axe Kick**<br>`board` | The board draws it as a sweep that finishes with the heel coming down. |

## GROUND — Special

| input | row | cells | look | name | what it does |
|---|---|---|---|---|---|
| neutral + Special | `flying_kick` | 6 | green 4% | **Flying Kick**<br>`board` | The committed flying kick — the taijutsu board's fourth row. |
| forward + Special | `gsfwd` | 6 | green 45% | **Wire Launch**<br>`engine` | The grounded forward Special. |
| back + Special | `gsback` | 6 | green 43% | **Wire Retreat**<br>`board` | He vanishes backwards on the wire — the board calls it WIRE RETREAT. |
| up + Special | `srisaa` | 6 | green 32% | **Rising Palm**<br>`board` | Board: SUP (RISING PALM), and it doubles as his anti-air. Box 44x150 for 14 — the tallest box in his kit. |
| down + Special | `special` · `attack_body` | 7 / 6 | green 29% / green 3% | **Wire Shuriken Feint**<br>`board` | Board: SPECIAL (WIRE SHURIKEN FEINT). ⛔ It spawns NO HITBOX AT ALL, measured — the whole move is the lie, and the punish is what follows it. `attack_body` is its tail. |

## AIR

| input | row | cells | look | name | what it does |
|---|---|---|---|---|---|
| air neutral + Light | `air` | 3 | green 42% | **Air Normal**<br>`engine` | — |
| air forward + Light | `afwd` | 6 | green 48% | **Air Forward**<br>`board` |  |
| air back + Light | `aback` | 6 | green 49% | **Air Backward**<br>`board` |  |
| air down + Light | `adown` · `kstomp` | 0 / 1 | never drawn / green 35% | **Dive Stomp**<br>`engine` | ⛔ ONE DRAWN CELL today (`kstomp`). `adown1..N` already outranks it, ungated — six beats of a feet-first stomp play the moment they are packed, with no code change. |
| air neutral + Heavy | `hneu` | 6 | green 44% | **Air Neutral Heavy**<br>`PROPOSED` |  |
| air forward + Heavy | `hfwd` | 6 | green 45% | **Air Forward Heavy**<br>`PROPOSED` |  |
| air back + Heavy | `hback` | 6 | green 45% | **Air Back Heavy**<br>`PROPOSED` |  |
| air up + Heavy | `hup` | 6 | green 45% | **Air Up Heavy**<br>`PROPOSED` |  |
| air down + Heavy | `hdown` | 6 | green 34% | **METEOR BREAK**<br>`engine` | The roster-wide dive slam — anti-grav hang, 2.5x-gravity plunge that spikes an airborne victim, then a landing shockwave both sides. Six beats: tuck, commit, plunge, the burst at the feet, the landed crouch, the rise. |
| air neutral + Special | `sneu` | 6 | green 43% | **Focus Breath**<br>`board` |  |
| air forward + Special | `sfwd` | 6 | green 44% | **Flying Kick (air)**<br>`board` |  |
| air back + Special | `sback` | 6 | green 44% | **Wire Retreat (air)**<br>`board` |  |
| air down + Special | `sdown` | 6 | green 44% | **Ground Sweep (air)**<br>`board` |  |
| air up + Special | `sup` | 6 | green 43% | **Rising Palm (air)**<br>`board` |  |

## KAGE-NUI (second form, V)

| input | row | cells | look | name | what it does |
|---|---|---|---|---|---|
| V | `—` | — | — | **KAGE-NUI** — *影縫い, shadow stitching*<br>`owner` | His second form. He drops bare-handed taijutsu and fights with KUNAI only — a leaf-shaped black iron blade with a ring pommel. A physical grapple kit, not zoning. |
| neutral/fwd/back + Light, beat 1 | `f2_light1_` | 6 | green 40% | **Poke**<br>`owner` | Low-telegraph linear kunai jab at throat height — his FASTEST move, four frames of startup. |
| … beat 2 | `f2_light2_` | 6 | green 48% | **Rising Slice**<br>`owner` | Diagonal upward slice low-to-high across the chest. |
| … beat 3 | `f2_light3_` | 6 | green 49% | **Double Thrust**<br>`owner` | Dual-hand forward thrust with both kunai; chips through guard. |
| neutral/fwd/back + Heavy, beat 1 | `f2_heavy1_` | 6 | green 44% | **Tsuki Poke**<br>`owner` | Deep lunging forward thrust — the longest reach in the kit. |
| … beat 2 | `f2_heavy2_` | 6 | green 47% | **Cross-Slice**<br>`owner` | Wide horizontal two-kunai scissor. |
| … beat 3 | `f2_heavy3_` | 6 | green 46% | **Disarming Hook**<br>`owner` | Catches the guard on the kunai's RING POMMEL and rips upward to launch. |
| down + Light | `f2_clow_` | 6 | green 39% | **Low Ankle Poke**<br>`owner` | Crouching tip-stab at the feet — deep crouch on all six beats. |
| down + Heavy | `f2_csweep_` | 6 | green 46% | **Sweeping Slice**<br>`owner` | Low 360-degree rotational sweep, spinning on the supporting hand and knee. |
| air + Light/Heavy | `f2_air_` | 6 | green 49% | **Dive-Pierce**<br>`owner` | Airborne on all six beats — a steep 45-degree downward point-lead dive. |

## States (not attacks, but they all still need art)

| rows | cells | look | name | what it is |
|---|---|---|---|---|
| `xidle` · `idle` · `idle_v` · `idle_stance` | 6 / 2 / 1 / 1 | green 36% / green 36% / green 35% / green 35% | **Crouched Idle** | his silhouette signature is a PERMANENT LOW CROUCH — six beats plus the stance variants |
| `run_clean` · `run` | 8 / 2 | green 30% / green 34% | **Run** | the forward run — eight beats today |
| `jump` · `ajump` · `fall` | 3 / 5 / 2 | green 26% / green 31% / green 30% | **Jump / air / fall** | the jump arc |
| `crouch_` · `kneel` | 4 / 1 | green 63% / green 28% | **Crouch** | four crouch beats plus the kneel |
| `block` · `xblkguard` · `xblkhit` | 2 / 1 / 1 | green 35% / green 35% / green 34% | **Guard** | the block, the guard hold and the chip flinch |
| `hurt` | 3 | green 35% | **Hurt** | three stagger beats paced over the stun window |
| `roll_` · `roll` | 6 / 1 | green 51% / green 32% | **Dodge roll** | six drawn beats |
| `grabbed` | 8 | green 46% | **Grabbed** | eight beats of being held and thrown |
| `wallslide` | 1 | green 33% | **Wall cling** | the wire and the wall |
| `heavy` · `heavy_i` | 3 / 5 | green 36% / green 28% | **Legacy heavy** | flagged dead by the sweep but KEPT — see SHEET_V 583 |
