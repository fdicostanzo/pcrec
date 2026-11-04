# smallfix1 report

## Fixes
1. [TMP-PRUNE-REF] done: `scripts/tmpdir.sh` pcrec_tmp_prune skips `$root/ref` by name. `scripts/tests/tmpdir.sh.test` (fake root under a mktemp dir) plants an old `ref` and old other children; `ref` survives, the others go. 15 passed, 0 failed.
2. [MECH-VALIDATE-VERDICT] done, premise partly stale: a VALIDATE_ONLY run already ended with `== mech FIELD VALIDATION COMPLETE: N definition(s) valid, 0 rows measured` (never the `mech run COMPLETE` trailer) since 2026-08-25. Added `mode=VALIDATE_ONLY` to that line (`tests/mech/run_sabotage_matrix.sh`, `bash -n` ok). Readers: only the BOILERPLATE job template's sed `\([0-9]*\) def.*`, unaffected; scripts/verdict, queuewatch, watchrun match only `mech run COMPLETE`.
3. [LANDMARK-DOC-CITE] done: `lib/pcrec.h` comment now says tuning.md §2.54 (verified: 2.54 is `-fno-landmark-walk`). No pin hashes the header (recursion identity FILEPIN compares generated output of a pinned commit; registry check reads symbols). `make strict` green; `tests/registry/axes_registry_check.sh` 245 passed, 0 failed.
4. [BOXQUEUE-READY-GUARD] done (about 9 changed lines): `boxqueue add` greps the script text for `--ready` and REFUSES (65) without it, never calling the script. Case added to `scripts/tests/boxqueue.test` (refused, nothing pending, the job body never ran).

All four rows moved to docs/dev/plan_completed.md (plan_lint requires finished rows to leave plan.md); `scripts/plan_lint.sh`: 0 violations.

## STATE AT HANDOFF
Branch lane/smallfix1 committed. Rulings file was empty (no entries applied). Validation run: make strict, tmpdir self-test, registry check, plan_lint. boxqueue.test full run was started in the background; see handback message for its result.
