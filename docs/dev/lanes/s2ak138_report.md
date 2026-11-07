# s2ak138 — the actual fix for K138

## Summary

The measures loader now refuses a row whose |`value_e6`| is past 10^15 at load, in the kit's exact accept range (both signs: memfn/src/compose.c refuses `> MF_MEASURE_MAX || < -MF_MEASURE_MAX`). A bad set is a clean load-time refusal instead of an internal error at every compile. Commits 535a2e78d (fix) and ebfdec1b2 (K138 marked FIXED). No emitted byte moved; no abi event.

## Changes

- `src/core/ks_measures.c` row loader: refuses `value_e6` outside +-`KS_MEAS_MAX` ("value_e6 N is past 10^15 in magnitude (refused, never clamped)"), applies to both set formats (the kit refuses either).
- Spec: measures.md §2.2¶3 states the bound (and that negative values are legal, e.g. a derived saving); §7 row "a `value_e6` of magnitude past 10^15 | §2.2¶3".
- `_Static_assert(KS_MEAS_MAX == MF_MEASURE_MAX)` added to `src/gen/memfn_sites.c` (product TU seeing both headers, so a plain `make` catches drift); the test TU `tests/knowledge/meas_store_check.c` keeps its copy; ks_measures.h comment names both and K138.
- Fixtures: `value-bound` (10^15+1) and `value-bound-neg` (-(10^15+1)) in `tests/knowledge/mfixtures.py`; `run_measures_tests.sh` floor 29 -> 31 classes (format-2 count stays 8). 97 measures checks.
- `docs/dev/known_issues.md`: K138 FIXED.

## Sabotage

S2912 (`tests/mech/sabotages/S2912_meas_value_bound_admitted.sh`): the bound test is disabled (`0 &&`). Planted by hand: 2 FAIL (value-bound, value-bound-neg), 95 pass; reverted: 97/0. Matrix run `run_sabotage_matrix.sh S2912` at ebfdec1b2: DETECTED, knowledge 2fail/307pass, 0 anomalies.

## Validation

make clean; make strict clean; run_measures_tests.sh 97/0; limits_check 39/0; `make test-knowledge` 309/0; bounded emit_sweep (150 argv, ref = 7355ea430 plain build vs this tip): movers 0, asymmetric 0 in every population. Full gate runs are owed to the queued jobs below.

## Gate jobs

Prepared, NOT queued, in /var/tmp/pcrec-pcrec/scratch/memfn/s2ak138/jobs/: 491-kit-s2a-k138-strict, 492-kit-s2a-k138-sections (14 sections incl. test-knowledge, test-registry), 493-kit-s2a-k138-mech (S2900-S2912, 13 rows). Each `--ready`: hold.sh first, 75 while kit-s2d-J9 is not green/failed/cancelled, then `after` the previous job (491 has no predecessor). Absolute paths throughout (common.sh sourced by absolute path); each dry-run from a copy in scratch/dry/: rc 0, and `--ready` returned 75 (J9 pending).

## Checklist

1. Loader bound at load, exact kit range, spec sentence + §7 row: done.
2. Static assert where both are visible (src/gen/memfn_sites.c), naming K138: done.
3. S2912 + fixtures with exact floors, red/green observed: done.
4. K138 marked FIXED naming 535a2e78d: done.
