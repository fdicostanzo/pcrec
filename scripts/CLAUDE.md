# scripts — project process tooling

Shell tooling for the development process, not for building or testing pcrec (the Makefile owns that). Each
script's header is its contract; this file is the index and the standing rules. Full rule detail and per-tool
entries (verbatim): NOTES.md here.

## Standing rules

- Update this file when scripts are added/removed or change role.
- Self-tests live in `scripts/tests/`, run ON CHANGE (`make testscripts`), NEVER in `make test` (D48); bound every case by coreutils `timeout`, never by watchdog.
- Kill only with `scripts/safekill PID`; never `pkill -f`/`pgrep -f`.
- Bound a run with `scripts/watchdog -s WALL -m MEM -c CPU -S label -- cmd` (a bare `-m` number is BYTES); not inside per-case loops; keep `tests/lib/gen_timeout.sh` in sync with its flags/log format.
- Remove worktrees only with `scripts/wtprune` (dry run, then `--apply`); never raw `git worktree remove`/`rm -rf`.
- Heavy runs: `boxlock`, `boxqueue`, `chainrun`, `watchrun`, `verdict` (artifacts, never process greps); do not hand-write chain.sh/waiters/watchers.
- A tool that ends a run prints ONE `TOOL: DONE rc=N` line on every ending; new long-running tools must follow it.
- `mk_d27_cell.sh` needs an explicit allowlist per invocation.
- Hooks are opt-in via `make hooks`; no CI auto-install (D2).
- An emitter refactor claiming "moves no emitted byte" is proved with `emit_sweep.py`; a new deny/force flag needs a DIFFER_PINS cell and a mech sabotage.
- Plan edits must pass `scripts/plan_lint.sh`; generated embeds are committed (`make gen-findings`, `make gen-measures`).

## Files

- Process control: `safekill`, `watchdog`, `wtprune`, `mk_d27_cell.sh`; run-control family `boxlock`, `chainrun`, `watchrun`, `verdict`, `boxqueue`, `perfrun` (+ `perfrun.shapes`, `cpusample.sh`, `sectiontimes`), `battery.sh`; `fullsuite_job.sh` (battery.sh as a box-queue job at a frozen commit, retained verdict in build/full_suite/, D177; its --dry-run is the only safe check: `boxqueue add` ARMS A RUNNER that runs it; `--simulate NAME[:STAGE]` = the same code path with only the stage payloads faked, battery.sh `BATTERY_SIMULATE`, scenarios in its header, no worktree/ledger/box lock; to rehearse a queue watcher use `tests/queuewatch.test`, never a hand-made scratch queue add); `queuewatch` (the whole queue's event watcher: one line per event then exit, persistent reported-events state; the standing `/pcrec-monitor` session loops it; also reports main's CI runs from `gh run list`: CI-RED/CI-CANCELLED/CI-UNAVAILABLE, `--no-ci` to skip; watchrun still watches ONE log); `monitor_rehearsal` (scratch-queue driver + comparer for the monitor skill's TEST MODE, simulated jobs only; setup/compare/status/teardown); `monitor_preflight` (the monitor's startup tools test: one PASS/FAIL line per tool incl. gh install/auth/run list, `DONE rc=N`, changes nothing).
- Checkers: `plan_lint.sh`/`.py`, `check_claudemd_size.sh`, `spec_toc.py`, `measure.sh`.
- Instruments: `emit_sweep.py`, `trace_diff.py`, `cls_identity.py`, `compile_time_census.py`, `alt_census.py`, `size_diff`.
- Generators: `embed_text.sh`, `ksgen.c`.
- `hooks/` — pre-commit, pre-push(-light), `no_cd_worktree.sh`, `no_stale_claudemd.sh`, `post_compact.sh`.
- `tests/` — self-tests (own CLAUDE.md).

## Pointers

docs/testing.md, docs/dev/learnings.md §6, docs/dev/devmethods/apply_here.md, docs/dev/ttune_measurement.md, BOILERPLATE.md, tests/CLAUDE.md.

History (not auto-injected): docs/dev/history/claude_md/scripts.md
