# grow5 report: the growth sweep's last cells

Lane grow5 (sonnet), branch lane/grow5 off lane/grow4 a4ea79855. Rulings file: empty, no R-n applied. No `src/` edit.
Premise test (passed): at the base the `empty`/`inl` rows were absent from cells.tsv and the 13 `compile:norun` cells carried
no exception name. Rulings applied: growth-compile-cells, limit-test-criteria, limit-cell-matcher-cost and the MANAGER line on
empty/inl (docs/design/plan_row_bodies/GROWTH-SWEEP.md).

## Summary

- Counts (`run_growth.py --list`): 1,594 cells = 696 limit + 898 stability (grow4: 1,398 = 599 + 799): +97 limit, +99 stability.
  696 pairs; 106 unpaired cells (was 196).
- New: 5 shipped-cap limit/stability pairs (cells.tsv), 92 `+` pairs (plus_edges.tsv), 2 red K156 stability cells; the 13
  compile-only cells are now NAMED exceptions (13 under `limit-cell-matcher-cost`, plus 92 under a second name, see below).
- Findings for the manager: (1) the 92 `+` edge limit cells also sit at the NFA-state / VM-node edge, so their matcher
  build is as costly as the 13 and they are compile-only under a second exception name (OWNER TO CONFIRM); (2) at the SHIPPED
  caps `empty`/`inl` ARE refused (the emit-code cap), so K156 exists only once the emit caps are lifted; (3) eight of the
  13 NFA/VM families have no buildable shipped-cap edge (K148 crash, K150 memory); (4) K155's stack reaches
  `target_headers_render`.

## Size-limit edge cells

Limits found in src/core/limits.def / docs/spec/limits.md section 8.1: PCREC_MAX_VM_EMIT_CODE_BYTES (500,000, code bytes)
and PCREC_MAX_EMIT_BYTES (1,000,000, whole artifact), both at their shipped defaults (`raise 0`). Each family's edge was
bisected on the default build with `growth_driver one` (a main() in the artifact counts toward the cap, as grow4 found; the
stability twin has none and is the first n refused without it). Scratch scripts: `$PCREC_TMPDIR/scratch/grow5/bis.py`, `scan.py`.

| cell pair (cells.tsv) | limit | limit cell n | stability twin n | note |
|---|---|---|---|---|
| alt_lit (existing) | PCREC_MAX_VM_EMIT_CODE_BYTES | 70657 | 70773 | refused at 500,007 / 500,001 bytes |
| alt_cap_emit | PCREC_MAX_VM_EMIT_CODE_BYTES | 799 | 802 | `({i}x)|...`; with main 800 is refused at 500,038 |
| cat_grp_emit | PCREC_MAX_VM_EMIT_CODE_BYTES | 1007 | 1009 | `(a)` x n; twin refused at 500,480 (n=1008 with main) |
| named_emit | PCREC_MAX_VM_EMIT_CODE_BYTES | 990 | 993 | `(?<n{i}>a)` x n |
| lit_ship | PCREC_MAX_NFA_STATES | 131069 | 131070 | shipped caps reach the NFA edge; the C is 428 KB and the matcher runs |
| anchors_ship | PCREC_MAX_NFA_STATES | 131070 | 131071 | `^` x n + `a`; 288 KB of C, the matcher runs |

All five new pairs, and alt_lit, run their matcher on the three subjects (spine family run: 197 passed, 0 failed).
Families with NO shipped-cap edge cell (a FINDING each, not a re-size):
- z_b, z_look, z_nlook, z_lookb, z_cilook: K148 SIGSEGV on the budget thread somewhere between n=8,000 (compiles) and 16,000
  at the SHIPPED caps, before the emit cap refuses; a size-limit edge cell cannot exist until K148 is fixed.
- z_cls, cat_ncgrp, uni: compile at 4,000 but exceed the 3 GB RSS bound by 8,000 (K150's quadratic memory, the same shape as
  the lm_* families), and the emit cap needs about 8,000 to bind; no "just before" cell.
- PCREC_MAX_EMIT_BYTES (whole artifact): no family tried reaches it before the code cap (a 150,000-word alternation is
  refused by the code cap at 1.55 MB; at 40,000 words the artifact is 413 KB with 405 KB of code). Not covered; a
  table-dominated family would have to be found first.

## Compile-only exceptions

`compile:norun` is now `compile:norun=NAME`, NAME a key of NORUN_EXCEPTIONS in run_growth.py; an unnamed one exits with a
table error (verified by the loader check); the summary prints the count per name and `--list` prints each reason.
- `limit-cell-matcher-cost` (owner ruling of 2026-11-21): the 13 NFA-state / VM-node edge limit cells (z_b, z_look,
  z_nlook, z_lookb, z_cilook, z_cls, lit, cat_ncgrp, anchors, uni, alt_cap, cat_grp, named). Reason: size limits lifted
  (`raise 1`), about 25 MB of C, gcc -O0 about 10 min and 3.4 GB. Count printed: 13 (spine run).
- `plus-edge-matcher-cost` (NEW, my extension; OWNER TO CONFIRM): the 92 matrix `+` edge cells. Measured: the first
  `--sample 20` run (box load about 10) had 14 of its `+` limit cells TIMEOUT in the gcc matcher build at the 180 s wall
  (their edge is the same 131,072-state edge, depth 12 to 15); with the exception the same sample passed (440 runs, 0
  failed). If the owner prefers a matcher run there, the options are a larger wall or a smaller C, neither built.

## K156 cells

`spine/empty@1000000` (`(?:)` x 1,000,000, a 4 MB pattern) and `spine/inl@1000000` (`(?i)(?-i)` x 1,000,000, 9 MB): kind
stability, raise 1, expect `refuse:pattern too large`, limit `none (K156)`, red `K156:compiled` (a new red kind: the
stability cell COMPILED). Why that size: 1,000,000 units is 7.6 x PCREC_MAX_NFA_STATES (131,072), a limit these units never
count (they add no NFA state), and it is large enough that any pattern-length or unit limit should have bound it long before.
Measured (growth_driver one, raise 1): `(?:)` x 400,000 0.89 s wall 120 MB RSS; x 1,000,000 0.42 s 292 MB (5.0 MB of C);
x 2,000,000 0.81 s 590 MB; `(?i)(?-i)` x 1,000,000 1.06 s 596 MB (11.0 MB of C); no named limit refuses.
CORRECTION to the premise: at the SHIPPED caps (`raise 0`) `(?:)` x 400,000 is refused ("2014582 bytes of emitted code (limit
500000)"), so a default user is bounded; K156 is that nothing counts the units once the emit caps are raised. Both spine run
verdicts: KNOWN-RED (K156, compiled), no failure. K156 is filed in docs/dev/known_issues.md; plan row [K156-NO-REPEAT-LIMIT]
(trigger: the next limits.def change or a pattern-length limit design); `python3 scripts/plan_lint.py` 0 violations.

## Plus-quantifier pairs

Method: each of the 92 matrix `+` cells (8 kinds x 4 positions x 3 cores, minus 4 lookbehind-bref) was bisected on its nest
depth (emit caps lifted as in the matrix cells; a main() in the artifact) for the deepest depth E that compiles; E + 1 is
refused. Result (`tests/growth/plus_edges.tsv`, one row per cell): E = 12 for 4 cells, 13 for 12, 14 for 47, 15 for 29. The
edge does NOT depend on the family alone: it depends on construct kind (atomic, the lookarounds and lookbehind sit 1 to 3
levels below group/ncgroup/named/inline), on position (first/second/last sit 0 to 2 below sole) and on core (litalt one below
lit); the limit that fires is NFA states (`NFA exceeds`, kinds group, ncgroup, named, atomic, inline with lit/litalt cores) or
VM nodes (`VM exceeds`: every bref core and every lookaround kind). So every cell has its own row, not a per-family value.
Each row makes a limit cell at E (compile-only, `plus-edge-matcher-cost`), a stability cell at E + 1, and the existing
matrix@250 cell becomes the same pair's far-past stability member (matrix/ID+). The @250 refusal is either the edge
limit's text or its sibling's, "nested bounded repeats would replicate" (PCREC_MAX_VM_REPLICATION_PRODUCT, a literal
alias of PCREC_MAX_VM_NODES): the first sample run failed 10 @250 cells on that text, so the @250 cell accepts both; the
pair names the edge limit.
Pairing result: 696 pairs (was 691); unpaired 106 of the previous 196: 92 are the `+` @251 cells (the depth limit has no
limit-test half for `+`, since no `+` nest compiles at 250: a different pairing does not exist), 12 are the old
non-matrix stability cells (spine/cnt_past x2, memory/cnt_nest, calls_past x3, calls_big x2, lm_cat/lm_cls/lm_alt2/lm_alt2_k150
x4), and 2 are the K156 cells (no limit exists to pair). All 92 `+` @250 cells are paired now.
Cost: the slowest edge compile measured is ncgroup.plus.first.lit@15, 112 s (box load about 10), against a 180 s wall:
margin 1.6 x; the `first` position at depth 15 is the one to watch.

## K155 stack

Re-run: `--lib --only depth` on an ASan+LSan build of this tree (the `make asan` flags, `build-asan/`, BUILD_DIR), with
`ASAN_OPTIONS=detect_leaks=1:allocator_may_return_null=1:fast_unwind_on_malloc=0:malloc_context_size=30` and the heap-cap
wrapper: still red, SUMMARY "32768 byte(s) leaked in 1 allocation(s)", and the 14-frame stack REACHES
`target_headers_render` (src/gen/memfn_stamps.c:363) under `pcrec_memfn_stamps_render` (:405), `compile_driver`
(src/core/compile.c:3427), `pcrec_compile` (:3777), via `pcrec_sb_printf`/`sb_grow` (src/core/sb.c:432/33) and the harness's
`__wrap_realloc`. The full stack is in docs/dev/known_issues.md K155. (Log: `$PCREC_TMPDIR/scratch/grow5/k155.log`.)

## Runs

- `make test-stackdepth`: 78 + 5 checks passed, 0 failed.
- `--only spine` (default ladder): 197 passed, 0 failed, 7 known-red (5 K148 CRASH, 2 K156 compiled).
- `--only memory,depth`: depth 330 passed; memory 65 passed, 0 failed, 3 known-red (K150 lm_alt2_k150, K151 calls_big x2).
- Matrix `--sample 20` (now also adds 10 extra `+` ids): 88 cells, 30 ids, 14 `+` pairs (56 cells); 440 runs passed, 0 failed;
  `--selftest` all four cases as written; `python3 scripts/plan_lint.py` 0 violations.
- Not run: the full sweep, the library stage beyond the K155 depth run (the cloud kind does them), `make test`.

## Validation dispatched

Cloud `make test`: name grow5-test, explicit sha (see the handback message). Nothing queued on the box.

## STATE AT HANDOFF

OWED: none. Owner question (slug plus-edge-matcher-cost): are the 92 `+` edge cells compile-only exceptions too (my reading of
limit-cell-matcher-cost), or should they run a matcher at a larger wall? Unfixed by design: items under Size-limit edge cells
(K148/K150 block eight families' shipped-cap edges; PCREC_MAX_EMIT_BYTES uncovered). The first full sweep with these cells
(the cloud kind) may expose more `first`-position timeouts on a loaded box. Last R-n applied: none (rulings file empty).
