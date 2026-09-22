# Corner defense — September 20, 2026

Owner request: stop repeated wall combos from keeping a fighter unable to defend or escape.

## Cause reproduced

The previous build refreshed hitstun on every clean contact, but its combo scaling reduced only damage. The wall absorbed the defender’s knockback, keeping free light attacks in range. Repeated wall-splat moves also added another 0.3 seconds of stun on every contact. The old help text promised a free substitution escape although that mechanic had been removed.

A real-keyboard regression probe ran eight attackers on both walls with neutral and forward light pressure (32 cases, 900 simulation ticks each). Seven of eight attackers could sustain the trap in both variants and on both walls; those 28 cases offered zero actionable frames after the first hit despite held Guard. Health alone was raised to keep the test running; resources and attack/stun rules remained unchanged. Cinematic hitstop was disabled in this probe to measure simulation frames. A separate before/after replay runs actual gameLoop with hitstop.

## Player-facing change

- After four clean hits or blocked contacts near a solid wall, hold Guard to use **Corner Break**: P1 **C**, P2 **M**, controller **LB/RB**, or the touch **GUARD** button.
- The break clears stun and interrupted actions, pushes nearby opponents away without damage, and provides 0.45 combat seconds of protection to move, jump, guard or roll. Choosing an attack ends the protection. It requires no chakra, including while winded.
- Another four contacts earn another break. There is no cooldown that can strand a defender in the same infinite again. Buildup clears on leaving the wall or after 0.8 seconds of actionable safety.
- Wall-splat can extend a continuous combo only once. Ordinary move timing, damage scaling and midscreen links retain their existing rules.
- Applies to both arena walls and the faces of interior solid walls. Open ledges, holes and camera boundaries do not award it.
- Grabs, wire tethers and stage snares cannot immediately cancel the protected escape. CPU fighters use the same held Guard path.
- A visible counter and hold-Guard prompt teach the mechanic. Training: press **B** once from Drill OFF for the Corner Break drill, move back to a wall, and hold Guard while the dummy attacks.

The brief protection is a defensive window, not a damaging counter. The received fourth hit still counts; a killing blow is not undone. This is an explicit combat-rule change in response to the owner’s request. No character art or source sprite files were changed.

## Verification

Results pending final frozen-source checks. Evidence is stored locally under `media/corner-defense-20260920/` (ignored by Git). Implementation is local on the Shodō edition at port 9101; no commit, merge or public deployment was made.
