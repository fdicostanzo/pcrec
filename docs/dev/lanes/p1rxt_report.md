# p1rxt report: rxtsource census re-pin on lane/p1build

## Cause
Job 709-p1tri-test failed test-rxtsource ("census MOVED: found 312/6304/75730, pinned 312/6298/75704"; C1 leg A 6304 vs 6298). Lane p1kind commit e766f6b15 added 6 libpcre2-generated blocks to tests/landwalk/landwalk.rxt after lane p1tri summed the pins.

## Delta check
`git show e766f6b15 -- tests/landwalk/landwalk.rxt`: 56 added lines, 6 `pattern` blocks (all `# pcre2-only`, g1/gstart witnesses), 26 expectation lines (m/n/ms/ns). Exactly +6 blocks / +26 lines; file count unchanged (312). No other corpus file moved.

## Readers re-pinned (grep 6298/75704 across tests/ scripts/ docs/testing.md found only these)
tests/rxtsource/run_rxtsource_tests.sh: CENSUS_BLOCKS (6304), CENSUS_LINES (75730), RUNSH_BLOCKS (6304), RUNSH_LINES (75730), comment style "summed by lane p1rxt (2026-10-30): +6 blocks p1kind". Commit "p1rxt: re-pin rxtsource census".

## Validation
OWED: `make test-rxtsource` queued as job 700-p1rxt-rxtsource (scripts/boxqueue add; a direct `boxlock run` yielded behind the qsplit/fsfix queue jobs, so it was killed by safekill and queued instead). Green line: no `*** [..test-rxtsource] Error`; pass line "census: 312 files / 6304 blocks / 75730 expectation lines (matches the pin)". Log: worktrees/.boxqueue (job 700-p1rxt-rxtsource).

## STATE AT HANDOFF
Pins committed on lane/p1build; the one validation run is queued and owed. Rulings file: no entries applied. docs/dev/artifact_size_log.tsv is dirty in the worktree and not mine (left uncommitted).
