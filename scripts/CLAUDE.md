# scripts — project process tooling

Process tooling, not for building or testing pcrec (the Makefile owns that). Each
script's header is its contract; this file is the index and the standing rules. Full rule detail and per-tool
entries (verbatim): NOTES.md here.

## Standing rules

- Update this file when scripts are added/removed or change role.
- Self-tests live in `scripts/tests/`, run ON CHANGE (`make testscripts`), NEVER in `make test` (D48); bound every case by coreutils `timeout`, never by watchdog.
- Kill only with `scripts/safekill PID`; never `pkill -f`/`pgrep -f`.
- Bound a run with `scripts/watchdog -s WALL -m MEM -c CPU -S label -- cmd` (a bare `-m` number is BYTES); not inside per-case loops; keep `tests/lib/gen_timeout.sh` in sync with its flags/log format.
- Remove worktrees only with `scripts/wtprune` (dry run, then `--apply`); never raw `git worktree remove`/`rm -rf`. Branches: `scripts/branchprune` (same shape; unmerged: `--archive NAME..`).
- Heavy runs: `boxlock` (a non-`queue:` run YIELDS to ready pending queue jobs; `PCREC_BOXLOCK_JUMP=1` overrides, audited; `status` lists the WAITERS, label runs `<lane>-<what>`), `boxqueue` (shortest ready run first: `boxqueue: est S`), `chainrun`, `watchrun`, `verdict`; do not hand-write chain.sh/waiters/watchers.
- A tool that ends a run prints ONE `TOOL: DONE rc=N` line on every ending; new long-running tools must follow it.
- `mk_d27_cell.sh` needs an explicit allowlist per invocation.
- Hooks are opt-in via `make hooks`; no CI auto-install (D2).
- An emitter refactor claiming "moves no emitted byte" is proved with `emit_sweep.py`; a new deny/force flag needs a DIFFER_PINS cell and a mech sabotage.
- Plan edits must pass `scripts/plan_lint.sh`; generated embeds are committed (`make gen-findings`, `make gen-measures`).

## Files

- Process control: `safekill`, `watchdog`, `wtprune`, `branchprune`, `mk_d27_cell.sh`; run-control family `boxlock`, `chainrun`, `watchrun`, `verdict`, `boxqueue` (+`_window`,`.inboxes`; NOTES.md), `perfrun` (+ `perfrun.shapes`, `cpusample.sh`, `sectiontimes`), `battery.sh`; `fullsuite_job.sh` (battery.sh as a box-queue job, D177; `--dry-run` is the only safe check; NOTES.md); `fullsuite_resume RUNDIR` (owner-commanded stage resume of a red full run, [SUITE-RESUME]; see fullsuite_job.sh header); `queuewatch` (the queue's event watcher, one line per event, then exit; CI runs via `gh`, `--no-ci` skips; `/pcrec-monitor` loops it); `queuemon`/`monread`/`hooks/monitor_unread.sh` ([MON-SCRIPT], header of queuemon); `session_role` (hook roles); `monitor_rehearsal` (monitor skill TEST MODE driver); `monitor_preflight` (monitor startup tools test; changes nothing).
- `lanecheck`/`lanewatch` — [LANECHECK] DELIVER self-check / the manager's watcher; `lanewatch --follow NAME` reports one lane's state; NOTES.md.
- `INDEX.md` — one `when:`/`does:` line per script (`scripts/entry NAME -l 2` adds its header). A new script needs its line in the same change (`entry --lint-scripts`, in `make test-doc-lint`).
- Checkers: `plan_lint.*`, `entry` + `doc_profiles.py` ([DOC-INDEX] D192: one item at a level, item grep, `--work`, `--over-cap`; the profile table; docs/dev/doc_format.md), `check_claudemd_size.sh`, `spec_toc.py`, `measure.sh`, `tmpdir.sh`, `doc_census.py`/`doc_control.py`/`doc_cites.py`
- Instruments: `statusline.sh` (NOTES.md), `gestalt`, `emit_sweep.py`, `trace_diff.py`, `cls_identity.py`, `compile_time_census.py`, `alt_census.py`, `size_diff`.
- Generators: `embed_text.sh`, `ksgen.c`.
- `hooks/` — pre-commit, pre-push(-light), `no_cd_worktree.sh`, `no_commit_all.sh` (`git commit -a`), `lane_writes_in_worktree.sh` (subagent writes only in worktrees/; escape worktrees/.mgr/main_write_ok), `no_stale_claudemd.sh`, `post_compact.sh`, `pcre2_ref_guard.sh` (D181), `check_pcre2_note.sh`; tests `hooks/test_*.sh`.
- `tests/` — self-tests (own CLAUDE.md).

## Pointers

docs/testing.md, docs/dev/learnings.md §6, docs/dev/devmethods/apply_here.md, docs/dev/ttune_measurement.md.

History (not auto-injected): docs/dev/history/claude_md/scripts.md
