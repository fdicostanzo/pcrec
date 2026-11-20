# l3pin report

## Summary
S811's anchor was the only stale one on lane/l3fix's tip. It is re-aimed at the line RM-2 rewrote. `scripts/m6read_check_sab_anchors.py` now reports all anchors resolve (1367 rows, 1425 sites). `make strict` is clean. The plant run for S811 and the full `make test` are queued; neither has finished, so the plant result is OWED (see Validation queued).

## S811 re-anchor
`tests/mech/sabotages/S811_k_admission_dropped.sh`: SAB_BEFORE is now the two-line statement
`return pcrec_landmark_margin(landmark_ppm, start_ppm,` / `pcrec_bound_stated(k) && k.v > 0 ? k.v : 0) > 0;` (src/gen/emit_dfa.c, about line 9357). SAB_AFTER is unchanged (the plant returns true, so every K is admitted). A RE-ANCHORED history comment is appended. Commit 5ce6c0fd7.

## Plant check
NOT yet shown. The anchor check proves the BEFORE text resolves exactly once (SAB_COUNT 1); that the plant goes red is the mech row's job. Queued as `200-l3pin-mech` (`bash tests/mech/run_sabotage_matrix.sh S811`, dry-run validated: field validation passes, 1 row). The verdict is that row's `== mech run COMPLETE` trailer; expect DETECTED.

## Other stale anchors
None. The whole-branch tripwire (`python3 scripts/m6read_check_sab_anchors.py`, the same script test-codegen's SABANCHOR check runs) printed `all anchors resolve` after the S811 edit, so no other row needed re-aiming.

## Validation queued
- `make strict`: clean (whole tree, -Werror -Wshadow).
- `200-l3pin-mech` (S811 plant), `201-l3pin-test` (`scripts/perfrun --label l3pin --timeout 5000`, cap 5400), scripts at /var/tmp/pcrec-pcrec/scratch/l3pin/. Queued behind the held 202-k146land make test, which was not touched.

## STATE AT HANDOFF
Branch lane/l3pin at 5ce6c0fd7 plus this report. No rulings file entries applied (the file has none). OWED: the S811 mech verdict (job 200-l3pin-mech) and make test (job 201-l3pin-test).
