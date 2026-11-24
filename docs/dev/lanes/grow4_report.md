# grow4 report: growth sweep cells split into STABILITY and LIMIT kinds

Lane grow4 (sonnet), branch lane/grow4 off lane/grow3 dfa834c3d. Rulings file: empty, no R-n applied.
No `src/` edit. Premise test (r73 VERDICT-2/3 base): at dfa834c3d a matrix@250 cell with an injected refusal
read PASS only if the refusal text was one of MATRIX_250_EXPECT's four substrings (an `internal error:` read
FAIL, so grow3 fixed it partly); the 252-cell "compile" population still passed on a COMPILE with no matcher run.

## Summary

- Every cell now carries a declared `kind` (`stability` | `limit`), a closed set, no default, and a `pair` id.
  The runner exits on a missing or unknown kind. `--pairs` lists pairs and UNPAIRED cells; `--selftest` shows the
  crossing-over alert both ways; `--sample N` runs N matrix pairs.
- Counts at this tip (`run_growth.py --list`): 1,398 cells = 599 limit + 799 stability (33 depth + 552 matrix + 14 spine limit cells; see the table below).
- Matrix sample (20 pairs, 40 cells, all 8 kinds / 7 quantifiers / 4 positions / 3 cores): 200 runs passed, 0 failed.
- `make test-stackdepth` green (78 + 5 checks); spine and memory families re-run: 0 FAIL, 5 KNOWN-RED (K148, now at the
  limit edge) + 3 KNOWN-RED (K150/K151).
- FINDINGS for the manager (below): matcher build at the NFA edge costs gcc 10 min / 3.4 GB; matrix cells that cannot be
  limit cells; K150 prevents any just-before-cap cell for the lm_* families; 2 families reach no limit.

## Kinds and criteria

Owner rulings growth-compile-cells and limit-test-criteria (docs/design/plan_row_bodies/GROWTH-SWEEP.md).
- STABILITY (sized past a named limit): PASS = a clean refusal whose text is that limit's. FAIL = crash, timeout,
  runaway, a different refusal (`internal error:` included), or a compile ("CROSSED OVER" in the message).
- LIMIT (just before a named limit): PASS = compiles AND the emitted C (with a main()) is built with `gcc -O0` and run on
  the subjects "", "a", "abcabc", each exiting 0 or 1 (a crash, give-up 3 or other exit = FAIL kind MATCHER; a gcc
  failure = BUILD). A refusal of any kind = FAIL ("CROSSED OVER", the limit fired early).
- Ladder (memory cap) runs are unchanged and stability-only in spirit: PASS = compiled, refused by the cell's limit text
  or out of memory. One harness fix: a rung smaller than twice the pattern's own size is skipped (the 1.6 MB `uni`
  pattern is read before the cap is set and left no room for a thread: ERROR at 2 MB).
- Red cells keep the known-kind rule (`ID:KIND`).
- "the cell's subject": no per-cell subject exists; three fixed subjects (SUBJECTS in run_growth.py).

## Cell classification

| family | cells | kind | note |
|---|---|---|---|
| depth@250 (33) / @251 (33) | 66 | 33 limit + 33 stability | 33 pairs, limit PCREC_MAX_GROUP_DEPTH |
| matrix@250 / @251 | 1,288 (was 1,344) | 552 limit + 92 stability (the `+` cells) @250; 644 stability @251 | 552 pairs; see below |
| spine compile cells (29) | 14 families | 14 LIMIT, each re-sized to the bisected edge, with a new exact stability twin | 13 NFA/VM-node edges, 1 emit-cap edge |
| memory compile cells (8) | lm_cat, lm_cls, lm_alt2 | all STABILITY (re-sized to the existing 8000 `_past` rows) | no pair |
| other cells.tsv stability rows | the rest | STABILITY | |

Spine decisions (limit cell n; its twin n+1; all bisected on the default build, 1 unit past = refused):
NFA states 131,072 (PCREC_MAX_NFA_STATES): z_b 131067, z_look/z_nlook/z_cilook 131068, z_lookb 131067, z_cls/lit/cat_ncgrp/uni
131069, anchors 131070. VM nodes 131,072 (PCREC_MAX_VM_NODES): alt_cap 17772, cat_grp 65535, named 65535. Emit code 500,000 bytes
(PCREC_MAX_VM_EMIT_CODE_BYTES, shipped caps): alt_lit 70657 (its twin 70773: the limit cell's artifact carries a main(), which
counts toward the cap). The old 16384 / 100000 sizes were 12 % / 76 % of a limit: not "just before"; dropped for the edge.
Dropped: `empty` (`(?:)` x n) and `inl` (`(?i)(?-i)` x n): they compile at 400,000 units and reach NO named limit, so they
can be neither kind (FINDING: no limit bounds them; the crash coverage of a 100,000-long spine of them is gone).
Memory: K150's quadratic memory runs away (3 GB) from about N=4,770, before the emit cap (about N=7,700) can be approached,
so no just-before cell exists; the 8 compile cells became stability cells past the cap (K150 FINDING, no change to src).

Pairing (`--pairs`): 691 pairs; 196 UNPAIRED cells (a finding, listed): all 92 matrix `+`@250 cells and their 92 @251 twins
(`+` replicates the body each level; PCREC_MAX_NFA_STATES / PCREC_MAX_VM_REPLICATION_PRODUCT refuse near depth 17 to 18, long
before 250, as limits.md 3.10 says; a limit cell would sit at a much smaller depth, not built: it needs a per-shape edge),
plus stability cells with no limit twin: spine/cnt_past (2), memory/cnt_nest, calls_past (3), calls_big (2), the 8 lm_*_past/k150
cells. No limit cell lacks its twin.

Matrix: `lookbehind x bref` (28 pairs) dropped (PCRE2 refuses a backreference in a lookbehind: no cell can compile); a bref core on
a kind that captures nothing (5 kinds) now gets `(a)` in front (without it the sample refused "\1 refers to capture group 1,
but this pattern has 0", which is not the depth limit). The first sample, before these two fixes, FAILED 8 of 20 limit cells.

FINDING (owner question, slug limit-cell-matcher-cost): the 13 NFA-state and VM-node edge limit cells have `expect
compile:norun`: their emitted C (emit caps lifted) is 25 MB and `gcc -O0` took 9 min 48 s and 3.4 GB (measured on z_cls@131069),
over the sweep's 180 s / 3 GB bounds. They compile but do NOT run a matcher; the ruling asks for one. Options: accept
compile-only for caps-lifted cells, or add limit cells at the emit-cap edge (shipped caps, buildable). The 552 matrix limit
cells and the 33 depth ones do run.
No STOP-rule finding: no limit cell in the sample refused by a limit that limits.md places above it (the `+` refusals are the
documented ones, 3.10 ¶3).

## Crossing-over checks

`python3 -I tests/growth/run_growth.py --selftest` (also run first by `make test-growth`), real runs through the driver:
- stability cell `a` (compiles): judged FAIL, "CROSSED OVER: a stability cell COMPILED (it no longer tests the limit)".
- limit cell at depth 251 (refused): judged FAIL, "CROSSED OVER: a limit cell was REFUSED (the limit fires early)".
- the two controls (stability at 251, limit at 250) judged PASS. Exit 0 iff all four are judged as written.
A live crossing also fired during the lane: spine/alt_lit_past@70658 compiled (the limit cell's main() had shifted the edge)
and was reported FAIL; fixed by sizing the twin at 70773.

## Runs

- `make test-stackdepth`: green, 78 and 5 checks passed, 0 failed (depth arm now also builds and runs 33 matchers; whole target 20 s).
- Spine family: 142 runs passed, 0 failed, 5 known-red (K148 SIGSEGV, now at the NFA edge: z_b, z_look, z_nlook, z_lookb, z_cilook).
- Memory family: 67 passed, 0 failed, 3 known-red (K150 lm_alt2_k150@4000; K151 calls_big x2).
- Matrix `--sample 20` (40 cells): 200 runs passed, 0 failed; 8 UNPAIRED lines (the `+` cells).
- Not run: the full matrix, the library stage (`--lib`), ASan. `python3 scripts/plan_lint.py`: 0 violations.

## Validation dispatched

- Box queue: KEY `grow4-growth` (job 300-grow4-growth), `bash tests/growth/run_growth.sh` on this worktree, est 7200 s, idle-ok
  (queued as the last box act; NOT waited for).
- Cloud `make test`: name grow4-test (see the handback message for the sha).

## STATE AT HANDOFF

OWED: none (the queued full sweep, box-queue name `300-grow4-growth`, is QUEUED for the manager, not owed by this lane).
The sweep (the first full run of the new kinds: the 552 matrix limit cells
that were not sampled may reveal more cells refused by a lower limit; the `+` rule is measured on 4 sampled cells only).
Unfixed by design: items under FINDING above (norun cells, dropped empty/inl, `+` limit cells at small depth, K150).
Last R-n applied: none (rulings file empty).
