# dpcompact — compact Unicode property tables behind one interface ([DATA-PLAN] A1)

STATE: in progress (Interface note committed before the code, per the charter).

## Summary

(filled at handoff)

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
