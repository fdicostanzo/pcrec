# l3pop report: L3's own sabotage rows into the cloud tables

## Summary
Premise reproduced at cc96bb7a8: `make cloud-check` 14 passed, 2 failed (axes, mech). The axes and mech shard tables
were regenerated with `tests/ci/cloud_reweight.sh axes` / `mech` exactly as cloudpop did, with the same one hand row;
`make cloud-check` is now 16 passed, 0 failed. L3's own rows run locally: all 17 rows reached (16 DETECTED, S3407 UNDETECTED
as declared). No src/ edit. Rulings file empty: no R-n.

## Dropped rows
39 mech ids in no shard: S3355-S3357, S3365-S3383, S3405-S3413, S3450, S3455, S3480-S3485 (list:
/var/tmp/pcrec-pcrec/scratch/l3dropped.txt). One axes plan job dropped: `--harness=restore=look`.

## Regenerated tables
tests/ci/cloud_axes_shards.tsv and tests/ci/cloud_mech_shards.tsv, commit 77c3cc83c. Hand row: the generator emits
`--window-search-width=4095`, which no AXES= selects; the row is the bare `--window-search-width` (taken verbatim from
lane/cloudpop 6f40233b4's axes table; the regenerated axes table differed from it in that row only). Generator defect
(`word_of` in tests/ci/cloud_units_plan.py) is cloudpop's open item, not fixed here.

## Local check of L3's own rows
Single-row `tests/mech/run_sabotage_matrix.sh ID` at 77c3cc83c, PROCS=1, nice. Rows S3465-S3469 do not exist on the
branch; S3456-S3464 neither. Every row that ran was REACHED (reach:ok(1/1)).
- DETECTED: S3405, S3406, S3408, S3410, S3411 (DETECTED-BUILD, designed compile catch), S3412, S3450, S3482, S3484, S3485.
- UNDETECTED (EXPECTED): S3407. Its row declares SAB_EXPECT=UNDETECTED (measured at landing by l3feat2: the clamp is
  defence in depth; a planted record that turns NOW DETECTED when a consumer lacks the guard). Matrix: unexpected 0.
  This is a declared survivor, not a new one; flagged because the brief names SURVIVED a STOP.
- DETECTED on the rerun (at fcf710c02, mechC.log, reach:ok(1/1) each): S3409, S3413, S3455, S3480, S3481, S3483.
All 17 rows reached; 16 DETECTED, S3407 UNDETECTED as declared.

## Validation dispatched
Cloud runs `--kind mech` and `--kind axes` on the tip sha; names l3pop-mech and l3pop-axes (see the reply to main
for the sha and the ls-remote proof). The cloud mech run covers all 6 owed rows as well.

## STATE AT HANDOFF
OWED: none to the deliverable (the cloud mech run covers every row).
The six rows first starved of the box lock were rerun and are all DETECTED. Cloud verdicts arrive as CLOUD-DONE.
Rulings: none applied. Branch lane/l3pop.
