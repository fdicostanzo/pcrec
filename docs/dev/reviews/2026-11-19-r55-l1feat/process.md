# process.md — round r55 l1feat (code)

- 14:11 coordinator start. SUBJECT lane/l1feat = 40e2e86265c9e235280efd986942470b6884e886; BASE (assigned) = 07c840368 (lane/l1build tip).
  main at freeze 472a53fb6 (decisions.md/plan.md commit at freeze = main 472a53fb6). merge-base(main, subject) = e121371b2.
- Review tree worktrees/crit-l1feat built (nice make -j2, build/pcrec + build/pcrec-harness) ~5 min; BASE git-archive export built in $R/base.
- Kit repointed from crit-l1remodels (pc, cmp.sh, match.sh, oracle.sh, mkplant.sh) + new fuzz.py (all-start-offset differential vs libpcre2). Sanity: S3365 plant shows MISMATCH on xy(?=bc)[bc]c, subject OK.
- 30 plants built (S3365-S3383, S1925, design's feature anchors S1653 S1887 S1907 S1926-S1930 S465 S474): 29 build OK; S1927 BUILD FAILS (stale AFTER: rb_zero_into 3 args).
- m6read_check_sab_anchors.py on the review tree: STALE ANCHOR S1915 (rr_rep_split line edited by the feature); BASE: all resolve.
- 14:18 compare_l1.py run into kit/compare (91 s): 316 observed movers, 62 model, 61 agree, 252 disagreements listed. Lens dirs + findings + deliver pre-created. Lenses: sound, emitted, table, contract, check (5 opus).
- 14:19 launched 5 opus critics (sound, emitted, table, contract, check), background, unnamed, one message.
- All five returned in the launch turn (final replies undeliverable, as expected); findings files complete with CRITIC COMPLETE and lanecheck .done for all five by 14:37.
  durations: sound ~18 min (no findings), emitted ~11 min (4), table ~11 min (7), contract ~6 min (4), check ~11 min (6). No resends, no nudges, no stalls.
- 14:37-14:45 inline verification (every CONFIRMED item a one-call facts/stamp repro or quote): all HOLD; TABLE-5 item 4 left SUSPECTED.
- Freeze drift at hand-back: main still 472a53fb6; decisions.md/plan.md/span_arms.md/facts_listing.md unchanged. None.
- Draft review.md written ~14:50. Time to draft from launch: ~30 min.

## Per lens
| lens | raised | verified | top severity | overlaps |
|---|---|---|---|---|
| sound | 0 | - | - | - |
| emitted | 4 | 4 (2 re-run, 2 by reading) | speed (EMITTED-2) | EMITTED-1 with TABLE-1/CONTRACT-3 (root A); EMITTED-3 with TABLE-7 |
| table | 7 | 5 re-run/quoted, 1 suspected sub-item | design/doc | TABLE-1 = CONTRACT-3 root |
| contract | 4 | 4 | doc/design | CONTRACT-3 = TABLE-1 root |
| check | 6 | 6 | maintenance (mech/make test red) | CHECK-1/2 = coordinator C-2/C-1 |

## Process observations
- KIT DEFECT 1: mkplant.sh (inherited from r53) applied only SAB_BEFORE/SAB_AFTER, so multi-edit rows (S3382, S1653) got half plants; S3382's was a no-op. The check critic caught it and built its own. Cost: one critic plant + risk of a false UNDETECTED.
- KIT DEFECT 2: mkplant copies build/ before make, so a plant whose make FAILS still has the SUBJECT's build/pcrec; S1927's "plant" silently ran the unplanted compiler. The check critic caught it.
- Setup checks found two findings before launch (S1915 stale anchor, S1927 non-compiling plant) at ~10 min cost: worth making standard.
- The emitted lens found the round's only speed-relevant regression (lost run_pin) by diffing stamps beyond the design's mover list; the subject's own compare and the design's list watched facts only. Lens briefs for facts-layer subjects should demand a full RX_* stamp diff.
- The sound lens noted --engine=vm emits RX_VM_PREFILTER "none", so a VM-forced differential never exercises the run prefilter: the kit's fuzz.py should default to the engine selection (no --engine) and say so. It does default to none; COMMON's "both --engine=dfa and --engine=vm" wording in the sound brief steered toward forced engines.
- Staffing: 5 opus critics for a 434-line req.c change + 20 rows was right-sized; every lens produced (sound's clean result is the answer-level control). Wall time ~18 min for the whole fan-out.

## Proposed changes
1. Skill §3.2 (plants): "apply EVERY SAB_FILEn/SAB_BEFOREn/SAB_AFTERn of the row, and remove the copied build/pcrec and build/pcrec-harness before make, so a failed plant has no binary" (r55: S3382/S1653 half plants; S1927 ran the subject's compiler).
2. Skill §3.2: "in code mode, run scripts/m6read_check_sab_anchors.py on the review tree AND the BASE tree during setup, and record every plant build failure; both go into the draft as coordinator findings" (r55: CHECK-1/2 found in setup).
3. Lens table, `emitted vs replaced` row: add "for a facts-layer subject, diff EVERY emitted `#define RX_*` stamp BASE vs SUBJECT over the mover population and name each stamp outside the design's mover list; a lost pin/prefilter is a performance mover (D191 Add. 1 (b))" (r55 EMITTED-2).
4. COMMON template: "a VM-forced (`--engine=vm`) differential never reads the run prefilter (RX_VM_PREFILTER "none"); answer fuzzing of prefilter facts runs at the DEFAULT engine selection" (r55 sound's caveat).

## Framework notes
- A coordinator with a prebuilt kit (plants, compare population, answer fuzzer) let five opus critics finish in 6-18 minutes with zero resends; the kit's two defects were caught by a critic, not by the coordinator: a kit self-test (one known multi-edit row; one failing plant) belongs in setup.
- The coordinator's own setup probes (anchor check, plant builds) duplicated two critic findings: cheap independent confirmation, and a control on the check critic (it found both blind).
