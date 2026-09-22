# ShadowClash Launch Messaging Package

**Prepared by:** Hermes (Marketing)  
**Issue:** SSG-386  
**Date:** 2026-07-16  
**Status:** Internal draft — not for public posting  
**Handoff target:** Imhotep (Tech Lead) for review

---

## 1. One-sentence positioning & target player

> **ShadowClash is a lightning-fast 2D ninja brawler for two players on one screen, where every hit could be a decoy and the only thing sharper than your blade is your read.**

**Target player:** Competitive couch gamers aged 13–35 who love the tight feel of platform fighters (Hollow Knight, Skullgirls, Super Smash Bros.) and want a 60-second duel they can settle on a phone, tablet, or laptop with a friend.

**Key differentiators (public-safe):**
- One-on-one local multiplayer — no matchmaking, no latency, no excuses.
- Six playable elemental ninjas, each with a distinct weapon and special move.
- “Kawarimi” substitution mechanic: vanish in a puff of smoke, leave a log, and punish greed.
- Simple 3-button combat (Light / Heavy / Special) with a hold-to-block defensive layer.
- 60–90 second rounds, best-of-3 matches, designed for short-session play.
- Full phone + tablet + desktop controls with Capacitor-wrapped native builds in progress.

---

## 2. App Store & Google Play descriptions

### Short description (App Store: 30 char guideline; use shortest variant)
**1-line:** 2P ninja brawler. Read, feint, strike.

### Short description (Google Play: 80 char max)
**80-char:** A fast local 2P ninja brawler. Six elemental ninjas, one screen, outplay your friend.

### Long description (App Store / Google Play, ~500–700 chars)

**ShadowClash** turns one screen into a ninja battleground. Pick from six elemental fighters — Kaze, Hibana, Mizu, Tsuchi, Kaminari, and Kage — each with their own weapon, playstyle, and chakra-powered special. No online matchmaking. No gacha. Just you, a friend, and 60 seconds to prove who’s faster.

Combat is built for couch play: Light, Heavy, and Special attacks chain into combos, while a well-timed block and the ninja substitution technique can flip a losing exchange into a brutal punish. The controls are simple enough to learn in one round, deep enough to argue about rematches all night.

Features:
• Six playable ninjas with distinct weapons and specials
• Local 2-player versus on one device
• Fast best-of-3 rounds, perfect for quick sessions
• Phone, tablet, and desktop control schemes
• No ads, no paid currencies, no energy timers

Grab a controller or split the keyboard — the duel starts now.

*(Keywords embedded: ninja brawler, 2 player fighting game, local multiplayer, platform fighter, anime fighting game, couch co-op, ninja game.)*

---

## 3. Feature bullets — six public ninjas only

| Ninja | Element | Weapon | One-line pitch | Signature feel |
|-------|---------|--------|----------------|----------------|
| Kaze | Wind | Katana | The balanced bamboo-blade all-rounder | Fast slashes, wind gust knockback, easy to learn |
| Hibana | Fire | Flame blades | Glass-cannon rushdown | Low health, high damage, burst fire offense |
| Mizu | Water | Bo staff | Sustained support fighter | Healing mist, fluid reach, outlasts trades |
| Tsuchi | Earth | Boulder / hammer | Walking fortress | Highest health, slowest speed, armor and throws |
| Kaminari | Thunder | Lightning swords | Blink-and-you-miss assassin | Fastest speed, teleport strike, storm super |
| Kage | Shadow | Claws / shadow blades | Fragile executioner | Highest damage, lowest defense, shadow dance invulnerability |

**Public feature bullets (for store, press, or social):**
- Six ninjas, six elements, six ways to fight.
- Local 2-player versus on the same screen — no internet required.
- Light → Heavy → Special chains, blocks, and substitution escapes.
- 60–90 second rounds, best-of-3 duels.
- Cross-device: play on phone, tablet, or desktop with the same build.
- Clean, readable pixel art and chibi ninja roster.

---

## 4. Seven-day launch content calendar

**Assumption:** launch when the production-art pass is approved and the build is App-Store-ready. This calendar is sized for a zero-budget, organic-launch week.

| Day | Channel / action | Content |
|-----|-------------------|---------|
| **Day -1 (pre-launch)** | Internal | Final build QA, screenshots finalized, store metadata submitted, App Store/Google Play review window started. |
| **Day 1 — Launch** | Personal TikTok / YouTube Shorts | 15-second “ROUND 1 → FIGHT!” clip. Show the six-character select, one flash combo, and a Kawarimi escape. Caption: “local 2P ninja brawler is live.” |
| **Day 2** | TikTok / Shorts | Character spotlight #1: Kaminari teleport strike. 10s loop. Hook: “fastest ninja in the game.” |
| **Day 3** | Twitter/X + Instagram Story | Animated GIF of the six select portraits. Copy: “Which ninja are you picking first?” Poll in Story. |
| **Day 4** | TikTok / Shorts | Character spotlight #2: Tsuchi — “he can’t run, but he also won’t die.” Wall-cling / armor clip. |
| **Day 5** | Reddit-style thread / X | “How we made a 2P ninja brawler that fits on a phone” (no Reddit posting per owner; use X thread instead). Show before/after procedural doll → real art. |
| **Day 6** | TikTok / Shorts | “Kawarimi explained in 15 seconds.” Show the log decoy, the reappear, the punish. |
| **Day 7** | Wrap-up + call to action | “First week recap + patch notes preview.” Ask for rating/review, share best clip. |

**Posting cadence:**
- TikTok personal account: 1–2 Shorts/day during launch week.
- YouTube Shorts: 1/day (reuse TikTok clips).
- X/Twitter: 1 text/thread post per day.
- Instagram Stories: 1–2/day for polls / behind-the-scenes.

**No paid spend.** No influencer outreach until organic clips show traction. No brand-account activity until personal channels cross 1K subs (owner’s standing strategy).

---

## 5. Asset checklist

### 5.1 Store listing assets

| Asset | Spec | Status | Owner / blocker |
|-------|------|--------|-----------------|
| App icon | iOS 1024×1024, Android 512×512, adaptive icon | **NOT READY** | Needs graphic design pass; no icon file found |
| Feature graphic (Google Play) | 1024×500 | **NOT READY** | Blocked on icon + key art |
| Screenshots — iPhone | 6.5" + 5.5" App Store required sizes, 3–10 screenshots | **NOT READY** | Capture from live match after UI/controls finalized |
| Screenshots — iPad | 12.9" + 11" required sizes | **NOT READY** | Same as iPhone |
| Screenshots — Android | 16:9 phone + 7" tablet + 10" tablet | **NOT READY** | Same as iPhone |
| App preview video (iOS) | 15–30s, device-captured gameplay | **NOT READY** | Optional but recommended; needs clean UI build |
| Store description | See section 2 | **DRAFT READY** | Hermes |
| Keywords / tags | ninja brawler, local multiplayer, 2P fighter, etc. | **DRAFT READY** | Hermes |

### 5.2 In-game / trailer assets

| Asset | Notes | Status |
|-------|-------|--------|
| 6-character select portraits | Art in `web/assets/ninjas/`; verified in build | **READY** |
| 6 full sprite sheets (20–36 cells each) | Art in `web/assets/sprites/`; production pass in progress | **IN PROGRESS — gated on owner decisions** |
| Title screen / logo | Not found in repo; likely placeholder | **NOT READY** |
| Stage / arena backgrounds | Current build has at least one arena; needs polish pass | **NOT READY** |
| Sound effects | PR #18 shipped 13 synthesized WebAudio SFX; not human-verified | **IN PROGRESS** |
| Music / trailer audio | Not identified; likely placeholder | **NOT READY** |
| “FIGHT!” / “KO” / “ROUND N” UI cards | Implemented in build; may need art pass | **IN PROGRESS** |
| Pause menu | Implemented; needs final screenshot | **READY** |
| Touch control overlay (phone/tablet) | Implemented in `web/index.html`; needs device capture | **IN PROGRESS** |
| Settings / control-remapping screen | Exists; needs final screenshot | **IN PROGRESS** |

### 5.3 Web / support pages

| Page | Notes | Status |
|------|-------|--------|
| Privacy policy | Required for App Store/Google Play | **NOT READY** |
| Support / contact page | WildComiks site already has support infra; can adapt | **NOT READY** |
| Press kit | One-page PDF with key art, fact sheet, GIFs | **NOT READY** |
| Social link landing | Linktree / bio page for TikTok/X/YouTube | **NOT READY** |

---

## 6. Launch blockers ranked by severity

**Severity scale:** P0 = cannot ship without; P1 = should fix before launch; P2 = polish / can patch post-launch.

### P0 — Hard blockers

| # | Blocker | Why it blocks | Suggested next step |
|---|---------|---------------|---------------------|
| 1 | **Production sprite art pass not approved** | Owner explicitly gated art pass on 5 pending decisions in `docs/AUDIT-2026-07-16.md`; visual presentation is a launch surface | Owner rules on decisions 1–5; then Claude-led art/animation branches land |
| 2 | **No app icon or feature graphic** | Cannot submit to App Store/Google Play without these | Design/create icon; derive feature graphic from key art |
| 3 | **No privacy policy** | Required for store submission; no store page found | Draft one-page privacy policy (no analytics, no login, local-only play) |
| 4 | **App Store / Google Play developer accounts** | Owner must enroll ($99 Apple, $25 Google); cannot be done by agents | Owner confirms enrollment status / creates accounts |

### P1 — Strongly recommended before launch

| # | Blocker | Why it matters | Suggested next step |
|---|---------|--------------|---------------------|
| 5 | **Phantom-slash live bug** | `pendingSlash` not cleared in `takeDamage` can spawn a weapon streak while the attacker is stunned (`docs/AUDIT-2026-07-16.md`) | One-line fix: clear `pendingSlash` in `takeDamage`; verify in match |
| 6 | **SFX not human-verified** | PR #18 shipped synthesized sounds; owner or QA should hear them | Play a match with audio; adjust volumes if needed |
| 7 | **No store screenshots across devices** | Store listings need iPhone/iPad/Android form factors | Capture clean screenshots after UI finalization |
| 8 | **Title screen / logo** | First impression; current build may use placeholder | Create logo lockup + title screen art |
| 9 | **Capacitor iOS/Android build verification** | Mobile launch requires native wrapper actually builds | Run `npm run build:mobile`, `npx cap open ios/android`, smoke on device |
| 10 | **Offline vendor CDN** | Current `web/index.html` loads Tailwind/FontAwesome from CDN; Capacitor app needs offline assets | Vendor the 3 CDN deps locally (owner’s Phase C plan) |

### P2 — Post-launch polish / nice-to-have

| # | Item | Why it helps | Suggested next step |
|---|------|--------------|---------------------|
| 11 | **Arcade / solo mode** | Phase B roadmap; gives single-player reason to play | Build after launch if resources allow |
| 12 | **Trailer video** | Boosts store conversion and social reach | Capture 30s gameplay montage after art final |
| 13 | **Press kit** | Enables organic press coverage | One-page fact sheet + 3 GIFs |
| 14 | **Leaderboard / achievements** | Increases retention; not in current scope | Post-launch feature |
| 15 | **Localization** | English only today; expands addressable market | Translate store copy + strings after English launch stable |

---

## 7. What is NOT in this package

- No private-roster names, stats, IDs, or portraits — public build only per `AGENTS.md`.
- No pricing, monetization, or live-service plan (current build is premium/paid).
- No external posts, messages, or accounts were touched.
- No money spent.

---

## 8. Next action

Hand this package to **Imhotep** for review. After review, the fastest path to launch is:

1. Owner rules on the 5 audit decisions → art/animation production pass begins.
2. Fix the P0 blockers (icon, privacy policy, developer accounts).
3. Land the P1 fixes (phantom-slash, SFX check, screenshots, mobile build verification).
4. Capture trailer/screenshots and submit store listings.

---

*End of package.*
