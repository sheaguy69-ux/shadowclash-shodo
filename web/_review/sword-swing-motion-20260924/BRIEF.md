# Executioner and Kael sword-swing review — 2026-09-24

Anthony says their sword swings look cheap, stiff, short-reaching and lack a shinobi's dynamic speed and flexibility. He wants a complete swing when new frame-by-frame sword art is made. The clean solid white FX look is the preferred effect direction, but FX alone cannot repair the pose sequence. No animation, hitbox, timing or runtime change is approved by this brief.

## What is live now

These strips are extracted from the current packed runtime cells, with the same crop across each row. `source-mapping.json` records the exact key/index mapping. They are static cell inspections, not normal-speed gameplay captures.

- Executioner grounded light: `xnuki1..6`, all six played. The main painted arc appears in `xnuki4` behind the body; the sword has little visible opponent-facing travel before it returns to guard.
- Executioner neutral heavy: the live move art returns `xjodan1..6`. `xjodan4` raises overhead, `xjodan5` is the downward arc near his own body, and `xjodan6` ends with the blade down in front. `xjodan7/8` exist as source cells but are not selected by this neutral-heavy route. This is a route finding, not a proposal to append them without review.
- Kael grounded light: `kdual1..8` is selected. Its clearest painted arc is `kdual4`; the following blade poses are compact and quickly return near the body.
- Kael neutral heavy: `kcross1..8` is selected, but `kcross2` and `kcross3` both map to cell 196, and `kcross6` and `kcross7` both map to cell 200. That yields two repeated holds rather than new spatial progression through those beats.

## Target for a new frame-by-frame sword pass

For **each distinct cut**, stage and review this complete motion at the game's actual display size:

1. **Anticipation:** feet plant, pelvis loads, shoulders counter-rotate, hands and blade move behind the intended cut.
2. **Launch:** rear foot drives the hips and chest; the hands lead the hilt. The blade begins a connected tip path, without a sudden pose jump.
3. **Acceleration:** a readable fast breakdown or selective directional smear bridges the previous tip position to contact. The whole body participates, while the head, costume and sword length stay consistent.
4. **Full-reach contact:** blade reaches clearly beyond the opponent-facing silhouette on the intended attack line. Contact pose, collision region and tip location must agree; do not replace physical reach with a detached arc.
5. **Follow-through:** the blade continues past contact on the same path; torso, hips, arms and scarf follow the momentum. The white motion tail occupies the path behind the blade tip and remains visibly substantial.
6. **Recovery and settle:** mass decelerates into a distinct end pose, then returns smoothly to the approved idle/guard. Do not snap the sword back across the body or reuse a contact drawing as recovery.

Preserve Executioner's approved masked purple/orange identity and sword dimensions. Preserve Kael's approved compact black/gold model, one long and one short sword, and each weapon's hand. Show left and mirrored-right playback, center and wall cases, and consecutive normal-speed frames before any sprite packing. The review should include separate rendered blade-tip paths for each weapon and an explicit before/after look at perceived reach. Keep combat timings and hitboxes unchanged during the visual proposal; any later gameplay reach change needs its own review.
