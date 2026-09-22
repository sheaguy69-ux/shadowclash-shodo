# ShadowClash character attack-frame and VFX brief

**For:** Claude/Fable ("Clyde") and anyone implementing the new character frames  
**Runtime checked:** SHODO-EDITION on `:9101`, `SHEET_V 709`, local head `1429501`

## Owner direction — this is binding

**Do not cut, erase, crop, mask, shrink, recolor, or treat any approved attack VFX as disposable decoration.** Slash arcs, X-marks, claw rakes, smoke, mist, water trails, sparks, halos, wire, afterimages, impact bursts and attack debris are part of the attack artwork. They communicate direction, reach, contact, timing and character identity.

An attack frame is complete only when the fighter, weapon **and the full approved effect** survive into the live game.

## Framing law

1. Measure fighter scale from the head or another validated rigid body landmark. **Never use total ink area to size the fighter**; large effects make a correctly sized body look oversized.
2. After body scale is locked, frame the union of the fighter, weapon and full VFX envelope with transparent safety margin.
3. If the complete effect does not fit, grow the cell/canvas or stop for a geometry decision. Never shrink the fighter or clip the effect just to make the old box work.
4. No effect may end in an accidental straight cut at a cell edge. A traveling effect must fade inside the frame or continue through its designated procedural runtime layer.
5. Preserve near-white and enclosed details during keying. Mizu, Tsubasa and Ember recently lost near-white eyes to the keyer; Oni's white mask is also artwork, not background.
6. Do not confuse baked and procedural effects. Keep exactly one owner of an effect, but verify the **final composite** still shows it. Example: Exile's chain-to-wall body row is intentionally chain-less because the live rope is procedural; the finished attack must still show the whole rope, hand anchor, wall bite and weapon end.
7. Every visible fighter frame, afterimage, clone or decoy stays on the shared `drawShodoFrame()` path. Non-character FX may remain procedural.

## Shared attack dynamics

- Every one-shot row must read as distinct cel beats: **anticipation -> launch/action -> contact -> follow-through -> recovery**. Do not cross-fade poses.
- Direction is captured when the button is pressed. The picture must continue to show the chosen forward/back/up/down move even if the player releases the direction during the animation.
- Air attacks stay airborne through recovery. Never settle an airborne fighter to a standing/grounded cell before landing.
- Contact VFX belongs on the contact beat; trails belong on travel/follow-through beats; recovery clears the effect without cutting it off.
- The neutral Medium board is the combo bridge from Light into Special. All nine have a neutral Medium, but **27 directional Medium inputs still reuse neutral art**. Do not invent those boards until Anthony chooses which directional Mediums should become unique.
- Some directional attacks still borrow neutral art. That is a coverage issue, not permission to discard any unique source row.

## Character-by-character attack read

| Fighter | How the attacks must move | Signature attacks and protected VFX |
| --- | --- | --- |
| **Executioner** | Heavy, planted judgment with slow body commitment and extremely fast iaijutsu cuts. One slim katana; the body should not chase the size of the crescent. | Iai Quick-Draw, Sheath Charge, Drive Stab, Gyaku Kesa launcher, Suso-giri, Harai Otoshi, Shadow Slip/Reprisal and Chudan stance. Preserve orange slash arcs, the full gallows/rising crescents, sheath-pass streaks and Dread embers. The approved large `xrise` crescent is attack art; if it cannot fit, stop for cell geometry instead of cropping or shrinking him. |
| **Mizu** | Long-range bō spacing: both hands control the staff, with push-pull footwork and flowing grip changes. Her mist changes visibility and distance, not her identity. | Bō Thrust, Low Sweep, Rising Staff, Guard-Break Spin, Reed Withdraw/Pierce, Vaulting Staff Slam, Mist Drop and Hanbō Kaeshi. Preserve water crescents, tip trails, mist silhouettes, vanish/reform edges, landing splash and Water Slick. Protect her near-white eyes from keying. |
| **Shin** | Fast hand-to-hand strikes connected to shuriken and razor-wire control. His body attacks hit sharply; wire actions pull, tether or reposition. | Flying Kick Rush, Fudo Ken, Sokuyaku Ken, Omote/Ura Shuto, Rising Anti-Air, Wire Shuriken, Wire-Step, Shuriken Fan, wall throws and Kage-Nui/Kage Step. Preserve teal smoke, wire lines and glints, shuriken trails, contact sparks and the vanish/re-form silhouette. Never turn wire or smoke into crop waste. |
| **Tsubasa** | Precision-counter fighter with exactly two short tantō. Fast crossing steps, reverse-grip rakes and clean parry-to-answer timing. | Parry Stance, Reverse-Grip Rush, Low Tantō, Rising Twin Slash, Evasive Flick, Aerial Dive Cut, Air-Throw Setup, Swallow's Pass and Tantō Reverse Flurry; Sakate changes the read into a mark-and-answer sequence. Preserve twin red/gold slash trails, X-cross flashes, pass-through afterimages and four distinct rake beats. |
| **Ember** | Low, aggressive claw rushdown. Alternating hands advance the body; every ordinary rake reads as **three parallel claw lines**, while the finisher uses both claws in an X. | Cinder Fang Rake, Rushing X-Shred/armored claw dash, Shred Charge, Ground Rip, Ceiling Hook, Claw Rend/Low Rake/Retreat Swipe, Blade-Trap Parry and wall Pounce Dive. Anthony explicitly kept the slash art: preserve the silver/white three-line rakes, the full X, sparks and claw trails. Do not recolor them merely because Ember's costume is green. |
| **Kael** | Balanced nitoryū using one long sword and one clearly shorter sword. The long blade leads; the short blade answers. Movement is clean, quick and symmetrical without making the blades equal. | Shadow Cyclone, Twin Fang Traverse, Twin Cyclone, Low-High Scissor, Rising Launcher, Skyward Fang, high/low parries and Niten Parry. Preserve both gold arcs, cyclone rings, crossing X-flashes and dash streaks. Every effect must still show which blade moved first and where the second crossed it. |
| **Exile** | Fast kusarigama zoning: body motion, sickle, chain path and weighted end form one readable attack. Her movement can cross the screen, wall or opponent, but the chain must remain spatially continuous. | Iaijutsu Cross, Heli Spin, Chain-Grapple Swing, Chain Anchor, Serpent's Tongue, Side/Up Reach, Counter-Weight and Champion Mode. Preserve the complete chain/rope route, wall-bite spark, kama, weighted ball, orbit arc, corridor/afterimage and impact effects. Procedural rope and baked body frames must meet at the measured hand anchor without gaps or double chains. |
| **Mokurai** | Bare-hand and prayer-bead power: planted, circular area control in normal form; delayed, broken rhythm in The Crack. He has no bō staff. | Prayer Halo, Temple Bell, Bell Ringer, Sage's Palm, Bead Snare, Zen Reflect, Prayer Orbit, Enlightenment and The Crack. Preserve gold halos, bell shockwaves on both sides, palm blasts, bead/wire paths, ash-white feint tells, cracked mask accents and landing rings. A halo enlarges the effect envelope; it does not mean the body is too large. |
| **Oni** | The Founder is violent rushdown built around the **right-hand claw**, razor wire, needles, knives and sudden position changes. He has no second-form staff moveset. | Razor Whip/Wire Shot and their executions, Phantom Dash, Anchor Slip, Rising Spiral/Claw, Smoke Bomb, Stomp, Meteor Break, cartwheel/backflip attacks, wall needles, Sky Harvest and the hand-seal attack. Preserve crimson smoke, black/red slash bursts, wire lines, claw arcs, needle/knife trails, ash-effigy effects and the Phantom Dash blackout. His white mask, red eyes and horns must never be keyed away as background/effect. |

## New frame work Claude must account for

1. **Air-hurt row for every fighter:** 3-4 beats, body off-balance, no ground line, no cast shadow. This is the remaining fix for airborne hitstun; do not fake it with a standing hurt or a neutral flight pose.
2. **Directional Mediums:** mechanics currently expose 27 directional Medium slots that reuse neutral Medium art. This is owner-decision work; list it, do not silently fabricate it.
3. **Directional aliases:** `SHEET_V 709` repaired attacks that were incorrectly drawing idle/ground cells, but some inputs still borrow an existing kick or neutral row. Test each requested new row through the actual input before calling it implemented.
4. **Effect-heavy geometry:** Executioner's rising crescent, Ember's X-shred, Mokurai's halos, Mizu's water/mist, Exile's chain, Shin's wire, Tsubasa's crossing trails, Kael's twin arcs and Oni's smoke/wire must be framed using their full effect extents.

## Acceptance gate for every row

- Owner-approved source montage and per-cell grade exist before packing.
- Body scale is proven with a body landmark; VFX are excluded from that scale calculation.
- Fighter + weapon + VFX all fit with transparent margin; zero accidental hard-edge clipping.
- Alpha/keying preserves eyes, masks, steel highlights, wire, smoke and soft effect falloff.
- Row is appended, not destructively repacked; `SHEET_V` changes with any sprite change.
- The real input reaches the intended row; it does not draw idle, neutral or ground art by mistake.
- A consecutive live filmstrip shows anticipation, contact, follow-through and recovery, including the complete VFX.
- Air moves contain no ground shadow/line and do not snap upright before landing.
- Final visible fighter/copy passes through `drawShodoFrame()`.

**Bottom line:** the VFX are not extra pixels around the character. They are part of the attack design. Frame around them; never frame them out.

## Current references

- `web/index.html` -> current `MOVES_LIST` and `SHEET_V 707-709` routing notes
- `RECOVERY/MOVE-LISTS.md` -> detailed per-character mechanics and move intent
- `docs/ART-BRIEF-OUTSTANDING-2026-09-02.md` -> effect-heavy geometry and open art decisions
- `docs/ROSTER-FRAME-AUDIT-2026-09-02.md` -> historical cut-off/erasure failure evidence
- `AGENTS.md` -> append-only, owner-review, live-filmstrip and shared Shodō renderer laws
