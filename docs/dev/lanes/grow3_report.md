# grow3 report: review r73 FIX-NOW rulings applied to the growth sweep

## Summary

Every FIX-NOW id of review r73's "Rulings (manager, 2026-11-21)" is applied, test-harness code only (no `src/`
edit). Premise test: DEPTH-1's repro (a dropped `runs passed:` line, runner rc 1) printed `PASS` at the base.
Each answer-level fix was shown red-before / red-after with a drill (scratch, not committed): a fake
`run_compile_stack.sh` runner, `run_growth.main()` with a faked watchdog, a fake library driver, a real driver
under `ulimit -d`. No R-n ever reached `grow3_rulings.md` (empty): none applied.
Opened for the owner, not touched: the cells VERDICT-1 names (growth-compile-cells).

## Fixes by id

- DEPTH-1 + DEPTH-2 + VERDICT-7: `tests/thread/run_compile_stack.sh` tests `runs passed` and `runs failed` each,
  fails on runner rc != 0, pins the population at 2 x table rows with a floor of 66; `run_growth.py` exits nonzero
  on an empty selection and on an unknown `--only` family. Before: dropcount, rcignored, empty (0) and short (64)
  all PASSED; after: each FAILs with its own message.
- VERDICT-2 + VERDICT-3: ladder PASS = compiled, or refused by one of the cell's `refuse:` texts or "out of memory";
  `rc=-9` is ERROR; an empty `refuse:` substring is refused at load. matrix@250 now names the four refusals
  measured over its 672 cells (MATRIX_250_EXPECT: capture-group reference, NFA limit, nested bounded repeats,
  lookbehind with a backreference; 432 compile). Before: 94 of 106 memory ladder runs passed on `internal error:`,
  672 matrix@250 passed on it; after: all FAIL.
- VERDICT-4: watchdog 123 (CPU) and 124 both TIMEOUT.
- VERDICT-5: `red` is `ID:KIND` (K148:CRASH, K150/K151/K154:RUNAWAY, measured from a base run of spine+memory);
  a failure of another kind is FAIL. Before: K148 cell timing out was KNOWN-RED; after: FAIL.
- VERDICT-6: library control non-match must exit 1 (a crashing control matcher passed before).
- VERDICT-8: walls file keyed by tree root (`growth-walls-<sha1(root)[:10]>.tsv`), named and counted in the
  library stage's and CLI stage's output.
- HOUSE-6(5): `set_cap` returns a status; `growth_driver` exits 2 when the cap cannot be set (before: ran
  uncapped, rc 0, with `ulimit -d 20000` and a 128 MB cap).
- HOUSE-1 (smaller landing): the CONTROL arm now runs on `growth_driver` (`one 0 32768 1 all 0 PATFILE`).
  Deleting `compile_stack_driver.c` is a plan row (with HOUSE-2).
- HOUSE-3: dead `if good: pass` block removed; `stack` is a closed set (`budget`|`main`); cells.tsv `features` /
  `engine` columns dropped, matrix_axes K/Q rows lose the unused `b`; tmp base computed once (`tmp_base()`).
- HOUSE-4: clamp in `over()` (a negative live count reads as 0).
- DEPTH-3: depth_families.tsv header (printf_fmt's actual rule; "checked in run_compile_stack.sh").
- VERDICT-9 + HOUSE-5: testing.md, tests/growth/CLAUDE.md, tests/thread/CLAUDE.md, Makefile comment, run_growth.py
  docstring (FIXED-RED in the exit rule, `--jobs`, `--no-ladder`, env switches, one `red`-column sentence, K155 as
  the library stage's red, walls file, limit claims).
- PLAN: [GROWTH-DRIVER-UNIFY] (HOUSE-1 deletion + HOUSE-2, trigger: the next lane touching tests/thread or
  tests/growth drivers); NOTE on [K154-ALT-1M-MEM] (alt_past@500000 at 88 % of the RSS kill).
- Lessons 1 and 2: two drills in the check-adequacy row of `.claude/skills/pcrec-critic/SKILL.md`.

## Sabotage and checks

The matrix runner's single-row form queues behind the box lock (held by queue job grow2-lib), so the 7 rows ran as
planted trees (the row's SAB_BEFORE/AFTER applied to an rsync copy of the worktree, built, then
`run_compile_stack.sh`; scratch, deleted). All seven go red:
S1336 1 fail (10000 captures killed), S1337 1 (trailing assertions killed), S1338 1 (VM literal killed),
S1339 25, S1340 31, S1440 14, S3470 1 (`depth/litcompound@250` CRASH). Clean tree: `make test-stackdepth` 78 pass /
0 fail. Families re-run (nice, jobs 3): depth+spine+memory 596 passed, 0 failed, 19 known-red (the same 15 K148
and 4 K150/K151/K154 runs as before, all of their recorded kind). No sabotage row added. `plan_lint.py` 0
violations. Not re-run: the matrix ladder and the library stage (`make test-growth`).

## Validation dispatched

Cloud `make test` at the tip: see the reply (name grow3-test). `make test-growth` (matrix ladder, library stage)
is OWED to the next full growth run; it is opt-in and held behind grow2-lib on the box.

## STATE AT HANDOFF

Branch lane/grow3 (cut from lane/grow2 6a8238519), committed; rulings file empty, last R-n applied: none.
Box lock was held by grow2-lib during the lane; nothing of mine is running. Open: owner question
growth-compile-cells (742 cells that pass by compiling) and its follow-up lane.

OWED: none (the matrix ladder and library stage of `make test-growth` are not owed by this lane's brief; named above).
