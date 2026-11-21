# cloudpop report: units missing from the cloud shard tables

## Summary
Both reds reproduced at base 0c9820cee. Axes: 1 unit dropped (`--harness=restore=look`). Mech: 26 sabotage ids
dropped, not only S3355 (S3355-S3357, S3365-S3381 and later ones from the span_arms L1 landing, up to S3501). Both
tables are regenerated with `tests/ci/cloud_reweight.sh axes|mech` (offline, committed measured files);
`make cloud-check` is now 16 passed, 0 failed. The mech population is 1371 ids over 90 shards, axes is 124 jobs and
32 passes over 20 shards, each exactly once. One row of the axes table is a hand re-instatement (see Fix).

## Cause
Axes: the look arm entered with 7e28bfd3d (2026-11-19, span_arms L1: "run_axes names the look arm"). The restore arms are
derived from walk_arms.def (40eed6973, 2026-11-15), so the word only appeared in the plan once that landing named it.
Mech: S3355 entered with be76ad164 (2026-11-19, r53 F1); S3365-S3383 with 15b9659bd (2026-11-19, span_arms L1); the rest
the same day. The last regeneration of both tables was c774d15c0 (2026-11-18). Each 2026-11-19 landing added units
and did not run `make cloud-reweight`.

## Fix
`bash tests/ci/cloud_reweight.sh axes` and `... mech` (the `reweigh` column's generator, `cloud_units_plan.py`), no hand
edits except one. The generator derives the width-arm unit as `--window-search-width=4095`, a word no `AXES=` selects
(`axes_has` matches the bare `--window-search-width`), so regeneration put the unit back into a shard that never ran
it. The row is restored by hand to the bare word, exactly as covs2g did on 2026-11-16 (its weight_source says so).
GENERATOR DEFECT, NOT FIXED (stop rule): `word_of` in `tests/ci/cloud_units_plan.py` needs a case mapping a
`--window-search-width=N` flag to the bare word. Until then every axes regeneration must repeat the hand row.
It is a second hand patch for one cause, so this wants a scope ruling from main.

## Why nothing caught it
`cloud_check.sh` runs only via `make cloud-check`, which is opt-in: it is not a TEST_SECTIONS member, not in `make test`,
and nothing in `.github/workflows/` (ci.yml, cloud-test.yml) or `scripts/cloudrun` calls it or the per-kind population
scripts (`cloud_axes_check.sh`, `cloud_mech_check.sh`). Only the `test` kind's table has a per-push gate
(`test-ci-shards` runs `check_shards.sh`). The workflow's plan job reads whatever table is committed and never counts it.
So a landing that adds a mech row or an axes arm without regenerating goes green everywhere, and the cloud runs
dispatched afterwards silently omit the unit. Cloud axes/mech verdicts since 2026-11-19 lacked these units.
Proposed smallest gate (not built): a `test-cloud-pop` section in TEST_SECTIONS running the axes and mech population
checks (both only list plans or ids, no matching), so any landing that moves a population without regenerating is red in
`make test`/CI. A cheaper alternative is a plan-job step in cloud-test.yml running the same two commands.

## Validation dispatched
`make cloud-check` 16/0 locally. Cloud mech run of S3355 via scripts/cloudrun --kind mech --rows S3355 (name
cloudpop-s3355), see STATE AT HANDOFF for the sha and the branch proof.

## STATE AT HANDOFF
Branch lane/cloudpop. Rulings file empty: no R-n applied (none). Owed: none. Open for main: the word_of generator fix
(scope ruling) and whether to build the test-cloud-pop gate.
