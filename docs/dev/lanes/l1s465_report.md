# l1s465 report

## Summary
Sabotage row S465 was ANOMALY (BUILD-FAILED) in mech job 202-l1ffix. Fixed; the row is now DETECTED with 0 anomalies.

## Cause
Compile failure, not anchor drift. l1ffix r55 fix A gave `rr_cat` a fourth parameter (`RbSet *set`). S465's SAB_AFTER still called `rr_cat(w, rr_none(1), acc->runs)` with three arguments, so the planted tree did not build.

## Fix
tests/mech/sabotages/S465_width_counts_characters.sh: SAB_AFTER now passes `NULL` as the set, the same form as the other no-set calls in src/facts/req.c. Witness, description and expectation are unchanged; the plant still counts a wide class as one byte.

## Validation
- `python3 -I scripts/m6read_check_sab_anchors.py`: 1329 sabotages (1384 anchor sites), all anchors resolve. No other stale anchor.
- `bash tests/mech/run_sabotage_matrix.sh S465`: DETECTED (pop 1, reach ok, corpus 50 fail, prechecks 14 fail); unexpected 0, undetected 0, unreached 0, anomalies 0.

## STATE AT HANDOFF
Committed on lane/l1s465. Rulings file had no entries to apply. Nothing owed.
OWED: none
