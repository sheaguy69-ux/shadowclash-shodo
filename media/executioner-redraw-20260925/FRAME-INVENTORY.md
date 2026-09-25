# Executioner complete redraw inventory · 2026-09-25

Anthony asked for **all Executioner frames** to be redone. This means every frame used by his playable animations, not just neutral heavy and shoulder bump. The approved character design is the masked, horned dark Executioner with two small circular orange eyes, one armored shoulder pad, both waist armor pads, rust-orange scarf, one long katana and its scabbard. The pad must lead the shoulder bump. Mask visibility may vary by frame as Anthony allowed. Existing game art is source for move identity and timing, not the new look authority.

Current `web/assets/sprites/executioner.json` has **293 named frame slots** pointing to **246 distinct cells**. The source atlas has **609 physical cells**; **363 have no direct frame name**. Some unaliased cells may still be reached through numeric routes, so reachability needs checking before excluding them from the work. The complete browsable current-cell map is at `web/_review/executioner-redraw-20260925/index.html`; it groups each named animation and also exposes the unaliased physical cells.

Existing owner approvals found before drawing:

- New appearance: `web/_review/sword-swing-motion-20260924/APPROVED-EXECUTIONER-LOOK.md`.
- Original three heavy-swing keys and three shoulder-bump keys: `media/attack-redraws-20260924/APPROVAL.md`.
- Three further heavy-swing pose images approved this session: `art/shodo-source/executioner/executioner-heavy-redraw-20260925/APPROVAL.md`.
- A new lower, longer shoulder-bump contact drawing is shown in the review page as a **candidate only**. It is not part of the approved three-key shoulder-bump strip or a finished eight-frame cycle.
- Many older move-specific approval folders remain under `art/shodo-source/executioner/`; these establish move choreography and source continuity but do not silently approve the newer mask/armor redraw of every cell.

For each animation, assemble the approved model, real startup/contact/follow-through/recovery drawings, correct long-katana length and scabbard, registered feet/pelvis, and both facing previews. Show consecutive frames at game size before touching the atlas. Keep timing, hitboxes, and combat mechanics unchanged during this art pass. An attractive isolated key is not a finished frame-by-frame move. No full-atlas replacement is claimed yet.
