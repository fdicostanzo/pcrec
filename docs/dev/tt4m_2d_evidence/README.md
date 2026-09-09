# [TT-4M] 2d acceptance evidence (2026-09-09, the R55-10 archive)

The four full `make test` runs behind the HARNESS_BATCH merge decision.
Logs themselves were session-scratch (multi-MB); this archive carries the
derived numbers, fingerprints and method — enough to re-derive the
verdict, and the RE-RUN RECIPE is one command per row.

| run | tree | shape | wall | user | sys | counts-hash | FAILs |
|---|---|---|---|---|---|---|---|
| A | main (ce223e1f+) | unbatched, -j4 PROCS=3 | 2269s (11:49:29→12:27:18) | — | — | fc8247017b39cd31c49366f5f94cbb0d | 170 |
| B | tt4m3 worktree (ea60e248) | HARNESS_BATCH unset, -j4 PROCS=3 | 2317s (12:28:18→13:06:55) | — | — | fc8247017b39cd31c49366f5f94cbb0d | 170 |
| C1 | main BY ERROR (no batch code) | env HARNESS_BATCH=64 (no-op), PROCS=8, -j4 | 2640.36s | 4213.10s | 3346.72s | fc8247017b39cd31c49366f5f94cbb0d | 170 |
| C2 | tt4m3 worktree | HARNESS_BATCH=64 PROCS=8, -j4 | 2067.32s | 3859.39s | 3225.86s | fc8247017b39cd31c49366f5f94cbb0d | 170 |

- counts-hash = `grep -E "passed|failed|checks" LOG | grep -vE "^\s*$" | sort | md5`.
  IDENTICAL across all four runs = the answer-identity gate, and it held
  under three different load profiles (a loaded-box under-count — the
  §3.14 shape — would break it; it never broke).
- FAIL-line SETS also identical modulo parallel-writer line interleaving
  (verified by diff on runs A vs B: same fragments, different glue).
- GATE 1 (byte-identical unset path): A vs B — PASS.
- GATE 2 (batched answer identity): C2 vs A/B — PASS.
- HEADLINE: C2 vs B = 10.8% suite-wall reduction; C2 vs C1 (equal
  PROCS=8, like-for-like) = 21.7%. BOTH are UPPER-BOUND-UNDERSTATED:
  C2 ran while a stage-5 validation suite ran concurrently on the box.
- C1 is an accident kept honestly: the command ran in the main repo
  (batchless), making it a clean UNBATCHED-PROCS-8 measurement — which
  reconfirms K44 (PROCS=8 unbatched is 14-16% WORSE than PROCS=3).
- The suite-level number is smaller than the prototype's 4.28x by
  construction: only the harness's per-case-exec sections batch; the
  suite carries many non-corpus sections. Per-section numbers are the
  prototype's (docs/dev/tt4m_darwin_validation.md).
- OWED onward: a QUIET-box C2 re-run whenever a cleaner headline is
  wanted; the axes-stage batching adoption (the 5.6h battery stage) as
  its own later row; F4's mech `harnessbatch` arm (chartered).
