#!/usr/bin/env python3
"""Build the BLADE LOCK handoff pack — reference art + measured scale spec.

Owner order (Aug 11 2026): the blade-lock cells are authored as STILLS, frame by
frame, not harvested from i2v clips. An outside still-generator does the drawing,
so it needs two things this repo can prove and prose cannot:

  1. REFERENCE ART that is the shipped look, not an intermediate. The refs are cut
     straight out of `web/assets/sprites/<f>.png`, so what the generator matches is
     exactly what the engine already draws.
  2. THE SCALE, MEASURED. Cell-space body height differs per fighter by a factor of
     1.4 (ember 207px, executioner 185px) because every fighter carries a different
     `scale`. "Draw them all the same size" is therefore WRONG, and is the single
     mistake that costs a whole batch. Every number in the spec is measured off the
     alpha bbox of the live idle cell here — nothing is typed by hand.

Outputs (all under docs/handoff/blade-lock/):
    refs/<f>-idle.png      the identity + height anchor
    refs/<f>-guard.png     the closest existing pose to a bind
    refs/<f>-swing.png     mid-swing, shows the weapon extended at full reach
    refs/<f>-spec.png      idle with the foot line, the lock height and the
                           crossing point drawn ON the cell
    scale-reference.png    all lockers on ONE ground line at true relative height
    lock-spec.json         the machine-readable table the doc quotes

Run: python3 tools/sprites/make_lock_handoff.py
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPRITES = os.path.join(REPO, "web", "assets", "sprites")
OUT = os.path.join(REPO, "docs", "handoff", "blade-lock")
REFS = os.path.join(OUT, "refs")

# WHO LOCKS — read off the ENGINE, not off `weapon_type` in the sprite json.
#
# The first pass of this script asked each `<fighter>.json` for `weapon_type` and
# excluded anyone missing it. That silently dropped both bosses, and it was WRONG:
# the roster spec in web/index.html is where a fighter's weapon actually lives, and
# `WEAPON_MAT` in the same file is what the clash predicate reads.
#
#   WEAPON_MAT = { 1:'wood' (mizu), 2:'mail' (shin), 6:'flesh' (buddha), 7:'iron' (oni) }
#   anything unlisted defaults to 'steel'
#   bladeOnBlade() requires isMetal() on BOTH sides, i.e. steel or iron
#
# So the engine's bind-capable set today is everyone EXCEPT buddha (flesh) and shin
# (mail is deliberately not a cutting edge). Exile carries a KUSARIGAMA — a sickle,
# steel by default — and already clashes in the shipped build. Oni's kanabo is 'iron'
# and already rings.
# ONI IS NOT MEASURED HERE, and his old packed cells must not be read at all.
# web/assets/sprites/oni.png still carries the SUPERSEDED pre-redesign oni. The canon
# master is RECOVERY/oni-redesign/NEW-ONI-DESIGN.png (white-maned skull-face, tattered
# bone pelt, PURPLE accents owner-approved) with 59 drawn frames under
# RECOVERY/oni-redesign/frames/. Measuring the old sheet would produce a body height
# and a contact anchor for a character that no longer exists, so he is excluded from
# the measured spec until his redesign sheet is packed. His reference card is built
# from the redesign frames instead (see make_lock_refcards.py).
# EXILE IS OUT (owner, Aug 11 2026): "This is the only true image of exile — if it don't
# look like this it's not usable, it should be deleted." He supplied the canon reference
# (EXILE — LOW SHINOBI RUN CYCLE, 8 frames): black hair with a BOLD WHITE STREAK, bare
# face with TWO RED EYES and red slash markings, black mask, purple scarf tails, tan
# wrapped forearms and shins, kama + spiked chain.
#
# Every cell in web/assets/sprites/exile.png is a DIFFERENT design — measured, not
# guessed, at 4x on the idle and on run_clean1/3/5/7: a tan cloth HEADBAND with red kanji
# covering one eye, a single glowing WHITE eye, muted grey streaks instead of the white
# one, no red facial markings, and an upright stance rather than the low shinobi lean.
# The whole sheet, not just the idle.
#
# So she is deleted from this pack rather than shipped with a warning label. A flagged
# wrong reference is still a wrong reference sitting in a generator's context, and this
# pack exists solely to stop the wrong thing being drawn. Her cells are drawn when her
# true sheet is in the repo, from that sheet, and not before.
# SHIN IS IN as of the per-hitbox material change: his kunai-dash (`2:back`) now declares
# mat:'steel', so it rings and binds while his mail-clad fists correctly still do not. He was
# excluded only because material used to be per-fighter — that was an engine gap, not an art
# problem, and it is closed.
LOCKERS = ["kael", "executioner", "tsubasa", "ember", "mizu", "shin"]

# The three existing cells that brief the pose best.
REF_CELLS = [("idle", ["idle"]),
             ("guard", ["xblkguard", "block"]),
             ("swing", ["heavy_i3", "heavy3", "heavy2"])]

# THE CONTACT ANCHOR, in ON-SCREEN pixels — this is the whole trick.
#
# The blades must meet in WORLD space, so the anchor is defined once on screen and
# converted into each fighter's cell space through that fighter's own `scale`. It is
# NOT a fraction of each fighter's own body height: that would put the crossing at a
# different world height for a short fighter and the blades would miss.
#
# Consequence worth stating out loud, because it looks like a bug and is not: 34px
# is 48% of the executioner's 70.4px but 54% of mizu's 62.4px. A short fighter binds
# HIGHER relative to her own body. That is correct — world height is what matters.
#
# 34px and not the 43.5px that 62%-of-body-height would give: this cast is CHIBI, so
# the head eats the top third and 62% lands at the chin. Measured against the live
# idles, 34px is mid-chest — where these fighters actually hold a weapon. Derive this
# from the art, never from realistic-proportion rules of thumb.
LOCK_Y_ONSCREEN = 34.0   # px above the feet = mid-chest on a 70px chibi fighter
# ⛔ FORWARD IS TO THE LEFT IN CELL SPACE. Every sheet in this game is authored facing LEFT
# and the engine mirrors it — `ctx.scale(-p.facing, 1)`, so facing=1 (right) draws the
# left-facing art flipped. Verified on the art itself, not from the comment: cropping the
# head of every idle cell shows the eye on the LEFT of the head with the scarf/hair
# trailing RIGHT, for all seven measured fighters.
#
# So the contact anchor is SUBTRACTED from the body centre. It used to be added, which put
# it behind the fighter — the weapon would have been drawn on his back.
# 34px — and this number has moved TWICE, both times because the pair pre-flight caught
# bodies interpenetrating that a per-cell art review never could:
#     26 -> kael/executioner overlap 2.8px   (the two widest torsos)
#     30 -> shin/executioner  overlap 2.3px  (found when shin joined the batch)
#     34 -> worst pair +5.6px, loosest +24.5px  <- chosen
#     36 -> loosest pair reaches 28.7px, past the too-far-apart threshold
# Anyone adding a fighter to LOCKERS must re-run tools/sprites/check_lock_pairs.py and
# re-sweep. A new body width can invalidate the anchor, and the failure is invisible until
# two finished fighters are composited.
#
# The spread across pairs (+5.6 to +24.5) is inherent: body widths differ and one global
# constant cannot equalise it. Deriving x per fighter from each torso's leading edge WOULD
# equalise it, but the bind is a lean-forward pose and the only art available to measure is
# the upright idle, so that would be false precision. Revisit once real lock cells exist.
#
# ⛔ LOCK_SEP in web/index.html IS 2x THIS. Change one, change both, re-run the pre-flight.
LOCK_X_ONSCREEN = 34.0   # px forward of body centre; engine separation = 2x this

CELLS = ["lock1", "lock2", "lock3", "lock4", "lock5", "lock6"]

# ⛔ THE SET IS KEYED BY WEAPON, NOT BY FIGHTER (owner, Aug 11 2026): "make this
# mechanic only apply to their attacks with blades... only certain attack frames have
# different blades so we might need different frames for different blade attacks."
#
# Half of this already exists in the engine and half does not:
#   hb.canClash  is PER-HITBOX — "armed melee, not a kick or a bare fist". Per-attack
#                granularity is already there.
#   weaponMat(p) is PER-FIGHTER — WEAPON_MAT[p.spec.id]. So a fighter who swings two
#                different weapons gets ONE material for every attack, and one lock pose.
# That is the gap. Shin punches (mail, no bind) AND throws kunai (steel, should bind);
# exile cuts with the kama (binds) AND swings the chain (must NOT bind edge-to-edge).
# Fixing it means moving material onto the hitbox — `hb.mat`, defaulting to the
# fighter's — which is an engine change, not an art change.
#
# phase 1  the fighter's PRIMARY binding weapon; ships the mechanic
# phase 2  secondary weapons; until these exist the engine falls back to the phase-1
#          set for that fighter, which is approximately right rather than wrong
# blocked  needs something that is not art
LOCK_SETS = [
    ("executioner", "nodachi", 1, "Two-handed nodachi. His only weapon — one set covers him."),
    ("kael", "katana", 1, "The long blade, the bind he leads with."),
    ("kael", "wakizashi", 2, "Off-hand short blade. Niten Ichi-ryū parries with it, so it is a "
                             "genuinely different bind — close in, elbow high, long blade still live."),
    ("tsubasa", "tanto", 1, "Both reverse-grip tantō together. One set — he never binds with just one."),
    ("ember", "claws", 1, "Tekkō-kagi. Not a cross — he TRAPS the opponent's edge in the claws."),
    ("mizu", "bo", 1, "Long wooden bō, hands wide. A lever braced across the body."),
    ("mizu", "hanbo", 2, "Short stick. Much closer bind, one hand, nothing like the bō pose."),
    # phase set to 0 = BLOCKED ON ART, not on an engine change like shin's kunai.
    ("exile", "kama", 0, "BLOCKED — the packed sheet is a superseded design (headband + red "
                         "kanji + one white eye). Her true look is the owner's LOW SHINOBI RUN "
                         "reference: white hair streak, bare face, two red eyes, red slash "
                         "markings. No cells until that sheet is in the repo."),
    ("shin", "kunai", 1, "UNBLOCKED — the KUNAI HE HOLDS (his back+Heavy dash) now declares "
                         "mat:'steel' per-hitbox, so it rings and binds. His FISTS still never "
                         "bind, from his 'mail' fighter default, and his THROWN kunai are "
                         "projectiles that deliberately do not bind — a blade in flight should "
                         "not drag anyone into a held struggle. OLD NOTE, now wrong: "
                         "kunai cannot bind today. Needs per-hitbox material first. His fists "
                         "must never bind."),
    ("oni", "kanabo", 2, "REDESIGNED ONI ONLY — canon is RECOVERY/oni-redesign/, never the old "
                         "packed cells. Iron kanabo, binds and rings. The club scales 1.0x->2.0-2.5x "
                         "on a strike, so the bind pose must show it PROJECTING, not at idle size. "
                         "Waiting on his sheet being packed, not on a design decision."),
    ("oni", "fist", 0, "NEVER BINDS. His claw/fist form is 'flesh' in the engine (fistMode), so it "
                       "has no steel to meet an edge. Two forms, two behaviours — this is the "
                       "clearest case in the roster for material living on the hitbox, not the "
                       "fighter. Whether the CLAWS should bind is an owner ruling, not an "
                       "assumption to make here."),
]
BEATS = [
    ("lock1", "BIND — impact", "Weapons have just caught. Weight pitched forward over the front foot, "
                               "both arms braced, head up. The frame of the catch, not the swing before it."),
    ("lock2", "BIND — settle", "The catch absorbs. Elbows compress a little, rear foot digs, shoulders drop. "
                               "Body height must NOT change from lock1."),
    ("lock3", "STRAIN — a", "The held push. Deep lean, both hands committed, whole body a straight line "
                            "from rear heel to the weapon."),
    ("lock4", "STRAIN — b", "Same stance, the tremble: a few px of shift in the shoulders and blade only. "
                            "lock3+lock4 loop for as long as the struggle lasts, so they must read as ONE "
                            "pose breathing, never as two poses."),
    ("lock5", "WIN — push through", "Shoves the bind open. Front foot steps THROUGH, weapon drives forward "
                                    "and up past the crossing point, chest open, full extension."),
    ("lock6", "LOSE — thrown off", "Loses the bind. Torso rocks back, weapon knocked wide off the centre "
                                   "line, guard broken open, back foot catching the weight. Off balance but "
                                   "still on both feet — this is not a knockdown."),
]


def load(f):
    with open(os.path.join(SPRITES, f + ".json")) as fh:
        d = json.load(fh)
    sheet = Image.open(os.path.join(SPRITES, f + ".png")).convert("RGBA")
    return d, sheet


def cell(d, sheet, idx):
    fw, fh = d["frameW"], d["frameH"]
    return sheet.crop((idx * fw, 0, idx * fw + fw, fh))


def pick(frames, names):
    for n in names:
        if n in frames:
            return n, frames[n]
    raise KeyError(names)


def font(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/System/Library/Fonts/Helvetica.ttc"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def measure(f):
    """Everything the generator must be told about one fighter, measured live."""
    d, sheet = load(f)
    fw, fh, footY, scale = d["frameW"], d["frameH"], d["footY"], d["scale"]
    iname, iidx = pick(d["frames"], ["idle"])
    bb = cell(d, sheet, iidx).getbbox()
    x0, y0, x1, y1 = bb
    bodyH = y1 - y0
    centerX = (x0 + x1) // 2
    # on-screen anchor -> this fighter's cell space, through its own scale
    lockY = round(footY - LOCK_Y_ONSCREEN / scale)
    lockX = round(centerX - LOCK_X_ONSCREEN / scale)   # MINUS: forward is LEFT (see above)
    return {
        "fighter": f, "frameW": fw, "frameH": fh, "footY": footY, "scale": scale,
        "weapon_type": d.get("weapon_type", "?"),
        "discipline": d.get("martial_art_discipline", "?"),
        "idleFrame": iidx, "idleBodyH": bodyH, "idleHeadY": y0, "idleCenterX": centerX,
        "onscreenH": round(bodyH * scale, 1),
        "lockAnchor": {"x": lockX, "y": lockY},
        "nextFreeCell": d["cols"],
        "newCells": {c: d["cols"] + i for i, c in enumerate(CELLS)},
    }


def spec_card(f, m):
    """The idle cell with the foot line, lock height and crossing point drawn on it.

    A number in a table is arguable; a crosshair on the art is not.
    """
    d, sheet = load(f)
    im = cell(d, sheet, m["idleFrame"]).copy()
    # dark mat so the guides read over a transparent/black character
    card = Image.new("RGBA", (im.width + 260, im.height + 70), (24, 24, 28, 255))
    card.paste(im, (0, 40), im)
    dr = ImageDraw.Draw(card)
    fs, fb = font(13), font(16)
    ox, oy = 0, 40
    fy, lx, ly = m["footY"] + oy, m["lockAnchor"]["x"] + ox, m["lockAnchor"]["y"] + oy
    hy = m["idleHeadY"] + oy
    # foot line (green), head line (grey), lock height (amber), crossing point (red)
    dr.line([(0, fy), (im.width, fy)], fill=(74, 222, 128, 255), width=2)
    dr.line([(0, hy), (im.width, hy)], fill=(148, 163, 184, 200), width=1)
    dr.line([(0, ly), (im.width, ly)], fill=(251, 191, 36, 255), width=2)
    dr.line([(m["idleCenterX"], oy), (m["idleCenterX"], fy)], fill=(148, 163, 184, 120), width=1)
    r = 7
    dr.ellipse([lx - r, ly - r, lx + r, ly + r], outline=(248, 113, 113, 255), width=3)
    dr.line([(lx - 14, ly), (lx + 14, ly)], fill=(248, 113, 113, 255), width=1)
    dr.line([(lx, ly - 14), (lx, ly + 14)], fill=(248, 113, 113, 255), width=1)
    dr.text((6, 8), f"{f.upper()}  —  cell {m['frameW']}x{m['frameH']}", font=fb, fill=(255, 255, 255, 255))
    tx = im.width + 10
    lines = [
        ("BODY HEIGHT", f"{m['idleBodyH']} px in-cell", (74, 222, 128, 255)),
        ("", f"= {m['onscreenH']} px on screen", (148, 163, 184, 255)),
        ("FEET (footY)", f"y = {m['footY']}", (74, 222, 128, 255)),
        ("HEAD TOP", f"y = {m['idleHeadY']}", (148, 163, 184, 255)),
        ("LOCK HEIGHT", f"y = {m['lockAnchor']['y']}", (251, 191, 36, 255)),
        ("CROSSING", f"x = {m['lockAnchor']['x']}", (248, 113, 113, 255)),
        ("", f"scale {m['scale']}", (148, 163, 184, 255)),
    ]
    y = 46
    for lab, val, col in lines:
        if lab:
            dr.text((tx, y), lab, font=fs, fill=col)
            y += 15
        dr.text((tx + 8, y), val, font=fs, fill=(226, 232, 240, 255))
        y += 20
    card.save(os.path.join(REFS, f"{f}-spec.png"))


def scale_reference(specs):
    """All lockers on ONE ground line at TRUE relative on-screen height.

    Each idle is scaled by its own `scale` and then by a common factor, so the
    heights on this image are the heights the engine draws. This is the picture
    that stops "make them all the same size".
    """
    K = 3.4  # common blow-up so 70px fighters render legibly
    pad, gap, base = 30, 26, 60
    tiles = []
    for m in specs:
        d, sheet = load(m["fighter"])
        im = cell(d, sheet, m["idleFrame"])
        bb = im.getbbox()
        im = im.crop(bb)
        w = max(1, round(im.width * m["scale"] * K))
        h = max(1, round(im.height * m["scale"] * K))
        tiles.append((m, im.resize((w, h), Image.LANCZOS), h))
    W = pad * 2 + sum(t[1].width for t in tiles) + gap * (len(tiles) - 1)
    H = base + max(t[2] for t in tiles) + 96
    card = Image.new("RGBA", (W, H), (24, 24, 28, 255))
    dr = ImageDraw.Draw(card)
    ground = H - 74
    dr.line([(0, ground), (W, ground)], fill=(74, 222, 128, 255), width=2)
    # the shared lock height, drawn once across every fighter
    ly = ground - round(LOCK_Y_ONSCREEN * K)
    dr.line([(0, ly), (W, ly)], fill=(251, 191, 36, 255), width=2)
    fs, fb, ft = font(15), font(20), font(12)
    dr.text((pad, 16), "SHADOW CLASH — TRUE RELATIVE HEIGHT (measured off the live sheets)",
            font=fb, fill=(255, 255, 255, 255))
    dr.text((pad, 40), "green = ground · amber = the blade-lock height, SHARED by everyone",
            font=ft, fill=(148, 163, 184, 255))
    x = pad
    for m, im, h in tiles:
        card.paste(im, (x, ground - h), im)
        cx = x + im.width // 2
        lab = f"{m['fighter']}  {m['onscreenH']}px"
        tw = dr.textlength(lab, font=fs)
        dr.text((cx - tw / 2, ground + 10), lab, font=fs, fill=(226, 232, 240, 255))
        sub = f"{m['idleBodyH']}px in-cell"
        tw = dr.textlength(sub, font=ft)
        dr.text((cx - tw / 2, ground + 30), sub, font=ft, fill=(148, 163, 184, 255))
        # the crossing point, at true on-screen offset from this fighter's centre
        lx = cx + round(LOCK_X_ONSCREEN * K)
        dr.ellipse([lx - 5, ly - 5, lx + 5, ly + 5], outline=(248, 113, 113, 255), width=2)
        x += im.width + gap
    card.save(os.path.join(OUT, "scale-reference.png"))


def main():
    os.makedirs(REFS, exist_ok=True)
    specs = []
    for f in LOCKERS:
        d, sheet = load(f)
        m = measure(f)
        specs.append(m)
        for tag, names in REF_CELLS:
            name, idx = pick(d["frames"], names)
            cell(d, sheet, idx).save(os.path.join(REFS, f"{f}-{tag}.png"))
            m.setdefault("refCells", {})[tag] = {"frame": name, "index": idx}
        spec_card(f, m)
        print(f"  {f:12} body {m['idleBodyH']:4}px in-cell = {m['onscreenH']:5}px on screen"
              f"   anchor ({m['lockAnchor']['x']},{m['lockAnchor']['y']})"
              f"   new cells {m['nextFreeCell']}..{m['nextFreeCell'] + len(CELLS) - 1}")
    scale_reference(specs)
    with open(os.path.join(OUT, "lock-spec.json"), "w") as fh:
        json.dump({
            "generated_by": "tools/sprites/make_lock_handoff.py",
            "anchor_onscreen": {"yAboveFeet": LOCK_Y_ONSCREEN, "xFromCenter": LOCK_X_ONSCREEN},
            "cells": CELLS,
            "beats": [{"cell": c, "name": n, "direction": t} for c, n, t in BEATS],
            "lockSets": [{"fighter": f, "weapon": w, "phase": p, "note": n,
                          "cells": [f"{f}-{w}-{c}" for c in CELLS]}
                         for f, w, p, n in LOCK_SETS],
            "fighters": specs,
        }, fh, indent=2)
    print(f"\n  pack -> {os.path.relpath(OUT, REPO)}/")


if __name__ == "__main__":
    main()
