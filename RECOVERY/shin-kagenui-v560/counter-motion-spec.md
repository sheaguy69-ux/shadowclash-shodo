# Shin — Kage-Nui Counter Style (candidate v1)

Status: owner-approved and implemented in `SHEET_V 560` (Shin cells 288–323). Built with the built-in ImageGen workflow.

## Six-frame move order

| Row | Move | Beats |
| --- | --- | --- |
| 1 | Tai-sabaki | guard → lean → sidestep/parry → slip → palm redirect → guard |
| 2 | Kote-gaeshi | guard → catch → outward turn → hip sink → ground control → release |
| 3 | Ashi-barai | guard → coil → drop → full sweep → retract → guard |
| 4 | Karami-dori | coil → cast → wire arc → brace → pull → catch |
| 5 | Tobi-geri | load → knee drive → tuck → side kick → land → guard |
| 6 | Utsusemi | guard → duck → dash smear → reappear → palm counter → guard |

The names are game choreography inspired by Japanese martial vocabulary, not a claim that this sequence is a documented historical kata.

## Deliverables

- `shin-counter-style-review-v2.png` — labeled 36-cell review board
- `shin-<move>-6frame-v1.png` — six source strips
- `shin-<move>-motion-v1.gif` — motion previews, except use `shin-karami-dori-motion-v4.gif` for Karami-dori
- `karami-frames-v1/` — manually isolated Karami-dori preview frames

## Final prompt set

Shared prompt: six-frame horizontal fighting-game sprite review strip on flat white; use Shin's idle reference as the strict identity/outfit anchor and the approved concealed-shuriken board as the style anchor; exactly one compact green-and-teal Shin per panel; permanent low crouch; teal scarf trails image-left; Shin faces image-right; full body, consistent scale and ground line; exactly one four-point wire shuriken; crisp hand-drawn 2D cel shading. Avoid opponents, victims, blood, gore, swords, kunai, extra weapons, purple, text, labels, watermarks, scenery, costume changes, perspective changes, and baked Shodo.

Move prompts:

- Tai-sabaki: guarded crouch, anticipation lean, diagonal sidestep/parry, torso slip, palm redirection, guarded recovery.
- Kote-gaeshi: catch an invisible wrist, outward two-hand turn, hip sink, downward control, release; no opponent shown.
- Ashi-barai: grounded weight shift into one low circular leg sweep; no spinning jump.
- Karami-dori: one underhand shuriken cast, one continuous wire arc, taut brace, two-hand pull, clean catch; never duplicate the star.
- Tobi-geri: low load, knee drive, compact tuck, one side-kick apex, compressed landing, low recovery.
- Utsusemi: duck, rapid rightward body-slip with abstract teal ribbons rather than a duplicate body, short palm counter, advanced guard.

## Production gate

The 36 cells preserve Shin's palette, single-character staging, and one-tool language. They pass owner approval, white-key extraction, exact `300×320` registration, shared `footY`/scale, and transparent-edge padding checks; Karami's long wire is rendered procedurally so Shin stays at canon scale without clipping.
