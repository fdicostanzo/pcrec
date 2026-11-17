# formsfixh report

## Summary
Fixes review r38 findings J5 and J6 (two check gaps in R-45 plan A). No compiler or kit source changed (movers: none). Branch lane/memfn-formsfixh from lane/memfn-forms 5d2a98710.

## Fixes
- J5: tests/compound/run_shell_checks.sh section (4). The red of the `_j = 8; for (` grep now names a wrong forwarded head (CLI store or sites send off by one) or a lost reach, not "vacuous". The comment now says the comparisons check the parse only and the grep is the value check; the control row's text no longer says an off-by-one would show.
- J6: memfn/tests/g2/g2_win_gen.c counts `long_pinned_def += st == 0` directly and prints `pinned_def=`. memfn/tests/run_g2_win.sh floors that count (FLOOR_LONG_PINNED_DEF) and asserts `pinned == pinned_def + pinned_force` by equality. The subtraction is gone.
- Sabotage rows: S3310 (default counter counts every pin, 8 -> 16: equality reds), S3311 (default counter counts nothing: floor and equality red), S3312 (CLI stores n + 2: the absolute grep reds).

## Validation
- make strict rc 0; make test-compound rc 0 (17/0, 16/0, 4/0); tests/compound/run_lever_fence.sh PASS (3 checks, 4 controls).
- memfn/tests/run_g2_win.sh (the file the suite runs): 27349 passed, 0 failed; default state `pinned=16 pinned_def=8 pinned_force=8`.
- python3 -I scripts/m6read_check_sab_anchors.py: 1333 sabotages, all anchors resolve.
- tests/mech/run_sabotage_matrix.sh S3310: DETECTED (g2win 1 fail/19084 pass). S3311: DETECTED (2 fail/19083 pass). S3312: DETECTED (compound 2 fail). Logs in /var/tmp/pcrec-pcrec/scratch/memfn/formsfixh/.
- S3304 not re-run (its edit target is unchanged; its force floor is unmoved).

## STATE AT HANDOFF
Committed on lane/memfn-formsfixh. No rulings file entries applied (none present). OWED: none
