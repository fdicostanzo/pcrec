# studies/tt4m_batchrun/ — [TT-4M] darwin batched-build validation

Measures, on THIS Mac (M1, darwin), Frank's batched-build/single-executable
proposal (2026-09-08, plan.md [TT-4M] STEP 1): does linking N pcrec-
generated matchers (distinct `-p` prefixes) into ONE gcc call producing ONE
executable (`main()` dispatches by an integer selector) beat the harness's
own one-gcc-call-per-pattern shape, on THIS box, where the profile is
PROCESS DISPATCH ([TT-14]/[XARCH] half 1: the Mac loss is spawn tax, not
compute), not gcc CPU the way [TT-4.1]'s Linux census found.

Never touches `tests/harness/` or `src/` — read-only against both;
patterns are collected by running the worktree's own `build/pcrec`
directly, matcher runs use a hand-copied `tests/harness/driver.c` (never
modified) for the baseline and a purpose-built dispatch driver
(`dispatch_gen.py`) for the batched shape.

## Prior art reused (not re-derived)

`collect_patterns.py` and `extract_cases.py` were adapted, logic-unchanged
at the time, from `studies/tt4_batching/proto/` ([TT-4.1], the Linux
census/prototype that closed [TT-4] on 2026-08-23 — see
docs/dev/tt4_measurement.md). Their job (pull real `pattern`/`flags`/
`features` blocks and real `m`/`n`/`ms`/`ns` cases straight from `.rxt`
source, compile through the live `build/pcrec`) is machine-independent;
only the docstring header was re-dated for this lane. **`extract_cases.py`
NO LONGER MATCHES ITS ORIGIN'S LOGIC as of the r55 revision (lane tt4m2f,
2026-09-08, `docs/dev/reviews/2026-09-08-r55-tt4m-batching.md` finding
R55-5/num-F4)**: the inherited logic matched a pattern's cases by regex
TEXT ALONE against the first same-text block in its source file, silently
misattributing cases whenever a later block in the same file repeats the
same text under different `flags`/`features` (54 files carry this shape
across the corpus). Now keyed on the (pattern, flags, features) TRIPLE —
the same key `collect_patterns.py`'s own `dedup_key` already dedups the
manifest on — so a block this function resolves is always the SAME block
`collect_patterns.py` compiled the manifest's prefix from. See
`docs/dev/tt4m_step2a_parallel_sizing.md`'s R55-5 correction for the
measured effect (12 of 1,022 pool patterns misattributed; aggregate case
count barely moved by coincidence).

`dispatch_gen.py` is NOT reused from that prototype — it predates DD-14.FB
(the `frames-buffer=` route argument) and the current typed give-up codes
(`work`/`recurse`/`internal`), so a straight copy would silently mis-decode
today's `tests/harness/driver.c` protocol. This file's `dispatch_gen.py`
is written directly against the driver.c in this tree, decode()
behaviorally identical (R55-6/harn-2 FIXED, 2026-09-08, lane tt4m2f: the
first version fell through to a plain byte copy on a TRAILING LONE
BACKSLASH where driver.c's own decode() refuses it as a malformed escape
— now refuses it identically, `free`+`NULL`, "trailing backslash in
subject"; population ~zero in every pool run so far, the divergence was
in the untested claim rather than in any observed result), give-up naming
byte-identical, DEFAULT ROUTE ONLY (see its
own header for the stated scope limit — no `_search_in`/`_match_in`
cross-check, since every pool here is drawn from `tests/base`, which has
no `frames-buffer=` blocks).

## Files

- `collect_patterns.py` — pool collection (prefix per pattern, manifest.tsv).
- `extract_cases.py` — real per-pattern cases from the source `.rxt` (cases.tsv).
- `dispatch_gen.py` — N-way selector driver for the batched shape (shape L).
- `batchrun.py` — the measurement driver. Three subcommands:
  - `baseline` — the harness's own unbatched shape: per pattern, one pcrec
    spawn (prefix `rx`, fresh dir) + one gcc spawn (`tests/harness/
    driver.c` unmodified) + one `timeout`-wrapped matcher-run spawn per
    case.
  - `batched` — shape L: per batch of N, N pcrec spawns (distinct prefixes,
    one shared dir) + **ONE** gcc spawn (`dispatch.c` plus the N `gen.c`
    files named as SEPARATE arguments on one command line — each its own
    translation unit by construction, which is what dodges [TT-4.1]'s
    `PCREC_FEATURE_SET`/`PCREC_FEATURE_MODULES` TU-concatenation collision
    without needing that memo's `--require-features` homogeneity
    restriction) + the same per-case run shape as baseline.
  - `failure-iso` — plants a syntax error in one batch member's `gen.c`
    copy, measures the batch link's all-or-nothing failure and the
    per-pattern fallback cost to recover the batch's other members.
  - `parallel` — [TT-4M] STEP 2 (2a), added 2026-09-08 (lane tt4m2): P
    CONCURRENT shape-L batch pipelines. Shards the pool's BATCHES (not raw
    rows) round-robin across P workers, writes each a private sub-pool,
    and launches each as an independent `batched` SUBPROCESS (the same
    self-reinvocation shape `tests/harness/run.sh`'s own `PROCS>1` fan-out
    uses). Wall is the parent's own outer wall clock; CPU is read two ways
    (each worker's own self-reported total, summed, AND the parent's own
    `RUSAGE_CHILDREN` after every worker is reaped) and cross-checked
    against each other. See `docs/dev/tt4m_step2a_parallel_sizing.md` for
    the N x P sweep this subcommand exists to run.
  Every subcommand writes a JSON file (spawn counts by kind, wall/CPU by
  kind, and every case's `(stdout, exit code)` for the answer-identity
  diff) and prints the spawn summary to stdout.

**Scope decision, stated once here rather than per-file**: the per-case
matcher-run shape (`timeout $RUN_SECS exe ... subj pos`) is held IDENTICAL
between `baseline` and `batched` — this isolates the gcc-invocation-count
lever alone. Exec-batching (one process per PATTERN reading all its cases,
collapsing the per-case spawn too) is a SEPARATE lever [TT-4.1]'s Stage A2
already measured on Linux (5.57x net of the timeout-binary effect) and is
not what this lane's charter asks about.

## Reproduce

    cd worktrees/tt4m   # or wherever this branch is checked out
    make -j4 CC=gcc-16
    mkdir -p /tmp/tt4m_pool
    python3 studies/tt4m_batchrun/collect_patterns.py \
        --pcrec build/pcrec --outdir /tmp/tt4m_pool \
        --count 128 --require-features "" tests/base
    python3 studies/tt4m_batchrun/extract_cases.py /tmp/tt4m_pool/manifest.tsv \
        > /tmp/tt4m_pool/cases.tsv
    python3 studies/tt4m_batchrun/batchrun.py baseline \
        --pool /tmp/tt4m_pool --pcrec build/pcrec --cc gcc-16 \
        --timeout-bin timeout --driver tests/harness/driver.c \
        --out /tmp/tt4m_pool/baseline.json --workdir /tmp/tt4m_pool/base_wd
    python3 studies/tt4m_batchrun/batchrun.py batched \
        --pool /tmp/tt4m_pool --pcrec build/pcrec --cc gcc-16 \
        --timeout-bin timeout --batch-size 16 \
        --out /tmp/tt4m_pool/batched.json --workdir /tmp/tt4m_pool/batch_wd

Failure isolation: `batchrun.py failure-iso --pool /tmp/tt4m_pool --pcrec
build/pcrec --cc gcc-16 --batch-size 16 --out /tmp/tt4m_pool/failiso.json
--workdir /tmp/tt4m_pool/failiso_wd`.

`make check` (this directory's own Makefile) runs the 8-pattern smoke test
above end to end plus the answer-identity diff, confirming the tooling is
live before a full sweep. Results/logs are NOT committed (scratch,
regenerable) — only this directory's own `.py` files and the memo they
feed (`docs/dev/tt4m_darwin_validation.md`) are.

Machine context: this Mac (M1, 10 cores per `sysctl -n hw.ncpu`), gcc-16
16.2.0 (Homebrew), bare `timeout` on this box IS GNU coreutils 9.11 (NOT
the uutils-tax situation [TT-4.1]'s Linux box had — see the memo). Measured
2026-09-08.

Maintenance: update this file when files are added/removed or the
reproduce command changes.
