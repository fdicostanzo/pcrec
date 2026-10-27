# tests/lib — infrastructure shared by every suite

Not a test suite itself: helpers other suites' scripts and the Makefile's
section targets depend on.

## Files

- **assoc.sh** — [MACPORT] a bash-3.2-safe `declare -A` shim, for the handful of maps in this tree whose keys are genuinely STRINGS (filenames, feature-set text, C macro ...
- **loadavg.sh** — [MACPORT] `load1`/`load3`: a real load-average reading on darwin (`sysctl -n vm.loadavg`, no `/proc` at all) instead of the `2>/dev/null || echo 0` ...
- **shard_split.sh** — `shard_split N IN OUTPREFIX` then `NSHARD="$SHARD_COUNT"`: portable awk line-chunk split, exactly min(N, lines) balanced contiguous shards (BSD ...
- **ncpu.sh** — [MACPORT] `$NCPU`, resolved once: `nproc` (present via Homebrew on this box) else `sysctl -n hw.ncpu` else `getconf _NPROCESSORS_ONLN` else the project's ...
- **procs_default.sh** — [CORPUS-PCAP] `$PROCS_DEFAULT`, the shared answer to "how many concurrent WORKERS should a parallel test section default to" — a DIFFERENT ...
- **cc_resolve.sh** — [MACPORT] resolves a real GNU gcc when the bare `gcc` on PATH is Apple clang wearing gcc's name (verified: `/usr/bin/gcc --version` prints "Apple ...
- **c_artifact_cmp.sh** — `cmp_c_artifacts FILE1 FILE2` (adm71 item 5, 2026-09-19): compares two pcrec-emitted `.c` files for identity while ignoring the `#include` ...
- **unit_cc.sh** — [REVW.U L5-R0] `unit_build <outbin> <src.c> [extra args...]`, the ONE build for the unit tier's internal-property checks ...
- **timeout_bin.sh** — [TT-6] resolves `TIMEOUT_BIN` ONCE per process: the coreutils `timeout` binary every suite should invoke instead of a bare `timeout`.
- **gen_timeout.sh** — D45's ONE implementation of the generated-code compile budget — CPU-PRIMARY since the D45 third addendum (2026-08-16): `gen_cpu_secs` (10s plain / ...
- **size_count.sh** — [ART-SIZE.1b]'s ONE implementation of "the census's own definition" of an emitted artifact's SIZE: total source bytes minus `/* */`/`//` comment-line ...
- **lib_srcs.sh** — [MEMFN] R4a: `pcrec_lib_srcs ROOT`, THE ONE LIST of libpcrec's C sources for a test script that builds a compiler (or a TSan library) from source ...
- **table.sh** — [SR-11]'s ONE implementation of docs/spec/table_contract.md (the RULED contract for tabular `pcrec` command output — `#` comments, header-names-columns, ...
- **load_guard.sh** — [TT-10] (2026-08-25) a THIRD outcome — INCONCLUSIVE, never PASS, never FAIL — for a check whose budget is a CPU-time cap sized against a quiet box.
- **run_gen_timeout_tests.sh** — its own section in `make test` (`test-gentimeout`) — a positive control that the wrapper FIRES, plus a coverage assertion that every suite ...
- **run_group.sh** ([TT-2], 2026-08-15) — runs N independent shell commands (suite scripts) CONCURRENTLY as one Makefile section recipe, used by `test-codegen` ...
- **mlscan.py** — [M6.2] wave C: WHERE IS `(?m)` IN FORCE, decided from the pattern TEXT. Three committed checks need that same answer, so it lives here once — ...
- **san_scripts.txt** — [TT-9]'s ONE manifest for `make ubsan`/`make asan`/ `make san`'s suite list (a plain path-per-line text file, not a Makefile variable, so ...
- **san_excluded.txt** — [TT-9]'s reasoned exclusions: every `tests/**/run_*.sh` not in `san_scripts.txt` is listed here as PATH<TAB>REASON (prefix legend in its header; `TODO-WIRE`/`DEFER-PLAIN` are the open san-coverage gap). `run_codegen_tests.sh` audits both files and runs a planted-defect control.
- **test_trailer.sh** — `make test`'s COMPLETION TRAILER (2026-08-26, manager finding: `make -j12 test` printed "Waiting for unfinished jobs" on an early section's failure ...

## Conventions

A script grouped by `run_group.sh` must isolate itself the same way every
other parallel path in this tree does: its own `mktemp -d` workdir, and
read-only against `build/pcrec`/`build/libpcrec.a` — never shared mutable
state with a sibling script in its group.

Maintenance: update this file when files are added/removed or their roles
change.

  [CI-SHARD]: optional env `TRAILER_TITLE`/`TRAILER_LIST_NAME` let `make
  test-shard` word its heading and last line for the shard's list; unset, the
  text is unchanged.
- **spec_extract.sh** — [decfbB0b] sourced, never run: the registry check's
  hand-written-set extractors (`extract_md_table_values`,
  `extract_c_return_values`) over `docs/spec/match_api.md` §6.3's value-set
  tables — each directly under a `<!-- value-set: RX_NAME -->` marker, the
  anchor every caller uses (lane specclean, 2026-10-09, which also retired
  `extract_line_values`/`extract_prose_values`) — and a C function's
  `return "..."` literals, moved here verbatim from `tests/registry/axes_registry_check.sh`
  so it and `tests/codegen/run_fallback_table.sh` read the spec's sets
  through ONE implementation. Defines functions only.
- **compound_art.sh / compound_art.py** — [COMPOUND] B4 (lane cpb4,
  2026-10-12), sourced/imported, never run: ONE answer to "is this artifact a
  compound" (`compound_row`, `is_compound`), read off `<PREFIX>_COMPOUND`.
  A corpus sweep that holds a MACHINE stamp to the emitted text skips a
  compound and COUNTS the skip: a compound's machine stamps read
  `"compound"` (match_api.md §6.3.12) and are held in one place,
  `tests/codegen/run_dfa_stamps.sh`'s compound bucket.

- **p2gen.py / p2probe.c** — (lane langfix3, 2026-10-22; written by lane
  langfix2) `python3 tests/lib/p2gen.py SPEC.gen.py > FILE.rxt`: writes `.rxt`
  blocks whose expectations come from libpcre2 (p2probe.c, built on demand
  into build/p2gen/), never from pcrec. Each generated corpus's SPEC sits
  beside it as `<name>.gen.py` (K122-K127's five files). An author's tool,
  never run by make; the reference is libpcre2 10.46 on the Linux dev box.

- Also (one-line entries for these are in the history file): `run_san_group.sh`.

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__lib.md`.
