# tt4m — [TT-4M] STEP 1 lane report

2026-09-08, lane tt4m, Sonnet, Mac-local. Charter: docs/dev/plan.md
[TT-4M] (chartered same hour by Frank, re-opening [TT-4]'s closed
batched-build question ON DARWIN). Full memo:
`docs/dev/tt4m_darwin_validation.md`, tooling/evidence:
`studies/tt4m_batchrun/`.

## What shipped

**A measured YES, bigger than [TT-4.1]'s closed Linux answer.** Shape L
(one gcc invocation naming N distinct pcrec-emitted `.c` sources plus a
generated dispatch `main()`, never concatenating source into one TU) beats
the harness's own one-gcc-call-per-pattern shape at every batch size
tried, on a 126-pattern / 413-case slice of `tests/base`:

| N | total wall | speed-up | total CPU | speed-up |
|---|---|---|---|---|
| baseline | 61.69s | 1.00x | 34.02s | 1.00x |
| 4 | 25.62s | 2.41x | 17.42s | 1.95x |
| 16 | 17.01s | 3.63x | 13.26s | 2.57x |
| 64 | 14.41s | **4.28x** | 12.19s | **2.79x** |

- **Answer identity: zero mismatches** across all 413 real cases at every
  N, plus an 8-pattern smoke test and a direct heterogeneous-`--features`
  pair (`atomic-groups` vs. `named-groups`) — confirming shape L needs
  none of [TT-4.1]'s TU-concatenation `--features`-homogeneity
  restriction, checked directly rather than assumed from the mechanism.
- **Degradation** reproduces [TT-4.1]'s Linux shape on darwin, at the real
  chartered N's: a batch's link failure is cheap (0.42s-5.96s across
  N=4-64) but recovering the other good members costs a full per-pattern
  recompile that scales linearly with N (0.84s-14.70s).
- **D77 residual trigger: NOT met.** pcrec's own spawn cost is ~1.5-2.8%
  of the batched path's total wall at every N, cross-validated against an
  independent standalone measurement (128 solo pcrec spawns, 0.455s
  wall). A multi-pattern pcrec CLI mode is not justified by today's
  numbers.
- **An unplanned second finding, bigger than the one this row set out to
  measure**: of N=64's 4.28x wall speed-up, the gcc-invocation lever
  contributes 2.65x on its own component, while fewer DISTINCT
  executables launched at case-run time (126 binaries → 2) contributes
  **11.79x** on its own — confirmed directly with a same-binary-reuse
  microbenchmark (4.72ms/call warm-reuse vs. baseline's 75.4ms/call
  average across mostly-cold binaries). This row's own scope decision
  (hold the per-case run SPAWN COUNT and argv shape identical between
  baseline and batched) held at the process-count level but not at the
  binary-identity level — batching narrows macOS spawn tax on two
  independent axes, not the one this row was chartered to isolate. Not
  smoothed over; the memo's own section on it names the mechanism and
  the confirming microbenchmark.

## A methodological finding, reported not hidden

126 of 128 collected patterns reached the sweep, not 128 — two
`tests/base/bounded_repeats.rxt` patterns contain a literal TAB character
inside the pattern text (`a{<TAB>1}` style), breaking the bare-TSV
manifest format `collect_patterns.py` (reused unchanged from [TT-4.1]'s
Linux prototype) uses. Affects both shapes equally, so it does not bias
the comparison — flagged in the memo rather than fixed, since fixing the
manifest format is outside this row's validation scope.

## Deliberately not done / owed to STEP 2

- Parallel-mode replication: this sweep is entirely SERIAL (box was
  holding for a concurrent full-population `run_encoding_checks.sh` for
  the whole construction phase — one-heavy-suite-at-a-time). [TT-4.1]'s
  Linux sweep found the single most important, easy-to-miss result was
  NON-monotonic under parallel dispatch (batch count near core count wins,
  not the largest N); this darwin pass never exercised that mechanism and
  does not claim to have.
- TU-concatenation (shape B) was not measured — shape L's own result
  (a clean win, no `--features` restriction needed) answers the brief's
  own conditional ("TU-concat measured second only if the link path
  leaves wins on the table") without needing it.
- `GENCFLAGS` axis family (`LINTGEN`/`CLANGGEN`/`RXTFLAGS`), routed/
  `frames-buffer=` cases, `perr`/head-target build paths, and the D45
  budget-wrapper overhead a real harness adoption would still pay per
  batch — all named as caveats in the memo, none modeled here.
- The box was not quiet for the timing sweep (load1 9.61 at the start,
  settling to 2.39 four minutes later; OS housekeeping — `logd`,
  Spotlight re-indexing — not another pcrec lane). Deltas are large
  (2-12x) and read as directionally solid, but a quiet-box re-run is
  worth doing before citing these numbers as a floor.

## Process notes for whoever reads this next

- The box-coordination hold (PID 84953, `tests/codegen/
  run_encoding_checks.sh`) was live for this lane's entire construction
  phase. Construction proceeded anyway (tooling, smoke tests, pcrec-only
  pool collection — none touch gcc or run multi-minute batches); all
  gcc-touching timing sweeps waited for the log's "checks failed: 0"
  line, confirmed via a backgrounded polling loop rather than repeated
  manual checks.
- `dispatch_gen.py` could NOT be reused verbatim from [TT-4.1]'s Linux
  prototype — it predates DD-14.FB's route argument and the current typed
  give-up codes (`work`/`recurse`/`internal`). Read the CURRENT
  `tests/harness/driver.c` before writing a new one rather than assuming
  an existing dispatch driver still matches the protocol.
- The 12x-plus binary-launch-cost effect was not obvious from the numbers
  alone — it surfaced because the "run" wall column dropped far more than
  the gcc column did, despite an explicit scope decision meant to hold
  that component constant. Worth checking a batching design's SIDE
  EFFECTS against its own stated scope, not just its headline metric.

## Commits

All on branch `lane/tt4m`, worktree `worktrees/tt4m`, not merged, not
pushed. Files: `studies/tt4m_batchrun/` (collect_patterns.py,
extract_cases.py, dispatch_gen.py, batchrun.py, CLAUDE.md, Makefile),
`studies/CLAUDE.md` update, `docs/dev/tt4m_darwin_validation.md`,
`docs/dev/CLAUDE.md` update, this report, and a `docs/dev/plan.md`
[TT-4M] STEP 1 delivery note (STATE left at `started` — STEP 2 harness
adoption is its own future row, not started).

**Validation: COMPLETE.** Every number in the memo and this report is
measured on this Mac, 2026-09-08, not owed. No background run pending.
