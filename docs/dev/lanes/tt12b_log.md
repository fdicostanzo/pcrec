# tt12b lane log — [TT-12] STEP 1

Running log, lane's own voice. See docs/dev/lanes/tt12b_report.md for the
delivery (commits, measured numbers, acceptance table) once complete.

## 2026-09-03

- Worktree `worktrees/tt12b` on `lane/tt12b` off `main` (6fba88d). Read
  STEP 0 profile (`docs/dev/tt12_step0_profile.md`), the `[TT-12]` plan
  row, K44/K45 (`docs/dev/known_issues.md`), `tests/axes/run_axes.sh` and
  its CLAUDE.md in full before touching anything.
- **Item 2 (K45)** done first, small and self-contained: five
  `REFUSAL_PATTERN` entries added/extended in `run_axes.sh` for
  `tests/size/size_term.rxt:34-35`'s nested-repeat tower — see the commit
  message and `tests/axes/CLAUDE.md`'s new "K45" section for the mechanism
  each of the five axes actually hits. Verified live against the shipped
  diagnostics before writing the substrings (never guessed).
- **Item 1 (pairwise axes)** built on top of the K45 fix (same file). Found
  and fixed a LATENT RACE while building it: `run_one_axis` wrote the
  harness's stdout/stderr and the diff-awk's stderr to FIXED filenames
  shared across every axis call — invisible serially, real once two axes
  can run concurrently. `trap - EXIT` inside each backgrounded subshell is
  load-bearing (the inherited `cleanup()` trap would otherwise delete the
  shared `$WORKDIR`, including `BASE_DUMP`, out from under the sibling
  axis the moment the first subshell's job finishes).
- **Validation run 1** (quiet-ish box, load ~0.3-1.5 before starting):
  `AXES="-fno-counter --engine=dfa"` (the grep-substring match on
  `--engine` pulls in BOTH engine directions) on the FULL corpus. First
  attempt with `gnutimeout 500` was CUT SHORT at the wall bound (3 axes ran
  — fno-counter, engine=vm, engine=dfa — not 2, because of the substring
  match; ~630s needed, 500s given). Re-ran at `gnutimeout 900`: clean.
  `refused_undoc=0` on all three (was 2 each pre-fix), `refused_doc`/agree/
  budget counts otherwise byte-identical to opt5i's pre-fix reference
  (`axes2.log`, 2026-09-02) plus exactly the two new K45 tower cells per
  axis. Confirms pairing preserves per-case answer identity AND the K45
  fix works end to end.
- Committed items 1+2 together (969b9ba) — both touch `run_axes.sh`, both
  validated in the same run; splitting the diff by concern would have been
  more surgery than the two independent changes were worth untangling.
- **Item 3 (san -P) code written**, NOT yet measured/committed:
  `tests/lib/run_san_group.sh` (new — a bounded job pool, FIFO-throttled,
  buffered per-script output replayed in argument order, "-- san: SCRIPT
  --" markers preserved) and the Makefile's `san:` target rewired to call
  it (`SAN_PROCS`, default 4) instead of the bare serial `for` loop.
  Deliberately NOT `tests/lib/run_group.sh` — that script's own header
  says GROUP_PROCS is a real throttle only at exactly 1; every existing
  call site (2-3 scripts) launches its whole group unthrottled above that,
  and san's 34-script list (several already internally parallel at
  PROCS=nproc) needs actual bounded concurrency, not that shape.
  D77 pre-measurement (five whole-corpus identity scripts, sequential vs
  `-P4`) still owed before this lands — box was occupied by the pairwise
  axes full sweep at the time this was written; queued next.
- **Item 5 (battery_v5) drafted**, NOT final: `scripts/battery.sh` — the
  six-stage chain (test/strict/axes/san/lint/mech), detached under
  `setsid` with a PID file, per-stage logs under a timestamped dir, a
  `trailer.log` with stage START/END/rc lines and the final
  `== BATTERY DONE rc=` line. `TEST_MAKE_J`/`TEST_PROCS`/`MECH_PROCS`/
  `SAN_PROCS`/`AXES_PROCS` are all overridable env vars with PLACEHOLDER
  defaults (`TEST_MAKE_J=4 TEST_PROCS=3`, item 4's not-yet-measured
  candidate (b); `MECH_PROCS=6`, item 1's finding 1 finding, already
  confirmed by [TT-8]; `SAN_PROCS=4`) — to be finalized once items 3/4's
  own measurements land. NOT run as a whole (brief: the manager runs the
  full battery at the next merge).
- **Item 1's full 21-axis paired sweep** (the wall-time-vs-4205s-reference
  confirming measurement) launched in background
  (`pairwise_full.log`), full corpus, oracle check included (not skipped —
  matching the delivered `make test-axes` shape, unlike the validation
  run above). Box load at launch: 3.17/8.00/6.69 (some daytime work
  already running per the day/night handshake — noted, not a hold).
  Numbers in the report once it completes.
