#!/usr/bin/env python3
"""Labelled WHO-IS-WHO cards for the blade-lock handoff.

The spec cards (make_lock_handoff.py) carry the geometry. These carry the IDENTITY:
name and weapon burned onto the art, so an outside generator cannot mix up which
fighter it is drawing or hand someone the wrong weapon.

Outputs (docs/handoff/blade-lock/):
    roster-labelled.png     all five lockers, named, at true relative height, plus a
                            DO-NOT-DRAW strip for the four who are out of this batch
    refs/<f>-card.png       one fighter: name, weapon, discipline, three poses
                            (idle / guard / swing) at native cell size, key numbers

Run: python3 tools/sprites/make_lock_refcards.py   (after make_lock_handoff.py)
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPRITES = os.path.join(REPO, "web", "assets", "sprites")
OUT = os.path.join(REPO, "docs", "handoff", "blade-lock")
REFS = os.path.join(OUT, "refs")

BG = (24, 24, 28, 255)
PANEL = (34, 34, 40, 255)
WHITE = (255, 255, 255, 255)
DIM = (148, 163, 184, 255)
TEXT = (226, 232, 240, 255)
GREEN = (74, 222, 128, 255)
AMBER = (251, 191, 36, 255)
RED = (248, 113, 113, 255)

# One line per fighter that names the weapon the way the generator must draw it —
# the part most likely to go wrong (tsubasa flipped to a forward grip, ember given
# a sword, mizu's staff turned into a spear).
WEAPON_NOTE = {
    "kael": "TWO blades: long katana + short wakizashi/tanto. Binds with the LONG one; "
            "the off-hand blade stays live.",
    "executioner": "ONE huge nodachi, held in TWO hands. Binds with his weight, not his arms.",
    "tsubasa": "TWO tanto knives, REVERSE GRIP (blade back along the forearm). Never a "
               "forward grip. Short blades, so the bind is close in.",
    "ember": "IRON CLAWS (tekko-kagi), NOT a sword. He CATCHES the opponent's edge in the "
             "claws. Match the claw count to the art exactly.",
    "shin": "The KUNAI HE HOLDS (back+Heavy dash) — a short steel blade, so the bind is very "
            "close in. NOT his fists, which are chainmail and never bind, and NOT a thrown "
            "kunai. One blade, held.",
    "mizu": "ONE long WOODEN bo staff, both hands wide apart on the shaft. A lever braced "
            "across the body, not an edge-to-edge cross.",
    "exile": "KUSARIGAMA — a steel SICKLE on a chain. The sickle HOOKS an edge and holds it. "
             "Her chain and weight attacks never bind: a chain has no edge to catch.",
    "oni": "ONI THE FOUNDER — owner's FINAL design (Aug 11 2026). White skull mask with three "
           "claw gouges, RED eyes, two dark horns, black hood and tattered mantle, ash-gray worn "
           "plate, cloth wrappings on BOTH hands, RIGHT-HAND CLAW ONLY (left hand wrapped, "
           "clawless), two swords crossed on his back. NO mane, NO bone pelt, NO PURPLE.",
}

# Out of this batch. Shown so nobody draws them by mistake, with the reason.
EXCLUDED = [
    ("exile", "Repo art is a SUPERSEDED design — headband with red kanji over one eye, one "
              "glowing white eye. CANON is the owner's LOW SHINOBI RUN sheet: bare face, TWO "
              "RED EYES, red slash markings, BOLD WHITE hair streak. Full spec in "
              "refs/OWNER-DESIGNS-README.md. Draw her ONLY from the owner's sheet."),
    ("buddha", "Bare hands and prayer beads — 'flesh' never clashes at all."),
    ("oni", "CANON is the owner's ONI THE FOUNDER sheet — white skull mask, RED eyes, "
            "RIGHT-HAND CLAW ONLY, two swords on his back. Repo art is superseded twice over "
            "(the packed sheet is pre-redesign; RECOVERY/oni-redesign is the purple/white-maned "
            "lane — a DIFFERENT character). Full spec in refs/OWNER-DESIGNS-README.md. Still "
            "blocked on two owner rulings: his one-handed claw versus this engine's sprite "
            "mirroring, and whether the kanabo survives."),
]

# Oni is measured with the binders (his kanabo is metal) but must not be DRAWN yet, so
# he is shown in the do-not-draw strip instead of the named row.
ROSTER_ROW = ["kael", "executioner", "tsubasa", "ember", "mizu", "shin"]

# ⛔ THE OWNER'S CANON SHEETS FOR EXILE AND ONI. Both were pulled from the batch because
# every image of them IN THIS REPO is a superseded design. The owner has since supplied the
# correct design for each, but as chat attachments — they are not on disk, and an
# attachment is not a file this script can open.
#
# So the slot is built and waiting: drop either file at the path below and it is picked up
# automatically, no code change. Until then the roster shows the fighter as PENDING with
# the reason, which is the honest state — better than an empty gap that reads as "forgot".
# Their canon is written out in full in refs/OWNER-DESIGNS-README.md so nothing depends on
# remembering this conversation.
OWNER_SHEETS = {
    "exile": ("OWNER-exile-run-cycle.png",
              "LOW SHINOBI RUN CYCLE — white hair streak, bare face, TWO RED EYES, red "
              "slash markings, purple scarf tails, tan wraps, sickle + spiked chain"),
    "oni":   ("OWNER-oni-founder-sheet.png",
              "ONI THE FOUNDER — white skull mask w/ three gouges, RED eyes, two horns, "
              "black hood + mantle, ash-gray plate, RIGHT-HAND CLAW ONLY, two swords on back"),
}


def owner_sheet(name):
    """The owner's canon sheet if it is on disk, else None. Never falls back to repo art —
    falling back is exactly how the superseded designs got shipped twice."""
    fn, _ = OWNER_SHEETS[name]
    path = os.path.join(REFS, fn)
    return Image.open(path).convert("RGBA") if os.path.exists(path) else None

# `weapon_type` is missing from the two bosses' sprite json — the roster spec in
# web/index.html is the real source. Fall back to it rather than printing "?".
# Shin's sprite json says "Unarmed & Shuriken", which is true of him overall and WRONG for
# this set: the lock is the kunai he HOLDS, not his fists and not a thrown shuriken. Naming
# the wrong weapon on the card is the single most likely way a generator draws the wrong
# thing, so the label is overridden here.
WEAPON_LABEL = {"exile": "Kusarigama (Sickle & Chain)", "oni": "Growing Kanabo (Iron Club)",
                "shin": "Kunai (held, not thrown)"}

# ⛔ ONI GETS NO CARD. It used to be built from RECOVERY/oni-redesign/frames/, but the
# owner's FINAL "Oni the Founder" design (Aug 11 2026) supersedes those frames: they are the
# white-maned, bone-pelt, PURPLE oni and the final design has none of that. Building his card
# from them would hand a generator a different character — the same mistake exile's card made,
# and it is not repeated here. He returns when the final design is in the repo.

# ⛔ NOTHING IN THIS REPO IS EXILE'S CANON LOOK. Three sources, all wrong:
#   RECOVERY/select-portrait-handoff/refs/exile-*.png  pre-repack, 74.1% / 32.6% baked
#                                                      white manga panels
#   web/assets/sprites/exile.png                       0.0% panels but a SUPERSEDED face
#                                                      design (headband + red kanji + one
#                                                      white eye) in every cell
#   her card in this pack                              deleted, for that reason
# Canon is the owner's LOW SHINOBI RUN reference, which is not in the repo yet. She is
# excluded until it is, and drawn from it rather than from any of the above.

REF_TAGS = [("idle", "IDLE — seed for lock1", ["idle"]),
            ("guard", "GUARD — closest to a bind", ["xblkguard", "block"]),
            ("swing", "SWING — weapon at reach", ["heavy_i3", "heavy3", "heavy2"])]


def font(size, bold=True):
    names = (["DejaVuSans-Bold.ttf", "DejaVuSans.ttf"] if bold else ["DejaVuSans.ttf"])
    for n in names:
        p = f"/usr/share/fonts/truetype/dejavu/{n}"
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def load(f):
    with open(os.path.join(SPRITES, f + ".json")) as fh:
        d = json.load(fh)
    return d, Image.open(os.path.join(SPRITES, f + ".png")).convert("RGBA")


def cell(d, sheet, idx):
    fw, fh = d["frameW"], d["frameH"]
    return sheet.crop((idx * fw, 0, idx * fw + fw, fh))


def pick(frames, names):
    for n in names:
        if n in frames:
            return n, frames[n]
    raise KeyError(names)


def wrap(dr, text, fnt, width):
    out, line = [], ""
    for word in text.split():
        t = (line + " " + word).strip()
        if dr.textlength(t, font=fnt) <= width:
            line = t
        else:
            out.append(line)
            line = word
    if line:
        out.append(line)
    return out



def card(f, spec):
    """One fighter, named, with the three reference poses at native cell size."""
    d, sheet = load(f)
    poses = []
    for tag, label, names in REF_TAGS:
        name, idx = pick(d["frames"], names)
        im = cell(d, sheet, idx)
        poses.append((label, name, im))

    pad, gap = 26, 20
    strip_w = sum(p[2].width for p in poses) + gap * (len(poses) - 1)
    strip_h = max(p[2].height for p in poses)
    W = pad * 2 + max(strip_w, 900)
    head_h = 132
    W = int(W)
    card = Image.new("RGBA", (W, head_h + strip_h + 104), BG)
    dr = ImageDraw.Draw(card)
    f_name, f_wep, f_lab, f_sm = font(46), font(19), font(15), font(14, False)

    dr.rectangle([0, 0, W, head_h - 12], fill=PANEL)
    dr.text((pad, 18), f.upper(), font=f_name, fill=WHITE)
    nw = dr.textlength(f.upper(), font=f_name)
    dr.text((pad + nw + 18, 40), WEAPON_LABEL.get(f) or d.get("weapon_type", "?"),
            font=f_wep, fill=AMBER)
    for i, line in enumerate(wrap(dr, WEAPON_NOTE[f], f_sm, W - pad * 2)):
        dr.text((pad, 78 + i * 19), line, font=f_sm, fill=TEXT)

    x = pad
    y = head_h
    for label, frame_name, im in poses:
        card.paste(im, (x, y), im)
        # foot line on every pose so the ground is unambiguous
        dr.line([(x, y + d["footY"]), (x + im.width, y + d["footY"])], fill=GREEN, width=2)
        dr.text((x, y + strip_h + 8), label, font=f_lab, fill=WHITE)
        dr.text((x, y + strip_h + 28), f"cell {im.width}x{im.height} · frame '{frame_name}'",
                font=f_sm, fill=DIM)
        x += im.width + gap

    foot = (f"body {spec['idleBodyH']}px in-cell = {spec['onscreenH']}px on screen   ·   "
            f"feet y={spec['footY']}   ·   weapons meet at x={spec['lockAnchor']['x']}, "
            f"y={spec['lockAnchor']['y']}   ·   scale {spec['scale']}")
    dr.text((pad, card.height - 26), foot, font=f_sm, fill=DIM)
    card.save(os.path.join(REFS, f"{f}-card.png"))


def roster(specs):
    """All five lockers named, at true relative height, plus the excluded four."""
    K = 3.9
    pad, gap = 34, 40
    tiles = []
    for m in [s for k in ROSTER_ROW for s in specs if s["fighter"] == k]:
        d, sheet = load(m["fighter"])
        im = cell(d, sheet, m["idleFrame"])
        im = im.crop(im.getbbox())
        w = max(1, round(im.width * m["scale"] * K))
        h = max(1, round(im.height * m["scale"] * K))
        tiles.append((m, im.resize((w, h), Image.LANCZOS)))

    ex = []
    for name, why in EXCLUDED:
        if name in OWNER_SHEETS:
            im = owner_sheet(name)
            if im is not None:
                # the owner's canon art IS available — show it as the reference it is
                bb = im.getbbox()
            else:
                fn, desc = OWNER_SHEETS[name]
                im = Image.new("RGBA", (150, 120), (44, 44, 52, 255))
                _d = ImageDraw.Draw(im)
                _d.rectangle([0, 0, 149, 119], outline=AMBER, width=2)
                _d.text((8, 8), "PENDING", font=font(14), fill=AMBER)
                for _i, _ln in enumerate(wrap(_d, "owner's sheet not in repo: " + fn,
                                              font(10), 134)):
                    _d.text((8, 30 + _i * 13), _ln, font=font(10), fill=DIM)
                bb = None
        elif name == "oni":
            # NO ART AT ALL for oni — deliberately. Both candidates are wrong: the packed
            # sheet is the pre-redesign oni and the RECOVERY frames are the purple/white-maned
            # lane, and the owner's final design is not in the repo. A wrong picture in a
            # DO-NOT-DRAW strip is still a picture a generator can copy, so he gets an empty
            # plate that says so instead.
            im = Image.new("RGBA", (110, 120), (44, 44, 52, 255))
            _d = ImageDraw.Draw(im)
            _d.rectangle([0, 0, 109, 119], outline=RED, width=2)
            for _i, _ln in enumerate(["NO", "CANON", "ART", "IN REPO"]):
                _d.text((10, 24 + _i * 18), _ln, font=font(13), fill=RED)
            bb = None
        else:
            d, sheet = load(name)
            idx = d["frames"].get("idle", 0)
            im = cell(d, sheet, idx)
            bb = im.getbbox()
        im = im.crop(bb) if bb else im
        h = 120
        w = max(1, round(im.width * h / im.height))
        ex.append((name, why, im.resize((w, h), Image.LANCZOS)))

    body_w = sum(t[1].width for t in tiles) + gap * (len(tiles) - 1)
    ex_w = 250 * len(ex)
    W = pad * 2 + max(body_w, ex_w, 1000)
    top = 96
    tall = max(t[1].height for t in tiles)
    ground = top + tall
    ex_top = ground + 118
    # MEASURE the tallest wrapped caption instead of reserving a fixed 150px. The
    # do-not-draw reasons got long enough to run off the bottom of the card, and a
    # truncated reason is worse than no reason — it reads as an unexplained exclusion.
    _probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    _cap_lines = max(len(wrap(_probe, why, font(13, False), 230)) for _, why, _ in ex) if ex else 0
    H = ex_top + 120 + 46 + _cap_lines * 17
    card = Image.new("RGBA", (W, H), BG)
    dr = ImageDraw.Draw(card)
    f_t, f_n, f_w, f_s = font(26), font(21), font(14), font(13, False)

    dr.text((pad, 22), "SHADOW CLASH — WHO BINDS BLADES", font=f_t, fill=WHITE)
    dr.text((pad, 56), "Named, at TRUE relative height. Green = ground. "
                       "Amber = the height where weapons meet, shared by everyone.",
            font=f_s, fill=DIM)

    dr.line([(0, ground), (W, ground)], fill=GREEN, width=2)
    ly = ground - round(34.0 * K)
    dr.line([(0, ly), (W, ly)], fill=AMBER, width=2)

    x = pad
    for m, im in tiles:
        card.paste(im, (x, ground - im.height), im)
        cx = x + im.width // 2
        name = m["fighter"].upper()
        tw = dr.textlength(name, font=f_n)
        dr.text((cx - tw / 2, ground + 12), name, font=f_n, fill=WHITE)
        sub = f"{m['onscreenH']}px tall"
        tw = dr.textlength(sub, font=f_w)
        dr.text((cx - tw / 2, ground + 40), sub, font=f_w, fill=AMBER)
        wep = WEAPON_LABEL.get(m["fighter"]) or m["weapon_type"].split("/")[0].strip()
        for i, line in enumerate(wrap(dr, wep, f_s, im.width + 34)):
            tw = dr.textlength(line, font=f_s)
            dr.text((cx - tw / 2, ground + 60 + i * 17), line, font=f_s, fill=TEXT)
        lx = cx + round(26.0 * K)
        dr.ellipse([lx - 6, ly - 6, lx + 6, ly + 6], outline=RED, width=2)
        x += im.width + gap

    dr.line([(pad, ex_top - 30), (W - pad, ex_top - 30)], fill=(60, 60, 68, 255), width=1)
    dr.text((pad, ex_top - 22), "DO NOT DRAW — not in this batch", font=f_n, fill=RED)
    # Fixed column pitch, and the reason wrapped INSIDE its column — free-flowing
    # captions under variable-width thumbnails overlap each other into mush.
    COL = 250
    x = pad
    for name, why, im in ex:
        faded = Image.new("RGBA", im.size, (0, 0, 0, 0))
        faded = Image.blend(faded, im, 0.34)
        cx = x + COL // 2
        card.paste(faded, (cx - im.width // 2, ex_top + 12), faded)
        tw = dr.textlength(name.upper(), font=f_w)
        dr.text((cx - tw / 2, ex_top + 138), name.upper(), font=f_w, fill=DIM)
        for i, line in enumerate(wrap(dr, why, f_s, COL - 20)):
            tw = dr.textlength(line, font=f_s)
            dr.text((cx - tw / 2, ex_top + 158 + i * 17), line, font=f_s, fill=(120, 130, 145, 255))
        x += COL
    card.save(os.path.join(OUT, "roster-labelled.png"))


def main():
    with open(os.path.join(OUT, "lock-spec.json")) as fh:
        specs = json.load(fh)["fighters"]
    for m in specs:
        card(m["fighter"], m)
        print(f"  refs/{m['fighter']}-card.png")
    roster(specs)
    print("  roster-labelled.png")


if __name__ == "__main__":
    main()
