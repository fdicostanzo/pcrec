# docs/dev/lanes/e1_evidence — lane e1's reproduction pieces

Evidence behind `../e1_report.md` §7 Q1 (the `shared` = `noipa` ruling):
the -O1 `window` maybe-uninitialized warning is a FALSE positive.

- **fp_driver.c** — the driver: every subject over `abcdz _` up to length 5,
  every start, `rx_search`'s return and span folded into one hash (114,381
  calls). Compiled beside an artifact `x.c`/`x.h`.
- **fp_runs.txt** — its runs: each witness's default and `shared` artifacts
  (the `noipa` build, then commit A's `noinline` build) under
  `-O1 -fsanitize=address,undefined -ftrivial-auto-var-init=pattern` and
  under valgrind memcheck (`--track-origins=yes`); equal hashes per pattern,
  no report from either tool.

Maintenance: update this file when files are added/removed or their roles
change.
