# s2afix — fixes for the ruled code review of S2a (docs/dev/reviews/2026-11-06-r8-memfn-s2a.md)

## Summary

Every FIX-NOW id of the review's Rulings section is applied on `lane/memfn-s2a`. No fix changes the seam layout, so
MF_SITE_ABI stays 24 and PCREC_ARTIFACT_ABI is untouched; 24 BASE/head compile pairs (8 patterns x default, `--engine=vm`,
`--measures=zen4-grid1@1`) are byte-identical, so no emitted pcrec byte moved. The MFMEAS digest now covers the handed
value (new row S2911, red when planted); the loader's per-format choice is one `meas_formats[]` row; the fixture floors are
exact; the spec text carries the four contract items.

## Fixes by finding id

- SEAM-1: `src/gen/memfn_sites.c` `meas_record` hashes `key TAB state TAB value_e6 TAB noise_e6 LF`;
  `tests/knowledge/ks_ref.py handed` writes the same line; `docs/design/memfn/span_cards.md` §4.2 states it;
  `tests/compound/run_part_measures.sh` (C) comment follows. Sabotage S2911.
- HOUSE-2: the record calls `pcrec_ks_fnv1a` / `pcrec_ks_fnv_basis` (the local `meas_fnv` and the literal basis are gone);
  the qsort stays, its comment says it serves the harness lever's file order.
- CHECKS-1: `tests/knowledge/mfixtures.py` pair `fx-f2-noisemax` (a noise of exactly 10^15 must load and digest apart);
  bad row `f2-noise-fitted` (a fitted row with a noise). Planting `>` -> `>=` at the noise bound goes red (1 FAIL).
- CHECKS-2: `run_measures_tests.sh` now counts bad fixtures exactly (29) and format-2 ones exactly (8, `f2-*`), pairs 3.
  Added `f2-events-bound` (events 2^63 refused) beside the spec's bound. 95 checks (was 91).
- CONTRACT-1: `docs/spec/measures.md` §2.2¶1a no longer grants `round med`; says the other cell columns are carried as text
  in both formats.
- CONTRACT-2: §2.2¶1a and the §7 row state `events` at most 9223372036854775807.
- CONTRACT-3: §4¶2a reworded to behaviour ("A reader of the set receives only its `kit.` rows that carry a value ...").
- CONTRACT-4: §7 row for a known column missing from a section that has a header (a format-1 `cells` under `format 2`),
  citing §2¶2 and §2.2¶1a.
- HOUSE-1 (+HOUSE-4, HOUSE-10): `src/core/ks_measures.c` `meas_formats[]` (digest role, cell width, cell columns, noise) read
  through `fmt_of`; the five per-format ternaries/`== 2` gates (role, width, columns, noise parse, decoded `noise_parsed`,
  events gate) use it; the digest fold widths are named (`FOLD_W1`, `FOLD_W2`); the kind row's `.item`/`.stamp` are NULL (they
  named the format-1 role and nothing reads them; the role is per set). `tests/knowledge/CLAUDE.md` count follows.
- HOUSE-5: `check_cells` extracted from `check_rows`.

## Sabotage

S2911 "fill hands value+1" (`tests/mech/sabotages/S2911_fill_hands_value_plus1.sh`, suite compound) planted by hand:
run_part_measures.sh 3 FAIL lines, reverted. S2900 re-anchored on `FOLD_W1`/`FOLD_W2` (its old anchor was HOUSE-1's text).
Every row planted by hand against its named detector and reverted (a `git checkout` of the planted file, clean tree after):
S2900 5 FAIL, S2901 5, S2902 2, S2903 g2 gate `checks failed: 1`, S2904 2, S2905 2, S2906 4, S2907 1, S2908 1, S2909 5,
S2910 3 (compile catch), S2911 3, S1232 6. A scan of every sabotage row anchored in the files this fix touched found no other
broken anchor. The matrix runner itself yielded to queued jobs, so it was stopped before planting (no row ran there).

## Validation

Light, mine, on the final tree: `make` clean; `make strict` rc 0; `make test-knowledge` 307 passed / 0 failed
(`run_measures_tests.sh` 95); `make test-codegen` 21/21 scripts; `tests/compound/run_part_measures.sh` PASS 16/0; identity
spot 24 pairs, 0 diffs vs the base build; `make test-memfn-g2` 70358660 checks, 0 failed. Not run (the manager's): make test, mech,
the gate jobs.

## Gate jobs

`/var/tmp/pcrec-pcrec/scratch/memfn/s2a/jobs/460-468` all `--dry-run` clean. Changed: `mech.sh` R3 gains S2911, so shard 3 is
24 rows (shards 24/24/24, 72 rows), `expect rows=24` follows by itself. The ident jobs (23 arms each) and the sections, test
and strict jobs keep their populations: no emitted byte moved and no new test script was added. Owed: gates 460-468
(the manager queues them).

## Charter-vs-committed checklist

| id | committed |
|---|---|
| SEAM-1 | yes: memfn_sites.c, ks_ref.py, span_cards.md §4.2, run_part_measures.sh, S2911 |
| CHECKS-1 | yes: fx-f2-noisemax pair, f2-noise-fitted bad row |
| CHECKS-2 | yes: exact 29 / 8 / 3 counts |
| CONTRACT-1 | yes: measures.md §2.2¶1a |
| CONTRACT-2 | yes: measures.md §2.2¶1a, §7 |
| CONTRACT-3 | yes: measures.md §4¶2a |
| CONTRACT-4 | yes: measures.md §7 |
| HOUSE-1 | yes: meas_formats[], named fold widths, kind row NULL |
| HOUSE-2 | yes: shared FNV, sort comment |
| HOUSE-5 | yes: check_cells |

## STATE AT HANDOFF

Complete. Owed, for the manager: gate jobs 460-468 (queue them; `mech.sh` already carries S2911). No ruling pending, no
rulings file. A fresh agent resumes from the Fixes table above; nothing else is open.
