# s686 -- mech row S686 UNDETECTED triage

## STATE AT HANDOFF
Row re-aimed (tests only), DETECTED locally at 0c9751138 (corpus 52 fail, memfnarms 2 fail). Cloud re-run OWED: `scripts/cloudrun --owner main --kind mechrows --rows S686 --name s686`. Rulings file: none written.

## CAUSE
Case (b). Anchors resolved and the reach probe passed (reach:ok 1/1), so the plant edited live text, but zero checks failed locally (reproduced). [RUN-POS-SET] partd put `fn-every-pos` above the pair/memchr rows and narrowed `memchr_holds` from the always-true floor to `a >= 0 && b < 0`. `pair_holds` (`a>=0 && b>=0`) and `memchr_holds` are now disjoint, so swapping their order is answer-invisible. Not a coverage loss (case c): the detectors still catch the intended breakage (below).

## FIX
tests/mech/sabotages/S686_fn_rows_body_order_swapped.sh: added a second edit (SAB_FILE2/BEFORE2/AFTER2) that restores the floor semantics (`memchr_holds` returns `a >= 0`) alongside the existing swap, so the floor takes a cube again. No src/ change.

## VALIDATION
`scripts/boxlock run --label s686-mech -- bash tests/mech/run_sabotage_matrix.sh S686`: before = UNDETECTED (corpus 0/287, memfnarms 0/382); after = DETECTED (corpus 52fail/235pass, memfnarms 2fail/380pass), unexpected 0. m6read_check_sab_anchors.py: all anchors resolve.

## OWED
Cloud confirmation run (cloudrun mechrows S686).
