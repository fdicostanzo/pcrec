# lwfollow report

## Summary
`scripts/lanewatch --follow [--quiet-min N=25] [--every S=60] [--max-sec S=14400] NAME` is built. It polls until one actionable state, prints that line and then the house final line `lanewatch: DONE rc=N`: DONE (rc 0), QUIET (10), GONE (11), CAP (12), STOPPED (13, added: a lane whose report said `STATE: stopped` is not DONE). One-shot mode is unchanged (its own case in the self-test).

## What was built
- `scripts/lanewatch`: follow block before the one-shot loop; the header documents the contract. DONE is the one-shot check itself, run as a child (`lanewatch [--dir D] NAME`) with `LANEWATCH_LOG=/dev/null`, so there is no second implementation and polling never adds to the misses log.
- QUIET = no good marker, no file change and no commit for N minutes, counted from the latest of watch start, last file change and last commit. The line carries minutes, last-change and last-commit as ISO times.
- Activity choice: the newest mtime of any file in the worktree except `.git` and `build/lanecheck`. `build/` COUNTS. Measured (read-only) on finished lanes cired2, emitbidi, expectpre, ic0, ic1a, ic1b, cired: a lane running its own sections writes `build/*.log`, `build/watchdog.log`, `build/scr/`, `build/jobs/`, `build/replay/`, objects; an idle lane writes nothing. Excluding build/ would flag a lane in the middle of its own run as QUIET. Only the marker dir is excluded so lanecheck's own writes do not count.
- Test overrides `--quiet-sec S` and `--tree D` (documented in the header).
- Docs: `scripts/CLAUDE.md` index line, `scripts/NOTES.md` per-tool entry, `docs/dev/lanes/BRIEF_TEMPLATE.md` (the manager arms `--follow NAME` in the background at every launch and relaunches on CAP). The .done marker is not mentioned to lanes anywhere.

## Self-test
`scripts/tests/lanewatch.test`, 9 cases, all PASS (run directly: `bash scripts/tests/lanewatch.test`; also picked up by the `scripts/Makefile` wildcard, run by `make testscripts`): good marker (written by the real lanecheck) -> DONE; aged untouched tree -> QUIET with ISO fields; aged tree with a growing `build/watchdog.log` is not QUIET and ends at CAP; writes only under `build/lanecheck` do not count (QUIET); removed tree -> GONE; `--max-sec` -> CAP; no misses-log entries from polling; one-shot unchanged. PLANT: a copy of lanewatch whose activity scan matches no file makes the touched case go QUIET, so the case fails as it must (the test also fails if the plant sed changed nothing). Every case runs under coreutils timeout.

## STATE AT HANDOFF
Committed on lane/lwfollow. Rulings file read: no entries (last entry applied: none). `make -C scripts test` (all scripts' self-tests) was started to confirm the pattern rule picks the new test up; see the handback for its result. OWED: none.
