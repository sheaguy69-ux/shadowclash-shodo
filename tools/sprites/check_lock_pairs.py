#!/usr/bin/env python3
"""PRE-FLIGHT the blade-lock contact anchor, before a single cell is drawn.

The one failure a per-cell review cannot see: each fighter's lock cells can grade
perfectly on their own and still not MEET. The anchor is shared, so it has to be
checked as a PAIR, and it can be checked right now — the anchor is pure geometry, so
it does not need the lock art to exist. Existing guard cells stand in for the pose.

What this measures, per pair:
  overlap    how far the two bodies interpenetrate at that separation. Two fighters
             leaning into a bind SHOULD overlap slightly at the weapon; bodies
             overlapping is a bug.
  gap        clear space between the two bodies. A large gap means the fighters are
             holding their weapons out at arm's length past a void, which reads as
             two people missing each other rather than straining.
  anchor dy  vertical distance from the shared anchor to each fighter's own chest
             centre. Large and opposite values mean the shared height flatters one
             fighter and cramps the other.

Writes a preview PNG per pair so the numbers can be eyeballed, since a number can be
in range while the picture is still obviously wrong.

Run: python3 tools/sprites/check_lock_pairs.py
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPRITES = os.path.join(REPO, "web", "assets", "sprites")
OUT = os.path.join(REPO, "docs", "handoff", "blade-lock", "pair-preflight")

# Pairs worth checking are the EXTREMES, not every combination. 6 lockers is 15 pairs;
# the anchor either survives the extremes or it does not.
STRESS = [("executioner", "mizu"),   # tallest vs shortest — the height extreme
          ("ember", "mizu"),         # widest in-cell body vs narrowest
          ("kael", "executioner"),   # the two tallest, both long blades
          ("tsubasa", "mizu"),       # shortest weapon vs longest weapon
          ("ember", "kael"),         # widest torso vs the longest blade
          ("shin", "executioner")]   # shortest blade (a held kunai) vs the longest
# exile is NOT a stress pair: her packed sheet is a superseded design, so measuring her
# would pre-flight an anchor for a character who does not look like that. She returns when
# her true sheet lands.


def font(size):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()


def load_spec():
    with open(os.path.join(REPO, "docs", "handoff", "blade-lock", "lock-spec.json")) as fh:
        d = json.load(fh)
    return {f["fighter"]: f for f in d["fighters"]}, d["anchor_onscreen"]


def guard_cell(f):
    """A stand-in for the bind pose: the closest existing pose to a weapon being set."""
    with open(os.path.join(SPRITES, f + ".json")) as fh:
        d = json.load(fh)
    sheet = Image.open(os.path.join(SPRITES, f + ".png")).convert("RGBA")
    fw, fh = d["frameW"], d["frameH"]
    for key in ("xblkguard", "block", "idle"):
        if key in d["frames"]:
            i = d["frames"][key]
            return sheet.crop((i * fw, 0, i * fw + fw, fh)), key
    raise KeyError(f)


def body_span(cell, footY, scale, y_lo, y_hi):
    """Horizontal extent of BODY pixels in a horizontal band, in on-screen px from feet.

    Banded deliberately: the weapon and the chain sprawl far outside the body, and a
    whole-cell bbox would call every pair "overlapping" because two chains crossed.
    """
    px = cell.load()
    lo = footY - int(y_hi / scale)
    hi = footY - int(y_lo / scale)
    xs = [x for y in range(max(0, lo), min(cell.height, hi))
          for x in range(cell.width) if px[x, y][3] > 160]
    return (min(xs), max(xs)) if xs else None


def check(a_name, b_name, specs, LOCK_Y=34.0):
    a, b = specs[a_name], specs[b_name]
    ca, ka = guard_cell(a_name)
    cb, kb = guard_cell(b_name)

    # ⛔ THE SHEETS ARE AUTHORED FACING LEFT and the engine mirrors them
    # (`ctx.scale(-p.facing, 1)`), so RAW art faces LEFT and a fighter facing RIGHT is the
    # mirrored one. This had it backwards, which measured the wrong body edges entirely.
    #
    # So: A is raw, faces LEFT, and therefore stands on the RIGHT of the pair. B is mirrored
    # to face RIGHT and stands on the LEFT. Both anchors land on the same world point.
    cb = cb.transpose(Image.FLIP_LEFT_RIGHT)
    b_anchor_x = cb.width - b["lockAnchor"]["x"]

    SC = 3.4
    def on(v, s):
        return v * s * SC

    # torso band: 20-46px above the feet, which brackets the 34px anchor
    sa = body_span(ca, a["footY"], a["scale"], 20, 46)
    sb = body_span(cb, b["footY"], b["scale"], 20, 46)
    # How far short of the shared anchor each body stops, on screen. A faces LEFT so its
    # leading edge is its MINIMUM x; mirrored B faces RIGHT so its leading edge is its
    # MAXIMUM x. Sum them: both stopping short of the anchor is clear space between the
    # fighters, and a negative sum means a body has pushed past the contact point into the
    # other fighter.
    a_short = (sa[0] - a["lockAnchor"]["x"]) * a["scale"]
    b_short = (b_anchor_x - sb[1]) * b["scale"]
    clearance = round(a_short + b_short, 1)   # >0 gap, <0 bodies interpenetrate

    verdict = ("BODIES OVERLAP" if clearance < -2 else
               "TOO FAR APART" if clearance > 26 else "OK")

    # preview
    W, H = 900, 520
    img = Image.new("RGBA", (W, H), (24, 24, 28, 255))
    dr = ImageDraw.Draw(img)
    ground = H - 90
    ia = ca.resize((round(on(ca.width, a["scale"])), round(on(ca.height, a["scale"]))), Image.LANCZOS)
    ib = cb.resize((round(on(cb.width, b["scale"])), round(on(cb.height, b["scale"]))), Image.LANCZOS)
    # both are placed by their ANCHOR landing on the frame's centre line, which is what puts
    # A (facing left) on the right and mirrored B (facing right) on the left, automatically
    img.paste(ia, (W // 2 - round(on(a["lockAnchor"]["x"], a["scale"])),
                   ground - round(on(a["footY"], a["scale"]))), ia)
    img.paste(ib, (W // 2 - round(on(b_anchor_x, b["scale"])),
                   ground - round(on(b["footY"], b["scale"]))), ib)
    dr.line([(0, ground), (W, ground)], fill=(74, 222, 128, 255), width=2)
    ly = ground - round(LOCK_Y * SC)
    dr.line([(0, ly), (W, ly)], fill=(251, 191, 36, 255), width=2)
    dr.ellipse([W // 2 - 8, ly - 8, W // 2 + 8, ly + 8], outline=(248, 113, 113, 255), width=3)
    f_t, f_s = font(20), font(14)
    col = (74, 222, 128, 255) if verdict == "OK" else (248, 113, 113, 255)
    dr.text((20, 16), f"{a_name}  vs  {b_name}", font=f_t, fill=(255, 255, 255, 255))
    dr.text((20, 44), f"clearance {clearance:+.1f}px   ->  {verdict}", font=f_s, fill=col)
    dr.text((20, 64), f"stand-in poses: {ka} / {kb} (lock cells do not exist yet)",
            font=f_s, fill=(148, 163, 184, 255))
    os.makedirs(OUT, exist_ok=True)
    img.save(os.path.join(OUT, f"{a_name}-vs-{b_name}.png"))
    return clearance, verdict


def main():
    # read the anchor out of the spec rather than restating it — a hardcoded caption here
    # went stale the moment the sweep changed the separation
    specs, anchor = load_spec()
    print(f"  anchor: {anchor['yAboveFeet']}px above feet, {anchor['xFromCenter']}px forward "
          f"of centre -> {anchor['xFromCenter'] * 2}px separation\n")
    # count CHECKED pairs, not the whole list — a skipped pair used to be tallied as a
    # pass, so the summary read 5/5 OK while only 4 had actually been measured
    bad = checked = 0
    for a, b in STRESS:
        if a not in specs or b not in specs:
            print(f"  {a} vs {b}: SKIPPED (not in the measured spec)")
            continue
        checked += 1
        clearance, verdict = check(a, b, specs, anchor["yAboveFeet"])
        flag = "" if verdict == "OK" else "   <-- "
        if verdict != "OK":
            bad += 1
        print(f"  {a:12} vs {b:12}  clearance {clearance:+6.1f}px   {verdict}{flag}")
    print(f"\n  {checked - bad}/{checked} pairs OK   previews -> "
          f"{os.path.relpath(OUT, REPO)}/")


if __name__ == "__main__":
    main()
