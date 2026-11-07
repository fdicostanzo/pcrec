start 11:02:34 SUBJECT=f8c513ec81d4fe3a8503b0859c742820122f3229 BASE=adb2d44b7d4d49e3b36f2920225006e6d2d847da rulings-freeze(main decisions/plan)=adb2d44b7
11:05:05 COMMON written; lenses contract(opus) seam(opus) checks(sonnet) house(sonnet)
11:14:19 all 4 critics returned in launch turn (agent ids contract a1157609, seam a36dd57b, checks ab959cae, house abd6a132)
11:07-11:13 files: house (14 tool uses, 2.7 min) 10 findings maint/doc; contract 4 doc (1 suspected D174); seam 2 (SEAM-1 MFMEAS omits value; SEAM-2 pre-existing mf_akind unchecked) + sibling/unlocks; checks 2 (bound boundary witness, floor slack). All lanecheck DONE, no nudges.
Coordinator own note: span_cards §4.5 lists src/dump/measures_dump.c as touched; it is not in the diff (decoded view lives in ks_measures.c) -> design text over-lists; NOTED.
11:14 verifier (sonnet) launched; returned in launch turn 11:19, verify.md complete (10 ids, all HOLDS), lanecheck DONE.
11:20 freeze drift: none. Draft review.md written 11:25.

## Per lens
- contract (opus): 4 raised (3 CONFIRMED doc, 1 SUSPECTED doc D174); 3 verified HOLDS; no overlap.
- seam (opus): 2 raised (SEAM-1 check/design FIX-NOW, SEAM-2 pre-existing kit PLAN) + sibling table + 4 unlocks; 2 verified; HOUSE-3 overlaps its sibling section.
- checks (sonnet): 2 raised (both test gaps, FIX-NOW); 2 verified; 12 plants all LOUD.
- house (sonnet): 10 raised (maintenance); 3 verified; 14 tool uses only (fast, reading-based).
- verifier (sonnet): 10/10 HOLDS; no REFUTED to re-run.

## Process observations
- All 5 agents returned within the launch turn (backgrounded but synchronous here); lanewatch unneeded. No nudges, no resends, no refusals.
- Pre-building BASE + SUBJECT-TRACE trees in the round dir (one coordinator build each, ~3 min) let the seam and checks lenses plant by hand (gcc one TU + ar + link) without make: 12 sabotage plants + 2 extra plants ran in ~8 min total. The hand-plant recipe in COMMON was the enabler.
- run_part_measures.sh runs make itself, so critics reproduced its (C) checks by hand; worth a PREBUILT_TRACE=DIR env hook in that script (proposed, not required).
- m6read_check_sab_anchors.py resolves its root from the main tree's scripts/, so it cannot be pointed at a review tree; the checks lens skipped it. The skill's instruction to run it "against the review tree" needs the script's path from the REVIEW tree (`python3 -I <review>/scripts/m6read_check_sab_anchors.py`).
- The lens table had no lens for "trace record as witness"; the seam lens caught SEAM-1 only because its brief named "equal records, different facts".

## Proposed changes
1. Skill §4, seam round trip lens, append: "For a record added as a witness, plant a wrong value in each NEIGHBOURING field of the struct the record describes; each must move the record (2026-11-06 s2a SEAM-1: a noise-only digest missed the handed value)."
2. Skill §3 item 2 / COMMON template: when the promise's checks include scripts that themselves run make (run_part_measures.sh), the coordinator pre-builds the needed tree variants AND COMMON gives a by-hand plant recipe (one TU, ar into a copied libpcrec.a, link) so check lenses can plant without make (s2a: 14 plants, no make).
3. Skill §4 check adequacy: "run `python3 -I <REVIEW TREE>/scripts/m6read_check_sab_anchors.py`" (the script roots itself at its own location).

## Framework notes
- A small code unit (35 files, zero movers) took 23 minutes freeze-to-draft with 4 critics + 1 verifier, all coordinator-side; the manager context saw nothing. The pattern fits code units well when the coordinator pre-builds all variants critics need.
