# Oni — current Shodo moves and controls

Updated September 7, 2026 for SHODO-EDITION on `:9101`. This replaces the player instructions in the older SHEET 515 `ONI-MOVELIST.md`. It describes the current playable kit, including where an approved replacement drawing has a different title from its retained mechanic.

Oni's current Spectral Founder design has one matte-black bo staff and one sheathed black katana crossed behind his torso, a white horned mask, black armor and a torn red half-cape. The August 27 model supersedes the older no-staff brief. The August 31 art routing explicitly preserved the existing damage table; a drawing named “rush,” “counter” or “super” did not itself implement a new command.

## Buttons

| Action | Player 1 | Player 2 |
|---|---|---|
| Move | A / D | Left / Right arrows |
| Jump | W | Up arrow |
| Down | S | Down arrow |
| Light | F | I |
| Medium | J | U |
| Heavy | G | O |
| Special | H | P |
| Guard | C | M |

Forward/back are relative to combat facing. Running away turns the running drawing in the movement direction; attacks use combat facing. Up is also the jump button, so a real Up press normally takes off before the attack.

## Ground attacks

| Input | Current move / behavior |
|---|---|
| Light | **Spectral Iai Fang:** sword draw-cut. Repeated connected Light presses continue the three-beat chain, with a launcher on the final beat. Current drawings reuse the sword row; the old separate body-jab and uppercut drawings are absent. |
| Forward+Light | **Hollow Gate Spearhand:** forward hand strike. |
| Back+Light | Rear strike, using the available low-sweep artwork. |
| Down+Light | **Abyss Staff Reap:** low sweep that trips. |
| Up+Light while strictly grounded | Forward-facing draw-cut; normal Up input jumps first. |
| Medium, any direction | **Hollow Gate Pommel Break:** forward-facing medium strike and Light→Medium→Special combo bridge. Held direction does not change its hitbox. |
| Heavy | **Founder's Severance:** committed heavy cut. |
| Forward+Heavy | **Black Pillar Staff Break:** long staff thrust. |
| Back+Heavy | Retreating body step with a forward cut. |
| Down+Heavy | Low trip strike. |
| Up+Heavy | **Pillar Ascension:** upward launcher. |
| Special | **Black Torii Procession:** ranged wire setup strike. This is a long hitbox, not a flying projectile. |
| Forward+Special | Close blackout quick-draw. Requires an opponent within 92 px to connect; the animation can whiff farther away. The installed drawing is titled **Crimson Founder Charge Rush**, but the owner-approved current move is the close draw. |
| Back+Special | Rear wire strike. The installed drawing is **Hollow Shrine Reversal**; this command currently strikes behind Oni rather than waiting to counter a hit. |
| Down+Special | Smoke concealment, **two uses total per round**, shared between ground and air. After both are used, this input becomes neutral Special and needs 25 chakra. |
| Up+Special | **Pillar Ascension:** rising attack with startup invulnerability. Early first-jump Up+Special also selects this launcher. |

Ordinary Special starters cost ** 25 chakra**. Smoke uses its two-use allowance instead. The engine stores the displayed chakra bar in the `stamina` field; there is no separate `chakra` pool.

## Air attacks

| Input | Current move / behavior |
|---|---|
| Neutral / Forward / Back+Light | Air staff attack, with a limited air-float allowance. |
| Down+Light | Downward pogo; contact bounces Oni upward. |
| Up+Light | Upward poke and launch. |
| Medium, any direction | Medium air staff attack. |
| Neutral / Up+Heavy | **Meteor Staff:** forward air heavy. |
| Forward+Heavy | Dedicated four-frame airborne **Severance**. |
| Back+Heavy | Forward air hit using the shared air staff row. |
| Down+Heavy | **Falling Pagoda / Meteor Break:** hang, dive, ground impact, recovery. |
| Neutral Special | **Cursed Burst:** short hitboxes on both sides. **Sixfold Eclipse** art appears only in the grounded portion of this air-origin move. |
| Forward+Special | Advancing air strike. |
| Back+Special | Invulnerable air retreat; no damaging hitbox. |
| Up+Special | Rising air attack; early first-jump input can select the ground launcher described above. |
| Down+Special | Smoke while charges remain; otherwise neutral air burst, requiring 25 chakra. |

## Wire follow-ups

A clean Special hit opens a **0.55-second wire-bind window**. Press **Special again**, with the direction below, to convert. Oni approaches during the 0.10-second startup and stops at the booked destination; the target is not reeled to his feet. The follow-up does not spend another 25 chakra, and a moving target can evade it.

Other attack buttons can also reach the conversion, but their earlier command routes can take priority. For example, grounded Back+Light after the starter recovers performs the rear kick. Wall Light remains a throw, and Down+Special uses smoke while charges remain. Special with neutral, forward or back input is the consistent conversion command.

| Follow-up direction / situation | Current finish | Current drawing |
|---|---|---|
| Neutral Special | Short-wire slice | **Last Gallows Doctrine** |
| Forward+Special | Forward execution | **Black Pillar Break** |
| Back+Special | Claw execution | **Ghost-Climber Reap** |
| Air Special, opponent airborne | Air-target execution | **Silent Star Doctrine** |
| Air Special, opponent grounded | Pulley slice | **Last Gallows Doctrine** |

The retained internal conversion names “katana” and “knives” predate the installed staff/pommel and shuriken-doctrine drawings. Those names are not extra inputs or a promise of new projectile mechanics. The current in-game instructions use “execution” to avoid advertising the wrong weapon action.

## Movement and defense

- Hold Jump for the full arc; release early for a short hop. A second press uses the remaining air jump. Oni retains a 1.10 jump multiplier; Exile's 1.12 remains highest.
- Double-tap a horizontal direction for Shunshin. Guard+direction or Down+double-tap performs the committed dodge roll.
- Hold toward a side wall to cling. Jump kicks away from it. Wall Light throws a **shuriken**, with three throws per airborne trip, replenished on landing.
- Light+Heavy throws. The ground art is **Founder's Judgment**; the airborne throw is **Sky Harvest**.
- Guard+Special creates **Ash Effigy Bunshin**, costing 30 chakra and lasting 2 seconds.
- The first-form-only build has no accessible V/K second-form toggle.

## Retired instructions and artwork without an independent command

The old knife→jab→uppercut labels, cartwheel/backflip commands, close Razor Whip, long Phantom Dash, Anchor Slip, ground Stomp and hidden handseal dial do not describe this version's commands. The unused handseal input sequence has been removed.

**Moonless River Doctrine**, **Scarlet Fang Doctrine** and **Twin Eclipse Doctrine** are archived artwork, with no separate current input. **Sixfold Eclipse** is not a separately selectable super. Adding independent mastery modes, a new rush, or a reactive counter would be a new moveset implementation, separate from correcting the current game's inputs and animation routing.

Authority: shared ShadowClash ledger, August 27 Spectral Founder ruling; August 31 SHEET 673 art-routing note; September 6–7 wall-projectile ruling; `docs/ONI-EVERYTHING-YOU-GAVE-ME.md` wire-conversion instruction; current runtime branches and real-input probes.
