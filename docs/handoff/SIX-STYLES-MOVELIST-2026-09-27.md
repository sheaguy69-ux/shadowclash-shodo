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

## Hitbox types (what the box IS)

Every attack gets exactly one type. The type decides how it can be stopped.

| Type | Blocked by | Beats | Loses to |
|---|---|---|---|
| **Strike** | standing or crouching guard | nothing special | everything below |
| **Low** | crouching guard only | standing guard | jumps |
| **Overhead** | standing guard only | crouching guard | fast pokes (slow startup) |
| **Grab** | cannot be blocked | guard | any attack, jumps, kawarimi |
| **Guard-break** | guard, but shatters it: guard stays down ~0.5s | turtling | parries, counters, jumps |
| **Projectile** | any guard | range | parries (deflect), jumping over |
| **Unblockable** | nothing | guard | armor-less interruption during its long startup |
| **Parry box** | — | the attack it catches | grabs, guard-breaks, delayed hits |
| **Counter box** | — | the attack that strikes it | grabs, projectiles, whiffing it |
| **Zone** | nothing (stays on the floor) | ground movement | jumping, waiting it out |

**Box modifiers** (stack on top of a type):
- **Disjointed** — the blade has no hurtbox; trading with a fist, a sword wins.
- **Sweetspot / sourspot** — tip of the weapon hits harder than the base (Executioner, Mizu).
- **Multi-hit** — several small boxes in sequence; each adds stagger.
- **Armor** — the attacker absorbs one hit during startup/active frames.

## Hit effects (what happens to the victim)

One primary effect per move; the notes column in each list names it.

| Effect | What happens | Sets up |
|---|---|---|
| **Stagger** | fills the dizzy bar | a full **Dizzy**: 1.2s free combo |
| **Stun** | short freeze, ~0.4s, no knockdown | a slow, big hit (Executioner's setups) |
| **Push** | slides them away | spacing |
| **Pull** | drags them in | close combos (Shin's wire) |
| **Wallsplat** | stuck to the wall ~0.6s | wall combo |
| **Trip** | knocked flat on the spot | okizeme (pressure on wake-up) |
| **Knockdown** | flung and flat | reset / okizeme |
| **Launch** | popped into the air | air combo → **Spike** |
| **Spike** | driven straight down, fast (below) | ground bounce, Crush, Break |
| **Ground bounce** | bounces once off solid floor | one more hit |
| **Crumple** | slowly folds to the floor ~0.8s | a charged hit |
| **Guard crush** | guard broken open | anything |
| **Blind** | can't block ~0.8s (Shin's Metsubushi) | anything |
| **Disarm** | weapon knocked aside; their next weapon attack is slower ~0.6s | tempo |
| **Crush** | breaks a weak floor/wall under/behind them | stage transition |
| **Break** | sends them *through* a floor/wall | follow-through (existing stage-break system) |

## The Spike mechanic

A **spike** is an air hit that drives the target straight down at high speed.

- **What spikes:** designated Air Heavies (list below) and any air hit landing on a
  **launched** or airborne target from above.
- **On solid floor:** **Ground bounce** — they pop up once, a short window for one more hit.
  Only one bounce per combo; a second spike in the same combo is a plain Knockdown.
- **On a breakable floor:** the spike **Breaks** it and they fall through — this rides the
  existing break/fall system (including the 8% max-HP fall cost; do not stack a second fall
  cost on top).
- **Into a stage spike hazard:** full hazard damage, no bounce.
- **Defending:** an airborne victim with guard held **air-guards** the spike: no bounce,
  no break, they land normally. Air kawarimi also escapes it (costs as usual).
- **Spiked while blocking on the ground:** it is an **Overhead**.

Spike moves:

| Fighter | Spike | Notes |
|---|---|---|
| Kael | Otoshi Nitō (Air H) | spike |
| Tsubasa | Kakato Otoshi (Air H) | overhead; spike |
| Executioner | Kabuto-wari (Air H) | spike; always Breaks a breakable floor |
| Mizu | Taki Otoshi (Air H) | spike; longest reach of the spikes (tied with Executioner) |
| Shin | Hiji Otoshi (Air H) | spike |
| Ember | Tsume Otoshi (Air H) | spike |

## Other terms

- **Parry** — timed catch/deflect; on success the attacker is left open, the parrier chooses
  the follow-up. Short window, big reward.
- **Counterattack** — a held stance or slip; if struck, the return strike fires
  automatically. Easier timing, fixed reward.

**Defensive rule (owner):** Kael, Tsubasa, Executioner, Ember have **parries**.
Shin and Mizu have **counterattacks** (no parries). Tsubasa is the parry expert (widest
window, best reward); Executioner's single parry hits hardest.

## Reach (owner rule)

**The Executioner and Mizu have the longest attack range on the roster, tied.** Every
other fighter's melee boxes stay shorter than theirs.

| Tier | Fighter | Reach comes from |
|---|---|---|
| 1 — longest (tied) | **Executioner** | long sword + his height; the tip is the sweetspot |
| 1 — longest (tied) | **Mizu** | the full-length bo; tip is the sweetspot. Split hanbō moves are short on purpose |
| 2 — mid + short | **Kael** | both ranges on purpose: long sword owns mid-range, short sword owns close range |
| 2 — mid | **Ember** | claws with a long lunging reach |
| 2 — mid | **Tsubasa** | kicks extend the tantō; blades alone are close |
| short + mid + long | **Shin** | short: fists (taijutsu) · mid: the wire · long: shuriken (projectiles) — the only fighter who covers every range |

Exceptions allowed: the Executioner's headbutt and shoulder bump are deliberately close-range,
and Shin's wire (mid) and shuriken (long) do not count against the "longest melee reach" rule — Executioner and Mizu still have the longest weapon swings.

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

## KAEL — Niten Ichi-ryū · Reach: mid + short

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
| Air H | **Otoshi Nitō** — both swords chop down | **Spike**; crush |
| Special | **Itsutsu no Kata** — five-cut sequence | chakra; last cut Breaks |
| Fwd+S | **Iai Ryūsen** — dash-through cut | switches sides |
| Guard+S | **Kage Nitō** (shadow) — clone dashes in from the far side and cuts | Strike → Push toward Kael |
| Throw | **Kodachi Osae** — pins arm with short, slashes with long | wallsplat near wall |
| Kawarimi | log swap, reappears behind with a short-sword stab | |

## TSUBASA — Tantōjutsu, parries, kicks · Reach: mid

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
| Air H | **Kakato Otoshi** — heel drop | **Spike**; overhead, crush |
| Special | **Kaeshi-waza** — counter stance | **PARRY-stance**; struck = twin-blade counter-cut, big stagger |
| Fwd+S | **Tsubame Gaeshi** — spinning blade run | chakra; ends in a kick that Breaks |
| Guard+S | **Kage Uke** (shadow) — clone parries the next attack aimed at him | Parry box → Disarm; Tsubasa takes the free cut |
| Throw | **Kote Kiri Nage** — disarm cut, kick away | |
| Guard | signature: fresh-block riposte (`executeReprisal`) is strongest on him | best parry reward on roster |

Known engine issue to check first: Tsubasa's sakate is still hijacked by the kick map
(missing `gl*` rows) — see MOVE-LISTS "directional-light law".

## EXECUTIONER — Kashima Shintō-ryū · Reach: longest (tied)

| Input | Move | Notes |
|---|---|---|
| Light | **Kote-uchi** — short wrist cut | his only fast poke |
| Fwd+L | **Tai-atari** — armored shoulder bump | **Guard-break** strike, **Push** a short distance; on hit leaves them **Stun**ned in sword range. **Setup:** links into Kesa-giri (Fwd+H) or Hitotsu-tachi (H) |
| Up+L | **Zutsuki** — helmeted headbutt | close **Strike**, beats throws on startup; on hit **Stun** ~0.4s. **Setup:** the only reliable way to land Hitotsu-tachi or a charged Shinbu no Tachi |
| Back+L | **Hiki-giri** — drawing slice while retreating | |
| Down+L | **Sune-giri** — shin cut | low |
| Air L | **Tobi Kiri** — short jumping chop | |
| Heavy | **Hitotsu-tachi** — one decisive overhead cut | very slow, huge damage, armor on startup |
| Fwd+H | **Kesa-giri** — stepping armor-cleaving diagonal | wallsplat |
| Back+H | **Kiri-otoshi** — his cut strikes down theirs and hits in one motion | **PARRY**; small window, biggest single parry reward |
| Down+H | **Nagi-harai** — wide low sweep | low, trip, long reach |
| Air H | **Kabuto-wari** — helmet-splitter drop | **Spike**; crush; always Breaks a breakable floor |
| Special | **Shinbu no Tachi** — gathers, then cuts | chakra, armor; unblockable at full charge |
| Fwd+S | **Ittō Ryōdan** — charging cut | breaks walls |
| Guard+S | **Kage Kubikiri** (shadow) — clone appears behind, slow overhead cut | Overhead → Stun; sets up Hitotsu-tachi |
| Throw | **Kubi Nage** — grabs the collar, throws over the hip | Knockdown; sets up okizeme |
| Guard | slow kawarimi; guard takes much less stagger | |

## MIZU — Kukishin-ryū Bōjutsu · Reach: longest (tied)

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
| Air H | **Taki Otoshi** — waterfall slam | **Spike**; crush |
| Special | **Mist Drop (Kirigakure)** — her invisible mist | **KEEP AS SHIPPED — owner rule.** Engine MIST DROP unchanged: radius 260, 7.0s, she vanishes (alpha 0), everyone else inside is only obscured, no hitbox, recast replaces the field. Do not retune it |
| Down+S | **Sōjō Hanbō** — split into twin-hanbō flurry | chakra, fast close combo |
| Fwd+S | **Bo Kakeru** — vaults on the bo, kicks | clears lows |
| Guard+S | **Kage Mizu** (shadow) — clone sweeps low, then pops into Water Slick | Low → Trip; Water Slick kept as shipped |
| Throw | **Bo Garami** — bo behind neck, hip throw | |
| Guard | standard kawarimi | no parry |

## SHIN — Taijutsu, wire, shuriken, spy tricks · Reach: short + mid + long

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
| Air H | **Hiji Otoshi** — elbow drop | **Spike**; crush |
| Special | **Metsubushi** — blinding powder | chakra; brief no-block; works from hiding spots |
| Fwd+S | **Ito Shibari** — wire pins to wall | ranged wallsplat |
| Down+S | **Makibishi** — scatter caltrops | floor zone, hurts on step |
| Guard+S | **Kage Nawa** (shadow) — clone throws its wire from the other side | Ranged grab → Pull toward Shin |
| Throw | **Oni Kudaki** — arm lock into slam | big damage, Break |
| Kawarimi | can end inside a hiding spot | |

## EMBER — Togakure-ryū Shukō, orthodox form · Reach: mid

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
| Air H | **Tsume Otoshi** — both claws drive down | **Spike**; crush |
| Special | **Senkō Tsume** — dashing claw strike | chakra, brief armor (near current `espec`) |
| Fwd+S | **Kabe Nobori** — climbs the wall, dives | crush |
| Guard+S | **Kage Tora** (shadow) — clone pounces and rakes low | Low → Trip; sets up Tora Tsume Tensho |
| Throw | **Tsume Kake Nage** — collar hook throw | |
| Guard | claw-catch parry is his reliable disarm | |

---

## Executioner setup chains (owner intent: headbutt and shoulder bump exist to set up his other attacks)

- **Tai-atari → Kesa-giri**: shoulder breaks the guard, the diagonal cut wallsplats.
- **Tai-atari → Hitotsu-tachi**: shoulder stun covers the big cut's slow startup.
- **Zutsuki → Hitotsu-tachi / Shinbu no Tachi**: headbutt stun is the window for his slowest,
  biggest hits.
- **Zutsuki → Tai-atari**: headbutt, then shoulder into the wall for a wallsplat.
- Neither setup deals much damage alone; their value is what follows.
- Engine: Up+Light is free (`glup`, not in the kick map) and the Executioner already has
  `glup` 8 cells; check whether they can read as a headbutt before calling it art owed.

## Shadow clone attacks (owner rule: every fighter's shadow gets a special attack)

Input stays the shipped Bunshin: **Guard held + Special, 30 chakra.** The clone now performs
one signature attack before it pops. Shared rules: one clone at a time; the clone's hit
does reduced damage (it sets up, the fighter finishes); hitting the clone pops it.
Map each onto the fighter's existing Bunshin variant (see `RECOVERY/MOVE-LISTS.md`) rather
than adding a second clone system.

| Fighter | Shadow attack | Type → effect | Sets up |
|---|---|---|---|
| Kael | **Kage Nitō** — the shadow dashes in from the far side and cuts | Strike → **Push** toward Kael | a pincer: they are knocked into his long sword |
| Tsubasa | **Kage Uke** — the shadow stands guard and parries the next attack aimed at him | Parry box → **Disarm** | his free cut on the opened attacker |
| Executioner | **Kage Kubikiri** — the shadow appears behind them with a slow overhead cut | Overhead → **Stun** | Hitotsu-tachi from the front |
| Mizu | **Kage Mizu** — the shadow sweeps the bo low, then pops into her shipped **Water Slick** | Low → **Trip**, slick stays | pressure on the slick. Water Slick is kept as shipped |
| Shin | **Kage Nawa** — the shadow throws its wire from the other side | Grab (ranged) → **Pull** toward Shin | his taijutsu combo |
| Ember | **Kage Tora** — the shadow pounces and rakes low | Low → **Trip** | his down-heavy tiger rake |

## Likely new engine work (confirm before building)

- Shadow clone attacks (above) on top of the existing `castBunshin()` path.

- Hitbox type + effect tags on every move (one type, one primary effect) — check what the
  engine already carries (`low`, `trip`, `wallsplat`, `behind` exist on kick boxes).
- Spike: downward-launch state, one-bounce-per-combo rule, air-guard, hookup to the
  stage-break system and spike hazards.
- Stun, Crumple, Guard-break, Disarm, Blind as new victim states.

- Parry framework shared by Kael / Tsubasa / Executioner / Ember (window + reward tiers);
  check whether `executeReprisal` / blade-lock (`docs/BLADE-LOCK-2026-09-06.md`,
  `docs/CLASH-SPEC-2026-09-07.md`) already covers part of it.
- Counter-stance framework for Mizu / Shin.
- Tsubasa Kaeshi-waza, Executioner Shinbu charge, Shin Metsubushi / Makibishi / Ito Shibari,
  Ember Kabe Nobori (wall interaction), Crush/Break hooks into the stage-break system.

## Deliverable back to Anthony

Per fighter: a table of move → existing engine move reused / new code / art owed, then wait
for his yes before implementing.
