# p1tri — triage of the make test RED on lane/p1cpu (2026-11-08, sonnet)

Job 470-main-p1cpu-maketest at 894d55387 went red in five sections. No emitted byte moved in any of them (every red is a test pin, a test-script shape or an inherited comment).

## Per-section diagnosis
- test-memfn-arch: INHERITED. S2977 `SAB_EXPECT` comment tripped the architecture-vocabulary census; fixed on main at b56c27d60. Cured by merging main (commit 7ae93b3c4; one trivial conflict in the lanes history index, both lines kept).
- test-core: REAL P1 consequence. The two new CLI arms in cli/main.c read/wrote `opt.flags` with raw masks; flag_access_check wants the accessors.
- test-code: STALE PIN. `--list-cpu-targets` is a new CLI_MODE_TABLE row: mode pin 18 -> 19 and entry-point rows 23 -> 24.
- test-subst: STALE CENSUS. cli_option_census.py VALUES did not know `--list-cpu-targets`.
- test-codegen: P1's own new cli test block (tests/cli/run_cli_tests.sh) tripped K35 (two `sort` sites under the ambient locale) and K37 (the `--list-cpu-targets` invocation had no bound).

## Fixes
- cli/main.c: `pcrec_flags_without(opt.flags, ...) | ...` in both arms (same value, accessor spelling).
- tests/code/run_code_tests.sh: pins 19 modes, 24 rows.
- tests/subst/cli_option_census.py: `--list-cpu-targets` as a `query` row.
- tests/cli/run_cli_tests.sh: `pcrec_run` on the listing call; `LC_ALL=C sort` on both sorts.

## Checks
make, make strict clean; `make test-core test-code test-memfn-arch test-subst test-codegen` each rc=0 alone on the worktree. No emitted-byte movement (sweep job 470-main-p1cpu-sweep was green, and these edits touch no emitter).

## STATE AT HANDOFF
Rulings file empty; none applied. OWED: full make test, box-queue key main-p1tri-maketest (log /var/tmp/pcrec-pcrec/scratch/p1cpu/maketest2.log; queue holds 19:00-01:00).
