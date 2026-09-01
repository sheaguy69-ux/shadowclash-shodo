#!/usr/bin/env python3
"""Strip leftover white clipping background from sprite frames -> transparent.

Dimensions are NEVER touched: every pixel written back is the same pixel,
only its alpha changes. Frame offsets / region rects / hitboxes stay valid.

ponytail: ONE guard, and it is the whole tool -- white dies only where it is
CONNECTED to the background (the already-transparent region or the image
border). A blanket "RGB >= 240 -> alpha 0" hollows out Oni's white demon
mask, measured and eyeballed on cell 69: the mask is canon-locked art, not
clipping residue, and it survives here only because black hood pixels seal
it off from the border.

Both alpha tiers of background white go: the solid core (Mokurai's leg
wedge, 4.7k px) AND the semi-alpha halo around it. Clearing the core alone
leaves a chalk-line outline tracing where the wedge was -- worse than the
wedge. Ceiling: 4-connectivity, so white sealed off by a 1px art bridge
survives -- that is what --pockets is for.

--pockets: the SEALED half of the same defect. A pose that closes the gap
(Mokurai's stance, Exile's chain loop, Shin's planted foot) walls the pocket
off from the border, so connectivity can never reach it. There is NO safe
automatic rule for these and four were tried and measured on the live sheets:
ring-brightness flags Ember's and Shin's EYES, ground-band flags Tsubasa's
flame column, pure-255 fraction separates nothing (packing resampled every
blob off exact white, 6-65% across the board), and size/fill flags blade
gleams. All 57 sealed blobs >=200px were therefore rendered at 4-5x and
judged by eye. Everything not cleared is ART -- eyes, katana gleams, slash
cores, Kael's sash, aura and flame cores -- and Exile's hair-adjacent white
was left alone because it could not be told from her silver streaks.

⛔ --pockets TAKES CELLS ON THE COMMAND LINE AND KEEPS NO LIST. It used to
carry the verified indices baked in, and SHEET_V 483 ("delete the dead
cells", 329 of 2354) renumbered every sheet underneath them -- a baked list
survives a repack as a set of confident pointers at whatever art now sits at
those numbers. Re-find the pockets, re-look at them, pass them in.

Usage:
  python3 tools/clean_frame_whitespace.py                 # dry run, web/assets/sprites
  python3 tools/clean_frame_whitespace.py --apply         # write
  python3 tools/clean_frame_whitespace.py --apply PATH..  # other roots
  python3 tools/clean_frame_whitespace.py --pockets mokurai:253,255 [--apply]
  python3 tools/clean_frame_whitespace.py --find-pockets  # ground-band candidates to go LOOK at
"""
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage

FUZZ = 240                       # R,G,B >= FUZZ counts as clipping white
DEFAULT_ROOTS = ["web/assets/sprites"]
SKIP_DIRS = {".claude", "node_modules", ".git"}

POCKET_MIN = 200                 # smaller sealed white is art detail, never residue
GROUND_BAND = 12                 # a wedge bottoms out within this many px of footY


def scan(roots):
    for root in roots:
        if os.path.isfile(root):
            yield root
            continue
        for dirpath, dirnames, files in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for f in sorted(files):
                if f.lower().endswith(".png"):
                    yield os.path.join(dirpath, f)


def _sealed(fighter):
    """-> (arr, sealed-white mask, meta). Sealed = white the border cannot reach."""
    import json
    base = os.path.join("web/assets/sprites", fighter)
    meta = json.load(open(base + ".json"))
    arr = np.array(Image.open(base + ".png").convert("RGBA"))
    a = arr[..., 3]
    white = (arr[..., :3].min(axis=2) >= FUZZ) & (a > 0)
    lab, _ = ndimage.label(white | (a == 0))
    seeds = set(np.unique(lab[a == 0]))
    for edge in (lab[0, :], lab[-1, :], lab[:, 0], lab[:, -1]):
        seeds |= set(np.unique(edge))
    seeds.discard(0)
    return arr, white & ~np.isin(lab, list(seeds)), meta


def find_pockets():
    """Ground-band sealed white = CANDIDATES ONLY. Go and look at each one:
    this band also catches Tsubasa's flame column, which is art."""
    import glob
    hits = 0
    for p in sorted(glob.glob("web/assets/sprites/*.json")):
        if p.endswith("PURGED-KEYS.json"):
            continue   # key tombstones, not a fighter manifest — no png behind it
        f = os.path.basename(p)[:-5]
        arr, sealed, meta = _sealed(f)
        if not sealed.any():
            continue
        fw, footY = meta["frameW"], meta["footY"]
        slab, _ = ndimage.label(sealed)
        for i, sc in enumerate(ndimage.find_objects(slab)):
            sz = int((slab[sc] == (i + 1)).sum())
            if sz < POCKET_MIN or abs(sc[0].stop - 1 - footY) > GROUND_BAND:
                continue
            hits += 1
            print(f"  {f:12} cell {sc[1].start // fw:>4} {sz:>6}px  bottom={sc[0].stop - 1} (footY {footY})")
    print(f"\n{hits} candidate(s) — LOOK at each before passing it to --pockets")
    return hits


def clean_pockets(fighter, cells, apply):
    """Clear SEALED white pockets in the named cells. -> (killed, w, h)."""
    arr, sealed, meta = _sealed(fighter)
    fw = meta["frameW"]
    h, w = arr.shape[:2]

    # only inside the listed cells, and only blobs big enough to be residue
    band = np.zeros(w, bool)
    for c in cells:
        band[c * fw:(c + 1) * fw] = True
    sealed &= band[None, :]
    slab, sn = ndimage.label(sealed)
    kill = np.zeros_like(sealed)
    for i, sc in enumerate(ndimage.find_objects(slab)):
        blob = slab[sc] == (i + 1)
        if blob.sum() >= POCKET_MIN:
            kill[sc] |= blob
    killed = int(kill.sum())

    if apply and killed:
        arr[kill] = (0, 0, 0, 0)
        out = Image.fromarray(arr, "RGBA")
        assert out.size == (w, h), f"{fighter}: canvas changed!"
        out.save(base + ".png")
    return killed, w, h


def clean(path, apply):
    """-> (killed, protected, w, h) or None if the file holds no white."""
    im = Image.open(path)
    mode = im.mode
    arr = np.array(im.convert("RGBA"))
    h, w = arr.shape[:2]
    a = arr[..., 3]
    white = (arr[..., :3].min(axis=2) >= FUZZ) & (a > 0)
    if not white.any():
        return None

    # background = existing transparency, grown through connected white
    lab, n = ndimage.label(white | (a == 0))
    if n == 0:
        return None
    seeds = set(np.unique(lab[a == 0]))
    seeds |= set(np.unique(lab[0, :])) | set(np.unique(lab[-1, :]))
    seeds |= set(np.unique(lab[:, 0])) | set(np.unique(lab[:, -1]))
    seeds.discard(0)
    if not seeds:
        return 0, int(white.sum()), w, h

    kill = white & np.isin(lab, list(seeds))
    killed = int(kill.sum())
    protected = int(white.sum()) - killed

    if apply and killed:
        arr[kill] = (0, 0, 0, 0)
        out = Image.fromarray(arr, "RGBA")
        if mode != "RGBA":
            out = out.convert(mode) if mode == "RGBa" else out
        assert out.size == (w, h), f"{path}: canvas changed!"
        out.save(path)
    return killed, protected, w, h


def selfcheck():
    """The one thing that must never regress: enclosed white art survives."""
    import tempfile
    a = np.zeros((20, 20, 4), np.uint8)
    a[2:18, 2:18] = (10, 10, 10, 255)          # black body, sealed
    a[7:13, 7:13] = (255, 255, 255, 255)       # Oni's mask: white, enclosed
    a[18:20, 8:12] = (255, 255, 255, 255)      # clipping wedge: white, on the border
    a[1, 8:12] = (255, 255, 255, 128)          # halo: white, semi-alpha, on background
    p = os.path.join(tempfile.mkdtemp(), "t.png")
    Image.fromarray(a, "RGBA").save(p)
    killed, protected, w, h = clean(p, apply=True)
    out = np.array(Image.open(p).convert("RGBA"))
    assert (w, h) == (20, 20), "canvas resized"
    assert (out[7:13, 7:13, 3] == 255).all(), "enclosed white ART was deleted"
    assert (out[18:20, 8:12, 3] == 0).all(), "border white wedge survived"
    assert (out[1, 8:12, 3] == 0).all(), "semi-alpha halo survived"
    assert protected == 36 and killed == 12, (killed, protected)
    print("selfcheck OK: mask kept, wedge + halo killed, canvas 20x20")


def main(argv):
    if "--selfcheck" in argv:
        selfcheck()
        return 0
    apply = "--apply" in argv
    if "--find-pockets" in argv:
        find_pockets()
        return 0
    if "--pockets" in argv:
        specs = [a for a in argv if ":" in a and not a.startswith("--")]
        if not specs:
            print("--pockets needs cells, e.g. mokurai:253,255  (no list is kept -- a "
                  "repack renumbers every sheet). Run --find-pockets for candidates.")
            return 2
        tot = 0
        for spec in specs:
            fighter, _, raw = spec.partition(":")
            cells = [int(c) for c in raw.split(",") if c.strip()]
            k, w, h = clean_pockets(fighter, cells, apply)
            tot += k
            print(f"{fighter:12} cells {str(cells):28} {w}x{h}  sealed white -> alpha {k}")
        print(f"\n{tot} px | {'APPLIED' if apply else 'DRY RUN'}")
        return 0
    roots = [a for a in argv if not a.startswith("--")] or DEFAULT_ROOTS
    files = list(scan(roots))
    tk = tp = 0
    touched = 0
    print(f"{'file':44} {'canvas':>13} {'killed':>9} {'protected':>10}")
    for p in files:
        try:
            r = clean(p, apply)
        except Exception as e:                     # never abort the sweep
            print(f"  ERROR {p}: {e}")
            continue
        if r is None:
            continue
        k, prot, w, h = r
        tk += k
        tp += prot
        if k:
            touched += 1
        print(f"{os.path.relpath(p):44} {f'{w}x{h}':>13} {k:>9} {prot:>10}")
    print(f"\naudited {len(files)} png | modified {touched} "
          f"| bg-white -> alpha {tk} | in-art white kept {tp} "
          f"| {'APPLIED' if apply else 'DRY RUN'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
