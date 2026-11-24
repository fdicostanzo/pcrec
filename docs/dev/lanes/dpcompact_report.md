# dpcompact — compact Unicode property tables behind one interface ([DATA-PLAN] A1)

STATE: built; long validation OWED (queued, keys below).

## Summary

The Unicode property tables now live behind ONE module, `src/parse/ucd_tables.{h,c}`. `generate.py` writes delta-varint interval lists plus a name blob into `src/parse/ucd_tables.inc`; only `ucd_tables.c` includes it. The old pair arrays are deleted (no second format). Every other reader moved to the interface (`pcrec_ucd_find`, `_contains`, `_row_*`, `_unicode_version`); the Python tools that regex-parsed the .inc now read `tests/uprops/ucd_dump.c`'s TSV, which goes through the same interface. A wall check (`tests/core/ucd_wall_check.sh`, in the core suite) fails if any other file names the generated file or its symbols; mech rows S3575-S3579 prove it. The compiler's output did not change (spot identity below; the full sweep is OWED).

## Format

Documented only in the header comment of `src/parse/ucd_tables.c` (the owner's constraint); `third_party/ucd-16.0.0/generate.py` is the writer (`encode_set`, `emit`). Not repeated here.

## Measurement

Before = `git archive` of the base commit 2fdbcad38 built in scratch; after = this branch; `make -j16` default flags (`-O2 -g`).

| quantity | before | after |
|---|---|---|
| property data object (`mod_uprops.o`, text+data) | 254,012 B | 85,150 B (`ucd_tables.o` 82,650 + `mod_uprops.o` 2,500) |
| interval data | 208,120 B (`pcrec_uprop_iv`, 8 B x 26,015) | 57,583 B (`ucd_iv_blob`) |
| name table | 33,216 B (`pcrec_uprop_names`, struct rows with pointers, plus relocations) | 9,419 B names + 2.8 KB x 3 row arrays + 3 KB set offsets |
| `libpcrec.a` | 15,475,760 | 15,338,982 (-136,778) |
| `build/pcrec` | 7,741,408 | 7,562,920 (-178,488) |

Compile time, NON-OFFICIAL sample (median of 20 interleaved runs, `-e utf8 --features all`, under `scripts/boxlock run`, box not otherwise quiet): `[\p{L}\p{N}\p{Greek}\p{Emoji}]+` 122.6 ms before, 120.6 ms after; `\p{L}` 39.9 / 39.6 ms; `a(b|c)+d` 4.9 / 4.9 ms. The decode is not measurable beside the compile.

Row identity: a dump of all 1,384 rows (both the normal and the `-i` set) through the interface equals the old table's rows exactly (1,384 of 1,384, both sets).

## Validation

Done by hand in the lane:
- spot byte identity, 48 cells (12 patterns incl. `\p{L}`-class mixes, `sc=`, `scx=`, `bc=`, `Block=`, `Age=`, `\p{Cs}`, `(?i)\p{Lu}`, a non-ASCII group name; x utf8/byte x `--ucp` on/off) against the base build: 0 diff.
- `make -s strict`: clean (it caught a one-byte-too-small `char` array in the first generated blob; fixed in the writer).
- `make test-plan-lint`: green. `python3 scripts/m6read_check_sab_anchors.py`: all anchors resolve (1,409 sabotages; S-U12, S1389 and S1583 were re-anchored for the moved code).
- `tests/core/ucd_wall_check.sh` solo: 3 passed (3,766 files read, control reports a planted include).
- `ENC=byte bash tests/uprops/run_uprops_tests.sh` (run before the last strict fix): `uprops: 54 passed, 0 failed`, including §1 `--check` staleness, §2 names via the dump, §3 byte-arm differential against libpcre2, and the generator's own sabotage cells.

OWED (queued, all under refuse-after-19:30 --ready gates):
- `200-dpcompact-test`: `make test` via perfrun (covers codegen, registry PC-3 which now reads the row accessors, clskit, core incl. the new wall check, uprops byte, rxtsource).
- `201-dpcompact-mech`: S3575 S3576 S3577 S3578 S3579 S-U12 S1389 S1583 (8 rows; the five new rows must read DETECTED by core).
- `202-dpcompact-sweep`: `scripts/emit_sweep.py --ref 2fdbcad38`, 0 movers required.
- `203-dpcompact-uprops-utf8`: `make test-uprops-utf8`, the whole code-point space on the utf8 encoding.

## Census (STEP 0): every reader of `uprops_tables.inc` and its symbols

| reader | what it touches | class | moves to |
|---|---|---|---|
| `src/parse/mod_uprops.c` | `#include`s the .inc; reads `pcrec_uprop_names[]`, `pcrec_uprop_iv[]`, `_names_n`, `PCREC_UPROP_NS_*`, `PCREC_UPROPS_UNICODE_VERSION`; defines `pcrec_uprops_span/_row_count/_row_name/_unicode_version` | the one in-tree format reader, mixed with the module's scanner | scanner keeps only the lookup CALL (`pcrec_ucd_find`) and the NS constants from the interface header; the accessors leave |
| `src/core/internal.h` (6501-6512) | declares the four accessors | declaration home | `src/parse/ucd_tables.h` |
| `src/parse/mod_code.c`, `mod_named_groups.c`, `mod_ucp.c` | `pcrec_uprops_span(name, &n)` | interface users already | `pcrec_ucd_find` (they gain an `Arena *`) |
| `tests/registry/pcre2_check.c` | `pcrec_uprops_row_count/_row_name/_unicode_version` | interface users already | renamed `pcrec_ucd_*` |
| `tests/clskit/ref/clsets.py`, `studies/cls_tree_study/clsets.py` | regex-parse the .inc (`pcrec_uprop_iv`, `pcrec_uprop_names`) | FORMAT READERS (the bad kind) | read a TSV dump written by `tests/uprops/ucd_dump.c`, a C program that calls the interface |
| `tests/uprops/uprops_names.py` | regex-parses NS macros, name rows, interval pool | FORMAT READER | same dump |
| `tests/uprops/run_uprops_tests.sh` | `sed`s the version macro; names the .inc in `--check` text and sabotage copy list | FORMAT READER (version) + path text | version from `ucd_dump --version`; path renamed |
| `tests/mech/sabotages/S-U12_*.sh` | anchors on the row loop in `mod_uprops.c` | anchor | re-anchored into `ucd_tables.c` |
| `Makefile` (`GEN_TABLES`) | prerequisite list | build | renamed file |
| `third_party/ucd-16.0.0/generate.py` | WRITER | the writer | writes the new format |
| docs/CLAUDE.md/README/comments naming the file | prose | prose | updated where live; frozen history left |
| `studies/linktest_probe/pcre2_check_linked.c` | frozen copy of pcre2_check.c, never built | frozen | left (noted) |

## Interface

Module `src/parse/ucd_tables.{h,c}` (layer `parse`: its callers are all in parse/ and tests; it needs `Arena` and `PcrecCpRange` from the core base tier, which is to its left). Generated data: `src/parse/ucd_tables.inc`, `#include`d by `ucd_tables.c` ONLY.

```c
#define PCREC_UCD_NS_BARE 1u ... SC 2u, SCX 4u, BC 8u, BLK 16u, AGE 32u   /* namespace bits */
const PcrecCpRange *pcrec_ucd_find(Arena *a, const char *name, size_t len,
                                   unsigned ns, bool caseless, int *n);
size_t      pcrec_ucd_row_count(void);
const char *pcrec_ucd_row_name(size_t i, unsigned *ns);
const PcrecCpRange *pcrec_ucd_row_set(Arena *a, size_t i, bool caseless, int *n);
const char *pcrec_ucd_unicode_version(void);
```

- `find`: first row whose name equals `name[0..len)` (already normalised by the caller) and whose ns mask intersects `ns`; returns that row's set (the `-i` set when `caseless`), NULL when no row. A present row with an empty set returns a non-NULL pointer with `*n == 0`.
- `row_set`: same for row `i` (NULL if out of range). Used by the test dump so no tool needs the row layout.
- Ownership: the returned array is allocated from `a` (the caller's compile arena), sorted, disjoint, non-adjacent, lives with the arena. Nothing static is handed out. Strings from `row_name` and `unicode_version` are static, immutable.
- Errors: none beyond NULL; an arena failure takes the arena's own route (`pcrec_ctx_fail`), as every `pcrec_arena_alloc` caller.
- Cost per lookup: linear name scan over 1,384 rows (same as before: length + memcmp, ~microseconds) plus a varint decode of n intervals, O(n) at roughly 2-3 ns per interval (`\p{L}` 677 intervals, ~2 us) and 8n bytes of arena. No caching: the largest caller (UCP) asks a handful of names per compile.
- The encoding (varints, offsets, name blob) is described only in the header comment of `ucd_tables.c`; `generate.py` is its writer; the generated .inc carries a consistency stamp (namespace numbers) that `_Static_assert`s against the header.

Out of scope: `fold_tables.inc` and `case_tables.inc` (different shapes; the charter's "fold links if they carry over" does not apply, they are not interval-pair pools of this kind).

## Notes for the reviewer

- The decode allocates from the compile arena on every `find`; UCP asks a handful of sets per compile, so nothing is cached (a cache would be a second mechanism without a measured need).
- `pcrec_ucd_contains` exists because `pcrec_group_name_cp` has no arena and is called per character from the subst template; it decodes with early exit and allocates nothing. `mod_code.c`'s refused-character table uses it too (it was a binary search over a static array; now a linear decode with early exit, cost not measured separately; refused sets are short).
- `studies/linktest_probe/pcre2_check_linked.c` is a frozen copy and still calls the old `pcrec_uprops_*` accessor names; it is never built. Only its one comment naming the .inc was changed.
- `tests/clskit/ref/clsets.py` is a frozen copy of the study's: both got the identical edit.
- The fold tables (`fold_tables.inc`, `case_tables.inc`, `utf8_fold_pairs.inc`) are untouched: different shapes, not in A1's scope.
- No caller-observable output moved, so no `docs/spec/` hunk. No abi bump: emitted bytes identical.

## STATE AT HANDOFF

Branch lane/dpcompact. Rulings file: empty at last read (before handback). Code and tests committed; long validation OWED by key: 200-dpcompact-test, 201-dpcompact-mech, 202-dpcompact-sweep, 203-dpcompact-uprops-utf8 (read with `scripts/monread dpcompact --wait` or `scripts/boxqueue state KEY`). A code critic round follows before landing.
