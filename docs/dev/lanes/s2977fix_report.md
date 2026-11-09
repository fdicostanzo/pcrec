# s2977fix report

## Summary
Sabotage row S2977 (the region text loses its gcc target pragma) now reads DETECTED, not COMPILE-CATCH, because
the entries' region-text fact check catches it first and the compile cells are skipped (simdskip rule). Row
flipped to `SAB_EXPECT=DETECTED` (commit f01a5299f). The single-row matrix re-run is OWED (see STATE AT HANDOFF).

## The catching check
tests/memfn/targets_check.c (part 2 of tests/memfn/run_targets.sh, arm memfntargets). It compares each target
with a region: its region text must push the target's needs for gcc and clang. With the gcc target line gone the
text no longer carries the needs, and it prints (four times, once per spelling of each of the two targets):
`FAIL: target x86-64: its region pushes its needs for gcc and clang, no arch=` and the same for `x86-64-v3`.
Then `FAIL: targets_check: rc=1, 70 passing (floor 63)`; every compile cell, census, guard and artifact cell is
`SKIP ... not compiled, the facts of ... failed`. Suite figure on a hand plant (git archive copy, scratch):
checks passed 6, failed 1. So a region missing its gcc target attribute IS caught by a real fact check; no gap.

## Single-row re-run
OWED. `bash tests/mech/run_sabotage_matrix.sh S2977` (JOBS=2, niced, KEEP=1) is waiting on the box lock, which
yields to queue jobs 208/212/218 (make tests, ~40 min each). Process: boxlock pid 2020473 (label mech:S2977),
log /var/tmp/pcrec-pcrec/scratch/memfn/s2977fix/run.log. I did not PCREC_BOXLOCK_JUMP.

## Checks run
- hand plant, run_targets.sh: as above.
- tests/memfn/run_arch_blind.sh: 17 passed, 0 failed (first run caught my comment's x86 token; reworded by role).
- python3 -I scripts/m6read_check_sab_anchors.py: all anchors resolve (1198 sabotages).
- tests/mech/CLAUDE.md: S2977 removed from the COMPILE-CATCH list.

## Charter-vs-committed checklist
- flip only to the naming check, named in the row: done (Detector comment).
- row detected on single-row re-run: NOT YET (owed).
- arch_blind, anchors: done.
- report + history-index line: done.

## STATE AT HANDOFF
owed: S2977 single-row matrix run (log path above; completion line: the S2977 matrix row reading DETECTED).
