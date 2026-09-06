# Shin old-art removal — SHEET_V727

Anthony reported that Shin still switched to an old frame and requested its removal. Inspection of all164 active cells found24 flat, saturated green cells354–377 in the four directional Heavy rows. These had been ported from RECOVERED in3317a1b, whose note already identified their mismatch with Shodo Shin.

Repointed those24 aliases to existing current-art poses. Each row retains six cells, so its authored timing track still applies. No attack duration, hitbox, damage, movement impulse or recovery changed.

| Heavy direction | Current cell sequence |
|---|---|
| Forward |258,260,261,245,319,321|
| Back |314,315,316,319,320,321|
| Down |250,251,253,254,256,257|
| Up |330,331,332,333,335,336|

Live review exposed missing facing metadata in the reused families. Raw artwork confirms245–248,317–320 and332–336 face right; their neighboring ready/settle poses face left. Added the13 mirror flags to the shared manifest so normal attacks, directional attacks and character copies receive the same correction.

All old354–377 references are absent from the active frame map. The atlas itself is unchanged, preserving original cell indices and pixels. No new raster art was generated. These sequences reuse current Shin artwork; they are not newly drawn directional animations.

Evidence is in `media/shin-old-frame-20260906/`: active inventory, raw facing comparisons, replacement map, per-cell QC, original PNG hash, and consecutive live filmstrips. `tools/check_shin_current_art.py` exercises both facings in base mode and Kage-Nui, checks actual rendered direction, retired-cell exclusion and the unchanged mechanics.

Verification passed:14 live directional-Heavy cases (both facings, base4 and Kage-Nui3),84 authored timing-slot samples,12 related-pose routing fixtures and588 consecutive live frames. Final base and stance filmstrips were visually reviewed. The22-direction move table and nine-sheet geometry checks pass; PNG SHA-256 is unchanged and no active Shin alias points to354–377. This checkpoint fixes Shin's reported old appearance; the wider roster sweep remains unfinished.
