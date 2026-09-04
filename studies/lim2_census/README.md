# studies/lim2_census/ — the raw-vs-minimized DFA table census

[LIM-2] STEP 1 charted a projected-size bail for the DFA route's
`PCREC_MAX_EMIT_BYTES` cap: project the forward table-engine machine's
emitted byte count DURING subset construction, and refuse early rather
than paying full construction + minimization + emission cost only to
discover the artifact was always going to be too big (measured on
pcrec-bench's `bench/altwide` set: an early refusal costs 0.01-1.6s
against 8.7-40.2s for the full construction on the same witness).

The projection is necessarily a projection of the RAW machine — before
`pcrec_minimize_dfa` runs — so it needs a MARGIN against how much
minimization typically shrinks a table. The manager's ruling on that
margin (docs/dev/lanes/lim2_rulings.md, ruling 1) was: **build a census.**
This directory is that census, kept as a permanent measuring instrument
after [LIM-2]'s own bail mechanism was **withdrawn** (ruling 7) because
the census itself disproved the margin the mechanism needed.

## The finding that withdrew the bail

Over the whole pcrec `.rxt` corpus plus pcrec-bench's `bench/altwide` set
(read-only; this study never writes to that sibling repo), 12 patterns
reach the regime the margin question is about — a forward table-engine
machine whose RAW (pre-minimize) transition table already exceeds
`PREMUL_MAX_ENTRIES` (65,535 entries, the point past which the indexed
representation is guaranteed for the rest of that machine's own raw
construction). Of those 12, the worst measured shrink is **97.062%**
(`tests/base/k18_cost_gates.rxt`'s own compile-COST stress witness:
27,575 raw states collapse to 1,010 after minimization).

The bail's margin design (`BAIL_KEEP_PCT`, a percent-of-raw-bytes
assumption) needs `2 x measured_max_shrink` points of margin to be safe
against a false early refusal (ruling 1's own acceptance rule). `2 x
97.062 = 194.125` points — and a percent-of-raw-bytes margin is bounded
at `[0, 100)` points BY CONSTRUCTION. No value in that range clears
194.125. Measured on a quiet box (load1 < 0.5), the branch at the
tightest representable margin (1, i.e. "assume as little as 1% of raw
bytes survive") is not even faster than main for either of the two
headline witnesses (w-2048: 11.39s vs 10.81s baseline; s-4096: 19.24s
vs 19.32s) — the bail simply never fires early enough to matter once the
margin is honest, and the reverse-first construction reorder the bail's
headstart needed pays for itself nowhere. See
`docs/dev/lanes/lim2_report.md` for the full three-way measurement and
`census_data.tsv`/`census_summary.txt` for this directory's own numbers.

**The generalisable finding, independent of this one mechanism**: a raw
subset-construction byte count is not a rigorous, marginable lower bound
on a DFA machine's final (minimized) table size for the corpus this
project actually compiles — minimization's shrink ratio is not bounded
by anything close to the ~3.5% a two-witness manual sample suggested.
This is the input [LIM-2] STUDY-1 (`docs/dev/dfa_online_minimization_study.md`
on `main`) cites for its N2/N1 successor design (§5.1 item 1): the
successor does not try to PROJECT the minimized size at all, it makes
minimization itself incremental/online during construction so there is
nothing left to project.

## What this directory is

- `lim2_census.c` — the measuring instrument. Links the repo root's
  `build/libpcrec.a` and drives the same internal pipeline
  `src/core/compile.c`'s D7 fast path calls (parse -> altcls ->
  discharge_atomic -> callgraph_build -> select_engine -> postresolve ->
  the `pcrec_artifact_has_dfa_scan` gate -> build_nfa -> the `nfa_has_bot`
  gate -> build_dfa -> minimize), under default options, so the
  population it measures is the real one any future margin-based
  mechanism would have to survive. See its own header comment for the
  full methodology and why sharing the byte-width FORMULA with
  `emit_dfa.c`'s own `emit_tr_table` layout is not the "control shares a
  source with what it controls" failure shape (docs/dev/learnings.md S3)
  — this study renders no verdict, so there is no verdict to share a
  source with.
- `Makefile` — `make` builds `lim2_census` against `../../build/libpcrec.a`
  (build the repo root first); `make census` re-runs the full sweep via
  `run_census.sh` and regenerates the two data files IN PLACE (does not
  commit them — re-measurement is a deliberate act, `studies/CLAUDE.md`'s
  own rule).
- `run_census.sh` — finds pcrec's `.rxt` corpus and (read-only, skipped
  loudly if absent) pcrec-bench's `bench/altwide/patterns/*.rx`, runs the
  binary over the union, writes `census_data.tsv` / `census_summary.txt`.
- `census_data.tsv` — the COMMITTED data (this is the row's lasting
  yield): one row per population member — `id`, `raw_n`, `raw_ncls`,
  `raw_bytes`, `min_n`, `min_bytes`, `shrink_pct` — for every pattern
  whose forward machine's raw entries cross `PREMUL_MAX_ENTRIES`.
  Population 12 (1 corpus, 11 altwide), measured 2026-09-04 on the
  project box against a `main`-identical tree (`lane/lim2` post-revert).
- `census_summary.txt` — the one-screen distribution: population size,
  per-route counts (refused / VM-only / ENG_ATTEMPT / below-threshold /
  in-population), the representation-ambiguous count (5 of 12 — where
  minimized entries drop back at or under `PREMUL_MAX_ENTRIES`, a
  geometry fact about this population, not a defect — see the tool's own
  header comment), the max shrink and its witness, and the required
  margin the max shrink would need.

## Machine/date context (D35 spirit)

Measured on the project box, 2026-09-04, against `lane/lim2` after
ruling 7's revert (i.e. functionally `main` at the branch's merge base,
`56f34b01`, plus this study). Re-measure before load-bearing use
elsewhere, per `studies/CLAUDE.md`'s standing rule.
