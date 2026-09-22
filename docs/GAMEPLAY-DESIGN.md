# ShadowClash — Gameplay Design: Learn, Don't Copy

**Mandate (owner):** study Skullgirls, Hollow Knight, and Naruto to *understand why their
mechanics work* — core mechanics may be borrowed, but ShadowClash must branch into
something **new and fresh** with its own identity.

This doc has three parts: what we learned (verified), what the current build actually does
(code audit), and the **original synthesis** — ShadowClash's own systems, each tagged with
what it learned from vs. what's new about it.

Method: 3 parallel research agents (Skullgirls systems, Naruto combat canon, local code
audit); the web tracks' top claims were independently fact-checked (corrections noted).
Sources at the bottom.

---

## 1. What we learned (the *why*, not the feature list)

### From Skullgirls (2D brawler systems — claims verified vs Mizuumi/Skullheart)
| Insight | Why it works |
|---|---|
| **Cancel-on-connect chains** (whiffs stay committal) | Confirms flow freely; mashing at air is punishable. ShadowClash already has this. |
| **Limits must be visible & legible** — no hitstun decay; instead IPS flags + a visible undizzy bar (15/20/30 per tier, 240 threshold) | Combos never drop for invisible reasons; both players *see* the wall coming. |
| **Escapes are earned, not stocked** — bursts exist only when the attacker gets greedy (repeats a starter / exceeds the bar); escaping is itself a mind game (gold/blue bursts, burst baiting) | The attacker owns the combo-length decision; even the escape is interactive. |
| **Damage scaling with floors** (×0.875/hit after 3, floors 20–55%) | Long combos pay diminishing returns; big spends stay worth it at the end. |
| **Two-sided meter** — the *defender* gains meter faster the longer they're comboed; whiff-farming is structurally blocked | Getting opened up banks you a comeback; greed feeds your opponent. |
| **A meter with 4+ price points is a decision engine** (supers/DHC/snapback/alpha counter compete for 5 bars) | One sink = a cooldown. Many sinks = choices every time the bar fills. |
| **The intended loop is resets, not combos** — systems price long combos so dropping into a mixup often outbids riding the string | "Offense" keeps both players playing. This is a tuning *target*, not a feature. |
| Free **pushblock** + paid guard-cancel | A defensive baseline that resets spacing for free, with a premium turn-steal on top. |

*Verification corrections kept honest:* IPS records **every move you hit with** from stage 3
(not just chain starters); whiff-cancel exceptions are narrower than folklore; assist-counterhit
scaling is 75% post-2024-patch. None change the lessons above.

### From Naruto (ninja combat canon — claims verified vs Narutopedia)
| Insight | Why it works |
|---|---|
| **Kawarimi is a *deception with a punchline*** — the LOG is the point: visible proof the attacker got fooled; canon allows rigging the log with an explosive tag | Without the decoy object it's just i-frames. With it, it's a mind game with a readable reveal beat. |
| **Shunshin ≠ teleport** — body flicker is fast *traversal* (interceptable, has a path); true space–time teleport is rare and premium | Two mobility tiers with different counterplay: read-and-clip a flicker; predict a teleport's exit. |
| **Shadow clones split chakra evenly** and pop to smoke in one hit | Power now, halved resources after — cost IS the balance. The 1-hit pop keeps deception honest. |
| **Chakra exhaustion is the drama** — total depletion is canonically lethal; the iconic image is a ninja panting, out of chakra | A resource you only notice when it's gone isn't felt. The *empty state* needs teeth. |
| **Hand seals are diegetic startup lag** — longer sequences for bigger jutsu, interruptible mid-weave | Visible commitment, an interrupt meta, cast speed as mastery. |
| **Taijutsu is canonically FASTER than jutsu** and near-free | The tap/hold split (fast free strikes vs. costed committed jutsu) is straight from canon. |
| **Wall/water clinging costs continuous chakra control** | Verticality as a resource decision, not free real estate. |
| **Projectiles are a dialogue** — shuriken deflect shuriken; wire-strings make "you dodged it" layer one of a two-layer trap | Prediction over reaction; the dodge can *be* the trap. |
| **The reveal beat** — false success → puff → log/clone → real attacker behind you | Outplays must be *followable* or they read as random. |

### From the code audit (what ShadowClash actually does today)
Strengths: the movement core (snap + buffer + cut + wall-jump) is genuinely good; the
on-connect chain rule is correctly implemented; hitstop/shake framework exists.

Problems found (file:line-grounded):
1. **No damage scaling** → confirmed touch = 41–50 dmg = 2-touch kills on 100 HP.
2. **No block at all** → no defensive baseline, no mixup triangle.
3. **Dead stats** — `power` only scales pushback; `defense` is never read.
4. **Kawarimi is mashable** — free arming + instant re-arm → near-permanent auto-dodge; **you can attack while intangible**.
5. **Tsubasa's parry**: free, 53% active uptime mashed, counters fullscreen projectiles, flat 1.0s stun.
6. **Chakra has one consumer** — all specials are free; Shin's zoning loop has no cost or counterplay.
7. **Pogo hitbox bug** — the down-strike box sits beside the player (`ox` computed before the pogo branch); striking straight down misses.
8. **Hitstop input leakage** — keydown handlers resolve during the freeze instead of buffering.
9. **No air/ground hit distinction, no knockdown, no throw, no juggle.**
10. **Single bar, no rounds, no timer** → 20-second matches; wall-stall is unbeatable when ahead.
11. **Phantom armor** — Executioner/Ember armor exists in cards + GDD, not in `takeDamage`.

---

## 2. The original synthesis — ShadowClash's own identity

**One line:** the game about shadows is a game about **which hits were real**. Combo
limits, escapes, baits, traps, and comebacks are all expressed through a single ninja
fantasy: **substitution** — not abstract bars and bursts.

### Pillar A — the Substitution Game *(new; learned from SG's earned-burst dialogue + Naruto's log canon)*
1. **The Log.** Every successful kawarimi leaves a **log decoy** that visibly takes the hit
   (smoke, clonk, hit-stop). The attacker's failure is legible — the reveal beat as a rule.
2. **Flagged hits.** Attacker greed earns the defender a free escape: starting a chain with
   a tier already used this combo, or exceeding the stagger budget, flashes the defender —
   kawarimi is **FREE** on that hit. *(The anti-infinite, with no arbitrary cap.)*
3. **The Bait.** The free kawarimi's reappear point is readable (80px behind), so a
   greedy-on-purpose attacker can trigger the flag and camp the exit — the burst-bait,
   fully diegetic.
4. **The Bomb-Log.** During ANY kawarimi, spend +25 chakra to **rig the log with a paper
   bomb**. Swing at the log or camp the exit → detonation. Escape/bait/trap becomes a
   three-layer read. *(No fighter has a booby-trapped burst. This is the signature.)*

### Pillar B — Chakra as a living economy *(learned from SG's two-sided meter + Naruto's exhaustion)*
- **Everything costs chakra** — specials 15–30, kawarimi 35, bomb-log +25, parry 20,
  shunshin 15. Multi-price sinks on one 100-pt pool.
- **Being hit builds YOUR chakra** (scaling with combo length) — long combos hand the
  victim their escape money. Comeback is systemic.
- **"Winded"** — 0 chakra triggers 1.5s panting: slowed movement, no jutsu, **no kawarimi**.
  Overdraft has a body.
- **Wall-cling drains chakra after ~1s** — verticality costs; wall-stall self-punishes.

### Pillar C — Two mobility truths *(learned from shunshin-vs-teleport canon)*
- **Universal Shunshin dash** (15 chakra): a blur that *traverses* — clippable mid-path.
  The approach tool slow archetypes need.
- **True teleports stay premium** (Shin's shadow-step, kawarimi): no path — predict the exit.

### Pillar D — Seal-weaving *(learned from hand seals; new as a hold-tier system)*
Hold special → seal icons flash (~150ms each). Release early = small jutsu; full weave =
big jutsu. Hit mid-weave = jutsu cancelled with partial refund — big moves are fair because
startup is diegetic and interruptible.

### Pillar E — Foundation borrowed openly *(correctness, not identity)*
Damage scaling ×0.875 after hit 3 (floor 20%, specials 45%); visible **stagger budget**
(L+15/H+30/S+20, threshold 240, counterhits subtract); fixed hitstun (no decay); hold-block
with 15% chip + on-block chain pressure; free pushblock + paid kawarimi guard-cancel;
throw (beats block AND kawarimi-arming); air-hit launch + once-per-combo pickup; best-of-3
rounds + 60s timer; hitstop input queueing.

### The tuning target
Max ridden combo ≈ **35–40%** health; reset into a landed second opener ≈ **55%+**.
If optimal play never drops a combo on purpose, the economy is mistuned.

---

## 3. Build order

**Phase 1 — Foundation (fixes; no new design):**
scaling ×0.875, live `power`/`defense` stats, block + chip + blockstun (hold the poof key),
chakra costs on all specials, kawarimi arm-tax (5) + 0.4s re-arm cooldown +
no-attack-while-vanished, parry priced (20 chakra, 0.5s whiff recovery, reflects
projectiles), pogo `ox=0` fix, hitstop input queue, real armor for Ember dash /
Executioner special.

**Phase 2 — The Substitution Game (the identity):**
log decoy + reveal beat, stagger bar + repeated-tier flags, free kawarimi on flagged hits,
bomb-log, throw.

**Phase 3 — The living economy & mobility:**
defender chakra gain, Winded state, shunshin dash, wall-cling drain, rounds + timer,
launch/juggle + knockdown.

**Phase 4 — Character identity:**
seal-weaving hold tiers, shadow clone (halved-meter shell game), Mizu mist as real info
denial (silhouettes), wire-shuriken return arc, shadow-shuriken double-tap.

---

## Sources
**Skullgirls:** mizuumi.wiki/w/Skullgirls (+ /Combo_Mechanics, /Defense, /Team_Mechanics,
/Attacks, /Game_Data, /Glossary), skullgirls.fandom.com Advanced_Mechanics, skullheart.com
IPS/undizzy manual + Complete Walkthrough + May-2024 balance thread, wiki.shoryuken.com
Bursts_IPS_Undizzy + Health_and_Damage.
**Naruto:** naruto.fandom.com — Body_Replacement_Technique, Body_Flicker_Technique,
Flying_Thunder_God_Technique, Shadow_Clone_Technique, Chakra, Nature_Transformation,
Hand_Seal, Taijutsu, Genjutsu, Tree_Climbing_Practice, Water_Surface_Walking_Practice,
Manipulating_Windmill_Triple_Blades, Explosive_Tag.
**Audit:** web/index.html (line refs above), docs/ninja-brawler-gdd.md.
