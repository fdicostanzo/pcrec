# dpfix — review r97's FIX-NOW items on the compact Unicode tables (branch lane/dpcompact)

STATE: built; long validation OWED (queued, keys below).

## Summary

All twelve FIX-NOW items the manager accepted are applied (RULED section appended to docs/dev/reviews/2026-11-24-r97-dpcompact.md). The cost regressions are gone: group-name compile is within noise of BASE and a 4,000-item `\p{L}` class peaks at BASE's memory. The wall check is rewritten (needle derived, docs/ scanned, population floor, whole-pipeline control) and six new mech rows plant shapes the old needle did not contain. No emitted byte moved (the 4,000-item and 80-name witnesses differ from BASE only in the generated file's own name).

## Fixes

- IDENTITY-1 + MOD-7: one private row lookup (`ucd_row_find`) and one interval cursor (`UcdCur`) in `ucd_tables.c`; find/row_set/contains are short callers. `contains` binary-searches a SEARCH CHECKPOINT index (one per 32 intervals: `ucd_set_ck`, `ucd_ck_lo/off/prev`, written by `generate.py`'s `encode_set`, described only in the module's header) and decodes at most one stride. Cost: +10 KB of data.
- IDENTITY-2: `pcrec_ucd_exists` (no decode) answers the probe; the decode happens inside `uprops_produce`, into a scratch arena freed right after the class constructor copies it.
- MOD-2: header states one-row-per-(name, ns bit), one-bit `ns`; `generate.py` asserts it. MOD-1: `k53()` filters `ns & 1` in the study and the frozen copy. MOD-6: `pcre2_check.c` uses `PCREC_UCD_NS_*`.
- MOD-8: (1)-(6) comments and `UCD_GEN_NSETS` (dropped) fixed; (7) the study's comment hunk reverted (and the file allow-listed in the wall as a frozen user of the retired interface); (8) study README/CLAUDE.md; (9) the clsets default that ran an unbuilt `build/ucd_dump` removed (`$UCD_DUMP` required, both copies); (10) encoding_data_layout.md B1; data_plan/CLAUDE.md's formats.py line. CHECKS-6: counts 747 sets / 1,384 rows in populations.py and both clsets.py. CHECKS-5: S-U12 expects `#define RX_REQ_BYTE "183"` (present with the Script_Extensions member U+00B7, absent for `sc=`).
- W-1..W-3: `tests/core/ucd_wall_check.py` (the .sh now wraps it). Needle = the product's own `ucd_*`/`UCD_GEN_*` identifiers + the module's static functions and `Ucd*` typedefs + the generated name from the module's include line; retired names a short hand list; adjacent string literals joined; backslash splices joined; Makefile include/GEN_TABLES line rules; non-comment `ucd_tables.c` mentions; `*.inc` glob; every non-prose file wherever it lives; floor = ALL non-prose files under src/lib/cli counted from `git ls-files`; control re-runs the whole list with an overlay. Of the review's 7 bypasses 5 are caught (Makefile include, firstword, splice, macro-built include via adjacent literals, include of ucd_tables.c plus ucd_decode); the rest are listed in the header as out of reach (run-time path assembly / non-adjacent macro pieces, a from-scratch decoder, a second product under a new name). New rows S3587-S3592 (splice, Makefile include, macro include, include of the module .c, docs/ code file, retired symbol): all six flag exactly their planted file in a dry overlay run.
- W-4 filed as plan row [CASE-TABLES-WALL] (Backlog). Charter wording (data_plan.md A1-compact) now carries the measured figures.

## Measurement

BASE = `git archive 2fdbcad38` built in scratch; SUBJECT = this tree; `perf stat -e instructions:u`, `-e utf8 --features named-groups`, 80 groups `(?<a` + U+1FBF9 x29 + 3 ASCII digits`>x)`.

| witness | BASE | before fix (r97) | after |
|---|---|---|---|
| 80 non-ASCII group names, instructions:u | 431.05M | 471.4M (+9.2%; 1.077 per the review) | 431.65M (+0.14%, runs 431.63-431.67M vs BASE 431.03-431.07M) |
| 4,000 `\p{L}` in a class, peak RSS | 78.1 MB | 99.9 MB | 77.7 MB |
| `ucd_tables.o` size | 82,650 B (before checkpoints) | | 92,786 B |
| `libpcrec.a` / `build/pcrec` | 15,475,760 / 7,741,408 (BASE) | | 15,354,130 / 7,577,824 |

`contains` checked against decoded sets at every interval's lo-1, lo, mid, hi, hi+1 plus 0 and 0x10FFFF for every bare-namespace row: 171,129 checks, 0 mismatches (the review's exhaustive full-range run was not repeated).

## Validation

Run here: `make -s strict` clean; `python3 scripts/m6read_check_sab_anchors.py` 1,415 rows, all anchors resolve; `generate.py --check` green; `tests/core/run_core_tests.sh` 9 checks, 0 failed (wall: 4 sub-checks, 6,100 files read, 139 under src/lib/cli); the six new rows flagged in an overlay run; `scripts/plan_lint.sh` 0 violations.
OWED (queued, refuse-after-19:30): `200-dpfix-test` (make test), `201-dpfix-mech` (S3575-S3579 S3587-S3592 S-U12 S1389 S1583), `202-dpfix-sweep` (emit_sweep vs 2fdbcad38, 0 movers).

## STATE AT HANDOFF

Branch lane/dpcompact, committed. Rulings file empty at last read. Old dpcompact jobs (`200-dpcompact-test` running, `201-dpcompact-mech`, `202-dpcompact-sweep` pending) read THIS tree and are superseded by the dpfix keys; the manager should cancel them. A code critic round on the fixes follows before landing.
OWED: 200-dpfix-test 201-dpfix-mech 202-dpfix-sweep
