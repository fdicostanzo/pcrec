# grow2: the growth sweep's library bound, the first-run numbers, the filings

Lane grow2 (sonnet), 2026-11-21, branch lane/grow2 cut from lane/grow1 e1310f1d7.
Last ruling applied: none (grow2_rulings.md held no entries at any re-read). No `src/` edit.

## Summary

- The library stage now bounds every in-process compile with its OWN wall
  bound and prints a progress line per cell; a cell over its bound is a FAIL
  (timeout = crash) and the series stops there with the cell named.
- The cell the first run seemed stuck on is `matrix/ncgroup.poss.last.lit@250`
  (series line 1,745, 128 MB rung). It is NOT a hang: it is a SLOW compile,
  26 s plain and 90 s under ASan, finishing on every rung. NEW-3 (a different
  hanging cell) is therefore not filed; the slow compile itself is a
  candidate finding for the manager (see "Which cell hung").
- `tests/growth/run_growth.sh` is listed in `tests/lib/san_excluded.txt`
  (OWN-TIER, with its reason).
- First-run CLI numbers folded in below; K154 (NEW-1) and K155 (NEW-2) filed.
- The library stage alone is queued as `grow2-lib`.

PREMISE TEST: the job record `worktrees/.boxqueue/failed/20261121T041946.630218578-300-grow1-growth`
has `rc` 1, `result` "outcome=failed rc=1 wall=6784s verdict=RED", and its
`job.log` ends "FAIL: library mode: library process exit 143" (the ASan stage
killed by the manager's safekill, SIGTERM) after 1,744 of 7,322 cell lines.
Confirmed.

## Library bound

- `growth_driver lib` takes a 7th series column, BOUND_S. Before each compile
  it prints `begin N bound=S pat=FILE` (flushed); it arms `alarm(S)`; the
  SIGALRM handler writes `cell N TIMEOUT bound=S pat=FILE` and `_exit(124)`.
  A cell line now also carries `wall=`. (One in-process compile cannot be
  abandoned and the process continue, so the series STOPS cleanly, cell named.)
- `run_growth.py`: bound = max(300 s, 20 x that cell's slowest CLI-stage wall).
  The CLI stage records each cell's wall in `$PCREC_TMPDIR/growth-walls.tsv`
  (`GROWTH_WALLS` overrides); a library run with no walls entry gets the 300 s
  floor. Margin: ASan+LSan at -O1 measured 3.5x the plain -O2 on the slow cell
  (90 s vs 26 s), 20x leaves a loaded-box allowance; the floor covers cells
  the CLI never timed. A TIMEOUT prints the series line, the cell id, the bound.
- The library process's progress goes to
  `$PCREC_TMPDIR/growth-lib-progress.log` (was a captured pipe: the first run
  showed nothing for 50 minutes), and the lib watchdog wall is 28,800 s (was
  14,400: the ASan series is slow, see below).
- Verified: bound 5 s on the slow cell prints the TIMEOUT line, exit 124;
  bound 100 s lets it finish (`wall=27.29`); `--lib --only depth` (330
  compiles) PASS with the new columns.

## Which cell hung

Series line 1,745 (cell index 1,744; the driver had printed 1,744 lines):
`matrix/ncgroup.poss.last.lit@250` (`(?:a|b|(?:a|b|...` nested 250, possessive
quantifier, features all, shipped caps raised), at the 128 MB rung
(heap-cap budget).

- Single cell, ASan driver, in-process, no cap: 90 s, compiles (rc 0). The
  rungs 8 MB / 32 MB / 128 MB: 90.4 s refused "out of memory" / 90.6 s rc 0 /
  90.4 s rc 0. Plain driver: 26 s (27.3 s with the new wall timer), on the
  budget thread and the main thread alike. So it does not hang; the first
  run's "no output since 03:28" was the pipe being captured, not a stall, and
  the manager killed the series while it was progressing (3,099 s, 1,744
  cells).
- It is not NEW-1 (the 1,000,000-way alternation is in the memory family, far
  later in the series, and its uncapped run is skipped).
- Whether it also "hangs" as a CLI process: no. The CLI stage compiled the
  same cell uncapped in the first run (matrix: 6,720 passed, 0 failed) inside
  the 180 s watchdog; 26 s is its plain wall.
- Consequence for the series: ASan makes each such cell about 90 s x 5 runs.
  How many of the 672 matrix nests are this slow is unmeasured; the queued
  job's progress log and the per-cell walls will say. A cell over its bound
  is reported by name. The 26 s compile of a 2.5 KB pattern (337 KB of
  emitted C) is itself worth a look by the crash-family lane; not filed as a
  K (it compiles and refuses nothing it should), recorded for the manager.

## Sanitizer list

Cloud run 44880433338 shard 5 [TT-9]: `tests/growth/run_growth.sh` was in
neither list. Added to `tests/lib/san_excluded.txt` as OWN-TIER: opt-in
`make test-growth`, a multi-hour sweep outside `make san`'s budget; its
library stage already runs ASan+LSan in-process, and the CLI stage is the
compiler axis with caps and a watchdog. (`make test-codegen` / the [TT-9]
check runs in the cloud run dispatched below.)

## First-run numbers

CLI stage of job grow1-growth (whole job 6,784 s; CLI stage first, then the
library stages), 1,467 cells x 5 runs (uncapped + caps 2, 8, 32, 128 MB):

| family | cells | passed | failed | known-red |
|---|---|---|---|---|
| depth | 66 | 330 | 0 | 0 |
| matrix | 1,344 | 6,720 | 0 | 0 |
| spine | 35 | 160 | 0 | 15 |
| memory | 22 | 106 | 0 | 4 |
| total | 1,467 | 7,316 | 0 | 19 |

- Known-red, all uncapped or at the high rungs and all listed in the job log:
  spine: K148 SIGSEGV on the budget thread for `z_b` (16,384: uncapped,
  32 MB, 128 MB; 100,000: uncapped, 128 MB), `z_look` (16,384: uncapped,
  128 MB; 100,000 uncapped), `z_nlook` (16,384: uncapped, 128 MB; 100,000
  uncapped), `z_lookb` (100,000 uncapped), `z_cilook` (16,384: uncapped,
  128 MB; 100,000 uncapped). memory: K150 `lm_alt2_k150@4000`, K151
  `calls_big@320` and `@1000`, K154 `alt_1m@1000000`: each RUNAWAY (tree RSS
  over 3 GB), uncapped column only. The 2, 8 MB caps and every depth and
  matrix cell: clean (compiled or "out of memory compiling this pattern").
- Ladder per cap: no ladder-only failure in any family; the only capped
  failures are K148's stack crashes at 32/128 MB.
- No FIXED-RED, no timeout, no crash outside the known-red list.
- Library stage, plain build (RLIMIT_DATA caps): 7,322 compiles in ONE
  process, rc histogram {0: 2,229, -1: 5,093}, PASS (no crash, control
  identical and correct).
- Library stage, ASan+LSan: 1,744 of 7,322 cells in 3,099 s, then killed by
  the manager; NO verdict. The series numbers come from the queued job.

## Filings

- K154 (NEW-1): known_issues.md, plan row [K154-ALT-1M-MEM]. cells.tsv
  `alt_1m` now says `red` K154.
- K155 (NEW-2): known_issues.md, plan row [K155-STAMPS-LEAK].
- NEW-3: none (the cell that stalled the series is slow, not hung).
- [GROWTH-SWEEP] status updated; plan_lint 0 violations.

## Validation dispatched

- Queued: KEY `grow2-lib` (name 300-grow2-lib), `SKIP_CLI=1 bash tests/growth/run_growth.sh`
  on worktrees/grow2 (new env switch: library stages only), cap 32,400 s,
  est 10,800 s. Progress: `$PCREC_TMPDIR/growth-lib-progress.log` (the ASan
  stage overwrites the plain one's). OWED: the plain and ASan library
  verdicts, the slow-cell census, and whether any cell trips its bound.
  Expect rc 1 until K155 is fixed.
- Cloud `make test` on the lane tip (name grow2-test).

## STATE AT HANDOFF

Committed on lane/grow2. Last ruling applied: none (rulings file empty).
Not done: the library series verdict (OWED to the queued job); the CLI walls
file does not exist yet, so the queued job uses the 300 s floor for every
cell (a later full run writes it). Do not edit tests/growth/ while the job
runs (it executes the worktree).
OWED: grow2-lib (box queue KEY `grow2-lib`).
