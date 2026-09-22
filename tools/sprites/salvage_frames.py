#!/usr/bin/env python3
"""Frame salvage — recover FAILED Seedance/Kling frames instead of re-generating.

Implements syntheses/sprite-frame-salvage-pipeline.md (owner canon, Jul 30 2026):

    failed frame + base character reference
      -> Nano Banana Pro 2 re-projects the pose to clean side profile on MAGENTA
      -> chroma-key #FF00FF
      -> align / pack

The insight the doc rests on: a clip that rotated 45 degrees off profile still
carries correct limb positions, stride length and weapon angle. That is pose data
you already paid for. Two reference images are passed -- the failed frame for the
POSE, the master for the IDENTITY -- which is why this recovers frames a single-
image edit cannot.

Magenta, not white: these sprites have white highlights and near-white steel, so a
white key eats the blade. #FF00FF appears nowhere in the roster palette.

READ THE FLAW BEFORE YOU "FIX" IT (owner rule, Jul 30 2026). Some defects are better
used than corrected — a frame is only broken relative to what you intended it for.

  Blade missing from the hand      -> a SPEED frame. Real 2D fighting games omit the
                                      weapon entirely on the fastest cell of a cut and
                                      let the arc carry it; the blade returns next cell.
                                      Executioner's rejected stance clip holds only the
                                      HILT with the saya at his back — that is nukitsuke,
                                      the instant the blade clears the scabbard.
  Motion blur smearing a limb      -> a smear/impact frame between two clean keys.
  Character mid-rotation           -> a turnaround or a dodge beat.
  Pose collapsed toward idle       -> a recovery / zanshin hold.

So triage first: is this frame wrong, or is it right for a DIFFERENT slot? Only send
the genuinely wrong ones through salvage.

Usage:
  python3 salvage_frames.py <fighter> <out_subdir> <frame.png> [frame.png ...]
Writes to media/salvaged-poses/<fighter>/<out_subdir>/ -- a reusable pose library,
so future work starts from these instead of paying Seedance again.
"""
import os, sys, re, subprocess, pathlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def load_key():
    if os.environ.get("FAL_KEY"):
        return
    for line in open('/Users/anthonyguy/WILDCOMIKS.2.0/.env.local'):
        m = re.match(r'\s*(?:export\s+)?FAL_KEY\s*=\s*["\']?([^"\'\s]+)', line)
        if m:
            os.environ['FAL_KEY'] = m.group(1)
            return
    sys.exit("FAL_KEY not found")

load_key()
import fal_client
from fal_models import still_edit

REPO = pathlib.Path(__file__).resolve().parents[2]
MASTER = {f: REPO / f"media/polished-candidates/{f}/truecolor-raw/idle.png"
          for f in ("executioner", "kael", "ember", "mizu", "shin", "tsubasa")}
IDENTITY = {f: (REPO / f"media/polished-candidates/{f}/identity-true.txt")
            for f in MASTER}

MAGENTA = "#FF00FF"

# BLADE WIELDERS DRAW FROM REAL SWORD TECHNIQUE (owner, standing rule). A salvaged
# pose must resolve to a NAMED technique from the fighter's actual school, never a
# generic swing -- "sword rotating around a man standing still" is the exact defect
# this exists to stop. Source: research/opus5-shadowclash-prompts.md.
TECHNIQUE = {
    "executioner": (
        "He is an ITTO-RYU / IAIJUTSU swordsman: ONE sword, leverage and edge alignment "
        "(hasuji). Resolve his pose to the nearest real technique — a kamae (Jodan "
        "overhead, Chudan centre, Gedan low, Hasso vertical beside the ear, Waki hidden "
        "with the blade trailing behind), or a cut (kesagiri diagonal down through the "
        "collar, gyaku-kesa rising, tsuki straight thrust, nukitsuke the draw-cut out of "
        "the scabbard). The edge must ALIGN with the cut path, the hips drive the cut, and "
        "the weight transfers from the back leg to the front. Guard never drops on "
        "recovery (zanshin)."
    ),
    "kael": (
        "He is a NITEN ICHI-RYU / two-heavens swordsman: long sword (daito) plus short "
        "sword (shoto). Resolve his pose to the real principle — the SHORT blade takes the "
        "line or parries while the LONG blade cuts, both arms moving at the SAME INSTANT, "
        "never one after the other. The two blades sit at different heights and never mirror "
        "each other."
    ),
    "tsubasa": (
        "She fights SHOTO NITOJUTSU with two short blades in reverse grip: close quarters, "
        "elbows tucked, tight inside-range cross-slices and trapping. No wide committed "
        "swings — that is a long-sword idea and wrong for her."
    ),
    "mizu": (
        "She fights BOJUTSU with a staff: strikes come from the ends through sliding grip "
        "changes and rotation about the centre, never from a sword-like edge swing."
    ),
    "ember": (
        "He fights TEKKO-KAGIJUTSU with hand claws — raking and trapping at close range, "
        "never a sword cut. The claws are an extension of the hand, so the wrist and elbow "
        "lead, not a blade arc."
    ),
}


def prompt_for(fighter):
    """The identity lock is pasted VERBATIM into every call -- the doc's rule that
    re-wording a character description gives the model licence to redesign him."""
    lock = IDENTITY[fighter].read_text().strip() if IDENTITY[fighter].exists() else ""
    tech = TECHNIQUE.get(fighter, "")
    tech_block = f"\n\nMARTIAL TECHNIQUE (the pose must read as a real technique, not a generic swing): {tech}\n" if tech else "\n"
    return (
        "Image 1 is a FAILED animation frame. Image 2 is the CANONICAL character.\n\n"
        "Redraw the character from Image 2 in the EXACT pose shown in Image 1: same limb "
        "positions, same stride, same weapon angle, same body lean. Keep the pose, replace "
        "nothing about it.\n\n"
        "Re-project that pose to a CLEAN LEFT SIDE PROFILE — if Image 1 rotated the "
        "character toward the camera or to three-quarter view, rotate it back to pure side "
        "view while preserving the limb positions. Centre him, and draw him at the SAME "
        "BODY HEIGHT as the character in Image 2. No camera angle shift, no perspective.\n\n"
        f"CHARACTER CANON (must match exactly): {lock}\n"
        f"{tech_block}\n"
        "Fix any anatomy the failed frame broke: BOTH arms fully drawn from shoulder to "
        "hand, both legs present, nothing cropped by the frame edge, weapons at their "
        "correct COUNT and their normal SIZE (never oversized, never a giant crescent or "
        "scythe). Only this one character is in the picture — no opponent, no second "
        "person's hand or arm.\n\n"
        f"Flat 2D cel-shaded cartoon game sprite, bold heavy black outlines, solid "
        f"{MAGENTA} magenta background, no shadow, no glow, no energy, no slash arcs, no "
        "speed lines, no motion blur, no text."
    )

def salvage(fighter, out_subdir, frames):
    out = REPO / "media/salvaged-poses" / fighter / out_subdir
    out.mkdir(parents=True, exist_ok=True)
    master = MASTER[fighter]
    p = prompt_for(fighter)
    done = []
    for f in frames:
        src = pathlib.Path(f)
        raw = out / f"{src.stem}_raw.png"
        keyed = out / f"{src.stem}.png"
        # image_urls order matters: [failed frame, canonical master] == [Image 1, Image 2]
        r = still_edit(fal_client, p, [str(src), str(master)])
        subprocess.run(["curl", "-sSL", "-o", str(raw), r["images"][0]["url"]], check=True)
        # Step 4: chroma-key. -fuzz BEFORE -transparent or the flag is ignored.
        subprocess.run(["magick", str(raw), "-fuzz", "22%", "-transparent", MAGENTA,
                        "-trim", "+repage", str(keyed)], check=True)
        print(f"  {src.name} -> {keyed.relative_to(REPO)}")
        done.append(keyed)
    return done

if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    fighter, sub, frames = sys.argv[1], sys.argv[2], sys.argv[3:]
    if fighter not in MASTER:
        sys.exit(f"unknown fighter {fighter}; known: {sorted(MASTER)}")
    print(f"salvaging {len(frames)} frame(s) for {fighter} -> media/salvaged-poses/{fighter}/{sub}/")
    salvage(fighter, sub, frames)
