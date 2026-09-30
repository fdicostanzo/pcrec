# admin86 report (2026-09-30, sonnet, admin/docs)

Branch `lane/admin86` from main a527ebb4.

## Delivered
1. **S189 `SAB_DOC_FIGURE` re-recorded by mechanism** (tests/mech/sabotages/S189_anchored_machine_unpruned.sh). The detector is the answer-level "N patterns DIVERGE between the unwrapped form and the search-and-filter form" check in tests/anchored/run_anchored_diff.sh; the count (1fail/6pass now, 2fail/5pass at 312612b) is incidental, and the old second red is unrecoverable (a scratch 312612b build had driver exit 125). The row's point, the green corpus arm, is kept.
2. **plan.md pointers** (each row's text read first, only stale parts changed): [K50-DD12AI-MANIFEST] now points at silentred (FINDINGS stamp explains most of it, 11/0 at slice 250, manifest untouched); [CLS-TREE] S3 MERGED, S4 + [OPT-CLSPACK] landing (land4); [OPT-CLOSURE-CTX] / [OPT-RETRY-REUSE] "DELIVERED" -> MERGED (a0886a08); [UCP] U2 MERGED, U3 twin "not a speed win", U3 awaits Frank on capability grounds.
3. **K77** filed in docs/dev/known_issues.md (INFRASTRUCTURE, K58's class): the pcrec compile budget is wall-primary and load-sensitive (`((a)|ab){4000}c` ~3 s CPU hit 20 s wall at load 13.8, lane k73tri); if it recurs, move to a CPU-primary budget as D45 does. The stale "0.38 s corpus worst case" comment in tests/lib/gen_timeout.sh is corrected to ~3 s and points at K77.

## OWED
`PROCS=2 bash tests/mech/run_sabotage_matrix.sh S189` was launched detached from this worktree (log `/tmp/admin86/s189.log`); at hand-off (~13 min in) it had printed only "-- running S189_anchored_machine_unpruned.sh --" (slower than the 5-10 min expected; scratch build under `$TMPDIR/pcrec-mech-sabotage.uCD9Nv`). Expected: `DETECTED`, `anchdiff:1fail/6pass`, `corpus:0fail/26pass`. If the reading differs, the figure text in the row must be amended (the mechanism claim stands regardless). Nothing else owed; no make test run (light lane).
