# ShadowClash — Soundtrack Brief (generation-ready)

Owner-requested, Aug 2 2026. One entry per track: **type** (instrumental or lyrics),
the **sounds** that belong in it, the **mood**, a **tempo** anchor, and — where sung —
**genre + vocal + what the words are about**. Grounded in the shipped stages
(STORY_BOARDS: bamboo, rooftops, warrant, snow, lantern, tollgate, temple, volcano)
and the Story Bible. House sound: **wagakki spine, modern muscle** — taiko, shamisen,
shakuhachi, koto up front; dark hybrid percussion and low synth pressure underneath.
Cel-illustration game, not pixel art — cinematic, never chiptune.

**The lyric rule:** anything that loops under a FIGHT stays instrumental — words fight
the announcer, repeat badly on loop, and date fast. Voices in-fight are TEXTURE only
(chant, vocalise, kakegoe shouts — no lyrics). Full lyrics live where the player
listens instead of fights: the story's emotional beat and the credits.
**Count: 15 instrumental · 2 with lyrics (#13, #17).**

---

## Menus & framing

**1. The Lantern Is Not Warm** — title theme
- Type: INSTRUMENTAL (texture: one distant female vocalise, wordless, far back in the mix)
- Sounds: solo shakuhachi lead, low koto drone, sub-bass pedal, sparse frame-drum pulses,
  wind and paper-lantern creak as ambience
- Mood: beautiful and wrong — the light you climb toward and shouldn't trust; serene on
  the surface, unease underneath
- Tempo: ~55 BPM, rubato phrasing

**2. Six Names, One List** — character select
- Type: INSTRUMENTAL
- Sounds: mid-tempo shamisen ostinato, tight taiko backbeat, muted electronic pulse;
  sparse arrangement, NO lead melody instrument — leave the melodic space on top
  open and empty
- Mood: appraising, dangerous-calm — reading a list of names you half-know
- Tempo: ~100 BPM
- Engine note (not prompt text): per-fighter lead stems are generated separately
  and layered by the game on hover — the bed must stay lead-less for that to work

**3. Round One, No Witnesses** — pre-fight / VS sting (~10 s)
- Type: INSTRUMENTAL
- Sounds: one massive taiko hit, real katana-draw shing, two seconds of true silence,
  then a falling drone into the stage track
- Mood: held breath; the last quiet either of them gets
- Tempo: free — it's a sting, not a loop

## Stage themes (the story climb, in order — ALL instrumental, loop-safe)

**4. Bamboo Counts the Cuts** — bamboo grove
- Type: INSTRUMENTAL
- Sounds: sparse koto and kacapi plucks like stalks knocking, shaker as leaf-rustle,
  deep space between phrases; almost no low end
- Mood: patient, watchful — a duel where the grove keeps score
- Tempo: ~70 BPM

**5. Run the Ridgeline** — rooftops
- Type: INSTRUMENTAL
- Sounds: galloping taiko, fast shamisen tremolo, breath-length flute stabs, hand-clap
  accents on the off-beat
- Mood: momentum, exposure, footwork on loose tiles at night
- Tempo: ~160 BPM

**6. Ink Still Wet** — the warrant
- Type: INSTRUMENTAL
- Sounds: low paranoid shamisen ostinato, brushed snare, clock-tick percussion,
  detuned drone that never resolves
- Mood: someone wrote a name down and everyone in earshot knows whose
- Tempo: ~95 BPM

**7. Snow Doesn't Bleed** — snow field
- Type: INSTRUMENTAL
- Sounds: high koto harmonics like ice, bowed strings, near-silent sub swells, wind;
  the quietest track in the game — leave room so the hits sound loudest
- Mood: cold, wide, still; grief that froze before it landed
- Tempo: ~60 BPM

**8. Festival for the Unmourned** — lantern district
- Type: INSTRUMENTAL (texture: crowd kakegoe shouts — "sore!", "ha!" — as rhythmic
  percussion ONLY; wordless, no sung lyrics, no other words)
- Sounds: matsuri drums, festival fue whistle, hand bells — all a half-step darker
  than they should be; celebration with a body in it
- Mood: deceptively festive; joy performed over something unresolved
- Tempo: ~130 BPM

**9. A Toll for Every Body** — tollgate
- Type: INSTRUMENTAL
- Sounds: grinding half-time drums, distorted bass pulse, iron-chain percussion,
  short stubborn horn figure
- Mood: the beat itself blocks the road — pay or turn around
- Tempo: ~85 BPM, heavy half-time feel

**10. Prayers Wear Thin** — temple
- Type: INSTRUMENTAL (texture: low monk chant, sustained syllables — not lyrics)
- Sounds: deep temple bells, singing-bowl swells, chant pads, one taiko downbeat
  that lands like karma given back
- Mood: patience running out inside a holy place
- Tempo: ~65 BPM

**11. The Mountain Keeps Receipts** — volcano
- Type: INSTRUMENTAL
- Sounds: heavy taiko battery, distorted low brass, heat-shimmer string tremolo,
  crackling ember foley in the ambience
- Mood: the climb's end short of the pit; everything owed comes due here
- Tempo: ~140 BPM

## Fighters & boss

**12. Two Swords, One Debt** — Kael
- Type: INSTRUMENTAL
- Sounds: two lead lines that never play in unison — one long phrase (katana), one
  short answer (wakizashi) — over driving taiko and a modern bass pulse
- Mood: discipline carrying a debt; inherited weight worn lightly
- Tempo: ~120 BPM

**13. What the Wire Took** — Shin & Ember, the rivalry ★ LYRICS
- Type: LYRICS — but generate an **instrumental mix too**; in-fight uses the
  instrumental, the vocal cut belongs to story beats, ending cards, and promos
- Genre: brooding alternative R&B / trip-hop ballad over East-Asian instrumentation
  (koto arpeggios, one bent string note held until it hurts, sparse 808s)
- Vocal: low male voice, restrained, close-mic — regret spoken more than sung
- Lyrics about: what the wire took and can't grow back; Shin knowing better than
  anyone what it cost Ember and staying quiet anyway — sympathy that changes nothing
  (both men, he/him — Story Bible canon)
- Mood: regret with a pulse under it
- Tempo: ~75 BPM

**14. The Pit Remembers** — Exile
- Type: INSTRUMENTAL
- Sounds: iaijutsu logic — 4-8 s stretches of near-silence (a faint low drone floor,
  never dead air), a single koto note, then EVERYTHING at once (full taiko + string
  stabs, 2-4 bars at ~140 BPM), back to the drone; cycle repeats on a bar boundary
- Mood: the calm of someone who has swept up after every loser the pit ever ate —
  she carried the invitations, knows every stair, and the eye patch is a receipt
- Tempo: drone rubato → bursts at ~140 BPM; loop the silence-strike cycle

## Results & endings

**16. Stand or Be Counted** — victory/results
- Type: INSTRUMENTAL
- Sounds: short proud brass-and-taiko figure, one shamisen flourish, clean exhale
  ending — 15-20 seconds, no loop
- Mood: won, not gloating; still breathing hard
- Tempo: ~120 BPM

**17. The Climb Behind You** — story ending / credits ★ LYRICS
- Type: LYRICS — the one full song the player sits with
- ⚠ Generation order: make #1 FIRST, then generate this one feeding #1's audio in
  as a reference/cover input so the melody genuinely reprises. If the tool can't
  take audio references, DROP the reprise wording from the prompt and treat the
  melodic callback as a post-generation arrangement task — a text prompt alone
  cannot quote a melody it has never heard.
- Genre: cinematic alt-folk ballad — koto and shakuhachi carrying the title theme's
  melody, warm strings, soft modern drums entering at the second verse
- Vocal: one voice, unforced (male or female — audition both), harmonies only on
  the final chorus
- Lyrics about: the climb now behind you — the names on the list, the pit, and the
  lantern finally allowed to feel like light; resolve the title theme's melody warm
- Mood: earned rest; the exhale after the whole story
- Tempo: ~72 BPM

---

## Production notes (all tracks)

- Loop-safe: every stage track needs a clean bar-boundary loop point (fights run long).
- Leave the 1-4 kHz band uncrowded — that's where the clash rings and whooshes live.
- KO moment ducks music hard (engine hitstop 300-360ms depending on the kill path) —
  tracks must survive a hard cut.
- Voices in-fight are texture only (chant/vocalise/kakegoe); full lyrics only on #13
  (vocal cut out-of-fight) and #17.
- Generate at least the stage tracks in both a full mix and a "-6dB percussion" alt —
  the taiko-heavy ones can mask hit_heavy's new 55Hz sub on small speakers.
