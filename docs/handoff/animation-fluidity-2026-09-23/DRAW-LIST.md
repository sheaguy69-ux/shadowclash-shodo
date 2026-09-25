# DRAW-LIST: every drawing owed for fluid frame-by-frame animation

Measured 2026-09-23 against `SHEET_V 872` (HEAD `7788dcd`), from the live manifests
`web/assets/sprites/<fighter>.json` and the pickers in `web/index.html`. Re-run
`inventory.py` before you start. If a number below no longer matches, trust the new run over this page.
Line numbers (`:13347`) drift whenever a lane edits `web/index.html`, so grep the named symbol.

This is the WHAT. `README.md` in this folder is the HOW (definition of done §1, clock §2,
packing traps §4, canon §5, lane rules §6). Read `README.md` first, then use this as the checklist.

---

## 0. Rules for every item on this list

1. **One item = one owner-gated step.** Show him the prompt and refs, he generates, you pack,
   show the filmstrip, he says yes, then move to the next item. Do not batch items.
2. **Search before you draw.** A drawing that already exists is not drawn again.
   - Approvals: `F=mizu; { find art media -iname "*approved*" -iname "*$F*"; find media -iname "APPROVAL*" | xargs grep -ril "$F"; } | sort -u`
   - Orphan cells (packed, no key points at them): `inventory.py` prints the count per fighter.
     LOOK at them at native size; most are superseded art, so reuse one only if it matches the
     current approved model.
   - Source boards: `art/shodo-source/<fighter>/`. The jump/land 8-frame boards
     (`*-jump-land-8f-*`) may already hold a missing apex or landing beat.
3. **No paid generation** (AGENTS.md §3.7). For each item you deliver to him: `PROMPT.md`,
   `refs/<fighter>-refs.png`, and `frame_breakdown.json` with target exposures. **Copy the shape of
   the finished pilot:** `media/mizu-airhurt-fluidity-20260923/` (PROMPT.md, frame_breakdown.json,
   candidate-keys/, live-check/, packed-preview/) and its source `art/shodo-source/mizu/mizu-airhurt-fluidity-v1/`.
4. **Board law:** figure faces LEFT, one row per prompt, ~1900–2000 px wide, feet on one ground line,
   same head size as that fighter's approved idle, no borders, no text. **Nothing but the body in the
   cell: no dust, no speed lines, no floor, no cast shadow.** Shadows baked into cells were
   deleted roster-wide at 798. FX are engine draws, not art.
5. **Canon (concrete tier):** Mizu bo (splits to hanbō) · Shin ONE eye, bare hands, wire + shuriken ·
   Mokurai bare bead-wrapped fists, no staff · Exile spiked ball, red iris `#B94828` · Tsubasa TWO
   tantō, no hood · Ember THREE claws per hand, grey, grey eyes · Kael one long + one short sword ·
   Executioner two eyes (front one a small wedge), ONE long sword. Full table: brief `PROMPTS.md` §0.
6. **Repointing:** new cells are appended to the sheet. Point the keys at them, bump `SHEET_V`, rebuild
   the runtime pack, all in the same commit. The old cells stay as orphans; stripping them is a
   separate step that he names.
7. **Transition keys are "art or nothing".** The engine plays `turn1`, `jsquat1..2`, `land1..3`,
   `skid1..2` only when the key exists (`transitionFrame` `:13347`, skid gate `:5704`). On Mokurai and
   Exile, adding the keys IS the wiring. No engine edit.

Clock: engine times below are GAME seconds at 60 ticks/s. Wall time = game ÷ 1.2 (`COMBAT_TEMPO`),
so 1 tick ≈ 13.9 ms on screen.

---

## 1. Row specs: what each drawing must show

Every fighter uses these specs. The per-fighter tables in §2 say which of them are owed.

### R-LAND · `land1..3` · 3 drawings
Plays only after a real fall (`landHard`), one-shot over `LAND_T 0.15` = 9 ticks, 3 ticks each (~42 ms).
Then cuts to `idle1`, so beat 3 must match the idle model exactly.

| beat | pose |
|---|---|
| land1 IMPACT | Feet planted wider than idle (~1.3× stance). Knees bent deep. Hips dropped so ink height is ~80–85 % of idle. Torso pitched forward. Arms, weapon, hair and cloth still LIFTED; they carry the fall and lag behind the body. |
| land2 OVERSHOOT | Body rising out of the squash, a little TALLER than idle (~103–105 %), chest up. Arms, weapon and cloth now swinging DOWN past their rest position. |
| land3 SETTLE | The idle pose with weight a few % lower, and cloth/hair falling into place. It cuts invisibly into `idle1`. |


### R-TURN · `turn1` · 1 drawing
Held for `TURN_T 0.07` = 4 ticks (~56 ms) on a grounded facing flip. The picker reads **`turn1` only**,
so a `turn2` would never play. Draw one.
- Square-on to camera (front view), mid-pivot. The HEAD already faces the new direction, because the head
  leads. Shoulders square to camera, hips still angled to the old side, weight on the back foot.
- Weapon pulled in close to the body, with nothing breaking the silhouette. The sprite is mirrored on the
  flip, so an asymmetric weapon changes hands. That is correct. It must not sit on the wrong hand
  *within* the cell.

### R-SKID · `skid1..2` · 2 drawings
Run released at speed → `SKID_T 0.10` = 6 ticks. `skid1` first half, `skid2` second half, facing the run.

| beat | pose |
|---|---|
| skid1 BRAKE | Torso leaning BACK against the run (~15–20° off vertical). Lead leg straight out front, heel down, toes up. Back knee bent low. Arms thrown forward and out for balance. Weapon, hair and cloth swinging FORWARD with the momentum. |
| skid2 RECOVER | Halfway from skid1 to idle: torso coming upright (a hair past vertical), feet closing toward the idle stance, arms returning. |


### R-JSQUAT · `jsquat1..2` · 2 drawings
`JUMP_SQUAT 0.05` = 3 ticks: `jsquat1` ~2 ticks, `jsquat2` the last ~1. The next cell is `jflight1`
(the launch), so `jsquat2` must read as the coil that launch releases.

| beat | pose |
|---|---|
| jsquat1 LOAD | Knees bent ~45°, hips dropped ~8 %, arms drawn back and down, head dipping. |
| jsquat2 COIL | Deepest crouch, ink ~75 % of idle. Heels LIFTING (weight on the balls of the feet), arms fully back, torso coiled forward. |


### R-WALK · `walk1..8` · 8 drawings
Already briefed. Law: `art/production/handoff/SHODO-WALK-LAUNCH-NINJAJUMP-BRIEF-2026-09-15/PROMPTS.md`
§2, paste-ready text in `prompts/<fighter>.md` Row A. It is a true loop: beat 8 flows into beat 1, and
every beat is equally strong, because `animPhase` never resets and all eight are seen. Paced flat
(`:13661`). Packing the row switches the WALK tier on by itself (`WALK_CYCLES 1`, `:3334`).

### R-AIRHURT · `airhurt1..8` · 8 drawings
Briefed in `PROMPTS.md` §3 and `prompts/<fighter>.md` Row B. **Two pilots are finished:**
Mizu (871, cells 256–263) and Shin (872, cells 447–454). Their folders are the template, above.
The engine is done: any sheet carrying `airhurt8` gets the eight-beat selector. Mizu's reads
her own arc (launch 0, apex 0.5, back at launch height 1): the apex drawing holds 6–9 frames at
the real apex and every beat plays on a juggle, so draw all eight as equals. Shin still runs the
fixed −150/0/80… px/s bands, where beat 1 hogs the rise and beats 4–7 flash one frame each; moving
him to the arc is his own owner call.

### R-NJUMP · `njump1..8` · 8 drawings, and the engine gate is still owed
Briefed in `PROMPTS.md` §4 with a per-fighter subsection (§4.1–§4.8). One full revolution over
`FLIP_TIME 0.45` (~56 ms a beat), beat 1 already airborne, beat 8 lands upright, every beat further
round than the last. **The owner wants it made in Blender plus his motion lane, not from stills**
(brief §5). Nothing plays until the `drawnFlip` gate from `ENGINE-CONTRACT.md` is added. Do that after
the art is approved.

### R-JFLIGHT · the normal jump · fill the repeated bands
The picker (`:13726`) shows `jflight(band+1)` by vertical speed (`jumpBand`, `:1697`):

| slot | vy band | should show |
|---|---|---|
| jflight1 | < −380 | launch: body stretched long, toes last off the floor |
| jflight2 | −380…−240 | rise: knees coming up |
| jflight3 | −240…−60 | tuck opening near the top |
| jflight4 | −60…100 | **apex hang:** most compact, weightless, the cloth floating |
| jflight5 | 100…270 | fall begins: legs extending down |
| jflight6 | ≥ 270 | **fast fall:** legs reaching for the floor, arms up, cloth streaming UP |

A slot that repeats another slot's cell shows the wrong phase of the arc. Draw exactly the repeated slots.

### R-DIVE · `dive1..6` · air Down+Heavy slam (`:14253`)

| slot | when | should show |
|---|---|---|
| dive1 / dive2 | the hang, `SLAM_HANG 0.15` split in half | tuck gathering → tuck at full coil |
| dive3 | the plunge | body driving straight down, stretched |
| dive4 | floor burst, recovery > 0.20 s | impact: deepest squash, weapon or fist into the floor |
| dive5 | recovery 0.20 → 0.09 s | rising out of the impact |
| dive6 | the last 0.09 s | near-idle recover |

`SLAM_LAG 0.38`. Every fighter today holds ONE impact drawing for dive4–6, so the whole 0.38 s recovery
is a freeze. Draw dive5 and dive6. Where dive2 repeats dive1, draw dive2 too.

### R-LOCK · `lock1..N` · blade lock (`bladeLockFrame` `:20202`)
The last two cells are the outcomes (second-last = WIN, last = LOSE). The rest are held: cell 1 =
CATCH (0–0.09 s), cell 2 = SETTLE (0.09–0.18 s), cells 3+ = STRAIN, alternating 12×/s until `LOCK_DUR 1.15`.
Strain needs at least two different drawings, or the lock is a still frame for a second.

### R-WALLTHROW · `wallthrow1..6` · throw from the wall cling (`:13698`)
0.45 s split evenly over the slots (6 slots → 75 ms each). The repeated wind-up at the start is an
acceptable anticipation hold. The three-slot freeze in the middle is not: replace slots 4 and 5 with the
release follow-through and the recoil.

### R-ATTACK · Light, then Medium: spacing audit, 0–2 redraws per row
Most attack rows need **re-timing, not new drawings**. Per row, in this order:
1. Read the live pacing: moves with `strikeWindows` are paced by the hitbox through
   `rosterAttackFrame`/`ROSTER_CONTACT_POSES` (`:12527`); the rest use `ANIM_TRACKS` (`:12403`) or
   `ATTACK_EXPOSURES_8` (`:12396`). **A track only applies when its length equals the row's cell count**
   (`attackCellIndex` `:12500`). Check that before you trust an existing one.
2. Look at the 8 cells at native size, in motion. Redraw ONLY:
   - the cell on the cut, as ONE directional smear that follows the real hand/weapon path, if no cell bridges the cut;
   - a follow-through cell that overshoots past the contact, if the row snaps straight back to guard.
3. Author the exposure: bunch cells near the coil and the settle, flash through the cut. Set it as a
   track or through `ROSTER_CONTACT_POSES`. Art changes do not authorize combat or hitbox changes.

### CHECK items: repeated cells inside attack/move rows
A repeated cell inside a move row is either a deliberate hold (e.g. the contact pose) or a missing
drawing. Decide per row: if the repeated cell IS the contact/hold pose, move the hold into the row's
exposure (track) and leave the art. If not, draw the missing beat. Never leave a silent repeat.

---

## 2. Per fighter. Owner order, Sep 23: Mizu → Shin → Mokurai → Exile first

"now →" lists the cells each key points at today, and which row those cells were borrowed from.

### MIZU. Air-hurt DONE (871).

| ID | row | draw | now → | note |
|---|---|---|---|---|
| MIZ-1 | R-LAND `land1..3` | 3 | 86, 89 (getup), 69 (xidle) | the bo must stay its full length in every beat. Measure staff px against idle |
| MIZ-2 | R-TURN `turn1` | 1 | 239 (taunt) | staff vertical, close to the body |
| MIZ-3 | R-SKID `skid1..2` | 2 | 36, 35 (roll_) | staff tip trails forward |
| MIZ-4 | R-JSQUAT `jsquat1..2` | 2 | jsquat1 = 228 (her launch cell); **no `jsquat2` key**, so add it | |
| MIZ-5 | R-WALK `walk1..8` | 8 | none | `prompts/mizu.md` Row A |
| MIZ-6 | R-JFLIGHT `jflight4` | 1 | [228,229,230,**229**,231,232] | the apex reuses the rise cell |
| MIZ-7 | R-DIVE `dive5,6` | 2 | [198,199,243,244,**244,244**] | |
| MIZ-8 | R-LOCK `lock2..4` | 3 | [17,**17,17,17**,11,19] | catch, settle and strain are all cell 17 |
| MIZ-9 | R-NJUMP `njump1..8` | 8 | none | brief §4.5: the staff is the axis |
| MIZ-10 | R-ATTACK `light`, `medium` | 0–2 each | | she has one track (`reed`) |
| MIZ-11 | CHECK | ? | heavy_i [182,183,233,233,233,187,188,189] · bothrust [190,191,191,193,193,195,197] · special [166,167,168,169,170,171,171,173] · staffspin [182,183,194,194,187,188,189] · aneu [198…203,205,205] | heavy_i and staffspin share 182/183/187–189 |


### SHIN. Air-hurt DONE (872).

| ID | row | draw | now → | note |
|---|---|---|---|---|
| SHN-1 | R-LAND | 3 | 304 (ajump), 300 (jflight3), 341 (crouch_/xidle) | ONE eye |
| SHN-2 | R-TURN | 1 | 399 (intro) | bare hands; wire coiled at the wrist |
| SHN-3 | R-SKID | 2 | 310, 309 (roll_) | widest cell on the roster (520×370), low stance |
| SHN-4 | R-JSQUAT | 2 | jsquat1 = 298 (launch cell); add `jsquat2` | |
| SHN-5 | R-WALK | 8 | none | `prompts/shin.md` Row A |
| SHN-6 | R-JFLIGHT `jflight6` | 1 | [298,301,300,302,303,**303**] | fast fall missing |
| SHN-7 | R-DIVE `dive2,5,6` | 3 | [150,**150**,436,437,**437,437**] | |
| SHN-8 | R-WALLTHROW `wallthrow4,5` | 2 | [378,378,379,**379,379**,333] | shuriken release, then recoil |
| SHN-9 | `roll_4` | 1 | [305,306,307,**306**,309,310] | the roll steps BACK a frame mid-rotation; draw the missing angle |
| SHN-10 | R-NJUMP | 8 | none | brief §4.2: fastest, lowest, barely a ball |
| SHN-11 | R-ATTACK `light`, `medium` | 0–2 each | | no tracks |
| SHN-12 | CHECK | ? | sparry [282,283,284,284,286,287,288,289] | |


### MOKURAI. Has NO transition keys; his run is `brun1..8`.
`run_clean1..8` are not on his sheet. `runCells` uses `brun`, so the skid refs are his brun board.

| ID | row | draw | now → | note |
|---|---|---|---|---|
| MOK-1 | R-AIRHURT `airhurt1..8` | 8 | 180, 181, 183 (grabbed; 183 also mroll) | same shape as the two pilots |
| MOK-2 | R-LAND | 3 | key missing | serene: the smallest squash on the roster; beads swing |
| MOK-3 | R-TURN | 1 | key missing | bare bead-wrapped fists, NO staff |
| MOK-4 | R-SKID | 2 | key missing | ref: brun board |
| MOK-5 | R-JSQUAT | 2 | key missing | |
| MOK-6 | R-WALK | 8 | none | `prompts/mokurai.md` Row A |
| MOK-7 | R-JFLIGHT `jflight2,4,6` | 3 | [291,**291**,292,**292**,293,**293**] | 3 drawings stretched over 6 bands |
| MOK-8 | R-DIVE `dive5,6` | 2 | [234,235,405,404,**404,404**] | |
| MOK-9 | R-NJUMP | 8 | none | brief §4.7: the only serene rotation |
| MOK-10 | R-ATTACK `light`, `medium` | 0–2 each | | no tracks |
| MOK-11 | CHECK | ? | bair [234,234,235,236,236,238,238,238] · bheavy [335,339,340,340,341] · bspec [356,357,358,360,356] · mhammer [202,203,205,205,206] · mblock [356,357,357,358,359,360,361,356] · getup [367,367,368,368,369,369,370,370] · gsup […,245,245,…] · kpush [378,372…377,378] · crouch_ [98,99,99,99] | `mroll` [99,369,368,183,368,369,100,101] is a roll built from getup, grabbed and crouch cells, so a real drawn roll (8) is the likely answer. Ask him. |
| MOK-✗ | `mwall1..8` | **0 — skip** | all 8 slots = cell 387 | zero engine references. Unreachable, so do not draw it. |


### EXILE. Has NO transition keys.

| ID | row | draw | now → | note |
|---|---|---|---|---|
| EXL-1 | R-AIRHURT | 8 | 179, 180, 183 (grabbed) | the chain stays one connected piece in every beat (keyer: one component) |
| EXL-2 | R-LAND | 3 | key missing | the ball lands AFTER her body, one beat late |
| EXL-3 | R-TURN | 1 | key missing | red iris `#B94828`; ball drawn in close |
| EXL-4 | R-SKID | 2 | key missing | ball swinging forward past her |
| EXL-5 | R-JSQUAT | 2 | key missing | |
| EXL-6 | R-WALK | 8 | none | `prompts/exile.md` Row A |
| EXL-7 | R-JFLIGHT `jflight4,6` | 2 | [346,347,348,**348**,349,**349**] | |
| EXL-8 | R-DIVE `dive5,6` | 2 | [425,423,422,424,**424,424**] | |
| EXL-9 | R-LOCK `lock2..4` | 3 | [339,**339,339,339**,336,343] | |
| EXL-10 | R-WALLTHROW `wallthrow4,5` | 2 | [412,412,413,**413,413**,312] | |
| EXL-11 | R-NJUMP | 8 | none | brief §4.8. ⛔ `finishGrapple()` also sets `flipTimer`, so her chain swing-around would play the curl too. That is an owner call (`ENGINE-CONTRACT.md`). |
| EXL-12 | R-ATTACK `light`, `medium` | 0–2 each | | no tracks |
| EXL-13 | CHECK | ? | xgrap [377…384,**383,384**] (10 slots) | probably a reel loop; confirm |


---

## 3. The final four: HOLD until he releases each one

Owner, Sep 23: Tsubasa, Ember and the Executioner may be redesigned, and Kael gets a new move set
(Light = short blade, Medium = long blade, Heavy and specials = both). **Draw nothing here yet.** When he
releases a fighter, recheck the latest approved refs and re-run `inventory.py`. The owed list today, so
the size of the job is known:

| fighter | owed now (drawings) | borrowed today |
|---|---|---|
| Tsubasa | airhurt 8 · land 3 · turn 1 · skid 2 · jsquat 2 · walk 8 · njump 8 (§4.1) · dive5,6 2 = **34** | airhurt [363,363,294] grabbed; land 23 crouch_/347 jflight/53 xidle; turn 466 intro; skid 244/245 roll_; jsquat 21/22 crouch_ |
| Ember | airhurt 8 · land 3 · turn 1 · skid 2 · jsquat 2 · walk 8 · njump 8 (§4.3) · jflight6 1 · dive2,5,6 3 = **36** | jsquat1 = jsquat2 = 432 (same cell); land 438/439 jmp + 505 idle; turn 392 taunt; skid 198, 68 |
| Executioner | airhurt 8 · land 3 · turn 1 · skid 2 · jsquat 2 · walk 8 · njump 8 (§4.6, he pikes) · jflight4,6 2 · dive5,6 2 = **36** | land 522/523 ajump + 455 xidle; turn 580 intro; skid 213/214 crouch_; jsquat 518 launch cell |
| Kael | airhurt 8 · land 3 · turn 1 · skid 2 · jsquat 2 · walk 8 · njump 8 (§4.4) · dive5,6 2 · lock strain 1 = **35**, and ALL attack rows wait for the new move set | airhurt [161,161,162]; land 304/300 jflight + 103 xidle; turn 318 taunt; skid 21/20 crouch_. His `ANIM_TRACKS` are 5–6 long and his rows are 8 cells: see R-ATTACK step 1 |


CHECK items for later: Tsubasa eflick [181,85,86,87,182,181], grabbed; Ember eafwd [304,360,355,355,…], grabbed;
Executioner kpush [97,238,239,341,341,341,103,104]; Kael kcross [194,196,196,197,198,200,200,201].
Executioner `lock` alternates 462/463 on purpose (strain vibration). It is fine, so leave it.

---

## 4. Owner calls: do NOT draw these without his yes

Two rows that play the same drawings (two moves, one piece of art). Each is his decision, not a gap.
Ask once, per fighter, when that fighter comes up:
Shin `sneu`=`special` · Mokurai `mblast`=`special` · Exile `glback`=`gsback` · Tsubasa `gsfwd`=`srush`,
`lowtanto`=`tendon`, `taunt`=`taunta` · Ember `chook`=`ehook`, `run`=`run_clean` · Executioner `xkiriage`=`xrise`.

Not a drawing: **`ajump`**. The engine reads only `ajump4`, as a fallback air pose (`:13280`), so
`ajump`=`jflight` costs nothing on screen. Skip it.

---

## 5. Totals and the queue

| fighter | drawings owed | status |
|---|---|---|
| Mizu | 30 + attack redraws + CHECK | first four |
| Shin | 31 + attack redraws + CHECK | first four |
| Mokurai | 37 + attack redraws + CHECK (+8 if he wants a real `mroll`) | first four |
| Exile | 41 + attack redraws + CHECK | first four |
| Tsubasa / Ember / Executioner / Kael | 34 / 36 / 36 / 35 | HOLD |


Queue for the first four. Row-major, like the air-hurt pilots, so each row's prompt style stays consistent
across fighters. One item per owner yes:

1. MOK-1, EXL-1: air-hurt (finishes that row on the first four)
2. land: MIZ-1 → SHN-1 → MOK-2 → EXL-2 (seen on every jump)
3. turn: MIZ-2 → SHN-2 → MOK-3 → EXL-3 (every crossup)
4. skid: MIZ-3 → SHN-3 → MOK-4 → EXL-4 (every run release)
5. jump squat: MIZ-4 → SHN-4 → MOK-5 → EXL-5
6. walk: MIZ-5 → SHN-5 → MOK-6 → EXL-6
7. air repeats: jflight, dive, lock, wallthrow, roll (MIZ-6..8, SHN-6..9, MOK-7..8, EXL-7..10)
8. R-ATTACK Light, then Medium, per fighter; CHECK items alongside
9. njump (Blender + his motion lane, then the `drawnFlip` gate)
10. idle: only if he asks
