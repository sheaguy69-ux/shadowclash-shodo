# Shadow Clash combat FX concepts — 2026-09-24

Review page: `index.html`. Summary: `contact-sheet.jpg`; blade-direction study: `direction-study.png`; Kael baked-FX comparison: `kael-before-after.jpg`.

Anthony asked to see visual choices before any implementation: long blade-direction trails with a substantial tail, white/yellow variants, shodō brush slice hits, punch effects, and a cleaner way to recolor some effects baked into character frames. This folder is review-only. No image here is routed by the game, packed into a sprite sheet, or approved by creation alone.

| Preview | Prompt focus | Intended use to discuss |
| --- | --- | --- |
| `blade-tail-white.png` | Single long ivory-white arc; broad tail behind the traveling tip; sparse ink edge | Long sword swings |
| `blade-tail-yellow.png` | Golden-yellow hook arc; solid broad tail and narrow white cutting edge | Alternate color/heavy swing |
| `twin-blade-trails.png` | Two distinct opposite-curving ivory trails, one per short blade | Kael/Tsubasa dual-weapon motions |
| `brush-slice.png` | Diagonal solid white shodō cut with restrained yellow contact splinters | Blade hit only |
| `blade-clash.png` | Compact white cross with three gold flecks | Steel-to-steel contact |
| `claw-rake.png` | Exactly three ivory/yellow curved prongs | Ember's three claws per hand |
| `punch-light.png` | Tight white compression mark and short blunt ticks | Light hand-to-hand hit |
| `punch-heavy.png` | Wider white/yellow shodō burst | Heavy hand-to-hand hit |
| `staff-impact.png` | Two blunt gold motion arcs ending at white contact | Mizu's bo staff |
| `kama-hook-trail.png` | White/yellow long sweep curling back at the leading hook tip | Exile's kama blade |

All ten source FX `raw/*.png` images came from the built-in image editor, which did not report a verifiable model identity. `raw/kael-recolor-white.png` is a built-in edit of `raw/kael-source-frame.png`, the existing Kael review frame. The edit is conceptual and changes more than pixel color, so it must not be treated as an exact production frame. `build_sheet.py` copies the generated visual shapes into presentation cutouts, removing faint alpha halos while retaining the unmodified originals in `raw/`. It also builds the nine-core contact sheet, comparison and direction diagram. No external API or paid generation was used.

Before any later implementation, measure each attacking blade's root and tip across the actual animated frames; attach the long trail to those paths, honor facing/mirroring, and suppress duplicates where baked FX already exists. Slice contact, clash, and punch impact are separate events. Existing baked effects should be reviewed per frame for recoloring; this concept does not authorize bulk repainting or erasing animation frames.
