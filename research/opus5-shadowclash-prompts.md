# Opus 5 — ShadowClash kenjutsu prompt pack

Source: owner's swordsmanship knowledge-base script (Jul 29 2026). Reference only —
nothing here is packed art. Sheet changes still gate on SHEET_V + owner motion review.

## 1. Roster ↔ style map (as of SHEET_V 288)

| fighter | weapon_type (manifest) | martial_art_discipline (manifest) | script style |
|---|---|---|---|
| executioner | Nodachi / Single Katana | Iaijutsu & Battōjutsu | **Ittō-ryū** (one-sword) |
| kael | Katana & Wakizashi / Tantō | Niten Ichi-ryū & Tantōjutsu | **Niten Ichi-ryū** ✅ already exact |
| tsubasa | Dual Tantō Knives | Tantōjutsu (Reverse-Grip) | **Shōtō Nitōjutsu** (two shorts) |
| shin | Unarmed & Shuriken / Kunai | Taijutsu & Shurikenjutsu | **Taijutsu + Shurikenjutsu** ✅ settled |
| ember | Tekkō-kagi (Iron Claws) | Tekkōkagijutsu / Shukōjutsu | — none in script |
| exile | Kusarigama (chain + sickle) | **Kusarigamajutsu** | — none in script |
| mizu | Bō / Hanbō | Bōjutsu & Hanbōjutsu | — none in script |
| mokurai, oni | (unset) | (unset) | — none in script |

**✅ Shin — SETTLED, do not re-open (owner, Jul 30 2026).** Shin is **primarily a
hand-to-hand fighter who only ever uses PROJECTILE steel** — shuriken and kunai. His
discipline is **Taijutsu + Shurikenjutsu**. He does NOT get a sword, so
**Shinobi Bikenjutsu is DROPPED from the roster** rather than reassigned — no other
fighter carries a ninjatō either. Earlier drafts of this file offered the owner an A/B
choice here; that was the file re-asking a question he had already answered in the
manifest (`weapon_type: "Unarmed & Shuriken / Kunai"`). The engine already agrees:
`spawnSlash` returns early for `spec.id === 2`, so Shin draws no blade crescent — correct
by canon, not by accident. Anything that needs a "swing frame" for Shin uses the THROW
RELEASE instead, and the projectile carries the motion.

**⛔ Exile is DONE — do not add to her (owner, Jul 30 2026).** Her moveset is complete and
already over-tuned ("too powerful"). The chain-entangle clash idea below is CANON NOTE
ONLY — do not implement it, it would buff a fighter the owner is already unhappy with.
Any blade-style work is scoped to **executioner, kael, tsubasa, ember**.

**Exile — Kusarigamajutsu.** Chain-and-sickle. Worth noting for combat design: the
weighted chain's historical job is to **entangle and trap the opponent's blade** so the
kama can finish — which makes her the roster's purest expression of the bind. Her arc is
hooked and short; her range comes from the chain, not the blade.

Only Kael's map was a no-op. Executioner/Tsubasa are naming refinements, not new art.

## 2. Style canon

**Ittō-ryū (One-Sword Style)** — single katana. Leverage, *hasuji* (edge alignment),
precise transitions between the five *kamae*: Jōdan (overhead), Chūdan (centre),
Gedan (low), Hassō (vertical beside the ear), Waki (hidden, blade trailing behind).

**Niten Ichi-ryū / Ryōtōjutsu** — daitō + shōtō. Simultaneous parry-and-strike; the short
sword takes the line while the long sword lands. Musashi's two-heavens principle.

**Shōtō Nitōjutsu** — dual wakizashi or dual tantō. Close-quarters: tight trapping, joint
locks, rapid reverse-grip slices. No long-range commitment.

**Shinobi Bikenjutsu** — ninjatō / concealable straight katana. Reverse grips, low-angle
surprise draws out of the saya, smoke-screen feints, silent vital strikes.

## 3. Etiquette gestures (animation hooks, not combat frames)

| term | beat | where it belongs |
|---|---|---|
| **reihō** | bow before and after engagement | round intro / victory pose |
| **zanshin** | alertness *held* after the strike — guard never drops on recovery | last 1–2 recovery cells of every heavy |
| **chiburi** | flick the blade clean | victory pose, sword fighters only |
| **nōtō** | deliberate re-sheathe into the saya | victory pose tail, after chiburi |

Zanshin is the one with real gameplay reach: it says recovery cells should read as *poised*,
not slumped. Everything else is a win-screen flourish.

## 4. i2v prompt wording (Seedance 2, ~$0.15 / 5s at 1080p — see CLAUDE.md MODEL LAW)

Append to the fighter's identity string from `<Fighter>-Identity-True-Lock.md`; keep the
side-profile framing and the existing NEVER gates.

- **Ittō-ryū strike** — "side profile, single katana held Chūdan centre guard, steps in and
  cuts to Gedan low finish, edge aligned with the cut path, blade never wobbles, holds the
  finish position alert"
- **Ittō-ryū kamae transition** — "side profile, raises katana from Chūdan to Jōdan overhead
  guard in one continuous lift, elbows tracking, no pause"
- **Niten Ichi-ryū** — "side profile, short sword parries high while the long sword cuts low
  at the same instant, both arms moving together, not sequentially"
- **Shōtō Nitōjutsu** — "side profile, two short blades in reverse grip, tight inside-range
  cross-slash, elbows stay close to the body, no wide swings"
- **Bikenjutsu draw** — "side profile, low crouched surprise draw of a straight ninjatō out
  of the scabbard rising from hip height, blade clears the saya mid-motion"
- **Chiburi + nōtō (victory tail)** — "side profile, sharp downward flick of the blade, then
  slow deliberate re-sheathe into the scabbard at the hip"

Harvest the side-profile window only — clips drift front-facing. Key at fuzz 42%.

## 5. What is not done here

- No sheet cells generated, no spend.
- `shin.json` carries both `martial_style` + `etiquette` keys (uncommitted); commit needs a
  SHEET_V bump only if a `web/assets/sprites/*.png` changes with it — a JSON-only metadata
  commit does not touch art.
- Executioner / Tsubasa manifests unedited pending the Shin decision.
