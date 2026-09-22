# Shodō Edition — Standalone First-Form Conversion

## Global constraints

- Work only in this independent `SHODO-EDITION` repository; never modify the recovered rollback edition.
- Preserve combat, controls, timing, hitboxes, physics, stages, UI, runtime frame aliases, and the shared Shodō renderer.
- Serve this edition on `:9101`; recovered stays on `:9100` and the gallery on `:9102`.
- Use approved first-form archive art only. Never regenerate art and never expose second forms.
- No legacy playable-character cell may be stored or reachable in this edition.

## Task 1 — Clean standalone export

- Export only post-baseline approved Shodō cells into fresh atlases.
- Preserve exact RGBA pixels and existing runtime metadata.
- Prove zero legacy cells and zero orphan cells.

## Task 2 — Complete first-form packing and portraits

- Inventory required live routes for all nine fighters.
- Pack missing approved first-form rows with one uniform scale per sequence.
- Replace all nine portraits from approved Shodō sources.

## Task 3 — Routing and provenance

- Keep existing runtime aliases and first-form gate.
- Remove silent idle/procedural character-art fallbacks.
- Record fighter, runtime alias, approved source, source hash, and final atlas/manifest hashes.

## Task 4 — Verification and launch

- Audit geometry, clipping, footing, scale, anatomy, weapons, identity locks, routing, provenance, and second-form exclusion.
- Prove gameplay body dimensions and representative hitbox values are unchanged.
- Verify all nine fighters live on `:9101`, then commit this independent repository.
