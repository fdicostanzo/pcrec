# scripts — project process tooling

Shell tooling for the development process, not for building or testing pcrec (the Makefile owns that). Each
script's header is its contract; this file is the index and the standing rules. Full rule detail and per-tool
entries (verbatim): NOTES.md here.

## Standing rules

- Update this file when scripts are added/removed or change role.
- Self-tests live in `scripts/tests/`, run ON CHANGE (`make testscripts`), NEVER in `make test` (D48); bound every case by coreutils `timeout`, never by watchdog.
- Kill only with `scripts/safekill PID`; never `pkill -f`/`pgrep -f`.
- Bound a run with `scripts/watchdog -s WALL -m MEM -c CPU -S label -- cmd` (a bare `-m` number is BYTES); not inside per-case loops; keep `tests/lib/gen_timeout.sh` in sync with its flags/log format.
- Remove worktrees only with `scripts/wtprune` (dry run, then `--apply`); never raw `git worktree remove`/`rm -rf`. Branches: `scripts/branchprune` (same shape; unmerged: `--archive NAME..`).
- Heavy runs: `boxlock` (a non-`queue:` run YIELDS to ready pending queue jobs; `PCREC_BOXLOCK_JUMP=1` overrides, audited in worktrees/.box.lock.audit; `status` lists the WAITERS, label runs `<lane>-<what>`), `boxqueue`, `chainrun`, `watchrun`, `verdict` (artifacts, never process greps); do not hand-write chain.sh/waiters/watchers.
- A tool that ends a run prints ONE `TOOL: DONE rc=N` line on every ending; new long-running tools must follow it.
- `mk_d27_cell.sh` needs an explicit allowlist per invocation.
- Hooks are opt-in via `make hooks`; no CI auto-install (D2).
- An emitter refactor claiming "moves no emitted byte" is proved with `emit_sweep.py`; a new deny/force flag needs a DIFFER_PINS cell and a mech sabotage.
- Plan edits must pass `scripts/plan_lint.sh`; generated embeds are committed (`make gen-findings`, `make gen-measures`).

## Files

- Process control: `safekill`, `watchdog`, `wtprune`, `branchprune`, `mk_d27_cell.sh`; run-control family `boxlock`, `chainrun`, `watchrun`, `verdict`, `boxqueue` (+`_window`,`.inboxes`; NOTES.md), `perfrun` (+ `perfrun.shapes`, `cpusample.sh`, `sectiontimes`), `battery.sh`; `fullsuite_job.sh` (battery.sh as a box-queue job at a frozen commit, retained verdict in build/full_suite/, D177; its --dry-run is the only safe check: `boxqueue add` ARMS A RUNNER that runs it; `--simulate NAME[:STAGE]` = the same code path with only the stage payloads faked, battery.sh `BATTERY_SIMULATE`, scenarios in its header, no worktree/ledger/box lock; to rehearse a queue watcher use `tests/queuewatch.test`, never a hand-made scratch queue add); `fullsuite_resume RUNDIR` (owner-commanded stage resume of a red full run, [SUITE-RESUME]; see fullsuite_job.sh header); `queuewatch` (the queue's event watcher, one line per event, then exit; CI runs via `gh`, `--no-ci` skips; `/pcrec-monitor` loops it); `queuemon`/`monread`/`hooks/monitor_unread.sh` (the queue monitor as a script, [MON-SCRIPT]; header of queuemon); `monitor_rehearsal` (monitor skill TEST MODE driver); `monitor_preflight` (monitor startup tools test; changes nothing).
- `lanecheck`/`lanewatch` — [LANECHECK] DELIVER self-check / the manager's watcher; `lanewatch --follow NAME` reports one lane's state; NOTES.md.
- Checkers: `plan_lint.*`, `check_claudemd_size.sh`, `spec_toc.py`, `measure.sh`, `tmpdir.sh`
- Instruments: `emit_sweep.py`, `trace_diff.py`, `cls_identity.py`, `compile_time_census.py`, `alt_census.py`, `size_diff`.
- Generators: `embed_text.sh`, `ksgen.c`.
- `hooks/` — pre-commit, pre-push(-light), `no_cd_worktree.sh`, `no_commit_all.sh` (blocks `git commit -a`), `lane_writes_in_worktree.sh` (a subagent writes only under worktrees/; escape file worktrees/.mgr/main_write_ok), `no_stale_claudemd.sh`, `post_compact.sh`; fixture tests `hooks/test_*.sh`.
- `tests/` — self-tests (own CLAUDE.md).

## Pointers

docs/testing.md, docs/dev/learnings.md §6, docs/dev/devmethods/apply_here.md, docs/dev/ttune_measurement.md, BOILERPLATE.md, tests/CLAUDE.md.

History (not auto-injected): docs/dev/history/claude_md/scripts.md
