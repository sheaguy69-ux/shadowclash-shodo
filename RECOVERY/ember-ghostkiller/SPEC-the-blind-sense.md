# EMBER — WHY THE FACE IS WRAPPED

**Owner spec, Aug 21 2026:** *"ember having a killer where he wrap his face all the way up —
he do that because he blocking his sight and all his sensitive stuff for his ears and his
nose. he... become stronger where he can hear his opponent and smell his opponent anywhere
they are, yet in the darkness."*

So the wrap is **not a look, it is the mechanic**. He blinds himself on purpose. Giving up
sight sharpens hearing and smell until he can locate an opponent **anywhere, including in
darkness** — concealment stops working on him.

That also explains the art: the killer form has **no visible eye** because his eyes are
covered. Every one of the nine strips in `strips/` draws it that way.

## The engine already has everything this would read

Concealment is not decorative here — it is a real system with one flag:

| mechanism | what it does | where |
|---|---|---|
| **Mizu's mist** | the caster goes to `alpha = 0`, **completely invisible**; everyone else in it dims to 0.3 | `index.html:3127-3150` |
| `hiddenInSmoke` | *"the flag every other system reads"* — CPU targeting, own-player marker | `:3135`, `:3146` |
| teleport vanish | `vanishTimer > 0` = invisible **and** intangible | `:2278`, `:3319` |
| bunshin / kawarimi | clone and log-decoy misdirection | `:2249`, `:1623` |

**And the CPU brain already models being blinded.** When the foe is `hiddenInSmoke` it steers
by `lastSawFoe` — last known position — decaying over 1.2s (`:14197-14206`). The comment
there says it plainly: *"which is what a blinded opponent actually has."*

So the sense mechanic is a **one-condition inversion** of code that exists: Ghost Killer Ember
is the fighter who does **not** lose them.

## ⛔ But the human-facing half collides with an owner ruling — his call, not ours

For a **human** playing Ghost Killer, sensing a hidden opponent means something has to appear
on screen. That is exactly what was already killed:

> **HIDDEN MEANS NOTHING IS DRAWN — NO TELL AT ALL** (owner: *"drop it"*). A faint ground ring
> used to mark a hidden fighter… *"a tell that says WHERE she is gives away the only thing the
> mist is protecting, and on a shared screen the opponent reads that ring just as easily as
> she does."* — `index.html:9437-9446`

**The reason given then applies to this now.** One shared canvas: a sense-silhouette drawn for
Ember's player is read just as easily by Mizu's. Nothing was built here, because building it
would re-add the thing that ruling deleted.

There is also a balance consequence worth stating before anyone rules: Mizu's mist is her
whole card, owner-ruled **completely invisible with no cooldown** (*"i want her completely
invisible"* — `:7711`). A sense that sees through it blanks that card whenever Ember is in
Ghost Killer.

### What is clean, and what needs a ruling

- **CLEAN, no tell involved:** a **CPU-driven** Ghost Killer Ember keeping true position
  instead of `lastSawFoe`. Pure AI behaviour, violates nothing. Only bites when the CPU is
  playing Ember.
- **NEEDS A RULING:** anything that shows a human player where a hidden opponent is.

Three ways it could go, all his to pick:

1. **Screen tell after all** — overrides the no-tell ruling for this one case.
2. **Direction only, no position** — Ember auto-faces the hidden opponent. Weaker leak, still a leak.
3. **No visual at all** — the sense is expressed as reach or tracking on his moves rather than as information.
