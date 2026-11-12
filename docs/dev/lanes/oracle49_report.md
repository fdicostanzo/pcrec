# oracle49 report: make test against the PCRE2 10.49 oracle build ([ORACLE-UPGRADE])

Lane oracle49 (sonnet), 2026-11-12. Process files only; no `src/`, `memfn/` or test-code edit.

## What was built
- No test-code change was needed. `tests/lib/resolve_pcre2.sh` tries `pkg-config libpcre2-8` first, so
  `PKG_CONFIG_PATH=$D/install/lib/pkgconfig` (D=/var/tmp/pcrec-pcrec/oracle/pcre2-10.49) selects 10.49 for the C oracles
  and, through `PCREC_PCRE2_PATH` (libdir glob), for the python ctypes consumers; `LD_LIBRARY_PATH=$D/install/lib`
  makes the loader take the same copy. The STOP RULE did not fire.
- Job script (copy): `docs/dev/lanes/oracle49/300-main-oracle49-maketest.job.sh` (live copy in the queue). It runs in this
  worktree (clean, at main 0c56b73cf; only docs are committed on lane/oracle49): `make -j16`, then
  `make -k -j16 -Otarget test`.
- It FIRST asserts the resolver gives `PCRE2_AVAILABLE=1`, `PCRE2_VERSION=10.49` and a `PCREC_PCRE2_PATH` under $D/install/lib
  (at dry run AND at start), and after the run fails the job if any `[ORACLE-LINK] libpcre2 resolved:` line in the log is not 10.49.
- Premise test: pkg-config printed 10.49. Dry run passed; the CI pin (D98) did not move.

## STATE AT HANDOFF
- Queued, not run. Job key: `300-main-oracle49-maketest` (owner main, prio 300, cap 5400, est 2400, patience none).
  The queue's no-start window holds it until 01:00.
- Log: `/var/tmp/pcrec-pcrec/scratch/oracle49/test.make.log` (build: `build.log`, same dir).
- Completion line to read: `== oracle49 make test rc=N` in the queue job log (`worktrees/.boxqueue/done/*oracle49-maketest/job.log`),
  followed by the `libpcre2 resolved` count (all 10.49) and any `test-red:` lines; the verdict is make's
  `*** [Makefile:N: test-X] Error` lines (grep -E `'\*\*\* \[(Makefile:[0-9]+: )?test-'`), not "sections ran".
- Last rulings entry applied: none (file empty or absent).

## OWED
- The queued run `300-main-oracle49-maketest` (starts 01:00; read via `scripts/monread main --wait` or the job dir).
- Disposition lane (after the run), for EVERY difference vs the 10.46 baseline (a main `make test` green on CI/box at the same commit):
  1. A 10.49 behaviour fix our expectations still encode the old way: follow it (oracle-verify, update the .rxt/registry row, cite the PCRE2 change).
  2. A PCRE2 10.49 regression: file it in `docs/dev/upstream_issues.md` (compatible-unless-PCRE2-bug rule), keep our behaviour, add a tolerance.
  3. A tolerance in the list at upstream_issues.md U25 that 10.49 no longer needs: retire it.
  Also record the PC-3 probe count (a per-build floor+record) and the PCRE2 version stamps. If green with no differences, say so; moving the CI pin (D98) is a separate ruling.
