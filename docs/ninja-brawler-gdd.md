# Ninja Brawler — Game Design Document (v0.1)

**Genre:** 2D local 2-player competitive ninja brawler
**Engine:** Godot 4.4 (project lives in [`/godot`](../godot))
**Playable prototype:** "Shadow Clash" — canvas/JS reference build served by the web app at
[`/web/index.html`](../web/index.html)
(open it directly in a browser). All mechanics below are proven there first,
then ported to Godot with proper frame data.
**Feel targets:** Hollow Knight's physics snap + a simplified Skullgirls chain-combo (magic
series) cancel system.
**Art direction:** chibi ninja lineup (see reference image in the design thread) —
frame-by-frame 2D animation, to be produced with the Wildcomiks art generator replicating the
six characters in motion. Until then, the game runs on color-matched placeholder dolls.

---

## 1. Roster

Order matches the reference lineup, left to right.

| # | Name | Weapon | Visual trait | Archetype / signature mechanic |
| - | ---- | ------ | ------------ | ------------------------------ |
| 1 | **Executioner** | Long sword | Horned mask, purple tunic, orange scarf | **Heavy/Berserk** — high impact, slow recovery, massive hitstop. *Blood Rage* special trades HP for +damage. |
| 2 | **Mizu** | Long bo staff | Purple hood, glowing white eyes, purple cape | **Zoning/Support** — mid-to-long staff pokes. *Smoke Bomb* special fades players inside the cloud (`modulate.a = 0.3`). |
| 3 | **Shin** | Shurikens & tools | Crouching, teal hood, blue glowing eyes | **Speed/Assassin** — shuriken zoning; *Shadow Step* teleports behind the target with backstab bonus damage. |
| 4 | **Tsubasa** | Dual swords | Spiky black hair, red scarf | **Precision/Counter** — frame-perfect **8-frame parry** stance triggering a heavy counter state. |
| 5 | **Ember** | Tekko-kagi claws | Olive green hood, glowing green eyes | **Brawler/Rushdown** — fast close-range multi-hits; forward **super-armor lunge**. |
| 6 | **Kael** | Short + long sword | Golden hood, black body armor | **Starter/All-rounder** — balanced physics; swordplay + utility dash. |

## 2. Core gameplay pillars

### A. Hollow Knight movement snap

- **Zero ground friction:** ground deceleration is near-instantaneous — release the stick,
  stop on a dime. Enables frame-tight spacing and baiting.
- **Heavy gravity:** 800–1200 px/s² per character for a grounded feel; strict terminal
  velocity cap in air.
- **Pogo:** downward strike in mid-air that connects with an opponent or physical hazard
  bounces the attacker upward and **refreshes jump vectors** (air jump restored).

### B. Simplified Skullgirls chain cancels ("magic series")

Universal three-tier chain: **Light → Medium → Heavy**.
On a successful **hit or shield block**, remaining recovery frames can be canceled
immediately into any *higher* tier. Whiffs cannot cancel — whiff punishing stays real.
Easy to learn (three buttons, one rule), high execution ceiling (confirms, delays, baits).

### C. Kawarimi — the ninja "poof" substitution

- **Trigger:** tapping the defend button at the frame of impact (small input buffer).
- **Cost:** 35% of the chakra (stamina) pool.
- **Effect:** smoke cloud burst, player alpha drops to 0.3 for the blink, and the player
  instantly relocates relative to the attacker's facing — 80 px behind them (or vertically
  up if blocked by geometry). Negates the hit entirely.

## 3. Technical architecture (Godot 4.x)

- **Modular FSM:** each player is a `CharacterBody2D` with a `StateMachine` node owning
  modular `State` child nodes (`Idle`, `Run`, `Air`, `Attack`, `Defend`, `Hitstun`,
  `Kawarimi`, plus character-special states like `Parry`, `Lunge`, `Teleport`).
- **Data-driven characters:** one registry (`characters.gd`) holds each ninja's physics
  params, palette, frame data, and special id — states read data, never hardcode.
- **Frame data in frames:** startup / active / recovery are authored in 60 fps frames,
  fighting-game style.
- **Hit resolution:** `Hitbox`/`Hurtbox` Area2D pairs; hitstop via the `Juice` autoload
  (see [game-juice-freeze-frame.md](./game-juice-freeze-frame.md)).
- **Local 2-player input:** duplicate action sets `p1_*` / `p2_*`, keyboard split
  (WASD+JKL; vs arrows+numpad) and per-device gamepad mapping, registered in code by an
  `InputSetup` autoload.

## 4. Out of scope for v0.1 (roadmap)

- Character select screen (v0.1 picks via constants in `main.gd`)
- Frame-by-frame sprite animation (Wildcomiks-generated sheets replace placeholder dolls)
- Stages/hazards beyond the first arena, training mode, rollback/online play
- Audio pass (SFX hooks exist; assets TBD)
