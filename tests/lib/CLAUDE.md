# tests/lib — infrastructure shared by every suite

Not a test suite itself: helpers other suites' scripts and the Makefile's
section targets depend on.

## Files

- **gen_timeout.sh** — D45's ONE implementation of the generated-code
  compile budget (10s plain, 60s sanitizer, `GENTIMEOUT`/`GENTIMEOUT_SAN`,
  axis derived from the flags): every compile of emitted C in the tree
  routes through its `gen_cc`, and exceeding the budget is a loud FAILURE
  naming the case, never a hang. Since 2026-08-16 (D45 second addendum) it
  also owns the EXECUTION budget for generated matchers: `gen_run_secs`
  (10s plain, 60s sanitizer, `GENRUNTIMEOUT`/`GENRUNTIMEOUT_SAN`; also
  runnable as `bash tests/lib/gen_timeout.sh runsecs` for python callers)
  and `gen_run <label> <argv...>`, which routes a run through
  `scripts/watchdog` — run budget plus a 512m peak-tree-RSS ceiling
  (`GENRUNMEM`) plus one section-tagged log line per execution in
  `build/watchdog.log`; 124 = run timeout, 122 = memory kill, both loud
  failures checked exactly. Per-pattern run sites use `gen_run`; inner
  loops with hundreds+ of sub-millisecond runs use bare
  `timeout`/`subprocess timeout=` reading the same number, because
  watchdog's fixed startup cost would multiply the loop's runtime.
- **run_gen_timeout_tests.sh** — its own section in `make test`
  (`test-gentimeout`) — a positive control that the wrapper FIRES, plus a
  coverage assertion that every suite routes through it, because a
  test-infrastructure property is invisible to every other suite in the
  tree. The run bound gets the full mirror: per-axis budget checks, a fire
  control on a REAL over-budget run (budget-bound so the control
  terminates even if the wrapper breaks), an oracle-verified pass-through
  control, a growing run-coverage list, and hand-rolled-number greps. The
  122 memory path's positive control deliberately lives in
  `scripts/test_watchdog.sh` instead: no real generated artifact can
  runaway on RSS (allocation-free), so a synthetic allocator there is
  honest where a stub here would only pretend to be an artifact.
- **run_group.sh** ([TT-2], 2026-08-15) — runs N independent shell commands
  (suite scripts) CONCURRENTLY as one Makefile section recipe, used by
  `test-codegen` (`run_codegen_tests.sh` + `run_trie_identity.sh`) and
  `test-vm` (`run_vm_identity.sh` + `run_ir_listing.sh` + `run_vm_tests.sh`)
  — the sections whose own recipe used to just be N sequential script lines.
  `GROUP_PROCS=1` runs the scripts serially in argument order with no
  backgrounding at all, byte-for-byte the old flat recipe; any other value
  (the Makefile passes `$${PROCS:-$$(nproc)}`, the same knob every other
  [TT-2] path honours) runs every script at once — there are only ever 2-3
  scripts per group, never enough to want real job-pool throttling. Output
  is replayed in argument order, each script's complete stdout+stderr as one
  contiguous block, once every script has finished, so nothing interleaves
  mid-line. A script whose wrapping subshell dies before it can record an
  exit code (crashed, killed, OOM) is a HARD FAILURE distinct from an
  ordinary nonzero exit, and is named as such — never silently read as a
  pass. Both failure paths (ordinary nonzero exit via `kill -9` on the
  script's own process, and total loss via `kill -9` on the wrapping
  subshell before it can write its result) are sabotage-validated; see
  docs/testing.md "Internal parallelism and section composition ([TT-2])"
  for the measured wall-time wins and the mechanism this file shares with
  `tests/reject/run_reject_tests.sh`'s own (call-index, not script-index)
  sharding.

## Conventions

A script grouped by `run_group.sh` must isolate itself the same way every
other parallel path in this tree does: its own `mktemp -d` workdir, and
read-only against `build/pcrec`/`build/libpcrec.a` — never shared mutable
state with a sibling script in its group.

Maintenance: update this file when files are added/removed or their roles
change.
