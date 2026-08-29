# tests/size — the artifact-size metrics log + corpus-level tripwire

[ART-SIZE.1b] (docs/dev/plan.md): the zero-cost size ratchet riding
`test-corpus`'s existing compile pass. No test corpus of its own — this
directory holds the WRAPPER and the CHECK, not `.rxt` files; the
population it measures is the whole tree's, discovered by
`tests/harness/run.sh` exactly as `test-corpus` always has.

## Files

- **run_size_log.sh** — drop-in replacement for `test-corpus`'s own
  `bash tests/harness/run.sh` recipe line (see the Makefile's `test-corpus:`
  target): threads `SIZELOG` through the SAME compile pass (no second gcc
  invocation anywhere — "riding the existing corpus" is the whole charter),
  then — ONLY on a full-corpus invocation (no file/dir arguments, matching
  `run.sh`'s own "no args = every `*.rxt` under `tests/`" rule) — assembles
  the raw rows into the stable, diffable `docs/dev/artifact_size_log.tsv`
  (D35's shape: stable filename, `git diff` shows what moved; deliberately
  NOT under `docs/measurements/` itself — see that file's own CLAUDE.md
  entry for why). A partial/targeted run (explicit files given) still gets
  raw rows at whatever `SIZELOG` path the caller sets directly, but this
  wrapper's own stable-file assembly is skipped — a developer's five-file
  spot-check must never silently overwrite the whole corpus's baseline.
  Exit code is `run.sh`'s own; an assembly problem is reported to stderr
  but never turns a passing corpus run red on its own — `check_size_tripwire.sh`
  is the separate step that can fail the build.
- **check_size_tripwire.sh** — THE ONE RED THIS ROW PRODUCES: the corpus-level
  max size and max gcc-CPU time seen in `docs/dev/artifact_size_log.tsv`
  (or `$ARTSIZE_LOG`), each pinned with headroom over the [ART-SIZE] census's
  own measured numbers (docs/dev/artifact_size_census.md) — see the script's
  own header for why the pins are NOT the census's raw numbers (a different
  compile shape: `-O1` compile+link with `driver.c`, not an isolated
  `-O2 -c`). PLUS the UNPINNED-MAX GUARD: a log that is empty, truncated
  after its own header was written, or below a hardcoded population floor
  fails LOUD rather than reading as "no blowup found" — the check-design
  lesson (memory `pcrec-check-design-lessons`) that a floor without a
  vacuity check measures nothing. A failure names the offending pattern,
  its number, the ratio over the pin, and the load at measurement. NO
  per-pattern gate exists anywhere in this directory — Frank's ruling on
  docs/dev/plan.md's [ART-SIZE.1b] row is explicit that per-pattern
  movement is examined post-test (`scripts/size_diff`), never gated.
  `make test-size` is the STANDALONE post-test check; in `make test` the tripwire runs as the tail of test-corpus's own recipe (a `test-size: test-corpus` prerequisite was skipped by `make -k` whenever the corpus's load cell went red — see the
  Makefile's own comment on why this is a deliberate, narrow exception to
  "no suite reads another's output": it runs strictly after test-corpus,
  reads a stable file-scoped artifact test-corpus produces as a byproduct,
  never a shared mutable workdir).

## Format of `docs/dev/artifact_size_log.tsv`

```
# artifact_size_log.tsv (docs/dev/plan.md [ART-SIZE.1b]) commit=<sha> date=<ISO8601 UTC> load1_at_start=<float> rows=<N> harness_args=(full corpus)
# pattern	engine	rungs	prefilter	size_bytes	gcc_cpu_s	gcc_wall_s	load1
<file>:<pattern-line>	dfa|vm	0x..|	hybrid|none|	<int>	<float>	<float>	<float>
...
```

`pattern` is `file:line` (the `.rxt` block's own coordinates), not the
regex text — stable across an emitter change, greppable straight back to
the corpus. `size_bytes` is the SELF-CONTAINED artifact's size (`.c`+`.h`
combined — the census's own correction, docs/dev/artifact_size_census.md
§6) with COMMENTS EXCLUDED, per `tests/lib/size_count.sh`'s definition
(verified byte-exact against the census's own Python classifier — see that
file's header and docs/testing.md's transcript).

**"COMMENTS EXCLUDED" IS LINE-BASED, AND AN EMITTER AUTHOR HAS TO KNOW
WHICH LINE.** The classifier recognises a line that STARTS a block (`/*`, or
`//`) and tracks the block to its end. A comment placed ABOVE a declaration
therefore costs zero counted bytes; the CONTINUATION lines of a comment that
begins after code on the same line — the `int x;   /* first line` … shape —
do not start a block and are counted as CODE. MEASURED at [ENG-ABS]
(2026-08-29): one new `rx_info` member whose comment used the trailing shape
put **+691 B into every one of the corpus's 2,875 artifacts** and moved the
corpus total 7.82 %; moving the same comment above the member took the
per-artifact cost to 38 B. Nothing is wrong with the classifier — a trailing
comment's continuation lines genuinely are not a block opener — but "the
emitted comments are free" is true only of the first shape, and the emitted
`struct rx_info` still carries two members (`scan`, `prefilter`) in the
second. `engine`/`rungs`/
`prefilter` are the D46 stamps (`RX_ENGINE`/`RX_VM_RUNGS`/
`RX_VM_PREFILTER`) read straight off the artifact; empty when the artifact
has no such stamp (a DFA artifact carries no rungs/prefilter at all).
`gcc_cpu_s` is user+sys CPU time (NOT wall) for the exact compile
`test-corpus` already performs (compile+link `gen.c`+`driver.c`, `-O1`);
`gcc_wall_s` rides along for comparison. `load1` is `/proc/loadavg`'s
1-minute figure at the moment that row's compile finished, so a
CPU-time reading taken under real contention is distinguishable from a
genuine blowup (the same load-context discipline `tests/lib/load_guard.sh`
uses one layer up).

## Measured overhead

The naive first cut (2x `awk` for size, 3x `sed` for stamps, 1x `awk` for
a CPU sum, 1x `cut` for load, 1x `grep` to parse `time`'s own output — 8
subprocess spawns per compile) cost **20.4%** of `test-corpus`'s own wall
time (75.6s -> 91.1s over 712 artifacts, `tests/base/*.rxt` at `PROCS=2`).
Consolidated into ONE subprocess per compile (`tests/lib/size_count.sh`'s
`size_count_row`, folding the size scan and the D46 stamp grep into a
single `awk` call) plus pure-bash arithmetic for the CPU-time sum and the
load reading (no `awk`/`cut`/`grep` at the call site at all): **1.79%**
(76.75s -> 78.13s, same 712-artifact sample). See
`tests/harness/run.sh`'s SIZELOG call site for the mechanism and
docs/testing.md "The artifact-size log" for the full transcript.

## Conventions

Nothing here writes into `tests/` (the harness's own compile output stays
under its own `mktemp -d` workdir, as always) — the log lands under
`docs/dev/`, never here. `run_size_log.sh` and `check_size_tripwire.sh` are
both read-only against `build/pcrec`/`build/libpcrec.a`, same as every
other section.

Maintenance: update this file when files are added/removed or the log
format changes.
