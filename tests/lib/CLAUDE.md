# tests/lib — infrastructure shared by every suite

Not a test suite itself: helpers other suites' scripts and the Makefile's
section targets depend on.

## Files

- **timeout_bin.sh** — [TT-6] resolves `TIMEOUT_BIN` ONCE per process: the
  coreutils `timeout` binary every suite should invoke instead of a bare
  `timeout`. THE FINDING (docs/dev/tt4_measurement.md, "The `timeout`
  binary itself"): this box's default `/usr/bin/timeout` is uutils
  coreutils 0.8.0, which POLLS its child instead of blocking on it —
  MEASURED ~108.7ms of pure wall per call, ~0 CPU; `/usr/bin/gnutimeout`
  (GNU coreutils 9.7) does the identical job in ~4.2ms. Detection order:
  env override, else the default `timeout` bare if it self-identifies as
  GNU (the common case, changes nothing for a stranger's box — D2/R5-Q1),
  else `/usr/bin/gnutimeout`, else `gtimeout` (Homebrew/macOS), else plain
  `timeout` (a box with no GNU coreutils `timeout` pays the uutils tax
  exactly as before this file existed — never a hard failure). Announces
  the resolved choice once per top-level script to stderr, only when it
  differs from plain `timeout`, gated by an exported
  `TT6_TIMEOUT_BIN_ANNOUNCED` so a script sourcing this both directly and
  transitively (via `gen_timeout.sh`) prints exactly once. POSIX sh, no
  bashisms — sourced from bash scripts AND from `scripts/Makefile`'s
  recipe under its default `/bin/sh`. A SEPARATE file from `gen_timeout.sh`
  because not every bare-`timeout` caller sources that file (`tests/
  reject/run_reject_tests.sh`, `tests/bench/run_bench.sh`, `tests/bench/
  compare/compare.sh` do not — folding this in would make them take on
  D45's CPU/wall-budget machinery just to get a binary name); those three
  plus `scripts/Makefile` source `timeout_bin.sh` directly instead.
  MEASURED (docs/testing.md "The `timeout` binary itself"): 6.31x wall on
  an isolated `make test-corpus` run (identical case counts before/after),
  a wash on the full `-j12 -Otarget make test` total (concurrent sections
  hide a sleeping worker's wall time — the tax shows where sections run
  closer to serially: the sanitizer axes, `make mech` rows, `PROCS=1`).
- **gen_timeout.sh** — D45's ONE implementation of the generated-code
  compile budget — CPU-PRIMARY since the D45 third addendum (2026-08-16):
  `gen_cpu_secs` (10s plain / 60s sanitizer, `GENCPU`/`GENCPU_SAN`,
  RLIMIT_CPU — load-resilient: contention inflates CPU ~2x at worst,
  measured, where wall stretches unboundedly) with
  `gen_timeout_secs` as the wall BACKSTOP (60s/180s,
  `GENTIMEOUT`/`GENTIMEOUT_SAN`) for the stuck-without-working class CPU
  cannot see; axis derived from the flags. Every compile of emitted C
  routes through its `gen_cc`, and exceeding either budget is a loud
  FAILURE naming the case AND the clock that fired, never a hang. Since 2026-08-16 (D45 second addendum) it
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
  **[TT-3] `CCACHE=1` (2026-08-21)** gates two more things in this file,
  both no-ops when unset: `_gen_cc_run` reshapes `gen_cc`'s compile+link
  calls into a `-c` compile per source then a link (the shape ccache can
  cache — a raw compile-and-link cannot), and `gen_cc_relativize` rewrites
  the call's own `-I<outdir>` to the textually-stable `-I.` after `cd`-ing
  into it (every call site's own `-o` directory), because a fresh per-case
  `mktemp` path in that flag defeated caching even with the shape fixed —
  `CCACHE_NOHASHDIR=1`/`CCACHE_BASEDIR` are exported alongside it for the
  same reason under `-g`. MEASURED (docs/testing.md "Compile caching"): a
  clear NO for `make test` (a cold/warm cycle came in at 4x+ the plain
  baseline even at a real 64.59% hit rate — thousands of sub-millisecond
  compiles is the wrong shape for caching's own overhead), a qualified YES
  for `make mech`'s per-sabotage tree rebuild. **[TT-6] sources
  `timeout_bin.sh`** (above) for `gen_cc`'s own wall wrapper, which now
  invokes `"$TIMEOUT_BIN"` rather than a bare `timeout` — this is
  sabotage S43's anchor line, re-derived in the same change.
- **table.sh** — [SR-11]'s ONE implementation of docs/spec/table_contract.md
  (the RULED contract for tabular `pcrec` command output — `#` comments,
  header-names-columns, append-only, optional `#section NAME` blocks), the
  same single-implementation shape `gen_timeout.sh` established for the
  compile budget. Sourced by shell/awk consumers of a dump (tests/reject/
  run_reject_tests.sh, tests/cli/run_cli_tests.sh case10, tests/spec_mod0/
  check09_every_feature_toggles.sh) instead of each hand-rolling its own
  index map or a literal field-count guard — the D65 failure shape
  (docs/design/registry_built_status_memo.md's Correction section): two
  consumers hard-coded `NF != 15`, an appended 16th column (`built`) broke
  both, and the header-deriving consumer (tests/spec_mod0/spec_common.h,
  the contract's own house exemplar, left untouched by this file on
  purpose) did not notice. `table_col_index FILE COL [SECTION]` resolves a
  column BY NAME; `table_header_ncols FILE [SECTION]` is the header's own
  declared field count, never a literal; `table_awk_map [-s SECTION] FILE
  COL...` emits an `-v name=idx ...` string ready to splice into an
  `awk -F'\t' $(table_awk_map ...) '...'` invocation, so an awk PROGRAM
  reads `$module`/`$status`/... instead of a bare `$4` a reader has to
  cross-reference against the header by hand; `table_check_truthfulness
  FILE [SECTION]` is the contract's HEADER TRUTHFULNESS check (every data
  row's field count equals the header's declared count) — the durable
  final form of the old case10 `NF != 16` pin. Sections
  (`#section NAME`) are supported per the contract: reading a
  multi-section file with no `section` argument fails LOUDLY rather than
  silently parsing whichever header came last (nothing in the tree emits
  sections yet — `--emit-ir` is the pending [DD-8] candidate — so this path
  is exercised only by this file's own tests today). Every failure names
  what it could not resolve (the column, the file, the section) rather than
  returning an empty string a caller might silently splice into `$0` — a
  caller whose own resolution call can fail (table_awk_map,
  table_header_ncols) MUST check its exit status before using the result,
  or an unresolved column reads as an unset awk variable (field 0, or
  "") rather than a failure; tests/reject/run_reject_tests.sh's own comment
  at its call site names this trap. compliance_section.py is python and
  cannot source this file; it re-implements the identical two rules
  (comment-skip, "the last `#` line before the first data row is the
  header") and cross-checks its own `COLS` list against the dump's live
  header on every run (table_contract.md's GENERATOR AGREEMENT check), so
  the two implementations cannot silently disagree about what a header
  says. Also runnable as a command for a sabotage control or a non-shell
  caller: `bash tests/lib/table.sh table-col-index FILE COL [SECTION]`
  (and `table-header-ncols`/`table-awk-map`/`table-check`), same coda shape
  as `gen_timeout.sh`'s `secs`/`runsecs`/`cpusecs`, `table-`-prefixed
  because this file is SOURCED by scripts whose own `$1` is often a short
  word ("check") a collision with an unprefixed command name would
  silently misfire against.
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

- **mlscan.py** — [M6.2] wave C: WHERE IS `(?m)` IN FORCE, decided from the
  pattern TEXT. Three committed checks need that same answer, so it lives
  here once — `tests/codegen/run_mlinectx_identity.sh` (which patterns the
  `-DPCREC_NO_MLINECTX` knob can change, i.e. its corpus split),
  `tests/assertions/run_mline_diff.sh` (which patterns its python arm must
  skip under U11b), and the `.rxt` corpus generator (which blocks are
  `# pcre2-only`). It is the M2.12 rule applied to a fork that has not
  happened yet.
  **It is a GRAMMAR scan, never a call into pcrec**: a split derived from
  `Dfa.clsctx` or any other verdict pcrec computes about the pattern under
  test would be the check reading its own subject's answer.
  **Two traps, both of which cost a real run before this file existed.**
  (1) A `^` inside a bracket expression is a CLASS NEGATION, not an anchor —
  half this module's corpus is `[^c]`-shaped, and missing that excluded
  `(?m)[^c]{1,3}$`, the D47.5 GUARD CELL, from python cross-verification.
  Exactly the trap `run_wordctx_identity.sh` documents for `[\b]`.
  (2) Setting `m` is not enough; an ANCHOR must receive it — `(?m)\Aa`,
  `(?m)\Bfoo` and `a$(?m)` all set the option and build no multiline node,
  and a coarser split reported ten such patterns as a dead reference knob.
  Scoping follows the parser (bare runs mutate the enclosing scope, `(?m:`
  scopes to its body, `(?^...)` resets), verified against libpcre2 on
  `((?m))a$` and `(?:(?m))a$`. **It carries its own self-check**: run
  `python3 tests/lib/mlscan.py` — 27 cases including every trap above and
  the three scoping cells, exit 1 on any failure. A scanner nobody exercises
  is a scanner that drifts.

## Conventions

A script grouped by `run_group.sh` must isolate itself the same way every
other parallel path in this tree does: its own `mktemp -d` workdir, and
read-only against `build/pcrec`/`build/libpcrec.a` — never shared mutable
state with a sibling script in its group.

Maintenance: update this file when files are added/removed or their roles
change.
