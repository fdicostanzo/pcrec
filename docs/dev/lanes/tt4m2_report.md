# tt4m2 report — [TT-4M] STEP 2 (2a) + (2b)

Lane tt4m2 (sonnet), 2026-09-08, branch `lane/tt4m2`, worktree
`worktrees/tt4m2`. Design + measurement only, per brief: nothing under
`tests/harness/` or `src/`. Changes live in `studies/tt4m_batchrun/`
(extension), `docs/dev/` (the 2a memo + CLAUDE.md updates), and
`docs/design/` (the 2b note + CLAUDE.md update).

## Delivered

- **(2a) Parallel-dispatch N x P sizing measurement.**
  `docs/dev/tt4m_step2a_parallel_sizing.md`. Extended `studies/
  tt4m_batchrun/batchrun.py` with a new `parallel` subcommand (P
  concurrent shape-L batch pipelines, self-reinvocation shape matching
  `tests/harness/run.sh`'s own `PROCS>1` fan-out). Collected a
  1,022-pattern/7,729-case cross-corpus pool (larger than STEP 1's
  `tests/base`-only slice, sized so N=128 x P=12 has enough batches to be
  meaningful) and swept N in {16,64,128} x P in {4,8,12} — the full 3x3
  grid the brief asked for, plus a same-pool serial (unbatched) baseline
  and a same-pool `failure-iso` re-run at all three N.
  - **Knee: P=8 at every N** — this box's own performance-core count (8
    of 10 `hw.ncpu`). P=8->P=12 buys 0-5% wall and COSTS up to 15% more
    CPU to contention; at N=128 it starves 4 of 12 requested workers
    outright (only 8 batches exist), reproducing [TT-4.1]'s Linux
    non-monotonicity in the form this box's population produces it.
  - **Recommendation: N=64, P=8.** Wall time is a near-flat plateau
    across N=16-128 at P=8 (28.70-33.33s, ~9% spread) while worst-case
    degradation-recovery cost scales linearly with N (3.61s at N=16 to
    29.22s at N=128) — N=64 sits at the grid's near-minimum wall (29.36s)
    with half of N=128's blast radius (14.72s recovery) for a
    statistically indistinguishable wall-time win.
  - **Sensitivity** (asymmetric, stated explicitly): getting P too small
    costs ~1.5-1.7x wall uniformly; getting P too large costs little wall
    but real CPU and, at large N, idle workers; getting N wrong within
    16-128 costs almost nothing in throughput (~9%) but scales the
    worst-case recovery cost 8x (3.6s to 29.2s).
  - **Zero answer-identity mismatches** across all 9 cells, pairwise, over
    7,706 distinct cases.
  - **K44 relief (§5): suggestive, not conclusive.** Peak load1 during the
    sweep (10.44, transient) is ~4.4x below K44's documented
    47.6-at-PROCS=12, but the comparison is not apples-to-apples (K44 is
    a full multi-section `make -j12 test`; this is an isolated
    corpus-compile prototype) — named as owed to STEP 2c/2d's real
    implementation.
  - **Addendum**: the same-pool serial baseline (547.52s wall/320.60s
    CPU) landed after the grid — **18.65x wall speedup end to end** at
    the recommended N=64/P=8 cell, bigger than STEP 1's 4.28x because it
    combines both of STEP 1's levers WITH this row's own parallel-dispatch
    lever. Honest caveat stated in the memo: this compares
    batching+parallelism TOGETHER against neither in isolation (today's
    real `run.sh` is already unbatched-but-parallel); decomposing the two
    contributions needs a `cmd_baseline --procs` this lane did not build
    (named as owed, D77 — the recommendation does not depend on it).

- **(2b) Design note.** `docs/design/tt4m_harness_batching.md`, all eight
  items the brief named:
  1. **Batching unit**: fixed-N (64) chunks of consecutive `pattern`
     blocks WITHIN one file's own parse (measured the corpus's own
     block-count distribution while sizing this: 1-357 blocks/file, mean
     18.7 — a general mechanism that degenerates correctly at both a
     small and large file's ends, per the project's own
     general-mechanisms convention). 2a's P maps onto `run.sh`'s
     EXISTING `PROCS` knob, not a new one.
  2. **Dispatch protocol**: a harness-local `dispatch.c` per batch
     (STEP 1/2a's `dispatch_gen.py` shape, default-route only), kept
     by-name-lookup-compatible for `[V-E]`'s later implement-then-replace.
  3. **SIZELOG**: option (a) — `-c`-per-TU compiles inside the batch's
     one gcc process, keeping per-pattern gcc CPU/wall EXACT. **Found,
     not merely chosen, that option (c) is actually unavailable**:
     `test-corpus:`'s own Makefile recipe threads SIZELOG through EVERY
     full-corpus run unconditionally, so "SIZELOG stays unbatched" would
     mean `make test-corpus` — the exact target this row exists to speed
     up — never sees batching's benefit at all.
  4. **Axes**: GENCFLAGS/LINTGEN/CLANGGEN/the san axes/the deny-force
     sweep all survive unmodified (confirmed by reading the actual
     env-var threading in `run.sh`/`run_axes.sh`, not assumed) — flags
     explicitly that `-fsanitize=` runtime linkage must ride option (a)'s
     reintroduced link step, citing `[TT-3]`'s own `_gen_cc_run`
     split-then-link precedent as the pattern to copy.
  5. **Mech**: grepped all eight `tests/harness`-anchored sabotage rows
     (S11/S43/S194/S196/S198/S199/S203/S205) — none anchor on the
     compile/link invocation line itself, all sit in the `.rxt`-parsing
     arm chain upstream of and unaffected by batching; S43 needs a stated
     budget-scaling note, not a re-derivation. One new mech row (a
     planted "batch never falls back to per-pattern recovery" sabotage)
     is named as owed to 2c.
  6. **Degradation/attribution**: a two-tier design — D88's per-TU gcc
     diagnostics attribute a common single-member failure for free
     (relink minus that member), with 2a's own measured linear-in-N
     recovery cost reframed as that path's RARE worst case (a
     link-only failure gcc cannot attribute), not the typical cost. Batch
     compile budget = D45's existing per-pattern GENCPU/GENTIMEOUT
     multiplied by N (linear-additive derivation, no new measurement
     needed). Per-case timeout wrapping unchanged.
  7. **Linux parity**: shape L is portable gcc, no darwin-isms. Predicts
     (not assumes) Linux's win is dominated by the SMALLER of STEP 1's
     two levers — the bigger one (11.79x per-binary-launch collapse) may
     not exist on Linux at all — names the executor-arm validation plan.
  8. **Rollout**: opt-in (`HARNESS_BATCH=N`) first, converging to
     default-on (not opt-in-forever like `CCACHE=1`) once a full `make
     test` is answer-identical on both platforms with mech/tripwire
     clean — the stated flip condition.
  States plainly what stays unchanged: the `.rxt` driver protocol, every
  expectation kind, both oracle tiers, the known-fail ratchet.

- **Incidental fix**: `studies/tt4m_batchrun/Makefile`'s `CC ?= gcc-16`
  was a silent no-op (`CC` is one of make's built-in variables, already
  implicitly defined, so `?=` never fires) — found during this lane's own
  tooling-validation step (`make check` was compiling the smoke pool with
  Apple clang, not gcc-16, the whole time, and happened to pass anyway
  since the 8-pattern smoke pool contains no shape clang rejects). Fixed
  with an `ifeq ($(origin CC),default)` guard; verified the corrected
  `make check` now actually invokes `gcc-16`.

## Validation

- `studies/tt4m_batchrun/` tooling: `python3 -c "import ast; ast.parse(...)"`
  syntax-checked after every edit to `batchrun.py`; `make check` (8-pattern
  smoke, both before and after the `Makefile` fix) — 0 mismatches both
  times, confirming the fix changed the compiler used, not the outcome.
- New `parallel` subcommand: smoke-tested at N=4/procs=2 on a 16-pattern
  pool (0 mismatches vs baseline) before the full sweep was trusted.
- Full N x P sweep: 9 cells, 1,022 patterns/7,729 real cases each, zero
  answer-identity mismatches pairwise across all 9 (COMPLETE, numbers
  inline above and in `docs/dev/tt4m_step2a_parallel_sizing.md`).
- Same-pool serial baseline: COMPLETE (547.52s wall/320.60s CPU, folded
  into the memo as an addendum after the grid).
- Same-pool `failure-iso` at N=16/64/128: COMPLETE, reproduces STEP 1's
  detect-cheap/recovery-linear-in-N shape on the larger, cross-corpus
  population; every fallback outcome matched expectation (0 unexpected
  results at any N).
- No `make`/`make test` run against the main tree — this lane never
  touched `tests/harness/` or `src/`, so the top-level suite is unaffected
  by construction; `make -j4 CC=gcc-16` (the worktree's own build) was run
  once at lane start to produce `build/pcrec` for the prototype tooling.

**Nothing is OWED from this lane's own scope.** The two items explicitly
named as owed in the memo (an unbatched-parallel baseline to decompose
the 18.65x figure; a quiet-box re-run) are D77-deferred by this lane's own
judgment — neither blocks 2b's design or its own recommendation, and
building them without a stated need they're triggered by would be the
D77 violation the project's own convention warns against.

## Files touched

- `studies/tt4m_batchrun/batchrun.py` — new `parallel` subcommand.
- `studies/tt4m_batchrun/Makefile` — `CC` built-in-variable fix.
- `studies/tt4m_batchrun/CLAUDE.md` — documents the new subcommand.
- `docs/dev/tt4m_step2a_parallel_sizing.md` — new, the 2a memo.
- `docs/dev/CLAUDE.md` — new file-list entry.
- `docs/design/tt4m_harness_batching.md` — new, the 2b design note.
- `docs/design/CLAUDE.md` — new file-list entry.

## Handback

Branch `lane/tt4m2`, 4 commits, all pushed to the branch (not merged —
this lane never merges). Both deliverables (2a memo, 2b design note) are
committed and complete; validation numbers are inline above and in the
memo itself, nothing left running in the background. `docs/dev/plan.md`'s
[TT-4M] row is NOT edited by this lane (left for the manager, matching
how STEP 1 was recorded) — the summary above is written so it can be
lifted directly into that row's STATE update. Next: the plan row's own
light D6 panel on the design note, then STEP 2c (implementation, tier
decided off this note) and 2d (acceptance: full `make test`
answer-identical on darwin AND the Linux executor arm, per item 8's flip
condition).
