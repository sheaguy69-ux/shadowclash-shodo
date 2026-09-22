# Shin Second Mode — Kakushi-buki core motion

Status: owner-approved and implemented in `SHEET_V 560` (Shin cells 270–287).

The shipped Kage-Nui mode already owns the toggle, tether, and wire Special, but its melee rows use twin kunai. These three strips establish the replacement language: one concealed four-point hira-shuriken held in the hand for every strike.

## Core mapping

| Input | Technique | Grip | Six beats |
|---|---|---|---|
| Light 1 | Tsuki-waza | Kakushi-gata → Kobo-gata | concealed ready → coil → launch → punch KIME → follow-through → conceal |
| Light 2 | Metsubushi | Kakushi-gata → Te-gata | concealed ready → pinch chamber → flick → face-level KIME → recoil → conceal |
| Light 3 | Kiri-kochi | Kakushi-gata → Te-gata | concealed ready → cross-body coil → launch → diagonal KIME → overshoot → conceal |

Kage-Nui's wire Special stays unchanged. Heavy, crouch, and air rows ship from the companion counter-style pack.

## Candidate files

- `shin-tsuki-waza-6frame-v1.png` / `shin-tsuki-waza-motion-v1.gif`
- `shin-metsubushi-6frame-v1.png` / `shin-metsubushi-motion-v1.gif`
- `shin-kiri-kochi-6frame-v1.png` / `shin-kiri-kochi-motion-v1.gif`
- `shin-second-mode-core-review-v1.png`

## QC

All 18 cells pass identity, palette, one-shuriken count, silhouette, full-body crop, white-key extraction, 300×320 registration, footY/scale, and transparent-edge padding checks. They are flipped to the atlas's canonical left-facing orientation during packing.

## Built-in ImageGen prompt set

Shared reference roles: Image 1 = shipped green Shin identity/style/low stance; Image 2 = four-point hira-shuriken shape only. Smooth 2D cel illustration, strict side profile facing right, one horizontal six-panel strip, pure white background, no text, victim, blood, ground shadow, baked Shodo, debris, or FX.

- **Tsuki-waza:** concealed Kakushi-gata ready; shift one point between the index and middle knuckles into Kobo-gata; hip-driven launch; fully extended direct-punch KIME; committed follow-through; recover concealed.
- **Metsubushi:** concealed ready; Te-gata thumb/forefinger pinch chamber; eye-height flick; short face-level rake KIME through empty air; immediate recoil; recover concealed.
- **Kiri-kochi:** concealed ready; Te-gata cross-body coil; short shoulder-driven launch; tight upward-diagonal rake KIME through empty air; compact overshoot; recover concealed. Final edit fixed all six figures to face right with scarf tails trailing left.
