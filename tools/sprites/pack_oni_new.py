#!/usr/bin/env python3
"""Pack the new Oni's cut cells into web/assets/sprites/oni.{png,json}.

    python3 tools/sprites/pack_oni_new.py --states <dir> --moveset <dir>

Builds a horizontal strip of frameW x frameH cells and the frames{} map the engine
reads, matching the format every other fighter already uses (see exile.json).

⛔ ONE UNIFORM SCALE, anchored on the IDLE body height — never per-cell MATCH_HEIGHT.
Per-cell height matching is right for a row of same-stance cells and catastrophic for a
mixed set like this one: it would blow the compact tucked poses (dive, roll, tumble) up
to the same height as the upright idle and he would visibly swell and shrink between
frames. The Ember recipe records this the hard way; cells here range 86-241px tall.

⛔ AUTHORED FACING LEFT, like the rest of the roster. The engine draws every fighter
through `ctx.scale(-p.facing, 1)`, which assumes the art faces LEFT and mirrors it toward
the opponent. Oni's boards are drawn facing RIGHT, so packed as-drawn he turns his BACK on
the enemy for whole moves — the owner reported exactly that. Calibrated, not guessed: on
the same face-offset measure Shin reads -55.7 and Exile -10.7 (both correctly
left-authored) while every Oni key reads positive (+10.5 idle, +30.8 run, +45.9 light).
So every cell is mirrored ONCE, here, uniformly. Uniformity is the safety: flipping cells
individually is what broke him before, when they were mirrored one at a time to chase claw
handedness and ended up facing opposite ways within the same animation.

⛔ FEET ON footY, not centred. The engine seats a sprite by its foot line, so every cell
is placed with its lowest opaque pixel on footY. Airborne poses are the exception the
caller must think about — they are still bottom-seated here, and the engine's own y
offset lifts them, exactly as it does for the rest of the roster.
"""
import argparse
import json
import pathlib

import numpy as np
from PIL import Image
from scipy import ndimage as nd

# ⛔ A POSE THAT DOES NOT FIT GROWS THE BOX. Never shrink the body, never crop
# the pose — the wall-jump kick-off broke 260 and the answer is a taller frame.
FRAME_W, FRAME_H, FOOT_Y = 420, 300, 268
IDLE_BODY_TARGET = 150          # px of body height inside the frame box
# ⛔ AND THE SCALE THE ENGINE DRAWS AT. These are two different numbers and conflating
# them ships a giant: packed at 150px with scale 1.0 he rendered 152px on screen against
# a roster of 62-72, i.e. more than twice everyone. `scale` in the manifest is the
# ON-SCREEN size, so it is TARGET_DRAWN / IDLE_BODY_TARGET.
#
# ⛔ SIZED ON BODY MASS, NOT ON HEIGHT (owner, Aug 12 2026). Height-matching is what put
# him at 70 and it under-sized him: the cast idles in a wide fighting stance and he
# stands square with his arms in, so at equal height his drawn AREA was 2065px against a
# roster median of 2436 — 15% less mass than everyone he lines up with, and the founder
# read as the smallest man on the card. Measured drawn areas at the shipped scales:
# exile 2879, executioner 2668, ember 2600, tsubasa 2497, mokurai 2375, shin 2317,
# mizu 1930 (kael 1459 is not a mass sample — his idle holds both blades clear of the
# body). Area goes as scale^2, so the median match was sqrt(2436/2065) = 1.086, i.e. 77.
#
# ⛔ AND THE OWNER TOOK THE HEAVIEST MATCH, NOT THE MEDIAN (Aug 12 2026: "increase his
# mass"). 77 was shown to him and it was still short, so the anchor is now the HEAVIEST
# fighter on the card rather than the middle of it: measured through the live engine
# (offscreen drawSprite, alpha bbox) exile draws 3089px of body against Oni's 2456 at 77,
# so sqrt(3089/2456) = 1.1215 and 77 -> 85. He is then tied-heaviest with Exile and
# clearly the tallest — 85 against exile 73, ember 72, executioner/tsubasa/kael 71,
# mokurai 70, shin 68, mizu 64. That is the founder towering over the six by design, so
# do NOT "correct" it back toward the roster's height band.
TARGET_DRAWN_PX = 85


def cells_from(d):
    out = {}
    for f in sorted(pathlib.Path(d).glob('*.png')):
        out[f.stem] = Image.open(f).convert('RGBA')
    return out


def mask_area(im):
    """Area of his WHITE DEMON MASK — the one feature drawn at a fixed size on him."""
    A = np.asarray(im).astype(int)
    op = A[:, :, 3] > 0
    rgb = A[:, :, :3]
    w = op & (rgb.min(2) >= 200) & ((rgb.max(2) - rgb.min(2)) < 40)
    lab, n = nd.label(w)
    if n == 0:
        return None
    sizes = nd.sum(w, lab, range(1, n + 1))
    return float(sizes.max())


def head_band_width(im):
    """Median opaque width across the top third of the figure — hood, horns and mask.

    A GEOMETRIC head measure, deliberately colour-blind, used to sanity-check the mask-area
    anchor below. It survives the mask being RESTYLED, which is exactly where mask area
    fails: on the LIGHT board his mask is drawn as a thin white outline instead of a solid
    face, so its area collapses to 64px against 410-432 on the other directional boards
    while the body is actually the LARGEST of the set. Measured this way the four boards
    agree to within 13% (2.13 / 1.97 / 2.24 / 2.16), which is what "drawn at the same size"
    should look like.
    """
    a = np.asarray(im)[:, :, 3] > 0
    ys, xs = np.where(a)
    if not ys.size:
        return None
    y0, y1 = ys.min(), ys.max()
    band = a[y0:y0 + max(1, int((y1 - y0 + 1) * 0.32))]
    w = band.sum(1)
    w = w[w > 0]
    return float(np.median(w)) if w.size else None


def med_body(cells):
    """Median body height across a board — the denominator for the head/body sanity test."""
    hs = []
    for im in cells.values():
        bb = body_box(im)
        if bb:
            hs.append(bb[3] - bb[1] + 1)
    hs.sort()
    return hs[len(hs) // 2] if hs else 1


def source_scale(cells, ref_area, ref_headw=None, name=''):
    """Per-BOARD scale so his head is the same size whatever sheet a cell came from.

    ⛔ THE BOARDS ARE NOT DRAWN AT ONE SIZE, and nothing warns you. Measured mask areas:
    states 363, moveset 438, run ~660, wall 828, dodge-roll 1672 — the roll board is more
    than four times the states board in area, i.e. twice as big linearly. Packing every
    board at one scale makes him BALLOON mid-roll and shrink back, which reads as the
    sprite breathing. Body height cannot be the anchor either, because a run crouch and
    an upright idle legitimately differ. The mask can: it is rigid, high-contrast, and
    the same object in every frame. This is the house "head-geometry scale only" rule.
    """
    areas = [a for a in (mask_area(im) for im in cells.values()) if a]
    if not areas:
        return 1.0
    areas.sort()
    med = areas[len(areas) // 2]
    k = (ref_area / med) ** 0.5

    # ⛔ AND CROSS-CHECK IT, BECAUSE THE MASK CAN BE RESTYLED. Mask area is the right anchor
    # while the mask is drawn the same way; when it is not, the number is silently absurd
    # rather than wrong-looking. The LIGHT board asked for x5.081 — every other board at the
    # same cell pitch measured x1.9-2.0 — and packing that would have blown 19 cells past
    # the frame box. Head-band WIDTH is geometric and cannot be fooled by a thinner mask, so
    # when the two disagree by more than a quarter the geometry wins and says so. Inside that
    # tolerance the mask keeps deciding, which leaves every already-packed board untouched.
    if ref_headw:
        widths = [w for w in (head_band_width(im) for im in cells.values()) if w]
        if widths:
            widths.sort()
            kg = ref_headw / widths[len(widths) // 2]
            # ⛔ AND THE GEOMETRY ONLY GETS A VOTE WHEN IT IS ACTUALLY MEASURING A HEAD.
            # head_band_width takes the top third of the figure, which stops being the head
            # the moment something thin reaches above it — a cast WIRE, a raised blade, an
            # FX streak. Measured on the Aug-10 GROUP 3 board, whose first two rows are wire
            # casts, it returned a head/body ratio of 0.029 and 0.020 against 0.390 on every
            # packed board, and asked for x29 and x42. That is not a scale, it is a thin
            # line. The failure mode is always a LOW reading, so the floor is what matters:
            # the roster sits near 0.39 and a tucked or crouched board legitimately reads
            # 0.56-0.62 (the body is folded, not the head enlarged), so only a collapsed
            # ratio means the band missed his head. Band kept deliberately loose.
            hb = widths[len(widths) // 2] / max(1, med_body(cells))
            if not (0.20 <= hb <= 0.85):
                print(f'  · {name or "source"}: head geometry ignored (head/body {hb:.3f} '
                      f'— the top band is not his head here, most likely a wire or blade '
                      f'reaching above it); mask area decides')
                return k
            # 1.8x, not something tighter. The two measures legitimately differ by up to
            # ~1.4x on boards that are perfectly fine (states 2.51 vs 1.97, the second jump
            # 1.47 vs 2.03) because the head band also catches hood and horns, which are
            # posed. A tolerance tight enough to "fix" those OVERRIDES four good boards to
            # repair one — measured, it resized the states board by 28% and the second jump
            # by 38%. Only a restyled mask lands beyond 1.8x; the light board sits at 2.27.
            if kg > 0 and (max(k, kg) / min(k, kg)) > 1.8:
                print(f'  ⚠ {name or "source"}: mask-area scale x{k:.3f} disagrees with head '
                      f'geometry x{kg:.3f} — the mask is drawn differently on this board, '
                      f'using the geometry')
                return kg
    return k


def body_box(im):
    a = np.asarray(im)[:, :, 3] > 0
    if not a.any():
        return None
    ys, xs = np.where(a)
    return xs.min(), ys.min(), xs.max(), ys.max()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--states', required=True)
    ap.add_argument('--moveset', required=True)
    ap.add_argument('--run', help='the 8-frame RUN CYCLE board (c1..c8)')
    ap.add_argument('--wall', help='wall-jump cells, slab already stripped')
    ap.add_argument('--roll', help='dodge-roll cells')
    ap.add_argument('--seq', action='append', default=[],
                    help='NAME=dir for a clean 6-frame sequence; repeatable')
    ap.add_argument('--keyed', action='append', default=[],
                    help='dir cut by cut_master_grid whose FILENAMES already name the '
                         'engine key (r<row>_<col>_<key>.png); repeatable')
    ap.add_argument('--skip', default='',
                    help='comma-separated key prefixes to leave out of --keyed dirs, '
                         'for a family that is drawn but not yet cleared to ship')
    ap.add_argument('--remap', default='',
                    help='FROM=TO[+TO2],... rename a --keyed family to the engine family '
                         'that actually draws it; TO+TO2 files the same cells under both')
    ap.add_argument('--out', default='web/assets/sprites')
    ap.add_argument('--dry', action='store_true')
    ap.add_argument('--face-left', dest='face_left', action='store_true', default=True,
                    help='mirror every cell so he is AUTHORED FACING LEFT (default)')
    ap.add_argument('--no-face-left', dest='face_left', action='store_false')
    a = ap.parse_args()

    S = cells_from(a.states)
    M = cells_from(a.moveset)
    R = cells_from(a.run) if a.run else {}
    Wl = cells_from(a.wall) if a.wall else {}
    Rl = cells_from(a.roll) if a.roll else {}
    SEQ = {}
    for spec in a.seq:
        nm, _, path = spec.partition('=')
        SEQ[nm.upper()] = cells_from(path)
    def q(name):
        return SEQ.get(name) or {}
    # ⛔ LOAD THE KEYED DIRS HERE, NOT WHERE THEY ARE USED. Every source has to be present
    # before the head-match loop below or it silently packs at x1.000 — and the four
    # directional boards are NOT drawn at the idle's size (they measure x1.2-1.5), so a
    # missed head-match is exactly the size boil the one-uniform-scale rule exists to stop.
    KEYED = {p: cells_from(p) for p in a.keyed}
    if not S or not M:
        raise SystemExit('no cells found')

    # ---- ONE SCALE, from the idle -------------------------------------------------
    # ⛔ ANCHOR ON THE CELL THE `idle` KEY ACTUALLY USES. When the clean IDLE sequence
    # is supplied it becomes the idle, so measuring scale off the OLD states cell sets
    # the body target for a cell that no longer ships — and the head-match then shrinks
    # the real idle to roughly half size on screen. Anchor and output must be the same cell.
    idle = (SEQ.get('IDLE') or {}).get('c1') or S.get('r1_1_idle')
    if idle is None:
        raise SystemExit('no idle cell — it is the scale anchor')
    x0, y0, x1, y1 = body_box(idle)
    scale = IDLE_BODY_TARGET / (y1 - y0 + 1)
    ref_area = mask_area(idle)
    ref_headw = head_band_width(idle)
    anchor_src = SEQ.get('IDLE') if (SEQ.get('IDLE') or {}).get('c1') else S
    SRC_SCALE = {id(anchor_src): 1.0, id(S): 1.0}
    for name, src in ([('states', S), ('moveset', M), ('run', R), ('wall', Wl), ('roll', Rl)]
                      + [(k.lower(), v) for k, v in SEQ.items()]
                      + [(pathlib.Path(p).name, v) for p, v in KEYED.items()]):
        if src and id(src) != id(anchor_src):
            k = source_scale(src, ref_area, ref_headw, name)
            SRC_SCALE[id(src)] = k
            print(f'  head-match {name}: x{k:.3f}')

    # ---- the map: engine key -> source cell ---------------------------------------
    # Names are the owner's. Where the engine wants a beat he did not draw, an adjacent
    # beat of the SAME move stands in — never a different move, so nothing reads as a
    # non-sequitur mid-animation.
    PLAN = [
        # ⛔ EACH STATE OFF ITS OWN CLEAN SEQUENCE. The owner delivered one bare page per
        # move — no titles, no frame numbers, no wall props — so nothing has to be dodged
        # and the whole figure survives, horns included. Earlier passes pulled these keys
        # off the mixed 4x8 sheets and had to crop text out, which is what decapitated him.
        ('idle',        q('IDLE') or S, 'c1' if q('IDLE') else 'r1_1_idle'),
        ('idle2',       q('IDLE') or S, 'c4' if q('IDLE') else 'r2_8_stand'),
        # ⛔ A RUN MUST CLOSE ON ITSELF. The states sheet only ever held a dash BURST —
        # start, accelerate, burst, stop — so run_clean8 used to fold back to an earlier
        # loop cell and the stride visibly hitched. The owner's 8-frame cycle board is a
        # true loop, so all eight keys come off it in order and frame 8 hands back to 1.
        ('run_clean1',  R or S, 'c1' if R else 'r1_2_run_start'),
        ('run_clean2',  R or S, 'c2' if R else 'r1_3_run_loop1'),
        ('run_clean3',  R or S, 'c3' if R else 'r1_4_run_accel'),
        ('run_clean4',  R or S, 'c4' if R else 'r1_5_run_loop2'),
        ('run_clean5',  R or S, 'c5' if R else 'r1_6_dash_start'),
        ('run_clean6',  R or S, 'c6' if R else 'r1_7_dash_burst'),
        ('run_clean7',  R or S, 'c7' if R else 'r1_8_dash_end'),
        ('run_clean8',  R or S, 'c8' if R else 'r1_3_run_loop1'),
        # the dash keeps the burst it was actually drawn for
        ('dash1',       S, 'r1_6_dash_start'),
        ('dash2',       S, 'r1_7_dash_burst'),
        ('dash3',       S, 'r1_8_dash_end'),
        ('jump',        q('JUMP') or S, 'c2' if q('JUMP') else 'r3_1_jump_takeoff'),
        ('jump1',       q('JUMP') or S, 'c3' if q('JUMP') else 'r3_2_jump_rise'),
        ('jump2',       q('JUMP') or S, 'c4' if q('JUMP') else 'r3_3_jump_peak'),
        ('fall',        q('JUMP') or S, 'c5' if q('JUMP') else 'r3_4_jump_fall'),
        ('fall2',       q('JUMP') or S, 'c6' if q('JUMP') else 'r3_8_land_recover'),
        # LIGHT = the lunge claw slash: quick, forward, claw-led.
        ('light1',      q('LUNGECLAW') or M, 'c1' if q('LUNGECLAW') else 'r3_1_claws_out1'),
        ('light2',      q('LUNGECLAW') or M, 'c2' if q('LUNGECLAW') else 'r3_2_claws_out2'),
        ('light3',      q('LUNGECLAW') or M, 'c3' if q('LUNGECLAW') else 'r3_3_claw_thrust1'),
        ('light4',      q('LUNGECLAW') or M, 'c4' if q('LUNGECLAW') else 'r3_4_claw_thrust2'),
        ('light5',      q('LUNGECLAW') or M, 'c5' if q('LUNGECLAW') else 'r3_8_rising_arc'),
        # HEAVY = the rising claw: the big committed swing, startup through recovery.
        ('heavy_i1',    q('RISINGCLAW') or M, 'c2' if q('RISINGCLAW') else 'r3_6_rising_slash1'),
        ('heavy_i2',    q('RISINGCLAW') or M, 'c3' if q('RISINGCLAW') else 'r3_7_rising_slash2'),
        ('heavy_i3',    q('RISINGCLAW') or M, 'c4' if q('RISINGCLAW') else 'r3_5_ground_slam'),
        ('heavy_i4',    q('RISINGCLAW') or M, 'c5' if q('RISINGCLAW') else 'r3_8_rising_arc'),
        ('heavy_i5',    q('RISINGCLAW') or M, 'c6' if q('RISINGCLAW') else 'r3_2_claws_out2'),
        # ⛔ SPECIAL = THE WIRE SHOT, OFF THE PAGE THE OWNER REDREW. Six beats in order:
        # stance, claw fires, wire taut at full reach, the retract slash, the coil, recovery.
        #
        # It runs off WIRESHOT2, not the first wire-shot page, because the first one could
        # not be cut cleanly: his figures drifted across the page (one beat was airborne and
        # off the ground line the others share) and the wire ran straight through two cut
        # columns. The redraw plants all six on one ground line — measured crop heights
        # 327-342px against the old page's spread — so the sequence no longer boils, and the
        # cut lands 6/6 with the only sliced FX being the neighbour stubs dropped at source.
        #
        # The wire-into-knives page stays cut and archived but UNROUTED, next to the katana
        # and the bo: there is one special slot and two complete 6-beat sequences, so routing
        # both would mean neither plays whole.
        ('special1',    q('WIRESHOT2') or M, 'c1' if q('WIRESHOT2') else 'r4_7_dive_bomb'),
        ('special2',    q('WIRESHOT2') or M, 'c2' if q('WIRESHOT2') else 'r4_8_dive_impact'),
        ('special3',    q('WIRESHOT2') or M, 'c3' if q('WIRESHOT2') else 'r4_8_dive_impact'),
        ('special4',    q('WIRESHOT2') or M, 'c4' if q('WIRESHOT2') else 'r4_7_dive_bomb'),
        ('special5',    q('WIRESHOT2') or M, 'c5' if q('WIRESHOT2') else 'r4_8_dive_impact'),
        ('special6',    q('WIRESHOT2') or M, 'c6' if q('WIRESHOT2') else 'r4_8_dive_impact'),
        ('divekick1',   q('DIVEKICK') or M, 'c3' if q('DIVEKICK') else 'r4_7_dive_bomb'),
        ('divekick2',   q('DIVEKICK') or M, 'c4' if q('DIVEKICK') else 'r4_8_dive_impact'),
        # the wire WHIP is the close-range arc off the same weapon
        ('wire1',       q('WIRE-WHIP') or M, 'c2' if q('WIRE-WHIP') else 'r3_1_claws_out1'),
        ('wire2',       q('WIRE-WHIP') or M, 'c4' if q('WIRE-WHIP') else 'r3_2_claws_out2'),
        ('wire3',       q('WIRE-WHIP') or M, 'c5' if q('WIRE-WHIP') else 'r3_8_rising_arc'),
        # dashing claw = the forward-dash attack
        ('dashatk1',    q('DASHCLAW') or M, 'c3' if q('DASHCLAW') else 'r3_3_claw_thrust1'),
        ('dashatk2',    q('DASHCLAW') or M, 'c4' if q('DASHCLAW') else 'r3_4_claw_thrust2'),
        # air kick gets its own page rather than borrowing the spin
        ('airkick1',    q('AIRKICK') or M, 'c3' if q('AIRKICK') else 'r4_1_air_kick1'),
        ('airkick2',    q('AIRKICK') or M, 'c4' if q('AIRKICK') else 'r4_2_air_kick2'),
        ('block',       q('BLOCK') or M, 'c1' if q('BLOCK') else 'r1_6_low_guard'),
        ('block2',      q('BLOCK') or M, 'c2' if q('BLOCK') else 'r2_5_knee_guard'),
        ('blockhit',    q('BLOCK') or M, 'c3' if q('BLOCK') else 'r2_5_knee_guard'),
        ('hurt',        q('HURT') or S, 'c1' if q('HURT') else 'r4_1_hurt_light'),
        ('hurt2',       q('HURT') or S, 'c2' if q('HURT') else 'r4_2_air_tumble1'),
        ('hurt3',       q('HURT') or S, 'c3' if q('HURT') else 'r4_3_air_tumble2'),
        ('kneel',       M, 'r2_1_deep_crouch'),
        ('roll',        Rl or S, 'c3' if Rl else 'r2_5_roll_mid'),
        ('roll2',       Rl or S, 'c4' if Rl else 'r2_5_roll_mid'),
        ('wallslide',   Wl or S, 'c3' if Wl else 'r2_1_wall_cling'),
        ('walljump',    Wl or S, 'c5' if Wl else 'r2_3_wall_jump_leap'),
        ('ksweep',      M, 'r2_3_slide_sweep1'),
        ('kstomp',      M, 'r1_7_axe_kick'),
        ('kheel',       M, 'r1_8_rising_crescent'),
        ('kpush',       M, 'r2_7_leap_punch'),
        # a few extras the engine reaches for when they exist
        ('crouch',      M, 'r2_1_deep_crouch'),
        ('slide1',      M, 'r2_3_slide_sweep1'),
        ('slide2',      M, 'r2_4_slide_sweep2'),
        ('getup',       q('HURT') or S, 'c5' if q('HURT') else 'r4_7_getup'),
        ('getup2',      q('HURT') or S, 'c6' if q('HURT') else 'r4_8_getup_stand'),
        # ⛔ THE DOUBLE JUMP. ajump1..6 is a real engine family and SIX of the eight fighters
        # carry it; Oni had none, so his second jump drew his ordinary rise. The owner's
        # second-jump board is exactly the six beats it wants — rise, tuck, the spin, fully
        # inverted, opening out, landing ready — and it had been sitting cut on disk unpacked.
        # ⛔ THE OWNER'S OWN LIGHT BOARD OWNS THIS FAMILY NOW. glfwd came off the front
        # cartwheel as a stand-in, because the cartwheel was the only forward-light art on
        # disk. His LIGHT-DIR board supersedes it: his forward light is the dual-knife X
        # slash, and he also drew the neutral, down and up rows, so all four arrive by
        # filename through --keyed. The BACKFLIP keeps glback — that board has no BACK row,
        # so nothing supersedes it, and the kit sheet files the backflip as a light attack.
        # ⚠ THE CARTWHEEL IS THEREFORE UNROUTED AGAIN, and that is flagged rather than
        # quietly dropped: it is still cut on disk and still a light attack per the kit
        # sheet, but every ground-light direction is now spoken for by the owner's own art.
        ('glback1',     q('BACKFLIP') or M, 'c1' if q('BACKFLIP') else 'r3_1_claws_out1'),
        ('glback2',     q('BACKFLIP') or M, 'c2' if q('BACKFLIP') else 'r3_2_claws_out2'),
        ('glback3',     q('BACKFLIP') or M, 'c3' if q('BACKFLIP') else 'r3_3_claw_thrust1'),
        ('glback4',     q('BACKFLIP') or M, 'c4' if q('BACKFLIP') else 'r3_4_claw_thrust2'),
        ('glback5',     q('BACKFLIP') or M, 'c5' if q('BACKFLIP') else 'r3_8_rising_arc'),
        ('glback6',     q('BACKFLIP') or M, 'c6' if q('BACKFLIP') else 'r3_2_claws_out2'),
        # ⛔ THE SMOKE BOMB IS THE **AIR** DOWN SPECIAL (kit sheet), so it takes sdown — the
        # air-gated family — and the earth-rupture stomp keeps gsdown, the GROUND one. They
        # were sharing both gates; splitting them gives each its own move and costs no cell.
        # ⛔ BEAT 4 IS DROPPED — HE IS NOT HIDDEN BY HIS OWN MOVE (owner). On the board,
        # beat 4 is a smoke COLUMN with his silhouette buried inside it: the player loses
        # the character for a frame, and a fighting game cannot afford an unreadable
        # attacker. Beat 3 (the bomb leaving his hand over the burst) is HELD for two beats
        # instead, which is also where the active window belongs, so the move reads as a
        # throw rather than a disappearance. Beat 5 stays — he is legible through the wisps.
        ('sdown1',      q('SMOKEBOMB') or M, 'c1' if q('SMOKEBOMB') else 'r4_7_dive_bomb'),
        ('sdown2',      q('SMOKEBOMB') or M, 'c2' if q('SMOKEBOMB') else 'r4_7_dive_bomb'),
        ('sdown3',      q('SMOKEBOMB') or M, 'c3' if q('SMOKEBOMB') else 'r4_8_dive_impact'),
        ('sdown4',      q('SMOKEBOMB') or M, 'c3' if q('SMOKEBOMB') else 'r4_8_dive_impact'),
        ('sdown5',      q('SMOKEBOMB') or M, 'c5' if q('SMOKEBOMB') else 'r4_8_dive_impact'),
        ('sdown6',      q('SMOKEBOMB') or M, 'c6' if q('SMOKEBOMB') else 'r4_8_dive_impact'),
        ('ajump1',      q('SECONDJUMP') or S, 'c1' if q('SECONDJUMP') else 'r3_2_jump_rise'),
        ('ajump2',      q('SECONDJUMP') or S, 'c2' if q('SECONDJUMP') else 'r3_3_jump_peak'),
        ('ajump3',      q('SECONDJUMP') or S, 'c3' if q('SECONDJUMP') else 'r3_3_jump_peak'),
        ('ajump4',      q('SECONDJUMP') or S, 'c4' if q('SECONDJUMP') else 'r3_4_jump_fall'),
        ('ajump5',      q('SECONDJUMP') or S, 'c5' if q('SECONDJUMP') else 'r3_4_jump_fall'),
        ('ajump6',      q('SECONDJUMP') or S, 'c6' if q('SECONDJUMP') else 'r3_8_land_recover'),
        ('air1',        q('AIRSPIN') or M, 'c2' if q('AIRSPIN') else 'r4_1_air_kick1'),
        ('air2',        q('AIRSPIN') or M, 'c3' if q('AIRSPIN') else 'r4_2_air_kick2'),
        ('air3',        q('AIRSPIN') or M, 'c4' if q('AIRSPIN') else 'r4_3_air_lunge1'),
    ]

    # ⛔ THE DIRECTIONAL BOARDS NEED NO PLAN ENTRIES. cut_master_grid names each cell for
    # the engine key it fills (r1_1_hfwd1.png -> hfwd1), because the owner's rows ARE the
    # families dirCells() reads and each is exactly the six beats it wants. Writing them
    # out by hand would be 96 lines that can only introduce typos, so the filename is the
    # mapping. Anything listed in --skip is dropped here rather than never cut: the art
    # exists and stays cut on disk, it just does not reach the sheet.
    #
    # ⛔ AND THE ROW'S NAME IS NOT ALWAYS THE ENGINE'S. dirCells is reached from two
    # different gates: hfwd/hback/hup/hdown and sfwd/sback/sup/sdown only draw behind
    # `if (p.attackAir)`, while gsfwd/gsback/gsdown are the GROUNDED special families.
    # The owner's "FORWARD SPECIAL / BACK SPECIAL" rows are planted dashes — measured
    # driving the engine, air-only keys drew 0 frames from the ground — so filing them
    # under sfwd/sback would have packed 12 cells nothing could ever reach. --remap moves
    # a row to the family that actually draws it, and TO+TO2 files one row under both
    # gates where the pose reads either way (the down stomp works grounded or dropped).
    skip = tuple(s for s in a.skip.split(',') if s)
    remap = dict(kv.split('=', 1) for kv in a.remap.split(',') if '=' in kv)
    for path, ksrc in KEYED.items():
        for stem in sorted(ksrc):
            key = stem.split('_', 2)[2]
            if skip and key.startswith(skip):
                continue
            fam, beat = key.rstrip('0123456789'), key[len(key.rstrip('0123456789')):]
            for tgt in remap.get(fam, fam).split('+'):
                PLAN.append((tgt + beat, ksrc, stem))

    uniq, order = {}, []
    for key, src, name in PLAN:
        if name not in src:
            print(f'  ⚠ {key}: source cell {name} missing — skipped')
            continue
        tag = (id(src), name)
        if tag not in uniq:
            uniq[tag] = len(order)
            order.append((name, src[name], id(src)))
    frames = {}
    for key, src, name in PLAN:
        if (id(src), name) in uniq:
            frames[key] = uniq[(id(src), name)]

    cols = len(order)
    sheet = Image.new('RGBA', (FRAME_W * cols, FRAME_H), (0, 0, 0, 0))
    over = 0
    for i, (name, im, srcid) in enumerate(order):
        sc = scale * SRC_SCALE.get(srcid, 1.0)
        w = max(1, int(round(im.width * sc)))
        h = max(1, int(round(im.height * sc)))
        r = im.resize((w, h), Image.LANCZOS)
        if a.face_left:
            r = r.transpose(Image.FLIP_LEFT_RIGHT)
        bb = body_box(r)
        if bb is None:
            continue
        bx0, by0, bx1, by1 = bb
        cx = FRAME_W * i + FRAME_W // 2 - (bx0 + bx1) // 2
        cy = FOOT_Y - by1
        if by1 - by0 > FRAME_H or w > FRAME_W:
            over += 1
            print(f'  ⚠ {name} exceeds the frame box ({w}x{h}) — GROW frameW/frameH')
        sheet.alpha_composite(r, (cx, max(0, cy)))

    draw_scale = TARGET_DRAWN_PX / IDLE_BODY_TARGET
    man = dict(frameW=FRAME_W, frameH=FRAME_H, footY=FOOT_Y, cols=cols,
               frames=frames, scale=round(draw_scale, 4))
    print(f'pack scale {scale:.4f} (idle body {y1-y0+1}px -> {IDLE_BODY_TARGET}px)')
    print(f'draw scale {draw_scale:.4f} -> ~{TARGET_DRAWN_PX}px on screen')
    print(f'{cols} unique cells, {len(frames)} keys, {over} oversize')
    if a.dry:
        return
    out = pathlib.Path(a.out)
    sheet.save(out / 'oni.png')
    (out / 'oni.json').write_text(json.dumps(man, indent=1))
    print(f'wrote {out}/oni.png  {sheet.width}x{sheet.height}')
    print(f'wrote {out}/oni.json')


if __name__ == '__main__':
    main()
