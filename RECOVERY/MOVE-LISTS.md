# SHADOWCLASH — EVERY FIGHTER'S MOVE LIST

Built from what the BUTTONS actually do — engine wiring traced per fighter, then every
claimed frame row re-checked against the shipped sheet. SHEET_V 619, 2026-08-24.

**Art status column:** `DRAWN` = its own cells · `ALIAS` = shares another row's cells ·
`FALLBACK` = no row of its own, engine draws something generic · `MISSING` = nothing draws.

---

## COVERAGE AT A GLANCE

| fighter | moves mapped | drawn | alias | fallback | missing |
|---|---|---|---|---|---|
| **Kael** | 46 | 29 | 4 | 6 | 7 |
| **Tsubasa** | 53 | 40 | 5 | 7 | 1 |
| **Shin** | 63 | 33 | 10 | 15 | 5 |
| **Ember** | 45 | 29 | 8 | 6 | 2 |
| **Mizu** | 54 | 35 | 9 | 5 | 5 |
| **THE EXECUTIONER** | 40 | 22 | 9 | 8 | 1 |
| **Exile** | 48 | 31 | 12 | 0 | 5 |
| **Mokurai** | 62 | 46 | 12 | 3 | 1 |
| **Oni** | 61 | 23 | 32 | 2 | 7 |

---

## THE CONTROLS

| button | P1 · P2 | what it does |
|---|---|---|
| **Jump / Up** | P1 W · P2 ArrowUp · pad d-pad 12 / stick up · touch pad 'up' | executeJump() on keydown (fireCombatKey L16081/16097). |
| **Left / Right (walk)** | P1 A/D · P2 ArrowLeft/ArrowRight · pad 14/15 · touch pad slide | NOT combat keys — read out of keys[] every frame by getInputAxis() (L2350). |
| **Down / Crouch** | P1 S · P2 ArrowDown · pad 13 · touch pad 'down' | isDownPressed() L2686. Hold on the ground = STATE.CROUCH (L3643-3651, crouchAt stamped on entry only). |
| **Light attack** | P1 F · P2 I · pad face 0 · mouse LMB · hand ✊ | executeAttack(STATE.ATTACK_LIGHT) L16082/16098. |
| **Heavy attack** | P1 G · P2 O · pad face 2 · mouse RMB · hand ✌ | Dispatch order at L16088-16090 is load-bearing: executeReprisal() first (fresh-block riposte), THEN isDefendHeld()+executeShadowSlip(), THEN executeAttack(ATTACK_HEAVY). |
| **Special** | P1 H · P2 P · pad face 3 · mouse wheel · hand ☝ | L16091-16092: Guard-held + Special = castBunshin() (30 chakra shadow clone) and RETURNS; otherwise executeAttack(ATTACK_SPECIAL). |
| **Poof / Kawarimi / GUARD** | P1 C · P2 M · pad 1, 4 or 5 (shoulder = block) · hand 🤏 | ONE key, three jobs. TAP = executeKawarimi() (L16093/16104). |
| **Mode / 2nd form (V)** | P1 V · P2 K · pad 8 | L16051-16054. In gameMode 'teams' V/K are teamSwap(1)/teamSwap(2) instead. |
| **Throw macro** | L+H within 90ms (F+G / I+O) · pad trigger 6 or 7 | L16019-16026: each attack key stamps _lt/_ht; if the partner stamp is <90ms old, executeThrow() and return. |
| **Escape** | Escape | L15915 setPaused toggle; during a cutscene it ends the cutscene (L15909), any other key advances a beat. |
| **F9 / F7** | F9, F7 | F9 flips the attack-FEEL preset punchy<->grounded (L15917). |
| **Training-only hotkeys** | R, T, L, B | L16029-16044, gated on gameMode==='training' and they RETURN before combat dispatch. |
| **Gamepad (standard mapping only)** | PAD_KEYS / PAD_BUTTONS L16249-16266 | Pad 0 -> P1 codes, pad 1 -> P2 codes. |
| **Touch** | TOUCH_CODE L16175 + bindPad L16184 | Combat buttons map to the same key codes and go through pressCombat. |

### The directional-light law (why fwd/back/down+Light differ per fighter)

THE KICK MAP (L5119-5136, inside executeAttack): `const kick = this.isDownPressed() ? 'sweep' : axis === this.facing ? 'push' : axis === -this.facing ? 'heel' : null;` then `const drew = { sweep: 'gldown', push: 'glfwd', heel: 'glback' }[kick];` — the kick fires ONLY if `kick && !(drew && kman.ready && kman.frames[drew+'1'] !== undefined)`. So: THE COMMAND-KICK TIER IS THE UNARMED DEFAULT FOR A DIRECTION NOBODY DREW, NOT A CLAIM ON THE INPUT. A fighter whose sheet carries the gl* row keeps the input and executeAttack falls through to the normal light path, where dirCells (L11367) resolves { fwd:'glfwd', back:'glback', down:'gldown', up:'glup', neutral:'glneu' }. ⛔ 'up' IS NOT IN THE KICK MAP — that is exactly why glup always worked while the other three never did: the input was taken, not the art missing. Other gates on the same block: grounded only, chainComboTier === 0, recoveryTimer <= 0, and NOT (spec.id===2 && kageNui) — a fighter who drew the whole tier keeps all of it, and without that gate Shin's Form-2 Light executed a generic sweep while his stance router drew the Ankle Poke over it. Tsubasa's sakate has the same shape and the same missing gl* rows and is still hijacked (known, not fixed). executeKick (L6645) sets state=ATTACK_LIGHT, kickKind, KICK_MS 140, startup = 140ms * FRAME_DATA.light.startup (~45ms — kicks are no longer exempt from the strike-frame gate), recovery from RECOVERY_TAX[id] ?? curSpeed/6, and spawns NO slash (unarmed, no blade crescent). Boxes: sweep {low, trip}, push {wallsplat} + puntLogs(), heel {behind}. 0 chakra, work while winded, build only 5 stagger, never advance the chain. THE DRAW SIDE (L11152-11209, inside case STATE.ATTACK_LIGHT, above the gl* dirCells call): mokurai bksweep/bkheel/bkfront (cracked: arake/spurn/bheel pairs) -> exile xksweep/xkpush/xkheel (slide cells doing double duty) -> kpush1..3 multi-frame if packed -> `const kc = F['k' + p.kickKind]` — the string-built lookup, resolving to the BARE keys ksweep / kpush / kheel -> final fallback `F.kstomp ?? F.jump2 ?? F.fall ?? F.light1` (a LEG pose, never the sword light chain: an unarmed kick must not brandish a weapon). WHO CARRIES gl* ROWS (measured from web/assets/sprites/*.json, SHEET_V 619): EXECUTIONER — glfwd 8, glback 8, gldown 8, glup 8 (the only full set; no glneu). ONI — glneu 2, glfwd 6, glback 10 (NO gldown, NO glup — the L5124 comment claiming his board draws gldown is stale against oni.json, so his Down+Light is still the generic sweep kick). KAEL — glup 6 only. NOBODY ELSE: ember, exile, mizu, mokurai, shin, tsubasa have zero gl* rows and take the kick tier on fwd/back/down. Multi-frame kick art (k*1..N): ember ksweep/kpush/kheel 6 each, kael ksweep 6 / kpush 3 / kheel 6, mizu kpush 3, shin kpush 3, tsubasa kpush 4 — everyone else has only the single bare cells or nothing.

### Universal systems

| system | input | how it works |
|---|---|---|
| **Direction capture (the law every slot depends on)** | heldDir(p) at press time | L1782: down > up > fwd/back off getInputAxis() vs facing; null = neutral. |
| **Chain / buffer** | any attack key during recovery | chainComboTier 0 during recovery>0.05 with no connect = buffered {type, dir, ttl 0.133} and RETURN, touching nothing (L4720). |
| **Dodge roll** | HOLD Guard + TAP a direction (one press) · or HOLD Down + double-tap the same direction within 250ms | Both routes live in the keydown handler (L15959-15979), not fireCombatKey, because movement keys aren't combat triggers. |
| **Shunshin dash** | double-tap Left or Right within DOUBLE_TAP_MS (250) | executeShunshin L8734. 15 chakra, DASH_SPEED 800 for DASH_TIME 0.15. |
| **Guard / chip** | HOLD Poof (C / M) | STATE.BLOCKING at L3604-3616; blockRaiseAt stamped on TRANSITION only. |
| **Kawarimi / substitution** | TAP Poof · tap again mid-vanish to rig the log (+25) | executeKawarimi L8985, 35 chakra, leaves a LOG decoy (LOG_LIFE 2.0). |
| **Throw + THROWN** | Light+Heavy within 90ms, close range | executeThrow L8773. THROW_RANGE 55 centre-to-centre, THROW_TIME 0.38, release at 0.56 of the arc, THROW_DMG 12 untechable. |
| **Blade lock (STATE.BLADE_LOCK, lock1..N)** | automatic on a bind; MASH Light or Heavy to win | processWeaponClash L17087: bindPair = weaponBind both ways (steel/iron/WOOD — owner Aug 12 'include wood, mizu bind'; flesh/mail/chain cannot) and clashCd<=0 -> enterBladeLock L17042. |
| **KIAI clash (this.lock, the OTHER lock) — DEAD CODE** | n/a | enterKiai L4512 (KIAI_TIME 1.0, draws STATE.BLOCKING) fires at L17151 on steelPair. |
| **Weapon clash / recoil** | automatic | Two active canClash boxes overlapping. |
| **Parry / deflect** | per-fighter, no universal button | STATE.PARRY_STANCE. Kael: Back+Heavy low parry (klowp1..3), Up+Heavy high parry (khigh1..3), Back+Special cross parry — all with NO hitbox on purpose. |
| **Meteor Break / dive** | air Down + Heavy (S+G held in the air) | L6522 -> startSlam(). Roster-wide. |
| **Zero-G Cut / Air Up-Poke** | neutral air Light · Up + air Light | L6111-6134. Neutral air Light suspends gravity for the swing (AIRLIGHT_FLOATS_MAX 2 per airtime, vy clamped to 40). |
| **Light strings** | grounded neutral/fwd/back + Light, repeated inside 0.55s | L6145-6158. stringStep walks lightBeats(this) while stringT>0, else resets to beat 0. |
| **Wall cling / wall slide / wall run** | airborne + HOLD the direction INTO the wall; UP held = wall run; Jump = wall jump | L4113: wallDir set only when !isGrounded && stunTimer<=0 && inputAxis === atWall. |
| **Mode 2 / stance switch** | V (P1) / K (P2), optionally with a direction held | modeKey L2727. Gate: grounded, not stunned, not attacking, not vanished, not grabbed. |
| **Hit-confirm windows (no teleport off a confirm)** | n/a — set by a landed hit | attacker.hitConfirmed = true at L9113 and is cleared by a substitution (L9286) so a vanished defender never pays a Skullgirls cancel. |
| **Input funnels** | n/a | ONE path: keydown -> pressCombat(code, e.repeat) -> fireCombatKey(code, t, repeat). |

---

## KAEL

**Starter / All-Round** · S/P/R/D **6/6/6/6** · he/him  
**Weapon:** Short & Long Sword — one SHORT + one LONG blade, difference obvious at a glance (Story Bible owner corrective 2026-07-31). kael.json calls it "Katana & Wakizashi / Tantō". WEAPON_FX[5] = 'cross' (L1320).  
**Discipline:** Niten Ichi-ryū / Ryōtōjutsu (long + short sword) — simultaneous parry-and-strike, Musashi two-blade coordination. kael.json martial_art_discipline: "Niten Ichi-ryū & Tantōjutsu".  
**Second form:** CHUDAN STANCE — bare V (P1) / K (P2). modeKey() L2726: the four roster-wide V+direction stances are read first, then id 7/2/3/1 branches, then the chudan fall-through at L2766, which gates on `frames.idle_chudan !== undefined`. Kael HAS idle_chudan, so V toggles chudan for him. Effect (roster-wide, not id-gated): CHUDAN_DMG 1.28 and CHUDAN_REACH 1.18 applied to ATTACK_HEAVY and ATTACK_SPECIAL hitboxes only (L6742-6748), and the BLOCKING branch is gated `&& !this.chudan` (L3605) so guard is genuinely unreachable while it is set. Taking chudan clears muki (L2774). ⛔ ZERO VISUAL CHANGE FOR HIM: the two chudan draw branches (xcentry entry L12308, idle_chudan hold L12317) sit BELOW the six-frame xidle1 breathing-idle branch at L12280, which returns first for any sheet carrying xidle1 — and Kael's does. His stance art never reaches the screen. He is also missing from the in-game training move list for V: MOVES_LIST['Kael'] (L16781) has no CHUDAN line, while the Executioner's entry does.  

| input | move | frame row | beats | art |
|---|---|---|---|---|
| Light (F / I) — neutral, grounded | Dual Slash Combo | `kdual1..6` | 6 | DRAWN |
| Fwd+Light (grounded, chain tier 0) | Push Kick / Teep | `kpush1..3` | 3 | DRAWN |
| Back+Light (grounded, chain tier 0) | Heel Kick (hits BEHIND) | none reached — engine reads bare F.kheel (L11203); his sheet packs kheel1..6 |  | MISSING |
| Down+Light (grounded, chain tier 0) | Sweep Kick (low, trips) | none reached — engine reads bare F.ksweep (L11203); his sheet packs ksweep1..6 |  | MISSING |
| Up+Light (grounded) | Rising Light Cut | `glup1..6` | 6 | DRAWN |
| air Light — neutral | Air Slash | `aneu1..6` | 6 | DRAWN |
| air Fwd+Light | Air Forward Slash | `afwd1..6` | 6 | DRAWN |
| air Back+Light | Air Reverse Slash | `aback1..6` | 6 | DRAWN |
| air Down+Light | Air Down Slash | `aneu1..6` | 6 | ALIAS |
| air Up+Light | Air Up-Poke | none reached — L11221 F.upatk3 ?? F.air2 ?? F.light3 ?? F.light1, all four undefined |  | MISSING |
| Heavy (G / O) — neutral, grounded | Cross Slash | `kcross1..6` | 6 | DRAWN |
| Fwd+Heavy (grounded) | TWIN CYCLONE | `kcyc1..6` | 6 | DRAWN |
| Back+Heavy (grounded) | LOW PARRY | `klowp1..3` | 3 | DRAWN |
| — Back+Heavy parry CATCHES | Low Parry Counter | `klowp4, klowp4, klowp5, klowp6` | 3 | DRAWN |
| Up+Heavy | HIGH PARRY | `khigh1..3` | 3 | DRAWN |
| — Up+Heavy parry CATCHES | High Parry Counter | `khigh4, khigh4, khigh5, khigh6` | 3 | DRAWN |
| Down+Heavy (grounded) | LOW-HIGH SCISSOR | `kscis1..6` | 6 | DRAWN |
| air Heavy — neutral / fwd / back / up | JUMPING X-CUT | `kxcut1..6` | 6 | DRAWN |
| air Down+Heavy | METEOR BREAK (roster-wide plunge) | none reached — L11556 if (p.slamPhase) return F.kstomp ?? F.fall2 ?? F.fall;, all undefined |  | MISSING |
| Special (H / P) — neutral | SPINNING FINISHER (Spinning Dual Slice) | `kspin1..6` | 6 | DRAWN |
| Fwd+Special (grounded) | TRAVELLING CROSS SLASH | `ktrav1..6` | 6 | DRAWN |
| Up+Special | SKYWARD FANG | `kfang1..6` | 6 | DRAWN |
| Down+Special (grounded) | RISING TWIN FANG | `krise2..6` | 5 | DRAWN |
| Back+Special (grounded) | NITEN PARRY | `xparry1..6` | 6 | DRAWN |
| — Back+Special parry CATCHES | Niten Counter (katana answers) | `xparry5, xparry5, xparry6` | 2 | DRAWN |
| air Special — neutral | Air Spinning Slice | `sneu1..6` | 6 | DRAWN |
| air Fwd / Back / Down + Special | Air Spinning Finisher (borrowed pose) | `kxcut1..6` | 6 | ALIAS |
| HOLD Poof (C / M, or pad shoulder) | Guard | `block / block2` | 2 | DRAWN |
| TAP Poof (C / M) | Kawarimi (substitution) | — (vanish + log FX, no fighter cell) |  | FALLBACK |
| Guard + direction | Dodge Roll | `roll_1..6` | 6 | DRAWN |
| Guard + Special (C+H / M+P) | BUNSHIN — sprint feint (30 chakra) | clone drawn from run_clean1..4 |  | ALIAS |
| Hold Down (grounded) | Crouch | `crouch_1..4` | 4 | DRAWN |
| Jump / Up (W / ArrowUp / pad 12) | Jump arc | `ajump1..6` | 6 | DRAWN |
| Left / Right (walk & run) | Run cycle | `run_clean1..8` | 8 | DRAWN |
| Double-tap direction | Dash | run_clean1..8 (no dash row) |  | ALIAS |
| Jump into a wall | Wall cling / slide | none reached — L11001 F.wallslide ?? F.fall; his row is wallslide1..5 |  | MISSING |
| Light+Heavy within 90ms (F+G / I+O, or pad trigger) | Throw | none reached — L11998 attackBodyCells(F) is null, ?? [F.heavy_i1, F.heavy_i3] both undefined |  | MISSING |
| (being thrown) | Grabbed tumble | `grabbed1..8` | 8 | DRAWN |
| (taking a hit) | Hitstun | `hurt, hurt2, hurt3` | 3 | DRAWN |
| (clash into a bind) | Blade lock | F.block (static hold) |  | FALLBACK |
| (neutral) | Idle | xidle1..6 (ping-pong 1-2-3-4-5-6-5-4-3-2) |  | DRAWN |
| V (P2: K), no direction held | CHUDAN STANCE (his mode 2) | xcentry1..6 + idle_chudan — packed, both shadowed by xidle1 |  | MISSING |
| V + Up | MUKI-KAMAE | — (no art, FX only) |  | FALLBACK |
| V + Down | SAYA / GYAKUTE grip flip | — (no art, spark FX) |  | FALLBACK |
| V + Back | KAGE-KAMI (delayed shadow) | — (clone replay, no new cells) |  | FALLBACK |
| V + Fwd | WEAVE ANCHOR | — (smoke puff, no cells) |  | FALLBACK |

**Signature:** NITEN PARRY (Back+Special) — the wakizashi catches, the katana answers; xparry1..6 into the xparry5/5/6 riposte · RISING TWIN FANG (Down+Special) — the game's first true reversal: 0.25s invuln startup, launches for a juggle, brutally punishable on whiff · TWIN CYCLONE (Fwd+Heavy) — two rings thrown on the way in, two hitboxes at 70 and 120 push · LOW-HIGH SCISSOR (Down+Heavy) — a low that must be blocked low, then the second blade back up through the same line, launchVy -300 · TRAVELLING CROSS SLASH (Fwd+Special) — covers ~2x the cyclone's ground and pays it off in one committed cut · SKYWARD FANG (Up+Special) — both blades driven straight up, FEET PLANTED; the patient anti-air, deliberately not a second reversal · HIGH / LOW PARRY (Up+Heavy / Back+Heavy) — with the Niten cross catch these are the three parries his own sheet draws, each on its own input, none with a hitbox

**Dead or missing:**

- `ko1..6 (6 cells)` — No code anywhere in web/index.html reads F.ko1..F.ko6 — grepped for the literal keys and for every string-built lookup form (`F['...' + i]`). The only 'ko' hits in the file are the sfx('ko') calls and koTimer/koFocus camera vars. Six packed cells, zero readers.
- `aup1..6 (6 cells)` — The substring 'aup' appears on exactly one line of the engine (the SHEET_V 619 comment block). No draw branch reads the row. Air Up+Light — the input this row is named for — dead-ends at L11221 on `F.upatk3 ?? F.air2 ?? F.light3 ?? F.light1` and falls back to F.idle.
- `adown1..6 (6 cells)` — The only reader is L11274, gated `p.spec.id === 8` (Oni). Kael's air Down+Light falls through to aneu1..6 instead. The generic line below it (L11279) needs `F.kstomp`, which he does not have either.
- `kheel1..6 (6 cells)` — The kick draw path reads a BARE key: `const kc = F['k' + p.kickKind]` (L11203) → F.kheel, which is undefined because the row is packed as kheel1..6. Only 'push' has a multi-cell special-case (L11201). Back+Light therefore draws F.idle.
- `ksweep1..6 (6 cells)` — Same defect as kheel — L11203 looks up bare F.ksweep. Down+Light draws F.idle. Fixing both is one line beside the existing kpush case; the row-collect helper already exists (dirCells / the `for (let i = 1; F[k+i] ...)` pattern).
- `wallslide1..5 (5 cells)` — STATE.WALL_CLING ends `return F.wallslide ?? F.fall;` (L11001) — a bare key. His row is wallslide1..5 and he has no `fall`, so every wall cling draws F.idle. Wall cling is roster-wide (assigned in applyPhysics L3743), so this is a state he really reaches.
- `xcslice1..6, xctsuki1..6, xcthrust1..6, xcuph1..6, xcfwdh1..6, xcdownh1..6 (36 cells)` — Every reader of these six rows is gated `p.spec.id === 0` (the Executioner) — L11143, L11604, L11482, L11751, L11742, L10361. They are Executioner chudan/stance art sitting on Kael's sheet with no input on any of his branches that can reach them.
- `xcentry1..6 + idle_chudan + idle_chudan2 (8 cells)` — Branch-order shadow. The six-frame xidle1 breathing-idle loop returns at L12280; the chudan entry (L12308) and chudan hold (L12317) are BELOW it and are only reached by a sheet with no xidle1. Kael has xidle1, so his mode-2 stance is mechanically live but visually identical to his normal idle. idle_chudan is still load-bearing — its mere presence is what lets V toggle chudan for him at L2766.
- `idle2 (1 cell)` — Same shadow: the `tick % 5 === 4 ? F.idle2 : F.idle` line (L12336) sits below the xidle1 return at L12280. Never drawn.
- `krise1 (1 cell)` — Packed but never exposed — L11863 plays [krise2, krise3, krise4, krise5, krise6], skipping beat 1 of the row.
- `INPUT with no art: Back+Light (Heel Kick)` — Hitbox and { behind: true } fire; the picture is his standing idle. See kheel1..6.
- `INPUT with no art: Down+Light (Sweep Kick)` — Box { low, trip } fires; the picture is his standing idle. See ksweep1..6.
- `INPUT with no art: air Up+Light (Air Up-Poke)` — Launcher box (34x62, launchVy -380) fires and airUpAnim is set at L6118, but L11221 returns undefined → F.idle. He hangs in a planted standing pose mid-air.
- `INPUT with no art: air Down+Heavy (METEOR BREAK)` — L11556 `if (p.slamPhase) return F.kstomp ?? F.fall2 ?? F.fall;` — all three undefined. Both the hang and the plunge draw F.idle; only the post-landing recovery falls through to kcross. Meteor Break is roster-wide and is listed on his own training move list ('air Down+G — Meteor Break').
- `INPUT with no art: Throw (Light+Heavy within 90ms)` — L11998: `attackBodyCells(F)` returns null (no attack_body1) and the `?? (F.heavy1 !== undefined ? [heavy1, heavy2] : [heavy_i1, heavy_i3])` tail is undefined on both sides. The whole THROW_TIME draws F.idle while the opponent plays their grabbed1..8 tumble.
- `INPUT with degraded art: Blade lock` — No lock1..N cells — draws a single static F.block by design (L10966). Not a bug, but it is a hole in the art, and it is roster-wide: nobody has lock cells.
- `INPUT with collapsed art: air Heavy fwd / back / up / neutral` — Four distinct inputs, one row. He packs no hfwd/hback/hup/hneu, so the air-direction dirCells at L11676 returns null and all four land on kxcut1..6. Air Fwd/Back/Down SPECIAL also alias onto the same row (L11846).

---

## TSUBASA

**Precision / Counter** · S/P/R/D **7/6/6/7** · he/him  
**Weapon:** Twin Daggers (Tantō) — `weapon_type: "Dual Tantō Knives"`, exactly TWO short silver knives, never full swords, never a hood  
**Discipline:** Tantōjutsu (Reverse-Grip) / Shoto Nitojutsu — "Rapid-fire twin knife combat using icepick grips combined with aerial acrobatics." Archetype: Precision / Counter (7/6/6/7). BLADES=2 (survives one Ghost-Killer disarm).  
**Second form:** SAKATE — "the Founder's Grip" (V for P1 / K for P2 → `toggleSakate()`, index.html L4191). Both tantō reverse to icepick grip. Buffs land once each: SAKATE_REACH 1.12, SAKATE_DMG 1.10, SAKATE_SPEED 1.10, gated `spec.id===3 && sakate`. THE TRADE: the Form-2 parry does NOT riposte — it MARKS the attacker for MARK_TIME 1.5s (`takeDamage` L9162), and Tsubasa's next hit on the mark forces `hasuji`/`hasujiHit` true and multiplies damage by MARK_DMG (L17322). One collect, only by the player who made the read. Sakate is a full moveset rewrite of the LIGHT and HEAVY tiers plus the parry; Specials keep Form-1 wiring entirely. It owns only two of the nine movement rows the shared `f2MovementFrame` router reads (f2_idle, f2_parry) — run/jump/roll/crouch/block/land/dash all fall back to Form 1 art.  

| input | move | frame row | beats | art |
|---|---|---|---|---|
| F (Light, neutral, grounded) | Alternating Dagger Chain | `light1..light5` | 5 | DRAWN |
| Fwd + F (grounded) | Push Kick (command-kick tier) | `kpush1..kpush3` | 3 | DRAWN |
| Back + F (grounded) | Heel Kick | `kheel` | 1 | DRAWN |
| Down + F (grounded) | Sweep Kick | `ksweep` | 1 | DRAWN |
| Up + F (grounded) | Standing light (no up-kick exists) | `light1..light5` | 5 | ALIAS |
| G (Heavy, neutral, grounded) | Double-Dagger Cross-Slash (X) | `heavy_i1..heavy_i5` | 5 | DRAWN |
| Fwd + G (grounded) | REVERSE-GRIP RUSH | `rgrush1..rgrush6` | 6 | DRAWN |
| Back + G (grounded) | EVASIVE FLICK | `eflick1..eflick6` | 6 | DRAWN |
| Down + G (grounded) | LOW TANTO | `lowtanto1..lowtanto6` | 6 | DRAWN |
| Up + G (grounded) | RISING TWIN SLASH | `ristwin1..ristwin6` | 6 | DRAWN |
| H (Special, neutral, grounded) | PARRY STANCE | `special1, special2` | 2 | DRAWN |
| Fwd + H (grounded, no Down/Up) | SWALLOW'S PASS (pass-through slash) | `special1..special7` | 7 | DRAWN |
| Back + H (grounded) | TANTO REVERSE FLURRY | attack_body1, attack_body3, attack_body4, attack_body5, attack_body6 |  | DRAWN |
| Down + H (grounded) | AERIAL DIVE CUT (grounded launch) | `divecut1..divecut6` | 6 | DRAWN |
| Up + H (grounded) | AIR-THROW SETUP | `airthrow1..airthrow6` | 6 | DRAWN |
| F + G within 90ms (throw macro; pad trigger 6/7) | Tantō Throw | `attack_body1..attack_body6` | 6 | ALIAS |
| Hold C + H | BUNSHIN — "the rising step" | (clone renders his own sprite) |  | FALLBACK |
| Hold C (guard) | Block | (resolves to F.block — UNDEFINED) |  | MISSING |
| Hold C + direction (or Down + double-tap) | Dodge Roll | `roll_1..roll_6` | 6 | DRAWN |
| Hold S / Down | Crouch | `crouch_1..crouch_4` | 4 | DRAWN |
| C (tap) | Kawarimi | (vanish, no cells) |  | FALLBACK |
| Double-tap direction (dash / shunshin) | Shunshin — traversal only in Form 1 | `run_clean1..run_clean8 / idle` | 8 | FALLBACK |
| W / ArrowUp (jump, double jump) | Acrobatic jump arc | `ajump1..ajump5` | 5 | DRAWN |
| (airborne, into a wall) | Wall Cling | `wallslide` | 1 | DRAWN |
| air F (neutral) | Air Slash | `air1..air3` | 3 | DRAWN |
| air Fwd + F | Air Forward Dagger | `afwd1..afwd6` | 6 | DRAWN |
| air Back + F | Air Reverse Cut | `aback1..aback6` | 6 | DRAWN |
| air Down + F | Air down poke | `kstomp` | 1 | FALLBACK |
| air Up + F | Air Up-Poke | `air2` | 1 | FALLBACK |
| air G (neutral) | Air Neutral Heavy | `hneu1..hneu6` | 6 | DRAWN |
| air Fwd + G | Air Lunge Thrust | `hfwd1..hfwd6` | 6 | DRAWN |
| air Back + G | Air Back Heavy | `hback1..hback6` | 6 | DRAWN |
| air Up + G | Air Up Heavy | `hup1..hup6` | 6 | DRAWN |
| air Down + G | METEOR BREAK | hdown2, hdown3 (of hdown1..6) |  | DRAWN |
| air H (neutral) | Air Neutral Special | `sneu1..sneu6` | 6 | DRAWN |
| air Fwd + H | Pass-Through Slash (air) | `sfwd1..sfwd6` | 6 | DRAWN |
| air Back + H | Air Back Special | `sback1..sback6` | 6 | DRAWN |
| air Up + H | Air Up Special | `sup1..sup6` | 6 | DRAWN |
| air Down + H | AERIAL DIVE CUT | `divecut1..divecut6` | 6 | DRAWN |
| V (P1) / K (P2) | SAKATE — the Founder's Grip (toggle) | `f2_idle_1..f2_idle_6` | 6 | DRAWN |
| [SAKATE] F neutral, beats 1/2/3 | BACKHAND RAKE → INWARD RIP → SCISSOR CUT | f2_light1_1..6 / f2_light2_1..6 / f2_light3_1..6 |  | DRAWN |
| [SAKATE] G neutral / Fwd / Back / Up, beats 1/2/3 | TURNING SLASH → DOUBLE DRIVE → THE ANSWER | f2_heavy1_1..6 / f2_heavy2_1..6 / f2_heavy3_1..6 |  | DRAWN |
| [SAKATE] Down + G (grounded) | HAMSTRING RAKE | `f2_clow_1..f2_clow_6` | 6 | DRAWN |
| [SAKATE] Fwd / Back / Down + F (grounded) | — kick tier hijack, no Sakate move exists — | executes kpush/kheel/ksweep, DRAWS f2_light{step} |  | ALIAS |
| [SAKATE] dash + F | THE DASH CUT | f2_dashcut_1..f2_dashcut_6 (fallback rgrush1..6) |  | DRAWN |
| [SAKATE] air G (not Down) | DIVE-PIERCE | f2_air_1..f2_air_6 (fallback divecut1..6) |  | DRAWN |
| [SAKATE] air Down + G | METEOR BREAK (art breaks) | executes startSlam, DRAWS f2_heavy{step} |  | ALIAS |
| [SAKATE] air F | Grounded knife string, played in the air | `f2_light1_/2_/3_` | 6 | ALIAS |
| [SAKATE] H neutral (grounded) | THE READ (parry that MARKS) | `f2_parry_1..f2_parry_6` | 6 | DRAWN |
| [SAKATE] Fwd/Back/Down/Up + H, all air specials, throw, roll, block, crouch, jump, run | — unchanged, Form 1 wiring — | (Form 1 rows) |  | FALLBACK |
| (being hit) | Hurt / Stunned | `hurt, hurt2, hurt3` | 3 | DRAWN |
| (being thrown) | Grabbed tumble | `grabbed1..grabbed8` | 8 | DRAWN |
| (blade lock) | Blade Lock struggle | `xblkguard` | 1 | FALLBACK |

**Signature:** SWALLOW'S PASS — Fwd+Special, grounded: blur THROUGH the opponent inside 260px, land at their back, re-face, 50x40 box. Out of range it is a committed 620px/s whiff lunge (L7345). · TANTO REVERSE FLURRY — Back+Special, grounded: four alternating rakes at 0.06/0.15/0.24/0.33s, the fourth launches (launchVy -200). recovery 0.46 (L7954). · PARRY STANCE — neutral Special, grounded: the roster's STRICTEST window, parryFlashTimer 0.133 (8f at 60fps). Whiff = 0.5s committal. Projectiles are REFLECTED; a caught melee hit teleports him behind and punishes for 20 with a 0.6s stun (L8059/L9136). · THE READ — the Sakate replacement for that parry: catch, mark, wait. No riposte, no stun; he only takes back his own frames (recovery 0.18). · THE ANSWER — Sakate heavy string beat 3: pierce + crescent follow-through, launch launchVy -440, and beat 4 of that row doubles as the mark's counter-KIME. · AERIAL DIVE CUT / AIR-THROW SETUP — the two Special directions the DIR_SPECIALS table exists for on this fighter ('3:down', '3:up').

**Dead or missing:**

- `tsprint1..tsprint8 (cells 242-249)` — The string `tsprint` appears ZERO times in web/index.html. Eight cells of a ninja-sprint cycle that no branch can reach — runCells() uses run_clean1..8, which is packed and wins.
- `aup1..aup6 (cells 303-308)` — `aup` appears nowhere in the engine. Air Up+Light draws the single shared cell air2 via the airUpAnim fallback chain. Commit 19209d0 (SHEET_V 609) states these are "empty rows the generic aerial dispatch already reads" — verified false.
- `adown1..adown6 (cells 297-302)` — The only `adown` reader is L11274, gated `p.spec.id === 8` (Oni). Tsubasa's air Down+Light is caught one line later by the roster-wide `return F.kstomp` at L11279. Six drawn cells replaced by one generic stomp pose.
- `wallslide1..wallslide6 (cells 309-314)` — STATE.WALL_CLING returns the single bare key `F.wallslide` (cell 312 = beat 4). The six-cell cycle is packed and keyed but has no reader — the channel note of Aug 23 05:54 says so explicitly ("cycle keys ready"). Needs a banded read like the JUMP/CROUCH cases.
- `block1 (cell 279) — and the entire held-guard pose` — ⛔ WORST HOLE. He is the ONLY one of the nine sheets keyed `block1`/`block2` instead of `block`/`block2` (checked all nine json files). STATE.BLOCKING at L12049 returns `F.block` for a held guard; that key does not exist, so the L10665 no-fighter-is-invisible wrapper substitutes `F.idle`. HOLDING GUARD DRAWS HIS IDLE STANCE. block2 only appears on the block-impact frame; block1 can never draw. One-line fix on the sheet (rename block1 -> block) or add the alias.
- `heavy1 / heavy2 / heavy3 (cells 11 / 13 / 15)` — Legacy aliases of heavy_i1 / heavy_i3 / heavy_i5. heavyCells() only reaches the `[F.heavy1 ?? F.light1, ...]` tail when heavy_i1 is undefined, and specialCells()'s `[F.heavy1, F.heavy2]` tail only when no special* row exists — he has both. Dead keys, not dead pixels.
- `kpush4 and the bare `kpush` key (both cell 150)` — The kick draw hard-lists `[F.kpush1, F.kpush2, F.kpush3]` at L11201 and returns, so kpush4 never plays and the bare `kpush` fallback (`F['k'+kickKind]`) is unreachable for the push kick. Cell 150 is also `kheel`, so his back heel kick and his 4th push-kick beat are the same drawing.
- `kneel (cell 149)` — Unreachable on this sheet. The CHIBI TAKEOFF SQUASH read at L11111 sits BELOW the ajump branch that returns unconditionally; STATE.CROUCH's `F.kneel ?? F.idle` tail sits below the crouch_1 branch; the landing read `if (p.landT > 0) return F.kneel` sits below `if (p.landT > 0 && F.crouch_3)`. Three call sites, all shadowed.
- `roll (bare, cell 252)` — Shadowed by roll_1..6 at L12143 and by the tumble read at L12183. Only reachable on a half-loaded sheet.
- `jump (287) / jump1 (287) / jump2 (288) / fall (289) / fall2 (290)` — STATE.JUMP returns inside the ajump branch (L11097) for any sheet carrying ajump1, so the vy-banded fallbacks and the id<=5 apex-spin triple `[F.jump2, F.air2, F.fall2]` below it are all dead for him. jump and jump1 also point at the same cell.
- `run1 / run2 (cells 121 / 125)` — runCells() takes the run_clean5 branch (he has run_clean1..8), so the 2-frame legacy toggle is unreachable.
- `xblkhit (cell 5)` — The string `xblkhit` appears nowhere in web/index.html outside the SHEET_V changelog. xblkguard is read once (the no-lock-cells blade-lock fallback); its partner never is.
- `attack_body2 (cell 35)` — Skipped by the flurry draw (L11857 lists 1,3,4,5,6). Still reachable — attackBodyCells() plays all six for the THROW — so this is a 5-of-6 gap on one move, not a dead cell.
- `special7 (cell 33)` — Aliases special6. The 7-beat Swallow's Pass row is really 6 distinct pictures with the last held.
- `crouch_4 (cell 258)` — Aliases crouch_3. The crouch 'breathing hold' alternates cr[3] and cr[2] — currently the same drawing, so the hold does not breathe. Flagged in commit 19209d0 ('Col 259 orphaned by the crouch alias — strip on next compaction').
- `INPUT WITH THE WRONG ART: grounded Fwd+Special (Swallow's Pass)` — The owner's delivered pass-through board with the baked red beam was packed at SHEET_V 606 as sfwd1..6 (cells 55-60), which only the AIRBORNE Fwd+Special reads. The grounded signature move — the one the Story Bible lists for him — draws the older special1..7 (cells 28-33), the same cells his parry stance borrows its first two from.
- `INPUT WITH NO SAKATE MOVE: Fwd / Back / Down + Light in Form 2` — The command-kick block at L5122 exempts Shin's Kage-Nui but not Tsubasa's Sakate, so three of his four Form-2 Light inputs execute a generic kick; tsubasaF2Frame has no kickKind guard, so f2_light{step} draws over the kick. The engine's own comment at L5113 records this and says it was left alone.
- `INPUT WITH THE WRONG ART: Sakate air Down+Heavy (METEOR BREAK)` — tsubasaF2Frame is missing the `if (p.moveArt || p.slamPhase || p.slamRecover > 0) return undefined;` guard that shinF2Frame carries (L10549), so the Form-2 heavy string draws over the whole plunge instead of hdown2/hdown3.
- `MISSING SAKATE ROWS: f2_run, f2_jump, f2_roll, f2_crouch, f2_block, f2_land, f2_dash, f2_csweep` — The shared f2MovementFrame router reads nine movement rows; his sheet carries two (f2_idle, f2_parry). Every other Form-2 movement state silently falls back to Form-1 art, which contradicts the L10601 comment ('this mode owns its LEGS as well as its hands'). f2_csweep's absence also means Sakate's low LIGHT and low HEAVY would share f2_clow — moot today, since low Light is eaten by the kick tier.
- `json `animations.evasive_flick.invulnerable: true` and `iaido_quick_draw.guard_pierce` / `tsuki_thrust.armor_pierce`` — Spec-only metadata. The engine reads nothing from tsubasa.json's `animations` block — Back+Heavy (eflick) grants NO i-frames, and the quick-draw / tsuki entries describe the EXECUTIONER's moves, not his. Do not treat these as shipped behaviour.

---

## SHIN

**Speed / Assassin** · S/P/R/D **9/4/7/4** · he/him  
**Weapon:** Engine spec: "Hand-to-Hand / Wire Tool". shin.json weapon_type: "Unarmed & Shuriken / Kunai". Story Bible canon: NO blade — chainmail head-to-toe under his clothes, so his engine weapon material is `mail` (clashes allowed, dull ring, no blade FX). Every projectile he throws now draws the WIRED SHURIKEN cells (wire1..6) — index.html:9898-9927 swaps the `kunai` projectile art for his sheet's own row.  
**Discipline:** Taijutsu & Shurikenjutsu (shin.json martial_art_discipline) — "classical unarmored striking and grappling paired with high-speed projectile throws". Etiquette in json: reiho (bow before/after) and zanshin (never drop guard after a strike).  
**Second form:** KAGE-NUI — bare V (P1 V / P2 K / pad 8), modeKey() index.html:2750 -> toggleKageNui() 4158. THE STANCE IS LIVE IN THIS TREE (cognee's "second mode removed" answer is STALE — shin.json at HEAD carries 54 f2_ keys and the router shinF2Frame at 10533 is wired). Mechanically COMPLETE, artistically HALF-BUILT: the movement half is fully drawn (f2_idle/run/jump/land/crouch/roll/block/dash + f2_vanish) and the ATTACK half has no art at all — shinF2Frame:10576 gates the attack branch on `F.f2_light1_1`, which shin.json does not have, so every Kage-Nui light and heavy falls back to Form-1 pictures while running Form-2 hitboxes. Damage is scaled by KAGE_DMG and incoming by KAGE_TAKEN (6801/9510). In stance the Special is REPLACED wholesale (7260): Fwd+S is the KAGE STEP, everything else is the wire cast / reel-in, and the generic special cost is refunded so the stance prices itself. Three Form-1 inputs are deliberately carved OUT of the stance and keep their Form-1 art and mechanics (5901-5905): grounded Fwd/Back/Up + Heavy (ghfwd/ghback/ghup) and air Down+Heavy (METEOR BREAK). Air Light is also exempt (5902) and takes his ordinary aerial light.  

| input | move | frame row | beats | art |
|---|---|---|---|---|
| Light (neutral, grounded) — P1 F | Fist Chain (cross -> spinning back-fist) | light1..light5 (cells 309-313) |  | DRAWN |
| Fwd + Light (grounded) | Push Kick | kpush1..kpush3 (cells 157-159) |  | DRAWN |
| Back + Light (grounded) | Back Heel Kick | kheel (cell 160) |  | DRAWN |
| Down + Light (grounded) | Leg Sweep | ksweep (cell 161) |  | DRAWN |
| Up + Light (grounded) | Standing light (no up-light exists) | light1..light5 (cells 309-313) |  | ALIAS |
| Dash + Light (double-tap a direction, then Light while dashTimer > 0) | Body Rush (Taijutsu dash attack) | dashatk1..dashatk6 (cells 234-239) |  | DRAWN |
| Heavy (neutral, grounded) — P1 G | Fudo Ken (charged straight punch) | hneu1..hneu6 (cells 0-5) |  | DRAWN |
| Fwd + Heavy (grounded) | Elbow-Knee-Palm rush | ghfwd1..ghfwd6 (cells 94-99) |  | DRAWN |
| Back + Heavy (grounded) | Ura-Shuto (reverse knife-hand) | ghback1..ghback6 (cells 100-105) |  | DRAWN |
| Up + Heavy (grounded) | Omote Shuto (rising launcher) | ghup1..ghup6 (cells 106-111) |  | DRAWN |
| Down + Heavy (grounded) | Sokuyaku Ken (low sweep) | ghdown1..ghdown6 (cells 228-233) |  | DRAWN |
| Special (neutral, grounded) — P1 H | Flying Kick Rush | special1..special7 (cells 341-347) |  | DRAWN |
| Fwd + Special (grounded) | Shuriken Volley | gsfwd1..gsfwd6 (cells 168-173) |  | DRAWN |
| Down + Special (grounded) | Shuriken Fan | attack_body1, attack_body2, attack_body6 (cells 162, 163, 167) |  | ALIAS |
| Up + Special (grounded, or inside the rise vy < -180) | Rising Palm (srisaa) | srisaa1..srisaa6 (cells 335-340) |  | DRAWN |
| Up-FORWARD diagonal + Special (grounded) | Wire Shuriken (the yank-in) | special1..special7 (cells 341-347) |  | ALIAS |
| Back + Special (grounded) | — no back special — | special1..special7 (cells 341-347) |  | ALIAS |
| Air Light (neutral) | Aerial slash | air1, air2, air3 (cells 354-356) |  | DRAWN |
| Air Fwd + Light | Forward air knife | afwd1..afwd5 (cells 315-319) |  | DRAWN |
| Air Back + Light | Reverse air knife | aback1..aback5 (cells 320-324) |  | DRAWN |
| Air Up + Light | Air Up-Poke | air2 (cell 355) — one cell held |  | FALLBACK |
| Air Down + Light | Air down poke | air1, air2, air3 (cells 354-356) |  | ALIAS |
| Air Heavy (neutral) | Fudo Ken, airborne | hneu1..hneu6 (cells 0-5) |  | ALIAS |
| Air Fwd / Back / Up + Heavy | Air directional heavy (undrawn) | air1, air2, air3 (cells 354-356) |  | ALIAS |
| Air Down + Heavy | METEOR BREAK | fall2 (cell 143) — one cell held |  | FALLBACK |
| Air Special (neutral) | Flying Kick, airborne | sneu1..sneu6 (cells 38-43) |  | DRAWN |
| Air Fwd + Special | Air special, forward | sfwd1..sfwd6 (cells 44-49) |  | DRAWN |
| Air Back + Special | Air special, back | sback1..sback6 (cells 50-55) |  | DRAWN |
| Air Up + Special | Air special, rising | sup1..sup6 (cells 56-61) |  | DRAWN |
| Air Down + Special | Air special, descending | sdown1..sdown6 (cells 62-67) |  | DRAWN |
| Light + Heavy within 90ms (F+G / I+O, or pad trigger 6/7) | Throw | attack_body1..attack_body6 (cells 162-167) |  | DRAWN |
| Wall cling + Light | Wired Shuriken wall throw | fall (cell 142) — one cell held |  | FALLBACK |
| Guard (hold C / M / pad shoulder) | Guard | block (127) held, block2 (128) on impact |  | DRAWN |
| Guard + direction | Dodge Roll | roll_1..roll_6 (cells 133-138) |  | DRAWN |
| Down held (grounded) | Crouch | crouch_1..crouch_4 (cells 129-132) |  | DRAWN |
| Tap C / M (Poof) | Kawarimi (substitution) | — none, he is invisible — |  | MISSING |
| Guard held + Special | Bunshin (shadow clone) | same cells as the live fighter |  | ALIAS |
| V (bare) | KAGE-NUI — set / drop the wire stance | f2_idle_1..6 once set (cells n/a to Form 1) |  | DRAWN |
| V + Up | MUKI (roster-wide offensive stance) | — no stance cells — |  | MISSING |
| V + Down | SAYA-KAMAE — REFUSED for Shin | — nothing draws, dud spark only — |  | MISSING |
| V + Back | KAGE-KAMI (shadow echo) | replays his own recorded cells |  | ALIAS |
| V + Fwd | SHADOW-WEAVE ANCHOR | — smoke puff, no dedicated cells — |  | MISSING |
| [KAGE-NUI] Light — beat 1 (neutral / fwd / back, grounded) | POKE — throat-height jab | light1..light5 (Form 1 fallback, cells 309-313) |  | FALLBACK |
| [KAGE-NUI] Light — beat 2 | RISING SLICE — diagonal cut | light1..light5 (Form 1 fallback) |  | FALLBACK |
| [KAGE-NUI] Light — beat 3 | DOUBLE THRUST — the guard-chipper | light1..light5 (Form 1 fallback) |  | FALLBACK |
| [KAGE-NUI] Down + Light (grounded) | LOW ANKLE POKE | light1..light5 (Form 1 fallback) |  | FALLBACK |
| [KAGE-NUI] Heavy — beat 1 (neutral, grounded) | TSUKI — the lunging thrust | hneu1..hneu6 (Form 1 fallback, cells 0-5) |  | FALLBACK |
| [KAGE-NUI] Heavy — beat 2 | CROSS-SLICE | hneu1..hneu6 (Form 1 fallback) |  | FALLBACK |
| [KAGE-NUI] Heavy — beat 3 | DISARM HOOK | hneu1..hneu6 (Form 1 fallback) |  | FALLBACK |
| [KAGE-NUI] Down + Heavy (grounded) | SWEEPING SLICE — the 360 spin | hneu1..hneu6 (Form 1 fallback) |  | FALLBACK |
| [KAGE-NUI] Air Heavy (not Down) | DIVE-PIERCE | hneu1..hneu6 (Form 1 fallback) |  | FALLBACK |
| [KAGE-NUI] Fwd + Special (grounded, no tether) | KAGE STEP (wire-step vanish) | f2_vanish_1..f2_vanish_6 |  | DRAWN |
| [KAGE-NUI] Special — neutral / back / up / down (no tether) | KAGE-NUI CAST (the wire shuriken snare) | special1..special7 (Form 1 fallback, cells 341-347) |  | FALLBACK |
| [KAGE-NUI] Special while a tether is held | REEL-IN ZIP | special1..special7 (Form 1 fallback) |  | FALLBACK |
| [KAGE-NUI] movement — idle / run / jump / land / crouch / roll / block / dash | Kage-Nui movement set | f2_idle_1..6, f2_run_1..6, f2_jump_1..3, f2_land_1..2, f2_crouch_1..4, f2_roll_1..6, f2_block_1..3, f2_dash_1..6 |  | DRAWN |
| Idle | Breathing idle | xidle1..xidle6 (cells 118-123) |  | DRAWN |
| Run / walk (A-D, auto-facing) | Ninja sprint | run_clean1..run_clean8 (cells 6-13) |  | DRAWN |
| Jump (W / ArrowUp) | Acrobatic jump arc | ajump1, ajump3, ajump4, ajump5 (+ ajump2 was deleted) — cells 330-334 |  | DRAWN |
| Hurt / hitstun | Flinch -> stagger -> settle | hurt, hurt2, hurt3 (cells 124-126) |  | DRAWN |
| Being thrown (victim) | Grabbed tumble | grabbed1..grabbed8 (cells 144-151) |  | DRAWN |
| Swept / tripped (STATE.STUNNED, tumbleT > 0) | Ground tumble | roll_2..roll_5 (cells 134-137) |  | ALIAS |
| Blade lock (mash Light/Heavy during a lock) | Blade lock | xblkguard (cell 127, = his block cell) held static |  | FALLBACK |
| Heavy after a fresh block (Reprisal) / Guard+Heavy (Shadow Slip) | — not his moves — | n/a |  | MISSING |

**Signature:** FLYING KICK RUSH — neutral Special, the move his spec line names (index.html:8045). Airborne unarmed rush, vx 560 / vy -185, 13 dmg. Draws special1..7, the board-look body rush. · SHURIKEN VOLLEY — grounded Fwd+Special (5467). Three wired shuriken fanned high/level/low at STAR_SPEED*1.3, 220ms, the shortest special on the roster. Costs 15. · SHURIKEN FAN — grounded Down+Special (7321). Three hira stars in one sweep, the Shurikenjutsu signature. · KAGE STEP — Kage-Nui Fwd+Special only (7276-7314). Owner, Aug 23: 'this is a special move that he can only access in his second mode.' Real quick-draw hitbox; a CLEAN hit (not blocked) starts the pass phase machine via beginKageStep. Six drawn beats over KAGE_STEP_DUR 0.30s: set -> burn to teal smoke -> smoke holds alone -> re-form -> stance -> settle. · KAGE-NUI WIRE CAST + REEL-IN ZIP — the stance's other Special. Cast latches a tether; re-press while bound and he pulls HIMSELF down the taut wire kunai-first (reelInZip 4237). · RISING PALM (srisaa) — Up+Special, DIR_SPECIALS '2:up'. Launcher, launchVy -400. · FUDO KEN — neutral Heavy, the board-look charged straight punch (hneu1..6). Also his ONLY air-heavy drawing. · BODY RUSH / TAIJUTSU — dash + Light (4988). Reaches him through the art-gated generic dash-attack branch (he has dashatk2 and no lunge1), not an id check. · WIRED SHURIKEN WALL THROW — Light while clinging (8673/8690). Three per airtime, aimed at the opponent, refills on landing.

**Dead or missing:**

- `flying_kick1..flying_kick6 (cells 359-364)` — PACKED, ZERO REACHABLE INPUTS. specialCells:10321-10324 records that this line used to return flying_kick and was changed to the generic special1..7 collector; the only remaining occurrence of the string 'flying_kick' in web/index.html is that comment. Six drawn cells that no input can reach. (cognee also still reports this as unreachable — that half of its answer is correct.)
- `f2_parry_1..f2_parry_5 (Kage-Nui parry)` — UNREACHABLE FOR SHIN. f2MovementFrame:10440 draws it on STATE.PARRY_STANCE, but no code path anywhere sets PARRY_STANCE for spec.id 2 — all seven setters are ids 0 (Executioner up/back Heavy), 3, 4, 5 and 6. Five drawn cells the fighter can never enter the state for. Either give him a parry input or the row stays dark.
- `ALL Kage-Nui ATTACK art (f2_light1/2/3, f2_heavy1/2/3, f2_air, f2_clow, f2_csweep)` — NINE MOVES WITH MECHANICS AND NO PICTURE. The Form-2 kit at 5901-5983 is fully built — Poke, Rising Slice, Double Thrust, Tsuki, Cross-Slice, Disarm Hook, Low Ankle Poke, Sweeping Slice, Dive-Pierce, each with its own boxes and recovery — but shin.json carries none of those rows, so shinF2Frame:10576 bails and every one of them draws a Form-1 picture. The stance arrived movement-first by design (10570-10575), so this is the outstanding half.
- `hfwd / hback / hup (air directional heavies)` — NO ROWS AT ALL. Air Fwd, Back and Up + Heavy are three distinct moves that all draw air1..3, his AIR LIGHT row. Owner note in MEMORY has these as removed in the Aug 23 cleanup; the inputs are still live.
- `dive1..6 / hdown1..6 (METEOR BREAK)` — NO ROW. The roster-wide air Down+Heavy is a real three-phase move for him and draws exactly one cell (fall2) for the hang, the plunge AND the landing shockwave. Meteor is hdown1..6 across the roster; his sheet has neither that nor the `dive` family.
- `glneu / glfwd / glback / gldown / glup (ground directional lights)` — NO ROWS. Consequence is per-input: Fwd/Back/Down get the one-to-three-cell command KICK tier instead (which is the intended default), but UP+LIGHT has no kick mapping either, so it silently replays the neutral light chain — a bound input with no move behind it.
- `wallslide` — NO ROW. Wall cling and the Wired Shuriken wall throw both draw F.fall (cell 142), one static cell, for the whole cling and the whole 0.45s wallThrowT toss window. Oni has wallneedle1..8 for the same mechanic.
- `lock1..lockN (blade lock)` — NO ROW — and no fighter on the roster has one. His lock holds xblkguard (his block cell). The last two lockN cells are supposed to be the win and lose beats.
- `light6 (cell 314)` — PACKED, NEVER READ. The generic light collector at 11454 takes light1..light5 when light5 is defined; nothing in the file references light6.
- `air4, air5 (cells 357-358)` — PACKED, NEVER READ. Every branch that touches his air set is hardcoded [F.air1, F.air2, F.air3] (11394, 11686). Grepped: no F.air4 / F.air5 anywhere.
- `run1, run2 (cells 412-413)` — PACKED, UNREACHABLE FOR HIM. runCells:10195 returns run_clean1..8 whenever run_clean5 exists, and the only other reader is the id===5 (Kael) bunshin cell list at 2580. These arrived in the 'run1/run2 converge in — key-set parity on all nine fighters' commit, so they are parity keys, not reachable art.
- `jump, jump1, jump2 (cells 139-141)` — UNREACHABLE. The ajump branch (11097) wins STATE.JUMP outright, and the vy-band fallbacks at 11130-11132 sit below it. `fall` (142) survives via the wall-cling fallback and `fall2` (143) via Meteor Break; the other three draw nowhere. ⚠ the comment at 11091 claims all five were 'repointed at the board beats' — they are NOT: ajump is cells 330-334 and these are 139-143. The comment is wrong, the cells are stale.
- `taijutsu1..6` — DEAD KEY NAME (cells 234-239 DO draw). Identical cells to dashatk1..6, which is what the engine reads. Only occurrences of 'taijutsu' in index.html are two comments (10285, 12333). Harmless but it is a trap for the next reader — cognee currently answers 'dashatk aliases taijutsu' and it is the other way round.
- `slowsweep1..6` — DEAD KEY NAME (cells 228-233 DO draw). Identical cells to ghdown1..6, which DIR_MOVES '2:down' reads. Only occurrence is the comment at 10285, which asserts slowsweep is 'gone from shin.json' — it is not, it is still in the file at HEAD.
- `idle_stance1, idle_v335, xblkhit` — ZERO REFERENCES in web/index.html. All three duplicate cells that draw under other names (118 = xidle1, 128 = block2). Measured with a whole-file scan, SHEET_V comment line excluded.
- `heavy1, heavy2 (cells 0-1), kpush (bare, 159), roll (bare, 135)` — SHADOWED ALIASES. Each is named only in a fallback the engine can never reach for him: heavy1/2 behind the hneu branch (10287) and the attackBodyCells throw, bare kpush behind the kpush3 three-beat branch (11201), bare roll behind roll_1..6. The cells draw under their real names.
- `INPUT WITH NO MOVE: Back + Special` — Back+Special is the roster's signature-technique slot (Ember blade-trap, Kael niten, Tsubasa flurry, Mokurai zen reflect, Exile iai cross) and Shin has NOTHING there — it replays the neutral Flying Kick. The 5481-5487 comment confirms the Back arm that used to live in the volley branch was deleted on purpose and warns against re-adding it there; the empty slot is the leftover.
- `INPUT ODDITY: WIRE SHURIKEN is only reachable on the up-forward diagonal` — index.html:7335 (`specId === 2 && axis === facing && isGrounded`) carries no !up/!down guard, while the Shuriken Volley at 5467 that shadows it DOES require !up && !down. Net effect: straight Fwd+Special is always the volley, Down+Fwd is always the fan, and the yank-in wire shuriken fires ONLY on Up+Fwd — where it also draws the neutral special row, because no gsup/wire-launch art is packed. Either an input the player cannot find, or a guard missing from 7335.

---

## EMBER

**Brawler / Rushdown** · S/P/R/D **8/7/3/8** · he/him  
**Weapon:** Tekkō-kagi (Iron Claws) — spec.weapon "Tekko-Kagi Claws", json weapon_type "Tekkō-kagi (Iron Claws)". Engine weapon material = 'steel' (WEAPON_MAT has no entry for id 4, so the default 'steel' applies) — he clashes, he can enter BLADE_LOCK, and Saya-Kamae accepts him.  
**Discipline:** Tekkōkagijutsu / Shukōjutsu — "Close-quarters claw slashes, blade trapping, and aggressive beast-style grappling" (ember.json martial_art_discipline / discipline_notes). Movement law on top of it: Ember-Claw-Combo-Wolverine-Spec.md — alternating hands never both at once, torso counter-rotates each swipe, low hunched posture, advance on every swipe, every swipe is a 3-line RAKE.  
**Second form:** NONE IN THIS TREE. modeKey() (index.html:2727) reads direction first (the four roster-wide stances), then branches by id for Exile/Shin/Tsubasa/Mizu, then falls through to the CHUDAN gate which requires a packed `idle_chudan` cell. ember.json has no `idle_chudan`, so a bare V / K press for Ember is a SILENT NO-OP. The GHOST KILLER form is packed as 33 `gk_*` rows (185 cells) and is referenced ZERO times in this engine (`grep -c "gk_" web/index.html` = 1, and that one hit is the SHEET_V comment). The wiring for it lives on the other tree — ~/shadowclash-fable-5/web/index.html has 29 `gk_` hits — so on SHADOWCLASH-RECOVERED at 619 the whole second form is dead art. RECOVERY/EVERYTHING-OWED.md line 22 calls the gk_ rows his authoritative new style and lines 36-52 list 7 gk_ rows still owed, which is written against the fable-5 engine, not this one.  

| input | move | frame row | beats | art |
|---|---|---|---|---|
| F (Light, neutral, grounded) — P1 F / P2 I | Claw Barrage (Wolverine light chain) | `elight1..elight5` | 5 | DRAWN |
| Fwd + F (grounded) | Push Kick (teep — shove, wall-splat, log punt) | `kpush1..kpush3` | 3 | DRAWN |
| Back + F (grounded) | Heel Kick (hits BEHIND — carries { behind: true }) | kheel (bare key only) |  | DRAWN |
| Down + F (grounded) | Sweep Kick (low, trips) | ksweep (bare key only) |  | DRAWN |
| Up + F (grounded) | Claw Barrage (no distinct up-light) | `elight1..elight5` | 5 | ALIAS |
| G (Heavy, neutral, grounded) — P1 G / P2 O | Both-Claws X Slash | `eheavy1..eheavy4` | 4 | DRAWN |
| Fwd + G (grounded) | CLAW REND (2 tears) | `clawrend1..clawrend6` | 6 | DRAWN |
| Down + G (grounded) | LOW CLAW RAKE | `lowrake1..lowrake6` | 6 | DRAWN |
| Back + G (grounded) | CLAW RETREAT SWIPE | `eretreat1..eretreat6` | 6 | DRAWN |
| Up + G (grounded, or inside a jump still rising vy < -180) | Rising Double-Claw Launcher | `upatk1..upatk6` | 6 | DRAWN |
| H (Special, neutral, grounded) — P1 H / P2 P | Shredding Lunges (armored claw dash) | `espec1..espec5` | 5 | DRAWN |
| Fwd + H (grounded) | SHRED CHARGE | `echarge1..echarge6` | 6 | DRAWN |
| Down + H (grounded) | GROUND RIP | `erip1..erip6` | 6 | DRAWN |
| Up + H (grounded, or rising vy < -180) | CEILING HOOK | `ehook1..ehook6` | 6 | DRAWN |
| Back + H (grounded) | BLADE-TRAP PARRY | `eparry1..eparry5` | 5 | DRAWN |
| — (automatic, on a caught hit during Blade-Trap) | Blade-Trap Counter (X-Shred Answer) | espec2 -> eheavy3 -> eheavy3 -> espec5 |  | ALIAS |
| F+G within 90ms (P1 F+G / P2 I+O / pad trigger 6 or 7) | Claw-Slice Throw (forward) / over-shoulder throw (back) | none — falls through to F.idle |  | MISSING |
| air F (Light, neutral) | Zero-G Claw Cut (neutral aerial) | `aneu1..aneu6` | 6 | DRAWN |
| air Fwd + F | Air Forward Claw Rake | `afwd1..afwd6` | 6 | DRAWN |
| air Back + F | Air Reverse Claw Rake | `aback1..aback6` | 6 | DRAWN |
| air Down + F | Pogo Claw Dive (down aerial light) | aneu1..aneu6 (NOT adown) |  | ALIAS |
| air Up + F | Air Up-Poke (skyward claws) | upatk3 (single cell) |  | ALIAS |
| air G (Heavy, neutral) | Air Claw Drop (neutral aerial heavy) | `hneu1..hneu6` | 6 | DRAWN |
| air Fwd + G | Air Forward Claw Drive | `hfwd1..hfwd6` | 6 | DRAWN |
| air Back + G | Air Reverse Claw Cut | `hback1..hback6` | 6 | DRAWN |
| air Up + G (while NOT rising hard, vy >= -180) | Air Up Claw Thrust | `hup1..hup6` | 6 | DRAWN |
| air Down + G | METEOR BREAK (roster-wide dive slam) | hdown2 (hang) -> hdown3 (plunge) |  | ALIAS |
| air H (Special) — neutral | Shredding Lunges, airborne | `sneu1..sneu6` | 6 | DRAWN |
| air Fwd + H | Shredding Lunges, airborne (forward art) | `sfwd1..sfwd6` | 6 | DRAWN |
| air Back + H | Shredding Lunges, airborne (back art) | `sback1..sback6` | 6 | DRAWN |
| air Down + H | Shredding Lunges, airborne (down art) | `sdown1..sdown6` | 6 | DRAWN |
| air Up + H | CEILING HOOK (airborne re-press) / airborne claw dash | `sup1..sup6` | 6 | DRAWN |
| H while wall-clinging (Ember only) | WALL POUNCE DIVE | s* row for whatever direction is held (sneu by default) |  | ALIAS |
| F while wall-clinging | — nothing wall-specific; ordinary air light | `aneu1..aneu6` | 6 | ALIAS |
| C hold (P1 C / P2 M / pad shoulder) | Claw Guard | `block / block2 / blockhit` | 3 | DRAWN |
| C tap | Kawarimi (substitution poof) | — vanish, no sprite drawn |  | FALLBACK |
| C + direction | Dodge Roll | `roll_1..roll_6` | 6 | DRAWN |
| C(hold) + H | BUNSHIN — trap clone (30 chakra) | idle / idle2 (the CLONE's cells) |  | ALIAS |
| V (P1) / K (P2), no direction | — DEAD PRESS for Ember | none |  | MISSING |
| V + Up | MUKI (offensive stance, roster-wide) | no dedicated row — normal art |  | FALLBACK |
| V + Down | SAYA-KAMAE / gyakute reverse grip (roster-wide) | no dedicated row — normal art |  | FALLBACK |
| V + Back | KAGE-KAMI echo (roster-wide) | replays his own recorded cells |  | FALLBACK |
| V + Fwd | WEAVE ANCHOR / swap (roster-wide) | no dedicated row — normal art |  | FALLBACK |
| — (state, on a steel-on-steel clash) | Blade Lock | xblkguard (single cell held) |  | FALLBACK |
| — (states) | Idle / Run / Jump / Crouch / Land / Hurt / Thrown / Wall cling | xidle1..6 (ping-pong 1-2-3-4-5-6-5-4-3-2) · run_clean1..6 · ajump1..6 (vy-banded) · crouch_1..4 · crouch_3 on touchdown · hurt/hurt2/hurt3 · grabbed1..8 · wallslide (bare key) |  | DRAWN |

**Signature:** Claw Barrage — the Wolverine light chain (elight1..5), 3-beat multi-tap on LIGHT_STRINGS.default · Both-Claws X Slash — neutral Heavy (eheavy1..4) · Shredding Lunges — neutral Special, armored claw dash (espec1..5); Specials-FrameMatrix 5.9 names it SHREDDING LUNGES · SHRED CHARGE — Fwd+Special, armored run-in with two boxes (echarge1..6) · CEILING HOOK — Up+Special, both feet leave together (ehook1..6) · BLADE-TRAP PARRY — Back+Special, crossed claws catch the blade, answer is the held X-shred (eparry1..5) · WALL POUNCE DIVE — Special off a wall cling, armored diagonal dive (Story Bible line 271 lists this as his one-line signature) · Rising Double-Claw Launcher — Up+Heavy (upatk1..6)

**Dead or missing:**

- `gk_* — 33 rows, 185 cells (gk_idle, gk_run, gk_jump, gk_block, gk_crouch, gk_kneel, gk_hurt, gk_wallslide, gk_air, gk_neu, gk_fwd, gk_back, gk_down, gk_up, gk_hneu, gk_hfwd, gk_hback, gk_hup, gk_hdown, gk_sneu, gk_sfwd, gk_sback, gk_sdown, gk_aneu-family: gk_afwd, gk_aback, gk_adown, gk_aup, gk_ahneu, gk_ahback, gk_ahdown, gk_asneu, gk_asback, gk_asdown)` — THE WHOLE GHOST KILLER FORM IS UNREACHABLE IN THIS TREE. `grep -c "gk_" web/index.html` returns 1 and that hit is inside the SHEET_V 619 comment string — there is no gk_ read, no form flag, and no modeKey branch for id 4. 185 packed cells draw nowhere. The wiring exists on the other tree (~/shadowclash-fable-5/web/index.html has 29 gk_ hits), which is exactly the engine-divergence RECOVERY/EVERYTHING-OWED.md Part 2D warns about.
- `adown1..adown6 (6 cells)` — Packed air-down-light row, never read. The only adown branch (index.html:11274) is gated `p.spec.id === 8` — Oni. Ember's air Down+Light falls through to aneu.
- `hdown1, hdown4, hdown5, hdown6 (4 of 6 cells)` — Air Down+Heavy is ALWAYS intercepted by the meteor branch (index.html:6523), so the `hdown` entry in the air-heavy dirCells map is unreachable. Only hdown2 and hdown3 draw, as the meteor hang and plunge.
- `ksweep2..ksweep6 (5 of 6 cells)` — The sweep kick is drawn by the string-built lookup `F['k' + p.kickKind]` (index.html:11203), which reads the BARE `ksweep` key (= ksweep1, cell 87). A six-beat drawn sweep plays as one held cell.
- `kheel2..kheel6 (5 of 6 cells)` — Same string-built bare-key lookup. `kheel` = kheel1 = cell 444. Six drawn beats, one on screen.
- `kpush4, kpush5, kpush6 (3 of 6 cells)` — index.html:11202 hardcodes `[F.kpush1, F.kpush2, F.kpush3]`. The last three beats of the packed push kick never draw.
- `wallslide2..wallslide6 (5 of 6 cells)` — STATE.WALL_CLING returns `F.wallslide ?? F.fall` (index.html:11001) — the bare key only, = wallslide1 = cell 450. Wall cling is core to Ember's identity and it is a still frame.
- `elight6` — index.html:11407 hardcodes elight1..elight5. The sixth beat of his most-pressed button never draws.
- `eheavy5, eheavy6` — heavyCells() (index.html:10222) returns eheavy1..eheavy4 only. eheavy3 is reused by the blade-trap counter; 5 and 6 are read nowhere.
- `fall, fall2` — Shadowed. Ember has ajump1..6, and the ajump branch (index.html:11097) returns before every fall band; WALL_CLING prefers wallslide; the slam prefers hdown3. Both keys are unreachable.
- `kneel` — Shadowed by crouch_3 — the touchdown branch (index.html:12253) takes crouch_3 first, and the `F.kneel ?? F.idle` line under it can never run for a sheet that has crouch_3. Only Mokurai's bunshin still reads kneel.
- `run1, run2 (name level only)` — runCells() prefers run_clean1..N when run_clean5 exists, which it does. run1/run2 are alias keys onto cells 63/66 (= run_clean1/run_clean4), so no cell is lost — but the names resolve nowhere except Kael's bunshin branch.
- `INPUT WITH NO ART: F+G throw (both forward and back)` — STATE.THROWING ends at `attackBodyCells(F) ?? (F.heavy1 ? … : [F.heavy_i1, F.heavy_i3])` and Ember has none of attack_body1, heavy1, heavy_i1, heavy_i3. The array is all-undefined, so the spriteFrameIndex wrapper substitutes his IDLE. He stands still through his own Claw-Slice Throw — a move with bespoke owner-approved physics (index.html:8938) and zero frames.
- `INPUT WITH NO ART: bare V / K (second form)` — Silent no-op. No idle_chudan on the sheet and no id-4 branch in modeKey(), so the key eats the press. The 185 gk_ cells that would be the form have no entry point here.
- `MISROUTED, not missing: air Down+Light` — Draws aneu (neutral air) while the purpose-drawn adown row sits packed. One `|| p.spec.id === 4` on index.html:11274 — or better, dropping the id gate to an art gate the way the ajump branch was fixed — reaches six drawn cells.
- `NO ROWS AT ALL: glneu, glfwd, glback, gldown, glup` — Ember has none of the ground-light directional family, which is why fwd/back/down Light all drop to the unarmed kick tier and up/neutral share elight. Not a defect — just the reason three of his five ground lights are kicks rather than claws.
- `gk_wallslide (quality, from RECOVERY/EVERYTHING-OWED.md Part 2B)` — Even if the form were wired, this tree's gk_wallslide has the wall baked into the cells; fable-5's is the clean one. Recorded as an import, not a re-key.

---

## MIZU

**Zoning / Support** · S/P/R/D **6/5/10/5** · she/her  
**Weapon:** Long Bō Staff (rokushaku) — splits into twin Hanbō in mode 2  
**Discipline:** Bōjutsu & Hanbōjutsu (json: "Mid-range staff sweeps, joint locks, rapid thrusts, and vaulting strikes")  
**Second form:** HANBŌ NO KATA — V (P1) / K (P2) / pad 8, Player.modeKey -> toggleHanbo() at web/index.html:2757, implemented 4209. The bo splits into twin half-staves; Kukishin-ryū flavour. Draw router is mizuF2Frame() at 10646, called FIRST in spriteFrameIndexRaw, so in stance it outranks every other draw branch. It bails (returns undefined -> Form 1 art) whenever moveArt / vaultAnim / reedAnim / kickKind is set. No locomotion, jump, crouch, block or reaction rows exist in hb_*, so all of that stays Form 1.  

| input | move | frame row | beats | art |
|---|---|---|---|---|
| Light (F/I) — neutral, grounded | Staff Thrust Chain (3-beat multi-tap) | `light1..5` | 5 | DRAWN |
| Fwd + Light, grounded | Push Kick (command kick 'push') | `kpush1..3` | 3 | DRAWN |
| Back + Light, grounded | Heel Kick (command kick 'heel') | `kheel` | 1 | DRAWN |
| Down + Light, grounded | Leg Sweep (command kick 'sweep') | `ksweep` | 1 | DRAWN |
| Up + Light, grounded | Staff Thrust Chain (no up variant) | `light1..5` | 5 | ALIAS |
| Light, airborne, neutral / fwd / back / down | Aerial Staff Swing (ZERO-G CUT on neutral & fwd/back) | `air1..3` | 3 | FALLBACK |
| Up + Light, airborne | Air Up-Poke | air2 (single cell) |  | FALLBACK |
| Heavy (G/O) — neutral, grounded | Overhead Staff Slam | `heavy_i1..5` | 5 | DRAWN |
| Fwd + Heavy, grounded | BŌ THRUST | `bothrust1..7` | 7 | DRAWN |
| Down + Heavy, grounded | BŌ LOW SWEEP | `bolow1..7` | 7 | DRAWN |
| Up + Heavy, grounded | RISING STAFF | `ristaff1..7` | 7 | DRAWN |
| Back + Heavy, grounded | Staff Spin (UI: 'GUARD-BREAK SPIN') | `staffspin1..7` | 7 | DRAWN |
| Fwd + Heavy, airborne | Air Staff Thrust | `hfwd1..7` | 7 | DRAWN |
| Up + Heavy, airborne | Air Rising Staff | `hup1..7` | 7 | DRAWN |
| Down + Heavy, airborne | METEOR BREAK | `hdown1..7` | 7 | DRAWN |
| Back + Heavy, airborne | Air Staff Swing (no back row) | `air1..3` | 3 | FALLBACK |
| Heavy, airborne, neutral | Air Staff Swing (no neutral row) | `air1..3` | 3 | FALLBACK |
| Special (H/P) — neutral, grounded | MIST DROP | `special1..8` | 8 | DRAWN |
| Fwd + Special, grounded | STAFF RUSH | `gsfwd1..7` | 7 | DRAWN |
| Down + Special, grounded | LOW DRIVE | `gsdown1..7` | 7 | DRAWN |
| Back + Special, grounded | REED WITHDRAW | `mback1..6` | 6 | DRAWN |
| Up + Special, grounded (W held while on the floor) | VAULTING STAFF SLAM | `gsup1..6` | 6 | DRAWN |
| Up + Special, airborne (the normal press — W then H) | VAULTING STAFF SLAM (drawing the wrong row) | `sup1..7` | 7 | ALIAS |
| Fwd + Special, airborne | FALLING REED | `sfwd1..7` | 7 | DRAWN |
| Back + Special, airborne | REED WITHDRAW, AIRBORNE | `sback1..7` | 7 | DRAWN |
| Down + Special, airborne | REED PLUNGE | `sdown1..7` | 7 | DRAWN |
| Up + Special, airborne (after the vault window closes / no jump left) | RISING REED | `sup1..7` | 7 | DRAWN |
| Special, airborne, neutral | MIST DROP (airborne) | `special1..8` | 8 | ALIAS |
| Light + Heavy within 90ms (F+G / I+O, or pad trigger 6/7) | Staff Throw | `attack_body1..6` | 6 | DRAWN |
| Guard hold (C/M, pad shoulder) | Guard | (none — F.block ABSENT) |  | MISSING |
| Guard + direction | Dodge Roll | `roll_1..6` | 6 | DRAWN |
| Guard + Special (hold C, press H) | BUNSHIN → WATER SLICK | idle / idle2 (clone) + procedural slick |  | FALLBACK |
| C tap (Poof / Kawarimi) | Kawarimi (substitution) + Bomb-Log | (no poof row — alpha 0 vanish) |  | MISSING |
| V (P1) / K (P2) / pad 8 | HANBŌ NO KATA — split the bo | hb_split_1..6 (PACKED BUT NEVER DRAWN) |  | MISSING |
| HANBŌ · Light — neutral or up, grounded | KOTE-UCHI (wrist snap) | `hb_rap1_1..6` | 6 | DRAWN |
| HANBŌ · Fwd + Light, grounded | TSUKI-OTOSHI (dropping point) | `hb_jab_1..6` | 6 | DRAWN |
| HANBŌ · Back + Light, grounded | Heel Kick (unchanged by the grip) | `kheel` | 1 | ALIAS |
| HANBŌ · Down + Light, grounded | Leg Sweep (unchanged by the grip) | `ksweep` | 1 | ALIAS |
| HANBŌ · Light, airborne (any direction) | Air Twin-Stick Rap | `hb_airrap_1..6` | 6 | DRAWN |
| HANBŌ · Heavy, grounded (ALL four directions + neutral) | MAKI-OTOSHI (spiral wrap-down) | `hb_maki_1..6` | 6 | DRAWN |
| HANBŌ · Heavy, airborne (incl. Down = METEOR BREAK) | Air Cross Strike | `hb_aircross_1..6` | 6 | DRAWN |
| HANBŌ · Back + Special, grounded | KAESHI (the return) | `hb_catch_1..6` | 6 | DRAWN |
| HANBŌ · Up + Special, truly grounded | JŪJI-UKE → HANE-AGE (cross-block flick) | `hb_cross_1..6` | 6 | DRAWN |
| HANBŌ · Special — neutral, grounded or airborne | MIST DROP (cast with the sticks) | `hb_mist_1..6` | 6 | DRAWN |
| HANBŌ · Fwd + Special, grounded | STAFF RUSH (mechanics) drawing the mist | `hb_mist_1..6` | 6 | ALIAS |
| HANBŌ · Down + Special, grounded | LOW DRIVE (mechanics) drawing the low stick sweep | `hb_low_1..6` | 6 | ALIAS |
| HANBŌ · Special, airborne — fwd / down / up / back | Form-1 air Reed kit, hanbō art | hb_mist (fwd) · hb_low (down) · hb_cross (up) · sback (back) |  | ALIAS |
| Down hold, grounded | Crouch | `crouch_1..4` | 4 | DRAWN |
| Left / Right hold | Run / Backpedal | `run_clean1..6` | 6 | DRAWN |
| Jump / Up | Jump arc | ajump1..6 (+ kneel takeoff, crouch_3 landing) |  | DRAWN |
| Wall contact while airborne | Wall Cling / Slide | `wallslide` | 1 | DRAWN |
| Taking a hit / stun / being thrown | Hit reaction | (none — F.hurt / hurt2 / hurt3 ABSENT) |  | MISSING |
| Blade lock (clash) | Blade Lock | (none — lock1..N ABSENT) |  | MISSING |
| Guard + Heavy | (no move — falls to plain Heavy) | `heavy_i1..5 or the DIR_MOVES row` | 5 | ALIAS |

**Signature:** MIST DROP (neutral Special) — radius 260, 7.0s, owner-ruled a VANISH not a haze: she is alpha 0 (measured hidden 719/720 frames), everyone else in it merely obscured, no hitbox, no cooldown. A recast replaces her own field rather than stacking. · VAULTING STAFF SLAM (Up+Special) — bōjutsu pole-vault: plant, ride it up, drive it down, the LANDING detonates. Own drawn board gsup1..6 since SHEET_V 580. · REED WITHDRAW (Back+Special) — retreating wide bo arc, vx -150; the only move on her sheet with a hand-authored exposure track ('reed', ANIM_TRACKS at 10129). · BŌ THRUST / RISING STAFF / BŌ LOW SWEEP / STAFF SPIN — her four DIR_MOVES ground heavies ('1:fwd/up/down/back' at index.html:1658-1670), the reach-10 zoner's spacing kit. · WATER SLICK — Mizu-only Bunshin rider: popBunshin() at 2604 leaves a 150px, 2.5s slick that breaks grounded grip. · KAESHI (hanbō Back+Special) — 0.25s catch that negates the hit and TURNS the attacker away. No damage; the punish is yours to take.

**Dead or missing:**

- `ASHI-BARAI — hanbō Down+Special (index.html:7192)` — UNREACHABLE MECHANIC. The LOW DRIVE intercept at 5431 has no `!this.hanbo` guard and `return`s before triggerSpecialAction is ever called, so the stance's own leg reap can never execute. hb_low_1..6 still draws over LOW DRIVE, which is why it looks like it works.
- `REED PIERCE — grounded Fwd+Special (index.html:8000)` — UNREACHABLE MECHANIC. Shadowed by the STAFF RUSH branch at 5410, same condition (`axis === facing && !down && !up && isGrounded`), which returns first.
- `MIST SILHOUETTES — grounded Down+Special in her own mist (index.html:7217)` — UNREACHABLE MECHANIC, and it is the Story Bible's listed signature for her ('Down+Special in mist — two fake Mizu silhouettes', roster table line 272). Shadowed by LOW DRIVE at 5431.
- `LOW REED — grounded Down+Special (index.html:7461)` — UNREACHABLE MECHANIC. Third branch shadowed by LOW DRIVE at 5431.
- `hb_split_1..6 (6 cells)` — PACKED, NEVER DRAWN. The stance-transition art. mizuF2Frame reads hb_split_1 only as an existence gate (10647); toggleHanbo (4209) is instantaneous with no animation, and no draw site names the row.
- `hb_airlow, hb_airraise, hb_airspin, hb_fan, hb_flick1, hb_flick2, hb_lowpoke, hb_plunge, hb_point, hb_rap2, hb_slam, hb_walkstrike (12 rows, 72 cells)` — PACKED, NEVER DRAWN. mizuF2Frame only ever names 9 hb_ rows (hb_jab, hb_rap1, hb_airrap, hb_maki, hb_aircross, hb_catch, hb_low, hb_cross, hb_mist). With hb_split that is 13 of 22 hanbō rows — 78 of 132 cells — unreachable by any input.
- `block / block2 / blockhit` — ABSENT FROM THE SHEET. STATE.BLOCKING (12025) resolves to undefined and the spriteFrameIndex wrapper substitutes F.idle. She guards in her idle pose; no raise beat, no braced hold, no impact spark.
- `hurt / hurt2 / hurt3` — ABSENT FROM THE SHEET. Every hit reaction, every stunned frame, and the entire time she is held in an opponent's throw draw her IDLE. Two draw tails (`return F.hurt` at 12023, `return F.hurt3` in STUNNED) end on keys she does not have.
- `grabbed1..8` — ABSENT. No per-fighter tumble while physically held (12013) — falls to the hurt pose, which is also missing, so it lands on idle.
- `lock1..N` — ABSENT. Blade-lock win/lose cells (10707). Roster-wide hole, not Mizu-specific.
- `kstomp` — ABSENT. The air-down-light branch at 11279 misses, so air Down+Light shares air1..3 with every other air light instead of a leg pose.
- `kpush (bare key, cell 130)` — DUPLICATE, NEVER READ. Identical cell to kpush2. The draw branch at 11201 uses kpush1..3 because kpush3 exists, so `F['k'+kickKind]` (11203) never resolves to it.
- `bothrust7, bolow7, ristaff7, staffspin7, hfwd7, hup7, hdown7, gsfwd7, gsdown7, sfwd7, sback7, sdown7, sup7, mback7, special7, special8, idle2` — PADDING KEYS POINTING AT THE PREVIOUS CELL. Harmless on their own, but on the four DIR_MOVES rows it is load-bearing: attackCellIndex (10147) honours a track only when `track.length === count`, and the authored 6-stop tracks in DIR_MOVES '1:fwd/down/up/back' meet 7-key rows, so all four are silently discarded and the moves fall to linear exposure. Same defect the Oni comment at 1735 documents and deletes for him.
- `gsup1..6 vs the vaultAnim draw branch (11791)` — DEAD DRAW BRANCH + WRONG-ROW ROUTING. dirCells (ground 11726 / air 11704) fires before the vaultAnim branch, so its physics-phase mapping never runs. Worse, the natural Up+Special press is airborne (Up is the jump key), so the air map draws sup1..7 — RISING REED's row — over the vault. Her own vault board only appears on a grounded-with-Up-held press. The comment at 11731 ('up is Oni's RISING CLAW and nobody else's — he is the only fighter with a gsup family packed') is factually stale since SHEET_V 580.
- `attack_body1..6` — NOT DEAD, but easy to misread as dead: heavyCells explicitly moved Mizu off it (10276), and its only remaining reader is STATE.THROWING (12006). If a future pass gives her drawn throw art, these six cells become orphans.
- `Fwd+Special and Down+Special chakra gating` — NOT AN ART HOLE — A MECHANICS HOLE. Both branches (5410, 5431) sit ABOVE the special gate at 5750, so they cost ZERO of her 30-chakra SPECIAL_COST and fire while WINDED. Every other special on the roster pays and refuses. Same defect class the Shin comment at 5455 documents as already fixed for him.
- `In-game move list, index.html:16777` — THREE ENTRIES NO LONGER MATCH THE ENGINE. It promises 'Fwd+H — Reed Pierce' (engine gives STAFF RUSH), 'Down+H — mist silhouettes (needs her mist)' (engine gives LOW DRIVE), and 'Back+G — GUARD-BREAK SPIN' (staffspin's box carries no `unblockable`). It also never mentions V / HANBŌ NO KATA at all, so the whole second mode is undiscoverable in-game.

---

## THE EXECUTIONER

**Heavy / Berserk** · S/P/R/D **3.5/9/9/6** · he/him  
**Weapon:** ONE SLIM KATANA. Story Bible owner ruling 2026-08-07: "His weapon is ONE SLIM KATANA — a single curved blade drawn iaijutsu style… the greatsword is retired." Engine roster card still says `weapon: "Long Sword"`; executioner.json still says `weapon_type: "Nodachi / Single Katana"`. Material tag = steel (WEAPON_MAT has no id-0 entry, so `weaponMat()` returns 'steel'), which is what gives him hasuji, blade-clash, blade-lock and Saya-Kamae eligibility.  
**Discipline:** Iaijutsu & Battōjutsu — quick-draw sword art (executioner.json `martial_art_discipline`). `martial_style` = Ittō-ryū (One-Sword Style), focus on hasuji (edge alignment) and kamae transitions (jōdan / chūdan / gedan / hassō / waki). Etiquette block in the json names reihō, zanshin, chiburi, notō. Stats speed 3.5 / power 9 / reach 8 / defense 8, archetype "Heavy / Berserk". RECOVERY_TAX[0] = 1 — he is the ONE fighter who pays no speed tax on recovery.  
**Second form:** CHŪDAN-NO-KAMAE — "Second Form" on V (P2 K), bare press, grounded, not mid-attack. Gate is `frames.idle_chudan !== undefined`, which he passes. Trade (owner, Jul 31 2026): heavies and specials get ×1.28 damage / ×1.18 reach (CHUDAN_DMG / CHUDAN_REACH), lights are NOT multiplied but become a 4-hit flurry, neutral heavy becomes a 3-hit thrust pump — and HE CANNOT BLOCK: the guard branch is gated `&& !this.chudan`, and `executeReprisal()` returns false in chūdan, so Iron Guard Reprisal dies with the guard. Taking chūdan also clears muki. VERIFIED LIVE on :9100 — the stance changes Fwd/Down/Up+Special art to xcfwdh/xcdownh/xcuph, the neutral heavy to xcthrust and the light to xcslice. ⛔ BUT THE STANCE HAS NO VISUAL: the IDLE case tests `F.xidle1 !== undefined` and returns BEFORE the `p.chudan && F.xcentry1` entry branch and the `p.chudan && F.idle_chudan` hold branch, so idle_chudan (cell 132) and the 6-cell xcentry entry never draw. He looks identical in and out of the stance.  

| input | move | frame row | beats | art |
|---|---|---|---|---|
| F (Light, neutral, grounded, base stance) | Nukitsuke light cut (3-beat string) | `xnuki1..6` | 6 | DRAWN |
| Fwd + F (grounded) | Kirikomi (forward cut) | `glfwd1..8` | 8 | DRAWN |
| Back + F (grounded) | Hiki-giri (withdrawing cut) | `glback1..8` | 8 | DRAWN |
| Down + F (grounded) | Sune-giri (shin cut) | `gldown1..8` | 8 | DRAWN |
| Up + F (grounded) | Age-tsuki (rising thrust) | `glup1..8` | 8 | DRAWN |
| F (Light, neutral, CHŪDAN) | Four Fast Slices (chūdan light flurry) | `xcslice1..6` | 6 | DRAWN |
| Fwd / Back / Down / Up + F (CHŪDAN) | chūdan directional light (art/mechanic split) | xcslice1..6 (art) over the generic light box |  | ALIAS |
| G (Heavy, neutral, grounded, base stance) | Jōdan Kiri Otoshi (overhead cut) | xjodan1..6 (row is 8 cells; engine names only 1..6) |  | DRAWN |
| Fwd + G (grounded) | Chūdan Tsuki — DRIVE STAB | xctsuki1..6 (row is 8) |  | DRAWN |
| Back + G (grounded) | Nukiuchi — IAI QUICK-DRAW | xnukiuchi1..6 (row is 8) |  | DRAWN |
| Down + G (grounded) | Suso-Giri (hem cut) | `xsuso1..6` | 6 | DRAWN |
| Up + G (grounded, or airborne while rising vy < -180) | GYAKU KESA (reverse rising cut) | xkiriage1..6 — SAME CELLS as hup1..6 (48-53) |  | DRAWN |
| G (Heavy, neutral, CHŪDAN) | Chūdan multi-thrust (three tsuki) | `xcthrust1..6` | 6 | DRAWN |
| H (Special, neutral, grounded) | Armored Battle Tsuki (the thrust) | xbtsuki1..6 (row is 8) |  | DRAWN |
| Fwd + H (grounded) | SHEATH CHARGE | base: xbtsuki1..6 (alias) · chūdan: xcfwdh1..6 |  | ALIAS |
| Back + H (grounded) | Iai Quick-Draw (roster-convention route) | `xnukiuchi1..6` | 6 | ALIAS |
| Down + H (grounded) | HARAI OTOSHI (sweeping drop cut) — replaced the deleted GRAVEWAVE | base: xbtsuki1..6 (alias) · chūdan: xcdownh1..6 |  | ALIAS |
| Up + H (grounded, or rising vy < -180) | SKY CLEAVE (kirioroshi) | base: xbtsuki1..6 (alias) · chūdan: xcuph1..6 |  | ALIAS |
| Guard held (C) + G | SHADOW SLIP REVERSAL | `xslip1..6` | 6 | DRAWN |
| G within REPRISAL_WINDOW of blocking a hit | IRON GUARD REPRISAL | xbtsuki1..6 (alias) |  | ALIAS |
| Guard held (C) + H | BUNSHIN — the headsman's shadow | none (his own cells drawn dark + translucent) |  | FALLBACK |
| F in the air, neutral | Kesa-giri (aerial cut) + ZERO-G CUT | `aneu1..6` | 6 | DRAWN |
| Fwd / Back + F in the air | aerial cut (no directional aerial light) | `aneu1..6` | 6 | ALIAS |
| Down + F in the air | pogo dive poke | `aneu1..6` | 6 | ALIAS |
| Up + F in the air | air up-poke (roster-wide skyward thrust) | light3 — ONE static cell |  | FALLBACK |
| G in the air, neutral | aerial neutral heavy | `hneu1..6` | 6 | DRAWN |
| Fwd + G in the air | aerial forward heavy | hfwd1..6 — cells 56-58 are ALSO keyed xtsuki1..3 |  | DRAWN |
| Back + G in the air | aerial back heavy | `hback1..6` | 6 | DRAWN |
| Up + G in the air while rising (vy < -180) | GYAKU KESA (air-armed) | `xkiriage1..6 / hup1..6` | 6 | DRAWN |
| Down + G in the air | METEOR BREAK (roster-wide dive slam) | fall2 — ONE static falling cell |  | FALLBACK |
| H in the air (neutral / fwd / back / down) | armored overhead shockwave, airborne | xbtsuki1..6 (alias) — a PLANTED standing thrust drawn in mid-air |  | ALIAS |
| V (P2 K), bare press, grounded | CHŪDAN-NO-KAMAE — enter / drop the offensive stance | idle_chudan + xcentry1..6 exist but NEVER DRAW |  | MISSING |
| Up+V · Down+V · Back+V · Fwd+V | Muki-Kamae · Saya-Kamae · Kage-Kami · Shadow-Weave Anchor (roster-wide, read BEFORE the per-fighter split) | none |  | FALLBACK |
| C held (grounded, not in chūdan/muki) | Guard | block (hold) / block2 (impact) |  | DRAWN |
| C tapped | Kawarimi (substitution) | none (smoke + log) |  | FALLBACK |
| Down held (grounded) | Crouch | kneel — ONE cell |  | FALLBACK |
| C held + direction | Dodge roll | `roll_1..6` | 6 | DRAWN |
| F+G within 90ms (throw macro) | Throw | heavy1..heavy2 — two of the oldest cells on the sheet |  | FALLBACK |
| F / G / H while blade-locked | Blade-lock mash | xblkguard — ONE held cell |  | FALLBACK |
| getting hit | Hurt / stagger (not an input, listed because the row order is a known trap) | hurt (impact) -> hurt2 (stagger) -> hurt3 (settle) |  | DRAWN |

**Signature:** Nukiuchi / IAI QUICK-DRAW (Back+Heavy, and Back+Special is redirected to it) — a dash-through pass with the damage resolving on the notō, unblockable, free (no chakra) · CHŪDAN-NO-KAMAE offensive stance (V) — hits harder, cannot block · SHADOW SLIP REVERSAL (Guard+Heavy) — i-frame back slip; the counter box only spawns if the opponent was mid-attack on the press ('the read') · IRON GUARD REPRISAL (Heavy inside REPRISAL_WINDOW of a block) — 0.06s startup riposte, armored, spends DREAD · DREAD / THE EXECUTION — every clean heavy or special on a non-blocking foe stacks dread to 3; the next SPECIAL comes out x1.5 damage, x1.4 width, x1.2 height, 0.5s armor, and consumes it. Ambient orange ember tell while dread > 0; decays one stack per round-tick. · Chudan Tsuki DRIVE STAB (Fwd+Heavy) — armor-pierce/unblockable step-in · GYAKU KESA (Up+Heavy) — waki-hide rising counter-cut, his one true anti-air, launches

**Dead or missing:**

- `xuke1..7 (cells 257-263)` — UKE NAGASHI (flowing deflection) — zero references anywhere in web/index.html. Packed, unreachable. Canon calls it one of his three deflection lines; this tree has no deflect mechanic at all (`deflectsBlades` does not exist here — that shipped only in ~/shadowclash-fable-5).
- `xgedan1..8 (cells 190-197)` — GEDAN DECEPTION (low bait -> counter-thrust from the low guard) — zero references. Packed, unreachable. URONAME board 4.
- `xmetsu1..8 (cells 237-244)` — METSUBUSHI (blinding powder + strike) — zero references. Packed, unreachable. The BLINDED primitive (`blindTimer`) does not exist in this tree either, so the move has neither an input nor a mechanic here.
- `xitto1..7 (cells 215-221)` — ITTŌ GIRI CROUCH — zero references. Packed, unreachable.
- `xjam1..7 (cells 222-228)` — SWORD EVASION & JAMMING — zero references. Packed, unreachable.
- `xtaihen1..6 (cells 251-256)` — TAIHEN EVASION — zero references. Packed, unreachable. (Board note: beat 6 is HIM in a desaturated all-purple palette, not an opponent.)
- `xgkamae1..7 (cells 198-204)` — GEDAN-NO-KAMAE (low guard stance) — zero references. Packed, unreachable. No engine stance exists for it.
- `xcombo1..8 (cells 170-177)` — chūdan combo row — zero references. Packed, unreachable.
- `xclash1 (cell 169)` — the clash-spark cell (the '5 5' double panel = two Executioners) — zero references. Packed, unreachable.
- `xparry1..8 (cells 295-302)` — Packed on HIS sheet but the only branches that read `xparry*` are gated `p.spec.name === 'Kael'` / `p.spec.id === 5`. He never enters PARRY_STANCE (no id-0 branch sets it; the Saya auto-parry resolves inside takeDamage without a state). 8 cells unreachable.
- `xiai1..7 (cells 288-294)` — The older Iai row. `F.xnukiuchi1` is defined, so L11617 returns first and the xiai branch (L11621) plus the kneel/heavy_i fallback (L11623) are both permanently dead. 7 cells unreachable.
- `xcentry1..6 (cells 14,15,159,160,161,162)` — The drawn chūdan ENTRY. Unreachable: the IDLE case returns at `F.xidle1 !== undefined` (L12280) before ever testing `p.chudan && F.xcentry1` (L12308). VERIFIED LIVE — chūdan idle returns cell 209. Also note xcentry1/2 point at cells 14/15, pre-619 small cells.
- `idle_chudan (cell 132) + idle_chudan1 (cell 132, duplicate key) + idle_chudan2 (cell 9)` — The stance HOLD pose. Same cause as xcentry — L12317 is unreachable behind the xidle branch. `modeKey()` still gates the whole second form on this key existing, so the stance toggles but never shows. idle_chudan2 points at cell 9, an orphaned pre-619 cell.
- `special1..special7 (cells 78-84)` — Fully dead. specialCells() returns xbtsuki for id 0 in every non-lowCut/non-slip case, and the only other consumer — the PARRY_STANCE tail `[F.special1, F.special2]` at L11949 — is a state he cannot enter.
- `light1, light2, light4, light5 (cells 16,17,19,20)` — Unreachable. Grounded lights go to xnuki (base) or xcslice (chūdan); air lights go to aneu; the generic collector at L11454 and the kick tail at L11209 are both unreachable for him. Only light3 survives, as the air up-poke fallback.
- `heavy3 (cell 3)` — Unreachable. heavy1/heavy2 are reached only through the THROWING fallback `[F.heavy1, F.heavy2]`; nothing reads heavy3. (heavy_i1..i5 do not exist on this sheet at all, so several engine fallbacks that name them are dead here.)
- `aland1, aland2 (cells 113,114)` — ZERO occurrences of the string 'aland' in web/index.html. The landing tail has no reader — landing draws `kneel` instead (VERIFIED LIVE).
- `block1 (cell 321)` — Unreachable. The BLOCKING draw reads `F.blockhit ?? F.xblock2 ?? F.mblock2 ?? F.block2 ?? F.block`; block1 is named nowhere.
- `xtsuki1..3 (cells 56,57,58)` — The KEYS are unreachable — xctsuki wins the Drive Stab (L11604 before L11608), xcthrust wins the chūdan heavy (L11481 before L11486), xbtsuki wins the neutral special (L10379 before L10381). The CELLS still draw, because they are the same three cells as hfwd1..3 (air forward heavy). Duplicate naming, not orphan art.
- `row tails: xjodan7/8 (235,236) · xctsuki7/8 (286,287) · xnukiuchi7/8 (320,322) · xkiriage7/8 (54,55) · xbtsuki7/8 (151,152)` — Ten cells packed and never drawn. These five rows were delivered as 8-beat URONAME boards but every branch that reads them hardcodes a 6-cell list instead of collecting 1..N the way dirCells does. Two extra beats per move sitting dark.
- `run1, run2 (139,140) · roll (133) · jump (107) · idle (209) · idle2 (212)` — Duplicate keys, not orphan cells — each points at a cell that a live row already draws (run_clean1/run_clean4, roll_1, ajump1, xidle1, xidle4). The named keys themselves are never read: runCells prefers run_clean, the roll prefers roll_, the jump prefers ajump, the idle prefers xidle. `fall` (122) is the exception — it is dead in the JUMP path but IS reached by WALL_CLING (verified live).
- `INPUT WITH NO ART — Fwd+Special (Sheath Charge), Down+Special (Harai Otoshi), Up+Special (Sky Cleave), Iron Guard Reprisal` — Four distinct moves all draw xbtsuki1..6, the neutral special's cells. `xsheath*`, `xharai*`, `xlow*`, `xskycleave*`, `xsky*` and `xreprisal*` are all NAMED in the engine and all ABSENT from this sheet — six dead branches. Chūdan masks three of them (xcfwdh / xcdownh / xcuph are real), so the holes only show in base stance. VERIFIED LIVE.
- `INPUT WITH NO ART — air Down+Heavy (Meteor Break)` — No dive1..6, no hdown row, no kstomp. A 900ms three-phase move plays on the single `fall2` cell.
- `INPUT WITH NO ART — air Up+Light` — No upatk3 and no air2; falls to `light3`, one held cell, for the whole poke.
- `INPUT WITH NO ART — air Special (all directions)` — No sneu/sfwd/sback/sup/sdown and no air1..3, so a braced STANDING thrust pose (xbtsuki) is drawn hanging in mid-air — the exact defect the L11835 comment says it fixed, reopened by the Aug-21 sheet.
- `INPUT WITH NO ART — Crouch, Throw, Blade lock` — Crouch has no crouch_1..4 (draws `kneel`, one cell, then gets squashed); the throw has no attack_body/grab row (draws heavy1/heavy2, two pre-619 cells); the blade lock has no lock1..N (draws `xblkguard`, one cell) — the last is roster-wide and deliberate.
- `BEHAVIOUR HOLE — Down+Light and Back+Light lost their kick properties` — Because his sheet now carries gldown1/glfwd1/glback1, the `drew` check at L5131 skips executeKick entirely. Measured live: Down+Light is a MID box (oy 9) with no `low` and no `trip`, and Back+Light has no `behind`. He is the only fighter to lose the whole command-kick tier, and the in-game move list still advertises it.
- `STALE IN-GAME TEXT — MOVES_LIST['Executioner'] line 'Down/Fwd/Back+F — sweep · push · heel kicks' (web/index.html L16776)` — No longer true in this tree — those three inputs now play glfwd/glback/gldown. The training move list (press L) teaches a kit he does not have.
- `CHŪDAN ART/MECHANIC SPLIT — Fwd/Back/Down+Light in stance` — The 4-slice flurry ART plays over a single ordinary light BOX (trigger requires neutral axis, draw branch does not check direction), and glfwd/glback/gldown/glup become unreachable for as long as the stance is held. VERIFIED LIVE.

---

## EXILE

**Glass cannon, longest reach** · S/P/R/D **10/6/12/2** · she/her  
**Weapon:** Kusarigama (kama sickle + iron chain-ball / fundo)  
**Discipline:** Speed / Agility — the roster's only rope-physics zoner. Speed 10 (fastest body), jumpScale 1.12 (highest jumper), defense 3 and takes 1.25x damage (glass cannon). Roster id 7, spec.id === 7 is the gate on every branch below. Sheet: frameW 480 / frameH 368 / footY 280 / cols 125 / scale 0.4667.  
**Second form:** CHAMPION MODE — bare V (P2: K), grounded, not mid-attack. enterChampion() (web/index.html L2783-2797): requires a FULL CHAIN bar (champion === CHAMPION_MAX 100; gauge fills 1.6/dmg taken, 1.1/dmg dealt, L9489-9491), SPENDS it, and sets frenzyTimer = CHAMPION_DUR — the same state CPU Chain Frenzy uses: faster, recovery drains 1.5x (L3409), and the 1.25x fragility is suspended. Below full it refuses with a dud spark. NO ART AT ALL — no stance cell, no entry row, no idle swap; only the HUD pips (L17416) and FX say it is on. She is also the only fighter whose bare-V is a resource dump rather than a stance.  

| input | move | frame row | beats | art |
|---|---|---|---|---|
| Light (F / P2 I), grounded, no direction | Quick-Draw Slash (3-beat light string) | light3, light4, light5 (cells 31, 32, 33) |  | DRAWN |
| Fwd + Light, grounded | Push Kick | xkpush (cell 74) |  | DRAWN |
| Back + Light, grounded | Heel Kick | xkheel (cell 75) |  | DRAWN |
| Down + Light, grounded | Leg Sweep | xksweep (cell 73) |  | DRAWN |
| Up + Light (grounded, or within a jump still rising, vy < -180) | UP-FLICK | upflick1..3 (cells 21, 22, 23) |  | DRAWN |
| Double-tap a direction (shunshin dash), then Light — also fires up to IAI_WINDOW after the dash ends | IAIJUTSU CROSS (dash route) | light3, light4, light5 (cells 31, 32, 33) |  | ALIAS |
| Light while clinging to a side wall (ordinary cling or after a Chain Anchor) | Ninja Star Throw (x3 per airborne trip) | wallslide (cell 116) — held, no throw pose |  | MISSING |
| Air Light, no direction | Aerial Kama Slash | air1, xair2, air1 (cells 77, 78, 77) |  | DRAWN |
| Air fwd + Light | Diving Cut | air1, xairf, air1 (cells 77, 79, 77) |  | DRAWN |
| Air back + Light | Reverse Cut | air1, xairb, air1 (cells 77, 80, 77) |  | DRAWN |
| Air up + Light (holding Up while not rising hard) | Air Up-Poke | upatk3 (cell 81) |  | DRAWN |
| Air down + Light | Air Poke | airpoke1..2 (cells 29, 30) |  | DRAWN |
| Heavy (G / P2 O), grounded, no direction | Kusarigama Reach | xheavy1..5 (cells 58, 59, 60, 61, 62) |  | DRAWN |
| Fwd + Heavy, grounded | SIDE REACH | `xheavy1, xheavy2, xheavy5, xheavy5, xheavy3` | 5 | ALIAS |
| Back + Heavy, grounded | COUNTER-WEIGHT SNAP | cwsnap1..5 (cells 24, 25, 26, 27, 28) |  | DRAWN |
| Down + Heavy, grounded | LOW SLASH | lowslash1..4 (cells 8, 9, 10, 11) |  | DRAWN |
| Up + Heavy (grounded, or a jump still rising, vy < -180) | UP REACH | upreach1..5 (cells 16, 17, 18, 19, 20) |  | DRAWN |
| Air Heavy — neutral, fwd, or back | AIR HURL | airhurl1..4 (cells 12, 13, 14, 15) |  | DRAWN |
| Air up + Heavy | UP REACH (if still rising hard) / AIR HURL (otherwise) | upreach1..5 (16-20) or airhurl1..4 (12-15) |  | DRAWN |
| Air down + Heavy | SKY DOWN-SMASH | hdown2 (105) on the hang, hdown3 (106) on the plunge, hdown6 (109) on the landing hold |  | DRAWN |
| Special (H / P2 P), no direction, ground or air | HELI SPIN | xspin1..10 (cells 86-95) |  | DRAWN |
| Fwd + Special (grounded or air), a side wall 60-520px away | CHAIN-GRAPPLE SWING | xjump1..6 during the reel; light3, light4, light5 on the swing-around |  | ALIAS |
| Back + Special, grounded | IAIJUTSU CROSS (direct input) | light3, light4, light5 (cells 31, 32, 33) |  | ALIAS |
| Up + Special, grounded, within ANCHOR_RANGE of a side wall | CHAIN ANCHOR (ground yank) | wallslide (cell 116) |  | ALIAS |
| Up + Special, airborne, within ANCHOR_RANGE of a side wall | CHAIN ANCHOR | wallslide (cell 116) |  | ALIAS |
| Down + Special, grounded | SERPENT'S TONGUE | xspin1..10 (cells 86-95) |  | ALIAS |
| Air fwd + Special (no wall in grapple range) | AIR HURL (special tier) | xspin1..10 (cells 86-95) |  | ALIAS |
| Air back + Special | TRAILING CHAIN | xspin1..10 (cells 86-95) |  | ALIAS |
| Air up + Special (no wall in anchor range) | CHAIN REACH | xspin1..10 (cells 86-95) |  | ALIAS |
| Air down + Special | BALL DROP | xspin1..10 (cells 86-95) |  | ALIAS |
| Hold Guard (C / P2 M) + Special | BUNSHIN — THE ECHO | clone draws idle, idle2 (cells 101, 102); the caster keeps her current pose |  | ALIAS |
| Light + Heavy within 90ms (F+G / I+O), grounded, close range | Chain Grapple Throw | xgrap2, xgrap3, xgrap4, xgrap5, xgrap6, xgrap9, xgrap10 (53, 54, 55, 56, 57, 71, 72) |  | DRAWN |
| Light + Heavy while holding Back, grounded | Chain Grapple Throw (back throw) | xgrap2, xgrap3, xgrap4, xgrap5, xgrap8, xgrap9, xgrap10 (53, 54, 55, 56, 70, 71, 72) |  | DRAWN |
| Light + Heavy in the AIR, opponent within THROW_RANGE+15 horizontally and 90px vertically | AIR GRAB / SKY HARVEST | xgrap1, xgrap5, xgrap6, xgrap7, xgrap9 (52, 56, 57, 69, 71) |  | DRAWN |
| Hold Guard (C / P2 M) | Guard | block (cell 67); xblock2 (cell 68) while absorbing a hit |  | DRAWN |
| Tap Guard (C / P2 M) | Kawarimi (log substitution) | no dedicated cells — vanish + smoke, the log is its own object |  | MISSING |
| Guard + direction, or double-tap a direction with Down held | Kusarigama Slide (dodge roll) | slide1..4 (cells 96, 97, 98, 99) |  | DRAWN |
| Double-tap a direction (no Down) | Shunshin Dash — and it ARMS the Iaijutsu Cross | no dash row — run_clean / idle keep drawing |  | MISSING |
| V (P2: K), bare, grounded | CHAMPION MODE | none |  | MISSING |
| Up + V / Down + V / Back + V / Fwd + V | MUKI-KAMAE / SAYA-KAMAE / KAGE-KAMI / WEAVE ANCHOR (roster-wide stances) | none |  | MISSING |
| Jump (W / ArrowUp) | Acrobatic Jump Arc | xjump1..6 (cells 38-43) |  | DRAWN |
| Left / Right (walk or run) | Run cycle | run_clean1..8 (cells 44-51) |  | DRAWN |
| Hold Down, grounded | Crouch | crouch_1..4 (cells 110, 111, 112, 113) |  | DRAWN |
| Hold into a side wall while airborne | Wall cling / slide | wallslide (cell 116) |  | DRAWN |
| (reaction) being hit | Recoil | xhurt1..3 (cells 64, 65, 66) |  | DRAWN |
| (reaction) being swept / tripped | Trip-tumble | xroll1..4 (cells 34, 35, 36, 37) |  | DRAWN |
| (reaction) being thrown | Grabbed tumble | grabbed1..8 (cells 117-124) |  | DRAWN |
| (idle) | Breathing idle | xbreath1..3 (cells 101, 102, 103), ping-pong 1-2-3-2 |  | DRAWN |

**Signature:** IAIJUTSU CROSS — the full-board quick-draw blink; the corridor she crossed is the hitbox (executeIaijutsu, L8267) · HELI SPIN — the chain swung all sides, front + behind boxes + simulated orbit (L8122) · CHAIN-GRAPPLE SWING — sickle bites the wall, reels her in at GRAPPLE_SPEED, swing-around hits both sides (executeGrapple L8189 / finishGrapple L8230) · CHAIN ANCHOR — kusarigama sunk into a side wall, hands free, 3 ninja stars (executeChainAnchor L8623; Exile-only, Shin gets only the throwing half) · SERPENT'S TONGUE — 170px floor-skimming chain that trips (L7972) · UP REACH / SIDE REACH / COUNTER-WEIGHT SNAP — the grounded chain-zoning triangle (UPREACH vertical, SIDE_REACH horizontal, and a GAP box with a deliberate dead zone under it) · CHAMPION MODE — her second form, spends a full CHAIN bar

**Dead or missing:**

- `heavy_i1..5 (cells 1, 1, 4, 4, 1)` — DEAD ROW. heavyCells L10271 returns her xheavy1..5 for spec.id 7 before the generic heavy_i tail is ever reached, and no other site names heavy_i for her. Five keys, two pictures, zero draws.
- `xthrow1..3 (cells 5, 6, 7)` — DEAD ROW. The THROWING branch (L11999) prefers `F.xgrap2 !== undefined`, which she has, so the xthrow fallback arm is unreachable. Old-generation art superseded by the owner's grapple page at SHEET_V 373.
- `special1..7 (cells 86, 90, 93, 90, 93, 86, 86)` — DEAD NAMES. specialCells L10387 returns xspin1..10 for spec.id 7 before the generic `for (let i = 1; F['special'+i] ...)` collector runs. The cells themselves still draw (via xspin1/5/8), the seven names never do.
- `nrun1..8 (cells 44-51)` — DEAD NAMES — `F.nrun` appears NOWHERE in web/index.html. Exact duplicates of run_clean1..8, which is what runCells reads.
- `xlight3n, xlight4n, xlight5n (cells 31, 32, 33)` — DEAD NAMES — no reference anywhere in the engine. Exact duplicates of light3/light4/light5, which are what her light chain reads.
- `xlight4 (cell 0)` — DEAD NAME AND ORPHAN CELL. The only `F.xlight4` site (L11148) is the Executioner's chudan slice flurry, gated on `p.spec.id === 0 && p.chudan`. Cell 0 is referenced by no other key on her sheet, so it draws nowhere at all.
- `ksweep, kpush, kheel (cells 73, 74, 75)` — DEAD NAMES. The id-7 kick branch at L11192 returns xksweep/xkpush/xkheel first, so neither the `F.kpush3` sequence check nor the string-built `F['k' + p.kickKind]` lookup at L11202 is ever reached for her. Same cells, shadowed names.
- `kstomp (cell 76)` — DEAD ROW. All three sites that could name it for her are shadowed: the kick fallback (L11209, beaten by xksweep), the air-down light (L11279, beaten by airpoke1), and the slam fallback (L11556, beaten by hdown3 at L11554). Cell 76 draws nowhere.
- `kneel and xcrouch (both cell 100)` — DEAD. `F.kneel` is only reached via the CROUCH tail and the landT tail, and both are beaten by crouch_1..4 / crouch_3 (L12082, L12246). `F.xcrouch` is only the Low Slash fallback (L11571), beaten by lowslash1. Cell 100 draws nowhere.
- `roll (cell 35)` — DEAD NAME. STATE.ROLL takes her slide1..4 (L12091) and the tumble takes xroll1..4 (L12155), so `F.roll ?? F.jump` (L12153) and `F.roll ?? F.hurt` (L12188) are both unreachable for her. Cell 35 still draws as xroll2.
- `hurt, hurt2, hurt3 (all cell 63)` — DEAD ROW AND DEAD CELL. STATE.STUNNED is caught by the xhurt1/2/3 branch (L12222) and STATE.THROWN by grabbed1..8 then xhurt1 (L12013/L12017). Cell 63 — described as a confident fighting stance that also served two run frames — now draws nowhere.
- `jump, jump1, jump2 (84, 84, 85) and fall, fall2 (82, 83)` — DEAD NAMES. STATE.JUMP returns her xjump1..6 arc at L11050 for spec.id 7, which covers the fall bands too, so every vy fallback below it (L11130-11133) is unreachable. Only the JUMP-state grapple ride reaches xjump, never these.
- `air2, air3 (both cell 77)` — DEAD NAMES. Her three air-light arrays name air1 explicitly ([air1, xair2/xairf/xairb, air1]); air2 and air3 are only reached by the `p.spec.id <= 5` generic branch (L11395/L11686), which excludes id 7. Cell 77 still draws via air1.
- `block2 (cell 67)` — DEAD NAME. The BLOCKING tail (L12051) only returns F.block2 when `F.blockhit !== undefined`, and she has no blockhit key — so the impact beat goes to xblock2 and the held beat to F.block. Same cell as `block`, so nothing is lost on screen.
- `hdown1, hdown4, hdown5 (cells 104, 107, 108)` — UNREACHABLE CELLS. The Sky Down-Smash draws exactly hdown2 (slamPhase 1) and hdown3 (slamPhase 2) at L11554-11555, and after touchdown attackAnim is nulled so attackFrame's follow-through hold returns arr[arr.length-1] = hdown6. Three of the six packed beats never appear. Verified: startSlam sets slamPhase = 1 in the same call, so no window exists where attackDir 'down' reaches dirCells with slamPhase still 0.
- `INPUT WITH NO ART: Light from a wall cling (3 ninja stars)` — throwWallProjectile opens a 0.45s wallThrowT window, but the only branch that reads wallThrowT is Oni's wallneedle1..8 (L10995). She throws all three stars out of a frozen wallslide pose. Owed: a wall-throw row (Oni's `wallneedle` is the precedent, 8 cells).
- `INPUT WITH NO ART: shunshin dash (double-tap direction)` — No dash row on her sheet, so the fastest body in the roster traverses in her run or idle cell. Notable for her specifically because the dash is the setup for the Iaijutsu Cross.
- `INPUT WITH NO ART: CHAMPION MODE (bare V/K) and all four V+direction stances` — Her second form has zero cells — no entry beat, no stance idle, no exit. Only the HUD pips and particle FX indicate it. The four roster-wide V+direction stances (Muki, Saya-Kamae, Kage-Kami, Weave Anchor) are equally unanimated on every fighter.
- `FOUR SPECIALS SHARE ONE PICTURE: Serpent's Tongue, Trailing Chain, Chain Reach, Ball Drop (+ the air-fwd Air Hurl special)` — None of the five sets an art flag or has an s*/gs* dir row, so specialCells returns the 10-beat Heli Spin for every one of them. The L7826 comment claims the air-fwd and air-up specials are wired to 'airhurl/upreach... real rows sitting unused' — that is TRUE of the mechanics and FALSE of the art: airhurl is reached only by the air HEAVY, upreach only by Up+HEAVY. Five distinct moves, one drawing.
- `TWO MOVES SHARE THE LIGHT CHAIN: Iaijutsu Cross (both routes) and the Chain-Grapple swing-around` — executeIaijutsu and finishGrapple both set state = ATTACK_LIGHT after clearMoveArt, so her signature blink and her grapple arrival both draw light3/4/5. The cross in particular is her spec's headline move and has no cells of its own.
- `STALE METADATA: exile.json `single_cell_names`` — The note reads 'hurt/hurt2/hurt3 -> 113, air1/2/3 -> 127, block/block2 -> 117, special1/6/7 -> 136'. Measured from the shipped file the real values are 63, 77, 67 and 86/86/86 — and cols is 125, so cells 127 and 136 DO NOT EXIST. The note's conclusion (legacy names superseded by the x-rows, unreachable not broken) is correct; every cell number in it is wrong.

---

## MOKURAI

**Flexible all-rounder** · S/P/R/D **7/7/7/7** · he/him  
**Weapon:** Prayer Beads / Bare Hands (spec.weapon string; identity lock: bead-wrapped fists, NO bo staff and never had one)  
**Discipline:** Sage of Nothingness / Area — "cyclone monk": orbital, area, counter-and-return. spec.id 6, stats speed 5 / power 7 / reach 8 / defense 8, scale 0.4667, frameW 300 frameH 248 footY 218, 221 cols, 274 frame keys over 221 cells.  
**Second form:** THE CRACK — his second form, and it is NOT on the V key. Entered by holding Down+Guard for 2.0s (`meditateTimer >= 2.0`, engine L3571-3600) with a FULL karma bar (karma >= KARMA_MAX 15): the meditation goes wrong and the monk cracks instead of going gold. Spends all 15 karma, once per round (`enlightenUsed`), CRACK_DUR 6s, every hitbox lands CRACK_FEINT 0.12s late behind an ash-white feint tell, damage taken x1.20, karma cannot charge in-mode, and it ends in a punishable SPENT KNEEL (CRACK_SPENT 0.8s, feint5 -> feint6). Transformation plays crack1..6 (0.55s, no stun). Same channel on a SHORT karma bar gives ENLIGHTENMENT instead: 5s of auto-dodge/auto-block, +3 damage on every hit, specials x1.30 box, once per round. Bare V does NOTHING for him — modeKey() falls through to a `idle_chudan` gate his sheet has no cell for. V+direction still gives him the four roster-wide stances (Up = Muki, Down = Saya but it DUD-SPARKS because saya needs a metal edge and he has none, Back = Kage-Kami echo, Fwd = Weave anchor).  

| input | move | frame row | beats | art |
|---|---|---|---|---|
| Light (F / P2 I) — neutral, or with Up held, grounded | TAP-TAP-SWEEP-UPPERCUT (the bare-hand light chain) | `blight1..5` | 5 | DRAWN |
| Fwd + Light (grounded) | Front Kick (command-kick tier, 'push') | `bkfront` | 1 | DRAWN |
| Back + Light (grounded) | Heel Kick (command-kick tier, 'heel') | `bkheel` | 1 | DRAWN |
| Down + Light (grounded) | Leg Sweep (command-kick tier, 'sweep') | `bksweep` | 1 | DRAWN |
| Dash (double-tap direction) + Light | THE MASK EATS / stone-mask headbutt | canon_headbutt (cell 32) |  | DRAWN |
| Heavy (G / P2 O) — neutral, grounded | DESCENDING HALO (overhead bell slam) | `bheavy1..5` | 5 | DRAWN |
| Fwd + Heavy (grounded) | STEPPING PALM | `mpalm1..5` | 5 | DRAWN |
| Down + Heavy (grounded) | LOW HAMMER (both fists to the floor) | `mhammer1..5` | 5 | DRAWN |
| Back + Heavy (grounded) | SAGE'S PALM (the crossing palm blast) | `mblast1..5` | 5 | DRAWN |
| Up + Heavy (grounded, or rising with vy < -180) | BELL RINGER (planted anti-air) | `mbell1..5` | 5 | DRAWN |
| Special (H / P2 P) — neutral, grounded OR airborne | PRAYER HALO | bspec1..5 (his STILLNESS row) |  | DRAWN |
| Fwd + Special (grounded) | PRAYER ORBIT | `bspec1..5` | 5 | ALIAS |
| Back + Special (grounded) | ZEN REFLECT (counter stance) | special1 -> special2 (= canon_guard cell 33, canon_burst cell 30) |  | ALIAS |
| Back + Special that CATCHES a hit | ZEN COUNTER (the answer) | `bspec1..5` | 5 | ALIAS |
| Up + Special (grounded) | BEAD SNARE | `bspec1..5` | 5 | ALIAS |
| Down + Special (grounded) | TEMPLE BELL | `bspec1..5` | 5 | ALIAS |
| air Light — neutral | Air bead-fist punch | `bair1..3` | 3 | DRAWN |
| air Fwd + Light | AIR LUNGE (forward bead-fist drive) | `mairf1/mairf2` | 2 | DRAWN |
| air Back + Light | Reverse elbow / turning air poke | `mairb1/mairb2` | 2 | DRAWN |
| air Down + Light | DIVING FIST | `mdive1..3` | 3 | DRAWN |
| air Up + Light | AIR UP-POKE (bead-wrapped fist driven skyward) | upatk3 (cell 170) |  | DRAWN |
| air Heavy — neutral (and Up when the Bell Ringer latch is not armed) | AIRBORNE FIST DRIVE | `mstrike1..5` | 5 | DRAWN |
| air Fwd + Heavy / air Back + Heavy | Air heavy (no directional variant) | `mstrike1..5` | 5 | ALIAS |
| air Down + Heavy | METEOR BREAK (roster-wide dive slam) | hdown2 (hang) -> hdown3 (plunge) |  | DRAWN |
| air Fwd + Special | FALLING PALM | `bspec1..5` | 5 | ALIAS |
| air Back + Special | TURNING HEEL | `bspec1..5` | 5 | ALIAS |
| air Up + Special | SKY SNARE (the air catch) | `bspec1..5` | 5 | ALIAS |
| air Down + Special | BELL TOLL (he becomes the bell) | `bspec1..5` | 5 | ALIAS |
| Light + Heavy within 90ms (F+G / I+O, or pad trigger) | Throw — seize, haul across the hip, release | `mthrow1..3` | 3 | DRAWN |
| Being thrown by the opponent | Grabbed tumble | `grabbed1..8` | 8 | DRAWN |
| Hold Guard (C / P2 M) | Guard | block (cell 175); mblock2 (cell 176) on the impact beat |  | DRAWN |
| Guard + direction | Dodge roll | `mroll1..4` | 4 | DRAWN |
| Tap Guard (C / P2 M) | Kawarimi (substitution) | — (universal vanish, no fighter art) |  | FALLBACK |
| Hold Guard + Special | BUNSHIN (shadow clone, 30 stamina) | kneel (cell 180) |  | DRAWN |
| Hold Down + Guard 2.0s (karma < 15) | ENLIGHTENMENT | mmed1..5 (the channel) |  | DRAWN |
| Hold Down + Guard 2.0s at 15/15 KARMA | THE CRACK (second form) | crack1..6 (transformation) |  | DRAWN |
| Passive — blocking / armoring / parrying | KARMA | — (engine pips, gold, at 5 / 10 / 15) |  | FALLBACK |
| Hold Down (grounded) | Crouch | `crouch_1..4` | 4 | DRAWN |
| Jump (W / ArrowUp) | Jump arc | `bjump1..4` | 4 | DRAWN |
| Walk / Run (A-D / arrows) | Run cycle | `brun1..4` | 4 | DRAWN |
| Neutral standing | Idle (he breathes) | `bidle1..4` | 4 | DRAWN |
| Jump into a wall | Wall cling | mwall1 (catch) / mwall2 (slide) |  | DRAWN |
| Taking a hit | Hurt | hurt -> mhurt2 -> mhurt3 |  | DRAWN |
| V (P1) / K (P2) — bare, no direction | — nothing happens | — |  | MISSING |
| V + Up / V + Back / V + Fwd | MUKI / KAGE-KAMI echo / WEAVE ANCHOR (roster-wide stances) | — (no Mokurai-specific art) |  | FALLBACK |
| CRACKED: Light (any grounded direction that is not a kick) | Cracked light chain | `bpray1..6` | 6 | DRAWN |
| CRACKED: Fwd + Light / Back + Light / Down + Light | Cracked kicks — spurn / bheel / arake | spurn1-2 (push), bheel1-2 (heel), arake1-2 (sweep) |  | DRAWN |
| CRACKED: Heavy (neutral) | UNMADE | `unmade1..6` | 6 | DRAWN |
| CRACKED: Fwd + Heavy | THE MASK EATS x3 | `meats1..6` | 6 | DRAWN |
| CRACKED: Back + Heavy | HOLLOW PALM | `hpalm1..6` | 6 | DRAWN |
| CRACKED: Down + Heavy | LOW HAMMER (mechanics unchanged) — GRAVEL SWEEP art never plays | mhammer1..5 (gravel1..6 is unreachable) |  | ALIAS |
| CRACKED: Up + Heavy | BELL RINGER (mechanics unchanged) — 'BELL RINGER, WRONG' art never plays | mbell1..5 (bring1..6 is unreachable) |  | ALIAS |
| CRACKED: Special (neutral, grounded) | HOLLOW HALO | `hhalo1..6` | 6 | DRAWN |
| CRACKED: Fwd + Special (grounded) | BEAD LASH | `blash1..6` | 6 | DRAWN |
| CRACKED: Back + Special (grounded) | CRACKED REFLECT (he offers his face) | crefl1/crefl2 stance; crefl3..6 on the catch |  | DRAWN |
| CRACKED: Up + Special (grounded, or rising) | SNARE, WRONG END | `snarew1..6` | 6 | DRAWN |
| CRACKED: Down + Special (grounded) | LAUGHING BELL | `lbell1..6` | 6 | DRAWN |
| CRACKED: Down + Special (airborne) | BELL TOLL, WRONG | btoll1 (hang) -> btoll2 (plummet) -> btoll3 (landed sprawl) |  | DRAWN |
| CRACKED: Light + Heavy throw | "SIT." | `sit1..3` | 3 | DRAWN |
| CRACKED: neutral / run / jump / land / guard / stun | Cracked form states | hidle1..6, scut1..6, dbell1..5, dbell6, cguard1-2, cguard3..6 |  | DRAWN |
| CRACKED: any attack (passive) | Feint tell | feint1 (twitch), feint5/feint6 (spent kneel) |  | DRAWN |
| CPU only — Mokurai below 40% HP as the Second Door boss | Boss ENLIGHTENMENT / boss CRACK | `mmed / crack1..6` | 6 | DRAWN |

**Signature:** PRAYER HALO (neutral Special — planted gold AoE bloom, 88x78) · TEMPLE BELL (Down+Special — rings BOTH sides, the roster's only true crossup answer) · BELL RINGER (Up+Heavy — planted anti-air, 150px tall box, launchVy -420, feet never leave the floor) · SAGE'S PALM (Back+Heavy — the slow crossing palm projectile) · BEAD SNARE (Up+Special — his one pull, wire projectile that yanks the mark in) · ZEN REFLECT (Back+Special — 8-frame strict parry; a catch answers with the in-place gold burst, +6 karma) · KARMA (half of every hit he blocks/armors/parries is stored, max 15, and returns on his next heavy or special) · THE MASK EATS (cracked Fwd+Heavy — the stone-mask headbutt gone rabid, three chained lunges)

**Dead or missing:**

- `gravel1..6 (cells 140-145)` — UNREACHABLE. Its draw branch (L10885) is `p.spec.id === 6 && p.cracked && p.lowAtkAnim`, but `lowAtkAnim` is set in exactly one place — L6480, inside a `this.spec.id === 7` (Exile) branch. Mokurai can never set the flag, so his cracked Down+Heavy silently plays mhammer1..5 and six drawn cells are stranded. The mechanic branch that ought to set it is L6220 (lowHammer).
- `bring1..6 (cells 152-157)` — UNREACHABLE — shadowed. L11506 (`upAtkAnim && F.mbell1 !== undefined`) returns before L11509-11514 ever runs, and his sheet HAS mbell1. So 'BELL RINGER, WRONG' never draws; cracked Up+Heavy plays the calm mbell row. Same class of bug the file already documents twice (Oni's dashatk vs lunge, Exile's upatk3).
- `SAGE'S PALM aim angles: straight-up and down-diagonal` — Two of the four coded aims are dead inputs. The palmBlast branch (L6232) only fires on `axisH === -facing`, so `up && axisH === 0` (straight up) can never be true — that press latches the BELL RINGER instead. And `dn` can never be true because the LOW HAMMER branch (L6220) tests bare isDownPressed() and sits ABOVE it, eating Back+Down+Heavy. The in-game move list still advertises "hold Up/Down to aim"; only Up works.
- `canon_palm (28), canon_beads (29), canon_idle (34), canon_kick (31)` — Four of his seven original shipped cells are now referenced by nothing. The engine names only canon_headbutt; canon_guard and canon_burst survive by accident because special1/special2 alias them in the parry stance. light1/2/5 point at canon_palm and light3/4 at canon_beads, but the whole light* family is shadowed by blight, so those two pictures never reach the screen.
- `light1..5, air1..3, heavy_i1..5, special3..7, run_clean1..8` — Legacy generic rows, all shadowed by his own rows (blight / bair+mairf+mairb+mdive / bheavy+mstrike / bspec / brun). None of them can draw for him. special1 and special2 are the only survivors of the special* family.
- `ksweep (41), kheel (43), kpush (42), kstomp (181)` — Shadowed by the Mokurai kick branch at L11161 (bksweep / bkheel / bkfront) and by mdive/hdown3 on the air-down and meteor paths. Four dead cells.
- `mbair1/mbair2 (167/168), mapex (164), mdive bare (171), hdown4 (185), bcrouch (180), xcrouch (180), bhurt (172), bblock (175), block2 (175), roll (178), hurt2/hurt3 (172), wallslide (220), idle/idle2 (204), jump/jump1/jump2 (162/163), fall/fall2 (165/166), feint2/feint3/feint4 (111-113)` — Packed keys with no reachable reference. Most are byte-aliases of a cell that IS drawn under another name (mbair = mairf, mapex = bjump3, bcrouch/xcrouch = kneel, bhurt = hurt, bblock/block2 = block, roll = mroll2), so nothing is visually missing — but wallslide (220) is a UNIQUE cell that nothing can ever draw, because mwall1/mwall2 take the WALL_CLING case at L10985 first. feint2-4 are three unique cracked cells with no addressing line.
- `glneu / glfwd / glback / gldown / glup` — MISSING entirely — he carries none of the drawn ground-directional Light rows. All four of his directional grounded Lights therefore resolve to the one-cell command-kick tier (bkfront / bkheel / bksweep), and Up+Light has no kick mapping at all so it just replays the neutral chain. Only the Executioner and Oni carry gl* rows in this tree.
- `lock1..N (blade lock)` — MISSING — like the rest of the roster, he has no blade-lock cells. STATE.BLADE_LOCK (L10944) falls to the deliberate single held guard cell (F.block), which the code marks as a placeholder so the gap stays visible.
- `air Fwd + Heavy / air Back + Heavy` — No art and no mechanic of their own. The Mokurai air block (L5195) matches only attackDir null/'up' for Heavy, and the Stepping Palm / Low Hammer / Sage's Palm branches are all isGrounded-gated, so both inputs fall to the generic air heavy and re-draw mstrike1..5.
- `Bare V (mode key)` — Dead input. modeKey() L2765 gates the fall-through on an `idle_chudan` cell he does not have, so a bare V press does literally nothing and gives no dud spark. V+Down (Saya) at least refuses visibly.
- `mairf / mairb comment drift` — Not dead, but mis-documented in a way that will get 'fixed' wrongly. L7825 and L7830 claim mairf1/2 and mairb1/2 are the Falling Palm's and Turning Heel's rows (air fwd/back SPECIAL). They are not — both draw lines (L11296/11297) sit inside `case STATE.ATTACK_LIGHT`, so those two rows belong to air fwd/back LIGHT, and the two air specials actually draw bspec1..5.

---

## ONI

**Final boss — BENCHED** · S/P/R/D **—** · he/him  
**Weapon:** Tekko-Kagi Claw — RIGHT HAND ONLY (left hand wrapped, empty). One katana + one bo staff crossed on his back as silhouette only; the staff moveset was deleted, so nothing but the claw, the razor wire and the needles/knives is ever swung.  
**Discipline:** The Founder — author of all six schools the roster fights with; story-canon final boss / "the LAST door" (currently out of BOSS_TAIL = [7,6] while his art is rebuilt). Engine archetype string: "Acrobat / Rushdown". Stats speed 9 / power 8 / reach 6 / defense 6, jumpScale 1.10, runAnimScale 0.8, SPECIAL_COST 25.  
**Second form:** NONE. `modeKey()` L2727-2765: Oni's bare-V staff/club second form was DELETED (owner, Aug 2026 — "the club is NOT his moveset"). He falls through to the chudan gate, which needs an `idle_chudan` cell his sheet does not have, so bare V is a silent no-op. `mode2` stays false all match. Only the four ROSTER-WIDE directional V stances still fire for him (V+up toggleMuki, V+down toggleSaya, V+back castKageKami, V+fwd weaveAnchor) — those are not his. Consequence: his second-mode string art (kick2/kick3) and the bostrike/bosweep staff rows can never draw.  

| input | move | frame row | beats | art |
|---|---|---|---|---|
| (none) — standing | Idle | stand1..6 (cells 0-5) |  | DRAWN |
| A / D (P2 arrows) — walk / run | Run cycle | run_clean1..10 (391-400) |  | DRAWN |
| W (P2 ArrowUp) — neutral jump | Jump / double jump | ajump1..6 (12-17) |  | DRAWN |
| W while holding forward | Front cartwheel (jump forward) | cart1..6 (135-140) |  | ALIAS — identical cells to roll_1..6 (dodge roll) and glfwd1..6 (Fwd+Light) |
| W while holding back | Backflip evasion (jump backward) | bflip1..6 (141-146) |  | ALIAS — the same six cells the away-roll uses |
| S (P2 ArrowDown) held on the ground | Crouch | crouch_1..4 (19,20,20,21) |  | DRAWN |
| double-tap A/A or D/D | Shunshin dash | blur1,2,5,6 (all = cell 0) |  | ALIAS — every blur cell points at cell 0, the IDLE pose |
| hold C (P2 M, pad shoulder) | Guard | guard1 / guard3 (27 / 29) |  | DRAWN (only 2 of the 6 packed cells are read) |
| hold C + toward the foe | Dodge roll (through) | roll_1..6 (135-140) |  | ALIAS — same cells as cart1..6 and glfwd1..6 |
| hold C + away from the foe | Dodge roll (backflip evasion) | bflip1..6 (141-146) |  | ALIAS — same cells as the backward jump |
| tap C (P2 M) | Kawarimi (log substitution) | — (no row) |  | FALLBACK |
| into a side wall while airborne | Wall cling | wallslide (277) |  | DRAWN |
| F (Light) while clinging to a wall | Wall needle toss | wallneedle1..8 (279-286) |  | DRAWN |
| W off a wall | Wall kick-off | walljump (278) |  | DRAWN |
| F (neutral, grounded) — string beat 1 | Knife poke | glneu1..2 (33,34) |  | ALIAS — glneu1/2 point at light1/light2 |
| F, F (grounded, within 0.55s) — string beat 2 | Body jab | punch21,punch22 (35,36) |  | ALIAS — the same cells as light3/light4 |
| F, F, F (grounded) — string beat 3 | Rising upper (LAUNCHER) | punch31,punch32 (37,38) |  | ALIAS — the same cells as light5/light6 |
| Fwd + F (grounded) | Cartwheel claw (Fwd Light) | glfwd1..6 (135-140) |  | ALIAS — the same six cells as cart1..6 and roll_1..6 |
| Back + F (grounded) | Backflip claw (Back Light) | glback1..10 (39-48) |  | DRAWN — his only fully unique grounded Light row |
| Down + F (grounded) | Sweep kick (low, trips) | ksweep (cell 0) |  | ALIAS — ksweep points at cell 0, the IDLE pose. `gldown` is MISSING from the sheet. |
| Up + F (grounded) | Up light (no drawn row) | light1..5 (33-37) |  | ALIAS — the generic light collector |
| dash (double-tap dir) then F | LUNGE CLAW (dash attack) | lunge1..6 (all = cell 0) |  | ALIAS — every lunge cell points at cell 0, the IDLE pose |
| G (neutral, grounded) | Claw combo (neutral Heavy) | hfwd1..20 (65-84) |  | DRAWN — the full 20-frame strip |
| Fwd + G (grounded) | CLAW STRIKE | ghfwd1..20 (65-84) |  | ALIAS — byte-for-byte the same twenty cells as hfwd / the neutral heavy |
| Back + G (grounded) | Reversal cut | ghback1..10 (49-58) |  | DRAWN (shared with the AIR back heavy hback, same cells; kick21-23/kick31-33 also alias 49-54) |
| Down + G (grounded) | CLAW SWEEP | ghdown1..8 (85-92) |  | DRAWN — unique cells (note: `hdown`, the air row, is a DIFFERENT eight cells, 323-330) |
| Up + G (grounded) | Rising launcher | ghup1..6 (59-64) |  | ALIAS — the same six cells as hup (air up heavy) and gsup (Rising Claw) |
| H (neutral, grounded, foe ≤132px) | RAZOR WHIP | whip1..6 (99-104) |  | ALIAS — the first six cells of special1..8 |
| H (neutral, grounded, foe >132px) | WIRE SHOT | special1..8 (99-106) |  | DRAWN — his own row |
| Fwd + H (grounded) | PHANTOM DASH | special1..8 (99-106) |  | ALIAS — borrows the WIRE SHOT row; `gsfwd` is MISSING from the sheet |
| Back + H (grounded) | REVERSE WIRE THROW / ANCHOR SLIP | gsback1..6 (93-98) |  | DRAWN — unique cells |
| Down + H (grounded OR airborne) — charges 1 and 2 | SMOKE BOMB | gsdown1..10 (331-340) grounded / sdown1..10 (same cells) airborne |  | DRAWN (gsdown and sdown are the identical ten cells) |
| Down + H after both charges are spent, grounded | STOMP IMPACT | special1..8 (99-106) |  | ALIAS — the wire-shot row |
| Down + H after both charges are spent, airborne | CURSED BURST | sneu1..8 (99-106) |  | ALIAS — sneu points at the same eight cells as special1..8 |
| Up + H, still rising out of his own jump (vy < -180, jumpsLeft >= 1) | RISING CLAW | gsup1..6 (59-64) |  | ALIAS — the same six cells as hup / ghup |
| Up + H while FALLING (outside the launch window) | CURSED BURST (fallback) | special1..8 (99-106) |  | ALIAS — `sup` has never existed on his sheet |
| Fwd + H within 0.55s of a Special CONNECTING | KATANA EXECUTION (wire conversion) | kdraw1..6 + kslash1..6 (all twelve = cell 0) |  | ALIAS — every kdraw and kslash cell points at cell 0, the IDLE pose |
| Back + H during a live wire bind | CLAW EXECUTION — DOES NOT EXIST | wclaw1..6 — NOT PACKED |  | MISSING ⚠ |
| H with no direction during a live wire bind (grounded) | SHORT-WIRE SLICE — DOES NOT EXIST | wslice1..3 — NOT PACKED |  | MISSING ⚠ |
| H during a wire bind, both airborne | DUAL KNIVES | knives1..6 (all = cell 0) |  | ALIAS — all six cells are cell 0, the IDLE pose |
| H during a wire bind, he is airborne and the foe is GROUNDED | PULLEY SLICE — DOES NOT EXIST | wslice1..3 — NOT PACKED |  | MISSING ⚠ |
| (the 0.55s bind window itself, between the Special and the conversion) | Wire bind hold | wire1..3 (all = cell 0) |  | ALIAS — all three cells are cell 0, the IDLE pose |
| F in the air, no direction | Claw whirl (neutral air) | aneu1..16 (147-154, 341-348) |  | DRAWN — the longest row on his sheet (first 8 cells shared with afwd/air/aspin) |
| Fwd + F in the air | Forward air claw | afwd1..8 (147-154) |  | ALIAS — cells 147-154 are also aneu1..8, air1..3 and aspin1..6 |
| Back + F in the air | Reverse air claw | aback1..8 (307-314) |  | DRAWN — unique cells |
| Up + F in the air | HIGH KICK (air up light) | airkick1..6 (349-354) |  | DRAWN — unique cells |
| Down + F in the air | Falling knife throw (down air) | adown1..6 (355-360) |  | DRAWN — unique cells |
| G in the air, no direction | Neutral air heavy | hneu1..9 (155-163) |  | DRAWN — unique cells |
| Fwd + G in the air | Forward air heavy | hfwd1..20 (65-84) |  | ALIAS — the same twenty cells as the ground neutral/Fwd heavy |
| Back + G in the air | Back air heavy | hback1..10 (49-58) |  | ALIAS — the same ten cells as ghback (grounded Back+Heavy) |
| Up + G in the air | Up air heavy | hup1..6 (59-64) |  | ALIAS — the same six cells as ghup and gsup |
| Down + G in the air | METEOR BREAK (dive slam) | dive1..6 (180-185) |  | DRAWN — unique cells, and the only fighter with a `dive` row |
| H in the air, neutral / fwd / back | AIR SPIN | aspin1..6 (147-152) |  | ALIAS — cells 147-152 are also air1..3 + afwd4..6 + aneu4..6 |
| F + G within 90ms (pad trigger), grounded | Shoulder throw | grab1..10 (361-370) |  | DRAWN — unique cells |
| F + G within 90ms, airborne | SKY HARVEST (air throw) | grab1..10 (361-370) |  | ALIAS — the same row as the grounded throw |
| getting up after being thrown | Get-up | getup / getup2 (both = cell 0) |  | ALIAS — both cells are cell 0, the IDLE pose |
| any hit taken | Hurt / flinch | hurt, hurt2, hurt3 (all = cell 32) |  | ALIAS — three keys, one cell |
| hold C + H (P2 hold M + P) | BUNSHIN — ash effigy | — (no row) |  | FALLBACK |
| G, G, G, F, G, G, F, F — each press within 0.7s of the last | Hand-seal sneak attack | handseal1..6 (166-171) |  | DRAWN — unique cells |
| V (P2 K) | — no second form | — (no row) |  | MISSING |
| G while a fresh block is still hot / hold C + G | — Reprisal and Shadow Slip do not exist for him | — (no row) |  | MISSING |

**Signature:** WIRE SHOT (230px) / RAZOR WHIP (≤132px) — one neutral Special split by distance; both open a 0.55s WIRE BIND · Wire-bind executions: KATANA EXECUTION (fwd), CLAW EXECUTION (back), SHORT-WIRE SLICE (neutral), DUAL KNIVES / PULLEY SLICE (air) · PHANTOM DASH — Fwd+Special, hardest quick-draw in the game (21*pow/6 = 28.0) but only inside 92px, and the screen BLACKS OUT · RISING CLAW — Up+Special anti-air with 0.16s invuln startup (needs the launch window: Up IS the jump key) · MID-AIR / GROUND SMOKE BOMB — Down+Special, blind only, hard cap of 2 per round · METEOR BREAK — air Down+Heavy dive slam, his own drawn dive1..6 · Hand-seal sneak attack — the 8-press dial H,H,H,L,H,H,L,L inside 0.7s gaps · Front CARTWHEEL / BACKFLIP as grounded Light attacks and as his jump arcs · Wall cling -> needle toss (his projectile is `needle`, not kunai or stars)

**Dead or missing:**

- `dashatk1..8 (cells 315-322) — DEAD, and it is the worst one` — Eight REAL drawn cells, unreachable. The dash-attack branch at L5023 is gated `dsh.frames.dashatk2 !== undefined && dsh.frames.lunge1 === undefined`. lunge1 IS defined, so this branch is skipped and the LUNGE CLAW below it wins — except lunge1..6 are all packed as cell 0 (idle). A placeholder row is beating real art. The merge comment says 'six drawn beats from the owner's own board beat two cells from the older cut', which was true of a sheet where lunge held real cells; on THIS sheet it is false.
- `lunge1..6, blur1..6, wire1..3, kdraw1..6, kslash1..6, knives1..6, bostrike1..6, bosweep1..6, divekick1..2, roll/roll2, slide1..2, getup/getup2, ksweep, kstomp, kheel, kpush — all point at CELL 0` — Sixteen rows / 60 keys packed as the IDLE cell. Everything the engine routes to them draws him standing still: the dash (blur), the dash attack (lunge), the whole wire-bind window (wire), the katana execution (kdraw+kslash), the dual knives (knives), the Down+Light sweep (ksweep) and the post-throw get-up (getup). These are the un-repacked remains of the older cut — the rows were kept so the code could find them and the cells were never re-pointed.
- `wclaw1..6 and wslice1..3 — NEVER PACKED` — Three of his five wire-bind conversions are gated `man.frames[row+'1'] !== undefined` and these keys do not exist, so CLAW EXECUTION (Back), SHORT-WIRE SLICE (neutral — the owner's own default, Aug 13) and PULLEY SLICE (air vs grounded foe) all silently fall through to an ordinary Special. The in-game move list advertises all three. `wclaw.gif` and `wslice.gif` sit unpacked in RECOVERY/oni-founder/.
- `athrow1..10 (cells 117-126) — DEAD` — `athrowAnim` is never assigned true anywhere in web/index.html — the only two assignments (L2309 init, L2420 clearMoveArt) set it false. The draw branch at L11899 and its hand-authored 8-exposure track ([0, .093, .171, .249, .327, .405, .560, .760], with beats 1-2 pumping twice per the owner's 'repeat that frame') can never run. Ten drawn cells dark.
- `hdown1..8 (cells 323-330) — DEAD` — Air Down+Heavy is METEOR BREAK for the whole roster (L6521), which sets slamPhase immediately; the dive branch at L11547 is filed above the air dirCells map and returns dive1..6 first. The `if (p.slamPhase && F.hdown3)` line below it is also unreachable for him. No other input can produce attackAir + attackDir 'down'.
- `dash1..8 (cells 297-299, 402-406) — DEAD` — Nothing in the engine reads a `dash<N>` key — no literal, no string-built lookup. His dash is drawn from `blur`, whose cells are all 0. Eight real cells packed with no reader, while the input they belong to draws the idle pose.
- `kick21..23 / kick31..33 (cells 49-54) — DEAD` — Second-mode string art. LIGHT_STRINGS's comment names 'kick2/kick3' but the only string lookup is `'punch' + (stringStep+1)` (L11361), and Oni's second mode was deleted outright, so there is no stance that could select them. They also alias ghback1..6.
- `bostrike1..6 / bosweep1..6 — DEAD` — Staff moveset, removed with mode 2 (L2762: 'the bostrike/bosweep/sdown/aspin/gh* club cells are never drawn'). Neither key appears anywhere in the engine outside that comment — and both rows are cell-0 placeholders anyway.
- `runb1..10, airidle, run1..2, crouch, kneel, heavy_i1..5, heavy1..2, block/block2/blockhit, guard2/guard4/guard5/guard6 — DEAD` — Unreferenced or shadowed. `runb` and `airidle` have no reader at all (runb duplicates run_clean's cells; airidle is a unique cell, 401, nobody draws). `run1/2`, `crouch`, `kneel`, `heavy_i*`, `heavy*` are fallbacks that a higher branch always beats. block/block2/blockhit (24-26) are unreachable because his `guard1` key exists and L12033 returns before them; of the six guard cells only guard1 and guard3 are ever read.
- `gldown — MISSING (Down+Light on the ground)` — His only grounded Light direction with no drawn row. The command-kick tier takes the input (L5131, drew = 'gldown' fails) and the sweep kick draws `ksweep` = cell 0. The comment at L5124 asserts 'Oni's MASTER-LIGHT-DIR board draws glfwd / glback / gldown' — oni.json carries only the first two.
- `glup — MISSING (Up+Light on the ground)` — Falls back to the generic light1..5 collector. Largely academic: Up is the jump key, so the press almost always resolves as the air up-poke (airkick) instead.
- `gsfwd — MISSING (Fwd+Special / PHANTOM DASH)` — The move sets attackDir 'fwd' specifically so a gsfwd row can pick it up, but the row was never packed, so the hardest quick-draw in the game draws the WIRE SHOT's eight cells.
- `sup, sfwd, sback — MISSING (air Up/Fwd/Back Special)` — `sup` never existed. L5631 tests for it and, failing, drops an airborne Up+Special outside the launch window to the Cursed Burst with special1..8 art. sfwd/sback are covered in practice by the aspin branch, but the air dirCells map still names them.
- `sneu1..8, gsup1..6, afwd, cart, roll_, glfwd, glneu, punch2/punch3, whip, hback, hup, hfwd/ghfwd, sdown/gsdown — reachable but ALIASED` — Not holes, but worth naming: 14 of his rows share cells with another row, so several distinct inputs are the same picture. Most consequential — Fwd+Heavy is byte-identical to the neutral Heavy (both hfwd 65-84); Up+Heavy, air Up+Heavy and the RISING CLAW are all cells 59-64; the Fwd+Light cartwheel, the dodge roll and the forward jump are all cells 135-140; the whip, the wire shot, the phantom dash, the stomp and the cursed burst all draw out of special1..8 (99-106).
- `orphan cells in the sheet` — The sheet is 407 columns; cells 300, 301 and 371-385 carry a `mirror: 1` flag but no frame key points at any of them, and 386-390 are unnamed too. Cells 39-48 (glback) and 315-322 (dashatk) are the only large drawn blocks in dispute.

---

