# Kael organic circular frenzy · motion research and redraft gate

## Owner correction

The earlier procedural orbit preview is withdrawn. It kept Kael's body nearly static while disconnected white arcs all traveled in roughly one direction. Anthony wants an organic swordsman action: slicing in several directions and planes, with a blade and arm carried *behind* him by body rotation. The eight-frame redraw is rejected as connected animation because body scale, sword hands and limb anatomy changed. Swing energy may inform new keys; its frames cannot be packed.

## Evidence and interpretation

- Murase et al. measured a kendo strike with force plates, anatomical markers and markers at the sword guard/tip; the paper connects faster upswing to foot push/body travel and downswing to blade velocity and shoulder movement: https://www.jstage.jst.go.jp/article/ijshs/15/0/15_201611/_article . It studied a forward men strike, **not** a 360-degree dual-sword frenzy.
- Motion capture of eighth-dan kendo players tracked shinai, left/right shoulders and right hip as a time series: https://commons.nmu.edu/isbs/vol38/iss1/135/ . This supports inspecting connected landmarks rather than rating each pose alone; it does **not** prescribe Kael's exact choreography.
- The All Japan Kendo Federation makes basic bokuto and kata training videos available: https://www.kendo.or.jp/en/information/20201221/ . The Kendo Show has a practice-swing video: https://kendostar.com/blogs/kendostar-blog/the-kendo-show-kendo-suburi-practice-swings . Their pages were located, but video playback was not verified in this pass. Do not claim footage was watched frame by frame.
- Musashi's two-sword passage describes learning a long blade in one hand and a short blade in the other, with wide versus narrow working space: https://miyamoto-musashi.org/en/genten/gorin/chi/05/ . Kael's cinematic frenzy is a stylized game invention rather than an authentic kata.

## Kinematic model for the redraw

**Coordinate convention:** identify Kael's *anatomical* hands, not screen left/right. The art is authored in one facing and the game mirrors the whole sprite. The right glove always grips the long katana; the left glove always grips the short wakizashi. Hilt, wrist and elbow remain one attached chain on each side.

**Body path:** support foot plants → pelvis begins the turn → ribs and shoulders follow → right arm and blade accelerate → the blade tip cuts an outer route → the arm continues into an anatomically reachable rear pose → feet/pelvis redirect → shoulder brings the long blade back through a rising cut. The left arm works on a shorter, independent inside route. It covers the opening while the long blade is behind, then makes a close reverse cut. The blades never tangle or switch hands.

**Cuts:** use a front-to-side horizontal cut, a continuing rear pass, a rising reverse diagonal, a falling diagonal and a close short-blade reverse. Opposite directions must be visible in consecutive blade-tip samples. A white trail is the recent history of the *actual tip*, rendered behind or in front according to the pose. It cannot be a centered ring independent of the hands. Give long-sword sweeps a wide tail and short-sword sweeps a shorter local trail.

**Depth:** draw a clear 3/4 back or back-facing key while the long katana moves behind the torso. Occlusion is intentional: the torso can hide portions of forearm/blade, but the hidden elbow/wrist route must remain physically continuous when the weapon reappears. Rear FX draw behind the body; front FX draw over it. The visible eye, hood, scarf and clothing follow the turn without changing identity.

**Timing:** the existing Twin Cyclone lasts 380 ms and hits at approximately 0.10 and 0.20 s. Use a brief readable windup, quick alternating exposures through the cuts, then a recovery. The 12 drawing beat plan in `frame_breakdown.json` totals 380 ms as a staging target. This is **not** a gameplay timing change or proof that 12 drawings fit the current two-hit move; review against the actual combat clock before installation.

## Tracking and rejection checks

For every drawing record pelvis/root, sternum, both shoulders, both elbows, both wrists/hilts, both sword tips, knees, ankles and feet. Overlay each adjacent pair. Reject a drawing when a hilt leaves its glove, a long blade becomes the short blade, a wrist reaches the opposite arm without a drawn turn, an elbow disappears and reappears in an impossible place, the blade teleports instead of completing its rear route, or body volume/scale jumps without perspective justification. Keep the floor anchor fixed while allowing crouch and foreshortening to change the bounding box.

At game size, play the whole move at normal speed and frame-step it. Check both facings, front/rear occlusion, blade-tip continuity and return to idle. Only after body and weapon motion read should the white FX be generated from tip trajectories and reviewed for width, direction and fading. No atlas, manifest, hitbox or timing change is authorized by this research artifact.

## First exploratory rear key

`rear-pass-study-unapproved.png` tests a three-quarter back turn with an outer long blade and inner short blade. It has one visible elbow/wrist chain per arm and no FX, but its head-to-foot size is materially larger than the exact approved contact source, and anatomical hand assignment through the rear perspective has not been independently certified. Treat it as a diagnostic study, **not** an approved production frame or proof of sequence continuity. Built-in editor model identity was not reported; do not describe it as GPT Image 2.5. No external paid API was used.
