# iterchk report -- check-side and doc FIX-NOW findings of the iterator r2 code round

Branch `lane/iterchk` (from `lane/iterland` 588714855), four commits. Touches no `src/`, pin,
manifest or count file. Review source: `docs/dev/reviews/2026-10-23-r2-iter-code/` (checks.md,
contract.md).

| id | change | commit | evidence |
|---|---|---|---|
| CHK-1 | `tests/findall/iter_drv.c`: a cell libpcre2 refuses is SKIP only when `fail[]` is empty; otherwise DIFF with FAIL= naming the arms | c9e37afa1 | `run_iter_diff.sh` green: skip=0 of 3,873 cells (the SKIP path itself is not exercised by any current cell) |
| CHK-2 | `run_iter_diff.sh`: `MAX_SKIP` ceiling (default 0, MEASURED: the suite has 0 SKIPs today; any SKIP is a cell that stopped reaching the oracle); no libpcre2 exits 77; `run_findall_tests.sh` turns 77 into `SKIP: test-findall`, `checks passed: 0`, `checks skipped: 1` (never PASS with 1 check); the ASan-unavailable case prints `PASS (ASan half SKIPPED)` with `checks skipped: 1` | c9e37afa1 | green on this box; the 77 path is not run here (libpcre2 resolves) |
| CHK-3 | driver appends `W=ill\|ok` (utf group, subject not well-formed UTF-8); the runner excuses a GIVEUP under `-futf-check` only on W=ill, under `--step-budget` only in the `(a+)+b` groups | c9e37afa1 | 132 giveups in the full run, all excused by the new per-subject rule |
| CHK-4 | `n0fresh` only if the FRESH iterator stayed FRESH after k=0 and the subject has a match; `n0ended` only if `it` was ENDED at that point | c9e37afa1 | n0fresh=3164, n0ended=3873 |
| CHK-5 | new driver-side reach tokens, written only when their condition held, added to REACH_NEED: `vmretry` (S1297, S1308), `dfaretry` (S1298, S1307), `kretry` (S1299), `stray` (S1300), `bpoison` (S1302). S1301/S1303/S1304/S1305/S1306 have no cell-dependent condition (their arms run on every subject, or are structural) and get none. No `src/` token was needed | c9e37afa1 | vmretry=235 dfaretry=398 kretry=20 stray=50 bpoison=3164 |
| T4 | no CLI input reaches a compound-class constraint row (P2/P3): every compound part has >= 2 callers and is copyable (probed 11 patterns x 4 flag sets plus the 395-pattern population, `--emit-facts`). Replacement fixture `compound-shared` (P4, beside `compound-inline` P5) pins that both parts reach the class rows; header states the limit | a564be4b4 | `make test-partlayout`: 50 passed, 0 failed |
| CHK-8 | `gen_global.py` takes every count from libpcre2's own global iteration, as the match count of `pcre2_substitute(PCRE2_SUBSTITUTE_GLOBAL, "")` in a small oracle program it writes; iter_drv's `G=` is read only for the skip rule and as a stop-on-disagreement cross-check; python disagreements are now named on stderr. `mc` lines use the same count | aaeb7216f | regenerated to a scratch file: every committed block identical; the generator also finds 5 NEW blocks (cells.tsv has outgrown the committed global.rxt: 67 blocks vs 62) |
| CONTRACT-3/4, EMIT-5 | match_api.md §3.8.2¶2-4 (VLA caps / buf from `info->ncaps`; `next` for one match, `next_n` pays from k >= 4), §3.8¶6a (a start past n ends with rc 0 before any check) | 933e353f7 | test-spec-history 11/0 |
| SLOT-8 (design side) | findall_iter.md §2.4 var row: per-search resolution as built | 933e353f7 | -- |
| CONTRACT-6 | `## Goals` on findall_iter_i2.md (5 ranked goals, priority, non-goals), marked as the 2026-10-23 revision | 933e353f7 | -- |

Validation (this worktree, `make -j16` first): test-findall PASS (full diff 256 groups, ASan half
16 groups), test-encseam 3/0, test-spec-history 11/0, test-plan-lint 2/0, test-partlayout 50/0.

## OWED to the manager / iterfix2
- `tests/findall/global.rxt` NOT regenerated: the 5 new blocks (and 1 extra subject in an existing
  block) move the rxtsource census, the startset manifests and the axes allowances, which this lane
  may not touch. Regenerate with `python3 -I tests/findall/gen_global.py build/pcrec cc
  tests/findall/global.rxt` together with the pin moves.
- CONTRACT-2 (the `lo` after a UTF refusal, spec §3.8¶9) and the CONTRACT-1 corpus rows are iterfix2's.
- Not done (not in the brief): CHK-6/7/9/10, T1/T3 judgements.
