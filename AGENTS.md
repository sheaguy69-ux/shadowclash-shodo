# ShadowClash — the rulebook

One file. If a rule is not here, it is not a rule.

---

## 0. Ask before each step

Anthony approves each step before you take it. Not a plan for ten steps — the next one.
Show the thing, get the yes, do it, show what happened.

## 1. A change DELETES the old version. Automatically. Same pass.

When Anthony rules something, the previous version stops existing everywhere in that same
turn — this file, the engine comments, agent memory, the design docs. No "superseded", no
struck-through text, no "this used to say", no parked conflicts.

He will change his mind, and he should be able to without paying for it later. The cost of
a contradiction is always paid by the next session, which cannot tell which version is live.

**He does not have to ask for the cleanup. Doing it is part of accepting the change.**

---

## 2. Two tiers, and only one of them is fixed

### CANON — concrete. Ask before changing.

Who a fighter **is**: gender, weapon, eye count and colour, anatomy, name and epithet.
These are identity. Getting one wrong ships a different character.

| | |
|---|---|
| **Executioner** | he/him · long sword · **two** eyes, front one a small wedge · oldest and tallest, *slightly* |
| **Mizu** | she/her · bo staff (splits to twin hanbō) |
| **Shin** | he/him · wire + shuriken · **single eye is canon — never flag it** |
| **Tsubasa** | he/him · twin tantō |
| **Ember** | he/him · **THREE claws on each hand** · grey, with grey eyes |
| **Kael** | he/him · **one long + one short sword** |
| **Mokurai** | he/him · **bare hands, bead-wrapped fists — no bo staff, ever** · "the Sage of Nothingness", his only epithet · the word "Buddha" never ships |
| **Exile** | she/her · kusarigama, **spiked** ball · **red** eye, iris `#B94828` |
| **Oni** | he/him · "The Founder" · white skull mask, three gouges, red eyes, two horns · black hood and mantle, ash plate · **right hand claw only**, left hand wrapped · two swords crossed on his back |

Also canon: **Mokurai is taller than Exile.** Sprites are authored facing **left** and
mirrored, so an asymmetric weapon swaps hands on a turn — that is how the game ships, for
everyone. Drawing a weapon on the wrong hand in a cell is an art mistake; mirroring is not.

### CURRENT — everything else. Changes freely.

Palette, mechanics, timing, balance, feel, movelists, stage looks, lore. These are the
state of the game today, not law. Read them to know what the game currently does; change
them when Anthony says so, and delete what they replace.

Do not quote a CURRENT value back at him as a reason not to do something.

---

## 3. Don't destroy work

The only rules here that exist to stop an accident rather than express a preference.

1. **Open your lane first**: `python3 tools/lane.py start "<your name>"`. Several agents
   share this tree. Anything already dirty is someone else's — the pre-commit hook refuses
   it. Claim what you touch: `lane.py claim <paths>`. If the hook refuses, leave it alone.
2. **Never `git checkout` a dirty file.** It has silently wiped another agent's work.
3. **Never delete anything he did not name.** Orphaned does not mean unwanted.
4. **Local commits only. Never push, merge or deploy.**
5. **Bump `SHEET_V`** in the same commit as any `web/assets/sprites/*` change, or the
   browser serves a stale sheet against a new manifest and the fighter renders invisible.
6. **Show art before it lands** — a montage strip or a filmstrip, in front of him, before
   the sheet is touched. Engine work commits itself; art waits for his eye.
   **But SEARCH FIRST — he may already have approved it, and re-asking wastes his time.**
   There are ~164 approval records already on disk in four shapes: `media/*/APPROVAL.md`
   and `.json`, folders ending `-approved-<date>` or `-approved-review`, and
   `approved-install-<NNN>` markers. One command covers all of them:

   ```bash
   F=ember   # the fighter
   { find art media -iname "*approved*" -iname "*$F*"
     find media -iname "APPROVAL*" | xargs grep -ril "$F"; } | sort -u
   ```

   Read the hits before you ask. If it is there, it is approved — do not re-litigate it.
   (Substring matching, so glance at the path: `oni-…-ember-mastery-…` answers to `ember`.)

   **When he approves something new, drop a marker in the same convention** — an
   `APPROVAL.md` beside the montage he looked at, naming the fighter, the rows and the
   date — so the next session finds it instead of asking him again.
7. **No paid generation.** New cells come from the generator he drives himself. This repo's
   job is to hand it measured references and check what comes back.
8. **Balance changes are their own commit,** named as such — never folded into an art or
   cosmetic commit where he cannot see them.

---

## 4. The tree

`web/index.html` is the whole game — one file, one inline classic `<script>`, bare
identifiers, no modules and no window globals. `godot/` is dead. Deliverables in `media/`.

**`:9101` IS THE TREE** (owner, Sep 22 2026) — his review surface, and what every tool in
`tools/` now defaults to. **Never kill it.** `python3 tools/serve.py 9101 web`.

`:9100` is the recovered rollback and `:9102` the approved-art gallery; both stay reachable
by override (`SHADOWCLASH_URL=http://localhost:9100/index.html <command>`), they are just
not the default any more. They used to be: `serve.py` served `:9101` while ~39 harnesses
graded `:9100`, so the checks measured the rollback tree while the work went to this one.

`curl -s localhost:<port>/whoami` before believing anything about what a page is serving.

Verify by watching, not by asserting: capture consecutive live frames. A static assert
cannot see a ghost, and "it builds" is not verification.
