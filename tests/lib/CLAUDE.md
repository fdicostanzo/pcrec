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
  **[K37] (2026-08-25) IT ALSO OWNS THE COMPILER'S OWN INVOCATION BUDGET,
  ONE HELPER EVERY SUITE CALLS RATHER THAN EACH RE-WRAPPING ITS OWN CALL
  SITES**: `pcrec_timeout_secs` (20s plain / 60s sanitizer,
  `PCRECTIMEOUT`/`PCRECTIMEOUT_SAN` — a different quantity from the
  generated-code numbers above, calibrated separately: pcrec's own compiles
  are sub-millisecond to under a second even on the worst corpus case) and
  `pcrec_run [--hostile] <pcrec-argv...>`, which every harness script now
  routes a compiler invocation through instead of calling `"$PCREC"`/
  `build/pcrec` bare. Fixes docs/dev/known_issues.md K37: sabotage row S159
  made the compiler loop forever on `((?1)*a)`, and
  `tests/recursion/run_recursion_diff.sh` called the compiler with no bound
  at all, turning a `make mech` row that should have read one FAILED ARM
  into a 50-minute hang a human had to kill by PID. TWO PATHS, MEASURED
  rather than uniform: the default is a bare `"$TIMEOUT_BIN"
  "$(pcrec_timeout_secs)"` wrap (~2.5ms/call, MEASURED 2026-08-25) —
  `scripts/watchdog` is used instead (wall + tree-RSS + CPU + a
  `build/watchdog.log` line) only when the invocation's last argument (the
  pattern, pcrec's own `--` convention) is CALL-BEARING (`(?R)`, `(?0)`,
  `(?N)`, `(?±N)`, `(?&name)`, `(?P>name)`, `\g<...>`, `\g'...'` — S159's own
  construct family) or the caller passes `--hostile` explicitly, because
  watchdog's own per-call cost is ~171ms/call (MEASURED, ~68x
  `"$TIMEOUT_BIN"`'s) and routing the ~360 call sites this fix swept through
  it unconditionally would multiply the harness's wall time rather than
  merely bound it — see the function's own comment in this file for the
  full measurement and the construct list. `tests/codegen/
  run_codegen_tests.sh`'s "[K37] THE BARE-COMPILER-CALL GUARD IS STRUCTURAL"
  is the standing check: every `tests/**/*.sh` compiler-token site must be
  guarded (`pcrec_run`/`"$TIMEOUT_BIN"`/`gen_run`/`gen_cc` on the line) or
  match a reasoned, non-vacuity-checked allowlist entry, so a new bare call
  site cannot recur silently. **NOT COVERED**: two python callers
  (`tests/registry/compliance_section.py`, `tests/vm/vm_oracle.py`) invoke
  the compiler via `subprocess.run()` with no `timeout=` at all — the
  identical hazard, outside this bash-only mechanism's reach; recorded in
  K37's own known_issues.md entry, not silently swept into this fix.
- **size_count.sh** — [ART-SIZE.1b]'s ONE implementation of "the census's
  own definition" of an emitted artifact's SIZE: total source bytes minus
  `/* */`/`//` comment-line bytes (docs/dev/artifact_size_census.md §5's
  `prose` bucket). `size_count_bytes FILE...` sums that quantity over any
  number of files, forcing `LC_ALL=C` internally (MEASURED: under this
  box's ambient `en_US.UTF-8`, `awk`'s `length()` counts CHARACTERS, not
  bytes, and a handful of `[DD-14.FB]`-annotation comments contain
  multi-byte UTF-8 punctuation — this silently undercounted a real
  artifact's prose bytes by 8 and 1 respectively; forcing the locale inside
  the function rather than trusting an inherited export fixes it
  regardless of caller). VERIFIED byte-for-byte against
  `docs/dev/artifact_size_census/census.py`'s own `attribute_source()`
  Python classifier on a real split artifact (both a small synthetic
  pattern's `gen.c`/`gen.h` and the corpus's own largest witness,
  `((a)|ab){4000}c`) — a FLAT top-to-bottom comment scan agrees with the
  census's depth-aware, function/table-tracking classifier exactly,
  because the census's own comment-detection rule is applied verbatim at
  every nesting depth with no depth-dependent variation (this file's own
  header has the full argument). `size_count_row FILE_C FILE_H` is the
  ONE-SUBPROCESS combination `tests/harness/run.sh`'s SIZELOG call site
  actually uses: the same size scan PLUS the D46 stamp extraction
  (`RX_ENGINE`/`RX_VM_RUNGS`/`RX_VM_PREFILTER`, same spellings
  `census.py`'s `extract_stamps()` greps) in ONE `awk` invocation, because
  the first cut of that call site (2x `awk` + 3x `sed` + 1x `awk` + 1x
  `cut` + 1x `grep` — 8 spawns per compile) cost 20.4% of `test-corpus`'s
  own wall time on a 712-artifact sample; consolidated to 1 spawn, MEASURED
  1.79% (see this function's own header and docs/testing.md "The
  artifact-size log" for both transcripts). Sourced by
  `tests/harness/run.sh` only — no other suite needs an artifact's byte
  count today.
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
- **load_guard.sh** — [TT-10] (2026-08-25) a THIRD outcome — INCONCLUSIVE,
  never PASS, never FAIL — for a check whose budget is a CPU-time cap sized
  against a quiet box. `tests/resource`'s 45s compile-CPU cap is already
  CPU-accounted through `scripts/watchdog -c` and still measured going RED
  under real contention (K31 addendum, docs/dev/plan.md): CPU-time
  ACCOUNTING itself inflates under contention, not merely wall stretching.
  `load_guard_ratio` reads the 1-minute load average / `nproc`;
  `load_guard_tripped` compares it against `LOAD_GUARD_RATIO` (default
  2.0, justified in the file's own header from this project's measured
  "~2x CPU inflation" figure and the K31 addendum's own 2.58 failure
  ratio) and returns true when the box is too contended for a CPU-bounded
  verdict to mean what it says. Callers own their own THIRD counter
  (`inc()`, printed and totalled separately from pass/fail) and check the
  guard only at the point a watchdog CPU/wall kill (123/124) actually
  fires — every other outcome keeps its full meaning regardless of load.
  Sourced by `tests/resource/run_resource_tests.sh` and
  `tests/counterk/run_counterk_tests.sh`; see `docs/testing.md`'s "The
  load guard" section for the full measurement and the validated numbers.
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

  **[K35], 2026-08-25 ([DD-14] close):** it also `export LC_ALL=C` right
  after `set -u`, so no grouped script inherits the ambient locale — a
  `sort -u` under `en_US.UTF-8` collates punctuation as ignorable and
  silently drops a third of a regex corpus (1,784 vs 2,758 patterns,
  measured). The same export sits in `tests/harness/run.sh`; both are the
  GENERAL half of K35's fix, with every site guarded individually as well.

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
- **san_scripts.txt** — [TT-9]'s ONE manifest for `make ubsan`/`make asan`/
  `make san`'s suite list (a plain path-per-line text file, not a Makefile
  variable, so `tests/codegen/run_codegen_tests.sh`'s "[TT-9] THE SANITIZER
  SUITE LIST IS STRUCTURAL" check can read the identical list from bash
  without parsing Makefile syntax — see its own header for the full note).
  Fixes the drift the ruling names: wave B+C's first patch added
  `tests/recursion/run_recursion_diff.sh` to `ubsan`'s own hand-maintained
  copy and `san` silently never ran it, because there were three copies to
  keep in sync and nothing that checked they agreed. Also added the five
  `run_*_diff.sh` scripts the [TT-9] structural check's own sweep found
  absent from all three lists with no stated reason (the ruling's lookaround
  example, plus three sibling scripts in `tests/assertions/` the search
  also surfaced) — all five compile generated C exactly like their already-
  listed siblings.

- **test_trailer.sh** — `make test`'s COMPLETION TRAILER (2026-08-26,
  manager finding: `make -j12 test` printed "Waiting for unfinished jobs"
  on an early section's failure and launched NO FURTHER targets —
  `test-premul-table`, last in the Makefile's `TEST_SECTIONS` list, never
  ran in two batteries, invisible to the checks-passed/checks-failed COUNT
  aggregation since an unlaunched target contributes nothing to either
  side of the sum). Paired with the Makefile's own `test:` recipe, which
  now invokes `$(MAKE) -k TEST_TRAILER_DIR=<dir> $(TEST_SECTIONS)` (the
  parent's jobserver is inherited automatically, so `-j` parallelism is
  unaffected) instead of listing the sections as prerequisites; every
  section target's recipe touches `<dir>/<name>.ran` as its FIRST line,
  before running its real script, so the marker means "make launched this
  recipe" independent of whether the recipe itself then passed. This
  script counts markers against the section-name list its CALLER passes
  (never re-derives the list from the Makefile — one list, two uses, not
  two lists), prints `sections ran: N/M`, and names every missing section;
  a zero-argument call is a hard failure (an empty expected list would
  read as a vacuous 0/0 pass). See docs/testing.md "make test completion
  trailer" for the reproduced bug, the fix's two halves, and the
  detect-demonstration transcripts (a genuinely-skipped section under the
  old shape; the trailer's own 0/N detection when a shared prerequisite
  fails even under the new one).

## Conventions

A script grouped by `run_group.sh` must isolate itself the same way every
other parallel path in this tree does: its own `mktemp -d` workdir, and
read-only against `build/pcrec`/`build/libpcrec.a` — never shared mutable
state with a sibling script in its group.

Maintenance: update this file when files are added/removed or their roles
change.
