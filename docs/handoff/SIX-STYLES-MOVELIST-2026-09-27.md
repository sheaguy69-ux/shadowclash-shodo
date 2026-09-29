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
| Tsubasa | Ryōtō Otoshi (Air H) | spike |
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
| 1 — longest (tied) | **Executioner** | long sword + his height; the tip is the sweetspot; iai draws reach far |
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
| Executioner | **Kashima Shintō-ryū + iaijutsu** | tank and heavy bruiser: slowest mover, fast quick-draw sword, armor-cutting decisive strike |
| Mizu | **Kukishin-ryū Bōjutsu** | reach and flow; bo splits to hanbō up close |
| Shin | **Taijutsu (Gyokko-ryū Kosshijutsu, jūtaijutsu) + wire + shuriken + Gyokushin-ryū spy tricks** | hand-to-hand specialist; the wire/shuriken/tricks are core kit |
| Ember | **Togakure-ryū Shukō, orthodox form** | traditional, textbook claw strikes — trained, not feral |

Historical note: many ninjutsu ryūha lineages are unverified; use them as flavour, never as
claimed history in shipped text.

---

## KAEL — Niten Ichi-ryū, "the Twin Shadow" · Reach: mid + short

Owner-approved rebuild, 2026-09-28. His game revolves around ONE parrying attack; the rest
of the kit feeds it or cashes it in. **He keeps his guard, but blocking costs him bigger
stagger than anyone else** — the parry is always the better answer, never the only one.

**Dash (new input, Kael):** double-tap forward.

| Input | Move | Notes |
|---|---|---|
| Light | **Kodachi Tsuki** — fast short-sword jab; first hit of Sōrai | fastest poke; chains into the second Light |
| Light, Light | **Sōrai** "Twin Lightning" — short sword then long sword | fast, low recovery; **cancels into Kage-uke at any point** |
| Light, Light, Heavy | **Tsuki-no-Bori** "Rising Moon" — crescent upward cut | **Launch**; follow with jump + Otoshi Nitō (spike) |
| Fwd+L | **Sasoi** — long sword slides in to draw a reaction | mid-range; safe on block |
| Down+L | **Ashi Barai-giri** — long-sword ankle cut | low |
| Back+L | **Ushiro Harai** — short-sword backhand, stepping back | whiff punish |
| Air L | **Tobi Kodachi** — jumping short-sword slash | jump-in |
| Heavy | **Kiri-tōshi** "Piercing Needle" — long-sword thrust | long reach, heavy guard/stagger damage; slow startup; **no cancel** |
| Fwd+H | **Nitō Kesa** — both blades, diagonal, one after the other | 2 hits, big stagger, wallsplat |
| **Back+H** | **Kage-uke** "Shadow Cross" — THE PARRYING ATTACK | crossed swords, body smokes. **Parry frames 2–8** (~33–133ms). **Success:** absorbs the hit, no hitstun, he smoke-flickers and an **automatic unblockable counter-cut** fires → **Knockdown** (bosses: **Stun**). **Whiff:** smoke puff gives him away, long recovery, fully punishable |
| Kage-uke (success) → Heavy | **Kage Kubi-kiri** "Shadow Execution" | freeze-frame + ink splash, both swords in a full circle, **AoE**, huge damage; high recovery, **ends the combo** |
| Kage-uke (success) → Dash | **Utsusemi** "Cicada Shell" | leaves a hollow husk (kawarimi-style) and reappears **behind** them for a backstab; combo continues |
| Dash + Heavy | **Shukuchi-giri** "Earth-Shrinking Cut" — low blurring lunge | gap-closer; **slides under high attacks**; on hit **cancels into Light** |
| Down+H | **Gedan Nitō** — both blades sweep low | low, trip |
| Air H | **Otoshi Nitō** — both swords chop down | **Spike**; crush |
| Special | **Itsutsu no Kata** — five-cut sequence | chakra; last cut Breaks |
| Fwd+S | **Iai Ryūsen** — dash-through cut | switches sides |
| Guard+S | **Kage Nitō** (shadow) — clone dashes in from the far side and cuts | Strike → Push toward Kael |
| Throw | **Kodachi Osae** — pins arm with short, slashes with long | wallsplat near wall |
| Guard | **kept**, with **increased block stagger** (Kael only) | balance change → its own commit |
| Kawarimi | log swap, reappears behind with a short-sword stab | |

Cancel rules: Sōrai → Kage-uke any time · Kage-uke absorbs on frames 2–8 and cancels only
into Kage Kubi-kiri or Utsusemi · Kage Kubi-kiri ends the string · Kiri-tōshi cannot be
cancelled · Shukuchi-giri → Light on hit.

## TSUBASA — Tantōjutsu, parries, kicks · Reach: mid

Owner revision, 2026-09-28: **Tsubasa is the parry master — his whole neutral game, defense
and counters revolve around trapping, deflecting, redirecting and using the opponent's
momentum.** Real dual-tantō work (ryōtōjutsu): **uke-nagashi** (flowing deflection) and
**jūji** (cross-blade) traps — one blade controls or redirects the incoming weapon, the other
blade or an open-hand **teishō** (heel-palm) counters instantly.

| Input | Move | Deflection & parry mechanics | Notes |
|---|---|---|---|
| Light | **Uke-Kiri** (Deflect & Slash) | off-hand tantō redirects the attack upward while the dominant blade slashes the chest | **auto-parries non-heavy high attacks on startup**; fast combo starter |
| Fwd+L | **Sokutō Geri** (Blade-Foot Thrust) | outer edge of the foot driven into the knee joint | low-profile poke; holds optimal short-blade range |
| Back+L | **Uke-Nagashi Teishō** (Flowing Deflect & Palm) | slips the stance, slides their blow along the blade spine, heel-palm to the jaw | **PARRY**; fast startup; frame-advantage generator that resets neutral |
| Down+L | **Ashi Kiri** (Ankle Cut) | low crouching slash at the Achilles / inner shin | low; forces crouching guard |
| Air L | **Tobi Hiji Tsuki** (Leaping Elbow Drive) | descending lead elbow into the shoulder/clavicle, blades held ready | **Overhead**; keeps pressure on landing |
| Heavy | **Jūji-Dome** (Cross-Blade Catch) | both tantō crossed in an X to lock down heavy attacks | **PARRY**; on catch, guaranteed heavy throat stab |
| Fwd+H | **Mae Geri → Nodo Tsuki** (Front Kick → Throat Piercer) | mid snap kick opens the guard, then a lunging throat stab | 2 hits; severe wallsplat near walls/edges |
| Back+H | **Ura Gyaku Tsuka-uchi** (Inner Wrist Twist & Pommel Strike) | steps around the attack, turns the wrist inward, drives the tantō pommel into nerve points | **anti-flank**; punishes aggressive forward dashes |
| Down+H | **Harai Ashi → Kote Kiri** (Leg Hook → Wrist Cut) | foot-hook sweeps the front leg while slicing the wrist/forearm | low multi-hit; hard knockdown / trip |
| Air H | **Ryōtō Otoshi** (Twin-Blade Drop) | double-blade downward thrust with full body mass | **Spike**; ground bounce on airborne targets (one per combo) |
| Special | **Kaeshi-Waza** (Omni-Counter Stance) | fluid dual-blade stance; any physical attack that strikes it is redirected, leaving them fully open | **PARRY STANCE**; severe stagger → full-combo punish |
| Fwd+S | **Renzen Kiri** (Continuous Trapping Flurry) | advances with alternating check-parries and short cuts, ends in a guard-breaking palm thrust | advancing string; **auto-reflects light projectiles**; last hit **Guard-break** |
| Guard+S | **Kage Uke** (Decoy Parrying Trap) | shadow clone takes the hit and pins their weapon between its blades | Tsubasa gets a guaranteed **unblockable** free counter-cut |
| Throw | **Kote Hineri Nage** (Wrist Lock & Disarm Throw) | traps the limb, twists the wrist (kote hineri), slashes the forearm, throws | command throw; beats block; high damage; resets position |
| Guard | **Sekitō Riposte** (Flash Block Counter) | striking immediately off a fresh block fires a lightning cross-cut | passive; **highest-damage riposte on the roster** (`executeReprisal`) |

Known engine issue to check first: Tsubasa's sakate is still hijacked by the kick map
(missing `gl*` rows) — see MOVE-LISTS "directional-light law".

## EXECUTIONER — Kashima Shintō-ryū + iaijutsu · Reach: longest (tied)

Owner revision, 2026-09-29. **Tank and heavy bruiser:** slowest walk, dash and jump on the
roster, the most health, and a guard that takes the least stagger. **The sword itself is
fast** — short-startup quick draws (iai/battōjutsu) with long reach — so he is hard to
walk away from even though he is the slowest to walk. Movement speed, health and block
stagger are balance changes → their own commit; sword frames stay fast, and Nukitsuke /
Iai-giri get short whiff recovery so a long-range draw is not punished.

| Input | Move | Notes |
|---|---|---|
| Light | **Nukitsuke** — quick draw, cut in one motion | fastest startup in his kit; long reach for a Light; chains |
| Fwd+L | **Tai-atari** — armored shoulder bump | **Guard-break** strike, **Push** a short distance; on hit leaves them **Stun**ned in sword range. **Setup:** links into Kesa-giri (Fwd+H) or Hitotsu-no-Tachi (H) |
| Up+L | **Zutsuki** — helmeted headbutt | close **Strike**, beats throws on startup; on hit **Stun** ~0.4s. **Setup:** the reliable way to land Hitotsu-no-Tachi or a charged Shinbu no Tachi |
| Back+L | **Saya-uchi** — scabbard strike while stepping back, then sheathes | close-range escape; mild push |
| Down+L | **Sune-nuki** — low quick draw at the shin | low |
| Air L | **Tobi Kiri-oroshi** — short jumping downcut | jump-in |
| Heavy | **Hitotsu-no-Tachi** — one decisive overhead cut down the centerline | biggest hit in the kit; faster startup than before; armor on startup |
| Fwd+H | **Kesa-giri** — stepping shoulder-to-hip diagonal that cuts through armor | wallsplat |
| Back+H | **Kiri-otoshi** — his cut lands on theirs, knocks it aside and hits in one motion | **PARRY**; small window, biggest single parry reward |
| Down+H | **Nuki-dō** — steps past them low, cutting across the torso | low, trip, long reach |
| Air H | **Kabuto-wari** — helmet-splitter drop | **Spike**; crush; always Breaks a breakable floor |
| Special | **Shinbu no Tachi** — gathers strength in a low stance, then cuts up and down | chakra, armor; unblockable at full charge |
| Fwd+S | **Iai-giri** — long draw, slides forward with the cut | his long-distance strike; beats weapon pokes; breaks walls; short whiff recovery |
| Down+S | **Maki-otoshi** — winds his blade around theirs and wrenches it down | **Disarm**: their next weapon attack is slower |
| Guard+S | **Kage Kubikiri** (shadow) — clone appears behind, slow overhead cut | Overhead → Stun; sets up Hitotsu-no-Tachi |
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

Owner revision, 2026-09-28: real taijutsu, koppōjutsu (bone-striking) and dakentaijutsu —
open palms, blade-hand chops and specialised hand formations (knife-hand, heel-palm, thumb
drive). **No boxing-style punches.**

| Input | Move | Attack & mechanics | Notes |
|---|---|---|---|
| Light | **Shutō Uchi** (Knife-Hand Chop) | swift diagonal blade-hand chop to the side of the neck | fast startup; chains into light follow-ups |
| Fwd+L | **Shuriken Uchi** (Shuriken Throw) | low-profile concealed shuriken from the hip/sleeve | fast projectile, mid-range check |
| Back+L | **Sokugyaku / Boshi-ken** (Heel-Palm Counter) | slips inward under the blow, strikes forward with an open **Teishō** (heel-palm) to the jaw | **COUNTER**; fast startup; resets neutral with mild pushback |
| Down+L | **Ashi Kudaki** (Ankle Smash) | low heel-stamp into the ankle or shin joint | low; disrupts standing guard |
| Air L | **Tobi Shuriken** (Air Shuriken) | angled downward shuriken while airborne | aerial zoning; keeps them grounded |
| Heavy | **Boshi-ken Tsuki** (Thumb-Drive Strike) | reinforced thumb-joint drive into rib/nerve points | high hit-stop; heavy stagger |
| Fwd+H | **Kaginawa Hiki** (Grapple Wire Hook) | weighted grapple line snags the target and reels them in | mid-range command hook → free combo |
| Back+H | **Omote Gyaku** (Outer Wrist Twist Throw) | catches the striking wrist, outward joint lock, drives them into the ground | **COUNTER** stance; long recovery on whiff |
| Down+H | **Ashi Garami Nawa** (Ankle Trap Wire) | weighted line swept across the floor entangles the legs | low sweep; hard knockdown |
| Air H | **Hiji Otoshi** (Descending Elbow Drop) | drops straight down, lead elbow through airborne opponents | **Spike**; ground bounce on air-hit (one per combo) |
| Special | **Metsubushi** (Blinding Powder) | flash of ash/metal dust into the face | unblockable flash; temporarily disables their block |
| Fwd+S | **Ito Shibari** (Wire Pin) | taut line binds them and hitches them to the wall | ranged wallsplat; sets up extended juggles |
| Down+S | **Makibishi** (Caltrop Scatter) | iron caltrops across the nearby ground | hazard zone; passive damage + hitstun when stepped on |
| Guard+S | **Kage Nawa** (Shadow Wire Trap) | shadow clone appears behind the target and lines them back into Shin's strike zone | reverses position; pulls them toward Shin |
| Throw | **Oni Kudaki** (Demon Breaker) | arm over the shoulder, elbow-joint snap, shoulder throw | command throw; high damage; breaks guard |
| Kawarimi | **Doton Kakure** (Earth-Hiding Evasion) | substitution that exits straight into an active stealth/hiding spot | defensive escape |

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
- **Tai-atari → Hitotsu-no-Tachi**: shoulder stun covers the big cut's slow startup.
- **Zutsuki → Hitotsu-no-Tachi / Shinbu no Tachi**: headbutt stun is the window for his slowest,
  biggest hits.
- **Zutsuki → Tai-atari**: headbutt, then shoulder into the wall for a wallsplat.
- **Maki-otoshi → Kesa-giri**: their weapon attacks are slowed, so the diagonal lands.
- **Nukitsuke / Iai-giri from range → Tai-atari**: the draw keeps them off, the shoulder bump takes over as they close.
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
| Tsubasa | **Kage Uke** — the shadow takes the hit and pins their weapon between its blades | Parry box → weapon pinned | a guaranteed unblockable counter-cut from Tsubasa |
| Executioner | **Kage Kubikiri** — the shadow appears behind them with a slow overhead cut | Overhead → **Stun** | Hitotsu-no-Tachi from the front |
| Mizu | **Kage Mizu** — the shadow sweeps the bo low, then pops into her shipped **Water Slick** | Low → **Trip**, slick stays | pressure on the slick. Water Slick is kept as shipped |
| Shin | **Kage Nawa** — the shadow throws its wire from the other side | Grab (ranged) → **Pull** toward Shin | his taijutsu combo |
| Ember | **Kage Tora** — the shadow pounces and rakes low | Low → **Trip** | his down-heavy tiger rake |

## Likely new engine work (confirm before building)

- Shadow clone attacks (above) on top of the existing `castBunshin()` path.
- Kael: double-tap-forward dash, the Kage-uke parry with post-parry branches (Heavy / Dash), and his larger block stagger (balance commit).

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
