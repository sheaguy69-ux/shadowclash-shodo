#!/usr/bin/env python3
"""Objective floater/hallucination detector for sprite candidate frames.

For each white-bg, single-character PNG: threshold non-white ink, label
8-connected components (pure numpy row-run union-find, no scipy), the
largest component is the character. Any other component >0.05% of image
area that is NOT within GAP_PCT of the character's silhouette (measured as
"does it fall inside the character's mask dilated by GAP_PCT of its own
bbox diagonal") is a FLOATER — a disconnected object (hallucinated
shuriken, duplicate limb, stray blob) the model invented.

NOTE ON THE SPEC'S "bbox touches bbox+2%" WORDING: a plain rectangle-vs-
rectangle check does not work on these sprites — capes/staffs/kicks make
the character's own bounding box span almost the full canvas, so a
same-rectangle floater (e.g. the Mizu shuriken bug this tool exists to
catch) would always trivially "touch" it. Verified against real data
(media/polished-candidates/mizu/raw/attack_body5.png: known floater
shuriken bbox nests entirely inside the body bbox, true nearest-pixel gap
measured at ~29.5px vs a 2%-of-diagonal threshold of ~26px). So attachment
is measured against the character's actual silhouette (dilated by the gap
threshold), not its bounding rectangle.

Usage:
    python3 tools/sprites/detect_floaters.py <raw-dir> [<raw-dir> ...]
    python3 tools/sprites/detect_floaters.py media/polished-candidates/{executioner,mizu,shin}/raw

Character name (for the Shin tolerance rule) is inferred from the raw
dir's parent folder name.
"""
import os
import sys
import time

import numpy as np
from PIL import Image

WHITE_THRESHOLD = 240              # channel value below this counts as "ink"
MIN_AREA_PCT = 0.05                # component must exceed this % of image area to matter
DEFAULT_GAP_PCT = 2.0              # % of character-bbox diagonal treated as "attached"
# Spec'd "simple approach" for Shin was a blanket 12% tolerance (his hand-held shuriken
# is canon per owner ruling, don't flag it). Verified against the real raw/ set first:
# in every sampled frame the shuriken is either literally touching the fist (merged into
# the main component, 0px gap, never reaches this check) or separated by <=21.5px (well
# inside the 2% default of ~20-26px for these frames) -- 12% is NOT needed to clear it.
# Applying the wider 12% anyway MASKS a real, pervasive bug: ~30/32 Shin raw frames carry
# a large (2-4.5% of image) duplicate-character fragment bled in near the top-left corner,
# at gaps of 35-105px -- comfortably caught by 2%, silently swallowed by 12%. So Shin gets
# no special-cased tolerance; verify before widening this again if a real frame needs it.
SHIN_GAP_PCT = DEFAULT_GAP_PCT
EDGE_MARGIN_PX = 2                 # within this many px of canvas border = "touching edge"
SKIP_IF_MODIFIED_WITHIN_SEC = 60   # frame may still be mid-generation, skip it


def connected_components(mask):
    """8-connected labeling via row-run union-find. Pure numpy/python, no scipy."""
    h, w = mask.shape
    labels = np.zeros((h, w), dtype=np.int32)
    parent = [0]

    def find(x):
        r = x
        while parent[r] != r:
            r = parent[r]
        while parent[x] != r:
            parent[x], x = r, parent[x]
        return r

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            if ra < rb:
                parent[rb] = ra
            else:
                parent[ra] = rb

    next_label = 1
    prev_runs = []
    for y in range(h):
        row = mask[y]
        if not row.any():
            prev_runs = []
            continue
        d = np.diff(row.astype(np.int8))
        starts = list(np.where(d == 1)[0] + 1)
        if row[0]:
            starts = [0] + starts
        ends = list(np.where(d == -1)[0] + 1)
        if row[-1]:
            ends = ends + [w]
        cur_runs = []
        for s, e in zip(starts, ends):
            lbl = next_label
            next_label += 1
            parent.append(lbl)
            labels[y, s:e] = lbl
            for ps, pe, plbl in prev_runs:
                if s <= pe and ps <= e:   # 8-connected: touching (incl. diagonally) counts
                    union(lbl, plbl)
            cur_runs.append((s, e, lbl))
        prev_runs = cur_runs

    remap = np.zeros(next_label, dtype=np.int32)
    roots = {}
    nxt = 1
    for lbl in range(1, next_label):
        r = find(lbl)
        if r not in roots:
            roots[r] = nxt
            nxt += 1
        remap[lbl] = roots[r]
    out = np.zeros((h, w), dtype=np.int32)
    fg = labels > 0
    out[fg] = remap[labels[fg]]
    return out, nxt - 1


def bbox(ys, xs):
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def _boundary(mask2d):
    """Pixels that are True but have >=1 False 4-neighbor (nearest-point search
    only ever needs the boundary of a solid blob, cuts point count 10-50x)."""
    e = mask2d.copy()
    e[1:, :] &= mask2d[:-1, :]
    e[:-1, :] &= mask2d[1:, :]
    e[:, 1:] &= mask2d[:, :-1]
    e[:, :-1] &= mask2d[:, 1:]
    return mask2d & ~e


def _sample_points(mask2d, cap):
    ys, xs = np.where(mask2d)
    if len(ys) == 0:
        return ys, xs
    if len(ys) > cap:
        idx = np.linspace(0, len(ys) - 1, cap).astype(int)
        ys, xs = ys[idx], xs[idx]
    return ys, xs


def gap_distance(comp_mask, main_mask, comp_bbox, h, w, search_margin, cap=600):
    """True nearest-pixel Euclidean distance from `comp_mask` to `main_mask`,
    cropped to `comp_bbox` expanded by `search_margin` (so cost is independent
    of image size / threshold magnitude), boundary-only + point-capped for
    speed. If no main-mask pixel falls within the crop the gap is, by
    construction, > search_margin (returned as inf) — a plain chessboard/
    Chebyshev dilation was tried first but it systematically UNDER-measures
    diagonal gaps (Chebyshev <= Euclidean), which silently missed the exact
    Mizu-shuriken bug this tool exists to catch; this measures real distance
    instead."""
    cx0, cy0, cx1, cy1 = comp_bbox
    x0, x1 = max(0, cx0 - search_margin), min(w, cx1 + search_margin + 1)
    y0, y1 = max(0, cy0 - search_margin), min(h, cy1 + search_margin + 1)
    mcrop = main_mask[y0:y1, x0:x1]
    if not mcrop.any():
        return float("inf")
    fcrop = comp_mask[y0:y1, x0:x1]
    mys, mxs = _sample_points(_boundary(mcrop), cap)
    if len(mys) == 0:
        mys, mxs = _sample_points(mcrop, cap)
    fys, fxs = _sample_points(_boundary(fcrop), cap)
    if len(fys) == 0:
        fys, fxs = _sample_points(fcrop, cap)
    fpts = np.stack([fys, fxs], axis=1).astype(np.float64)
    mpts = np.stack([mys, mxs], axis=1).astype(np.float64)
    d2 = ((fpts[:, None, :] - mpts[None, :, :]) ** 2).sum(-1)
    return float(np.sqrt(d2.min()))


def analyze_frame(path, character):
    img = Image.open(path).convert("RGB")
    arr = np.array(img)
    h, w = arr.shape[:2]
    mask = np.any(arr < WHITE_THRESHOLD, axis=2)
    if not mask.any():
        return {"verdict": "CLEAN", "note": "empty frame (no ink pixels)"}

    labels, n = connected_components(mask)
    sizes = np.bincount(labels.ravel())
    sizes[0] = 0
    largest = int(np.argmax(sizes))
    lys, lxs = np.where(labels == largest)
    lx0, ly0, lx1, ly1 = bbox(lys, lxs)
    diag = ((lx1 - lx0) ** 2 + (ly1 - ly0) ** 2) ** 0.5

    gap_pct = SHIN_GAP_PCT if character == "shin" else DEFAULT_GAP_PCT
    gap_threshold_px = max(1, int(round(diag * gap_pct / 100.0)))
    main_mask = labels == largest
    search_margin = gap_threshold_px + 40   # buffer so a real near-point never falls outside the crop

    image_area = h * w
    min_area_px = image_area * MIN_AREA_PCT / 100.0

    floaters = []
    edge_notes = []
    for lbl in range(1, n + 1):
        if lbl == largest:
            continue
        area = int(sizes[lbl])
        if area < min_area_px:
            continue
        comp = labels == lbl
        cys, cxs = np.where(comp)
        cx0, cy0, cx1, cy1 = bbox(cys, cxs)
        touches_edge = (cx0 <= EDGE_MARGIN_PX or cy0 <= EDGE_MARGIN_PX or
                         cx1 >= w - 1 - EDGE_MARGIN_PX or cy1 >= h - 1 - EDGE_MARGIN_PX)
        gap = gap_distance(comp, main_mask, (cx0, cy0, cx1, cy1), h, w, search_margin)
        attached = gap <= gap_threshold_px
        if attached:
            if touches_edge:
                edge_notes.append(f"attached-part@({cx0},{cy0})-({cx1},{cy1})")
            continue
        centroid = (int(round(cxs.mean())), int(round(cys.mean())))
        floaters.append({
            "size_px": area,
            "size_pct": round(area / image_area * 100, 3),
            "centroid": centroid,
            "bbox": (cx0, cy0, cx1, cy1),
            "touches_edge": touches_edge,
            "gap_px": round(gap, 1) if gap != float("inf") else f">{search_margin}",
        })
        if touches_edge:
            edge_notes.append(f"floater@({cx0},{cy0})-({cx1},{cy1})")

    main_touches_edge = (lx0 <= EDGE_MARGIN_PX or ly0 <= EDGE_MARGIN_PX or
                          lx1 >= w - 1 - EDGE_MARGIN_PX or ly1 >= h - 1 - EDGE_MARGIN_PX)
    if main_touches_edge:
        edge_notes.append(f"main-silhouette@({lx0},{ly0})-({lx1},{ly1})")

    is_smear = "smear" in os.path.basename(path).lower()
    if not floaters:
        verdict = "CLEAN"
    else:
        verdict = "ADVISORY-FLOATER" if is_smear else "FLOATER"

    return {
        "verdict": verdict,
        "count": len(floaters),
        "floaters": floaters,
        "touching_edge": edge_notes,
        "gap_threshold_px": gap_threshold_px,
    }


def format_verdict(res):
    if res["verdict"] == "CLEAN":
        out = "CLEAN"
        if res.get("note"):
            out += f" ({res['note']})"
        return out
    sizes = ", ".join(f"{f['size_px']}px({f['size_pct']}%,gap={f['gap_px']}px)" for f in res["floaters"])
    centroids = ", ".join(str(f["centroid"]) for f in res["floaters"])
    out = f"{res['verdict']}(count={res['count']}, sizes=[{sizes}], centroids=[{centroids}])"
    if res["touching_edge"]:
        out += " TOUCHING-EDGE(" + "; ".join(res["touching_edge"]) + ")"
    return out


def character_for_dir(raw_dir):
    # .../<character>/raw  ->  <character>
    parts = os.path.normpath(raw_dir).split(os.sep)
    if parts and parts[-1] == "raw" and len(parts) >= 2:
        return parts[-2].lower()
    return parts[-1].lower() if parts else ""


def scan_dir(raw_dir):
    character = character_for_dir(raw_dir)
    now = time.time()
    rows = []
    for fname in sorted(os.listdir(raw_dir)):
        if not fname.lower().endswith(".png"):
            continue
        path = os.path.join(raw_dir, fname)
        mtime = os.path.getmtime(path)
        if now - mtime < SKIP_IF_MODIFIED_WITHIN_SEC:
            rows.append((fname, "SKIPPED", "modified <60s ago, likely mid-generation"))
            continue
        res = analyze_frame(path, character)
        rows.append((fname, res["verdict"], format_verdict(res)))
    return character, rows


def _selftest():
    """Synthetic-image assertions for the core verdict logic (no repo data needed)."""
    import tempfile

    def make(w, h, boxes):
        arr = np.full((h, w, 3), 255, dtype=np.uint8)
        for (x0, y0, x1, y1) in boxes:
            arr[y0:y1, x0:x1] = 0
        return arr

    tmp = tempfile.mkdtemp()

    # 1. single blob only -> CLEAN
    Image.fromarray(make(200, 200, [(50, 50, 150, 150)])).save(f"{tmp}/clean.png")
    res = analyze_frame(f"{tmp}/clean.png", "test")
    assert res["verdict"] == "CLEAN", res

    # 2. big blob (160x160, diag~226, 2%~5px threshold) + a small blob 3px away -> attached, CLEAN
    Image.fromarray(make(200, 200, [(20, 20, 180, 180), (183, 90, 195, 110)])).save(f"{tmp}/attached.png")
    res = analyze_frame(f"{tmp}/attached.png", "test")
    assert res["verdict"] == "CLEAN", res

    # 3. big blob + a small blob 80px away -> real floater
    Image.fromarray(make(200, 200, [(20, 20, 120, 120), (170, 20, 195, 45)])).save(f"{tmp}/floater.png")
    res = analyze_frame(f"{tmp}/floater.png", "test")
    assert res["verdict"] == "FLOATER" and res["count"] == 1, res

    # 4. same as #3 but filename says "smear" -> downgraded to advisory, not a hard fail
    Image.fromarray(make(200, 200, [(20, 20, 120, 120), (170, 20, 195, 45)])).save(f"{tmp}/run_smear.png")
    res = analyze_frame(f"{tmp}/run_smear.png", "test")
    assert res["verdict"] == "ADVISORY-FLOATER", res

    # 5. floater touching canvas edge -> flagged TOUCHING-EDGE
    Image.fromarray(make(200, 200, [(60, 60, 160, 160), (0, 10, 15, 30)])).save(f"{tmp}/edge.png")
    res = analyze_frame(f"{tmp}/edge.png", "test")
    assert res["verdict"] == "FLOATER" and res["floaters"][0]["touches_edge"], res

    # 6. Shin gets the same threshold as everyone else (see SHIN_GAP_PCT comment) ->
    #    the 80px-gap floater from #3 must still be caught for character="shin"
    res = analyze_frame(f"{tmp}/floater.png", "shin")
    assert res["verdict"] == "FLOATER", res

    print("detect_floaters selftest: 6/6 OK")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    if sys.argv[1] == "--selftest":
        _selftest()
        return "", False

    any_hard_floater = False
    all_rows = {}
    for raw_dir in sys.argv[1:]:
        character, rows = scan_dir(raw_dir)
        all_rows[character] = rows

    lines = []
    total_clean = total_floater = total_advisory = total_skipped = 0
    for character, rows in all_rows.items():
        lines.append(f"\n=== {character} ({len(rows)} frames) ===")
        lines.append(f"{'frame':<24} {'verdict':<18} detail")
        lines.append("-" * 90)
        for fname, verdict, detail in rows:
            lines.append(f"{fname:<24} {verdict:<18} {detail}")
            if verdict == "CLEAN":
                total_clean += 1
            elif verdict == "FLOATER":
                total_floater += 1
                any_hard_floater = True
            elif verdict == "ADVISORY-FLOATER":
                total_advisory += 1
            elif verdict == "SKIPPED":
                total_skipped += 1

    lines.append("\n=== TOTALS ===")
    lines.append(f"CLEAN: {total_clean}  FLOATER: {total_floater}  "
                  f"ADVISORY-FLOATER: {total_advisory}  SKIPPED: {total_skipped}")
    report = "\n".join(lines)
    print(report)
    return report, any_hard_floater


if __name__ == "__main__":
    _, hard_fail = main()
    sys.exit(1 if hard_fail else 0)
