# September 6 roster audit repairs — Shodo :9101

Working build 738. Anthony authorized the full fix list and approved the displayed repairs. This pass preserves Mokurai's expressly approved run. Changes are local and uncommitted; unrelated pending edits are preserved.

## Disposition of the 36 findings

| Finding | Result |
|---|---|
| F01 Oni run | Shared collector reads the actual contiguous run_clean row. Two valid frames; no undefined slots or idle substitution. Approved drawings preserved. |
| F02 Exile Special facing | Corrected source-facing metadata for169/170/171/173/175/176/257/258. Both-direction live routes and reviewed source-facing assertions pass. |
| F03 Executioner Special | Preserved the concurrent734 correction for329/296; confirmed by live routes. |
| F04–F05 Mizu arms/staff | Preserved concurrent737 appended complete staff drawings233/234 and their contact holds. |
| F06 Mizu thrust | Weaponless218 retired; the directional thrust now uses the intact current Medium family. |
| F07 Mizu air staff | Short-staff204 retired; intact airborne205 supplies the recovery beat. |
| F08 Mizu finish | Flat214–227 directional families retired. Thrust and spin use reviewed current textured staff poses, with existing exposure counts and combat timings. |
| F09 Shin roll | Unreadable311 retired; readable309 tuck held for that beat. |
| F10–F12 Shin legacy Special | Damaged mapped-only sneu family retired from aliases in favor of the current special1–8 family. No new attack exposed. |
| F13 Shin parry | Blunt foreign-blade288 retired; adjacent defensive287 holds that beat. |
| F14–F17 Tsubasa | Preserved prior734 head repair363, intact effect269, established evasive-flick family, and733 source-rule cleanup338. |
| F18 Ember hood hole | Appended restored crouched recoil308. |
| F19 Ember prone hood | Appended restored prone309. Preserved concurrent737 source-restored neighboring get-up310–312. |
| F20 Ember wall pole | Original anatomy retained. Painted rail is excluded at the contact plane using existing frameClear/wallContactX. A generated alternative was rejected. |
| F21 Ember throw effect | Appended clean claw-extension313 with complete silhouette and no rectangular ground effect. |
| F22 Ember low claws | Clipped294 retired; intact293 supplies the held extended rake. |
| F23 Kael guard | Cropped192 retired; complete crossed-blade196 supplies the guard. |
| F24 Mokurai Special | Clipped249–256 family retired from Special aliases; intact existing palm-charge/release170–177 substituted. Live Back+Special reaches its initial held beats. |
| F25 Mokurai source line | Narrow source-line mask on238, outside the raised fingers. |
| F26 Mokurai crouch | Entry98→99; both held slots now99. Twenty sampled held-crouch phases select the low pose. |
| F27 Mokurai run | No change: owner's explicit approval overrides the audit's gait judgment. |
| F28 Exile wall rails | Original wall poses retained; source rail removed at contact plane41. Native wall films reviewed. |
| F29 Exile overhead crop | Appended409 from restored full overhead arc. Ground-start Up+Heavy reaches409 in both directions. Air-start attacks retain their separate airborne row. |
| F30 Exile forward Special size | Applied1.25 frame scale to393–395, using head/body comparison rather than effect-envelope height. |
| F31–F32 Executioner weapons | Preserved734 intact guard mappings and complete registered thrust341. |
| F33 Oni ground impact crops | Appended674/675 clean committed sword poses. Original airhfwd664–667 untouched. |
| F34 Oni directional finish | Appended eight matching cowl/cloak/armor poses676–683. Existing ten/eight exposure tracks hold those drawings across the same attack phases. No gameplay timing or move definitions changed. |
| F35 Obsolete tools | Removed obsolete mechanics constant access, updated wall-hold and speed-trail expectations, updated authored-direction fixtures, and replaced stale blade-lock string checks with the current runnable blade-lock regression. |
| F36 Coverage | Added valid run-row assertions, actual repaired-cell reachability, held-crouch checks, and source-reviewed Special facing assertions in both directions. |

Some repairs deliberately hold an intact drawing for more than one exposure. They do not create additional animation detail, and no cross-fades or body warps were added. Style acceptance is visual judgment; tests cannot certify anatomical quality automatically.

## Verification

- 36 live roster transition scenarios: no reported failures or JavaScript errors.
- 40 targeted attack routes ×65 simulation ticks: pass; required repaired contact cells reached.
- All nine fighters: both-direction consecutive run loops and four wall visibility cases each pass.
- Direction compass: no reported failures across all nine fighters.
- Current mechanics probe: pass, including all nine roster boots.
- Run collector: all nine manifests plus1/2/4/8/10-frame row cases pass.
- Hasuji, polish, surface and stance checks pass; stance invokes the current blade-lock regression.
- Nine sheets whole. Every original HEAD RGBA cell remains byte-identical; additions are appended.
- :9101 /whoami and served index verified against this checkout. :9100 untouched.

Checks: `tools/check_run_cells.mjs`, `tools/check_audit_routes.py`, existing roster/compass/mechanics tools. Evidence is in `media/audit-fixes-20260906/`: native review boards, routes, transitions, locomotion, compass and source/packing provenance. Concurrent repairs are documented in `media/remaining-repairs-20260906/REPORT.md` and `media/mizu-ember-repairs-20260906/REPORT.md`.

## Visual review of appended art

| New art | Identity/weapon | Pose/scale | Style/silhouette | Timing/contact | Integrity |
|---|---|---|---|---|---|
| Ember308/309 | Hood, claws and eye reviewed | Crouched/prone; prior per-frame scale preserved | Shodo; hood holes filled | Received-hit/get-up poses, no attack timing change | Append-only |
| Ember313 | Complete forward claw extension | Low braced attack | Shodo; clipped ground mass removed | Existing throw track retained | Append-only |
| Exile409 | Sickle, weighted chain, hair/scarf intact | Full overhead reach, source scale comparison | Full arc, source rules absent | Reached in both ground-start Up+Heavy routes | Append-only |
| Oni674/675 | Mask, armor, sword/cape reviewed | Committed low slash | Complete silhouette without squared effect slabs | Existing ground Heavy track; air row protected | Append-only |
| Oni676–683 | Mask/cowl/cloak continuity reviewed | Crouch, aerial tuck/palm, low sweep, recovery | Textured Shodo; full limbs/cape | Existing exposure durations, held drawings explicitly reused | Append-only |

This closes the named audit findings within their stated scope. It is not an exhaustive guarantee about every archived cell, matchup, platform, audio path, or future art change. The rejected Mizu glow candidate and malformed wall redraw were not installed.
