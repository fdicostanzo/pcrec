# studies/tt4_batching/proto/ — [TT-4.1] Stage B/A2 batching prototypes

Measures, on real generated matchers (never the harness — patterns are
collected by running `build/pcrec` directly), two independent levers:
whether batching COMPILATION (one TU/link per N patterns instead of one
gcc call per pattern, Stage B) is actually faster under the harness's own
execution shape at several batch sizes, and whether batching EXECUTION
(one process reading all of a pattern's cases instead of one process
spawn per case, Stage A2's addendum) is faster than
`tests/harness/run.sh`'s own per-case `timeout` shape. Neither touches
the harness. See docs/dev/tt4_measurement.md's "Stage B" and "Stage A2:
the remainder" sections for the numbers and what they mean; this file
documents how to reproduce them.

## Files

- **collect_patterns.py** — extracts real `pattern`/`flags`/`features`
  blocks from `.rxt` files (the same directive mapping
  `tests/harness/run.sh` uses: `flags i` -> `-i`, `features LIST` ->
  `--features LIST`, `perr` blocks skipped) and compiles each through
  `build/pcrec` with a DISTINCT sequential prefix (`rx0000`, `rx0001`,
  ...) into an output directory, stopping once `--count` patterns have
  compiled successfully. `--require-features` restricts collection to one
  homogeneous `--features` bucket — load-bearing, not cosmetic, because
  TU-batching two matchers built with DIFFERENT `--features` values fails
  to compile (see the memo's "Emitter-side obstacles" section:
  `PCREC_FEATURE_SET`/`PCREC_FEATURE_MODULES` are unprefixed `#define`s
  written directly into each `gen.c` body).
- **dispatch_gen.py** — emits a small C driver reproducing
  `tests/harness/driver.c`'s exact decode/match/nomatch/steps/frames
  protocol (byte-for-byte verified against it), but selecting WHICH of N
  distinctly-prefixed matchers to call by an integer index (`argv[1]`) —
  needed because shapes A/B put several matchers in one binary and
  `driver.c` itself is hardcoded to the harness's own fixed `-p rx`
  prefix.
- **bench.py** — the sweep. Three shapes (C baseline / A link-batching /
  B TU-batching) at batch sizes N in `--sizes` over a fixed `--total`
  pool, each cell median/min of `--reps` runs, both `serial` (clean
  per-call attribution) and `parallel` (`--parallel`-way, matching the
  harness's own `PROCS=$(nproc)`) via `concurrent.futures`. Shape C does
  NOT depend on N (it is always the same one-shot-per-pattern workload
  regardless of what A/B are being compared against at a given N) and is
  measured ONCE per mode, not once per N — a bug in the first version of
  this file re-measured it redundantly inside the N loop (5x wasted runs,
  caught and fixed 2026-08-23 before it burned the row's time budget).
  Also reports peak RSS (`/usr/bin/time -v`) on the largest-N TU compile,
  and runs a correctness check (baseline vs. batched executable output,
  byte-for-byte, on a few subjects per pattern from the largest batch).
  `--failure-isolation N` plants a syntax error in one batch member and
  measures shape B's all-or-nothing compile-failure cost plus the
  per-pattern fallback cost to recover the batch's OTHER good members —
  the fallback must compile against the SAME (corrupted) source directory
  the batch failure used, or the planted error is never exercised and
  every fallback compile trivially "succeeds" (a bug caught and fixed
  2026-08-23, same day as the baseline-remeasurement one).
- **extract_cases.py** — [Stage A2, 2026-08-23] pulls the REAL `m`/`n`/
  `ms`/`ns` case lines that follow a collected pattern's own `pattern`
  line in its SOURCE `.rxt` file (never synthetic cases) — the same
  subject/startpos values `tests/harness/run.sh` itself would run.
- **multidriver_gen.py** — [Stage A2] emits a ONE-PATTERN driver that
  reads ALL of that pattern's cases from stdin (`subject<TAB>startpos`
  per line) in a loop inside a SINGLE process, instead of
  `tests/harness/driver.c`'s shape of one process per case. A tiny,
  purpose-built copy — never `tests/harness/driver.c` itself.
- **bench_execcost.py** — [Stage A2] the manager-requested exec-cost
  comparison: for a fixed pattern sample and their real cases, times (i)
  the harness's OWN shape (`tests/harness/run.sh:356`'s exact one-
  `timeout`-spawn-per-case pattern, reproduced in a generated bash
  script) against (ii) one process per PATTERN via `multidriver_gen.py`,
  3 reps, median. `--timeout-bins` (added 2026-08-23, second manager
  finding) runs shape (i) once per listed `timeout` binary — this box has
  BOTH uutils coreutils' `timeout` (`/usr/bin/timeout`, the real one
  `run.sh` uses) and GNU coreutils' (`/usr/bin/gnutimeout`) installed,
  and they are NOT equivalent: uutils costs ~108.7ms/call at ~0 CPU, GNU
  ~4.2ms — a THIRD, independent lever this file's first version had
  conflated into the (i)-vs-(ii) comparison. See
  docs/dev/tt4_measurement.md's "The `timeout` binary itself" and "exec-
  cost prototype cell" sections for the decomposed result (uutils-harness
  1.00x / GNU-harness 31.18x / one-process-per-pattern 173.59x, i.e. the
  TRUE exec-batching-specific lever beyond just fixing the timeout binary
  is only 5.57x, not the 245.59x this row first reported before the
  three-way split existed) and why the remaining ratio should scale UP,
  not down, at `corpus`'s real ~10-cases/pattern average.
- **results/** — committed sweep output (`*_results.json` from `bench.py`,
  `*_bench.log` its stdout) for the two pools used in the memo: `corpus`
  (256 patterns, `tests/base`, default/no-`--features` bucket — the
  worst gcc-bound section per Stage A) and `atomic` (64 patterns,
  `tests/atomic_groups` restricted to `--features atomic-groups` — the
  second worst); plus `execcost.log` (Stage A2's exec-cost cell output).
  Machine/date context: studies/tt4_batching/CLAUDE.md.

## Reproduce

    cd /path/to/pcrec-worktree
    make -j$(nproc) all
    mkdir -p /tmp/tt4proto
    python3 studies/tt4_batching/proto/collect_patterns.py \
        --pcrec build/pcrec --outdir /tmp/tt4proto/corpus_pool \
        --count 256 --require-features "" tests/base
    python3 studies/tt4_batching/proto/bench.py \
        --patterns /tmp/tt4proto/corpus_pool --outdir /tmp/tt4proto/out \
        --sizes 1,4,16,64,256 --total 256 --reps 3 --parallel $(nproc)

Failure isolation: `bench.py --patterns /tmp/tt4proto/corpus_pool --outdir
/tmp/tt4proto/out --failure-isolation 16`.

Exec-cost cell: `python3 studies/tt4_batching/proto/bench_execcost.py
--patterns /tmp/tt4proto/corpus_pool --limit 16 --outdir /tmp/tt4proto/execcost
--reps 3` (uses the SAME `corpus_pool` collected above — no separate
collection step).

Pattern pools themselves are NOT committed (scratch, regenerable from the
command above); only the sweep's own `results.json`/log output is, under
`results/`.

Maintenance: update this file when files are added/removed or the
reproduce command changes.
