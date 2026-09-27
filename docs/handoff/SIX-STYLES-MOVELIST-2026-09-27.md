# HANDOFF — Six fighting styles + new attack list (Codex)

Owner-approved design, 2026-09-27. **This is a design brief, not engine truth.** Nothing
here is wired yet. Read `AGENTS.md` first — its rules win over this file.

## Scope

- Fighters: **Kael, Tsubasa, Executioner, Mizu, Shin, Ember.** Nobody else.
- **Second form (V/K) is OUT.** Do not add, change or map any Form-2 move.
- Controls are the shipped ones (`RECOVERY/MOVE-LISTS.md` → THE CONTROLS): Light, Heavy,
  Special, each with neutral / fwd / back / down / air; Throw (L+H); Guard / Kawarimi.
- Canon weapons (AGENTS.md §2) are unchanged: Kael long + short sword · Tsubasa twin tantō ·
  Executioner long sword · Mizu bo that splits to twin hanbō · Shin wire + shuriken ·
  Ember three claws per hand.

## How to work it

1. **Ask Anthony before each step** — one fighter at a time, show it, get the yes.
2. Open a lane: `python3 tools/lane.py start "codex"`, claim what you touch.
3. **Reuse before you build.** Map each move to an existing engine move/row where one fits
   (e.g. `executeReprisal`, `executeKick` sweep/push/heel, Ember `lowrake`/`clawrend`/`eheavy`).
   Report which moves reuse, which need new code, which need new art — before writing any.
4. Name changes replace the old names everywhere, same pass (AGENTS.md §1): the fighter's
   `*-MOVE-NAMES.md`, `RECOVERY/MOVE-LISTS.md`, the in-game L move-list panel, engine comments.
5. **No new art is generated here.** Missing cells go on an "art owed" list for Anthony.
6. Any timing/damage/armor number is a **balance change → its own commit.** The notes below
   are intent ("big stagger", "slow"), not numbers — propose numbers, don't invent them silently.

## Terms

- **Low / trip** — must be crouch-blocked; knocks down.
- **Wallsplat** — sticks them to the wall.
- **Crush** — breaks weak floors/walls. **Break** — knocks them *through* one.
- **Armor** — absorbs a hit without flinching.
- **Parry** — timed catch/deflect; on success the attacker is left open, the parrier chooses
  the follow-up. Short window, big reward.
- **Counterattack** — a held stance or slip; if struck, the return strike fires
  automatically. Easier timing, fixed reward.

**Defensive rule (owner):** Kael, Tsubasa, Executioner, Ember have **parries**.
Shin and Mizu have **counterattacks** (no parries). Tsubasa is the parry expert (widest
window, best reward); Executioner's single parry hits hardest.

## The six styles

| Fighter | Style | Identity |
|---|---|---|
| Kael | **Niten Ichi-ryū** (daishō, long + short) | long blade controls distance, short blade guards and finishes |
| Tsubasa | **Tantōjutsu + parries + keri-waza (kicks)** | blade user and parry expert; kicks set up the cut |
| Executioner | **Kashima Shintō-ryū** | master swordsman; armor-cutting, one decisive stroke |
| Mizu | **Kukishin-ryū Bōjutsu** | reach and flow; bo splits to hanbō up close |
| Shin | **Taijutsu (Gyokko-ryū Kosshijutsu, jūtaijutsu) + wire + shuriken + Gyokushin-ryū spy tricks** | hand-to-hand specialist; the wire/shuriken/tricks are core kit |
| Ember | **Togakure-ryū Shukō, orthodox form** | traditional, textbook claw strikes — trained, not feral |

Historical note: many ninjutsu ryūha lineages are unverified; use them as flavour, never as
claimed history in shipped text.

---

## KAEL — Niten Ichi-ryū

| Input | Move | Notes |
|---|---|---|
| Light | **Kodachi Tsuki** — short-sword jab | fastest poke, chains |
| Fwd+L | **Sasoi** — long sword slides in to draw a reaction | mid-range, safe on block |
| Back+L | **Ushiro Harai** — short-sword backhand, stepping back | whiff punish |
| Down+L | **Ashi Barai-giri** — long-sword ankle cut | low |
| Air L | **Tobi Kodachi** — jumping short-sword slash | jump-in |
| Heavy | **Nitō Kesa** — both blades, diagonal, one after the other | 2 hits, big stagger |
| Fwd+H | **Chūdan Tsuki** — lunging long-sword thrust | wallsplat |
| Back+H | **Jūji-uke** — catches the attack on crossed swords | **PARRY**; success = free short-sword finisher |
| Down+H | **Gedan Nitō** — both blades sweep low | low, trip |
| Air H | **Otoshi Nitō** — both swords chop down | crush |
| Special | **Itsutsu no Kata** — five-cut sequence | chakra; last cut Breaks |
| Fwd+S | **Iai Ryūsen** — dash-through cut | switches sides |
| Throw | **Kodachi Osae** — pins arm with short, slashes with long | wallsplat near wall |
| Kawarimi | log swap, reappears behind with a short-sword stab | |

## TSUBASA — Tantōjutsu, parries, kicks

| Input | Move | Notes |
|---|---|---|
| Light | **Sōtō Kiri** — fast twin-tantō slashes | chains |
| Fwd+L | **Sokutō Geri** — edge-of-foot side kick | pushes into blade range |
| Back+L | **Uke-nagashi** — turns the attack aside | **PARRY**; success sets up next attack |
| Down+L | **Ashi Kiri** — low tantō slash | low |
| Air L | **Tobi Geri** — flying kick | jump-in, light knockback |
| Heavy | **Jūji-dome** — catches the blade between crossed tantō | **PARRY**; success = free cut |
| Fwd+H | **Mae Geri → Tsuki** — front kick then stab | 2 hits, wallsplat |
| Back+H | **Ushiro Mawashi** — spinning back kick | beats a chaser |
| Down+H | **Kaiten Ashi Barai** — sweep kick then tantō cut | low, trip |
| Air H | **Kakato Otoshi** — heel drop | overhead, crush |
| Special | **Kaeshi-waza** — counter stance | **PARRY-stance**; struck = twin-blade counter-cut, big stagger |
| Fwd+S | **Tsubame Gaeshi** — spinning blade run | chakra; ends in a kick that Breaks |
| Throw | **Kote Kiri Nage** — disarm cut, kick away | |
| Guard | signature: fresh-block riposte (`executeReprisal`) is strongest on him | best parry reward on roster |

Known engine issue to check first: Tsubasa's sakate is still hijacked by the kick map
(missing `gl*` rows) — see MOVE-LISTS "directional-light law".

## EXECUTIONER — Kashima Shintō-ryū

| Input | Move | Notes |
|---|---|---|
| Light | **Kote-uchi** — short wrist cut | his only fast poke |
| Fwd+L | **Tsuki-komi** — pommel shove, thrust | push |
| Back+L | **Hiki-giri** — drawing slice while retreating | |
| Down+L | **Sune-giri** — shin cut | low |
| Air L | **Tobi Kiri** — short jumping chop | |
| Heavy | **Hitotsu-tachi** — one decisive overhead cut | very slow, huge damage, armor on startup |
| Fwd+H | **Kesa-giri** — stepping armor-cleaving diagonal | wallsplat |
| Back+H | **Kiri-otoshi** — his cut strikes down theirs and hits in one motion | **PARRY**; small window, biggest single parry reward |
| Down+H | **Nagi-harai** — wide low sweep | low, trip, long reach |
| Air H | **Kabuto-wari** — helmet-splitter drop | crush, Break |
| Special | **Shinbu no Tachi** — gathers, then cuts | chakra, armor; unblockable at full charge |
| Fwd+S | **Ittō Ryōdan** — charging cut | breaks walls |
| Throw | **Yoroi Oshi** — armored shoulder, hilt strike | |
| Guard | slow kawarimi; guard takes much less stagger | |

## MIZU — Kukishin-ryū Bōjutsu

| Input | Move | Notes |
|---|---|---|
| Light | **Tsuki** — straight bo jab | long reach |
| Fwd+L | **Kasumi-uchi** — quick face strike | sets up next attack |
| Back+L | **Hanbō Kaeshi** — splits the bo, answers a strike with a hanbō | **COUNTER** stance; struck = twin-hanbō return |
| Down+L | **Sune-barai** — low bo sweep | low |
| Air L | **Tobi Tsuki** — downward bo jab | long jump-in |
| Heavy | **Mizu-guruma** — spinning bo | multi-hit |
| Fwd+H | **Nagare Tsuki** — sliding thrust | wallsplat |
| Back+H | **Nagare Gaeshi** — slips aside, cracks the bo on them | **COUNTER**; struck = evade + knockdown |
| Down+H | **Ashi-garami** — hooks the ankle with the bo | trip |
| Air H | **Taki Otoshi** — waterfall slam | crush |
| Special | **Sōjō Hanbō** — split into twin-hanbō flurry | chakra, fast close combo |
| Fwd+S | **Bo Kakeru** — vaults on the bo, kicks | clears lows |
| Throw | **Bo Garami** — bo behind neck, hip throw | |
| Guard | standard kawarimi | no parry |

## SHIN — Taijutsu, wire, shuriken, spy tricks

| Input | Move | Notes |
|---|---|---|
| Light | **Shikan-ken** — fast knuckle jabs | chains |
| Fwd+L | **Shuriken Uchi** — thrown shuriken | range |
| Back+L | **Nagare Kōtei** — slips, palm-strike return | **COUNTER**; fast, small reward |
| Down+L | **Ashi Kudaki** — ankle stomp | low |
| Air L | **Tobi Shuriken** — downward shuriken | air |
| Heavy | **Kosshi Tsuki** — thumb strike to a nerve point | big stagger |
| Fwd+H | **Kaginawa Hiki** — wire throw, pull in | ranged grab into combo |
| Back+H | **Omote Gyaku** — catches the arm, wrist lock, throw | **COUNTER** stance |
| Down+H | **Ashi Garami Nawa** — wire around the ankle | low, trip |
| Air H | **Hiji Otoshi** — elbow drop | crush |
| Special | **Metsubushi** — blinding powder | chakra; brief no-block; works from hiding spots |
| Fwd+S | **Ito Shibari** — wire pins to wall | ranged wallsplat |
| Down+S | **Makibishi** — scatter caltrops | floor zone, hurts on step |
| Throw | **Oni Kudaki** — arm lock into slam | big damage, Break |
| Kawarimi | can end inside a hiding spot | |

## EMBER — Togakure-ryū Shukō, orthodox form

| Input | Move | Notes |
|---|---|---|
| Light | **Tsume Tsuki** — straight claw jab | |
| Fwd+L | **Kamae Tsuki** — stepping strike from stance | mid-range |
| Back+L | **Shukō Uke** — catches the blade in the claws | **PARRY**; knocks weapon away |
| Down+L | **Gedan Tsume** — low claw cut | low |
| Air L | **Tobi Tsume** — jumping claw swipe | |
| Heavy | **Jūji Tsume** — crossing X rake | big stagger (reuses `eheavy`) |
| Fwd+H | **Tobi Tora Geki** — lunging two-hand strike | wallsplat, 2nd hit sends (reuses `clawrend`) |
| Back+H | **Tora Gaeshi** — claw guard, rake back | |
| Down+H | **Tora Tsume Tensho** — downward tiger rake | low, trip — **CANON, owner Aug 21** (`lowrake`) |
| Air H | **Tsume Otoshi** — both claws drive down | crush |
| Special | **Senkō Tsume** — dashing claw strike | chakra, brief armor (near current `espec`) |
| Fwd+S | **Kabe Nobori** — climbs the wall, dives | crush |
| Throw | **Tsume Kake Nage** — collar hook throw | |
| Guard | claw-catch parry is his reliable disarm | |

---

## Likely new engine work (confirm before building)

- Parry framework shared by Kael / Tsubasa / Executioner / Ember (window + reward tiers);
  check whether `executeReprisal` / blade-lock (`docs/BLADE-LOCK-2026-09-06.md`,
  `docs/CLASH-SPEC-2026-09-07.md`) already covers part of it.
- Counter-stance framework for Mizu / Shin.
- Tsubasa Kaeshi-waza, Executioner Shinbu charge, Shin Metsubushi / Makibishi / Ito Shibari,
  Ember Kabe Nobori (wall interaction), Crush/Break hooks into the stage-break system.

## Deliverable back to Anthony

Per fighter: a table of move → existing engine move reused / new code / art owed, then wait
for his yes before implementing.
